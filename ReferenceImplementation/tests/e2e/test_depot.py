"""WP-5.2 — the same visit, with the train resolved from a real Train Depot.

`test_m1.py` runs the Handler against the station with both of them reading trains from the
contracts' files. Here a third real component is added: the Handler asks the Depot what the
train is, the station asks the *same* Depot, and neither reads a train from disk.

That is the arrangement the acceptance criterion describes, and it is the one worth testing,
because it is where the two components can disagree. The Handler puts a digest in the
descriptor; the station compares it with what the Depot tells it; PEP 2 hashes the bytes the
Depot served and compares them with what the agreement pinned. Three comparisons, one source,
and if the Depot is wrong about any of it the visit does not run.

Nothing here is a fake. The only thing standing in for a deployment is the transport: ASGI
instead of sockets.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient
from pydantic import AnyHttpUrl

from fdt_depot.api import build_app as build_depot
from fdt_depot.core.config import DepotSettings
from fdt_depot.core.contracts import Contracts as DepotContracts
from fdt_handler.contracts import Contracts as HandlerContracts
from fdt_handler.protocol.client import StationClient
from fdt_handler.run.catalogue import FixtureCatalogue
from fdt_handler.run.depot import DepotCatalogue
from fdt_handler.runner import Runner
from fdt_station.app import create_app
from fdt_station.core.contracts import Contracts as StationContracts
from fdt_station.core.depot import DepotClient

from conftest import COMMONS, STATION_IRI, STATION_URL, plan_with_min_evidence

ONTOLOGY = COMMONS.parent / "FDT-O"
DEPOT_IRI = "https://example.org/fdt/depot/community"
TRAIN = "https://example.org/fdt/train/gene-disease"


@pytest.fixture(scope="module")
def depot() -> Iterator[TestClient]:
    settings = DepotSettings(
        iri=DEPOT_IRI,
        title="FDT Community Depot (fictional)",
        contracts_dir=COMMONS,
        ontology_dir=ONTOLOGY,
    )
    with TestClient(
        build_depot(settings, DepotContracts(COMMONS, ONTOLOGY)),
        base_url="http://depot.community.test",
    ) as client:
        yield client


@pytest.fixture
def runner(station_settings, depot: TestClient) -> Iterator[Runner]:  # noqa: F811
    """A Handler and a station that both resolve this train from the same Depot."""
    station_contracts = StationContracts(COMMONS, ONTOLOGY, depot=DepotClient(client=depot))
    app = create_app(station_settings, contracts=station_contracts)
    with TestClient(app, base_url=STATION_URL) as http:
        contracts = HandlerContracts(COMMONS, ONTOLOGY)
        catalogue = DepotCatalogue(
            FixtureCatalogue(contracts, endpoints={STATION_IRI: STATION_URL}),
            client=depot,
        )
        yield Runner(
            contracts=contracts,
            catalogue=catalogue,
            handler="https://handler.cardionet.example/fdt/v1",
            agent="m.devries@cardionet.example",
            client_for=lambda endpoint: StationClient(endpoint, client=http),
            follow_deadline=30.0,
        )


def test_a_visit_runs_with_the_train_resolved_from_the_depot(
    runner: Runner, depot: TestClient, tmp_path: Path
) -> None:
    """The acceptance criterion, executed with all three components real."""
    events: list[dict[str, Any]] = []
    report = runner.run(
        plan_with_min_evidence(2, tmp_path),
        on_event=lambda station, event: events.append(event),
    )

    assert [e["type"] for e in events][-1] == "visit.delivered"
    assert report.outcome is not None and report.outcome.state == "Finished", report.outcome

    # The digest that travelled is the hash of the bytes the Depot serves, traced end to end:
    # Depot bytes -> Depot's published digest -> the Handler's descriptor -> what PEP 1 checked.
    # Nothing in that chain is a number copied between two files.
    served = depot.get("/trains/gene-disease/payload").content
    computed = "sha256:" + hashlib.sha256(served).hexdigest()
    assert report.visits[0].descriptor["payload"]["digest"] == computed
    assert report.visits[0].descriptor["train"]["type"] == \
        "https://w3id.org/fdt/fdt-o#SPARQLTrain"


def test_a_train_the_depot_withholds_never_becomes_a_visit(
    station_settings, depot: TestClient, tmp_path: Path  # noqa: F811
) -> None:
    """A Depot that will not vouch for a train stops the run before a station is troubled.

    The Depot is given a corpus whose payload bytes do not match the declared digest — the
    substitution the digest exists to catch. It withholds the train; the Handler cannot resolve
    it; no descriptor is built and no station is asked to judge anything. The failure belongs
    to the consumer's plan, and it is reported as a refusal to act rather than as a rejection,
    because no controller decided anything.
    """
    from fdt_handler.run.catalogue import Unresolvable

    tampering = DepotContracts(COMMONS, ONTOLOGY)
    real = tampering.payload_bytes
    tampering.payload_bytes = (  # type: ignore[method-assign]
        lambda iri: (real(iri) or b"") + b"\n# substituted\n" if "gene-disease" in iri
        else real(iri)
    )
    withholding = TestClient(
        build_depot(DepotSettings(iri=DEPOT_IRI, contracts_dir=COMMONS,
                                  ontology_dir=ONTOLOGY), tampering),
        base_url="http://depot.broken.test",
    )

    listing = withholding.get("/trains").json()
    assert [u["reason"] for u in listing["unserved"]] == ["DigestMismatch"]
    assert all(t["id"] != "gene-disease" for t in listing["trains"])

    contracts = HandlerContracts(COMMONS, ONTOLOGY)
    catalogue = DepotCatalogue(FixtureCatalogue(contracts), client=withholding)
    with pytest.raises(Unresolvable, match="no Depot describes"):
        catalogue.train(TRAIN)


def test_the_station_and_the_handler_saw_the_same_train(
    depot: TestClient,
) -> None:
    """One authority, asked twice, answering the same — which is the point of having one."""
    import rdflib

    media_type = rdflib.URIRef("https://w3id.org/fdt/fdt-o#payloadMediaType")

    contracts = HandlerContracts(COMMONS, ONTOLOGY)
    handler_view = DepotCatalogue(FixtureCatalogue(contracts), client=depot).train(TRAIN)
    station_view = StationContracts(COMMONS, ONTOLOGY, depot=DepotClient(client=depot))

    assert handler_view.digest == station_view.payload_digest(TRAIN)

    described = station_view.payload_node(TRAIN)
    assert described is not None
    node, payload_graph = described
    assert handler_view.media_type == str(payload_graph.value(node, media_type))

    declared = station_view.declared_output(TRAIN)
    assert declared is not None
    assert declared[0] == handler_view.output_schema

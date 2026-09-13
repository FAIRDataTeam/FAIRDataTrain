"""WP-5.3 — the Handler chooses where to go by asking a registry, and then goes there.

Four real components in one scenario, and no fakes anywhere: two stations publishing their own
catalogues and data shapes, a Train Depot publishing the train and the shapes its requirement
names, a metadata registry harvesting all three over HTTP, and the Handler resolving a plan's
target set from the registry and then running the visit against the station it chose.

What makes it worth running as a scenario rather than as three unit tests is the hand-off. The
registry answers with a station IRI; the Handler has to turn that into a dispatch endpoint it
has never been told about, negotiate at that station and come back with an envelope. Every one
of those steps reads something a different component published, and a fake at any point would
be the two halves of one team agreeing with itself.

The second station is the near miss. It is in the same network, speaks the same mechanism,
processes in the same jurisdiction and curates the same kind of data under the same class — and
it does not record the one property the train reads. It must be left out, and the reason must
name that property, because a run that visited one of two stations has to say which one it did
not visit and why (ADR-026).
"""

from __future__ import annotations

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
from fdt_handler.run.registry import RegistryCatalogue
from fdt_handler.runner import Runner
from fdt_registry.api import build_app as build_registry
from fdt_registry.core.config import RegistrySettings, Source, SourceKind
from fdt_registry.core.contracts import Contracts as RegistryContracts
from fdt_registry.harvest.harvester import Harvester
from fdt_station.app import create_app
from fdt_station.core.config import Adapter, HostedDataset, StationSettings

from conftest import COMMONS, STATION_IRI, STATION_URL, plan_with_min_evidence

ONTOLOGY = COMMONS.parent / "FDT-O"
DEPOT_IRI = "https://example.org/fdt/depot/community"
DEPOT_URL = "http://depot.community.test"
TRAIN = "https://example.org/fdt/train/gene-disease"
NEAR_MISS_IRI = "https://example.org/fdt/station/westerlicht"
NEAR_MISS_URL = "http://station.westerlicht.test"
HEALTH_RESEARCH = "https://example.org/fdt/net/health-research-nl"
SPARQL = "https://w3id.org/fdt/instances#SPARQL"
NLD = "http://publications.europa.eu/resource/authority/country/NLD"


def _near_miss_settings() -> StationSettings:
    """Westerlicht: everything the selector asks for except the data.

    Its shape declares the same class and the same properties bar one — the curation database
    records which studies support an association and not how many subjects each covered, and
    `gd:subjectCount` is what the train's k-anonymity duty is a rule about.
    """
    return StationSettings(
        iri=AnyHttpUrl(NEAR_MISS_IRI),
        title="Westerlicht University data station (fictional)",
        owner_name="Westerlicht University — research data services",
        base_url=AnyHttpUrl(NEAR_MISS_URL),
        catalog_iri=AnyHttpUrl("https://example.org/fdt/catalog/westerlicht"),
        adapters=frozenset({Adapter.SPARQL}),
        auth_required=False,
        contracts_dir=COMMONS,
        processing_location=AnyHttpUrl(NLD),
        memberships=[{
            "network": HEALTH_RESEARCH,
            "network_title": "National health research network",
            "governance_authority": "https://example.org/fdt/auth/hri-like",
            "governance_authority_name": "Governance authority",
            "admits_natural_persons": False,
            "trusted_issuer": "https://idp.example.org/ls-aai-like",
            "role": "https://w3id.org/fdt/network#StationRole",
            "credential": "https://example.org/fdt/cred/westerlicht-hri",
        }],
        datasets=[HostedDataset(
            iri=AnyHttpUrl("https://example.org/fdt/dataset/westerlicht-variant-curation"),
            adapter=Adapter.SPARQL,
            source=COMMONS / "examples" / "data" / "ut-gene-disease.ttl",
        )],
    )


@pytest.fixture
def ecosystem(station_settings: StationSettings) -> Iterator[dict[str, TestClient]]:
    """Two stations, a Depot and a registry that has harvested all three."""
    depot = TestClient(
        build_depot(
            DepotSettings(iri=DEPOT_IRI, contracts_dir=COMMONS, ontology_dir=ONTOLOGY),
            DepotContracts(COMMONS, ONTOLOGY),
        ),
        base_url=DEPOT_URL,
    )
    ut = TestClient(create_app(station_settings), base_url=STATION_URL)
    near_miss = TestClient(create_app(_near_miss_settings()), base_url=NEAR_MISS_URL)

    settings = RegistrySettings(
        iri="https://registry.example/fdt/v1",
        sources=(
            Source(url=STATION_URL, kind=SourceKind.STATION),
            Source(url=NEAR_MISS_URL, kind=SourceKind.STATION),
            Source(url=DEPOT_URL, kind=SourceKind.DEPOT),
        ),
        contracts_dir=COMMONS,
        ontology_dir=ONTOLOGY,
    )
    registry_contracts = RegistryContracts(COMMONS, ONTOLOGY)
    harvester = Harvester(
        settings, registry_contracts,
        clients={STATION_URL: ut, NEAR_MISS_URL: near_miss, DEPOT_URL: depot},
    )
    with ut, near_miss, depot, TestClient(
        build_registry(settings, registry_contracts, harvester=harvester)
    ) as registry:
        assert all(row["reached"] for row in registry.post("/harvest").json())
        yield {"registry": registry, "ut": ut, "near_miss": near_miss, "depot": depot}


@pytest.fixture
def catalogue(ecosystem: dict[str, TestClient]) -> RegistryCatalogue:
    """Stations from the registry, the train from its Depot (ADR-029).

    The registry indexes trains too, and answering from it would be one line. That line would
    put a harvester on the path of the digest a station agrees to run — a discovery service
    deciding a security question, which is the arrangement ADR-029 declined to build.
    """
    contracts = HandlerContracts(COMMONS, ONTOLOGY)
    return RegistryCatalogue(
        DepotCatalogue(FixtureCatalogue(contracts), client=ecosystem["depot"]),
        client=ecosystem["registry"],
    )


def test_the_registry_resolves_the_target_set_and_names_what_it_left_out(
    catalogue: RegistryCatalogue,
) -> None:
    """WP-5.3's acceptance criterion, both clauses, with every component real."""
    selection = catalogue.select(
        train=TRAIN,
        mechanisms=(SPARQL,),
        networks=(HEALTH_RESEARCH,),
        processing_locations=(NLD,),
    )

    assert selection.stations == (STATION_IRI,)
    assert selection.harvested_at, "an answer with no harvest time cannot be judged for staleness"

    skipped = {item.station: item for item in selection.skipped}
    assert set(skipped) == {NEAR_MISS_IRI}
    excluded = skipped[NEAR_MISS_IRI]
    assert excluded.on == "data", (
        "excluded on the wrong clause: this station is in the network, speaks the mechanism and "
        "processes in the jurisdiction — reporting it as a governance exclusion would "
        "misdescribe the run"
    )
    assert any("subjectCount" in reason for reason in excluded.reasons), excluded.reasons


def test_the_visit_runs_at_the_station_the_registry_chose(
    catalogue: RegistryCatalogue, ecosystem: dict[str, TestClient], tmp_path: Path
) -> None:
    """From "which station?" to a delivered envelope, without the Handler being told either.

    The dispatch endpoint is the one the station published in its own catalogue; the train, its
    digest and its parameters are the Depot's; the target dataset is chosen from what the
    station says it holds and offers under this network. Nothing in this test hard-codes the
    route.
    """
    selection = catalogue.select(train=TRAIN, mechanisms=(SPARQL,), networks=(HEALTH_RESEARCH,))
    assert selection.stations == (STATION_IRI,)

    endpoint = catalogue.station(selection.stations[0]).dispatch_endpoint
    assert endpoint.startswith(STATION_URL)

    runner = Runner(
        contracts=HandlerContracts(COMMONS, ONTOLOGY),
        catalogue=catalogue,
        handler="https://handler.cardionet.example/fdt/v1",
        agent="m.devries@cardionet.example",
        client_for=lambda _endpoint: StationClient(_endpoint, client=ecosystem["ut"]),
        follow_deadline=30.0,
    )
    events: list[dict[str, Any]] = []
    report = runner.run(
        plan_with_min_evidence(2, tmp_path),
        on_event=lambda station, event: events.append(event),
    )

    assert [e["type"] for e in events][-1] == "visit.delivered"
    assert report.outcome is not None and report.outcome.state == "Finished", report.outcome
    assert report.visits[0].descriptor["target"] == (
        "https://example.org/fdt/dataset/ut-gene-disease"
    )


def test_a_station_the_registry_could_not_reach_is_reported_not_dropped(
    station_settings: StationSettings, ecosystem: dict[str, TestClient]
) -> None:
    """"The station is down" and "the station does not exist" are different facts.

    A registry that dropped the row would answer every later search with one station fewer and
    nothing to show for it, and the run's completeness statement would silently narrow.
    """
    settings = RegistrySettings(
        sources=(
            Source(url=STATION_URL, kind=SourceKind.STATION),
            Source(url="http://station.nowhere.invalid", kind=SourceKind.STATION),
        ),
        contracts_dir=COMMONS,
        ontology_dir=ONTOLOGY,
    )
    harvester = Harvester(
        settings, RegistryContracts(COMMONS, ONTOLOGY), clients={STATION_URL: ecosystem["ut"]},
    )
    index = harvester.harvest()

    rows = {report.source.url: report for report in index.reports}
    assert rows[STATION_URL].reached
    assert not rows["http://station.nowhere.invalid"].reached
    assert rows["http://station.nowhere.invalid"].error
    assert [record.iri for record in index.stations] == [STATION_IRI]

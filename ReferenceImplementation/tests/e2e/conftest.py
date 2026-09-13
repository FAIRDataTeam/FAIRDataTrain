"""Shared setup for the end-to-end scenarios.

The station, its fixture network and the plan-rewriting helper live here because more than one
scenario needs them: `test_m1.py` runs the Handler against the station, and `test_depot.py`
runs both of them against a real Train Depot as well.
"""

from __future__ import annotations

import json
from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from pydantic import AnyHttpUrl

from fdt_handler.contracts import Contracts as HandlerContracts
from fdt_handler.protocol.client import StationClient
from fdt_handler.run.catalogue import FixtureCatalogue
from fdt_handler.runner import Runner
from fdt_station.app import create_app
from fdt_station.core.config import Adapter, HostedDataset, StationSettings

ROOT = Path(__file__).resolve().parents[2]
COMMONS = ROOT / "fdt-commons"

#: The station is addressed by a bare host: ASGI routes by path, and the station's own routes
#: hang off the root. The IRI it is *known* by is the fixture's, which is what the descriptor
#: and every agreement will name.
STATION_IRI = "https://example.org/fdt/station/ut"
STATION_URL = "http://station.ut.test"


@pytest.fixture(scope="module")
def station_settings() -> StationSettings:
    return StationSettings(
        iri=AnyHttpUrl(STATION_IRI),
        title="University station (fictional)",
        owner_name="University — ICT services",
        base_url=AnyHttpUrl(STATION_URL),
        catalog_iri=AnyHttpUrl("https://example.org/fdt/catalog/ut"),
        adapters=frozenset({Adapter.SPARQL}),
        # The visit carries no token here and the station is told so explicitly. Turning
        # authentication off is a visible act of configuration, never a default: a station that
        # accepted anonymous visits by accident could not say who ran a train against its data.
        auth_required=False,
        contracts_dir=COMMONS,
        memberships=[
            {
                "network": "https://example.org/fdt/net/health-research-nl",
                "network_title": "National health research network",
                "governance_authority": "https://example.org/fdt/auth/hri-like",
                "governance_authority_name": "Governance authority",
                "admits_natural_persons": False,
                "permits_automated_decision": True,
                "trusted_issuer": "https://idp.example.org/ls-aai-like",
                "role": "https://w3id.org/fdt/network#StationRole",
                "credential": "https://example.org/fdt/cred/ut",
            }
        ],
        datasets=[
            HostedDataset(
                iri=AnyHttpUrl("https://example.org/fdt/dataset/ut-gene-disease"),
                adapter=Adapter.SPARQL,
                source=COMMONS / "examples" / "data" / "ut-gene-disease.ttl",
            )
        ],
    )


@pytest.fixture
def runner(station_settings: StationSettings) -> Iterator[Runner]:
    app = create_app(station_settings)
    # `TestClient` is an `httpx.Client` that speaks ASGI, so the Handler's own client talks to
    # the real station app through it without a socket — same code, same protocol, no port.
    with TestClient(app, base_url=STATION_URL) as http:
        contracts = HandlerContracts(COMMONS)
        yield Runner(
            contracts=contracts,
            catalogue=FixtureCatalogue(contracts, endpoints={STATION_IRI: STATION_URL}),
            handler="https://handler.cardionet.example/fdt/v1",
            agent="m.devries@cardionet.example",
            client_for=lambda endpoint: StationClient(endpoint, client=http),
            follow_deadline=30.0,
        )


def plan_with_min_evidence(value: int, tmp_path: Path) -> Path:
    """The M1 plan, one parameter changed and nothing else."""
    source = COMMONS / "examples" / "plan-gene-disease-single.jsonld"
    document = json.loads(source.read_text())
    if value != 2:
        document["@id"] = f"{document['@id']}-k{value}"
        for parameter in document["parameterValues"]:
            if parameter["parameter"].endswith("gd-min-evidence"):
                parameter["value"] = value
    written = tmp_path / f"plan-{value}.jsonld"
    written.write_text(json.dumps(document, indent=2))
    return written



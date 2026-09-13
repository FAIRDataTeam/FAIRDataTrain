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
from fdt_handler.protocol.signing import OwnerKey
from fdt_handler.run.catalogue import FixtureCatalogue
from fdt_handler.runner import Runner
from fdt_station.app import create_app
from fdt_station.core.config import (
    Adapter,
    DecisionMode,
    HostedDataset,
    StationSettings,
)

ROOT = Path(__file__).resolve().parents[2]
COMMONS = ROOT / "fdt-commons"

#: The station is addressed by a bare host: ASGI routes by path, and the station's own routes
#: hang off the root. The IRI it is *known* by is the fixture's, which is what the descriptor
#: and every agreement will name.
STATION_IRI = "https://example.org/fdt/station/ut"
STATION_URL = "http://station.ut.test"


#: The train owner these scenarios act for: the party the M1 request names as assignee, and
#: whose key signs the agreements it concludes (ADR-038).
OWNER_PARTY = "https://example.org/fdt/party/eu-cardionet-like"
STATION_KEY_ID = "https://station.ut.test/fdt/v1/keys/1"
OWNER_KEY_ID = "https://handler.cardionet.example/fdt/v1/keys/1"


def _jwk(private: object, key_id: str, private_half: bool) -> dict[str, object]:
    import base64

    def b64u(raw: bytes) -> str:
        return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")

    key: dict[str, object] = {
        "kty": "OKP", "crv": "Ed25519", "alg": "EdDSA", "use": "sig", "kid": key_id,
        "x": b64u(private.public_key().public_bytes_raw()),   # type: ignore[attr-defined]
    }
    if private_half:
        key["d"] = b64u(private.private_bytes_raw())          # type: ignore[attr-defined]
    return key


@pytest.fixture(scope="module")
def signing_keys(tmp_path_factory: pytest.TempPathFactory) -> dict[str, Path]:
    """Real keys for both parties, generated per run and never committed.

    ADR-038 is the one rule in this system that two components have to agree on *through
    cryptography* rather than through a shared reading of a document, so the scenarios that run
    the real Handler against the real station are where it is actually tested: the station signs
    the assigner's side, the Handler checks and signs the assignee's, and the station verifies
    it against a key it was told about out of band. Any disagreement about canonicalisation,
    about what is excluded from the digest, or about who a signature is for, fails here.
    """
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

    directory = tmp_path_factory.mktemp("fdt-e2e-keys")
    station_private = Ed25519PrivateKey.generate()
    owner_private = Ed25519PrivateKey.generate()

    station_key = directory / "station-signing-key.json"
    station_key.write_text(json.dumps(
        {"keys": [_jwk(station_private, STATION_KEY_ID, private_half=True)]}))

    owner_key = directory / "owner-signing-key.json"
    owner_key.write_text(json.dumps(
        {"keys": [_jwk(owner_private, OWNER_KEY_ID, private_half=True)]}))

    # What the station is told, out of band, about the party it will be asked to accept a
    # signature from. Only the public half: a station holding a train owner's private key would
    # be able to sign for them, which is the arrangement the two signatures exist to rule out.
    party_keys = directory / "party-keys.json"
    party_keys.write_text(json.dumps(
        {OWNER_PARTY: {"keys": [_jwk(owner_private, OWNER_KEY_ID, private_half=False)]}}))

    return {"station": station_key, "owner": owner_key, "parties": party_keys}


@pytest.fixture(scope="module")
def station_settings(signing_keys: dict[str, Path]) -> StationSettings:
    return StationSettings(
        signing_key=signing_keys["station"],
        party_keys=signing_keys["parties"],
        # ADR-034: these scenarios are about what the negotiation rule decides, so
        # the operator's own dial is stated. A production station defaults to
        # `manual`, and a scenario that relied on the default would be exercising
        # the default rather than the rule it was written for.
        decision_mode=DecisionMode.AUTOMATED,
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
def runner(station_settings: StationSettings, signing_keys: dict[str, Path]) -> Iterator[Runner]:
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
            owner_key=OwnerKey.load(signing_keys["owner"], OWNER_PARTY),
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



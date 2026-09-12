"""M1 — one visit, end to end, with both components real.

The milestone's exit criterion, executed: *the gene–disease SPARQL train reaches one station
with a test graph, is auto-approved, runs through PEP 1–3; the Handler CLI prints the event
stream and the envelope; the invalid fixtures are refused or rejected with the right reasons.*

Nothing here is a fake. The Handler resolves the plan from the contracts' catalogue, builds a
descriptor, pushes it, follows the stream and assembles a run state; the station checks the
train, negotiates an agreement, runs the payload against the test graph and inspects what came
out. The only thing standing in for a deployment is the transport: the station is reached over
ASGI instead of a socket, which is the same code and the same protocol without a port. The
same two components were also run over HTTP under uvicorn, driven by `fdt-handler run`.

The pair is what makes it a test rather than a demonstration. Two plans differing in **one
parameter** — `min_evidence` 2 against 1 — go to the same station, under the same agreement,
against the same data, and reach opposite outcomes. Whether a result may leave is a property of
the result, and only the inspection can tell.
"""

from __future__ import annotations

import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any

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


# --------------------------------------------------------------------------- the criterion


def test_the_handler_drives_a_train_to_a_station_and_gets_an_aggregate(
    runner: Runner, tmp_path: Path
) -> None:
    events: list[dict[str, Any]] = []
    report = runner.run(
        plan_with_min_evidence(2, tmp_path),
        on_event=lambda station, event: events.append(event),
    )

    assert [(e["type"], e["checkpoint"]) for e in events] == [
        ("visit.received", "PEP1"),
        ("negotiation.requested", "NEG"),
        ("negotiation.matched", "NEG"),
        ("negotiation.active", "NEG"),
        ("visit.queued", "PEP2"),
        ("visit.running", "EXEC"),
        ("visit.inspecting", "PEP3"),
        ("visit.delivered", "PEP3"),
    ]
    assert report.outcome is not None
    assert report.outcome.state == "Finished"

    visit = report.visits[0]
    assert visit.outcome == "delivered"
    assert visit.envelope is not None
    assert visit.envelope["result"] == json.loads(
        (COMMONS / "examples" / "protocol" / "visit-result-gd-m1.json").read_text()
    )["result"]
    assert visit.agreement and visit.agreement.startswith(STATION_URL)


def test_one_parameter_different_and_the_run_fails_with_the_reason(
    runner: Runner, tmp_path: Path
) -> None:
    report = runner.run(plan_with_min_evidence(1, tmp_path))
    visit = report.visits[0]

    assert visit.outcome == "rejected"
    assert visit.envelope is not None
    assert visit.envelope["checkpoint"] == "PEP3"
    assert visit.envelope["result"] == {}                     # ADR-015: nothing travelled
    assert "fewer than 5 subjects" in str(visit.reason)

    assert report.outcome is not None
    assert report.outcome.state == "FailedRun"
    # ADR-026 verbatim: the run says *rejected*, not "failed" and not "refused"
    assert "1 rejected" in report.outcome.reason


def test_the_run_state_is_a_valid_run_state(runner: Runner, tmp_path: Path) -> None:
    """`run-state.schema.json` is the envelope ADR-025 conditions are evaluated over, so a
    Handler that produced an invalid one would make every condition in every plan meaningless."""
    report = runner.run(plan_with_min_evidence(2, tmp_path))
    state = report.state(runner.contracts)          # raises if it does not conform
    assert state["runState"] == "Finished"
    assert state["outcomes"]["delivered"] == 1
    assert len(state["visits"]) == 1
    assert state["visits"][0]["state"] == "delivered"
    assert "incomplete" not in state


def test_a_failed_run_is_describable_too(runner: Runner, tmp_path: Path) -> None:
    """The half that could not be described before `fdt-commons` finding 47: a station that
    produced envelopes only for successes left a Handler able to report a good run and unable
    to report a bad one."""
    report = runner.run(plan_with_min_evidence(1, tmp_path))
    state = report.state(runner.contracts)
    assert state["runState"] == "FailedRun"
    assert state["outcomes"]["rejected"] == 1
    assert state["visits"][0]["checkpoint"] == "PEP3"
    assert "incomplete" not in state


# --------------------------------------------------------------------------- what it refuses


def test_the_handler_will_not_hold_what_a_station_should_not_have_sent(
    runner: Runner, tmp_path: Path
) -> None:
    """ADR-015, enforced rather than assumed. The station is honest; the Handler checks anyway.

    Two independent checks, and this is the second: it stops the Handler *storing* what a
    broken or hostile station sent, which no amount of correctness in the station can do.
    """
    from fdt_handler.store import HandlerStore, RecordLevelRefused

    report = runner.run(plan_with_min_evidence(2, tmp_path))
    envelope = dict(report.visits[0].envelope or {})

    envelope["inspection"] = {**envelope["inspection"], "onwardStateClass": "RecordLevel"}
    with pytest.raises(RecordLevelRefused, match="never leaves a station"):
        HandlerStore.check(envelope)

    rejected = runner.run(plan_with_min_evidence(1, tmp_path)).visits[0].envelope
    assert rejected is not None
    with pytest.raises(RecordLevelRefused, match="does not travel"):
        HandlerStore.check({**rejected, "result": {"rows": [{"subject_count": 3}]}})

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

from conftest import COMMONS, STATION_IRI, STATION_URL, plan_with_min_evidence  # noqa: F401
from fdt_handler.runner import Runner

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
        # ADR-038, and the step that proves the two implementations agree: the station signed
        # the assigner's side and waited, the Handler checked and signed the assignee's, and
        # the station verified it. Nothing between these two events ran.
        ("negotiation.awaiting-signature", "NEG"),
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

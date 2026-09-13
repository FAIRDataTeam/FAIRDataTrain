"""WP-5.5 — what the consoles read, read against real components.

The acceptance criterion for WP-5.5 is the M1 scenario *watched*: the itinerary, the
checkpoints, the justifications, the envelope. A browser is not a thing a test suite can hold,
but everything the browser is shown is, and that is what this file pins — the two surfaces the
consoles were built on, answering for a run that actually happened at a station that actually
decided.

Why it is worth a test of its own rather than trusting the component suites. Each side's tests
check its own API against its own store. What nothing checked was whether **the two accounts of
the same visit agree**: the station's operator timeline and the Handler's itinerary describe one
event stream from opposite ends, and a console user reading both would be the first to notice if
they did not. They are separate surfaces on purpose — a station operator must not see a whole
run, a consumer must not see a station's other traffic — and that separation is exactly what
lets them drift.
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
from conftest import COMMONS, STATION_IRI, STATION_URL, plan_with_min_evidence
from fastapi.testclient import TestClient

from fdt_handler.api import build_app
from fdt_handler.contracts import Contracts as HandlerContracts
from fdt_handler.protocol.client import StationClient
from fdt_handler.run.catalogue import FixtureCatalogue
from fdt_handler.runner import RunReport, Runner
from fdt_handler.runs import RunStore
from fdt_station.app import create_app
from fdt_station.core.config import DecisionMode, StationSettings

ONTOLOGY = COMMONS.parent / "FDT-O"

OPERATOR = {"Authorization": "Bearer testbed-operator"}


@pytest.fixture
def watched(
    station_settings: StationSettings,
) -> Iterator[tuple[TestClient, TestClient, RunReport]]:
    """One M1 run, with both console surfaces open over it.

    The station is configured with an admin credential because its operator surface needs one:
    the visits are other parties' traffic, and a station that served them to whoever asked
    would be publishing one consumer's business to the next.
    """
    settings = station_settings.model_copy(update={"admin_token": "testbed-operator"})
    app = create_app(settings)
    with TestClient(app, base_url=STATION_URL) as http:
        contracts = HandlerContracts(COMMONS)
        runs = RunStore()
        runner = Runner(
            contracts=contracts,
            catalogue=FixtureCatalogue(contracts, endpoints={STATION_IRI: STATION_URL}),
            handler="https://handler.cardionet.example/fdt/v1",
            agent="m.devries@cardionet.example",
            client_for=lambda endpoint: StationClient(endpoint, client=http),
            follow_deadline=30.0,
        )
        report = runner.run(
            COMMONS / "examples" / "plan-gene-disease-single.jsonld", on_start=runs.remember
        )
        handler = TestClient(
            build_app(contracts, runs, handler="https://handler.cardionet.example/fdt/v1")
        )
        yield http, handler, report


def got(client: TestClient, path: str, **kwargs: Any) -> Any:
    response = client.get(path, **kwargs)
    assert response.status_code == 200, f"{path}: {response.text}"
    return response.json()


def test_the_handler_console_can_draw_the_itinerary(
    watched: tuple[TestClient, TestClient, RunReport],
) -> None:
    """H3's three panels — the KPI row, the map and the visits table — from two calls."""
    _, handler, report = watched
    [run] = got(handler, "/runs")["runs"]
    [visit] = got(handler, f"/runs/{report.run}/visits")["visits"]

    assert run["runState"] == "Finished"
    # The whole counter set, not just the happy number. ADR-026 keeps six outcomes apart, and a
    # console panel built on `delivered` alone would read identically against a Handler that
    # had stopped counting the other five — which is the failure that loses a refusal.
    assert run["outcomes"] == {
        "intended": 1, "delivered": 1, "skipped": 0, "refused": 0,
        "timedOut": 0, "rejected": 0, "failed": 0, "revoked": 0,
    }
    assert visit["station"] == STATION_IRI
    assert visit["outcome"] == "delivered"
    assert [c["status"] for c in visit["checkpoints"]] == ["passed"] * 5


def test_the_station_console_can_draw_the_same_visit_from_the_other_end(
    watched: tuple[TestClient, TestClient, RunReport],
) -> None:
    """The operator's row for the visit the Handler dispatched, with its checkpoint chain."""
    station, _, report = watched
    [row] = got(station, "/admin/visits", headers=OPERATOR)["visits"]
    assert row["visit"] == report.visits[0].visit
    assert row["state"] == "Delivered"
    assert row["checkpoint"] == "PEP3"
    assert row["consumer"] == "https://example.org/fdt/party/eu-cardionet-like"


def test_the_two_accounts_of_the_visit_agree(
    watched: tuple[TestClient, TestClient, RunReport],
) -> None:
    """The check neither component's own suite can make.

    The station's timeline and the Handler's feed are the same event stream read from opposite
    ends, by two codebases, over two APIs, for two audiences who are not allowed to see each
    other's. Nothing but a comparison holds them together — and a console user reading both
    would be the first to find out if they had drifted.
    """
    station, handler, report = watched
    visit = report.visits[0].visit
    theirs = got(station, f"/admin/visits/{visit}/events", headers=OPERATOR)
    ours = got(handler, f"/runs/{report.run}/events")

    assert [e["sequence"] for e in theirs] == [e["sequence"] for e in ours]
    assert [e["type"] for e in theirs] == [e["type"] for e in ours]
    assert [e.get("justification") for e in theirs] == [e.get("justification") for e in ours]
    assert [e["state"] for e in theirs][-1] == "Delivered"


def test_the_envelope_is_reachable_and_carries_only_what_may_leave(
    watched: tuple[TestClient, TestClient, RunReport],
) -> None:
    """"the envelope" of the acceptance criterion, and ADR-015 checked where a console reads it.

    The run state is what H3's completeness panel is built from and what a plan's stop condition
    is evaluated over, so it is the same document in both roles — and it must not be able to
    carry record-level data to either.
    """
    _, handler, report = watched
    state = got(handler, f"/runs/{report.run}")
    [envelope] = state["visits"]
    assert envelope["state"] == "delivered"
    assert envelope["inspection"]["onwardStateClass"] in ("Aggregate", "Pseudonym")
    assert envelope["inspection"]["outcome"] == "passed"
    assert envelope["result"], "a delivered envelope carries the aggregate that was released"


def test_a_rejected_result_is_reported_as_rejected_on_both_consoles(
    station_settings: StationSettings, tmp_path: Path
) -> None:
    """The hardest distinction in ADR-026, through both console surfaces at once.

    The same train, the same station, the same data, one parameter changed: the aggregate comes
    out with a cell below the agreement's k threshold and PEP 3 will not release it. The visit
    is **Rejected** — the result failed inspection — which is not **Refused**, where a
    controller declined access, and is not **Failed**, where something broke.

    Both consoles have to carry that word. The Handler's itinerary row is what a consumer reads
    when their run comes back short, and the station's row is what the operator reads when the
    controller asks what happened to their data; a console that said "failed" on either side
    would have told one of them something untrue about the other.
    """
    settings = station_settings.model_copy(update={"admin_token": "testbed-operator"})
    app = create_app(settings)
    with TestClient(app, base_url=STATION_URL) as http:
        contracts = HandlerContracts(COMMONS)
        runs = RunStore()
        runner = Runner(
            contracts=contracts,
            catalogue=FixtureCatalogue(contracts, endpoints={STATION_IRI: STATION_URL}),
            handler="https://handler.cardionet.example/fdt/v1",
            client_for=lambda endpoint: StationClient(endpoint, client=http),
            follow_deadline=30.0,
        )
        report = runner.run(plan_with_min_evidence(1, tmp_path), on_start=runs.remember)
        handler = TestClient(
            build_app(contracts, runs, handler="https://handler.cardionet.example/fdt/v1")
        )

        [ours] = got(handler, f"/runs/{report.run}/visits")["visits"]
        [run] = got(handler, "/runs")["runs"]
        [theirs] = got(http, "/admin/visits", headers=OPERATOR)["visits"]

    assert ours["outcome"] == "rejected"
    assert ours["outcome"] not in ("refused", "failed")
    assert theirs["state"] == "Rejected"
    # and the checkpoint chain says WHERE: the result was inspected and not released, which is
    # a different place in the station from a request that was declined at negotiation
    marks = {c["checkpoint"]: c["status"] for c in ours["checkpoints"]}
    assert marks["NEG"] == "passed", marks
    assert marks["PEP3"] == "failed", marks
    assert run["outcomes"]["rejected"] == 1
    assert run["outcomes"]["refused"] == 0
    assert run["outcomes"]["failed"] == 0


def test_a_controller_decides_and_the_run_carries_their_words(
    station_settings: StationSettings, tmp_path: Path
) -> None:
    """WP-2.4 end to end: a station that decides nothing, a person who does, and a consumer who
    reads what they said.

    This is the loop ADR-032 exists for, with every component real. The station is in `manual`
    decision mode, so it evaluates the request, recommends, and stops. The controller reads the
    case on their own surface, refuses, and states why. The Handler — which has no idea any of
    that happened — reports the visit as **Refused** with the controller's own sentence in it.

    The words are the point. A run that reported this as "failed" would be telling a consumer
    that something broke, when what happened is that a person considered their request and said
    no; and one that reported it as "rejected" would point them at their result rather than at
    their request (ADR-026).
    """
    controller = "https://example.org/fdt/party/ut-life-sciences"
    settings = station_settings.model_copy(update={
        "decision_mode": DecisionMode.MANUAL,
        "controller_tokens": {"ut-secret": controller},
    })
    words = "The committee does not release this extract outside the consortium."

    app = create_app(settings)
    with TestClient(app, base_url=STATION_URL) as http:
        contracts = HandlerContracts(COMMONS)
        runs = RunStore()
        runner = Runner(
            contracts=contracts,
            catalogue=FixtureCatalogue(contracts, endpoints={STATION_IRI: STATION_URL}),
            handler="https://handler.cardionet.example/fdt/v1",
            client_for=lambda endpoint: StationClient(endpoint, client=http),
            follow_deadline=5.0,
        )

        # The controller decides as soon as the case appears, from the other side of the
        # station, while the Handler is still following the visit.
        as_controller = {"Authorization": "Bearer ut-secret"}

        def refuse_the_moment_it_arrives(_: object) -> None:
            queue = got(http, "/controller/approvals", headers=as_controller)["approvals"]
            for item in queue:
                case = got(http, f"/controller/approvals/{item['id']}",
                           headers=as_controller)
                http.post(
                    f"/controller/approvals/{item['id']}/decision",
                    json={"decision": "refuse", "shownAtDecision": case["shown"],
                          "decidedUnderAuthority": "https://example.org/fdt/authority/dac",
                          "reason": words,
                          "departureReason": "Outside the consortium regardless of the match."},
                    headers=as_controller,
                )

        report = runner.run(
            COMMONS / "examples" / "plan-gene-disease-single.jsonld",
            on_start=runs.remember,
            on_event=lambda _station, event: (
                refuse_the_moment_it_arrives(event)
                if event["type"] == "negotiation.pending-approval" else None
            ),
        )
        handler = TestClient(
            build_app(contracts, runs, handler="https://handler.cardionet.example/fdt/v1")
        )
        [ours] = got(handler, f"/runs/{report.run}/visits")["visits"]
        decided = got(http, "/controller/approvals?includeDecided=true",
                      headers=as_controller)["approvals"]
        # and the station's own status, which is what a Handler coming back later reads —
        # a refusal reachable only by replaying the event stream reaches a consumer as
        # "Refused" with nothing after it (ADR-026).
        status = got(http, f"/visits/{ours['visit']}")

    # what the consumer is told
    assert ours["outcome"] == "refused", ours
    assert ours["reason"] == words
    assert ours["outcome"] not in ("rejected", "failed")
    marks = {c["checkpoint"]: c["status"] for c in ours["checkpoints"]}
    assert marks["NEG"] == "failed", marks
    assert marks["PEP2"] == "not-reached", marks
    assert status["state"] == "Refused"
    assert status["reason"] == words

    # and what the controller's own record says about the act (ADR-032 §3)
    [record] = [a["decided"] for a in decided]
    assert record["decision"] == "refuse"
    assert record["decidedBy"].startswith("approver:")
    assert record["decidedUnderAuthority"] == "https://example.org/fdt/authority/dac"
    assert record["shownAtDecision"].startswith("sha256:")
    assert record["followedRecommendation"] is False
    assert record["departureReason"]


def test_the_depot_console_leads_with_what_it_withholds(
    watched: tuple[TestClient, TestClient, RunReport],
) -> None:
    """The Depot console's first panel, from the call that fills it.

    `GET /trains` answers with both lists in one document: what this Depot serves, and what it
    holds and refuses to serve. The second is what the page leads with, and the API has to make
    that possible without a second round trip — a console that had to ask separately would be a
    console that could render the healthy half first and the refusals a moment later.
    """
    from fdt_depot.api import build_app as build_depot
    from fdt_depot.core.config import DepotSettings
    from fdt_depot.core.contracts import Contracts as DepotContracts

    settings = DepotSettings(
        iri="https://depot.example.org/fdt/v1", contracts_dir=COMMONS, ontology_dir=ONTOLOGY
    )
    with TestClient(build_depot(settings, DepotContracts(COMMONS, ONTOLOGY))) as depot:
        held = got(depot, "/trains")
    assert "trains" in held and "unserved" in held
    assert held["trains"], "the fixture corpus has trains this Depot serves"
    for train in held["trains"]:
        # the digest the Depot computed over the bytes it serves, never a declared one repeated
        assert train["digest"].startswith("sha256:")
    for withheld in held["unserved"]:
        assert withheld["reason"] and withheld["detail"], withheld


def test_the_registry_console_can_say_why_a_station_was_not_selected(
    watched: tuple[TestClient, TestClient, RunReport],
) -> None:
    """The registry console's search panel, and the half that matters to a short run.

    "No station holds your data" is not an answer anybody can act on. The exclusion names the
    clause that excluded the station and the property that was missing, and the console gives
    it the same weight as a match — to the person whose run came back short it is the more
    useful half.
    """
    from fdt_registry.api import build_app as build_registry
    from fdt_registry.core.config import RegistrySettings, Source, SourceKind
    from fdt_registry.core.contracts import Contracts as RegistryContracts
    from fdt_registry.harvest.harvester import Harvester
    from test_registry import NEAR_MISS_URL, _near_miss_settings

    from fdt_depot.api import build_app as build_depot
    from fdt_depot.core.config import DepotSettings
    from fdt_depot.core.contracts import Contracts as DepotContracts

    # The Depot is a source and not an afterthought: a registry reads a train's input
    # requirement from what its Depot published, because the Depot is the authority for the
    # train (ADR-029). A registry harvesting only stations knows what data exists and nothing
    # about what any train needs, so it can answer no search at all.
    station, _, _ = watched
    depot_url = "http://depot.test"
    depot = TestClient(
        build_depot(
            DepotSettings(
                iri="https://depot.example.org/fdt/v1",
                contracts_dir=COMMONS,
                ontology_dir=ONTOLOGY,
            ),
            DepotContracts(COMMONS, ONTOLOGY),
        ),
        base_url=depot_url,
    )
    near_miss = TestClient(create_app(_near_miss_settings()), base_url=NEAR_MISS_URL)
    settings = RegistrySettings(
        iri="https://registry.example/fdt/v1",
        sources=(
            Source(url=STATION_URL, kind=SourceKind.STATION),
            Source(url=NEAR_MISS_URL, kind=SourceKind.STATION),
            Source(url=depot_url, kind=SourceKind.DEPOT),
        ),
        contracts_dir=COMMONS,
        ontology_dir=ONTOLOGY,
    )
    contracts = RegistryContracts(COMMONS, ONTOLOGY)
    harvester = Harvester(
        settings,
        contracts,
        clients={STATION_URL: station, NEAR_MISS_URL: near_miss, depot_url: depot},
    )
    with near_miss, depot, TestClient(
        build_registry(settings, contracts, harvester=harvester)
    ) as reg:
        assert all(row["reached"] for row in reg.post("/harvest").json())
        answer = reg.post(
            "/search", json={"train": "https://example.org/fdt/train/gene-disease"}
        ).json()

    assert answer["harvestedAt"], "every answer says how old the index behind it is"
    assert [m["station"] for m in answer["matched"]] == [STATION_IRI]
    [excluded] = answer["excluded"]
    assert excluded["on"] == "data"
    assert any("subjectCount" in reason for reason in excluded["reasons"]), excluded["reasons"]


def test_the_operator_surface_is_not_open_to_the_consumer(
    watched: tuple[TestClient, TestClient, RunReport],
) -> None:
    """The separation the two surfaces exist for, checked rather than asserted in prose.

    A data consumer holds a visit token, not the station operator's credential. Without it the
    station's own traffic is not readable — otherwise the Handler console's user could read
    every other consumer's requests at every station they visited.
    """
    station, _, report = watched
    visit = report.visits[0].visit
    guessed = {"Authorization": "Bearer guess"}
    for path in ("/admin/visits", f"/admin/visits/{visit}/events"):
        assert station.get(path).status_code == 401, path
        assert station.get(path, headers=guessed).status_code == 401, path
        assert station.get(path, headers=OPERATOR).status_code == 200, path

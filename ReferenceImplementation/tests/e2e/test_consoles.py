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


# =============================================================================================
# The screens WP-5.5 finished with: the catalogue pages (S1, S6, S9), the audit slice (S7),
# and the train catalogue (H1, H2). Each is checked for the thing its screen cannot do without.
# =============================================================================================


def _catalogue(station: TestClient) -> Any:
    """The station's catalogue as the consoles parse it — Turtle, into an rdflib graph.

    The consoles parse this with N3 in the browser; here it is rdflib, which is the point: the
    document has to be readable by an ordinary RDF consumer, not only by the station's own
    tests. Three screens are built on it and none of them has a JSON projection to fall back to.
    """
    import rdflib

    response = station.get("/catalogue", headers={"Accept": "text/turtle"})
    assert response.status_code == 200, response.text
    graph = rdflib.Graph()
    graph.parse(data=response.text, format="turtle")
    return graph


def test_the_catalogue_carries_the_terms_and_not_only_a_link_to_them(
    watched: tuple[TestClient, TestClient, RunReport],
) -> None:
    """S9 and S6 render the controller's condition as a sentence. They can only do that if the
    offer's rules are *in* the catalogue — an `odrl:hasPolicy` pointing at an IRI that resolves
    nowhere leaves a public page with a dataset and no terms, which is the half a consumer has
    to read."""
    import rdflib

    station, _, _ = watched
    graph = _catalogue(station)
    odrl = rdflib.Namespace("http://www.w3.org/ns/odrl/2/")
    dataset = rdflib.URIRef("https://example.org/fdt/dataset/ut-gene-disease")

    offers = list(graph.subjects(odrl.target, dataset))
    assert offers, "the catalogue names no offer over the dataset it publishes"
    [offer] = [o for o in offers if (o, rdflib.RDF.type, odrl.Offer) in graph]
    # every rule the console draws a line for
    assert list(graph.objects(offer, odrl.permission)), "no permission travelled with the offer"
    assert list(graph.objects(offer, odrl.prohibition)), "no prohibition travelled with it"
    assert list(graph.objects(offer, odrl.obligation)), "no duty travelled with it"
    # and the duty's threshold, which is what "requires aggregates above k = 5" is made of
    thresholds = {
        str(value)
        for duty in graph.objects(offer, odrl.obligation)
        for constraint in graph.objects(duty, odrl.constraint)
        for value in graph.objects(constraint, odrl.rightOperand)
    }
    assert thresholds == {"5"}


def test_the_catalogue_names_its_network_so_a_console_need_not_invent_one(
    watched: tuple[TestClient, TestClient, RunReport],
) -> None:
    """The consoles show a condition as in force "in <network>". The network's title is in the
    station's self-description, which travels with the catalogue — so a reader of the catalogue
    alone has a name to show. Without it every screen falls back to the IRI's last segment, and
    the fallback is what `src/rdf/__tests__/policy.test.ts` pins when reading the bare fixture."""
    import rdflib

    station, _, _ = watched
    graph = _catalogue(station)
    network = rdflib.URIRef("https://example.org/fdt/net/health-research-nl")
    titles = [str(title) for title in graph.objects(network, rdflib.URIRef(
        "http://purl.org/dc/terms/title"))]
    assert titles == ["National health research network"]


def test_the_public_page_can_be_drawn_without_a_credential(
    watched: tuple[TestClient, TestClient, RunReport],
) -> None:
    """S9 is served to anyone. Everything it shows comes from two unauthenticated documents, and
    if either needed the operator credential the page would not exist."""
    station, _, _ = watched
    for path in ("/", "/catalogue", "/shapes"):
        response = station.get(path, headers={"Accept": "text/turtle"})
        assert response.status_code == 200, (path, response.status_code)
        assert response.text.strip(), path


def test_the_audit_slice_answers_a_question_the_visit_list_cannot(
    watched: tuple[TestClient, TestClient, RunReport],
) -> None:
    """S7, and finding 65.

    The question is "everything that happened to this dataset". Composed from the visit list it
    is answerable only for the visits on the page; asked of the station it is answerable for all
    of them, and the station says how many matched apart from how many it returned.
    """
    station, _, _ = watched
    everything = got(station, "/admin/events", headers=OPERATOR)
    on_the_dataset = got(
        station,
        "/admin/events?dataset=https://example.org/fdt/dataset/ut-gene-disease",
        headers=OPERATOR,
    )
    assert everything["total"] > 0
    assert on_the_dataset["matched"] == everything["matched"] > 0
    # every event carries the context that made the filter answerable at all
    for event in on_the_dataset["events"]:
        assert event["target"] == "https://example.org/fdt/dataset/ut-gene-disease"
        assert event["consumer"], "an audit row with no actor answers no audit question"
    # and the justification chain the screen draws is on the events, not assembled by it
    assert any(event.get("justification", {}).get("rule") for event in everything["events"])


def test_the_audit_slice_keeps_refused_and_rejected_apart(
    watched: tuple[TestClient, TestClient, RunReport],
) -> None:
    """ADR-026 through the filter. An auditor asking for a controller's refusals must not be
    handed results that failed inspection: a different party decided a different thing."""
    station, _, _ = watched
    refused = got(station, "/admin/events?state=Refused", headers=OPERATOR)
    rejected = got(station, "/admin/events?state=Rejected", headers=OPERATOR)
    delivered = got(station, "/admin/events?state=Delivered", headers=OPERATOR)
    assert delivered["matched"] > 0
    assert refused["matched"] == 0 and rejected["matched"] == 0
    # the station is not empty — the filter selected nothing, which is a different fact
    assert refused["total"] == delivered["total"] > 0


def test_the_handler_console_resolves_a_train_from_its_depot_and_not_the_index(
    watched: tuple[TestClient, TestClient, RunReport],
) -> None:
    """H1 and H2, and ADR-029.

    The registry says a train exists and where it was harvested from; the Depot says what it is.
    The screen resolves `source` + `id` and reads the description there. This checks that the
    registry publishes enough to make that possible, and that what comes back carries the parts
    H2 renders — the declared parameters and the input requirement that selects a station.
    """
    import rdflib

    from fdt_depot.api import build_app as build_depot
    from fdt_depot.core.config import DepotSettings
    from fdt_depot.core.contracts import Contracts as DepotContracts
    from fdt_registry.api import build_app as build_registry
    from fdt_registry.core.config import RegistrySettings, Source, SourceKind
    from fdt_registry.core.contracts import Contracts as RegistryContracts
    from fdt_registry.harvest.harvester import Harvester

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
    settings = RegistrySettings(
        iri="https://registry.example/fdt/v1",
        sources=(Source(url=depot_url, kind=SourceKind.DEPOT),),
        contracts_dir=COMMONS,
        ontology_dir=ONTOLOGY,
    )
    contracts = RegistryContracts(COMMONS, ONTOLOGY)
    harvester = Harvester(settings, contracts, clients={depot_url: depot})

    with depot, TestClient(build_registry(settings, contracts, harvester=harvester)) as reg:
        assert all(row["reached"] for row in reg.post("/harvest").json())
        indexed = reg.get("/trains").json()
        entry = next(
            train for train in indexed
            if train["iri"] == "https://example.org/fdt/train/gene-disease"
        )
        # the two fields the console follows back to the authority
        assert entry["source"] == depot_url
        assert entry["id"]
        described = depot.get(f"/trains/{entry['id']}", headers={"Accept": "text/turtle"})

    assert described.status_code == 200, described.text
    graph = rdflib.Graph()
    graph.parse(data=described.text, format="turtle")
    train = rdflib.URIRef("https://example.org/fdt/train/gene-disease")
    run = rdflib.Namespace("https://w3id.org/fdt/run#")
    fdt_o = rdflib.Namespace("https://w3id.org/fdt/fdt-o#")

    # H2 renders exactly these, and a plan that set anything else would set what the train
    # does not read
    names = {str(graph.value(parameter, run.name))
             for parameter in graph.objects(train, run.parameter)}
    assert names == {"mode", "terms", "min_evidence", "limit"}
    # ADR-030: this, and not the theme, is what selects a station
    assert graph.value(train, fdt_o.hasRequirement) is not None
    # and the digest the screen shows, which a station checks at PEP 1
    payload = graph.value(train, fdt_o.hasPayload)
    assert str(graph.value(payload, fdt_o.artifactDigest)).startswith("sha256:")


def test_the_registry_console_can_tell_never_harvested_from_unreachable(
    watched: tuple[TestClient, TestClient, RunReport],
) -> None:
    """Finding 67, from the console's side.

    `GET /sources` is where the registry explains an empty index, and it is where its 404 for an
    unknown train sends a reader. Before the first harvest it listed nothing at all — while
    `GET /` reported three sources in the same breath — so the page contradicted itself and gave
    no way to find out why.

    The distinction is not cosmetic. "Nobody has harvested yet" needs a harvest; "the station is
    down" needs somebody to go and look at the station. A console that painted both red as
    Unreachable sends whoever is on that screen after the wrong one.
    """
    from fdt_registry.api import build_app as build_registry
    from fdt_registry.core.config import RegistrySettings, Source, SourceKind
    from fdt_registry.core.contracts import Contracts as RegistryContracts
    from fdt_registry.harvest.harvester import Harvester

    station, _, _ = watched
    settings = RegistrySettings(
        iri="https://registry.example/fdt/v1",
        sources=(
            Source(url=STATION_URL, kind=SourceKind.STATION),
            Source(url="http://nothing.here.test", kind=SourceKind.STATION),
        ),
        contracts_dir=COMMONS,
        ontology_dir=ONTOLOGY,
    )
    contracts = RegistryContracts(COMMONS, ONTOLOGY)
    harvester = Harvester(settings, contracts, clients={STATION_URL: station})

    with TestClient(build_registry(settings, contracts, harvester=harvester)) as reg:
        before = {row["url"]: row for row in got(reg, "/sources")}
        described = got(reg, "/")
        reg.post("/harvest")
        after = {row["url"]: row for row in got(reg, "/sources")}

    # Before any harvest: every configured source is listed, and none of them has failed.
    assert len(before) == described["sources"] == 2
    for row in before.values():
        assert row["attempted"] is False
        assert row["reached"] is False
        assert row["error"] is None, "nothing was tried, so nothing failed"

    # After: the two are told apart, and the unreachable one keeps its place with its reason.
    assert after[STATION_URL]["attempted"] is True
    assert after[STATION_URL]["reached"] is True
    unreachable = after["http://nothing.here.test"]
    assert unreachable["attempted"] is True
    assert unreachable["reached"] is False
    assert unreachable["error"], "a source that could not be reached must say why"

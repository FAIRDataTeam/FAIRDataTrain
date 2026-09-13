"""One derivation rule, two evaluators — ADR-036, `protocol/train-publication.md` §3.

A station evaluates a data controller's offer over a dataset. A Depot evaluates a train
creator's licence over a train. ADR-036 is explicit that these must not fork: *whatever a
station concludes about a clause, a Depot must conclude about the same clause.* The rule is
`agreement-derivation.md`, and there is one of it.

The two implementations live in different repositories with no shared package, so nothing but a
test holds them together. Reading both and finding them similar is not that test: the clauses
that diverge are the ones that are hard, and they diverge quietly — an owner takes a train under
terms the Depot read one way, a station reads the same words the other way, and the disagreement
surfaces as a refused visit for an owner holding a licence that says they may.

So each case here is **one clause specification**, rendered twice: over a dataset for the station
and over a train for the Depot, with only the target and the assigner differing. Both are asked,
and the two verdicts are compared.

Where a Depot is *narrower* the test says so rather than papering over it: a Depot holds no
eligibility facts and has nobody to ask, so a clause the station settles from its own memberships
is one the Depot fails closed on. That asymmetry is in the inputs, not the rule, and the cases
that exercise it are marked.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest
import rdflib
from conftest import COMMONS, STATION_IRI
from fastapi.testclient import TestClient

from fdt_depot.core.config import DepotSettings
from fdt_depot.core.contracts import Contracts as DepotContracts
from fdt_depot.holdings import Holdings
from fdt_depot.licence import Agreed, LicenceEvaluator, Refused
from fdt_station.core.contracts import Contracts as StationContracts
from fdt_station.policy.evaluator import OdrlNegotiator

ODRL = rdflib.Namespace("http://www.w3.org/ns/odrl/2/")
FDT_P = rdflib.Namespace("https://w3id.org/fdt/profile#")
RDF = rdflib.RDF

ONTOLOGY = COMMONS.parent / "FDT-O"
NETWORK = "https://example.org/fdt/net/health-research-nl"
CONSUMER = "https://example.org/fdt/party/eu-cardionet-like"
CONTROLLER = "https://example.org/fdt/party/ut-controller"
CREATOR = "https://example.org/fdt/party/open-genomics-collective"
DATASET = "https://example.org/fdt/dataset/agreed-clause"
TRAIN = "https://example.org/fdt/train/gene-disease"
PAYLOAD_DIGEST = "sha256:0f2ea318c57bde07b025561f2333bbf0b0cb7ce75ed867ca72020ff60a7890b9"

RESEARCH = "https://w3id.org/dpv#ResearchAndDevelopment"
COMMERCIAL = "https://w3id.org/dpv#CommercialResearch"

Constraint = tuple[str, str, str]


@dataclass(frozen=True)
class Clause:
    """One licensing question, asked of both evaluators."""

    name: str
    permits: tuple[str, ...]
    offer_constraints: tuple[Constraint, ...]
    asks: tuple[str, ...]
    request_constraints: tuple[Constraint, ...]
    prohibits: tuple[str, ...] = ()


def _rule(graph: rdflib.Graph, policy: rdflib.URIRef, prop: rdflib.URIRef,
          action: str, constraints: tuple[Constraint, ...]) -> None:
    rule = rdflib.BNode()
    graph.add((policy, prop, rule))
    graph.add((rule, RDF.type,
               ODRL.Permission if prop == ODRL.permission else ODRL.Prohibition))
    graph.add((rule, ODRL.action, rdflib.URIRef(action)))
    for left, operator, value in constraints:
        node = rdflib.BNode()
        graph.add((rule, ODRL.constraint, node))
        graph.add((node, ODRL.leftOperand, rdflib.URIRef(left)))
        graph.add((node, ODRL.operator, rdflib.URIRef(operator)))
        graph.add((node, ODRL.rightOperand, rdflib.URIRef(value)))


def offer_over(clause: Clause, *, target: str, assigner: str,
               iri: str) -> tuple[rdflib.Graph, rdflib.URIRef]:
    """The same clause, over whichever asset the evaluator being asked is about."""
    graph = rdflib.Graph()
    offer = rdflib.URIRef(iri)
    graph.add((offer, RDF.type, ODRL.Offer))
    graph.add((offer, ODRL.profile, rdflib.URIRef("https://w3id.org/fdt/profile")))
    graph.add((offer, ODRL.target, rdflib.URIRef(target)))
    graph.add((offer, ODRL.assigner, rdflib.URIRef(assigner)))
    graph.add((offer, FDT_P.policyKind, FDT_P.AccessPolicy))
    graph.add((offer, FDT_P.underNetwork, rdflib.URIRef(NETWORK)))
    graph.add((rdflib.URIRef(target), ODRL.hasPolicy, offer))
    for action in clause.permits:
        _rule(graph, offer, ODRL.permission, action, clause.offer_constraints)
    for action in clause.prohibits:
        _rule(graph, offer, ODRL.prohibition, action, ())
    return graph, offer


def request_document(clause: Clause, *, target: str, train: str) -> dict[str, Any]:
    """The would-be consumer's request, as JSON-LD — the spelling a visit descriptor carries."""
    return {
        "@context": "http://www.w3.org/ns/odrl.jsonld",
        "@type": "Request",
        "@id": "https://example.org/fdt/request/agreed-clause",
        "profile": "https://w3id.org/fdt/profile",
        "target": target,
        "assignee": CONSUMER,
        "https://w3id.org/fdt/profile#train": {"@id": train},
        "https://w3id.org/fdt/profile#underNetwork": {"@id": NETWORK},
        "permission": [
            {
                "@type": "Permission",
                "action": action,
                "constraint": [
                    {"leftOperand": left, "operator": operator,
                     "rightOperand": {"@id": value}}
                    for left, operator, value in clause.request_constraints
                ],
            }
            for action in clause.asks
        ],
    }


class OneOffer:
    """An `OfferSource` holding exactly the offer under test, and nothing else.

    The contracts' fixture offers are deliberately absent: a case that fell through to one of
    them would be comparing the Depot's answer about this clause with the station's answer about
    a different one, and would pass.
    """

    def __init__(self, graph: rdflib.Graph, offer: rdflib.URIRef, contracts: Any) -> None:
        self._graph = graph + contracts.vocabularies
        self._offer = offer

    @property
    def graph(self) -> rdflib.Graph:
        return self._graph

    def offers_for(self, dataset: str, network: str) -> list[rdflib.URIRef]:
        if str(self._graph.value(self._offer, ODRL.target)) != dataset:
            return []
        if rdflib.URIRef(network) not in set(self._graph.objects(self._offer,
                                                                FDT_P.underNetwork)):
            return []
        return [self._offer]


def verdict(graph: rdflib.Graph, agreement: rdflib.term.Node) -> dict[str, Any]:
    """What was granted, in a form the two evaluators can be compared on."""
    granted: dict[str, set[tuple[str, str, str]]] = {}
    for rule in graph.objects(agreement, ODRL.permission):
        for action in graph.objects(rule, ODRL.action):
            terms = {
                (str(graph.value(c, ODRL.leftOperand)),
                 str(graph.value(c, ODRL.operator)),
                 str(value))
                for c in graph.objects(rule, ODRL.constraint)
                for value in graph.objects(c, ODRL.rightOperand)
            }
            granted[str(action)] = terms
    return {"state": "granted", "actions": granted}


def ask_the_station(clause: Clause, station_settings: Any) -> dict[str, Any]:
    contracts = StationContracts(COMMONS)
    graph, offer = offer_over(clause, target=DATASET, assigner=CONTROLLER,
                              iri="https://example.org/fdt/offer/agreed-clause-data")
    negotiator = OdrlNegotiator(station_settings, contracts,
                                offers=OneOffer(graph, offer, contracts))
    outcome = negotiator.negotiate({
        "visit": "https://example.org/fdt/visit/agreed-clause",
        "target": DATASET,
        "network": NETWORK,
        "consumer": {"party": CONSUMER},
        "train": {"iri": TRAIN},
        "payload": {"digest": PAYLOAD_DIGEST},
        "negotiation": {"request": request_document(clause, target=DATASET, train=TRAIN)},
    })
    if outcome.state != "active":
        return {"state": outcome.state, "reason": outcome.reason or ""}
    document = outcome.agreement_document or {}
    return verdict(document["graph"], rdflib.URIRef(str(outcome.agreement)))


def ask_the_depot(clause: Clause, tmp_path: Path) -> dict[str, Any]:
    contracts = DepotContracts(COMMONS, ONTOLOGY)
    graph, offer = offer_over(clause, target=TRAIN, assigner=CREATOR,
                              iri="https://example.org/fdt/offer/agreed-clause-train")

    holdings = Holdings.load(contracts)
    train = holdings.by_id("gene-disease")
    assert train is not None
    # the train's own licence, replaced with the clause under test: `offer_for` reads the
    # description, so this is the offer the evaluator will find
    described = train.description
    for existing in list(described.subjects(RDF.type, ODRL.Offer)):
        for triple in list(described.triples((existing, None, None))):
            described.remove(triple)
        described.remove((rdflib.URIRef(TRAIN), ODRL.hasPolicy, existing))
    described += graph

    settings = DepotSettings(iri="https://example.org/fdt/depot/community",
                             base_url="http://depot.test/fdt/v1",
                             contracts_dir=COMMONS, ontology_dir=ONTOLOGY,
                             store_dir=tmp_path / "store")
    outcome = LicenceEvaluator(settings, contracts).evaluate(
        train,
        json.dumps(request_document(clause, target=TRAIN, train=TRAIN)),
        "application/ld+json",
    )
    if isinstance(outcome, Refused):
        return {"state": "refused", "reason": outcome.detail}
    assert isinstance(outcome, Agreed), outcome
    return verdict(outcome.graph, rdflib.URIRef(outcome.iri))


AGREE = [
    Clause(
        name="a purpose the offer admits is granted as asked",
        permits=(str(ODRL.execute),),
        offer_constraints=((str(ODRL.purpose), str(ODRL.eq), RESEARCH),),
        asks=(str(ODRL.execute),),
        request_constraints=((str(ODRL.purpose), str(ODRL.eq), RESEARCH),),
    ),
    Clause(
        name="a purpose the offer does not admit is bounded, not refused",
        permits=(str(ODRL.execute),),
        offer_constraints=((str(ODRL.purpose), str(ODRL.eq), RESEARCH),),
        asks=(str(ODRL.execute),),
        request_constraints=((str(ODRL.purpose), str(ODRL.eq), COMMERCIAL),),
    ),
    Clause(
        name="an action the offer does not permit is not granted",
        permits=(str(ODRL.read),),
        offer_constraints=((str(ODRL.purpose), str(ODRL.eq), RESEARCH),),
        asks=(str(ODRL.execute),),
        request_constraints=((str(ODRL.purpose), str(ODRL.eq), RESEARCH),),
    ),
    Clause(
        name="a prohibited action is refused and nobody may waive it",
        permits=(str(ODRL.execute),),
        offer_constraints=((str(ODRL.purpose), str(ODRL.eq), RESEARCH),),
        asks=(str(ODRL.execute),),
        request_constraints=((str(ODRL.purpose), str(ODRL.eq), RESEARCH),),
        prohibits=(str(ODRL.execute),),
    ),
]


@pytest.mark.parametrize("clause", AGREE, ids=lambda c: c.name)
def test_the_station_and_the_depot_read_the_same_clause_the_same_way(
    clause: Clause, station_settings: Any, tmp_path: Path
) -> None:
    station = ask_the_station(clause, station_settings)
    depot = ask_the_depot(clause, tmp_path)

    assert station["state"] == depot["state"], (
        f"{clause.name}: the station says {station['state']} and the Depot says "
        f"{depot['state']}. ADR-036: whatever a station concludes about a clause, a Depot must "
        f"conclude about the same clause."
    )
    if station["state"] == "granted":
        assert station["actions"] == depot["actions"], clause.name


def test_the_depot_fails_closed_where_the_station_can_establish_the_fact(
    station_settings: Any, tmp_path: Path
) -> None:
    """The one asymmetry, stated rather than discovered.

    `fdt-p:processingLocation` is an eligibility operand a station settles from its own
    configuration — it knows where it processes. A Depot knows nothing about who is asking
    beyond what they have just claimed, so the same clause fails closed there.

    This is a difference of **inputs and not of rule**: both implementations apply
    "an eligibility fact that is not evidenced is not assumed". Asserting it here keeps it from
    being mistaken, later, for the fork ADR-036 forbids — and keeps a future change that quietly
    made the Depot credulous from passing as an improvement.
    """
    clause = Clause(
        name="an eligibility fact",
        permits=(str(ODRL.execute),),
        offer_constraints=(
            (str(ODRL.purpose), str(ODRL.eq), RESEARCH),
            (str(FDT_P.processingLocation), str(ODRL.eq), "https://example.org/fdt/loc/nl"),
        ),
        asks=(str(ODRL.execute),),
        request_constraints=((str(ODRL.purpose), str(ODRL.eq), RESEARCH),),
    )
    depot = ask_the_depot(clause, tmp_path)
    assert depot["state"] == "refused"
    assert "processingLocation" in depot["reason"]
    assert "fails closed" in depot["reason"]

    # and the station, which knows where it is, does not fail closed on it for the wrong reason:
    # it compares the fact it holds with the one the offer requires.
    station = ask_the_station(clause, station_settings)
    assert station["state"] in {"granted", "refused"}
    if station["state"] == "refused":
        assert "processingLocation" in station["reason"]


def test_the_depot_never_assigns_a_licence_it_does_not_hold(tmp_path: Path) -> None:
    """`invalid/train-taken-from-someone-who-did-not-write-it.ttl`, as a property of the code.

    That counter-example is an agreement granting rights over a train, assigned by a party that
    never held them. It is otherwise impeccable — real offer, real request, all three digests
    pinned — and the one thing wrong with it is the one thing that decides whether any of it
    means anything.

    The Depot cannot produce it, and not because it checks: the assigner is read from the offer,
    and the offer is the creator's. The assertion is that this stays true.
    """
    clause = AGREE[0]
    contracts = DepotContracts(COMMONS, ONTOLOGY)
    holdings = Holdings.load(contracts)
    train = holdings.by_id("gene-disease")
    assert train is not None

    settings = DepotSettings(iri="https://example.org/fdt/depot/community",
                             base_url="http://depot.test/fdt/v1",
                             contracts_dir=COMMONS, ontology_dir=ONTOLOGY)
    outcome = LicenceEvaluator(settings, contracts).evaluate(
        train,
        json.dumps(request_document(clause, target=TRAIN, train=TRAIN)),
        "application/ld+json",
    )
    assert isinstance(outcome, Agreed)
    assigner = str(outcome.graph.value(rdflib.URIRef(outcome.iri), ODRL.assigner))
    assert assigner == CREATOR
    assert assigner != "https://example.org/fdt/party/fdt-community-depot"
    assert assigner != CONSUMER


def test_the_depot_is_reachable_over_http_the_way_a_station_would_reach_it() -> None:
    """The whole surface, from outside: the write operations are HTTP, not a Python API."""
    from fdt_depot.api import build_app

    settings = DepotSettings(iri="https://example.org/fdt/depot/community",
                             base_url="http://depot.test/fdt/v1",
                             contracts_dir=COMMONS, ontology_dir=ONTOLOGY)
    with TestClient(build_app(settings, DepotContracts(COMMONS, ONTOLOGY))) as client:
        assert client.get("/").json()["depot"] == "https://example.org/fdt/depot/community"
        # a read-only Depot says what it is rather than losing a submission
        assert client.post("/trains", json={}).status_code == 501
        assert STATION_IRI  # the station's IRI is what an agreement over data would name

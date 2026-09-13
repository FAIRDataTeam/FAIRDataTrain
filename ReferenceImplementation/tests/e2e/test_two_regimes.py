"""WP-5.4 — two networks that differ on whether a machine may decide (ADR-032).

The decision ADR-032 records is a legal one wearing technical clothes, and the only way to tell
whether an implementation took it is to run the same request under both regimes and watch what
comes back. That is what this does. Nothing is stubbed: two stations, both real, both reading
the same contracts, differing in their network membership and in what their controllers offered.

Three things are shown, and the third is the one that is easy to get wrong.

* **The same train, two stations, two agreements.** The university station's controller asks for
  aggregates of at least five; the clinical genetics station's asks for ten. Same train, same
  request, different terms — because conditions belong to controllers, not to trains (ADR-014).
* **The same commercial request, refused by a machine where that is permitted.** The offer
  prohibits `odrl:sell` and the request asks for it; in `health-research-nl` the station says so
  and the visit ends Refused.
* **The same request, in a network that bars automated authorisation, is not refused at all.**
  It waits for a person, carrying the station's recommendation and the evidence behind it. A
  machine forbidden to grant is forbidden to refuse, because both are adverse decisions taken
  about somebody's request — and the grounds being clear-cut is not the station's call to make.
"""

from __future__ import annotations

import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
import rdflib
from fastapi.testclient import TestClient
from pydantic import AnyHttpUrl

from fdt_station.app import create_app
from fdt_station.core.config import (
    Adapter,
    DecisionMode,
    HostedDataset,
    NetworkMembership,
    StationSettings,
)

from conftest import COMMONS, STATION_IRI, STATION_URL

HEALTH_RESEARCH = "https://example.org/fdt/net/health-research-nl"
STROKE_OOST = "https://example.org/fdt/net/stroke-oost"
OOSTERLICHT_IRI = "https://example.org/fdt/station/oosterlicht"
OOSTERLICHT_URL = "http://station.oosterlicht.test"
GENE_DISEASE = "https://example.org/fdt/dataset/ut-gene-disease"
OOSTERLICHT_DATA = "https://example.org/fdt/dataset/oosterlicht-gene-disease"

FDT_P = rdflib.Namespace("https://w3id.org/fdt/profile#")
ODRL = rdflib.Namespace("http://www.w3.org/ns/odrl/2/")


def _membership(network: str, *, automated: bool, authority: str, issuer: str,
                title: str) -> NetworkMembership:
    return NetworkMembership(
        network=AnyHttpUrl(network),
        network_title=title,
        governance_authority=AnyHttpUrl(authority),
        governance_authority_name="Governance authority",
        admits_natural_persons=False,
        permits_automated_decision=automated,
        trusted_issuer=AnyHttpUrl(issuer),
        role=AnyHttpUrl("https://w3id.org/fdt/network#StationRole"),
        credential=AnyHttpUrl(f"{network}/credential"),
    )


HRI = _membership(HEALTH_RESEARCH, automated=True,
                  authority="https://example.org/fdt/auth/hri-like",
                  issuer="https://idp.example.org/ls-aai-like",
                  title="National health research network")
#: The regime that bars automated authorisation — and therefore automated refusal (ADR-032).
OOST = _membership(STROKE_OOST, automated=False,
                   authority="https://example.org/fdt/auth/roaz-oost",
                   issuer="https://idp.example.org/surfconext-like",
                   title="Stroke network Oost (regional acute-care network)")


@pytest.fixture
def oosterlicht() -> Iterator[TestClient]:
    """A station in both networks, holding data the gene–disease train can read.

    Two memberships and two offers over one dataset is not a contrivance: it is ADR-017's rule
    in a fixture. Conditions are evaluated per network, and a dataset offered in one network is
    not thereby offered in another.
    """
    settings = StationSettings(
        # ADR-034: these scenarios are about what the negotiation rule decides, so
        # the operator's own dial is stated. A production station defaults to
        # `manual`, and a scenario that relied on the default would be exercising
        # the default rather than the rule it was written for.
        decision_mode=DecisionMode.AUTOMATED,
        iri=AnyHttpUrl(OOSTERLICHT_IRI),
        title="Oosterlicht MC station (clinical genetics, fictional)",
        owner_name="Oosterlicht MC — clinical genetics IT",
        base_url=AnyHttpUrl(OOSTERLICHT_URL),
        catalog_iri=AnyHttpUrl("https://example.org/fdt/catalog/oosterlicht"),
        adapters=frozenset({Adapter.SPARQL}),
        auth_required=False,
        contracts_dir=COMMONS,
        memberships=(OOST, HRI),
        datasets=(
            HostedDataset(
                iri=AnyHttpUrl(OOSTERLICHT_DATA),
                adapter=Adapter.SPARQL,
                source=COMMONS / "examples" / "data" / "ut-gene-disease.ttl",
            ),
        ),
    )
    with TestClient(create_app(settings), base_url=OOSTERLICHT_URL) as client:
        yield client


@pytest.fixture
def ut(station_settings: StationSettings) -> Iterator[TestClient]:
    with TestClient(create_app(station_settings), base_url=STATION_URL) as client:
        yield client


def _descriptor(target: str, station: str, network: str, *, visit: str,
                selling: bool = False, purpose: str | None = None) -> dict[str, Any]:
    """The M1 descriptor, re-aimed. Everything else about it is the fixture's."""
    source = COMMONS / "examples" / "protocol" / "visit-descriptor-gd-m1.json"
    descriptor: dict[str, Any] = json.loads(source.read_text())
    descriptor["visit"] = visit
    descriptor["target"] = target
    descriptor["network"] = network
    descriptor["reporting"] = {"mode": "poll"}
    request = descriptor["negotiation"]["request"]
    request["target"] = target
    request["underNetwork"] = network
    if purpose is not None:
        for permission in request["permission"]:
            for constraint in permission.get("constraint", []):
                if constraint.get("leftOperand") == "purpose":
                    constraint["rightOperand"] = purpose
    if selling:
        request["permission"].append(
            {"@type": "Permission", "action": "http://www.w3.org/ns/odrl/2/sell"}
        )
    return descriptor


def _agreement(station: TestClient, visit: str) -> rdflib.Graph:
    """The agreement the station concluded, fetched from the station that concluded it."""
    events = station.get(f"/visits/{visit}/events").json()
    iri = next(e["agreement"] for e in events if e.get("agreement"))
    response = station.get(f"/agreements/{iri}")
    assert response.status_code == 200, response.text
    graph = rdflib.Graph()
    graph.parse(data=response.text, format="json-ld")
    return graph


def _threshold(graph: rdflib.Graph) -> int:
    for duty in graph.objects(predicate=ODRL.obligation):
        for constraint in graph.objects(duty, ODRL.constraint):
            if graph.value(constraint, ODRL.leftOperand) == FDT_P.kAnonymity:
                return int(graph.value(constraint, ODRL.rightOperand))  # type: ignore[arg-type]
    raise AssertionError("the agreement carries no k-anonymity duty")


def test_the_same_train_at_two_stations_gets_two_different_agreements(
    ut: TestClient, oosterlicht: TestClient
) -> None:
    """ADR-014: one agreement per hop, on the terms of the controller whose data it is.

    Both stations auto-conclude here — both are in the network that permits it — so the only
    thing that differs is what the two controllers asked for. A Handler that reused the first
    agreement at the second station would be running under terms nobody at that station set.
    """
    here = _descriptor(GENE_DISEASE, STATION_IRI, HEALTH_RESEARCH, visit="visit-two-regimes-a")
    there = _descriptor(OOSTERLICHT_DATA, OOSTERLICHT_IRI, HEALTH_RESEARCH,
                        visit="visit-two-regimes-b")

    assert ut.post("/visits", json=here).status_code == 202
    assert oosterlicht.post("/visits", json=there).status_code == 202

    first, second = _agreement(ut, here["visit"]), _agreement(oosterlicht, there["visit"])
    assert _threshold(first) == 5
    assert _threshold(second) == 10
    assert set(first.objects(predicate=ODRL.assigner)) != set(
        second.objects(predicate=ODRL.assigner)
    )
    for graph in (first, second):
        assert FDT_P.AutomaticPermitted in set(graph.objects(predicate=FDT_P.authorisationMode))


def test_the_commercial_request_is_refused_by_a_machine_where_that_is_permitted(
    ut: TestClient,
) -> None:
    """Q14-C, and the one path that exercises an ODRL prohibition end to end."""
    descriptor = _descriptor(GENE_DISEASE, STATION_IRI, HEALTH_RESEARCH,
                             visit="visit-two-regimes-commercial-hri", selling=True,
                             purpose="https://w3id.org/dpv#CommercialResearch")
    response = ut.post("/visits", json=descriptor)

    # Refused on the spot, with the ADR-026 word in the body. The station answers the question
    # it was asked rather than accepting the visit and reporting the refusal later.
    assert response.status_code == 403
    body = response.json()
    assert body["outcome"] == "Refused"
    assert body["checkpoint"] == "NEG"
    assert "prohibits sell" in body["detail"]
    assert body["justification"]["evidence"]["prohibition"].endswith("sell")
    assert "approval" not in body, "nobody was asked; a machine decided"


def test_the_same_request_in_the_other_network_waits_for_a_person(
    oosterlicht: TestClient,
) -> None:
    """ADR-032, and WP-5.4's reason for existing.

    The identical request, at a station whose network bars automated authorisation. The grounds
    are as clear-cut as grounds get and the station still does not act on them: it evaluates,
    recommends refusing, names the rule that put a person in the loop, and waits.

    The outcome word is the part a console must not get wrong. This is **not** Refused — no
    controller has decided anything — and reporting it as one would present a machine's analysis
    as a party's decision (ADR-026).
    """
    descriptor = _descriptor(OOSTERLICHT_DATA, OOSTERLICHT_IRI, STROKE_OOST,
                             visit="visit-two-regimes-commercial-oost", selling=True,
                             purpose="https://w3id.org/dpv#CommercialResearch")
    response = oosterlicht.post("/visits", json=descriptor)
    assert response.status_code == 202

    events = oosterlicht.get(f"/visits/{descriptor['visit']}/events").json()
    last = events[-1]
    assert last["type"] == "negotiation.pending-approval"
    assert last["state"] == "PendingApproval"
    assert last["state"] not in ("Refused", "Rejected")

    approval = last["approval"]
    assert approval["recommendation"] == "refuse"
    assert approval["mode"] == "HumanRequiredByRegulation"
    assert approval["rule"] == STROKE_OOST
    assert approval["controller"] == "https://example.org/fdt/party/oosterlicht-genetics"

    # the analysis goes with it: the person is shown what the machine would have acted on
    assert "prohibits sell" in last["message"]
    assert last["justification"]["evidence"]["prohibition"].endswith("sell")


def test_no_train_runs_while_a_person_has_not_decided(oosterlicht: TestClient) -> None:
    """The recommendation is not a grant, and nothing about it lets a visit proceed.

    PEP 2 requires an active agreement, and there is none: the person has not decided, so no
    agreement exists to be active. This is the check that would fail if "pending approval" were
    implemented as "approved, pending paperwork".
    """
    descriptor = _descriptor(OOSTERLICHT_DATA, OOSTERLICHT_IRI, STROKE_OOST,
                             visit="visit-two-regimes-waiting")
    oosterlicht.post("/visits", json=descriptor)
    events = oosterlicht.get(f"/visits/{descriptor['visit']}/events").json()

    assert events[-1]["type"] == "negotiation.pending-approval"
    assert events[-1]["approval"]["recommendation"] == "grant", (
        "everything matched — and matching is not concluding"
    )
    assert not [e for e in events if e["type"] in ("visit.running", "visit.delivered")]
    assert oosterlicht.get(f"/visits/{descriptor['visit']}/result").status_code in (404, 409)

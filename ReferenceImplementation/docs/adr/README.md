# Architecture decision records

Every architectural decision this implementation is built on, in this repository. Forty of
them, and the code cites them by number throughout — in the shapes, the fixtures, the
checkpoint modules and the plan.

## ADR-001–027 — the architecture

Extracted verbatim from the two normative documents, which remain the source: the **station
architecture** (ADR-001–013) and the **ecosystem architecture** (ADR-014–027), both in
[`../architecture/`](../architecture/). Each file carries a `Source` line saying where it came
from. **Edit the source document and re-extract**; do not edit these in place, or the two drift
and nobody can tell which is current.

| ADR | Decision | Status |
|---|---|---|
| [**001**](ADR-001-python-fastapi-for-the-station-core.md) | Python + FastAPI for the station core | Accepted (2026-07-02) |
| [**002**](ADR-002-build-time-adapter-modules-behind-a-stable-spi.md) | Build-time adapter modules behind a stable SPI ("pragmatic middle path") | Accepted |
| [**003**](ADR-003-docker-executor-is-process-isolated-from-the.md) | Docker executor is process-isolated from the start | Accepted |
| [**004**](ADR-004-support-both-push-and-poll-dispatch.md) | Support both push and poll dispatch | Accepted |
| [**005**](ADR-005-new-fairdatastation-repo-language-neutral-fdt.md) | New `FAIRDataStation` repo + language-neutral `fdt-commons` | Accepted |
| [**006**](ADR-006-conform-to-the-fdp-specification-do-not-reuse.md) | Conform to the FDP specification; do not reuse FDP code | Accepted |
| [**007**](ADR-007-odrl-for-conditions-requests-and-agreements.md) | ODRL for conditions, requests, and agreements; evaluator behind an interface | Accepted |
| [**008**](ADR-008-automated-matching-with-optional-human-in-the.md) | Automated matching with optional human-in-the-loop approval | Accepted |
| [**009**](ADR-009-align-negotiation-with-the-dataspace-protocol.md) | Align negotiation with the Dataspace Protocol "where cheap" | Accepted |
| [**010**](ADR-010-federated-oidc-now-vc-ready-party-model.md) | Federated OIDC now; VC-ready party model | Accepted |
| [**011**](ADR-011-data-controller-station-owner-multi-tenant.md) | Data controller ≠ station owner; multi-tenant policy administration | Accepted |
| [**012**](ADR-012-one-architecture-deployment-profiles-for-scale.md) | One architecture, deployment profiles for scale | Accepted |
| [**013**](ADR-013-support-both-orchestrated-and-choreographed.md) | Support both orchestrated and choreographed multi-station itineraries | Accepted in principle (2026-09-11); realisation per pattern pending the itinerary-pattern analysis (`fdt-itinerary-patterns.md`) |
| [**014**](ADR-014-agreements-per-hop-negotiated-on-arrival.md) | Agreements per hop, negotiated on arrival | Accepted (2026-09-11) |
| [**015**](ADR-015-the-train-handler-holds-non-personal-aggregate.md) | The Train Handler holds non-personal, aggregate data only | Accepted |
| [**016**](ADR-016-three-mechanisms-for-state-between-hops-peer.md) | Three mechanisms for state between hops; peer forwarding deferred to v2 | Accepted |
| [**017**](ADR-017-federated-governance-stations-may-belong-to.md) | Federated governance; stations may belong to several networks | Accepted |
| [**018**](ADR-018-natural-persons-as-controllers-participation-by.md) | Natural persons as controllers: participation by deployment profile | Accepted |
| [**019**](ADR-019-dataspace-protocol-conformance-in-two-steps.md) | Dataspace Protocol conformance in two steps | Accepted |
| [**020**](ADR-020-trains-are-contracted-assets-executables-not.md) | Trains are contracted assets (executables, not datasets); the Garage is a catalogue of train offers | Accepted; **amended 11 Sep 2026** after the `fdt-commons` probe |
| [**021**](ADR-021-gaia-x-alignable-not-compliant.md) | Gaia-X: alignable, not compliant | Accepted |
| [**022**](ADR-022-linkage-station-as-an-fdt-o-station-type.md) | Linkage Station as an FDT-O station type | Accepted |
| [**023**](ADR-023-run-description-vocabulary-in-fdt-commons.md) | Run-description vocabulary in `fdt-commons` | Accepted |
| [**024**](ADR-024-cross-domain-alignment-through-alignment.md) | Cross-domain alignment through alignment services and self-description | Accepted |
| [**025**](ADR-025-conditions-in-plans-are-jmespath-predicates-over.md) | Conditions in plans are JMESPath predicates over JSON evaluation envelopes | Accepted (proposed 11 Sep 2026; confirmed by Luiz 12 Sep 2026). **Decision** below stands as decided; the JMESPath expressions of the example plans still await a run through an engine (`fdt-commons/tests/conditions-check.html`) |
| [**026**](ADR-026-visit-outcomes-failure-policy-and-completeness.md) | Visit outcomes, failure policy and completeness statement | Accepted (proposed 11 Sep 2026; confirmed by Luiz 12 Sep 2026) |
| [**027**](ADR-027-the-visit-protocol-is-the-ecosystem-s-data-plane.md) | The visit protocol is the ecosystem's data plane: descriptor, events, envelope, two dispatch directions | Accepted (12 Sep 2026; requested by Luiz as the next contract to define) |

## ADR-028 onward — decisions taken during implementation

Drafted here, as `CLAUDE.md` requires: an architectural decision that changes what the
implementation may do gets a record with Context, Decision, Alternatives and Consequences, and
the affected work package stops until Luiz accepts it. ADR-030 to ADR-033 were taken in the
decision interview of 13 September 2026, which closed every question blocking M2 and M5.

| ADR | Decision | Status |
|---|---|---|
| [**028**](ADR-028-counter-signed-agreements.md) | Agreements are counter-signed by the train owner | **Accepted**, 13 September 2026 |
| [**029**](ADR-029-train-depot-and-metadata-registry.md) | The Train Depot, and one metadata registry for stations and trains | **Accepted**, 12 September 2026 |
| [**030**](ADR-030-train-data-requirements-and-station-selection.md) | A train declares the data it needs, and that is what selects a station | **Accepted**, 13 September 2026 |
| [**031**](ADR-031-credentials-and-eligibility-evidence.md) | A credential proves what metadata only names | **Accepted**, 13 September 2026 |
| [**032**](ADR-032-when-a-machine-may-not-decide.md) | Where a machine may not grant, it may not refuse either | **Accepted**, 13 September 2026 |
| [**033**](ADR-033-dataset-parts.md) | A controller may offer part of a dataset | **Accepted**, 13 September 2026 |
| [**034**](ADR-034-run-modes-and-the-station-decision-mode.md) | Run modes supply defaults; a station's decision mode narrows, never widens | **Accepted**, 13 September 2026 |
| [**035**](ADR-035-standing-at-a-station.md) | Standing: who may act at a station, and on whose behalf | **Accepted**, 13 September 2026 |
| [**036**](ADR-036-train-creator-train-owner-and-the-depot.md) | A train's three parties, and what a Depot may be asked to do | **Accepted**, 13 September 2026 |
| [**037**](ADR-037-a-depot-is-a-station-for-trains.md) | A Depot is a station for trains; a creator is asked through their Gateway | **Accepted**, 13 September 2026 |
| [**038**](ADR-038-both-parties-sign-the-agreement.md) | Both parties sign the agreement, and it records who signed for whom | **Accepted**, 13 September 2026 |
| [**039**](ADR-039-delegated-standing-and-the-auditor.md) | A controller may delegate to a named party; the auditor reads and writes nothing | **Accepted**, 13 September 2026 |
| [**040**](ADR-040-a-depot-pings-its-registry.md) | A Depot pings its registry; the registry announces nothing | **Accepted**, 13 September 2026 |

## The rule

A change to an architectural decision means a new ADR with status **Proposed**, and the affected
work package stops until Luiz accepts it. Decisions Luiz takes directly in a session are drafted
here as **Accepted**, with the date and the session recorded, so the reasoning survives the
conversation it was taken in.

Open questions that are not yet decisions live in
[`../../OPEN-QUESTIONS.md`](../../OPEN-QUESTIONS.md), each with the conservative default in force
until it is answered. Contract defects found by building against the contracts are numbered in
[`../../fdt-commons/FINDINGS.md`](../../fdt-commons/FINDINGS.md).

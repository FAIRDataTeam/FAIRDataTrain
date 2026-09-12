# ADR-013 — Support both orchestrated and choreographed multi-station itineraries

| | |
|---|---|
| **Status** | Accepted in principle (2026-09-11); realisation per pattern pending the itinerary-pattern analysis (`fdt-itinerary-patterns.md`). |
| **Deciders** | Luiz Olavo Bonino da Silva Santos |
| **Source** | Extracted verbatim on 12 September 2026 from *FAIR Data Station — Architecture (station component), v0.3*, §Architecture Decision Records (`docs/architecture/fair-data-station-architecture.md` in this repository, `FAIR Data Train/fair-data-station-architecture/` in the project folder). The source document remains normative; edit there and re-extract. |

## Context

Analyses such as *time-to-groin* require trains to visit a sequence of stations that is discovered hop by hop; other patterns (iterative rounds, two-phase conditional dispatch, dependent trains) need coordination across visits. Query and API trains carry no logic and can only be coordinated externally; script and container trains can embed routing.

## Decision

The ecosystem supports **orchestration** (an external coordinator — by default the Train Handler — decides successive visits from hop results) **and choreography** (the routing algorithm is embedded in the train). Ecosystem elements may play orchestrator and choreographer roles; the station remains agnostic to who coordinates but must expose what each style needs.

## Alternatives

orchestration only (simpler stations, but forces every analysis through a Handler that sees intermediate results and excludes autonomous container trains); choreography only (excludes all query/API trains).

## Consequences

the station's result-inspection checkpoint (PEP 3) must distinguish *results delivered to the consumer* from *state travelling onward*; agreement lifecycle must accommodate multi-hop runs (scope and mid-chain approvals); station-to-station forwarding and run-level provenance become design items; the Handler's `Run` model evolves from a set of independent jobs to dependent jobs/phases.

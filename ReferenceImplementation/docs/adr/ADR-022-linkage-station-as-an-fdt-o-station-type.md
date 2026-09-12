# ADR-022 — Linkage Station as an FDT-O station type

| | |
|---|---|
| **Status** | Accepted. |
| **Deciders** | Luiz Olavo Bonino da Silva Santos |
| **Source** | Extracted verbatim on 12 September 2026 from *FAIR Data Train — Ecosystem Architecture, v0.1.4*, §Architecture Decision Records (`docs/architecture/fdt-ecosystem-architecture.md` in this repository, `FAIR Data Train/fair-data-station-architecture/` in the project folder). The source document remains normative; edit there and re-extract. |

## Context

Cross-organisation patterns need identifier translation without exposing identities; health uses trusted third parties, other domains shared persistent identifiers.

## Decision

FDT-O gains a *LinkageStation* type whose interaction mechanism is identifier translation between pseudonym spaces; it is visited as a hop under its own agreement; existing TTPs can be wrapped; datasets declare the pseudonym spaces and join keys they support.

## Alternatives

dataset capability only; outside FDT scope.

## Consequences

a reference linkage station in v1; the visit protocol carries pseudonym translation requests; the itinerary map shows linkage hops.

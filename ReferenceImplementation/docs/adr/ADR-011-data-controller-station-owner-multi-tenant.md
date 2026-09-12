# ADR-011 — Data controller ≠ station owner; multi-tenant policy administration

| | |
|---|---|
| **Status** | Accepted. |
| **Deciders** | Luiz Olavo Bonino da Silva Santos |
| **Source** | Extracted verbatim on 12 September 2026 from *FAIR Data Station — Architecture (station component), v0.3*, §Architecture Decision Records (`docs/architecture/fair-data-station-architecture.md` in this repository, `FAIR Data Train/fair-data-station-architecture/` in the project folder). The source document remains normative; edit there and re-extract. |

## Context

Stations host data from many providers; authority over data and control of infrastructure are different concerns.

## Decision

Controller and owner are distinct first-class roles; the PAP is multi-tenant; effective decisions are the conjunction of controller offer and owner station policy; every resource carries a controller binding.

## Alternatives

*Not recorded in the source document for this decision.*

## Consequences

FDT-O extension required (Section 11); personal stations work as the single-tenant degenerate case.

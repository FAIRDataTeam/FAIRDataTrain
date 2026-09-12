# ADR-007 — ODRL for conditions, requests, and agreements; evaluator behind an interface

| | |
|---|---|
| **Status** | Accepted. |
| **Deciders** | Luiz Olavo Bonino da Silva Santos |
| **Source** | Extracted verbatim on 12 September 2026 from *FAIR Data Station — Architecture (station component), v0.3*, §Architecture Decision Records (`docs/architecture/fair-data-station-architecture.md` in this repository, `FAIR Data Train/fair-data-station-architecture/` in the project folder). The source document remains normative; edit there and re-extract. |

## Context

Access conditions (station/controller), access requests (trains), and access agreements (shared) must be machine-actionable; W3C ODRL formal semantics are still being standardized (active CG work, 2026).

## Decision

Use `odrl:Offer` / `odrl:Request` / `odrl:Agreement` natively; domain specificity via ODRL profiles (FDT core profile; DUO+DPV for health). The evaluator/matcher is a replaceable internal component.

## Alternatives

*Not recorded in the source document for this decision.*

## Consequences

pragmatic matching semantics initially, documented explicitly; upgrade path to standardized evaluator semantics and compliance reports without API change.

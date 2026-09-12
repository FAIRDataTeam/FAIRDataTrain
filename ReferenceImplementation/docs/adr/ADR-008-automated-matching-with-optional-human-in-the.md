# ADR-008 — Automated matching with optional human-in-the-loop approval

| | |
|---|---|
| **Status** | Accepted. |
| **Deciders** | Luiz Olavo Bonino da Silva Santos |
| **Source** | Extracted verbatim on 12 September 2026 from *FAIR Data Station — Architecture (station component), v0.3*, §Architecture Decision Records (`docs/architecture/fair-data-station-architecture.md` in this repository, `FAIR Data Train/fair-data-station-architecture/` in the project folder). The source document remains normative; edit there and re-extract. |

## Context

*Not recorded in the source document for this decision.*

## Decision

Matching runs automatically at request arrival; a controller's offer may flag resources as requiring manual approval, inserting a *pending-approval* state. Negotiation is asynchronous for trains in all cases.

## Alternatives

pre-arranged agreements only (safer but not machine-actionable at scale); fully automated only (no controller comfort for sensitive resources).

## Consequences

agreement lifecycle needs notification and timeout handling; trains must handle deferred outcomes.

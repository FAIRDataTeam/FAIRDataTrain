# ADR-004 — Support both push and poll dispatch

| | |
|---|---|
| **Status** | Accepted. |
| **Deciders** | Luiz Olavo Bonino da Silva Santos |
| **Source** | Extracted verbatim on 12 September 2026 from *FAIR Data Station — Architecture (station component), v0.3*, §Architecture Decision Records (`docs/architecture/fair-data-station-architecture.md` in this repository, `FAIR Data Train/fair-data-station-architecture/` in the project folder). The source document remains normative; edit there and re-extract. |

## Context

Hospitals and firewalled sites often cannot accept inbound connections; the prototype assumed push.

## Decision

Push endpoint and poll worker both feed one internal queue; identical processing beyond the gateway.

## Alternatives

*Not recorded in the source document for this decision.*

## Consequences

Train Handler needs a pending-jobs endpoint; stations choose their mode per network posture.

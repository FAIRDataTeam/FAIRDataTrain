# ADR-016 — Three mechanisms for state between hops; peer forwarding deferred to v2

| | |
|---|---|
| **Status** | Accepted. |
| **Deciders** | Luiz Olavo Bonino da Silva Santos |
| **Source** | Extracted verbatim on 12 September 2026 from *FAIR Data Train — Ecosystem Architecture, v0.1.4*, §Architecture Decision Records (`docs/architecture/fdt-ecosystem-architecture.md` in this repository, `FAIR Data Train/fair-data-station-architecture/` in the project folder). The source document remains normative; edit there and re-extract. |

## Context

*Not recorded in the source document for this decision.*

## Decision

State may travel inside the train (inspected by the origin station's PEP 3 as a distinct policy object), via the orchestrator (non-personal only, ADR-015), or via a linkage station (opaque pseudonyms). Station-to-station forwarding of a train (P10) is designed for — dispatcher role, mTLS and identity binding, progress reporting to the originating Handler — but not implemented in v1; a choreographing train returns to the Handler between hops.

## Alternatives

*Not recorded in the source document for this decision.*

## Consequences

PEP 3 gains an "onward state" decision; the visit protocol carries onward-state hand-over; stations stay agnostic to coordination style.

# ADR-003 — Docker executor is process-isolated from the start

| | |
|---|---|
| **Status** | Accepted. |
| **Deciders** | Luiz Olavo Bonino da Silva Santos |
| **Source** | Extracted verbatim on 12 September 2026 from *FAIR Data Station — Architecture (station component), v0.3*, §Architecture Decision Records (`docs/architecture/fair-data-station-architecture.md` in this repository, `FAIR Data Train/fair-data-station-architecture/` in the project folder). The source document remains normative; edit there and re-extract. |

## Context

Container execution is the riskiest interaction mechanism.

## Decision

The Docker adapter shells out to an isolated executor process (default: no network egress, resource limits); its boundary is a minimal internal protocol.

## Alternatives

*Not recorded in the source document for this decision.*

## Consequences

a crashing or compromised execution cannot take down the core; the executor's implementation language can change independently if ever warranted.

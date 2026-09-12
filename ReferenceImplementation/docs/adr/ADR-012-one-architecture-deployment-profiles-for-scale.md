# ADR-012 — One architecture, deployment profiles for scale

| | |
|---|---|
| **Status** | Accepted. |
| **Deciders** | Luiz Olavo Bonino da Silva Santos |
| **Source** | Extracted verbatim on 12 September 2026 from *FAIR Data Station — Architecture (station component), v0.3*, §Architecture Decision Records (`docs/architecture/fair-data-station-architecture.md` in this repository, `FAIR Data Train/fair-data-station-architecture/` in the project folder). The source document remains normative; edit there and re-extract. |

## Context

Stations range from personal devices to hospital infrastructure.

## Decision

No mandatory heavy dependencies: embedded defaults (SQLite, in-process queue, external OIDC) scaling by configuration to PostgreSQL, external queues, HA workers. Stations advertise a capacity class.

## Alternatives

*Not recorded in the source document for this decision.*

## Consequences

core code must remain infrastructure-agnostic behind thin persistence/queue interfaces.

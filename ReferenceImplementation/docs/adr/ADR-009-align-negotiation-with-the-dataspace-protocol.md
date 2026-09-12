# ADR-009 — Align negotiation with the Dataspace Protocol "where cheap"

| | |
|---|---|
| **Status** | Accepted. |
| **Deciders** | Luiz Olavo Bonino da Silva Santos |
| **Source** | Extracted verbatim on 12 September 2026 from *FAIR Data Station — Architecture (station component), v0.3*, §Architecture Decision Records (`docs/architecture/fair-data-station-architecture.md` in this repository, `FAIR Data Train/fair-data-station-architecture/` in the project folder). The source document remains normative; edit there and re-extract. |

## Context

IDSA DSP / Eclipse EDC also negotiate ODRL offer→request→agreement.

## Decision

Mirror DSP's asynchronous state-machine shape and ODRL payloads; do not adopt the full protocol now.

## Alternatives

*Not recorded in the source document for this decision.*

## Consequences

a future DSP bridge (e.g. toward Gaia-X / EHDS-adjacent infrastructures) is a mapping exercise, not a redesign.

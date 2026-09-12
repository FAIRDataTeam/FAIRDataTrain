# ADR-006 — Conform to the FDP specification; do not reuse FDP code

| | |
|---|---|
| **Status** | Accepted. |
| **Deciders** | Luiz Olavo Bonino da Silva Santos |
| **Source** | Extracted verbatim on 12 September 2026 from *FAIR Data Station — Architecture (station component), v0.3*, §Architecture Decision Records (`docs/architecture/fair-data-station-architecture.md` in this repository, `FAIR Data Train/fair-data-station-architecture/` in the project folder). The source document remains normative; edit there and re-extract. |

## Context

FDP metadata functionality is "solved", but the reference implementation is Java.

## Decision

The station embeds FDP-compliant metadata endpoints implemented in the station stack; deployments may additionally sync to an external FDP.

## Alternatives

*Not recorded in the source document for this decision.*

## Consequences

one reimplementation of the FDP API surface; full independence from the Java lineage; conformance validated against the FDP spec test expectations.

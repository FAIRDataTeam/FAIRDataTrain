# ADR-005 — New `FAIRDataStation` repo + language-neutral `fdt-commons`

| | |
|---|---|
| **Status** | Accepted. |
| **Deciders** | Luiz Olavo Bonino da Silva Santos |
| **Source** | Extracted verbatim on 12 September 2026 from *FAIR Data Station — Architecture (station component), v0.3*, §Architecture Decision Records (`docs/architecture/fair-data-station-architecture.md` in this repository, `FAIR Data Train/fair-data-station-architecture/` in the project folder). The source document remains normative; edit there and re-extract. |

## Context

Reuse across FDT applications without code duplication; polyglot ecosystem after ADR-001.

## Decision

Station in its own repository; shared *spec artifacts* (shapes, ODRL profile, OpenAPI schemas, JSON-LD contexts) in `fdt-commons`; both as submodules of the metaproject.

## Alternatives

shared Java libraries (invalidated by ADR-001); single monorepo (couples release cycles).

## Consequences

cross-language consistency is enforced at the artifact level, not the code level.

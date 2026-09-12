# ADR-024 — Cross-domain alignment through alignment services and self-description

| | |
|---|---|
| **Status** | Accepted. |
| **Deciders** | Luiz Olavo Bonino da Silva Santos |
| **Source** | Extracted verbatim on 12 September 2026 from *FAIR Data Train — Ecosystem Architecture, v0.1.4*, §Architecture Decision Records (`docs/architecture/fdt-ecosystem-architecture.md` in this repository, `FAIR Data Train/fair-data-station-architecture/` in the project folder). The source document remains normative; edit there and re-extract. |

## Context

*Not recorded in the source document for this decision.*

## Decision

Vocabulary and code-system mappings are provided by reusable alignment stations/services discoverable via the Directory (visited as hops or consulted by trains), and stations declare per dataset the vocabularies and join keys they support so a Handler can check joinability before dispatch. Trains may still embed mappings, but that is not the ecosystem's mechanism.

## Alternatives

*Not recorded in the source document for this decision.*

## Consequences

FDT-O gains AlignmentStation/service and join-key vocabularies; the Directory indexes them; cross-domain plans become checkable at planning time.

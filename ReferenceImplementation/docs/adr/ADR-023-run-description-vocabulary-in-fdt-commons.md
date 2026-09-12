# ADR-023 — Run-description vocabulary in `fdt-commons`

| | |
|---|---|
| **Status** | Accepted. |
| **Deciders** | Luiz Olavo Bonino da Silva Santos |
| **Source** | Extracted verbatim on 12 September 2026 from *FAIR Data Train — Ecosystem Architecture, v0.1.4*, §Architecture Decision Records (`docs/architecture/fdt-ecosystem-architecture.md` in this repository, `FAIR Data Train/fair-data-station-architecture/` in the project folder). The source document remains normative; edit there and re-extract. |

## Context

*Not recorded in the source document for this decision.*

## Decision

Plans, itineraries, phases, dependencies, stop conditions, budgets, state-carriage choice and join keys are described in an FDT-O vocabulary with SHACL shapes and JSON-LD schemas shared by Handlers and stations; expressible as DSP/ODRL where overlapping.

## Alternatives

Handler-internal model; adopt CWL/BPMN.

## Consequences

stations can validate what a visit is part of (e.g. to accept onward state); plans are portable between Handler implementations.

# ADR-015 — The Train Handler holds non-personal, aggregate data only

| | |
|---|---|
| **Status** | Accepted. |
| **Deciders** | Luiz Olavo Bonino da Silva Santos |
| **Source** | Extracted verbatim on 12 September 2026 from *FAIR Data Train — Ecosystem Architecture, v0.1.4*, §Architecture Decision Records (`docs/architecture/fdt-ecosystem-architecture.md` in this repository, `FAIR Data Train/fair-data-station-architecture/` in the project folder). The source document remains normative; edit there and re-extract. |

## Context

Orchestrated patterns need the Handler to act on intermediate results; the Handler is not a party to agreements; DGA intermediation and EHDS SPE rules bite if it holds data.

## Decision

The Handler may receive and hold only results that a station's result inspection released as non-personal (counts, aggregates, next-hop lists, opaque pseudonyms); record-level data never reaches it.

## Alternatives

never any data (forces all orchestration into stations or trains); trusted party holding pseudonymous record-level data (heavier legal position).

## Consequences

orchestration conditions (P7) and routing (P4) work on aggregates and pseudonyms; record-level joins happen in stations or through linkage stations; simplifies the Handler's legal position.

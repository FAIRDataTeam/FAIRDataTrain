# ADR-019 — Dataspace Protocol conformance in two steps

| | |
|---|---|
| **Status** | Accepted. |
| **Deciders** | Luiz Olavo Bonino da Silva Santos |
| **Source** | Extracted verbatim on 12 September 2026 from *FAIR Data Train — Ecosystem Architecture, v0.1.4*, §Architecture Decision Records (`docs/architecture/fdt-ecosystem-architecture.md` in this repository, `FAIR Data Train/fair-data-station-architecture/` in the project folder). The source document remains normative; edit there and re-extract. |

## Context

*Not recorded in the source document for this decision.*

## Decision

v1: the station catalogue is a DSP-conformant `dcat:Catalog`; FDT offers, requests and agreements follow DSP structural rules enforced by SHACL shapes in `fdt-commons`; the mapping of FDT agreement and visit states to DSP Contract Negotiation and Transfer Process states is documented. v2: DSP endpoints, `/.well-known/dspace-version`, TCK conformance; DCP for identity.

## Alternatives

endpoints in v1 (premature while the SPI moves); mapping only (leaves interoperability with Simpl/EDC untested).

## Consequences

FDP and DSP catalogues coexist on one DCAT graph; the visit protocol is FDT's DSP data plane.

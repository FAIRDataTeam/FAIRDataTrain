# ADR-014 — Agreements per hop, negotiated on arrival

| | |
|---|---|
| **Status** | Accepted (2026-09-11). |
| **Deciders** | Luiz Olavo Bonino da Silva Santos |
| **Source** | Extracted verbatim on 12 September 2026 from *FAIR Data Train — Ecosystem Architecture, v0.1.4*, §Architecture Decision Records (`docs/architecture/fdt-ecosystem-architecture.md` in this repository, `FAIR Data Train/fair-data-station-architecture/` in the project folder). The source document remains normative; edit there and re-extract. |

## Context

Multi-hop itineraries (P3, P4, P8) involve controllers that are not known before dispatch.

## Decision

Every station visit is governed by its own ODRL agreement negotiated when the train arrives, including visits to linkage and alignment stations; a run may stall in *pending approval* at any hop.

## Alternatives

chain-level agreement up front (predictable but impossible for discovery chains); hybrid framework + per-hop instantiation (deferred; may return as a convenience layer).

## Consequences

plans carry timeout and partial-result policies; the run-level record is provenance over agreements; matches ADR-008 and the DSP negotiation model.

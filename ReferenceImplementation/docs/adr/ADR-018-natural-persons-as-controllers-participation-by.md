# ADR-018 — Natural persons as controllers: participation by deployment profile

| | |
|---|---|
| **Status** | Accepted. |
| **Deciders** | Luiz Olavo Bonino da Silva Santos |
| **Source** | Extracted verbatim on 12 September 2026 from *FAIR Data Train — Ecosystem Architecture, v0.1.4*, §Architecture Decision Records (`docs/architecture/fdt-ecosystem-architecture.md` in this repository, `FAIR Data Train/fair-data-station-architecture/` in the project folder). The source document remains normative; edit there and re-extract. |

## Context

Controllers are organisations or natural persons; the IDSA Rulebook admits only legal organisations as participants; the Individual Gateway serves any single controller, company or person.

## Decision

The personal profile allows a natural person to be a participant with their own gateway (and station); team and enterprise profiles require an operator-participant (institution, patient organisation, data-altruism organisation) with the person as rights holder whose conditions travel as credentials or agreements.

## Alternatives

*Not recorded in the source document for this decision.*

## Consequences

two identity paths in the gateway; networks declare whether they admit natural-person participants; the enterprise path is data-space alignable today, the personal path is an FDT extension.

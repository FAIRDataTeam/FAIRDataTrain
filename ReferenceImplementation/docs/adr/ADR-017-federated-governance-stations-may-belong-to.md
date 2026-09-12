# ADR-017 — Federated governance; stations may belong to several networks

| | |
|---|---|
| **Status** | Accepted. |
| **Deciders** | Luiz Olavo Bonino da Silva Santos |
| **Source** | Extracted verbatim on 12 September 2026 from *FAIR Data Train — Ecosystem Architecture, v0.1.4*, §Architecture Decision Records (`docs/architecture/fdt-ecosystem-architecture.md` in this repository, `FAIR Data Train/fair-data-station-architecture/` in the project folder). The source document remains normative; edit there and re-extract. |

## Context

Communities differ in rules and trust anchors; a station typically serves several.

## Decision

FDT defines the governance function and its interfaces (onboarding, evidence categories, trusted issuers, membership statements) and issues nothing itself; each FDT network runs its own authority; a station's self-description lists its memberships and policies are evaluated per network.

## Alternatives

one FDT-wide authority; layered root + local authorities (Gaia-X-like).

## Consequences

membership and trusted-issuer formats in `fdt-commons`; agreements and audit partitioned by network; identity providers are network choices.

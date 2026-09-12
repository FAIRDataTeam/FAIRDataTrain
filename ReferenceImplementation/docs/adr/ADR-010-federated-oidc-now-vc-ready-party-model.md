# ADR-010 — Federated OIDC now; VC-ready party model

| | |
|---|---|
| **Status** | Accepted. |
| **Deciders** | Luiz Olavo Bonino da Silva Santos |
| **Source** | Extracted verbatim on 12 September 2026 from *FAIR Data Station — Architecture (station component), v0.3*, §Architecture Decision Records (`docs/architecture/fair-data-station-architecture.md` in this repository, `FAIR Data Train/fair-data-station-architecture/` in the project folder). The source document remains normative; edit there and re-extract. |

## Context

*Not recorded in the source document for this decision.*

## Decision

Stations trust configured OIDC providers; agreements record the authenticated legal party as an identity claim set (issuer, subject, attributes, proof method).

## Alternatives

*Not recorded in the source document for this decision.*

## Consequences

W3C Verifiable Credentials can be introduced later by adding an issuer type — no agreement schema migration.

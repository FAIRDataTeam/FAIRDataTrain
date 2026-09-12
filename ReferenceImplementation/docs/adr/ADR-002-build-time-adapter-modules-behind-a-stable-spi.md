# ADR-002 — Build-time adapter modules behind a stable SPI ("pragmatic middle path")

| | |
|---|---|
| **Status** | Accepted. |
| **Deciders** | Luiz Olavo Bonino da Silva Santos |
| **Source** | Extracted verbatim on 12 September 2026 from *FAIR Data Station — Architecture (station component), v0.3*, §Architecture Decision Records (`docs/architecture/fair-data-station-architecture.md` in this repository, `FAIR Data Train/fair-data-station-architecture/` in the project folder). The source document remains normative; edit there and re-extract. |

## Context

Deployers must choose supported execution models; third-party mechanisms desirable eventually; SPI will evolve during early development.

## Decision

Adapters are build-time modules enabled by configuration; the SPI is a clean, versioned interface from day one. Revisit runtime plugins/service protocol after the SPI survives 3–4 real adapters.

## Alternatives

runtime plugins (ecosystem extensibility, but freezes the plugin API prematurely and adds sandboxing burden); separate services per adapter (language freedom and isolation, but N+1 containers and an internal protocol from day one — conflicts with easy deployment).

## Consequences

contributing a mechanism initially requires a core-repo contribution; migration path to plugins is mechanical, the reverse is not.

# ADR-001 — Python + FastAPI for the station core

| | |
|---|---|
| **Status** | Accepted (2026-07-02). |
| **Deciders** | Luiz Olavo Bonino da Silva Santos |
| **Source** | Extracted verbatim on 12 September 2026 from *FAIR Data Station — Architecture (station component), v0.3*, §Architecture Decision Records (`docs/architecture/fair-data-station-architecture.md` in this repository, `FAIR Data Train/fair-data-station-architecture/` in the project folder). The source document remains normative; edit there and re-extract. |

## Context

No predetermined stack; team to be hired; community adapter contributions expected from the FAIR/research-data world; no obligation to follow the Java prototype.

## Decision

Python 3.12+/FastAPI, mandatory typing (pydantic, mypy strict).

## Alternatives

Java/Kotlin (best RDF/SHACL stack — RDF4J/Jena/TopBraid — and direct FDP code reuse, but slower iteration and smaller contributor pool); TypeScript/Node (Comunica/TPF strength, but SHACL Core-only and fewer domain contributors); Go (operationally excellent, but RDF/SHACL ecosystem too thin for a semantics-centric component).

## Consequences

rdflib/pySHACL are slower than RDF4J — acceptable because the station fronts data sources rather than hosting large graphs; FDP reuse becomes spec conformance (ADR-006); discipline enforced via strict typing.

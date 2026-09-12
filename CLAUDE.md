# FAIR Data Train — instructions for a coding agent

The reference implementation lives in `ReferenceImplementation/`. Read its `README.md` and
`OPEN-QUESTIONS.md` first, then the normative architecture documents it points to, in the
order the implementation plan's §1 gives.

Run `make check` in `ReferenceImplementation/` before and after touching anything in
`fdt-commons/` or `FDT-O/`. It is the gate: every SHACL shape, JSON Schema, protocol fixture
and the JSON-LD round-trip. Nothing downstream is trustworthy while it is red.

## Rules that are not negotiable

- **Contracts live in `fdt-commons`; code consumes them and never redefines them.** To change
  one: edit `fdt-commons` first, bump `VERSION`, add a `FINDINGS.md` line, run its
  validators, and only then update consumers. Generate pydantic models and TypeScript types
  from the JSON Schemas and OpenAPI documents — do not hand-write them.
- **Fixtures before features.** Each work package starts by making the relevant
  `fdt-commons/examples/*` fixtures pass through the new code, and the invalid fixtures fail
  *with the message the shape carries*.
- **A train is an executable asset, never a `dcat:Dataset`** (ADR-020). Hosted data is
  `fdt-o:HostedDataset`. Do not "fix" this in code.
- **The Train Handler never stores record-level data** (ADR-015) — envelopes, events and
  aggregates only.
- **Every station decision is an event with a justification** (ADR-027). No silent state
  changes.
- **Refused ≠ Rejected ≠ Not selected** (ADR-026). Keep the outcome vocabulary exact in code,
  logs and UI: a completeness statement reports these words verbatim to a data consumer, and
  reporting a controller's refusal as "below threshold" misrepresents their decision.
- **Fictional stations and parties only** — the fixtures and the mock-ups' sample data name
  them. No real institution is a case actor. Never present the "< 2 h onset-to-groin" figure
  as a Dutch norm.
- **Domain-agnostic.** Nothing in the station or Handler may assume health data; domain
  specificity enters through ODRL profiles, DCAT profiles and adapter configuration.
- **Stack.** Station and services: Python 3.12+, FastAPI, pydantic v2, `mypy --strict`,
  rdflib, pySHACL, Docker SDK. Consoles: React 18 + TypeScript + Vite, one codebase, three
  role-based apps.

## Decisions

D1 (Python), D2 (`FAIRDataTeam/FDT-O` is canonical) and D3 (React + TypeScript + Vite) were
taken on 12 September 2026 — see `ReferenceImplementation/OPEN-QUESTIONS.md`. Remaining
decisions belong to Luiz Olavo Bonino da Silva Santos: do not take them in code. Write the
question to `OPEN-QUESTIONS.md`, take the conservative default named there, mark the code
with the question id, and continue.

Changing an architectural decision means drafting an ADR (Context / Decision / Alternatives /
Consequences) with status *Proposed* and stopping the affected work package until Luiz
accepts it.

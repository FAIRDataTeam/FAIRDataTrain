# Brief for the FDT implementation agent

You are implementing v1 of the **FAIR Data Train (FDT)** ecosystem — a "code visits data" platform: trains (executable queries, API calls, scripts, containers) travel to Data Stations, run inside policy checkpoints, and only inspected aggregates leave. Owner and architect: Luiz Olavo Bonino da Silva Santos (University of Twente).

## Start here

1. Read `fair-data-station-architecture/fdt-implementation-plan.md` — the plan, the milestones, the work packages, the ground rules. Then the documents it lists in its §1, in that order.
2. Begin with **M0 / WP-0.1**: create the `FAIRDataTrain` metaproject, add `fdt-commons/` and `FDT-O-v2/` (this folder's copies are the seeds), and make `make check` run:
   - `python3 fdt-commons/tests/validate.py` (install **pySHACL** and **jsonschema ≥ 4.18**; the checks were developed on a subset validator and old jsonschema — the first thing to learn is whether a conformant processor agrees),
   - `python3 FDT-O-v2/tests/validate.py`.
3. Continue in work-package order. Each package's acceptance criterion is a runnable scenario; do not move on with a red one.

## Rules that are not negotiable (the plan explains why)

- Contracts live in `fdt-commons`; code consumes them, never redefines them. Change the contract first, then the code.
- A train is an executable asset — never a `dcat:Dataset`. Hosted data is `fdt-o:HostedDataset`.
- The Train Handler never stores record-level data; stations release aggregates and pseudonym-class state only.
- Every station decision is a visit event with a justification; Refused, Rejected and Not selected are different things.
- Fictional stations and parties only (the fixtures name them). No real institution is a case actor.
- Domain-agnostic code; health specifics enter through profiles and configuration only.
- Decisions D1–D5 in the plan's §7 are Luiz's. Write open questions to `OPEN-QUESTIONS.md`; take the conservative default; continue.

## What exists

`fair-data-station-architecture/` — the architecture documents (ADR-001–027), the pattern catalogue, the reference case, the data-space requirements register, and `mockups/` (22 console screens with their generator — the UI specification). `fdt-commons/` v0.4 — vocabularies, SHACL shapes, JSON Schemas, the **visit protocol v1** (spec + OpenAPI), JSON-LD contexts, fixtures (valid and invalid), validators. `FDT-O-v2/` — the ontology delta and revised shapes; the ontology file itself is decision D2.

## What "done" looks like for v1

Four milestone scenarios run from `docker compose up` in the metaproject: one visit (M1); fan-out with approval, refusal and a completeness statement (M2); the time-to-groin discovery chain through a linkage station and a two-phase plan, with the itinerary map live and in replay (M3); a composition run, provenance, profiles and conformance material (M4).

# FAIR Data Train — reference implementation

The v1 implementation of the FDT ecosystem: a "code visits data" platform where trains —
executable queries, API calls, scripts and containers — travel to data stations, run inside
policy checkpoints, and release only inspected aggregates.

This directory is the metaproject. Each component is its own repository, checked out here as
a submodule, so that `fdt-commons` can be consumed by third parties and each component
released on its own.

```sh
git submodule update --init --recursive
make check          # the gate: every contract validator in fdt-commons and FDT-O
```

## Components

| Submodule | What it is | Status |
|---|---|---|
| [`fdt-commons`](https://github.com/FAIRDataTeam/fdt-commons) | **the contracts**: vocabularies, SHACL shapes, JSON Schemas, JSON-LD contexts, the visit protocol, the fixtures | v0.5 — validated |
| [`FDT-O`](https://github.com/FAIRDataTeam/FDT-O) | the ontology: what a train, payload, hosted dataset, catalogue, controller and station type *are* | v2.0.0 on branch `fdt-o-v2` ([PR #1](https://github.com/FAIRDataTeam/FDT-O/pull/1)) |
| [`FAIRDataStation-py`](https://github.com/FAIRDataTeam/FAIRDataStation-py) | the station: PEP 1–3, agreements, metadata, adapters | skeleton |
| [`FAIRDataTrainHandler`](https://github.com/FAIRDataTeam/FAIRDataTrainHandler) | the Handler: run model, orchestration, conditions, failure policy | skeleton |
| [`IndividualGateway`](https://github.com/FAIRDataTeam/IndividualGateway) | the data controller's agent across stations | skeleton |
| [`StationDirectory`](https://github.com/FAIRDataTeam/StationDirectory) | federation catalogue of station self-descriptions | skeleton |
| [`TrainGarage`](https://github.com/FAIRDataTeam/TrainGarage) | catalogue of train offers with payload digests | skeleton |
| [`FDTConsole`](https://github.com/FAIRDataTeam/FDTConsole) | one front-end, three role-based apps | skeleton |

The Java prototypes — `FAIRDataStation`, `TrainHandler`, `TrainHandler-server`,
`TrainHandler-client`, `TrainOrchestrator` — are the earlier lineage and are not evolved
(decision D1). They are left where they are.

## Ground rules

These are not style preferences. The plan's §2 explains each; they are repeated here because
they are the rules most easily broken by accident.

- **Contracts live in `fdt-commons`, and code consumes them.** No component redefines a
  term, shape, schema or endpoint that exists there. If a contract is missing or wrong,
  change it *in `fdt-commons` first* — bump the version, add a `FINDINGS.md` line, run its
  validators — and only then change the code. Models are generated from the JSON Schemas and
  OpenAPI documents, never hand-written.
- **Fixtures before features.** Every work package starts by making the relevant
  `fdt-commons/examples/*` fixtures pass through the new code. The invalid fixtures must be
  refused *with the message the shape carries* — the message a user sees is part of the
  contract and is tested as one.
- **A train is an executable asset, never a `dcat:Dataset`** (ADR-020 as amended). Hosted
  data is `fdt-o:HostedDataset`.
- **The Handler never holds record-level data** (ADR-015). A Handler-side test that stores
  anything but envelopes, events and aggregates fails by design.
- **Every station decision is an event with a justification** (ADR-027). No silent state
  changes.
- **Refused ≠ Rejected ≠ Not selected** (ADR-026). A refused station declined the request; a
  rejected one produced a result that failed inspection; a not-selected one was never asked.
  Keep the three exact in code, in logs and on screen — a completeness statement reports
  them verbatim to the data consumer.
- **Fictional stations and parties only.** Noorderlicht MC, Zuiderlicht MC, Linkage station
  Oost, Ambulancezorg Oost, UT Data Station, EU-CardioNet, HealthAI B.V. No real institution
  is a case actor, and the "< 2 h onset-to-groin" figure is never presented as a Dutch norm.
- **Domain-agnostic.** Nothing in the station or the Handler may assume health data. Domain
  specificity enters through ODRL profiles, DCAT profiles and adapter configuration.
- **When in doubt, don't guess.** Add the question to `OPEN-QUESTIONS.md`, take the most
  conservative reading, mark the code with the question id, and continue.

## Layout

```
ReferenceImplementation/
  Makefile              make check · make generate · make test · make up · make e2e
  OPEN-QUESTIONS.md     what is undecided, and the default in force until it is
  <submodules>          the eight component repositories
  deploy/               Dockerfiles, compose per scenario, the three deployment profiles
  fixtures/             scenario data: test graphs, the fixture OIDC provider, synthetic datasets
  tests/e2e/            the milestone scenarios, run against composed stations
  tests/fakes/          a fake station, garage and TTP, so orchestration is testable alone
```

## Milestones

Each ends in a scenario that runs from `docker compose up` and is recorded as an end-to-end
test. The order and the exit criteria are fixed; durations are not.

| | Exit scenario |
|---|---|
| **M0** Foundations | `make check` runs every validator; models generate from the contracts; a station skeleton answers `GET /` with a valid self-description |
| **M1** One visit | the gene–disease SPARQL train reaches one station, is auto-approved, runs through PEP 1–3; the Handler CLI prints the event stream and the envelope; invalid fixtures are refused with the right reasons |
| **M2** Fan-out and governance | three stations, push and poll; one approval in the Gateway; one refusal on commercial purpose; the run ends **Partially Delivered** with a completeness statement |
| **M3** Multi-hop | a two-phase plan selecting stations by condition; the time-to-groin chain through a linkage station with per-hop agreements, a pending approval and a pruned branch; the itinerary map live and in replay |
| **M4** Hardening | composition with a rejected phase; PROV-O run records; DSP state mapping asserted; three deployment profiles from one image; a security review of PEP 1 and the Docker sandbox; conformance material |

### Where M0 stands

- **WP-0.1 Metaproject and CI** — done. `make check` is green; CI runs it on a clean clone.
- **WP-0.2 FDT-O v2 merge** — done, pending review of
  [PR #1](https://github.com/FAIRDataTeam/FDT-O/pull/1). See Q5.
- **WP-0.3 Generated models** — TypeScript types generate from the OpenAPI documents
  (`FDTConsole`); the pydantic side and the `fdt_commons` Python package are next.
- **WP-0.4 Station skeleton** — package layout in place; the FastAPI app and the
  self-description endpoint are next.

## Documentation

The architecture is normative and lives outside this repository: the ecosystem architecture
(ADR-014–027), the station architecture (ADR-001–013), the itinerary patterns, the
time-to-groin reference case, the data-space alignment register, and the 22 console mock-ups
that are the UI specification.

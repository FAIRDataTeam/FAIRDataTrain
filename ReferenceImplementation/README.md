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
| [`fdt-commons`](https://github.com/FAIRDataTeam/fdt-commons) | **the contracts**: vocabularies, SHACL shapes, JSON Schemas, JSON-LD contexts, the visit protocol, the fixtures | v0.9.0 — validated |
| [`FDT-O`](https://github.com/FAIRDataTeam/FDT-O) | the ontology: what a train, payload, hosted dataset, catalogue, controller and station type *are* | v2.0.0 on branch `fdt-o-v2` ([PR #1](https://github.com/FAIRDataTeam/FDT-O/pull/1)) |
| [`FAIRDataStation-py`](https://github.com/FAIRDataTeam/FAIRDataStation-py) | the station: PEP 1–3, agreements, metadata, adapters | WP-0.4 done — `GET /` self-description, three profiles, 75 tests |
| [`FAIRDataTrainHandler`](https://github.com/FAIRDataTeam/FAIRDataTrainHandler) | the Handler: run model, orchestration, conditions, failure policy | skeleton |
| [`IndividualGateway`](https://github.com/FAIRDataTeam/IndividualGateway) | the data controller's agent across stations | skeleton |
| [`StationDirectory`](https://github.com/FAIRDataTeam/StationDirectory) | federation catalogue of station self-descriptions | skeleton |
| [`TrainGarage`](https://github.com/FAIRDataTeam/TrainGarage) | catalogue of train offers with payload digests | skeleton |
| [`FDTConsole`](https://github.com/FAIRDataTeam/FDTConsole) | one front-end, three role-based apps | design system and generated contract types; no screens yet |

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

### Where the work stands

This section is the progress record. The roadmap it tracks — milestones, the 25 work packages
and their acceptance criteria — is §4 and §5 of `fdt-implementation-plan.md` in the
architecture folder, which is normative and lives outside this repository. Decisions and their
conservative defaults are in [`OPEN-QUESTIONS.md`](OPEN-QUESTIONS.md); contract defects and
what closed them are in `fdt-commons/FINDINGS.md`, numbered and referred to by number.

**M0 — Foundations: done.**

| | |
|---|---|
| WP-0.1 Metaproject and CI | done — `make check` green on a clean clone; CI runs it |
| WP-0.2 FDT-O v2 merge | done, pending [PR #1](https://github.com/FAIRDataTeam/FDT-O/pull/1) (Q5). Terms stay at `https://w3id.org/fdt/fdt-o#` (D2); shapes reference 42 terms, ontology declares 71, undeclared 0, asserted on every run |
| WP-0.3 Generated models | done — pydantic models from the JSON Schemas and TypeScript types from the OpenAPI documents, reproducibly and offline; `generated/` is git-ignored. **Finding 32**: the models are a typed view, not enforcement — validate against the schema |
| WP-0.4 Station skeleton | done — `GET /` self-description served for all three profiles; enabled adapters are the sole source of `supportsInteractionMechanism` (Principle 1). **Finding 33**: a component binding the wrong namespace still passed its SHACL tests |

**M1 — One visit: not started; its fixtures now exist.** The acceptance-criteria sweep
([Q10](OPEN-QUESTIONS.md), `docs/reviews/2026-09-12-acceptance-criteria-sweep.md`) found all
five M1 criteria unrunnable. Decisions A, D and E ([Q14](OPEN-QUESTIONS.md)) fixed the fixture
side in `fdt-commons` v0.8.0 and v0.9.0.

| | |
|---|---|
| WP-1.1 Visit protocol server | **ready to start.** Its descriptor conforms to `RequestShape` (finding 31 closed) and the wrong-digest fixture its PEP 1 clause needs exists |
| WP-1.2 PEP 1 and payload validation | fixtures ready — every payload has real bytes and a true digest (finding 36). Still needs an invalid-request fixture, and the criterion says "refused" where ADR-026 says Rejected |
| WP-1.3 Negotiation on arrival | **blocked on decision B** — `AgreementShape` validates form, never derivation (finding 28), and carries neither the evidence block nor the validity window Q12 decided. `agr-m1-01` is derivable from its own inputs, so the target exists |
| WP-1.4 Orchestrator, PEP 2/3, SPARQL adapter | fixtures ready — a SPARQL-reachable dataset, an auto-approving offer, a test graph, and a released and a k-violating result computed from the train's own payload (finding 37) |
| WP-1.5 Handler core v0 | fixtures ready — the P1 plan exists in Turtle and JSON-LD, asserted isomorphic |

**M2–M4** are untouched. The sweep lists what each of their criteria still needs, as decisions
F–L; none blocks M1.

**Next:** WP-1.1, and decision B before WP-1.3.

## Documentation

The architecture is normative and lives outside this repository: the ecosystem architecture
(ADR-014–027), the station architecture (ADR-001–013), the itinerary patterns, the
time-to-groin reference case, the data-space alignment register, and the 22 console mock-ups
that are the UI specification.

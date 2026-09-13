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
| [`fdt-commons`](https://github.com/FAIRDataTeam/fdt-commons) | **the contracts**: vocabularies, SHACL shapes, JSON Schemas, JSON-LD contexts, the visit protocol, the fixtures | v0.20.0 — twelve validation passes |
| [`FDT-O`](https://github.com/FAIRDataTeam/FDT-O) | the ontology: what a train, payload, hosted dataset, dataset part, catalogue, controller and station type *are* | v4.0.0 on branch `fdt-o-v2` ([PR #1](https://github.com/FAIRDataTeam/FDT-O/pull/1)) |
| [`FAIRDataStation-py`](https://github.com/FAIRDataTeam/FAIRDataStation-py) | the station: PEP 1–3, agreements, metadata, adapters | M1 done; publishes its catalogue and data shapes — 210 tests |
| [`FAIRDataTrainHandler`](https://github.com/FAIRDataTeam/FAIRDataTrainHandler) | the Handler: run model, orchestration, conditions, failure policy | M1 done; resolves stations from a registry and trains from their Depot — 72 tests |
| [`IndividualGateway`](https://github.com/FAIRDataTeam/IndividualGateway) | the data controller's agent across stations | skeleton |
| [`FDTRegistry`](https://github.com/FAIRDataTeam/FDTRegistry) | the **metadata registry**: harvests and indexes what Depots and Stations publish; not a trust anchor (ADR-029). Answers a train's data requirement by structural coverage and names the property a near-matching station was missing (ADR-030) | **v0.1.0** — 28 tests |
| [`TrainDepot`](https://github.com/FAIRDataTeam/TrainDepot) | the **Train Depot**: the authority for a train — payload bytes, digests it computes rather than repeats, parameters, the input requirement, declared output, the owner's offer and public keys (ADR-029) | **v0.1.0** — 35 tests |
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
  deploy/               `make up`: the testbed as one docker compose, one .env profile per instance
  fixtures/             scenario data: test graphs, the fixture OIDC provider, synthetic datasets
  tests/e2e/            the milestone scenarios, every component against the others
  tests/fakes/          a fake station, depot and TTP, so orchestration is testable alone
```

## Milestones

Each ends in a scenario that is recorded as an end-to-end test and can be watched running:
`make e2e` runs every component against the others in one process, and `make up` brings the
ecosystem up in Docker — two stations, a Depot, a registry, a Handler and the consoles — to look
at in a browser. The order and the exit criteria are fixed; durations are not. (`make
up-processes` runs the same testbed straight out of the checkout, which is what you want while
changing a component: a container build stands between every edit and the screen. The three
*deployment* profiles are still WP-4.3's, and are a different question from a testbed.)

| | Exit scenario |
|---|---|
| **M0** Foundations | `make check` runs every validator; models generate from the contracts; a station skeleton answers `GET /` with a valid self-description |
| **M1** One visit | the gene–disease SPARQL train reaches one station, is auto-approved, runs through PEP 1–3; the Handler CLI prints the event stream and the envelope; invalid fixtures are refused with the right reasons |
| **M2** Fan-out and governance | three stations, push and poll; one approval in the Gateway; one refusal on commercial purpose; the run ends **Partially Delivered** with a completeness statement |
| **M3** Multi-hop | a two-phase plan selecting stations by condition; the time-to-groin chain through a linkage station with per-hop agreements, a pending approval and a pruned branch; the itinerary map live and in replay |
| **M4** Hardening | composition with a rejected phase; PROV-O run records; DSP state mapping asserted; three deployment profiles from one image; a security review of PEP 1 and the Docker sandbox; conformance material |

**M5** (testbed) was added on 12 September 2026 by ADR-029 and runs before M2: a Train Depot, a metadata registry, several stations and the consoles, so that the ecosystem is something you can watch rather than only something the tests assert.

### Where the work stands

[`task.md`](task.md) is the tracked roadmap: the plan's work packages, with a box checked only
when its acceptance criterion has been run. **M0 and M1 are done. M5 — the testbed — is in
progress: a Train Depot, a metadata registry and a station now run against each other under a
Handler, and `make e2e` chooses where to send a visit by asking which stations hold the data.**
Next: WP-5.4, several stations in two networks that differ on whether a machine may decide.

Decisions and their conservative defaults are in [`OPEN-QUESTIONS.md`](OPEN-QUESTIONS.md);
contract defects and what closed them are in `fdt-commons/FINDINGS.md`, by number; dated audits
are in [`docs/reviews/`](docs/reviews/).

## Documentation

The architecture is normative and is **edited** in the project folder `FAIR Data Train/fair-data-station-architecture/`; **copies live in this repository** under [`docs/architecture/`](docs/architecture/) (copied 12 Sep 2026): the ecosystem architecture (ADR-014–027), the station architecture (ADR-001–013), the itinerary patterns, the time-to-groin reference case, the data-space alignment register, the implementation plan, and the 22 console mock-ups that are the UI specification. Every decision record ADR-001–027 is also extracted into its own file in [`docs/adr/`](docs/adr/), next to ADR-028 onward.

[`docs/deployment.md`](docs/deployment.md) is the operator's reference: the deployment profiles, the **run mode** a deployment is started as, the **decision mode** that says how much of a negotiation a station concludes by itself, and every `FDT_STATION_*` setting. Read it before bringing a station up over data that matters — the defaults are the cautious ones, and the reasons they are cautious are there.

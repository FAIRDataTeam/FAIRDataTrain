# FAIR Data Train — Implementation Plan and Roadmap

| | |
|---|---|
| **Status** | v0.1, 12 September 2026 — for the implementation agent to start on M0 |
| **Author** | Luiz Olavo Bonino da Silva Santos (with AI assistance) |
| **Audience** | The implementation agent (a coding agent or a developer) and its reviewers. It says *what* to build, *in what order*, *from which contracts*, and *how to know it is done*. It does not repeat the architecture: the documents in §1 are normative and this plan points into them |
| **Scope** | v1 of the FDT ecosystem as decided on 2 July (station, ADR-001–013) and 11–12 September 2026 (ecosystem, ADR-014–027): Data Station, Train Handler, Individual Gateway, Station Directory, Train Garage, Linkage Station reference, `fdt-commons`, FDT-O v2 |

## 1. Read this first — the normative stack

Read in this order; everything below assumes them.

1. `fdt-ecosystem-architecture.md` (v0.1.4) — components, roles, networks, run model, shared contracts, **ADR-014–027**. The ADRs are decisions; do not re-open them in code. If one proves unimplementable, write it up (see §8) rather than silently deviating.
2. `fair-data-station-architecture.md` (v0.3) — the station component: SPI, PEP 1–3, agreement lifecycle, profiles, repository layout, **ADR-001–013** (stack: Python 3.12 / FastAPI, pydantic, rdflib, pySHACL, Docker SDK; SQLite → PostgreSQL by profile).
3. `../fdt-commons/` (v0.4) — the contracts you code against: `vocab/` (ODRL profile, run description, network), `shapes/` (SHACL), `schemas/` (JSON Schema envelopes), `protocol/` (visit protocol v1: spec + OpenAPI), `contexts/`, `examples/` (valid and invalid fixtures — **your first test data**), `tests/validate.py`, `mapping/state-machines.md` (DSP), `FINDINGS.md`.
4. `../FDT-O-v2/` — the ontology delta and revised shapes the contracts assume (`README.md` lists what still needs the ontology file).
5. `fdt-itinerary-patterns.md` (v0.4) — patterns P1–P10, §9 failure semantics per pattern; `fdt-use-case-time-to-groin.md` (v0.2) — the reference case (fictional stations); `fdt-data-space-alignment.md` (v0.3.1) — the requirements register (what "alignable" means).
6. `mockups/README.md` and the design canvas — the 22 screens are the UI specification for the three consoles; the generator in `mockups/gen/` holds the exact copy, states and sample data.

## 2. Ground rules for the implementation agent

- **Contract-first, contracts are shared.** `fdt-commons` is consumed as a git submodule by every component. Code never redefines a term, shape, schema or endpoint that exists there. If a contract is missing or wrong, change it *in fdt-commons first*, with a line in its `FINDINGS.md` and a version bump, then use it. Generate pydantic models / TypeScript types from the JSON Schemas and OpenAPI files; do not hand-write them.
- **Fixtures before features.** Every work package starts by making the relevant `fdt-commons/examples/*` fixtures pass through the new code (the time-to-groin descriptor, events and envelope; the three example plans; the network-and-stations catalogue). The invalid fixtures must be rejected with the message the shape or schema carries.
- **Trains are executables, never `dcat:Dataset`** (ADR-020). Hosted data is `fdt-o:HostedDataset`. Do not "fix" this in code.
- **The Handler never holds record-level data** (ADR-015). A Handler-side test that stores anything but envelopes, events and aggregates fails by design.
- **Every decision is an event with a justification** (ADR-027, Principle 7). No silent state changes in the station.
- **Refused ≠ Rejected ≠ Not selected** (ADR-026). Keep the outcome vocabulary exact in code, logs and UI.
- **Fictional data only.** Station names, controllers, consumers and figures come from the fixtures and the mock-up sample data (Noorderlicht MC, Zuiderlicht MC, Linkage station Oost, Ambulancezorg Oost, UT Data Station, EU-CardioNet, HealthAI B.V.). No real institution is a case actor. Never present the "< 2 h onset-to-groin" figure as a Dutch norm.
- **Domain-agnostic.** Nothing in the station or Handler may assume health data; domain specificity enters through ODRL profiles, DCAT profiles and adapters' configuration (Principle 8).
- **Stack.** Station: Python 3.12+, FastAPI, pydantic v2, `mypy --strict`, rdflib, pySHACL, Docker SDK; SQLite (personal) / PostgreSQL (team, enterprise). Consoles: one front-end codebase, role-based (the mock-ups' three apps share one design system). Handler and Gateway language: **decision D1 (§7)** — until taken, build the Handler core as a Python package with a CLI so it can be exercised without a UI.
- **Tests.** Unit tests per package; contract tests generated from `fdt-commons` (schema validation of every request/response; SHACL validation of every RDF payload); an end-to-end suite that runs the milestone scenarios (§4) against Docker-composed stations with fixture data. CI runs `fdt-commons/tests/validate.py` and `FDT-O-v2/tests/validate.py` as well.
- **When in doubt, don't guess.** Append the question to `OPEN-QUESTIONS.md` in the repository, pick the most conservative interpretation, mark the code with the question id, and continue.

## 3. Repositories

| Repository | Content | Status |
|---|---|---|
| `FAIRDataTrain` (metaproject) | submodules below, `docker-compose` for the demo scenarios, end-to-end suite, this plan, `OPEN-QUESTIONS.md` | to create |
| `fdt-commons` | the contracts (exists as folder v0.4; becomes a repository at M0) | seed exists |
| `FDT-O` | ontology + shapes; merge `FDT-O-v2/` delta, settle the namespace (finding 1) | exists (prototype) |
| `FAIRDataStation` | station core + adapters: packages `core`, `policy`, `metadata`, `protocol`, `adapters/{sparql,sql,api,docker,linkage}`, `console` | to create |
| `FAIRDataTrainHandler` | run model, orchestration, conditions, failure policy, visit-protocol client + Handler API, console | prototype (Java 17 / Spring Boot v0.1.0 + Nuxt) — **D1** |
| `IndividualGateway` | controller's agent across stations: conditions per network, approvals, audit slice, revocation; talks to stations' controller API | to create |
| `StationDirectory`, `TrainGarage` | federation catalogues (harvesting self-descriptions; catalogue of train offers with digests) | to create (thin in v1) |

## 4. Milestones and demo scenarios

Each milestone ends with a scenario that runs from `docker compose up` in the metaproject and is recorded as an end-to-end test. Durations are not set here (team size is not decided); the order and the exit criteria are.

| Milestone | Exit scenario | Screens it makes real |
|---|---|---|
| **M0 Foundations** | `make check` runs all fdt-commons and FDT-O validations, generates models from the contracts, and a station skeleton answers `GET /` with a valid self-description | — |
| **M1 One visit** | The gene–disease SPARQL train (fixture) is pushed to one station with a SQLite/rdflib test graph; auto-approved; runs through PEP 1–3; the Handler CLI prints the event stream and the envelope; the invalid fixtures are refused/rejected with the right reasons | S2 (checkpoint timeline), H3 (one station) |
| **M2 Fan-out and governance** | The fan-out plan runs against three stations (push and poll); one dataset requires approval — the controller approves in the Gateway; one request is refused (commercial purpose); the run ends Partially Delivered with a completeness statement; conditions engine and failure policy exercised by unit tests on `tests/conditions.cases.json` | H1–H4, S1, S3–S6, G1–G2, G4 |
| **M3 Multi-hop** | Two-phase plan (P7) selects stations by JMESPath condition; the time-to-groin plan (P4) runs EVT centre → linkage station (reference implementation, fake TTP) → two discovered stations with per-hop agreements, a pending approval, a pruned GP branch; itinerary map live and replay; Directory harvests self-descriptions and answers a join-key query; Garage serves train offers and the station verifies digests | H5, H6, H7 (map only), S7, S8, S9, G3 |
| **M4 Hardening and alignment** | Composition plan (P8) with a rejected phase; PROV-O run records; DSP state mapping asserted by tests; Gaia-X-alignable self-description; three deployment profiles from one image; security review of PEP 1 and the Docker sandbox; documentation and conformance material for third-party stations | H8, all consoles complete |

v2 backlog (not in this plan): DSP endpoints and TCK, DCP identity, P5 iterative rounds as a first-class Handler feature (H7 is a preview), P6 aggregator stations, P10 station-to-station forwarding, alignment services, EHDS SPE profile.

## 5. Work packages

Format: **id — name** · depends on · inputs (contracts) · deliverables · acceptance. Sizes S/M/L are relative.

### M0 — Foundations

**WP-0.1 — Metaproject and CI** · — · §3 · repositories, submodules, `make check`, CI running `fdt-commons/tests/validate.py` (pySHACL installed — the probe ran on a subset validator; this is where pySHACL replaces it), `FDT-O-v2/tests/validate.py`, `tests/validate_protocol.py` · acceptance: green CI on a clean clone. **S**

**WP-0.2 — FDT-O v2 merge** · 0.1 · `FDT-O-v2/`, `fdt-commons/FINDINGS.md` finding 1 · the delta merged into the ontology; one namespace (`https://w3id.org/fdt#`) with `owl:equivalentClass` bridges or a documented retirement of the other; TrainShape/PayloadShape/Datastation shapes replaced by the v2 versions; the mechanism individuals typed with FDT-O's class · acceptance: `FDT-O-v2/tests/validate.py` passes against the merged ontology; `fdt-commons` profile `owl:imports` resolves. **S** — *needs the ontology file (§7, D2).*

**WP-0.3 — Generated models** · 0.1 · `schemas/*.json`, `protocol/openapi/*.yaml`, `contexts/` · pydantic models (station, Handler) and TypeScript types (consoles) generated in CI; a `fdt_commons` Python package exposing shapes, schemas, JMESPath conformance cases and the fixtures · acceptance: the four `examples/protocol/*.json` fixtures load into the models; round-trip is byte-identical after normalisation. **S**

**WP-0.4 — Station skeleton** · 0.3 · station architecture §4, §9, ADR-001/012 · FastAPI app, configuration by profile (SQLite default), `GET /` self-description derived from configuration (Principle 1: enabled adapters ⇒ `supportsInteractionMechanism`), FDP metadata endpoints stubbed, structured audit log · acceptance: self-description validates against `station-catalog.shapes.ttl` (`StationSelfDescriptionShape`) with a membership in a fixture network. **M**

### M1 — One visit

**WP-1.1 — Visit protocol server (Station API)** · 0.4 · `protocol/visit-protocol.md`, `station-visit-api.yaml`, `visit-descriptor`, `visit-event`, `visit-result` schemas · `POST /visits` (idempotent on visit IRI, attempt), status, `GET /events` (+ SSE), `GET /result`, artefacts, `POST /cancel`; event emission with sequence numbers; callback client (`POST events`, `PUT result`) · acceptance: the hop-1 fixture descriptor is accepted and produces an event stream schema-identical in shape to `visit-events-ttg-hop1.json` up to `negotiation.pending-approval`; a descriptor with a wrong digest is rejected at PEP 1 with `outcome: Rejected`. **M**

**WP-1.2 — PEP 1 and payload validation** · 1.1 · station §6.2, FDT-O v2 `PayloadShape`, mechanism SPI `validate()` · token verification against trusted issuers per network (ADR-010/017, a fixture OIDC provider in compose), descriptor schema check, SHACL check of the ODRL request (`RequestShape`), payload digest against the train's Garage offer (fetched by IRI; a fixture Garage serving `examples/trains-and-plans.ttl`) · acceptance: all `examples/invalid/*` that concern requests/trains are refused with the shape's `sh:message` in the event justification. **M**

**WP-1.3 — Negotiation on arrival (PDP, auto-approval path)** · 1.2 · ADR-007/008/014, `policy.shapes.ttl`, `mapping/state-machines.md` · ODRL evaluator behind an interface: offer (per network) × request × station policy → agreement (`AgreementShape`-valid, with `dspace:timestamp`, `derivedFromOffer/Request`), states requested → matched → active | refused; agreement store; `GET /agreements/{id}` · acceptance: the fixture offer `evt-registry-research` and request `ttg-2026q3` produce an agreement equal in structure to `agr-9a01`; the HealthAI commercial request is Refused with the prohibition named. **L**

**WP-1.4 — Orchestrator, PEP 2, SPARQL adapter, PEP 3 (aggregate rules)** · 1.3 · station §5, §7.1, ADR-002 · internal queue; PEP 2 (agreement active, quotas); SPI with `describe/validate/execute/collect_result`; SPARQL adapter over rdflib/SPARQL endpoint; PEP 3 with duties as pluggable checks — v1: aggregation threshold (k), permitted output fields per `outputSchema`, no record-level classes; result envelope assembly with `inspection.outcome` passed/redacted/rejected; onward destination `handler` only · acceptance: M1 scenario; a result violating k triggers `visit.rejected` at PEP3 with the S2 timeline's justification. **L**

**WP-1.5 — Handler core v0 (library + CLI)** · 1.1 · `fdt-run` vocabulary, `contexts/fdt-run.context.jsonld`, `plan-time-to-groin.jsonld` · load a plan (JSON-LD), validate with `run.shapes.ttl`, mint visit IRIs, build descriptors, push, receive callbacks or poll, persist events and envelopes, print the run record · acceptance: M1 scenario driven by `fdt-handler run plan.jsonld`. **M**

### M2 — Fan-out and governance

**WP-2.1 — Conditions engine (ADR-025)** · 1.5 · `fdt-run:Condition`, `schemas/visit-result`, `run-state`, `tests/conditions.cases.json` · JMESPath evaluation over VisitResult / PhaseResults / RunState envelopes (a compliance-tested library, vendored if registries are blocked); run-state envelope maintenance with outcome counters · acceptance: every case in `conditions.cases.json` yields its expected value. **S**

**WP-2.2 — Failure policy and completeness (ADR-026)** · 2.1 · `FailurePolicy`, outcomes, `Completeness`, patterns §9 · reactions per outcome, `approvalWait`/deadline timers → `POST /cancel`, retries with `attempt`, pruning of dependants, completeness threshold, run end states, completeness statement in the run record (`ex:run/ttg-2026q2-01` as the target shape) · acceptance: simulated stations (a fake station implementing the Station API from fixtures) produce Finished / PartiallyDelivered / FailedRun exactly per §9 table for P2, P3, P7. **M**

**WP-2.3 — Poll dispatch (Handler API)** · 1.5 · `handler-callback-api.yaml`, ADR-004 · `GET pending-visits`, `ack`, `POST events`, `PUT result`, `PUT artifacts`; station poll worker feeding the same queue as push · acceptance: M2 scenario with one station in poll mode behind a compose network with no inbound port. **M**

**WP-2.4 — Manual approval, controller API, Individual Gateway v0** · 1.3 · ADR-008/011/017/018, mock-ups S3, G1, G2, G4 · pending-approval state with station timeout; station controller API (approve/deny with reason, revoke, suspend, withdraw, audit slice per controller); Gateway service aggregating several stations for one controller (organisation first; natural person by profile flag), conditions listed per network · acceptance: M2 scenario approval flow; a revocation mid-visit yields `visit.revoked` and the run's failure policy reaction. **L**

**WP-2.5 — Metadata: FDP endpoints and DSP-conformant catalogue (ADR-006/019)** · 0.4 · `station-catalog.shapes.ttl`, `examples/network-and-stations.ttl` · FDP-compliant metadata; `StationCatalog` with hosted datasets, one offer per dataset, distributions per mechanism, data service; join keys and `dct:conformsTo`; regenerated on configuration change · acceptance: catalogue validates against all catalogue shapes; the fixture catalogue for Noorderlicht MC is reproducible from configuration. **M**

**WP-2.6 — SQL, API/FHIR and Docker adapters** · 1.4 · ADR-002/003, station §5 · SQL (read replica, statement timeout, schema allow-list), API/FHIR facade (aggregate operations), Docker executor as isolated process (no egress, CPU/memory/wall-clock limits, read-only mounts, images from trusted garages by digest) · acceptance: the time-to-groin Docker train fixture runs in the sandbox against a synthetic dataset; an image with a wrong digest never starts. **L**

**WP-2.7 — Consoles: Station S1–S6, Handler H1–H4, Gateway G1/G2/G4** · 2.1–2.5 · `mockups/gen/*.py` (copy, states, layouts), design system sheet · one front-end with three role-based apps; the itinerary map component (live from events) and the replay scrubber; state = hue + icon + label everywhere · acceptance: screenshots match the mock-ups' structure; every state label in `mockups/gen/base.py STATES` appears from real data in the M2 scenario. **L**

### M3 — Multi-hop

**WP-3.1 — Two-phase orchestration (P7)** · 2.1, 2.2 · `plan` example B (two-phase), H6 · phase conditions per VisitResult, selected/not-selected/not-evaluated causes, "selected s of m, delivered d of s" · acceptance: M3 part 1 with six fixture stations. **S**

**WP-3.2 — Discovery chain (P4) and onward state** · 3.1 · `plan-time-to-groin.jsonld`, `onward` block, `routing`, ADR-015/016 · selectors on VisitResult, budget, stop condition, per-hop agreements, pruning, `onward.destination = linkage` hand-over with digests · acceptance: M3 part 2 reproduces the events and envelope shapes of `examples/protocol/` for hop 1 and completes the chain on fixture stations. **M**

**WP-3.3 — Linkage Station reference implementation (ADR-022)** · 1.4 · FDT-O v2 `LinkageStation`, `pseudonymSpace`, mechanism `IdentifierTranslation` · a station whose only adapter translates pseudonyms between two fixture spaces (a fake TTP), visited with the same protocol, releasing only `Pseudonym`-class state · acceptance: the translation visit in M3 yields an envelope with `onward.stateClass = Pseudonym` and never a record-level field. **M**

**WP-3.4 — Directory v0 and Garage v0** · 2.5 · ADR-020/024, `GarageCatalog`, `trains-and-plans.ttl` · Directory harvests self-descriptions and catalogues, answers mechanism/theme/network/join-key queries (P2b target queries); Garage serves `GarageCatalog` with train offers, payload digests and provenance; station digest verification points here · acceptance: the P2b plan resolves its target set from the Directory; a tampered payload is rejected at PEP 1 by digest. **M**

**WP-3.5 — Consoles: H5, H6, H7 (map), S7 audit explorer, S8 settings, S9 public page, G3 condition editor** · 2.7 · mock-ups · acceptance: S7 shows the justification chain of a real `visit.rejected` event; S9 renders from the station's own catalogue. **M**

### M4 — Hardening and alignment

**WP-4.1 — Composition (P8) and PROV-O run records** · 3.2 · patterns §9 P8, ADR-023 · DAG phases, typed outputs, optional inputs, pruning along dependencies; PROV-O record linking visits, agreements, artefacts, parameters · acceptance: M4 scenario; the run record validates against `RunShape` and answers "which outputs derive from a revoked visit". **M**

**WP-4.2 — DSP mapping tests and alignability self-description (ADR-019/021)** · 2.5 · `mapping/state-machines.md`, register A–H · assert the FDT ↔ DSP state mapping on every transition; self-description carries processing location, memberships, trusted issuers; Gaia-X-mappable shapes noted, not certified · acceptance: mapping tests green; register items marked v1 have a test or a documented gap. **S**

**WP-4.3 — Profiles, packaging, security review** · all · ADR-003/012, station §9 · one image, three profiles (personal SQLite, team PostgreSQL, enterprise HA with external queue); threat review of PEP 1, token handling, Docker sandbox, artefact egress · acceptance: the M3 scenario runs under each profile; review findings triaged into issues. **M**

**WP-4.4 — Conformance material and documentation** · 4.1–4.3 · protocol §8 · conformance checklist and fixture suite for third-party stations and Handlers; operator and controller guides derived from the console copy · acceptance: a station implemented only from `fdt-commons` + this material passes the suite. **S**

## 6. Dependency graph (summary)

```
0.1 → 0.3 → 0.4 → 1.1 → 1.2 → 1.3 → 1.4 ┐
0.2 (needs D2)                 1.1 → 1.5 ┼→ 2.1 → 2.2 → 3.1 → 3.2 → 4.1
                               1.5 → 2.3 │   1.3 → 2.4 ──────┘  1.4 → 3.3
                               0.4 → 2.5 ┼→ 3.4 → 4.2          2.7 → 3.5
                               1.4 → 2.6 ┘   all → 4.3 → 4.4
```

## 7. Decisions still needed from Luiz (do not decide these in code)

| Id | Decision | Why it matters | Default until decided |
|---|---|---|---|
| **D1** | Handler (and Gateway) implementation language: evolve the Java 17 / Spring Boot prototype, or rebuild in Python alongside the station | Team skills, reuse of the prototype's plan/job model, one or two stacks for the agent to maintain. ADR-001's reasoning for the station (community contributions, no obligation to the Java prototype) applies equally | Handler core as a Python library + CLI (WP-1.5) so orchestration logic is testable either way; UI decision deferred to WP-2.7 |
| **D2** | Location of the FDT-O ontology file (repository/branch) | WP-0.2 cannot merge the delta or settle the namespace without it | Delta stays a sidecar; shapes use `https://w3id.org/fdt#` |
| **D3** | Console technology (the mock-ups are framework-neutral) | One codebase for three apps; the Nuxt prototype exists | Whatever D1 implies; keep the design system from `mockups/gen/base.py` |
| **D4** | First target networks and identity providers for the compose demo (fixture OIDC only, or a real test IdP such as an institutional one) | WP-1.2 trusted-issuer configuration | Fixture OIDC provider in compose |
| **D5** | Whether the JMESPath library may be vendored into the repositories (registries were unreachable from both environments during the design sessions) | WP-2.1 | Vendor a compliance-tested implementation with its licence |

## 8. Definition of done and change protocol

A work package is done when: its acceptance scenario runs in CI; every request/response it handles is validated against the `fdt-commons` schema or shape; every decision it takes emits an event with a justification; its console copy (if any) uses the outcome vocabulary of ADR-026; `OPEN-QUESTIONS.md` has no unanswered question blocking it; and its documentation states which ADRs it implements.

Changing a contract: edit `fdt-commons` (and `FDT-O` if ontological), bump the version, add a `FINDINGS.md` line, run its validators, then update consumers. Changing an architectural decision: draft an ADR (Context / Decision / Alternatives / Consequences) in `fdt-ecosystem-architecture.md` with status *Proposed* and stop the affected work package until Luiz accepts it — this is how ADR-025/026/027 came about.

## 9. Risks

Approval latency in real deployments will dominate run times — the failure policy and the "waiting for approval at X" state exist for this; design the demo data so a pending approval is visible, not hidden. The Docker sandbox is the largest security surface (ADR-003): keep it process-isolated and behind PEP 3 from the first commit. Record-level leakage through "aggregates" is the main correctness risk — PEP 3 rules must be tested with adversarial fixtures (small cells, quasi-identifiers), not only the happy path. Finally, the DSP mapping is documentation in v1; do not let a v2 binding sneak in through the protocol server — the protocol is FDT's own until ADR-019's v2 step.

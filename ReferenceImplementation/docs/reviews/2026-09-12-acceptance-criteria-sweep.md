# Sweep — are the work packages' acceptance criteria runnable? (OPEN-QUESTIONS Q10)

| | |
|---|---|
| **Scope** | Every work package in `fdt-implementation-plan.md` §5, WP-0.1 through WP-4.4 (25 packages), against the contracts as they are: `fdt-commons` v0.7.0, `FDT-O` v2.0.0 (branch `fdt-o-v2`), term namespace `https://w3id.org/fdt/fdt-o#`. |
| **Question asked of each criterion** | (1) Do the artefacts it names exist? (2) Are they internally consistent — is the named output derivable from the named inputs? (3) Does the criterion exercise the path it claims? |
| **Method** | Everything below was checked against the files, not the descriptions of the files. `make check` is green (3 valid Turtle files, 8 counter-examples, 1 JSON-LD round-trip, 14 protocol/condition fixtures, 10/10 JMESPath cases, 42/42 ontology terms). The three probes in `tests/probes/` were re-run (agreement probes: CONFORMS on A, B, C, E, G; descriptor probe: VIOLATES `RequestShape`; schema probes: invalid on all six). The cross-fixture claims — which station supports which mechanism, which offer a request template can reach, what the digests are, which output schemas are served — were checked with an rdflib script against `examples/*.ttl`, `vocab/*.ttl` and `FDT-O/ontology/fdt-o.ttl`; the results are quoted inline. No contract, fixture or component file was changed. |
| **Working tree note** | The WP-0.3/WP-0.4 work that was uncommitted while the sweep ran (`fdt-commons/tools/gen_models.py`, `tests/test_models.py`; `FAIRDataStation-py`'s self-description and its tests) has since landed in `2f0ca03`. It was not touched by the sweep and is not evaluated here. |
| **Citation style** | `plan:78` is line 78 of `fdt-implementation-plan.md`; other paths are relative to `ReferenceImplementation/` unless they start with `mockups/` or name an architecture document. Turtle prefixed names escape the slash (`ex:net\/stroke-oost`); IRIs are quoted here in the unescaped `ex:net/stroke-oost` form. |

## 0. The one-paragraph result

**2 of 25 criteria are runnable as written, 11 are runnable with caveats, and 12 are not runnable** — the whole of M1 (five packages), five of M3/M2's core packages, and two of M4. WP-1.3's three defects are not an outlier: they are the visible corner of **one fixture set written around a single story (the time-to-groin discovery chain) that is internally inconsistent about the action its own train performs, and that never describes the M1 scenario at all.** No fixture station hosts a dataset a SPARQL train can reach, no offer auto-approves any request the fixtures contain, no payload has real bytes behind its digest, and the time-to-groin train — a `DockerTrain` — is requested, offered and agreed as `runQuery` in Turtle and `executeContainer` in JSON, then dispatched down a chain where two of four downstream stations do not support Docker at all. Roughly a dozen decisions, listed in §3, would fix all twelve.

---

## 1. The table

| WP | Verdict | One line |
|---|---|---|
| **M0** | | |
| 0.1 Metaproject and CI | **runnable** (done) | `make check` green on a clean clone; the criterion names nothing that does not exist. |
| 0.2 FDT-O v2 merge | runnable with caveats | Criterion names the namespace D2 rejected (`https://w3id.org/fdt#`) and a path that no longer exists (`FDT-O-v2/tests/validate.py`); its second clause (`owl:imports` resolves) is blocked by Q1. Reword. |
| 0.3 Generated models | runnable with caveats | The four fixtures exist; `run-state` `$ref`s a remote IRI (finding 15), `negotiation.request` is typed `object` so the generated model is untyped, and "byte-identical after normalisation" defines no normalisation. |
| 0.4 Station skeleton | runnable with caveats | Shape and fixture networks exist; the criterion names only the `fdt-commons` shape while FDT-O's `DataStationShape`/`LinkageStationShape` also apply (finding 18); `fdt-p:processingLocation` is an `odrl:LeftOperand` used as a station property (finding 17). |
| **M1** | | |
| 1.1 Visit protocol server | **not runnable** | The hop-1 descriptor's embedded request violates `RequestShape` and asks an action the offer never grants — under 1.2's own check the descriptor is Rejected, not accepted; the events "up to pending-approval" need PEP 1 and NEG, which are WP-1.2 and 1.3; no wrong-digest fixture exists. |
| 1.2 PEP 1 and payload validation | **not runnable** | "All `examples/invalid/*` that concern requests/trains" is one file; there is no invalid request fixture at all; the digest check has no payload bytes to check (placeholders: `sha256("test")` and a corrupted empty-string hash); "refused" is the wrong ADR-026 word for PEP 1. |
| 1.3 Negotiation on arrival | **not runnable** | Q9, findings 19, 20, 21, 31; Q12/Q13 open. No change since Q9 was written; confirmed by re-running the probes. |
| 1.4 Orchestrator, PEP 2/3, SPARQL adapter | **not runnable** | The M1 scenario has no fixture: no station hosts a SPARQL-reachable dataset, no offer auto-approves `gd-2026`, the gene–disease output schema is served by nothing, there is no test graph and no adversarial (k-violating) result. |
| 1.5 Handler core v0 | **not runnable** | The only JSON-LD plan is the M3 discovery chain; the gene–disease plan exists only in Turtle, is a three-station fan-out (M2), and one of its entry stations cannot run a SPARQL train. There is no P1 single-visit plan anywhere. |
| **M2** | | |
| 2.1 Conditions engine | **runnable** | `conditions.cases.json` exists, 10 cases, all executed and green in CI already. Caveat only: the `PhaseResults` scope has no schema and no case. |
| 2.2 Failure policy and completeness | runnable with caveats | Target run fixture exists and conforms; no P3 Sequence plan fixture; the P7 plan needs the Directory (WP-3.4); the fixture refusal at `rav-oost` is not derivable from the request template (the offer would auto-approve it). |
| 2.3 Poll dispatch | runnable with caveats | Contract complete (`handler-callback-api.yaml`); inherits the M2 scenario's fixture problems. |
| 2.4 Manual approval, controller API, Gateway | runnable with caveats | Approval fixture exists (`evt-registry-research`, events 4–5); the controller API it must implement has **no contract anywhere**; what a human decision records is undecided (Q13); the natural-person path's dataset is an untyped IRI. |
| 2.5 Metadata and catalogue | runnable with caveats | Fixture catalogue conforms; Noorderlicht advertises Docker but offers no Docker distribution, so "reproducible from configuration" needs one of the two changed; no `dcat:theme` anywhere (needed by 3.4). |
| 2.6 SQL, API/FHIR, Docker adapters | **not runnable** | No image exists; the digest is `sha256("test")`; no synthetic dataset; the payload URL differs between the Garage fixture and the descriptor; the action question (runQuery vs executeContainer) is unsettled. |
| 2.7 Consoles S1–S6, H1–H4, G1/G2/G4 | **not runnable** as written | "Every state label in `STATES`" is 31 labels, 11 of which the M2 scenario cannot produce; the mock-up copy the criterion says to reuse writes "rejected at matching" for what ADR-026 calls Refused. |
| **M3** | | |
| 3.1 Two-phase orchestration | **not runnable** | Names "plan example B (two-phase)" — B is the discovery chain, C is two-phase; plan C's `targetQuery` asks `FHIRAPI` for a SPARQL train and `theme = heart-failure` when no dataset has a theme; "six fixture stations" — three exist in that network and one hosts data. |
| 3.2 Discovery chain and onward state | **not runnable** | Two of four downstream stations lack the Docker mechanism; every downstream offer permits `runQuery` only; the linkage offer permits `translateIdentifiers`, which the request template never asks; `ex:dataset/linkage-oost-service` is an untyped IRI; the hop-1 descriptor is invalid (finding 31). |
| 3.3 Linkage station | runnable with caveats | Station, mechanism and `pseudonymSpace` exist; the translation service has no catalogue entry, no request asks for translation, and no output schema says what a translation envelope contains. |
| 3.4 Directory and Garage | **not runnable** | `targetQuery` has no grammar; nothing carries `dcat:theme`; the digest half shares 1.2's root cause (no payload bytes). The `GarageCatalog` fixture itself is fine. |
| 3.5 Consoles H5–H7, S7–S9, G3 | runnable with caveats | Depends on a real `visit.rejected` event, whose fixture WP-1.4 lacks. |
| **M4** | | |
| 4.1 Composition and PROV-O | **not runnable** | No P8 plan fixture; `fdt-run` has no terms for outputs, artefacts or derivation, so "which outputs derive from a revoked visit" has no vocabulary to be asked in. |
| 4.2 DSP mapping tests, alignability | runnable with caveats | `mapping/state-machines.md` conflates Refused and Rejected (finding 22) — asserting it "on every transition" would enshrine an ADR-026 violation; fix the mapping first. |
| 4.3 Profiles, packaging, security | runnable with caveats | Inherits M3; `deploy/profiles/` is empty, which is the deliverable. |
| 4.4 Conformance material | **not runnable** by a third party | `fdt-commons` is private (Q6), its IRIs resolve to nothing (Q1, finding 15), and `protocol/visit-protocol.md` §8 names as conformance material the fixtures finding 31 shows to be inconsistent. |

Counts: **runnable 2 · runnable with caveats 11 · not runnable 12.**

---

## 2. Per work package — what is missing or wrong, and the smallest fix

Ordered by what blocks soonest. Each entry quotes the criterion, states what was checked, and ends with the smallest change that would make it runnable. "Fixture" changes go through the `fdt-commons` change protocol (version bump, `FINDINGS.md` line, validators green); "reword" changes are edits to the plan.

### M0

#### WP-0.1 — Metaproject and CI (`plan:67`) — runnable

*Criterion:* "green CI on a clean clone."

Checked: `make check` runs `fdt-commons/tests/validate.py` (which chains `validate_protocol.py`, `tests/validate.py:203-207`) and `FDT-O/tests/validate.py`; both green (`Makefile:57-69`). The README records it done (`README.md:93`). The criterion names pySHACL replacing the subset validator — done (`fdt-commons/FINDINGS.md`, v0.5 note). Nothing to fix. The one caveat is not the criterion's: `FDT-O` is pinned to branch `fdt-o-v2` until PR #1 lands (Q5).

#### WP-0.2 — FDT-O v2 merge (`plan:69`) — runnable with caveats

*Criterion:* "`FDT-O-v2/tests/validate.py` passes against the merged ontology; `fdt-commons` profile `owl:imports` resolves."

- **Names a path that no longer exists in the metaproject.** `FDT-O-v2/` is a sidecar in the design folder; the merged repository is `FDT-O/`, and the validator is `FDT-O/tests/validate.py` (`FDT-O/README.md:14`). `make check` runs the right one (`Makefile:66-69`).
- **Names the namespace D2 rejected.** The deliverable says "one namespace (`https://w3id.org/fdt#`)"; D2 chose `https://w3id.org/fdt/fdt-o#` (`OPEN-QUESTIONS.md`, D2). The criterion's first clause passes anyway — 42/42 terms declared — but a reader of the plan is told the wrong namespace.
- **Second clause is blocked by Q1.** `vocab/fdt-profile.ttl:61` imports `<https://w3id.org/fdt/fdt-o>`, which resolves to nothing on the network; validators resolve it locally (`tests/validate.py:42-46`). "Resolves" is true only offline.

*Smallest fix:* reword to "`FDT-O/tests/validate.py` passes; one namespace, `https://w3id.org/fdt/fdt-o#`; the profile's `owl:imports` resolves locally in CI and publicly once Q1 is done."

#### WP-0.3 — Generated models (`plan:71`) — runnable with caveats

*Criterion:* "the four `examples/protocol/*.json` fixtures load into the models; round-trip is byte-identical after normalisation."

- The four fixtures exist (`examples/protocol/visit-descriptor-ttg-hop1.json`, `visit-events-ttg-hop1.json`, `visit-result-ttg-hop1.json`, `visit-result-refused.json`) and validate (`make check`).
- `schemas/run-state.schema.json:77,81` `$ref` `https://w3id.org/fdt/schemas/visit-result` by absolute IRI; a code generator fetches it and gets a 404 (finding 15). The criterion says nothing about the local resolution step every generator needs.
- `visit-descriptor.schema.json:54` types `negotiation.request` as `{"type": "object"}`. The generated model therefore has no fields for the ODRL request — which is exactly what let finding 31 go unnoticed. A round-trip through an untyped dict is trivially byte-identical and proves nothing about the request.
- "Byte-identical after normalisation" names no normalisation. Two JSON serialisers differ on key order, whitespace, float formatting and Unicode escaping.

*Smallest fix:* reword to "the four fixtures load; serialising back and comparing under RFC 8785 (JSON Canonicalization Scheme) is identical; generation resolves `$ref`s from `schemas/` locally (finding 15)". Separately — a contract decision, not this WP's — whether `negotiation.request` gets a JSON Schema of its own (§3, decision I).

#### WP-0.4 — Station skeleton (`plan:73`) — runnable with caveats

*Criterion:* "self-description validates against `station-catalog.shapes.ttl` (`StationSelfDescriptionShape`) with a membership in a fixture network."

- Shape exists (`shapes/station-catalog.shapes.ttl:71-87`), the three fixture networks exist (`examples/network-and-stations.ttl:17-25`), and Noorderlicht is a worked example with two memberships (`:32-40`). Runnable.
- **Two shape sets apply and the criterion names one** (finding 18). FDT-O's `DataStationShape` requires `dct:title`, `supportsInteractionMechanism` and a `StationOwnerShape`-conformant owner (`FDT-O/shapes/DatastationShape.ttl:20-63`); `LinkageStationShape` requires two `pseudonymSpace` values (`:65-77`). A self-description that satisfies only the `fdt-commons` shape can fail FDT-O's.
- `fdt-p:processingLocation`, required by the shape (`station-catalog.shapes.ttl:75`), is declared `a odrl:LeftOperand` (`vocab/fdt-profile.ttl:44`) — finding 17. The skeleton will emit a left operand as a station property, correctly per the shape and incorrectly per the vocabulary.
- Principle 1 ("enabled adapters ⇒ `supportsInteractionMechanism`") is being tested by the concurrent WP-0.4 work (`FAIRDataStation-py/tests/test_principle_1.py`); the fixture it mirrors (`test_fixture_fidelity.py`) advertises Docker on Noorderlicht (`network-and-stations.ttl:34`) while the dataset's distributions are SQL and FHIR only (`:55-56`). See WP-2.5.

*Smallest fix:* name both shape files in the criterion ("…and against `FDT-O/shapes/DatastationShape.ttl`"), and resolve finding 17 in the vocabulary before the skeleton's self-description becomes a fixture others copy.

### M1

#### WP-1.1 — Visit protocol server (`plan:77`) — not runnable

*Criterion:* "the hop-1 fixture descriptor is accepted and produces an event stream schema-identical in shape to `visit-events-ttg-hop1.json` up to `negotiation.pending-approval`; a descriptor with a wrong digest is rejected at PEP 1 with `outcome: Rejected`."

Three independent problems, one of them new.

1. **The descriptor cannot be "accepted" by a conformant station.** Its embedded request (`examples/protocol/visit-descriptor-ttg-hop1.json:39-68`) has no `fdt-p:train` and no `fdt-p:underNetwork`, so it violates `RequestShape` and `PolicyCommonShape` — re-confirmed by `tests/probes/descriptor_request_probe.py` this session. `visit-protocol.md:74` says PEP 1 validates it against `RequestShape`. The same descriptor WP-1.1 must accept, WP-1.2 must reject. It also asks `fdt-p:executeContainer` (`:48`) while the only offer in that network permits `runQuery` (`examples/policies.ttl:25`), so the fixture's `negotiation.matched` (`visit-events-ttg-hop1.json:43-57`) is not derivable from the fixtures it names (finding 31).
2. **The criterion reaches into two later work packages.** Events 1–4 of the fixture are `visit.received` at PEP 1 and three `negotiation.*` events at NEG (`visit-events-ttg-hop1.json:10-77`). PEP 1 is WP-1.2, negotiation is WP-1.3; WP-1.1 depends only on 0.4 (`plan:77`). A protocol server alone can emit `visit.received` and nothing else honestly.
3. **No wrong-digest fixture exists.** `examples/protocol/` has no `invalid/` directory (checked), and `validate_protocol.py` checks only valid fixtures (`tests/validate_protocol.py:39-43`). A negative fixture is trivial to write, but "fixtures before features" (`plan:24`) says it should exist before the code.

A fourth point is about M1 rather than WP-1.1: the M1 scenario is the **gene–disease SPARQL train** (`plan:54`), and the only descriptor fixture in the repository is for the **time-to-groin Docker train**, whose adapter is WP-2.6. M1's protocol server will be tested against a descriptor M1 cannot execute.

*Smallest fix:* (a) repair the descriptor's request — add `fdt-p:train`, `fdt-p:underNetwork`, the `legalBasis` constraint the Turtle request carries, and the action the architect decides on (§3, decision A); (b) add `examples/protocol/visit-descriptor-gene-disease.json` (SPARQL, inline `payload.content`, `reporting.mode: poll`) as M1's descriptor; (c) add `examples/protocol/invalid/visit-descriptor-wrong-digest.json` and have `validate_protocol.py` assert it fails the digest rule; (d) reword the criterion to "accepted with 202 and a `Location`; `visit.received` appears in `GET /events`; the wrong-digest descriptor is answered 400 with `outcome: Rejected`" and move the negotiation events to WP-1.3.

#### WP-1.2 — PEP 1 and payload validation (`plan:79`) — not runnable

*Criterion:* "all `examples/invalid/*` that concern requests/trains are refused with the shape's `sh:message` in the event justification."

- **The set is one file.** Of the eight `examples/invalid/*.ttl`, the only one about a train or request is `train-typed-as-dataset.ttl` — and it is a Garage-side train description, not something a station receives in a descriptor. There is **no invalid request fixture**: `RequestShape` (`shapes/policy.shapes.ttl:60-68`) has never had a counter-example, which is the finding-21 pattern (a shape with no negative subject).
- **"Refused" is the wrong word.** ADR-026 reserves Refused for a negotiation decline; a PEP 1 failure is **Rejected** (`plan:28`; `station-visit-api.yaml:198-199`; `fdt-itinerary-patterns.md` §9.1). The criterion for the checkpoint that must get this vocabulary right uses it wrongly.
- **The digest check has nothing real to check.** `examples/trains-and-plans.ttl:73` gives the gene–disease payload digest `sha256:3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855e` — the SHA-256 of the empty string with its leading `e` moved to the end (empty string: `e3b0c442…855`). `:76` gives the time-to-groin digest `sha256:9f86d081…0a08`, which is `sha256("test")` (computed this session). Neither payload exists as bytes anywhere: the query text at `https://garage.example.org/trains/gene-disease/1.3/query.rq` is fictional and no `.rq` file is in the repository; there is no container image. The same `3b0c…855e` digest is also the artefact digest in `visit-result-ttg-hop1.json:36` — one placeholder doing two jobs. A digest verification can only be tested against a payload whose hash is the recorded one; today that payload is the four bytes `test`.
- The criterion's other inputs — a fixture OIDC provider and a fixture Garage serving `trains-and-plans.ttl` — do not exist yet (`fixtures/.gitkeep`, `deploy/compose/.gitkeep`) but are this package's deliverables, so that is expected, not a defect.

*Smallest fix:* (a) add `examples/invalid/request-without-purpose.ttl` and `request-without-train.ttl` with expectations (the two `sh:message`s of `RequestShape`); (b) add `examples/payloads/gene-disease-1.3.rq` — an actual SPARQL query — and set `fdt-o:artifactDigest` to its true SHA-256; give the time-to-groin payload its own digest once an image exists (WP-2.6) and stop sharing `3b0c…` with the artefact; (c) reword "refused" to "Rejected at PEP 1 (`outcome: Rejected`)".

#### WP-1.3 — Negotiation on arrival, auto-approval path (`plan:81`) — not runnable

*Criterion:* "the fixture offer `evt-registry-research` and request `ttg-2026q3` produce an agreement equal in structure to `agr-9a01`; the HealthAI commercial request is Refused with the prohibition named."

Already recorded (Q9; findings 19, 20, 21, 23–25, 28, 30, 31; Q12, Q13). Re-verified this session: the agreement probes still report CONFORMS on A, B, C, E and G (`agreement_probes.py`), i.e. `AgreementShape` still cannot see whether an agreement follows from its offer; the descriptor probe still reports VIOLATES. Two additions the earlier notes did not make explicit:

- The **station policy** — the third named input of "offer × request × station policy" — has no fixture and its shape has never fired (finding 21; `shapes/policy.shapes.ttl:89-92`). WP-1.3's evaluator has no third input to read.
- The criterion's first half is now known to be **doubly** non-derivable: `agr-9a01` drops `legalBasis` (explained by the eligibility/usage split of finding 24) **and** drops the offer's `odrl:dateTime lt 2027-12-31` validity bound (`policies.ttl:28`), which is a usage constraint under that same split (finding 24's correction; finding 30). The event says "active until 2026-12-31" (`visit-events-ttg-hop1.json:90`), a date in neither input.

*Smallest fix:* as Q9's default plus: settle the derivation rule (§3, decision B) and regenerate `agr-9a01` from it so the fixture is the rule's output rather than its counter-example; add `examples/policies.ttl` entries for (i) `ex:request/healthai-2026q3` with `fdt-p:consumerType fdt-p:Commercial`, (ii) an offer with `requiresManualApproval false` reachable by a fixture request in its network (see WP-1.4 — one fixture serves both), (iii) one `fdt-p:StationPolicyDocument`.

#### WP-1.4 — Orchestrator, PEP 2, SPARQL adapter, PEP 3 (`plan:83`) — not runnable

*Criterion:* "M1 scenario; a result violating k triggers `visit.rejected` at PEP 3 with the S2 timeline's justification."

The M1 scenario (`plan:54`): "the gene–disease SPARQL train (fixture) is pushed to one station with a SQLite/rdflib test graph; auto-approved; runs through PEP 1–3". Checked against the fixtures with rdflib:

| Needed by M1 | In the fixtures |
|---|---|
| A station that supports SPARQL **and hosts a dataset** | `ex:station/ut` and `ex:station/radboud-like` support SPARQL (`trains-and-plans.ttl:101,104`) but have **no catalogue, no dataset, no offer**. The three stations that host data (`noorderlicht`, `rav-oost`, `zuiderlicht`) do not support SPARQL (`network-and-stations.ttl:34,61,84`). No hosted dataset has a SPARQL distribution. |
| An offer that **auto-approves** the gene–disease request | `ex:request/gd-2026` (`trains-and-plans.ttl:96-99`) is under `health-research-nl` and states only `purpose`. The only offer in that network is `evt-registry-research`, which has `requiresManualApproval true` and requires `consumerType` and `legalBasis` the request does not carry — fail closed. The only `false` offer, `rav-rides-research`, is under `stroke-oost` and SQL-only. **No fixture pair auto-approves.** |
| An output schema for PEP 3's "permitted output fields per `outputSchema`" | `ex:output/gene-disease-table dct:conformsTo <https://garage.example.org/shapes/aggregate-table>` (`trains-and-plans.ttl:39`) — served by nothing in `schemas/`. The only output schema that exists is the time-to-groin one (`schemas/examples/time-to-groin-output.schema.json`). |
| A test graph | `fixtures/` contains `.gitkeep`. |
| A **k-violating result** | None. The S2 mock-up's job-31b7 (`mockups/gen/station.py:54`: "Aggregate contains 2 cells with count < 5 — violates duty k-anonymity threshold k = 5") is sample data about a FHIR train, EU-CardioNet and `agr-8f19`, none of which are fixtures. |

So the path the criterion names — SPARQL train, auto-approved, inspected — has no station, no offer, no schema, no data and no adversarial result to run against. The **k-violation** is the single most important PEP 3 test in the plan (`plan:153`: "PEP 3 rules must be tested with adversarial fixtures") and it is the one with no fixture.

*Smallest fix:* one coherent M1 fixture, added to `examples/`: (a) a hosted dataset at `ex:station/ut` with a SPARQL distribution and a catalogue; (b) an offer over it, under `health-research-nl`, `requiresManualApproval false`, whose constraints `gd-2026` satisfies as it stands (`purpose eq R&D`), with an `odrl:aggregate` duty `kAnonymity gteq 5`; (c) `schemas/examples/gene-disease-output.schema.json` declaring the aggregate table's fields, and `ex:output/gene-disease-table` pointed at it; (d) a small Turtle test graph in `fixtures/` whose gene–disease counts include cells below 5, so the same graph yields both the passing and the rejected result depending on the parameters; (e) `examples/protocol/visit-result-rejected-k.json` (`state: rejected`, `inspection.outcome: rejected`, `reason`, `justification.rule: k-anonymity(k=5)`) as the target envelope. Reword "the S2 timeline's justification" to that fixture.

#### WP-1.5 — Handler core v0 (`plan:85`) — not runnable

*Criterion:* "M1 scenario driven by `fdt-handler run plan.jsonld`."

- The only JSON-LD plan is `examples/plan-time-to-groin.jsonld` — a P4 discovery chain, Docker train, linkage station, four phases. That is the **M3** scenario (`plan:56`). Loading it exercises WP-1.5's parser well and its M1 story not at all.
- The gene–disease plan `ex:plan/gene-disease-fanout` exists **only in Turtle** (`trains-and-plans.ttl:81-94`), so `fdt-handler run plan.jsonld` has no file to be given. It is also a **three-station fan-out** — the M2 scenario (`plan:55`) — and one of its entry stations, `noorderlicht`, does not support SPARQL (rdflib check: `entry ex:station/noorderlicht supports ['Docker','FHIRAPI','SQL'] -> train mechanism supported: False`).
- There is **no P1 `SingleVisit` plan** in any serialisation, although the pattern is in the shape's list (`shapes/run.shapes.ttl:37`) and M1 is, by name, one visit.

*Smallest fix:* add `examples/plan-gene-disease-single.jsonld` (pattern `SingleVisit`, one entry station `ex:station/ut`, request `gd-2026`, a failure policy) **and** its Turtle twin in `trains-and-plans.ttl`, so `validate.py`'s round-trip pass covers it (`tests/validate.py:181-199`). Either drop `noorderlicht` from the fan-out plan or give it a SPARQL mechanism (§3, decision F).

### M2

#### WP-2.1 — Conditions engine (`plan:89`) — runnable

*Criterion:* "every case in `conditions.cases.json` yields its expected value."

Ten cases, all with embedded envelopes valid against their scope's schema, all evaluated under jmespath 1.1.0 and green in `make check` (`tests/validate_protocol.py:53-66`). This criterion is already met by CI before the engine exists, which is the right way round. Two caveats, neither blocking:

- `fdt-run:PhaseResults` is a legal scope (`shapes/run.shapes.ttl:91`; `vocab/fdt-run.ttl:31`; ADR-025) with **no JSON Schema and no case**. The deliverable says "JMESPath evaluation over VisitResult / PhaseResults / RunState envelopes"; the third envelope is undefined.
- `fdt-run:RunState` is both an `owl:Class` (`vocab/fdt-run.ttl:40`) and an `fdt-run:EvaluationScope` individual (`:32`). Harmless in RDF, confusing to a generated enum.

*Smallest fix:* add `schemas/phase-results.schema.json` (an array of `visit-result`) and one P7 case over it, or strike `PhaseResults` from v1. D5 (vendoring) has expired (Q4).

#### WP-2.2 — Failure policy and completeness (`plan:91`) — runnable with caveats

*Criterion:* "simulated stations produce Finished / PartiallyDelivered / FailedRun exactly per §9 table for P2, P3, P7"; target shape `ex:run/ttg-2026q2-01`.

- The target run exists, conforms, and uses only declared terms (`trains-and-plans.ttl:182-194`; `refusedCount`/`skippedCount` declared at `vocab/fdt-run.ttl:126-128`). The §9 table exists (`fdt-itinerary-patterns.md` §9.4).
- **P3 has no plan fixture.** The only `Sequence` itinerary in the repository is the invalid `plan-query-train-choreographed.ttl`. §9.4's P3 rule ("SkipBranch only for a step marked `optional`; otherwise FailRun") is enforced by no shape, so a P3 fixture is where it becomes testable.
- **P7's plan needs WP-3.4.** `ex:plan/hf-feasibility-then-analysis` has no `entryStation`, only a `targetQuery` (`trains-and-plans.ttl:159`) — a Directory query, and the Directory is WP-3.4, which is not among 2.2's dependencies (`plan:91`, `plan:127-133`).
- **The fixture refusal is scripted, not derived.** `ex:visit/q2-v3` at `rav-oost` is Refused with "quality-improvement purpose not covered by the ambulance service's research offer" (`trains-and-plans.ttl:191-192`; `visit-result-refused.json:11`). The request template carries `purpose eq ResearchAndDevelopment`, which `rav-rides-research` permits with `requiresManualApproval false` (`policies.ttl:41-54`) — a real station would **auto-approve** it. For a fake station scripted to refuse this is fine, but the criterion should say the outcomes are scripted, or the fixture should be one a real evaluator refuses (the commercial request, Q9).
- No descriptor fixture exercises `negotiation.agreement` (the retry path, `visit-descriptor.schema.json:55`), which "retries with `attempt`" needs.

*Smallest fix:* add a P3 `Sequence` plan fixture (three steps, one `optional`); give plan C `entryStation`s for WP-2.2's purposes (keep `targetQuery` as an alternative for 3.4); reword to "fake stations scripted per outcome"; add a retry descriptor fixture with `negotiation.agreement`.

#### WP-2.3 — Poll dispatch (`plan:93`) — runnable with caveats

*Criterion:* "M2 scenario with one station in poll mode behind a compose network with no inbound port."

All five operations the deliverable lists are in `protocol/openapi/handler-callback-api.yaml:21-108`. The criterion is testable once compose exists. It inherits every M2 fixture problem above (no auto-approval, no commercial request, a fan-out entry station that cannot run the train). Nothing of its own to fix.

#### WP-2.4 — Manual approval, controller API, Gateway v0 (`plan:95`) — runnable with caveats

*Criterion:* "M2 scenario approval flow; a revocation mid-visit yields `visit.revoked` and the run's failure policy reaction."

- The approval fixture is the best-covered path in the repository: `evt-registry-research` requires approval (`policies.ttl:22`) and events 4–5 show `pending-approval → active` with `approval.controller` and `expiresAt` (`visit-events-ttg-hop1.json:58-94`). `visit.revoked` is in the event enum and requires a `reason` (`visit-event.schema.json:63,215-233`); `fdt-run:Revoked` and `onRevoked` exist. Constructible.
- **The controller API has no contract.** `station-visit-api.yaml:180`: "Revocation, approval and suspension are controller actions performed through the station console or the Individual Gateway, not through this API." No OpenAPI path, JSON Schema or shape for approve/deny/revoke/suspend/withdraw exists in `fdt-commons` (grep of `protocol/` finds only the Handler's `cancel`). The ground rules say models are generated from contracts (`plan:23`); there is nothing to generate from. The access-match review ranks this fourth by consequence (`docs/reviews/2026-09-12-access-match-process.md` §3.2 M3, §5 #4).
- **What the decision records is undecided** (Q13; findings 26, 27). The Gateway's G4 screen is built around a match summary that no contract persists.
- The natural-person path (`ex:party/jansen`, `ex:offer/jansen-activity`) targets `ex:dataset/jansen-activity-data`, which appears once in the whole fixture set — as that offer's target (`policies.ttl:59`) — with no type, no station, no catalogue.

*Smallest fix:* write `protocol/openapi/station-controller-api.yaml` (approve / deny / revoke / suspend / withdraw, each with a mandatory `reason`, a decider, and the decision record Q13 settles) **before** the Gateway code, under the change protocol; either type `ex:dataset/jansen-activity-data` as a `HostedDataset` on a personal station or strike the natural-person clause from v0's acceptance.

#### WP-2.5 — Metadata and catalogue (`plan:97`) — runnable with caveats

*Criterion:* "catalogue validates against all catalogue shapes; the fixture catalogue for Noorderlicht MC is reproducible from configuration."

- The fixture exists and conforms (`network-and-stations.ttl:42-56`; `make check`).
- **Not reproducible from one configuration as it stands.** The deliverable says "distributions per mechanism" and Principle 1 says "enabled adapters ⇒ `supportsInteractionMechanism`". Noorderlicht advertises `FHIRAPI, SQL, Docker` (`:34`) and its only dataset has `SQL` and `FHIRAPI` distributions (`:55-56`). A generator working from "Docker enabled" produces a Docker distribution the fixture lacks; one working from the distributions omits Docker from the station. One of the two must change, or the rule "one distribution per *enabled* mechanism" must be qualified per dataset.
- Finding 17 (`processingLocation` is a left operand) surfaces here too.
- No dataset anywhere carries `dcat:theme` (rdflib check: `hosted datasets with dcat:theme: NONE`). Not this WP's criterion, but WP-3.4's `targetQuery` depends on it, and the catalogue is where it would come from.

*Smallest fix:* decide whether the catalogue advertises a distribution for every enabled mechanism (then add a Docker distribution to the EVT registry) or per dataset (then reword Principle 1's consequence in the criterion); add `dcat:theme` to the fixture datasets.

#### WP-2.6 — SQL, API/FHIR and Docker adapters (`plan:99`) — not runnable

*Criterion:* "the time-to-groin Docker train fixture runs in the sandbox against a synthetic dataset; an image with a wrong digest never starts."

- **There is no image.** The payload is an IRI (`trains-and-plans.ttl:74-76`) with digest `sha256("test")`. Nothing can be pulled, so nothing can be run or digest-checked.
- **There is no synthetic dataset** (`fixtures/.gitkeep`).
- **The payload has two different URLs.** The Garage fixture says `https://garage.example.org/trains/time-to-groin/0.4/image` (`:75`); the descriptor says `oci://garage.stroke-oost.example/trains/time-to-groin@sha256:9f86…` (`visit-descriptor-ttg-hop1.json:25`). The station is told to verify the descriptor's payload against the Garage offer; the two fixtures disagree about where the payload is.
- **The action question.** Whether a container train's visit is `executeContainer` or `runQuery` is unsettled (§3, decision A); the adapter's PEP 2 check ("agreement covers this action") cannot be written until it is.

*Smallest fix:* build a tiny real image (a script that reads a CSV and emits the `time-to-groin-output` JSON) under `deploy/`, record its true digest in `trains-and-plans.ttl:76` and the descriptor, pick one URL form; add `fixtures/synthetic/evt-registry.csv`; reword to name them.

#### WP-2.7 — Consoles (`plan:101`) — not runnable as written

*Criterion:* "screenshots match the mock-ups' structure; every state label in `mockups/gen/base.py STATES` appears from real data in the M2 scenario."

- `STATES` has **31 keys** (`mockups/gen/base.py:71-107`). The M2 scenario (fan-out, one approval, one refusal, partial delivery; `plan:55`) cannot produce at least eleven of them: `fulfilled`, `expired`, `timedout`, `pruned` (P4 only), `dropped` (P5 only), `stopped`, `redacted`, `unreachable`, `synced`, `disabled`, `negotiating`. Five more are operational statuses, not visit or run states (`healthy`, `enabled`, `synced`, `unreachable`, `scheduled`). The criterion is unsatisfiable as written.
- **The mock-up copy contradicts ADR-026**, and the criterion says to take the words from the mock-ups (`FDTConsole/README.md`, "The screens are the specification"). `mockups/gen/station.py:28` and `gateway.py:36` write "Request from HealthAI B.V. **rejected at matching**"; `station.py:82` badges a no-agreement arrival as `rejected`. Under ADR-026 a decline at matching is **Refused**. `STATES["rejected"]` is used for both the agreement lifecycle (`base.py:80`) and the job lifecycle (`system.py:8-9`). Building the console from this copy reproduces exactly the conflation finding 22 records in the DSP mapping.

*Smallest fix:* reword to "every ADR-026 outcome the M2 scenario produces (Delivered, Refused, PendingApproval/Waiting, PartiallyDelivered, …) appears from real data; the remaining `STATES` entries appear from fixture data in Storybook-style fixtures"; correct the three mock-up strings to "refused at matching" (a change to the UI specification, so the architect's).

### M3

#### WP-3.1 — Two-phase orchestration (`plan:105`) — not runnable

*Criterion:* "M3 part 1 with six fixture stations"; input "`plan` example B (two-phase)".

- **Mislabelled input.** In `trains-and-plans.ttl` plan **B** is the discovery chain (`:108`) and plan **C** is the two-phase (`:150`).
- **Plan C cannot resolve a target set.** Its `targetQuery` is `"mechanism = FHIRAPI AND theme = heart-failure AND network = health-research-nl"` (`:159`). Checked: no hosted dataset carries `dcat:theme`; the only FHIRAPI stations in that network are `noorderlicht` and `radboud-like`; `radboud-like` hosts nothing. And the plan's train is `ex:train/gene-disease`, a **SPARQL** train (`:22-24`) — a query for FHIRAPI stations selects stations that cannot run it.
- **"Six fixture stations" do not exist** in `health-research-nl`: three are members (`ut`, `radboud-like`, `noorderlicht`) and only `noorderlicht` hosts a dataset — one whose offer requires manual approval and constraints `gd-2026` does not carry.
- **Hidden dependency.** Resolving a `targetQuery` needs the Directory (WP-3.4), which depends on 2.5; 3.1 depends on 2.1 and 2.2 only (`plan:105`, `:127-133`).
- The condition `result.count >= 50` (`:164`) reads a field of an output schema that is served by nothing (`https://garage.example.org/shapes/aggregate-table`).

*Smallest fix:* reword to "plan C"; rewrite plan C with a train whose mechanism matches its query (or `entryStation`s instead of a `targetQuery`); add to `network-and-stations.ttl` enough `health-research-nl` stations with a SPARQL-reachable dataset and an auto-approving offer each to make "six" true (or change "six" to what exists); give the gene–disease output a real schema declaring `count` (same fix as WP-1.4c).

#### WP-3.2 — Discovery chain and onward state (`plan:107`) — not runnable

*Criterion:* "M3 part 2 reproduces the events and envelope shapes of `examples/protocol/` for hop 1 and completes the chain on fixture stations."

The chain in the fixtures is `noorderlicht → linkage-oost → {rav-oost, zuiderlicht} → hap-oost`. Checked hop by hop:

| Hop | Station | Mechanisms | Offer permits | Can the Docker train visit? |
|---|---|---|---|---|
| 1 | `noorderlicht` | Docker, FHIRAPI, SQL | `runQuery`, `carryOnward` (manual) | mechanism yes; **action no** if the train is `executeContainer` (finding 31) |
| 2 | `linkage-oost` | IdentifierTranslation | `translateIdentifiers` | the request template `ttg-2026q3` asks `runQuery` + `carryOnward` and never `translateIdentifiers` — **action overlap is empty** (rdflib check). `agr-9a02` (`trains-and-plans.ttl:201-206`) grants an action its request never asked. Its target `ex:dataset/linkage-oost-service` is an **untyped IRI with zero triples** as subject. |
| 3 | `rav-oost` | **SQL only** | `runQuery` (auto) | **mechanism unsupported** → 415 per `station-visit-api.yaml:81` |
| 3 | `zuiderlicht` | Docker, SQL | `runQuery` only | mechanism yes; action no if `executeContainer`. `agr-9a04` grants `runQuery` for a Docker train. |
| 4 | `hap-oost` | **FHIRAPI only** | (no dataset, no offer) | **mechanism unsupported**, and nothing to negotiate about |

So "completes the chain on fixture stations" is false for two of the four downstream stations on mechanism alone, and for all of them on action if the train's action is `executeContainer`. The hop-1 half inherits WP-1.1's invalid descriptor. The envelope's `onward.handedOverDigest` is `sha256:aaaa…` (`visit-result-ttg-hop1.json:47`), a placeholder no linkage station can verify.

*Smallest fix:* decide the action model (§3, decision A); give `rav-oost` and `hap-oost` the Docker mechanism and `hap-oost` a dataset and offer; type `ex:dataset/linkage-oost-service` as a `HostedDataset` (or a service class) with a catalogue entry; make the linkage hop's request derivable — either a per-hop request fixture asking `translateIdentifiers`, or a stated rule for how the Handler rewrites the template per hop (§3, decision A).

#### WP-3.3 — Linkage station (`plan:109`) — runnable with caveats

*Criterion:* "the translation visit in M3 yields an envelope with `onward.stateClass = Pseudonym` and never a record-level field."

- Everything the ontology needs exists: `fdt-o:LinkageStation`, `fdt-o:pseudonymSpace` (two values on the fixture, `network-and-stations.ttl:98`), `fdt-inst:IdentifierTranslation` (`FDT-O/ontology/fdt-o.ttl:223-226,305-311`), `fdt-p:translateIdentifiers` (`vocab/fdt-profile.ttl:31`). `onward.stateClass` admits `Pseudonym` (`visit-result.schema.json:202`).
- What is missing is the same as 3.2's hop 2: no request asks for translation, the service IRI is untyped, and there is **no output schema for a translation result**, so "never a record-level field" is a sentence with no schema behind it — the `inspection.outputSchema` the envelope must now carry (v0.7) has nothing to point at. A pseudonym list is one row per person; the contracts should say explicitly that that is `Pseudonym`-class and not record-level, and what other fields may accompany it (none, presumably).

*Smallest fix:* `schemas/examples/identifier-translation-output.schema.json` (`additionalProperties: false`, one array of opaque strings, a count), referenced by a `generatesOutput` on the linkage service; plus 3.2's fixes.

#### WP-3.4 — Directory v0 and Garage v0 (`plan:111`) — not runnable

*Criterion:* "the P2b plan resolves its target set from the Directory; a tampered payload is rejected at PEP 1 by digest."

- `fdt-run:targetQuery` is `xsd:string` with the note "SPARQL or a structured filter" (`vocab/fdt-run.ttl:82`). The fixture's `mechanism = FHIRAPI AND theme = heart-failure AND network = health-research-nl` is neither; **no grammar exists**, so no Directory can be conformant or non-conformant.
- `theme` has nothing to match (no `dcat:theme` on any dataset); `mechanism = FHIRAPI` contradicts the plan's SPARQL train (WP-3.1).
- The `GarageCatalog` fixture is sound (`trains-and-plans.ttl:17-20`, conforms to `GarageCatalogShape`).
- The digest half has WP-1.2's root cause: no payload bytes exist, so "tampered" has no untampered original.

*Smallest fix:* define the `targetQuery` grammar in `vocab/fdt-run.ttl` (the four keys the fixture already uses: `mechanism`, `theme`, `network`, `joinKey`, with `AND` and `=`), add `dcat:theme` to the fixture datasets, fix plan C's mechanism; real payloads as in 1.2.

#### WP-3.5 — Consoles H5–H7, S7–S9, G3 (`plan:113`) — runnable with caveats

*Criterion:* "S7 shows the justification chain of a real `visit.rejected` event; S9 renders from the station's own catalogue."

S9's input exists (the catalogue fixture). S7's input — a real rejection — is the k-violation WP-1.4 has no fixture for; once WP-1.4's fixture exists this criterion is runnable. Nothing of its own.

### M4

#### WP-4.1 — Composition and PROV-O run records (`plan:117`) — not runnable

*Criterion:* "M4 scenario; the run record validates against `RunShape` and answers 'which outputs derive from a revoked visit'."

- **No P8 plan fixture.** `fdt-run:Composition` is in the pattern list (`shapes/run.shapes.ttl:38`) and `dependsOn` exists (`:131`), but no plan uses either. The H8 mock-up's agriculture × weather × soil DAG (`mockups/gen/more.py:57-82`) is sample data, not a fixture.
- **No vocabulary for the question.** `fdt-run` makes `Run` and `Visit` subclasses of `prov:Activity` (`vocab/fdt-run.ttl:36-37`) and uses `prov:startedAtTime`; there is **no** term for an output, an artefact, or a derivation (`prov:Entity`, `prov:wasGeneratedBy`, `prov:wasDerivedFrom` appear nowhere in `vocab/` or `shapes/`). `RunShape` (`run.shapes.ttl:143-153`) constrains none. "Which outputs derive from a revoked visit" cannot be asked of a record built from the current vocabulary. The envelope has a `provenance` link (`visit-result.schema.json:284`) to a PROV-O document whose shape is unspecified.
- No run fixture contains a `Revoked` visit.

*Smallest fix:* add `examples/plan-composition.ttl` (P8, three phases, one `optional`, `dependsOn` edges) and a run fixture of it with one `Revoked` visit and typed outputs; add `prov:Entity`-based output/artefact terms and `wasDerivedFrom` to `vocab/fdt-run.ttl` and a `RunProvenanceShape`, so the question in the criterion is a SPARQL query over a fixture.

#### WP-4.2 — DSP mapping tests and alignability (`plan:119`) — runnable with caveats

*Criterion:* "mapping tests green; register items marked v1 have a test or a documented gap."

- **The mapping to be asserted is wrong in one row.** `mapping/state-machines.md:15` maps "rejected (matching failed; approval denied; timeout)" to TERMINATED — three outcomes ADR-026 names Refused, Refused and TimedOut. A test that asserts this mapping "on every transition" enshrines the conflation (finding 22). Fix the mapping row first; the `dsp` block on events is informative (`visit-event.schema.json:178-189`), so the test surface is real.
- Q2: the `dspace:` namespace IRI and `timestamp` local name are unverified against the published context; a mapping test cannot be more right than that.
- The register (`fdt-data-space-alignment.md` §2) has 29 rows whose horizon column includes "v1" in some form (A1, A2, A5, A7, A8, B1–B4, B7, C1–C5, C7, C8, D1–D4, D6, E1, E3, F1–F4, H2). Several are organisational decisions (A1, A4, F1). "A test or a documented gap" accommodates that; the criterion is runnable as an audit.
- "Trusted issuers" in the self-description: `fdt-net:trustedIssuer` has domain `Network` (`vocab/fdt-network.ttl:29`), so a station carries them transitively through its memberships, not directly. Fine; say so.

*Smallest fix:* rewrite `state-machines.md:15` per ADR-026 (Refused → TERMINATED with reason; TimedOut → TERMINATED, "request withdrawn"); keep the criterion.

#### WP-4.3 — Profiles, packaging, security review (`plan:121`) — runnable with caveats

*Criterion:* "the M3 scenario runs under each profile; review findings triaged into issues."

Inherits M3 wholesale. `deploy/profiles/` is empty, which is the deliverable. Nothing of its own.

#### WP-4.4 — Conformance material (`plan:123`) — not runnable by a third party

*Criterion:* "a station implemented only from `fdt-commons` + this material passes the suite."

- `fdt-commons` is **private** until M1 runs (Q6). A third party cannot clone it.
- Its IRIs — the term namespace, the JSON-LD context, the schema `$id`s the generators fetch — **resolve to nothing** (Q1; finding 15). "Implemented only from `fdt-commons`" today means "implemented by someone who also patches their code generator".
- `protocol/visit-protocol.md:101` names `examples/protocol/` as "the test fixtures" for conformance; finding 31 shows the descriptor in that set is invalid against the shape the same section requires stations to apply.

*Smallest fix:* none inside this WP — Q1 and Q6 are the fix; and the fixture repairs above so that the conformance material describes one consistent visit.

---

## 3. Root causes and the decisions the architect has to make

Twelve criteria are not runnable, but they share far fewer causes. Deduplicated:

| # | Decision | Which work packages it unblocks | What exists today |
|---|---|---|---|
| **A** | **Which ODRL action does a container train perform, and is the request template rewritten per hop?** The `DockerTrain` `time-to-groin` is requested, offered and agreed as `fdt-p:runQuery` in Turtle (`policies.ttl:25,73,89`; `trains-and-plans.ttl:199,205`) and as `fdt-p:executeContainer` in the descriptor (`visit-descriptor-ttg-hop1.json:48`); the profile defines `executeContainer` as the container action (`fdt-profile.ttl:30`). The linkage hop's offer permits `translateIdentifiers`, which no request asks for. Either every fixture says `executeContainer` and the linkage hop gets its own request, or the plan's "target filled per visit" (`policies.ttl:67`) is widened to "target **and action** filled per hop" and that rule is written down. | 1.1, 1.3, 2.6, 3.2, 3.3 | inconsistent |
| **B** | **The agreement derivation rule and `AgreementShape`'s content** (findings 19, 23, 24, 25, 28, 30; Q12): what survives from offer × request × station policy (usage constraints including the validity bound), what is recorded as evidence, pinning digests, `fdt-p:train` and payload digest first-class. Then regenerate `agr-9a01`, `agr-9a02`, `agr-9a04` from it. | 1.3, 2.4, 4.1 | shape validates form only; probes A, B, C, E, G conform |
| **C** | **The two missing negotiation fixtures**: an offer that auto-approves a fixture request without a human, and the HealthAI commercial request a prohibition refuses (Q9, finding 20) — plus where `consumerType` comes from (access-match review §2.2 i). | 1.3, 1.4, 2.2, 2.4, 2.7 | none of the three exist |
| **D** | **The M1 station fixture**: a SPARQL-reachable hosted dataset with a catalogue at `ex:station/ut`, an auto-approving offer over it, a served `gene-disease-output` schema declaring `count`, a Turtle test graph in `fixtures/`, a P1 `SingleVisit` plan in JSON-LD and Turtle, and an adversarial (k < 5) result fixture. | 1.4, 1.5, 3.1, 3.5 | none exist; M1 has no fixture at all |
| **E** | **Real payload bytes and true digests**: a `.rq` file for gene–disease and a built image for time-to-groin, one URL form, distinct digests (today `sha256("test")` and a corrupted empty-string hash shared with an artefact). | 1.2, 2.6, 3.4 | placeholders |
| **F** | **Stations' mechanisms versus the plans that visit them**: `noorderlicht` in a SPARQL fan-out without SPARQL; `rav-oost` and `hap-oost` in a Docker chain without Docker; `hap-oost` with no dataset; Noorderlicht advertising Docker with no Docker distribution (Principle 1 vs "distributions per mechanism"). | 1.5, 2.5, 3.2 | mismatched |
| **G** | **P2b `targetQuery`**: a grammar for `fdt-run:targetQuery`, `dcat:theme` on fixture datasets, plan C's mechanism matching its train, and whether WP-3.1 depends on WP-3.4 or plan C gets `entryStation`s. | 2.2, 3.1, 3.4 | free text; no themes |
| **H** | **Pattern fixtures that do not exist**: P1 `SingleVisit`, P3 `Sequence`, P8 `Composition` (with a `Revoked` visit), and PROV-O terms for outputs/artefacts/derivation in `fdt-run`. | 1.5, 2.2, 4.1 | only P2, P4, P7 |
| **I** | **Contracts that do not exist**: the controller API (approve/deny/revoke/suspend/withdraw with the Q13 decision record); a JSON Schema or the `RequestShape` check for `negotiation.request`; a `PhaseResults` envelope (or its removal); `StationPolicyDocument` instance; the linkage translation output schema; typing `ex:dataset/linkage-oost-service` and `ex:dataset/jansen-activity-data`. | 0.3, 1.1, 1.3, 2.1, 2.4, 3.2, 3.3 | absent |
| **J** | **Criterion wording** (plan edits only): WP-0.2 namespace and path; WP-0.3 "normalisation" → RFC 8785; WP-1.1 scope (`visit.received` only, negotiation events to 1.3); WP-1.2 "refused" → "Rejected"; WP-2.2 "scripted outcomes"; WP-2.7 the `STATES` subset M2 can produce; WP-3.1 "example B" → "plan C"; WP-0.4 both shape files. | 0.2, 0.3, 0.4, 1.1, 1.2, 2.2, 2.7, 3.1 | — |
| **K** | **The mock-up copy "rejected at matching"** (`mockups/gen/station.py:28,82`; `gateway.py:36`) contradicts ADR-026; the mock-ups are the UI specification, so this is the architect's to change, not the console developer's. Same defect as finding 22 in `mapping/state-machines.md:15`, which WP-4.2 must not enshrine. | 2.7, 4.2 | contradicts ADR-026 |
| **L** | **Publication and visibility** (Q1, Q6): the term namespace, context and schema IRIs served; repository public. Nothing in the repository can substitute. | 0.2, 4.4 | unresolvable / private |

Decisions **A–E** are the ones on M1's path and should be taken first; **A** alone touches five packages and three agreements, and until it is taken the hop-1 fixtures — the only protocol fixtures the repository has — describe a visit no conformant station would run.

---

## 4. Reproducing this sweep

```sh
cd ReferenceImplementation
make check                                           # green
PY=.venv/bin/python
$PY tests/probes/agreement_probes.py                 # A, B, C, E, G conform (finding 28 open)
$PY tests/probes/descriptor_request_probe.py         # VIOLATES RequestShape; executeContainer vs runQuery (finding 31)
$PY tests/probes/schema_probes.py                    # all six invalid (finding 29 fixed)
```

The cross-fixture script used for §2 (stations × mechanisms × datasets × offers; plans × entry stations; request-template reachability; digests; served output schemas; typed IRIs) ran from the session scratchpad and is not part of the repository. Its eight checks are each a dozen lines of rdflib over `examples/*.ttl` + `vocab/*.ttl` + `FDT-O/ontology/fdt-o.ttl`; if the architect wants it kept, it belongs beside the probes in `tests/probes/` as `fixture_consistency_probe.py`, because it — like them — becomes a regression test the day the fixtures are fixed.

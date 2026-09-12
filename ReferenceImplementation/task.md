# Roadmap and progress

The 25 work packages of `fdt-implementation-plan.md` §4–§5, tracked here. Each box is checked
only when its **acceptance criterion has been run**, not when the code looks finished.

The plan remains the normative source for what each criterion says; where the criterion itself
is wrong — it names a fixture that does not exist, or a decision has since overtaken it — that
is noted under the package and carries the id of the sweep item or question that settles it
(`docs/reviews/2026-09-12-acceptance-criteria-sweep.md`, [`OPEN-QUESTIONS.md`](OPEN-QUESTIONS.md)).

**Next:** decision **Q14-B**, which is now the only thing between the contracts and WP-1.3.

| | | |
|---|---|---|
| **M0** Foundations | ✅ done | 12 Sep 2026 |
| **M1** One visit | 🟨 2 of 5 — WP-1.1, 1.2 done; WP-1.3 blocked on Q14-B | |
| **M2** Fan-out and governance | ⬜ not started | |
| **M3** Multi-hop | ⬜ not started | |
| **M4** Hardening and alignment | ⬜ not started | |

---

## M0 — Foundations ✅

Exit: `make check` runs every fdt-commons and FDT-O validation, models generate from the
contracts, and a station skeleton answers `GET /` with a valid self-description. **Met.**

- [x] **WP-0.1 — Metaproject and CI** · — · S
      *Acceptance: green CI on a clean clone.* Met. `make check` is the gate; CI runs contracts,
      console and a per-component matrix.
- [x] **WP-0.2 — FDT-O v2 merge** · 0.1 · S
      *Acceptance: FDT-O validators pass against the merged ontology; the profile's `owl:imports`
      resolves.* First clause met — 432 triples, v2.0.0 on branch `fdt-o-v2`. Second clause is
      blocked by Q1 (the IRIs are not published yet) and the criterion names the namespace D2
      rejected; reword (sweep J). Merge of [PR #1](https://github.com/FAIRDataTeam/FDT-O/pull/1)
      is Q5, yours.
- [x] **WP-0.3 — Generated models** · 0.1 · S
      *Acceptance: the protocol fixtures load into the generated models; regeneration is
      byte-identical.* Met, offline and reproducibly. **Finding 32**: the models accept envelopes
      the schema rejects — they are a typed view, not enforcement.
- [x] **WP-0.4 — Station skeleton** · 0.3 · M
      *Acceptance: the self-description validates against `StationSelfDescriptionShape` with a
      membership in a fixture network.* Met for all three profiles, served and curled.
      **Finding 33**: a station binding the wrong namespace still passed all three conformance
      tests — `sh:targetClass` selected nothing.

---

## M1 — One visit

Exit: the gene–disease SPARQL train reaches one station with a test graph, is auto-approved,
runs through PEP 1–3; the Handler CLI prints the event stream and the envelope; the invalid
fixtures are refused or rejected with the right reasons.

**Every M1 criterion was unrunnable** when the sweep asked (Q10). The contract work below fixed
the fixture side; the code has not started.

### M1 preparation — contracts and fixtures

- [x] **Q14-A — which action a container train performs.** `fdt-o:DockerTrain` performs
      `fdt-p:executeContainer`; offers, request template and two agreements corrected; the two
      chain stations that supported no container mechanism gained one. Finding 31 closed,
      finding 34 recorded. `fdt-commons` v0.8.0.
- [x] **Q14-E — real payload bytes and true digests.** Every declared digest is now the sha256
      of bytes in the repository; `tools/payloads.py` builds, stamps and re-checks them, and the
      deliberate wrong-digest fixture is asserted to stay wrong. Finding 36. v0.8.0.
- [x] **Q14-D — one coherent M1 fixture.** A SPARQL-reachable dataset at a SPARQL station, an
      offer that grants without a human, a test graph, the P1 plan in Turtle and JSON-LD, and a
      released and a k-violating result — all computed by running the train's own payload
      against the graph. Finding 37. v0.9.0.
- [ ] **Q14-B — the agreement derivation rule and what `AgreementShape` requires.**
      **Blocks WP-1.3.** Findings 19, 23–25, 28, 30 and the four decisions recorded in Q12: the
      evidence block, the validity window, the payload digest and the train as first-class terms
      on the agreement. `AgreementShape` still validates form, never derivation.
- [ ] **Q14-C — the auto-approving offer and the commercial request.** Q9 and finding 20: the
      HealthAI request WP-1.3's second clause names does not exist, and `consumerType` has no
      source. The M1 offer now covers the auto-approval half; this is the refusal half.

### Work packages

- [x] **WP-1.1 — Visit protocol server (Station API)** · 0.4 · M
      *Acceptance: the fixture descriptor is accepted and produces an event stream shaped like
      the fixture; a descriptor with a wrong digest is rejected at PEP 1 with `Rejected`.*
      **Both halves run**, under uvicorn and curl as well as in tests. The criterion's "up to
      `negotiation.pending-approval`" reaches into WP-1.2 and 1.3; scoped to the server, as the
      sweep recommended (J) — the visit stops at `negotiation.requested` behind a `Negotiator`
      interface and that is visible in the stream. 104 tests; six mutations, five caught at
      once, and the two survivors bought a bounded event stream and a test for the event log's
      own validation.
- [x] **WP-1.2 — PEP 1 and payload validation** · 1.1 · M
      *Acceptance: the invalid fixtures concerning requests and trains are refused with the
      shape's `sh:message` in the event justification.* **Met**, with the criterion's word
      corrected: ADR-026 calls this **Rejected**; a controller refuses. The three request
      counter-examples it needed did not exist and now do (finding 38); each is converted to
      the serialisation a descriptor carries and rejected in the shape's own words. Token
      verification is per network and checks signatures (ADR-017). Findings 39, 40, 41 came out
      of building it. Eight mutations, all caught.
- [ ] **WP-1.3 — Negotiation on arrival (auto-approval path)** · 1.2 · L
      *Acceptance: the fixture offer and request produce the target agreement; the commercial
      request is Refused with the prohibition named.* **Blocked on Q14-B**, and the second clause
      needs Q14-C. `agr-m1-01` is derivable from its own offer and request, so the first clause
      now has a reachable target — unlike `agr-9a01` (finding 19).
- [ ] **WP-1.4 — Orchestrator, PEP 2, SPARQL adapter, PEP 3** · 1.3 · L
      *Acceptance: the M1 scenario; a result violating k triggers `visit.rejected` at PEP 3 with
      a justification.* Fixtures ready, including the adversarial one: same train, same
      agreement, one parameter different, and PEP 3 must reach opposite outcomes.
- [ ] **WP-1.5 — Handler core v0 (library + CLI)** · 1.1 · M
      *Acceptance: the M1 scenario driven by `fdt-handler run plan.jsonld`.* Fixtures ready —
      `examples/plan-gene-disease-single.jsonld`, asserted isomorphic to its Turtle.

---

## M2 — Fan-out and governance

Exit: the fan-out plan across three stations (push and poll); one approval in the Gateway; one
refusal on commercial purpose; the run ends **Partially Delivered** with a completeness
statement.

- [ ] **WP-2.1 — Conditions engine (ADR-025)** · 1.5 · S
      *Acceptance: every case in `conditions.cases.json` yields its expected value.* The only
      M2 criterion that was runnable as written; the 10 cases are evaluated on every
      `make check`. `PhaseResults` scope has no schema and no case.
- [ ] **WP-2.2 — Failure policy and completeness (ADR-026)** · 2.1 · M
      Needs a P3 Sequence plan fixture; the fixture refusal at the ambulance service is not
      derivable from the request template.
- [ ] **WP-2.3 — Poll dispatch (Handler API)** · 1.5 · M
      Contract complete; inherits the M2 scenario's fixture gaps.
- [ ] **WP-2.4 — Manual approval, controller API, Individual Gateway v0** · 1.3 · L
      The controller API it must implement **has no contract anywhere** (sweep I); what a human
      decision records is Q13.
- [ ] **WP-2.5 — Metadata: FDP endpoints and DSP-conformant catalogue** · 0.4 · M
      Fixture catalogue conforms. `dcat:theme` exists on trains and on the M1 dataset only;
      WP-3.4 needs it more widely.
- [ ] **WP-2.6 — SQL, API/FHIR and Docker adapters** · 1.4 · L
      The payload is now a real OCI image layout with true digests, so "an image with a wrong
      digest never starts" is testable. Still needs a synthetic dataset per adapter.
- [ ] **WP-2.7 — Consoles: Station S1–S6, Handler H1–H4, Gateway G1/G2/G4** · 2.1–2.5 · L
      **Unsatisfiable as written**: 11 of the 31 state labels cannot arise in M2. Scope the
      criterion to the states the scenario produces (sweep J), and fix the mock-up copy that
      writes "rejected at matching" for what ADR-026 calls Refused (sweep K).

---

## M3 — Multi-hop

Exit: a two-phase plan selecting stations by condition; the time-to-groin chain through a
linkage station with per-hop agreements, a pending approval and a pruned branch; the itinerary
map live and in replay; Directory and Garage in use.

- [ ] **WP-3.1 — Two-phase orchestration (P7)** · 2.1, 2.2 · S
      The criterion names "plan example B (two-phase)"; B is the discovery chain, C is two-phase.
      Plan C queries `FHIRAPI` for a SPARQL train and a theme no dataset carries (sweep G).
- [ ] **WP-3.2 — Discovery chain (P4) and onward state** · 3.1 · M
      Q14-A fixed the actions and mechanisms; **finding 35** remains — the linkage service is an
      untyped IRI in no catalogue and the GP station publishes no dataset, so two hops have
      nothing to visit.
- [ ] **WP-3.3 — Linkage Station reference implementation (ADR-022)** · 1.4 · M
      Station, mechanism and pseudonym spaces exist; the request template now asks
      `translateIdentifiers`, so the linkage agreement derives. No output schema for a
      translation envelope yet.
- [ ] **WP-3.4 — Directory v0 and Garage v0** · 2.5 · M
      `targetQuery` has no grammar (sweep G). The digest half is now testable.
- [ ] **WP-3.5 — Consoles: H5, H6, H7 (map), S7, S8, S9, G3** · 2.7 · M
      S7 needs a real `visit.rejected` event — WP-1.4 now has the fixture for one.

---

## M4 — Hardening and alignment

- [ ] **WP-4.1 — Composition (P8) and PROV-O run records** · 3.2 · M
      No P8 plan fixture, and `fdt-run` has no terms for outputs, artefacts or derivation — so
      "which outputs derive from a revoked visit" cannot yet be asked (sweep H).
- [ ] **WP-4.2 — DSP mapping tests and alignability self-description** · 2.5 · S
      `mapping/state-machines.md` conflates Refused and Rejected (**finding 22**); asserting the
      mapping as it stands would enshrine an ADR-026 violation. Fix the mapping first.
- [ ] **WP-4.3 — Profiles, packaging, security review** · all · M
      `deploy/profiles/` is empty, which is the deliverable.
- [ ] **WP-4.4 — Conformance material and documentation** · 4.1–4.3 · S
      Not runnable by a third party while the repositories are private (Q6) and the IRIs resolve
      to nothing (Q1).

---

## Decisions this waits on

Decisions belong to Luiz (plan §7); code takes the conservative default in
[`OPEN-QUESTIONS.md`](OPEN-QUESTIONS.md) and carries the question id until then.

| | | Blocks |
|---|---|---|
| **Q14-B** | agreement derivation and `AgreementShape` | WP-1.3, WP-2.4 |
| **Q14-C** | the commercial request and where `consumerType` comes from | WP-1.3's second clause |
| **Q5** | merge FDT-O PR #1 | WP-0.2's close-out |
| **Q1** | publish the contracts at their `w3id.org` IRIs | WP-0.2, WP-4.4 |
| **Q6** | repository visibility | WP-4.4 |
| **Q11** | can an ODRL policy target part of a dataset | WP-1.3's scope, WP-2.5 |

## Dependency graph

```
0.1 → 0.3 → 0.4 → 1.1 → 1.2 → 1.3 → 1.4 ┐
0.2                            1.1 → 1.5 ┼→ 2.1 → 2.2 → 3.1 → 3.2 → 4.1
                               1.5 → 2.3 │   1.3 → 2.4 ──────┘  1.4 → 3.3
                               0.4 → 2.5 ┼→ 3.4 → 4.2          2.7 → 3.5
                               1.4 → 2.6 ┘   all → 4.3 → 4.4
```

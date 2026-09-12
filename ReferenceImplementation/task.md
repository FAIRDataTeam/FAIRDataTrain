# Roadmap and progress

The 25 work packages of `fdt-implementation-plan.md` §4–§5, tracked here. Each box is checked
only when its **acceptance criterion has been run**, not when the code looks finished.

The plan remains the normative source for what each criterion says; where the criterion itself
is wrong — it names a fixture that does not exist, or a decision has since overtaken it — that
is noted under the package and carries the id of the sweep item or question that settles it
(`docs/reviews/2026-09-12-acceptance-criteria-sweep.md`, [`OPEN-QUESTIONS.md`](OPEN-QUESTIONS.md)).

**Next:** **WP-5.0 — FDT-O v4 and the contracts ADR-030/033 need**, then WP-5.3 (`FDTRegistry`) and WP-5.4 (several stations, in two networks that differ on whether a machine may decide). The decision interview of 13 September 2026 closed every question that blocked M2 and M5: **ADR-030** — a train declares the data it needs as a SHACL model, non-RDF stations map with RML and publish a generated shape, and matching is structural coverage; **ADR-031** — a credential proves what a train's metadata only names; **ADR-032** — where a machine may not grant it may not refuse either, and must instead present its recommendation and evidence to a person; **ADR-033** — `fdt-o:DatasetPart`; and **ADR-028** accepted. Contracts move first, as always. WP-5.1 and WP-5.2 are done: FDT-O is at 3.0.0 and `make e2e` runs the Handler, a station and a Train Depot against each other with the payload digest traced from bytes to checkpoint.

| | | |
|---|---|---|
| **M0** Foundations | ✅ done | 12 Sep 2026 |
| **M1** One visit | ✅ done | 12 Sep 2026 |
| **M5** Testbed (new — ADR-029) | ⬜ next | |
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
- [x] **Q14-B — the agreement derivation rule and what `AgreementShape` requires.**
      A normative rule (`protocol/agreement-derivation.md`) and a checker run by `make check`,
      because the rule relates three documents and SHACL constrains one node at a time. Splits
      eligibility from usage (`fdt-p:constraintRole`), which is what makes `agr-9a01` derivable
      at all. Agreements are counter-signed by the train owner with a real Ed25519 key —
      **ADR-028, draft, needs your acceptance** (`docs/adr/`). Closes findings 19, 23–25, 28, 30.
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
- [x] **WP-1.3 — Negotiation on arrival (auto-approval path)** · 1.2 · L
      *Acceptance: the fixture offer and request produce the target agreement; the commercial
      request is Refused with the prohibition named.* **First clause met** — the evaluator
      produces an agreement **isomorphic** to the published `agr-m1-01`, and what it produces is
      run through the contracts' own checker. Refusal is exercised on a prohibition the fixtures
      do have (`odrl:sell`) and on an unevidenced eligibility fact; the *commercial* request the
      criterion names still does not exist (**Q14-C**, Q9/finding 20), so that one clause waits
      on a fixture, not on code.
- [x] **WP-1.4 — Orchestrator, PEP 2, SPARQL adapter, PEP 3** · 1.3 · L
      *Acceptance: the M1 scenario; a result violating k triggers `visit.rejected` at PEP 3 with
      a justification.* **Both met**, in tests and live under uvicorn: the M1 visit produces the
      published eight-event stream and the published envelope, and the adversarial visit — one
      parameter different, nothing else — is rejected at PEP 3 naming the agreement's
      `odrl:aggregate` duty. PEP 2 hashes the payload bytes immediately before the adapter gets
      them and compares with the digest the agreement pinned, which closes PEP 1's open item.
      Three contract gaps had to be closed first (`fdt-commons` v0.13–v0.15, findings 42–46);
      the largest was that **the k threshold lived in two places and the schema was winning**,
      so the duty was dead code and a disclosure decision was reported as a malformed result.
      27 mutations, 0 survivors — on the second pass, after the first harness turned out to be
      a check that could not fail.
- [x] **WP-1.5 — Handler core v0 (library + CLI)** · 1.1 · M
      *Acceptance: the M1 scenario driven by `fdt-handler run plan.jsonld`.* **Met**, and run
      three ways: in the Handler's own tests against a fake station replaying the fixtures, in
      `make e2e` with the real station over ASGI, and over HTTP under uvicorn driven by the
      command itself. The Handler resolves what the plan names, validates the plan *in the
      context of what it resolved* (the shapes constrain classes a plan file does not contain),
      builds the one document it authors and checks it against the descriptor schema before
      sending, follows the stream, and assembles a run state whose visits are the envelopes the
      station returned. Two contract gaps had to be closed first: an envelope could not say a
      visit was rejected before it ran (**finding 47**), so a Handler could describe a
      successful run and not a failed one; and `fdt-run:DropForRemainingRounds` is admitted by
      no shape (**finding 48**).

---

## M5 — Testbed

A running ecosystem, with user interfaces: **one Train Depot** holding several trains, **one
metadata registry** indexing stations and trains, **a few FAIR Data Stations**, and **one Train
Handler**. Decided 12 September 2026; **ADR-029** records what changed and why — the Garage
becomes the Depot down to the ontology, and the Directory becomes an FDP-Index-shaped registry
rather than a component of its own.

It re-orders the roadmap rather than adding to the end of it: WP-3.4 is re-scoped and pulled
forward, and console work that sat in WP-2.7 and WP-3.5 now has a reason to exist earlier.

- [x] **WP-5.1 — FDT-O v3: the Depot rename, and Train made abstract** · 0.2 · M — **done
      13 Sep 2026.** FDT-O 3.0.0, `fdt-commons` 0.17.0. `fdt-o:GarageCatalog` →
      `fdt-o:DepotCatalog`, `fdt-p:trainGarage` → `fdt-p:trainDepot`, `fdt-net:GarageRole` →
      `fdt-net:DepotRole`, no aliases; `fdt-o:Train` abstract (`dash:abstract`, enforced by
      `:TrainShape` — OWL has no abstract classes) and no longer `⊑ odrl:Asset`, so a train
      plays the asset role as the `odrl:target` of a policy. Fixtures are now
      `a fdt-o:SPARQLTrain` alone. `make check` green, `make e2e` 5 passed, station 187 and
      Handler 53 tests, ruff and `mypy --strict` clean.
      **Findings 49 and 50**, both uncovered by dropping the redundant `a fdt-o:Train`:
      every shape targeting `fdt-o:Train` had been selecting focus nodes by that assertion
      alone — SHACL resolves `sh:targetClass` through `rdfs:subClassOf*` in the **data** graph,
      and both checkers kept the hierarchy elsewhere — so with it gone they selected nothing
      and a train missing payload, title, output and theme validated clean. And
      `:LinkageStationShape` had never had an instance to check at all. Both checkers now mix
      the named-class hierarchy into the data graph (`tools/ontology.py`) and count what they
      select; 7 mutations, 0 survivors, against a green control. Q18 records whether the
      intermediate train families are abstract too (conservative default: not).
      **Repository renames are Q17** — `TrainDepot` and `FDTRegistry` still carry their
      old names on GitHub; everything inside them says Depot.
- [x] **WP-5.2 — Train Depot v0** · 5.1 · L — **done 13 Sep 2026.** `fdt-depot` 0.1.0,
      `fdt-commons` 0.18.0 with the Depot API contract. Serves `/`, `/catalogue`, `/trains`,
      `/trains/{t}`, `/trains/{t}/payload`, `/trains/{t}/output-schema` and a JWKS of the
      owner's **public** keys. Both halves of the acceptance criterion run against the real
      component: the station's PEP 1 resolves a train over HTTP and rejects a wrong digest, and
      the Handler builds a descriptor from the same Depot — `make e2e` now runs all three
      together and traces the digest from the bytes to the checkpoint.
      **What makes it an authority: it computes digests rather than repeating them.** It holds
      the bytes, hashes them at startup, and withholds any train whose bytes do not match its
      catalogue — saying so, because "I do not have it" and "I have it and it is wrong" are
      different facts. Without that, PEP 1's digest check compares two copies of one claim.
      The station's description *and* bytes now come from the same place; taking one from each
      would make PEP 1 and PEP 2 agree without either checking what the other saw.
      **Finding 51**, found by asking whether the description a Depot serves conforms to the
      contracts on its own: it did not, because `fdt-p:underNetwork` was `sh:class
      fdt-net:Network`, so publishing a conforming train offer required the train's owner to
      republish who the network trusts. Also **the Handler was emitting non-deterministic
      descriptors** — rule order followed rdflib's blank node labels, so the same plan produced
      different documents about two runs in five. And `fdt-commons`' OpenAPI documents were
      validated by nothing at all; `make check` has a tenth pass now.
      12 mutations on the Depot, 11 caught, 1 equivalent (noted in `holdings.py`).
      JWKS is published because ADR-029 makes the Depot the authority for the owner's keys; no
      counter-signing is implemented anywhere, because **ADR-028 is still Proposed**.
- [ ] **WP-5.0 — FDT-O v4 and the contracts ADR-030/033 need** · 5.1 · M
      Additive. `fdt-o:DatasetPart` with its own IRI, controller and offers (**ADR-033**, Q11);
      the train families `QueryTrain`, `APITrain`, `ScriptTrain`, `ContainerTrain` marked
      `dash:abstract` and dropped from `:TrainShape`'s list (Q18); the input-requirement
      structure made normative and given station-side counterparts — a hosted dataset declares
      what it `dct:conformsTo`, and `fdt-run:targetQuery` is replaced by a data requirement plus
      separately-stated non-data constraints (**ADR-030**). *Acceptance: `make check` green;
      every shape that targets an offer accepts a part as a target; a counter-example for each
      new rule.*
- [ ] **WP-5.3 — Metadata registry v0 (`FDTRegistry`)** · 5.0, 5.2 · L
      Harvests and indexes what Depots and Stations publish, FDP-Index-shaped. **Not a trust
      anchor** — membership is proven by a credential, not by an index entry. Shows harvest time
      rather than implying currency. Its query surface is **ADR-030**: index the shapes stations
      publish, answer a train's data requirement by **structural coverage**, and say which
      required property a station was missing. *Acceptance: a Handler resolves a plan's stations
      and trains from the registry instead of the fixture catalogue, and a station that nearly
      matches is excluded with the missing property named.*
- [ ] **WP-5.4 — Several stations, configured and running** · 1.4 · M
      More than one station with real data sources, in at least two networks — and the two
      networks differ in **whether automated authorisation is permitted** (ADR-032), so both
      regimes are exercised rather than described. *Acceptance: the same train visits two
      stations and gets different agreements; the same commercial request is refused
      automatically in one network and produces a recommendation awaiting a human in the other.*
- [ ] **WP-5.5 — Consoles for the testbed** · 2.7, 5.2, 5.3 · L
      Each component's UI has its own job; they are not one observability layer.
      **Depot:** publish and withdraw trains — upload a payload, declare parameters, the input
      requirement and the declared output, set the owner's offer, and see the digest the Depot
      computed; and, first on the page, **what it withholds and why**.
      **Registry:** harvest status and freshness per source; search by facet and by a train's
      data requirement, showing why each station matched or did not.
      **Station:** live visits with every checkpoint decision and justification; the controller's
      queue — approve, refuse, revoke — with the recommendation and evidence attached (ADR-032);
      the catalogue and its offers, including parts; configuration and the published
      self-description.
      **Handler client:** connect to `FDTRegistry` instances, select and parametrise trains,
      choose an itinerary strategy, watch the run.
      The **Individual Gateway is not in M5** — it lands in M2 with the controller workflow it
      needs (WP-2.4). *Acceptance: the M1 scenario watched end to end in a browser — the
      itinerary, the checkpoints, the justifications, the envelope — and a train published to the
      Depot and found through the registry by its data requirement.*

Nothing in M5 is blocked on a decision. Q16 is answered by **ADR-030**, which replaced
`fdt-run:targetQuery` rather than giving it a grammar: a train declares the data it needs and
that is what selects a station.

## M2 — Fan-out and governance

Exit: the fan-out plan across three stations (push and poll); one approval in the Gateway; the
commercial-purpose case shown **both ways** — refused automatically in a network that permits
automated decisions, and referred to a human with the system's recommendation and evidence in a
network that does not (**ADR-032**); the run ends **Partially Delivered** with a completeness
statement.

- [ ] **WP-2.1 — Conditions engine (ADR-025)** · 1.5 · S
      *Acceptance: every case in `conditions.cases.json` yields its expected value.* The only
      M2 criterion that was runnable as written; the 10 cases are evaluated on every
      `make check`. `PhaseResults` scope has no schema and no case.
- [ ] **WP-2.2 — Failure policy and completeness (ADR-026)** · 2.1 · M
      Needs a P3 Sequence plan fixture. The refusal at the ambulance service is now derivable:
      `consumerType` arrives as a verifiable credential (**ADR-031**), so the mismatch is an
      evidenced fact rather than an unverifiable claim. ADR-026 also needs a term for an adverse
      **recommendation** that is not yet a decision (ADR-032) — neither Refused nor Rejected,
      because no controller has decided anything.
- [ ] **WP-2.3 — Poll dispatch (Handler API)** · 1.5 · M
      Contract complete; inherits the M2 scenario's fixture gaps.
- [ ] **WP-2.4 — Manual approval, controller API, Individual Gateway v0** · 1.3 · XL
      The controller API **still has no contract anywhere** (sweep I) and **ADR-032** now sets
      what it must carry: the recommendation, the evidence behind it, the decision, and the four
      things the agreement records — the mode and the rule that imposed it, who decided and under
      what authority, what they were shown, and whether they followed or departed from the
      recommendation. Write the contract in `fdt-commons` first.
      The **Individual Gateway** is the component that shows what FDT is for, and it is larger
      than "approve things": ask each station whether it holds data under my control — an
      authenticated ask, answered only for a verified identity and itself logged as an access
      event (**ADR-031**); define the access conditions for my data; see who accessed it, when
      and for what; receive and decide consent requests. The station-side "do you hold data I
      control" endpoint is a new protocol capability and needs its own contract and its own
      counter-examples — it is a probe about a named individual and must not become one.
      `fdt-o:DatasetPart` (**ADR-033**) is what lets a person be the controller of part of
      somebody else's dataset, which is the case that makes a Gateway necessary at all.
- [ ] **WP-2.5 — Metadata: FDP endpoints and DSP-conformant catalogue** · 0.4, 5.0 · M
      Fixture catalogue conforms. `dcat:theme` exists on trains and on the M1 dataset only; the
      registry needs it more widely. Each hosted dataset must now also declare what it
      `dct:conformsTo` (**ADR-030**), and the catalogue must be able to list `fdt-o:DatasetPart`
      alongside datasets (**ADR-033**).
- [ ] **WP-2.6 — SQL, API/FHIR and Docker adapters** · 1.4 · L
      The payload is now a real OCI image layout with true digests, so "an image with a wrong
      digest never starts" is testable. Still needs a synthetic dataset per adapter — and, under
      **ADR-030**, an **RML mapping** per non-RDF source, from which the station's published
      shape is generated. That is what makes a SQL or FHIR station selectable by a train's data
      requirement at all.
- [ ] **WP-2.7 — Consoles: Station S1–S6, Handler H1–H4, Gateway G1/G2/G4** · 2.1–2.5 · L
      **Rescoped (decided 13 Sep 2026).** The criterion named 31 state labels and 11 cannot arise
      in M2 (sweep J); it is now the states the scenario actually produces, with the remaining 11
      listed explicitly as owed to the milestone that produces them — deferred, not dropped. Fix
      the mock-up copy that writes "rejected at matching" for what ADR-026 calls Refused (sweep
      K), and add the label ADR-032 needs for an adverse recommendation awaiting a human.

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
| **Q1** | publish the contracts at their `w3id.org` IRIs | WP-0.2, WP-4.4 |
| **Q6** | repository visibility | WP-4.4 |
| **Q2, Q3, Q7, Q8** | DSP namespace, demo IdPs, the Java prototypes, the old token | nothing in M2 or M5 |

**Answered 13 September 2026** in the M5 decision interview, and now ADRs: **Q16** (station
selection — ADR-030), **Q14-C** (credentials — ADR-031), **Q13.2/13.3** (human decisions —
ADR-032), **Q11** (dataset parts — ADR-033), **ADR-028** accepted, **Q15** (a zero cell passes),
**Q18** (the train families are abstract too), **Q17** (rename both repositories; the registry
becomes `FDTRegistry`), **Q5** (push v3 onto PR #1's branch). Nothing in M2 or M5 is blocked on
a decision any more.

## Dependency graph

```
0.1 → 0.3 → 0.4 → 1.1 → 1.2 → 1.3 → 1.4 ┐
0.2                            1.1 → 1.5 ┼→ 2.1 → 2.2 → 3.1 → 3.2 → 4.1
                               1.5 → 2.3 │   1.3 → 2.4 ──────┘  1.4 → 3.3
                               0.4 → 2.5 ┼→ 3.4 → 4.2          2.7 → 3.5
                               1.4 → 2.6 ┘   all → 4.3 → 4.4
```

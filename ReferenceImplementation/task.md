# Roadmap and progress

The 25 work packages of `fdt-implementation-plan.md` §4–§5, tracked here. Each box is checked
only when its **acceptance criterion has been run**, not when the code looks finished.

The plan remains the normative source for what each criterion says; where the criterion itself
is wrong — it names a fixture that does not exist, or a decision has since overtaken it — that
is noted under the package and carries the id of the sweep item or question that settles it
(`docs/reviews/2026-09-12-acceptance-criteria-sweep.md`, [`OPEN-QUESTIONS.md`](OPEN-QUESTIONS.md)).

**Next:** **WP-5.5's last surface — the Depot's publish and withdraw — and then M5's browser acceptance.** Eleven screens now exist: station S1, S2, S3, S6, S7, S8 and the public page S9; Handler H1, H2, H3 and H4; plus the Depot and registry read consoles. What is left all writes or reads a controller's own policy *as that controller* — the Depot's writes, station S4 and S5, and H2's dispatch step — and the console has no controller identity to do it as: **Q21 now blocks four things**, and is the one decision standing between here and M5 closing. WP-5.0 through WP-5.4 are done — FDT-O is at 4.0.0, a train declares the data it needs, a Depot is the authority for it, a registry answers which stations hold it and names the property the others were missing, and two stations in two networks now show the difference between a decision a machine may take and one it may not. The decision interview of 13 September 2026 closed every question that blocked M2 and M5: **ADR-030** — a train declares the data it needs as a SHACL model, non-RDF stations map with RML and publish a generated shape, and matching is structural coverage; **ADR-031** — a credential proves what a train's metadata only names; **ADR-032** — where a machine may not grant it may not refuse either, and must instead present its recommendation and evidence to a person; **ADR-033** — `fdt-o:DatasetPart`; and **ADR-028** accepted. Contracts move first, as always.

| | | |
|---|---|---|
| **M0** Foundations | ✅ done | 12 Sep 2026 |
| **M1** One visit | ✅ done | 12 Sep 2026 |
| **M5** Testbed (new — ADR-029) | 🟨 in progress — WP-5.0–5.4 done; WP-5.5 at 11 of 13 screens, blocked on Q21 | |
| **M2** Fan-out and governance | 🟨 in progress — WP-2.4's controller API done | |
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
- [x] **Q14-C — the auto-approving offer and the commercial request.** Q9 and finding 20.
      **Done 13 Sep 2026** (`fdt-commons` 0.21.0): `ex:request/gd-commercial-2026` and its
      twin under the other network, from `ex:party/healthai-like`. It fails two ways on
      purpose, because the two are different in kind and a refusal has to name the right one —
      a purpose CONSTRAINT the offer does not cover, which a different request could satisfy
      tomorrow, and `odrl:sell`, which every one of these offers PROHIBITS and no approver may
      waive. WP-1.3's second clause runs. The other half of Q14-C — where `consumerType` comes
      from — is **ADR-031**, and is credentials rather than a fixture.

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
- [x] **WP-5.0 — FDT-O v4 and the contracts ADR-030/033 need** · 5.1 · M — **done 13 Sep
      2026.** FDT-O 4.0.0, `fdt-commons` 0.19.0. Every clause of the criterion ran: `make check`
      is green over twelve passes, both station-catalogue shapes accept a part where they
      accepted only a whole, and each new rule has a counter-example that fails on the rule's
      own words — eleven in FDT-O, fifteen here.
      **`fdt-o:DatasetPart`** (ADR-033) with its own IRI, controller and offers, and
      **`fdt-o:GovernedData`** as the common superclass of the whole and the part, so that a
      rule about data an offer may target is written once. Writing it twice is how it goes
      wrong: a rule still saying `fdt-o:HostedDataset` stops applying to parts and reports
      "conforms" over data nobody checked. The fixture is the case the alternatives could not
      express — the 90-day patient-reported answers inside a hospital's registry, controlled by
      the patient participation council and not by the hospital.
      **A train declares the data it needs** (ADR-030), as a SHACL model, and that is what
      selects a station. `fdt-run:targetQuery` is gone with no alias; `fdt-run:StationSelector`
      states the data requirement (required) and the non-data constraints (optional) separately,
      because "no station holds your data" and "no station in this network may process in the
      EU" are different answers a completeness statement has to keep apart. `tools/coverage.py`
      is the normative implementation of structural coverage and pass 12 runs it over the whole
      matrix: fourteen pairs, four hits, ten misses in three kinds, each recorded in
      `tests/coverage-expectations.json` — because a matcher that only ever answers yes is a
      check that cannot fail, and one that only ever answers no passes just as quietly.
      **The four train families are abstract** (Q18). The three consumers that had hard-coded
      "every subclass of Train except Train itself" now read `dash:abstract` from the ontology,
      each guarded so that missing markers stop the component rather than silently widening what
      it accepts.
      **Finding 53**: FDT-O has said since v2 that every train declares a requirement, and no
      train did — an OWL restriction licenses an inference and never fails, and no shape checked
      it. **Finding 52**: `fdts:StationPolicyShape` had validated nothing since v0.1 and
      finding 21 had said so eight versions earlier; a note does not fail a build. What closed
      it is the new **pass 11**, which counts the focus nodes every shape selects — and which
      checks its own detector against a shape built to come out dead, so "0 dead" cannot itself
      be vacuous. 20 mutations, 0 survivors, against a green control run.
- [x] **WP-5.3 — Metadata registry v0 (`FDTRegistry`)** · 5.0, 5.2 · L — **done 13 Sep 2026.**
      `fdt-registry` 0.1.0, `fdt-commons` 0.20.0. Both clauses of the criterion run in
      `make e2e` with four real components and no fakes: a Handler resolves the target set from
      the registry, takes the dispatch endpoint the chosen station published, and runs the visit
      through to a delivered envelope; the near-miss station is excluded and the reason names
      `subjectCount`.
      **Trains still come from their Depot.** The registry indexes them too and answering from
      it would have been one line — the line that puts a harvester on the path of the digest a
      station agrees to run. Discovery is a hint, a train's identity is an authority question,
      and ADR-029 keeps them apart; `RegistryCatalogue` wraps `DepotCatalogue` rather than
      replacing it.
      **The coverage relation is not reimplemented.** The registry loads
      `fdt-commons/tools/coverage.py` — the module `make check` runs over the fixture corpus —
      the way the station loads `tools/inspection.py`. Two implementations of one definition
      would make the contracts repository's copy a second opinion, and structural coverage has
      exactly the edge cases where two opinions differ quietly.
      **Three things are contract, not convention**, because each fails silently: the registry
      declares `trustAnchor: false` in its own self-description; every row and every answer
      carries when its source was last harvested and whether that attempt succeeded; and a
      source that cannot be reached keeps its row with the error on it, because "the station is
      down" and "the station does not exist" are different problems and dropping the row turns
      the first into the second. A search with no data requirement is refused rather than
      answered — it is `fdt-run:targetQuery` in new clothes, resolving to every station that
      could be *visited*.
      **Two defects surfaced, both from making a consumer use what a publisher published.** The
      Depot served a train's input requirement and not the shapes it names, so a registry could
      not resolve them and the train would have matched every station rather than none
      (`GET /trains/{train}/input-shapes`). And **the station published a dispatch endpoint it
      did not serve**: `base_url + "/fdt/v1"` while the router was mounted at the root, so its
      own minted visit IRIs and its advertised address disagreed. Nothing had caught it because
      every consumer was handed the URL out of band — the Handler's fixtures carry an
      `endpoints` override. The first Handler to take the endpoint from the registry pushed a
      visit to it and got a 404 from the station's own advertised address.
      Along the way the station gained `GET /catalogue` and `GET /shapes` (a WP-2.5 down
      payment): what it holds, on whose terms, with parts, and the shapes its data conforms to —
      conforming to the contracts **standalone**, which is how a registry receives it. The first
      draft of the catalogue published every policy that pointed at a dataset, which is other
      consumers' requests and the evidence they submitted; the standalone conformance check
      found it.
- [x] **WP-5.4 — Several stations, configured and running** · 1.4 · M — **done 13 Sep 2026.**
      `fdt-commons` 0.21.0. Both clauses run in `make e2e`, with two real stations and no
      fakes: the same train at two stations comes away with two different agreements (k ≥ 5 and
      k ≥ 10, because conditions belong to controllers and not to trains), and the same
      commercial request is refused by a machine in `health-research-nl` and left waiting for a
      person in `stroke-oost`, carrying the station's recommendation and the evidence behind it.
      **ADR-032 in the contracts.** `fdt-net:permitsAutomatedDecision` sits on the **network**,
      beside its trusted issuers — not on the offer and not on a participant's own membership,
      because both are editable by the party the rule binds. One flag covers both directions:
      an automated refusal is an adverse decision taken by a machine about somebody's request,
      and reading the regime as "granting only" is the implementer's convenience rather than
      the regulator's meaning. Where it is false the station does the whole evaluation anyway
      and publishes what it concluded — withholding the analysis because the machine may not
      decide would leave the person with less basis, not more independence.
      An agreement now records **how it was reached** and, where a person decided, who they
      were, under what authority, **what they were shown** (`fdt-p:shownAtDecision`, pinned by
      digest), what was recommended and whether they followed it. **Findings 56 and 57** close
      findings 26 and 27, open for twelve versions: an agreement could not say whether a human
      was legally necessary or merely preferred, and nothing recorded what one was shown.
      Where both rules apply the mode names the **network**, because a controller who drops
      their own preference tomorrow must not thereby turn a legally-required decision into an
      automatic one.
      **Finding 57 was found by asking the question from the other side.**
      `fdt-p:requiresManualApproval` says it inserts the pending-approval state; the evaluator
      consulted it only on the branch where an eligibility fact could not be evidenced. So a
      controller who asked for a person got one exactly when the station was stuck, and was
      silently ignored whenever the machine was able to decide — the case they were most likely
      asking about. It survived because no fixture both required approval and matched cleanly:
      the defect lived in the gap between two fixtures.
      **Q14-C's commercial request exists at last** — named by WP-1.3's acceptance criterion
      since the plan was written, absent until now. It fails two ways on purpose, a purpose
      constraint and a prohibition, because those are different in kind and a refusal has to
      name the right one. **Q19** records the reading taken for a network that states no regime:
      silence bars automated decisions, because the two errors are not symmetric.
      13 mutations, 0 survivors, against a green control. `make e2e` 15 passed.
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
      self-description — including the **decision-mode selector** (automated / semi-automated /
      manual, ADR-034), which shows the *effective* mode per network rather than the operator's
      selection, marks a network whose regime was assumed rather than published, and records
      every change with a reason into an append-only history.
      *(**Built:** station **S1 Dashboard**, **S2 Jobs**, **S3 Approvals** (in WP-2.4),
      **S6 Datasets**, **S7 Audit explorer**, **S8 Settings** and **S9 public catalogue** — S9
      as its own bundle, because an anonymous visitor should not be served the operator's
      console with one route rendered differently; Handler **H1 Trains**, **H2 New plan**,
      **H3 Run monitor** and **H4 Replay**; and read consoles for the **Depot** and the
      **registry**. Three contract surfaces had to be built first, because none existed: the
      station's operator API, `handler-api.yaml` (the Handler had no HTTP server at all), and
      `controller-api.yaml`. Building them found findings 60, 61, 62, 63, 65 and 66.

      Three screens read what a station **publishes as RDF** — `GET /`, `/catalogue`, `/shapes`
      — because there is no JSON projection of them and there should not be: a second
      representation is a second thing to keep true, and the one the console read would be the
      one nobody else did. `src/rdf/` parses the published Turtle and renders an `odrl:Offer` as
      the design system's controlled sentence, with every label generated from the vocabularies
      (`tools/vocabulary.mjs`) so a console cannot call `fdt-p:carryOnward` "deliver result".
      That found **finding 64 / Q22**: 49 FDT-O terms carry no `rdfs:label`, among them every
      interaction mechanism a station publishes.

      **Still to build: the Depot's publish/withdraw surface**, station **S4** (the condition
      builder) and **S5** (agreement detail). All three write or read a controller's own policy
      *as that controller*, and the console has no controller identity to do it as — **Q21**.
      H2 stops on the same line for the same reason: it composes a `fdt-run:Plan` and hands it
      over, because starting a run means dispatching a train on somebody's behalf and nothing
      yet says who may do that for whom. The Handler's own CLI already declines to grow a "run
      this" endpoint on that reasoning, and adding one from a console would be taking the
      decision in a worse place.

      **The acceptance run has not been done in a browser**, and its second half — a train
      published to the Depot and found through the registry — needs those Depot writes. Its
      first half is covered from both ends by `tests/e2e/test_consoles.py` (15 tests), which
      caught a bug shipped in the registry console the session before: finding 66.)*
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
      *(Controller API **done** — `controller-api.yaml` in fdt-commons 0.24.0, the station's
      queue and decision, and console **S3 Approvals**. The queue is scoped to the
      authenticated controller and another's case answers as one that does not exist; what the
      person was shown is pinned and a decision on a case that has since changed is refused;
      a controller may supply evidence and may not waive a prohibition, and a grant the offer
      still does not cover ends Refused rather than being forced through. Findings 62 and 63.
      **Still to do: the Individual Gateway**, and the station-side "do you hold data I
      control" probe, which is the part that needs its own contract and its own
      counter-examples — it is a question about a named individual and must not become a probe.
      The identity model behind all of it is still Q21's placeholder.)*
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

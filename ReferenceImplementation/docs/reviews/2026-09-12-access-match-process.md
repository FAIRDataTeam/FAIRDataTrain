# Review — matching an access request against access conditions, and recording the agreement

| | |
|---|---|
| **Scope** | The five-step process stated by the system owner on 12 Sep 2026 (arrival → policies → checks → immutable ODRL agreement → automatic / semi-automated authorisation), judged against the contracts as they are in this sandbox: `fdt-commons` v0.6.0, `FDT-O` v2.0.0 (`fdt-o-v2`), `docs/station-checkpoints.md`, `OPEN-QUESTIONS.md`, the Java PoC. |
| **Method** | Everything below was checked against the files, not the descriptions of the files. `make check` was run (green: 3 valid Turtle files, 8 counter-examples, 1 JSON-LD round-trip, 14 protocol/condition fixtures, 42/42 ontology terms). Where I claim a shape or schema *accepts* something it should not, I constructed the instance and validated it with pySHACL 0.40.1 / rdflib 7.6.0 / jsonschema 4.x. The probe scripts are in `probes/` at the sandbox root and rerun with `.venv/bin/python probes/<name>.py`. The ADRs are not in the sandbox; where I cite one I cite it as quoted by a file that is. |
| **Verdict in one paragraph** | The checkpoint **order** is right and the **matching model** — controller's offer × requester's request under the station owner's policy, producing a per-visit ODRL agreement — is the right model. As stated, the process is **not yet sound** in three places: (1) in automatic mode it treats the requester's self-assertions (legal basis, purpose, consumer type) as established facts and has no notion of which facts need an external source; (2) it binds the agreement to the dataset and the parties but not to the **executable**, and the agreement-reuse path then verifies only target and assignee, so what a human approved is not what PEP 2 enforces; (3) the human path has no decision model — nothing records who decided, on what basis, whether they contradicted the system, or *why* a human was involved, and the channel that carries the decision has no contract at all. The agreement as `AgreementShape` defines it is **not** the durable, auditable record the process claims: findings 23–25 are correct and necessary, but they are not sufficient, because the shape constrains the agreement's *form* and nothing constrains its *content relative to the offer it names* — I show below that an agreement granting an action the offer never offered, at record level, on a different dataset, to a different party, validates cleanly. |

The rest of this document is the evidence, then the classification the brief asked for: **(a)** the process is wrong, **(b)** the process is right and the contracts do not express it, **(c)** the process is right, expressed, and merely unimplemented.

---

## 1. What I executed, and what it showed

| Check | Result |
|---|---|
| `make check` | green, as recorded in `README.md:93`. |
| `probes/agreement_probes.py` — seven synthetic policies added to the valid fixture set, validated against `shapes/*.ttl` + vocab + ontology | **A** empty agreement (no permission, prohibition or duty) — *conforms*. **B** agreement granting `fdt-p:executeContainer` and `onwardStateClass eq fdt-p:RecordLevel`, no k-anonymity duty, "derived from" `evt-registry-research` which offers neither — *conforms*. **C** agreement whose target, assigner and network all differ from the offer it names — *conforms*. **D** agreement without `odrl:profile`/`underNetwork` — violates (as it should). **E** agreement whose assignee differs from the request's assignee — *conforms*. **F** two `requiresManualApproval` values — violates (as it should). **G** request whose `fdt-p:train` is a dataset IRI — *conforms* (nodeKind only). |
| `probes/descriptor_request_probe.py` — the ODRL request embedded in `examples/protocol/visit-descriptor-ttg-hop1.json` parsed as JSON-LD and validated against `RequestShape` | **Violates** `RequestShape` (no `fdt-p:train`) and `PolicyCommonShape` (no `fdt-p:underNetwork`). It asks `executeContainer`; the Turtle request `ttg-2026q3`, the offer `evt-registry-research` and the agreement `agr-9a01` all say `runQuery`; the offer has no `executeContainer` permission at all. It also omits the `legalBasis` constraint the Turtle request carries and the offer requires. `visit-protocol.md:74` says this request is "validated by `RequestShape`"; `tests/validate_protocol.py` validates it as `{"type": "object"}` (`visit-descriptor.schema.json:54`) and never runs SHACL on it. |
| `probes/schema_probes.py` — decision events and envelopes with the decision content removed | `negotiation.refused` with no `reason` and no `justification` — **valid**. `negotiation.active` with no `agreement` and no `justification` — **valid**. `visit.delivered` with no `justification` — **valid**. A `visit.rejected` event carrying `state: Delivered` at `checkpoint: OBL` — **valid** (type, state and checkpoint are not cross-constrained). A `state: delivered` envelope with no `agreement`, no `inspection` block and `{"patient_id": …, "name": …, "dob": …}` in `result` — **valid**. A `state: refused` envelope with no `reason` — **valid**. |
| grep for instances of `fdt-p:StationPolicyDocument`, `fdt-p:consumerType`, any approver / decider / override term across `fdt-commons`, `FDT-O`, the Python components and the console | `StationPolicyDocument`: shape and vocab only, no instance (confirms finding 21). `consumerType`: one occurrence, the constraint on the offer at `examples/policies.ttl:27`; no request, descriptor field, token claim or membership property carries a value for it. No term anywhere for who approved, on what basis, or whether a suggestion was overridden. |

Three of the checks the process relies on therefore report success today for the reason this project has already been bitten by: **they have no subject to look at** — the station policy (finding 21), the embedded request (never validated), and the agreement's relation to its offer (no shape can see it).

---

## 2. The sequence: order, lateness, and checks without an input

### 2.1 What is right

The order `PEP 1 → NEG → PEP 2 → EXEC → PEP 3` (`visit-protocol.md:29-42`) is correct and I have no change to propose to it:

- Identity, descriptor shape and payload digest before any policy is read; negotiation before any data is touched ("a governance decision before any data is touched", `station-visit-api.yaml:72`); an existence-and-liveness check of the agreement immediately before execution; result inspection *after* the adapter returns and *before* the envelope is assembled, in the orchestrator, not the adapter. `docs/station-checkpoints.md:55-58` is right that the PoC's FHIR-only inspection (`FHIRTrainInteraction.java:117-119`, whose `validateResponse` is itself `// TODO: validate (?)` at line 154-156) shows why PEP 3 cannot live in the adapter.
- Separating **negotiation produces an agreement** from **PEP 2 checks one is active** (`docs/station-checkpoints.md:39-40`) is the correct reading of the PoC's single empty `checkAccess()` (`BasicAccessControlService.java:35-37`) and is what makes the agreement-reuse path (retries, P5 rounds) possible.
- Revocation stopping "at the next checkpoint" (`visit-protocol.md:70`) is sound because PEP 3 is a checkpoint: a revocation during EXEC prevents release, not just further computation.

### 2.2 Checks that are load-bearing without an input they could actually have

These are places where the process names a check that has nothing, in the contracts, to check *against*. This is the failure class of findings 12, 16, 20 and 21.

**(i) `consumerType` has no source.** The offer constrains it (`policies.ttl:27`, `isAnyOf (Academic NonProfit PublicBody)`), the event fixture asserts it was checked (`visit-events-ttg-hop1.json:46` "consumer type … permitted"), and `docs/station-checkpoints.md:63-65` says it "must come from" the token at PEP 1. No contract names the claim, the request template does not carry it (`policies.ttl:68-77`), the descriptor has no field for it (`visit-descriptor.schema.json:18-25`), and `fdt-net:Membership` (`vocab/fdt-network.ttl:18-19, 32-37`) has `credential` and `role` but no participant class. **A refusal on commercial purpose (M2, Q9) is the one path that exercises a prohibition end to end, and its deciding fact has no defined origin.** Classification: **(b)**, with an **(a)** component — the process must say *who vouches for* consumer type (network governance authority via membership, IdP claim, or self-assertion) because those have different evidential weight and the agreement must record which it was.

**(ii) `legalBasis` and `purpose` are self-asserted, and in automatic mode that self-assertion *is* the decision.** The request states its own legal basis and purpose (`policies.ttl:74-75`); the offer accepts a set (`policies.ttl:26, 29`). The match "request says X, offer admits X" is a check that the requester *claimed* something admissible, not that it is true. This is normal ODRL, and for a non-profit consortium's research purpose it may be exactly the intended trust model — but the process as stated does not distinguish facts the station can verify (token issuer, payload digest, network membership, an `fdt-p:externalPermit` it can dereference) from facts it can only *record as asserted*. In automatic mode this is the whole of the eligibility decision. Classification: **(a)** — the process needs the distinction; **(b)** — the agreement's evidence block (finding 24) must label each fact `asserted-by-assignee` / `verified-against <source>`; and it bears directly on §4: a regulator who forbids automated decisions is usually forbidding exactly "grant on self-assertion".

**(iii) In poll mode, the "who submitted this train" check has no token.** PEP 1's identity check is "a bearer token against the trusted issuers of the network" (`docs/station-checkpoints.md:62-65`; `visit-protocol.md:97`). In push mode the Handler presents one. In poll mode the *station* authenticates to the Handler with its operator's client credentials (`handler-callback-api.yaml:12-14`) and pulls descriptors; `consumer.agent` is "as asserted by the bearer token" (`visit-descriptor.schema.json:22`) but no consumer token accompanies a pulled descriptor. The station is therefore trusting the Handler's assertion of `consumer.party` and `consumer.agent`, transitively, and the contracts do not say so. Nothing binds the token subject (a person, `r.bakker@…`) to the legal party it acts for (`stroke-network-oost-qi`) in either mode. Classification: **(b)** — and it must be settled before the agreement's evidence block can say what identity evidence it holds.

**(iv) The station policy — one of the three named inputs — has no instance and its shape has never fired.** Finding 21 is correct; I re-confirmed it (grep above). Until a `StationPolicyDocument` fixture exists, NEG is `offer × request × ∅`. Classification: **(b)**.

**(v) The train provider's offer exists in the contracts and is matched by nothing.** `TrainOfferShape` *requires* every train to carry `odrl:hasPolicy` an `odrl:Offer` "from its provider (licence, permitted purposes/stations)" (`train-offer.shapes.ttl:26-27`), and the fixture `offer/train-time-to-groin` constrains `fdt-p:network eq stroke-oost` (`trains-and-plans.ttl:66-70`). The process, `visit-protocol.md:56` and `docs/station-checkpoints.md:36` all describe negotiation as three inputs. A fourth policy is *mandatory in the catalogue and absent from the decision*. Either the provider's licence is evaluated at NEG (and the agreement records it — a train licensed for `health-research-nl` only, run under `stroke-oost`, is a licence breach the station would be enabling) or the shape's `minCount 1` is decoration. Classification: **(a)** — decide; then **(b)**.

**(vi) The agreement-reuse path verifies the wrong things.** `visit-protocol.md:56`: "With an agreement IRI (rounds of P5, retries), the station verifies the agreement is active and its target and assignee match." Not the train, not the payload digest, not the network, not the action. Because the agreement does not name the train (finding 23) it *cannot* verify them. PEP 1 verifies the arriving digest against the Garage offer *as the Garage publishes it today* (`visit-protocol.md:74`). So: a controller approves `time-to-groin 0.4` by hand at 10:12; the Garage publishes 0.5 with a new digest; the Handler retries or starts round 2 with `negotiation.agreement = agr-9a01` and the 0.5 digest; PEP 1 passes (digest matches the Garage), PEP 2 passes (target and assignee match), and a different executable runs against patient data under a human's approval of a different one. Classification: **(a)** as written, **(b)** for the shape.

### 2.3 Checked too late

- **Static computation requirements.** `docs/station-checkpoints.md:77` places "declared requirements against capacity and sandbox posture" at PEP 2 — after negotiation, so after a human may have spent a day approving (`approvalWait P2D`, `visit-descriptor-ttg-hop1.json:87`). Dynamic capacity (quota, concurrent jobs) belongs at PEP 2; *static* requirements (mechanism enabled — already at PEP 1 —, sandbox posture, `fdt-o:hasRequirement`, memory/GPU class) should be refused at PEP 1 so a person is never asked to approve a train the station cannot run. Minor; **(a)**.
- **The descriptor's embedded request is validated nowhere.** See §1: it fails `RequestShape` and asks an action the offer does not grant. As a fixture it means the event stream's `negotiation.matched` (`visit-events-ttg-hop1.json:43-56`) is not derivable from the descriptor, the offer and the request in this repository — the same defect class as finding 19, one layer down. As a *process* matter it means PEP 1's "the ODRL request against `RequestShape`" (`docs/station-checkpoints.md:74`) has no executed check anywhere in `tests/`. Classification: fixture defect plus **(b)**.

---

## 3. Is the agreement a durable, auditable record?

### 3.1 Findings 23–25 and Q12: right, and what they miss

**Finding 23 (no train on the agreement) — correct, and understated.** It is not only that the audit chain is broken; §2.2(vi) shows it is *exploitable* on the reuse path. I agree with the proposed fix (first-class `fdt-p:train` + payload digest on the Agreement) and add: PEP 2 must compare the arriving digest against the *agreement's* digest, not only the Garage's; and probe G shows `fdt-p:train` on a request accepts any IRI — it needs `sh:class fdt-o:Train`. The declaration `fdt-p:train a odrl:LeftOperand` (`fdt-profile.ttl:41`) while shapes use it as a property is finding 17's defect again; agree.

**Finding 24 (granted terms versus evidence) — correct as a distinction of kind; two caveats.**

1. It does not, on its own, make `agr-9a01` derivable. The agreement drops `legalBasis` (eligibility — explained), but also drops the offer's `dateTime lt 2027-12-31` (`policies.ttl:28`) and `consumerType`. `dateTime` is a *usage* constraint by finding 24's own definition (PEP 2 must re-check it on every job), so under the split it must survive into the agreement and does not. The fixture is still inconsistent after the split; say so when the derivation rule is written.
2. "Settled once at negotiation" is right for facts like network and train, but some eligibility facts have their own validity — an `fdt-p:externalPermit` (EHDS data permit) expires; a membership has `dct:valid` (`station-catalog.shapes.ttl:87`). Evidence entries need an optional `validUntil`, and PEP 2 must check the *date* (cheap, deterministic) without re-evaluating the *fact*. Otherwise the split converts a lapsed permit into silent continued access, which is the opposite of what the finding wants.

**Finding 25 (pin the offer and request) — correct.** Add the station policy and the provider's offer (§2.2 v) to the list of things pinned, and note the reciprocal problem: the *agreement itself* is referred to by bare IRI in every event (`visit-events-ttg-hop1.json:89`) and envelope (`visit-result-ttg-hop1.json:10`). Events need `agreementDigest` too, or the event stream cannot tell which version of an agreement it was acting under.

**Q12 "immutability against whom" — correctly identified as open; the default is not enough.** "Digests plus the station retaining the documents" (`OPEN-QUESTIONS.md:208-209`) makes the station custodian of the record of its own decisions, which is the threat Q12 then names. It does not need a new ADR to improve: the Handler already receives `negotiation.active` with the agreement IRI (`visit-events-ttg-hop1.json:86-93`) and `GET /agreements/{id}` exists for parties (`station-visit-api.yaml:173-188`). Require the Handler to fetch and retain the agreement plus the pinned offer/request at `negotiation.active`, and put the agreement's digest in that event. Two independent custodians holding the same digest is tamper-evidence; counter-signature is the stronger version and can come later. This is a protocol-level MUST, i.e. **(b)**, not an ADR.

### 3.2 What the findings miss

**M1. Nothing constrains an agreement's content relative to the offer it claims to derive from.** Probes B, C, E (§1). `AgreementShape` (`policy.shapes.ttl:71-86`) requires target, assigner, assignee, timestamp, `derivedFromOffer`, `derivedFromRequest` — all *form*. It has no `odrl:permission minCount` (probe A: an empty agreement conforms; contrast `OfferShape` line 55-56). SHACL Core cannot express "every permission's action ∈ the offer's actions and every constraint is at least as strict" cheaply, and it should not try: that is the **derivation rule**, which is the missing contract. Without it, and without pinning, no party and no auditor can recompute what the agreement *should* have said. This is the gap that turns "immutable" from a property into a slogan: an immutable record of the wrong content is worse than a mutable one, because it looks settled. Classification: **(a)** — the process must state the derivation rule (offer ∩ request, duties from the offer carried whole, narrowing allowed only via the DSP `OFFERED` path in `state-machines.md:12`); **(b)** — `fdt-commons` needs the rule as a spec, a reference evaluator and fixtures for it, and an "agreement ⊆ offer" check that the Gateway and the Handler run on receipt.

**M2. The agreement does not record the decision.** Not the mode (automatic or human), the decider, the time of the decision as distinct from `dspace:timestamp`, the basis shown, the system's suggestion, or whether the human contradicted it. The only trace in the fixture set is free text: `"Approved by the controller; agreement agr-9a01 active until 2026-12-31"` (`visit-events-ttg-hop1.json:90`) on an event with no `justification`, which the schema permits (§1). §4 says what must be there.

**M3. The approval decision has no contract.** `station-visit-api.yaml:180`: "Revocation, approval and suspension are controller actions performed through the station console or the Individual Gateway, not through this API." The Gateway's approvals package is a docstring (`IndividualGateway/src/fdt_gateway/approvals/__init__.py`). There is no OpenAPI path, JSON Schema or SHACL shape for a decision message anywhere in `fdt-commons`. The write that turns a pending request into access to patient data is the one write in the system with no shape, no fixture and no counter-example. Classification: **(b)**, severe.

**M4. The agreement never expires.** `agr-9a01` (`policies.ttl:80-96`) has no `dateTime` constraint; the offer says `lt 2027-12-31T23:59:59Z` (`policies.ttl:28`); the event says "active until 2026-12-31" (`visit-events-ttg-hop1.json:90`); `state-machines.md:17` says "expiry is a property of the ODRL agreement (dateTime constraint)". Three answers, and the agreement as written is the one that never lapses. Fixture defect plus **(b)**: `AgreementShape` should require a validity bound (or the derivation rule must carry the offer's).

**M5. "Accessible by the station and the train owner" names an agent the model does not have.** FDT-O defines `TrainOwner` as "who *sent* a Train … the Train is visiting on behalf of the Train Owner" (`fdt-o.ttl:104-105`) — i.e. the consumer, the `odrl:assignee`. The fixtures type the *Garage provider* as `TrainOwner` (`trains-and-plans.ttl:25, 50`: "Stroke Network Garage (fictional provider)"), contradicting the ontology's own definition, while FDT-O has a separate `TrainProvider` — "who *created* the Train" (`fdt-o.ttl:111-113`) — which is what the fixtures' Garage parties actually are. The Station API grants agreement access to "a party" (`station-visit-api.yaml:179, 187`), i.e. assigner and assignee. The descriptor has a third agent, `consumer.agent`, the token subject. Decide which of {assignee party, acting agent, Garage provider} "train owner" means, fix the fixtures to FDT-O's definition or FDT-O to the fixtures, and record the acting agent and issuer on the agreement as evidence. Classification: **(a)** terminology, then **(b)**.

**M6. Decision events and envelopes do not have to say anything.** `visit-protocol.md:89`: "Every decision event carries a `justification`". `visit-event.schema.json:7` requires `id, visit, sequence, time, type, state` and nothing else; `reason` is optional even for `negotiation.refused`; type/state/checkpoint are independent enums. The RDF `VisitShape` does enforce reason-on-refusal (`run.shapes.ttl:165`) — but that is the Handler's run record, not the station's stream. The result envelope requires neither `agreement` nor `inspection` on a delivered visit (`visit-result.schema.json:7-15`), and `result` is an open object — a station can emit a fully conformant stream and envelope that record no decision and carry record-level fields. ADR-027 as quoted ("every station decision is an event with a justification", `README.md:51`) is a **(b)**: the schemas do not express it. Conditional `required` per `type` (JSON Schema `if/then`) fixes the events; `inspection` and `agreement` required when `state == delivered` fixes the envelope.

---

## 4. Authorisation modes

### 4.1 "Automatic versus semi-automated" is not the right cut

It conflates at least five independent questions, and the contracts already contain evidence for most of them:

| Dimension | Values the system already needs | Where the contracts touch it today |
|---|---|---|
| **Who decides** | the machine · the controller (a person) · an external authority (a permit body) · several parties jointly (a linkage hop joins two controllers' data; a DPO co-signs) | `fdt-p:externalPermit` exists (`fdt-profile.ttl:56`) with no procedure; linkage stations have their own agreement (`visit-protocol.md:23`) but nothing says both source controllers must approve the join |
| **What the machine may do** | grant and refuse · **refuse only, never grant** · advise only | nothing — and "the machine may say no, only a person may say yes" is the most common regulatory pattern for this kind of data |
| **Why a person is involved** | controller's discretion (waivable by that controller) · legal requirement (not waivable by anyone at the station) · risk trigger computed per case (container train; `Pseudonym` onward class; first visit by this assignee; override of a prohibition) | `requiresManualApproval` (discretion only, see §4.3) |
| **When** | before activation · automatic grant with mandatory post-hoc review (sampled or total) | nothing; but "automatic with audit" is a legitimate mode and is what the S7 audit explorer is for |
| **Standing authorisation** | a new decision per visit · reuse of an earlier decision (retries, P5 rounds) | the agreement-IRI path (`visit-protocol.md:56`) — a mode in its own right, and the one that must *not* be available when the reason for the human was legal |

The state machine already has room for this: `pending-approval` (`visit-event.schema.json:20`) can stay the single waiting state. What changes is what the *offer, network rule and agreement* say about which of the above applied, and what gets recorded.

### 4.2 What must be recorded differently when a person decided

At minimum, on the agreement (as evidence, finding 24's block) and on the `negotiation.active` / `negotiation.refused` event:

1. **Effective decision mode** and **its source** — `Automatic`, `HumanDiscretionary` (offer flag), `HumanRequiredByRule` (network rulebook / station policy / dataset regime, with a citation), `ExternalPermit`. An auditor must be able to tell a discretionary approval from a mandatory one without reading the offer's history.
2. **Decider**: IRI of the person, the issuer that authenticated them, the party on whose behalf they acted (must equal `odrl:assigner` or a delegate the assigner has named), and the decision time (distinct from `dspace:timestamp`, which is the agreement's conclusion).
3. **What they were shown**: a digest of the case presented (request, offer, station policy, the match summary with each constraint's outcome, the pinned documents) — so a later reader can see what the decider saw, and can detect if the presentation was wrong. This is the "summary or suggestion showing how the request matches or fails to match" of the owner's step 5, and it must be *stored*, not only displayed.
4. **The system's suggestion**: `permit` / `deny` / `permit-with-duties` and the rule that produced it — the same `justification.decision` vocabulary already in `visit-event.schema.json:40`.
5. **The decision** and a **stated reason** — mandatory on approval as well as refusal. Today only refusal has a reason anywhere (`run.shapes.ttl:165`), and only on the Handler's record.
6. **Whether the decision contradicts the suggestion** — an explicit flag, not something an auditor has to infer by re-running the evaluator.
7. **Any narrowing the person applied** (added duty, shorter window) — the `OFFERED` path of `state-machines.md:12`; the agreement then differs from offer ∩ request *by design* and the derivation rule (§3.2 M1) must account for it.

### 4.3 When the person contradicts the system

- **Person refuses what the machine would permit.** Already `Refused` with a reason (`fdt-run.ttl:108`). Sound. Make the reason mandatory on the event schema (§3.2 M6) and record the suggestion it overrode.
- **Person approves what the machine would deny.** This is the highest-consequence event in the system and today it is indistinguishable from any other approval. It must: require a reason; record the failed constraints by name; produce an agreement that carries the override as evidence; **not** be reusable via the agreement-IRI path without a fresh decision; and be visible to the station owner as well as the controller (the station owner's policy may forbid overrides of certain rules — e.g. a controller may not override the network's `reidentify` prohibition or the owner's onward-state ceiling). Which rules a person *may* override is itself a policy question the process does not state: I would take the conservative default that prohibitions from a party other than the decider (station owner, network) are never overridable, and permissions' constraints are.
- **Person approves something the machine could not evaluate** (missing `consumerType` source, §2.2 i). Record it as `asserted, accepted by <decider>` — not as `verified`.

### 4.4 One boolean cannot carry both meanings

`fdt-p:requiresManualApproval` is `a owl:DatatypeProperty ; rdfs:domain odrl:Offer ; rdfs:range xsd:boolean` (`fdt-profile.ttl:53`), constrained to at most one value (`policy.shapes.ttl:57`), with the note "equivalently a duty with action `fdt-p:approve` assigned to the assigner" (`fdt-profile.ttl:54`). It is a good encoding of *"this controller wants to decide"* and a wrong one for *"the law does not permit a machine to decide"*, for four reasons:

1. **Wrong author.** The domain is the Offer — the controller's document. A legal prohibition on automated decision is not the controller's to switch off, and with this encoding they can, by editing one triple. It belongs to the network's rulebook (`fdt-net:rulebook`, `vocab/fdt-network.ttl:30`), the station owner's policy (the `StationPolicyDocument` that has no instance yet), or the dataset's legal regime — sources the controller cannot edit.
2. **Different override semantics.** A discretionary flag is waivable by its author: pre-approve this train for all P5 rounds, reuse the agreement on retry, delegate to a colleague. A legal requirement is per-decision, not waivable by pre-approval, and survives agreement reuse. The boolean has no place to say which.
3. **Different automation envelope.** Under a legal regime the machine may typically still *refuse* and still *advise*; it may not *grant*. The boolean cannot say "refuse-only", so an implementation either over-automates (grants) or under-automates (queues obvious refusals for a person, wasting the approval window).
4. **Wrong ODRL idiom.** A duty (`fdt-p:approve` on the assigner) is an obligation a party may or may not discharge; a legal requirement is a constraint on the *procedure* by which the agreement may come into force. Encoding it as a duty implies it can be "fulfilled" by anyone the assigner delegates to, and that an unfulfilled duty is a breach by the assigner rather than an invalid agreement.

**Proposal (contract change, so through `FINDINGS.md` and a version bump):** keep `requiresManualApproval` on the offer with its current meaning; add a network/station/dataset-level `fdt-p:automatedDecision` ∈ {`Permitted`, `RefuseOnly`, `NotPermitted`} with a mandatory `dct:source` citing the rule; define the **effective mode** as the most restrictive of all applicable sources; record the effective mode *and every source that contributed* on the agreement as evidence. Add a fixture per mode and a counter-example where an offer says `false` under a network that says `NotPermitted`, so the "most restrictive wins" rule is a tested contract and not a comment.

---

## 5. Where the process could produce a wrong or unauditable outcome — ranked by consequence

Ranked by what a failure would let someone **do** or **conceal**, not by how easy it is to fix.

| # | Failure | What it lets someone do or conceal | Class |
|---|---|---|---|
| 1 | **Record-level content leaves labelled as aggregate.** The process places PEP 3 correctly, but the envelope schema requires neither `inspection` nor `agreement` on a delivered visit and `result` is an open object (probe, §1). `docs/station-checkpoints.md:57` calls this "the main correctness risk in the system"; the contract does not gate it. | Exfiltrate patient records through a conformant envelope; conceal it because nothing in the record says inspection did not happen. | (b) |
| 2 | **A different executable runs under a human-approved agreement** (§2.2 vi + finding 23). | Get code a controller never saw against data a controller approved for other code; conceal it because the agreement, events and envelope all name the same agreement IRI. | (a)+(b) |
| 3 | **An agreement grants more than the offer, and nothing can tell** (§3.2 M1, probes B/C/E; station is the scribe, Q12). | A compromised, misconfigured or buggy station grants record-level onward state, or an action the controller never offered, and records it as agreed; conceal it because the record validates and is "immutable". | (a)+(b) |
| 4 | **The human decision is unrecorded and its channel uncontracted** (§3.2 M2–M3, §4). | An insider approves a request the evaluator would refuse; conceal it because approval needs no reason, no identity and no justification, and the decision message has no schema to be audited against. Also: an auditor cannot distinguish machine decisions from human ones at all. | (a) modes, (b) record |
| 5 | **Eligibility on self-assertion in automatic mode**, with `consumerType` sourceless (§2.2 i–ii). | A commercial party obtains automatic research access by asserting `Academic` and a legal basis; conceal it because the agreement records neither the claim nor its provenance. | (a)+(b) |
| 6 | **Poll-mode identity gap** (§2.2 iii). | A Handler asserts any `consumer.party`; the station's "verified identity" is a transitive trust it does not know it is extending. | (b) |
| 7 | **Agreement without expiry** (§3.2 M4). | Access continues past the offer's window; conceal it because the record says nothing is wrong. | fixture + (b) |
| 8 | **Decision events need not justify; type/state/checkpoint unlinked** (§3.2 M6). | Emit a valid stream that says nothing; a completeness statement built from it is hollow. | (b) |
| 9 | **The provider's licence is not matched** (§2.2 v). | Run a train where its provider forbade it; the station is the enabling party. | (a) then (b) |
| 10 | **Station policy has no subject** (finding 21). | The owner's rules do not exist in any tested form; a station "under policy" is under none. | (b) |
| 11 | **Descriptor request fixture inconsistent and unvalidated** (§2.3). | Not exploitable; it means M1's acceptance can pass on fixtures that do not describe one consistent visit. | fixture |
| 12 | **Refused/Rejected conflated in the DSP mapping** (finding 22). Agree entirely. | Misreport a controller's refusal as a data failure in a completeness statement. | (b) |

Items 1–4 are the ones that decide who may run code against patient data and what may leave a hospital. None of them is fixed by findings 23–25 alone.

---

## 6. Classification summary

**(a) The process is wrong or incomplete as stated**

- No distinction between verifiable facts and requester assertions; automatic mode grants on assertion (§2.2 ii).
- No derivation rule from offer × request × station policy to agreement; the station writes a contract between two other parties with no rule either can check (§3.2 M1).
- Agreement reuse verifies target and assignee only (§2.2 vi).
- Authorisation has two modes where it needs a mode model: decider, machine envelope, reason for human involvement, timing, standing authorisation (§4.1); no statement of what a person may override (§4.3).
- `requiresManualApproval` carries controller discretion only; legal non-automation needs its own, non-controller-editable, source (§4.4).
- Provider's licence is mandatory in the catalogue and absent from the decision (§2.2 v).
- Static computation requirements checked after a human has been asked (§2.3).
- "Train owner" names three different agents (§3.2 M5).

**(b) The process is right and the contracts do not express it**

- `AgreementShape`: no `fdt-p:train`/digest (23), no evidence block (24), no pinning digests (25), no permission minimum, no validity bound, no decision record, no `sh:class fdt-o:Train` on `fdt-p:train` (§3.1, §3.2).
- No contract for the approval decision message (M3); no agreement digest on events (§3.1); no source for `consumerType` (§2.2 i); no consumer identity in poll mode (§2.2 iii); no `StationPolicyDocument` instance (21).
- `visit-event.schema.json` does not require `justification`/`reason` per decision type and does not link type/state/checkpoint; `visit-result.schema.json` does not require `inspection`/`agreement` on delivery (M6, ranked #1 and #8).
- `tests/validate_protocol.py` never validates the embedded request with SHACL (§2.3).
- `state-machines.md` conflates Refused/Rejected (22).
- Fixtures: `agr-9a01` not derivable even under the eligibility/usage split (§3.1); embedded request inconsistent with the Turtle request and the offer (§1); no auto-approval offer (20); no commercial request (Q9); three different expiry statements (M4); `TrainOwner` used against FDT-O's definition (M5).

**(c) The process is right, the contracts express it, and it is merely unimplemented**

- The checkpoint order and the placement of PEP 3 in the orchestrator (`visit-protocol.md:29-42`, `docs/station-checkpoints.md:55-58`).
- The `requested → matched → pending-approval | active | refused` state machine and the `pending-approval` event with `approval.controller`/`expiresAt` (`visit-event.schema.json:20, 49-53`).
- Payload digest verification against the Garage at PEP 1 (`visit-protocol.md:74`, `TrainPayloadShape`).
- Per-network offer selection (`fdt-p:underNetwork`, `PolicyCommonShape` line 43-44) and trusted issuers per network (`NetworkShape` line 94, `network-and-stations.ttl:19,22,25`).
- Reason-on-refusal in the Handler's run record (`run.shapes.ttl:165`).
- Everything in `FAIRDataStation-py/src/fdt_station/policy/__init__.py` and `IndividualGateway/src/fdt_gateway/approvals/__init__.py`, which are docstrings.

---

## 7. Where I disagree with what is already recorded

- **Finding 19 → 24.** Finding 24 says the split "settles finding 19's question". It settles *why* `legalBasis` may be absent as a constraint; it does not make `agr-9a01` derivable, because the agreement also drops the offer's `dateTime` bound, which is a usage constraint under 24's own definition (§3.1). Both must be true before WP-1.3's "equal in structure to `agr-9a01`" can be an acceptance criterion.
- **Q12 item 2.** "The station retains the documents" is the custody problem, not its solution. The default should be two-party retention (Handler fetches and stores at `negotiation.active`) plus the agreement digest on the event — a protocol MUST, available now, not an ADR (§3.1).
- **`docs/station-checkpoints.md:36` "four things".** At least six: add the train provider's offer and the network's decision-mode rule; and the identity input differs between push and poll (§2.2).
- **`docs/station-checkpoints.md:76` PEP 2 = "an agreement exists, is active, covers this action, within quota".** Add: binds this train and payload digest, this network, this assignee; is within its validity bound; and its decision mode permits reuse (§2.2 vi, §4.3).
- **Finding 6 (v0.1) "manual approval has no ODRL idiom … equivalently a duty".** The duty idiom is fine for discretion and wrong for a legal requirement (§4.4 point 4). Do not adopt it as the general form.

I agree with findings 12–18 and 20–25 as recorded, having re-verified 19, 20, 21, 22, 23, 24 and 25 against the files.

---

## 8. Reproducing this review

```sh
cd <sandbox>
make check                                       # green, as the README says
.venv/bin/python probes/agreement_probes.py      # §1: A, B, C, E, G conform; D, F violate
.venv/bin/python probes/descriptor_request_probe.py   # §1: embedded request violates RequestShape; action mismatch
.venv/bin/python probes/schema_probes.py         # §1: six decision-less events/envelopes validate
```

The probes add nothing to the repository's own test paths and can be deleted; they exist so that every "conforms" and "violates" above is a thing that ran, not a thing I read.

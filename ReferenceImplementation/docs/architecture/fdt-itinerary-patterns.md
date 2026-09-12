# FAIR Data Train — Itinerary Patterns (working catalogue)

| | |
|---|---|
| **Status** | Working draft v0.4 — cases still for validation; the architectural questions of §8 were **decided on 11 Sep 2026** (see `fdt-ecosystem-architecture.md`, ADR-014–024) |
| **Date** | 11 September 2026 (v0.1; v0.2 adds non-life-science and cross-domain cases; v0.3 grounds the time-to-groin case in Dutch sources and replaces §6 with a pointer to the verified requirements register) |
| **Purpose** | Collect a representative sample of *itinerary patterns* — the ways a train's visits to stations can be shaped and decided — with cases that require each, so that their architectural requirements and impact on Train Handler, Station, Train and FDT-O can be evaluated before designing UI or APIs for them |
| **Design stance** | FDT is a **general-purpose, domain-agnostic** platform; the stronger claim is **cross-domain interoperability** (Section 5). The design must remain **alignable with the IDSA architecture and components, the EHDS and the other European Data Spaces** (Section 6) |
| **Companion documents** | `fair-data-station-architecture.md` (station architecture, §7.4 and ADR-013 on orchestration/choreography); Train Handler prototype (`Plan` = train + target stations, `Run` = execution, `Job` = one visit) |

## 1. How to read this document

Each pattern gets a short definition, cases from several domains, who decides the route and when, the coordination styles that can realise it, and its architectural implications. Cases are labelled by provenance so that nothing is mistaken for an established requirement:

- **[given]** — a real case stated by Luiz Olavo (currently *time-to-groin*). Luiz has confirmed that many of the proposed life-science cases have counterparts in projects he is involved in; they remain labelled [proposed] until a concrete counterpart is written down.
- **[literature]** — a pattern established in the federated-analysis or integration literature (iterative federated learning as practised in Personal Health Train implementations such as vantage6; Enterprise Integration Patterns: Scatter–Gather, Routing Slip, Process Manager, Content-Based Router, Aggregator).
- **[proposed]** — a hypothetical case written to illustrate the pattern; needs a real counterpart or should be dropped. Each pattern carries at least one case **outside life sciences**, marked with its domain, to test domain-agnosticism.

Section 7 summarises the patterns against a fixed set of dimensions; Section 8 lists the questions whose answers determine architectural impact.

## 2. Analysis dimensions

| Dimension | Values |
|---|---|
| **Route determination** — who decides the next station | Train owner at submission (static) · Train Handler (orchestrator) · Train itself (choreographer) · Visited station (referral) · Directory query (declarative target set) |
| **Route knowledge** — when the full route is known | Before dispatch · Per hop · Per round · Never fully (open-ended until a stop condition) |
| **Topology** | Single visit · Parallel set · Sequence · Tree (branching per record) · Loop (rounds) · Hierarchy (aggregator nodes) · DAG (dependent steps) |
| **State carriage** — what travels between hops | Nothing · Parameters only · Intermediate results returned to Handler and re-injected · Intermediate results carried inside the train |
| **Aggregation locus** | Data consumer · Train Handler · Dedicated aggregator station · The train · None |
| **Termination** | Fixed set exhausted · Stop condition on data · Convergence · Budget/timeout · Human stop |
| **Coordination style** | Orchestration (external coordinator) · Choreography (embedded routing) · Hybrid |
| **Train-type capability** | Query/API trains (`fdt-o:QueryTrain`, `fdt-o:APITrain`): no embedded logic ⇒ orchestration only · Script/Container trains (`fdt-o:ScriptTrain`, `fdt-o:ContainerTrain`): either style |
| **Domain span** (new in v0.2) | Single domain · **Cross-domain** — hops in different domains, each with its own vocabularies, ODRL profile, identity federation and metadata profile (Section 5) |

## 3. Pattern catalogue

### P1 — Single visit

One train, one station, one job. The degenerate base case; every other pattern composes it.

*Cases*: **[proposed · health]** a FHIR query train against one hospital station for an aggregate table. **[proposed · cultural heritage]** a SPARQL train against one museum's collection station retrieving provenance events for a set of object identifiers. **[proposed · public administration]** a SQL train against one municipality's station counting permit applications per district.

*Implications*: none beyond the station's job lifecycle; baseline for the matrix.

### P2 — Static fan-out (scatter–gather)

The same train (same parameters) goes simultaneously to a set of stations chosen before dispatch; jobs are independent; results are combined by the consumer or the Handler. This is the prototype's `Plan` with several `PlanTarget`s and the pattern in the current Handler mock-ups.

*Cases*: **[given, generalised · health]** the parametrised gene–disease SPARQL train sent to several annotation stations. **[proposed · agriculture]** one yield-and-soil query to the stations of farm cooperatives in several regions. **[proposed · energy]** an outage-statistics query to the stations of several distribution grid operators. **[proposed · mobility]** a trip-count query to regional public-transport operators' stations. **[literature]** Scatter–Gather.

*Variant P2b — query-defined fan-out* **[proposed]**: the target set is a Station Directory query ("all stations supporting FHIR whose datasets are about stroke care"; "all stations publishing DCAT datasets with theme *energy* in NUTS-2 region NL21"), resolved at dispatch time and re-resolved per recurring run (P9).

*Implications*: Handler needs per-run resolution of target sets and a record of which stations were actually visited (provenance). Stations unaffected. Aggregation at the Handler raises whether the Handler may see individual station results at all.

### P3 — Static sequence (routing slip)

The train visits stations in an order fixed before dispatch; each hop refines what the previous hop produced. The route is known; the data flowing along it is dynamic.

*Cases*: **[proposed · health]** registry station issues pseudonymous cohort identifiers → hospital station adds clinical variables → follow-up registry adds outcomes. **[proposed · manufacturing]** batch traceability with a known chain: component registry station → supplier production-record station → logistics station, to assemble the history of one production batch. **[proposed · public administration]** a policy-evaluation train collecting a cohort of addresses at a land-registry station, then energy labels at a certification body's station, then subsidy records at a municipal station. **[literature]** Routing Slip.

*Implications*: first pattern where **state travels between hops** — either re-injected by the Handler (orchestration; the Handler sees intermediate results) or carried by a container/script train (choreography; the origin station's PEP 3 must judge what may *leave with the train*, distinct from what is *delivered to the consumer*). The Handler's `Run` needs dependencies between jobs.

### P4 — Discovery chain (dynamic sequence / tree)

The next station is discovered from data at the current station; neither train nor Handler knows the route in advance. Because different records point to different next stations, the itinerary is in practice a **tree**.

*Cases*: **[given · health + emergency transport]** *time-to-groin for stroke* — EVT centre (treated patients, groin-puncture and door times, referring hospital, ambulance service) → that ambulance service's station (call, on-scene, hand-over times and pick-up place) → the referring primary stroke centre (door, CTA, needle, door-out times) → … until the symptom-onset time is found. Grounded in the Dutch guideline, the NVN/NVvR EVT-centre criteria (median door-to-groin < 30 min referred / < 75 min direct; onset-to-groin must be registered, no target), the Kwaliteitskader Ambulancezorg 2.0 (45 min from call to stroke/EVT centre, 80 % target) and the DASA registry — see `fdt-use-case-time-to-groin.md`. No official Dutch "< 2 h onset-to-groin" target was found; the case benchmarks the chain against the official component norms instead. The case is **cross-domain** (hospital care and ambulance care are different sectors with different standards, systems and vocabularies) and part of the hospital-side answer already exists centrally in DASA, so FDT's contribution is the prehospital extension and regional, route-level insight. **[proposed · cultural heritage]** provenance research — an artwork's ownership chain traced across museum, archive and auction-house stations, each record naming the previous holder. **[proposed · manufacturing / supply chain]** origin-of-materials due diligence — each supplier's station names its own suppliers for a given component; the chain ends at raw-material producers. **[proposed · finance]** transaction tracing across institutions, each hop revealing the counterparty's institution (heavily regulated; listed as a candidate only).

*Implications* (the most demanding pattern): per-record branching (many concurrent partial chains merged into one result); **record linkage across organisations** (a linkage key released by the origin station under policy, a pseudonymisation/TTP hop, or fragile matching on quasi-identifiers — Section 4); **agreement scope** (per hop on arrival, fitting ADR-008 but allowing a run to stall in *pending approval* mid-tree, versus chain-level up front with parties unknown in advance); data-dependent **stop condition** plus a **budget** (max hops, stations, deadline); coordination — query/API trains only orchestrated, container trains may hop autonomously (P10) or return to the Handler between hops (hybrid).

### P5 — Iterative rounds (convergence loop)

A fixed set of stations is visited repeatedly; each round's partial results are aggregated and the aggregate is sent back with the next round, until convergence or a round limit.

*Cases*: **[literature · health]** federated model training as in Personal Health Train implementations (e.g. vantage6). **[proposed · energy]** federated load-forecasting model across distribution grid operators' stations. **[proposed · mobility]** federated model across vehicle-fleet operators' stations for demand prediction, without pooling trip data. **[proposed · manufacturing]** predictive-maintenance model trained across several factories' stations.

*Implications*: the Handler (or a dedicated aggregator) is a **stateful orchestrator across rounds**; late or failed stations force a policy (wait, drop, timeout); agreements must cover repeated visits; stations accept the same train many times with changing payload; per-round result inspection (model updates can leak).

### P6 — Hierarchical aggregation

Stations organised in levels; lower-level results are combined by an intermediate aggregator station before reaching the next level, so no single party sees all raw partial results.

*Cases*: **[proposed · health]** hospitals → regional stroke-network station → national analysis, with counts below a disclosure threshold never leaving the region. **[proposed · official statistics]** municipal → provincial → national aggregation with statistical disclosure control at each level (output checking as practised by statistical offices). **[proposed · agriculture]** farm cooperatives → regional → national yield statistics. **[literature]** Aggregator; hierarchical federated learning.

*Implications*: an **aggregator station role** — a station acting as data consumer towards its children and data controller towards its parent; disclosure-control duties as ODRL duties evaluated at PEP 3 of each level.

### P7 — Conditional two-phase (feasibility → analysis)

A cheap first train (typically a count) goes to many stations; a heavier train is sent only where the first-phase result satisfies a condition.

*Cases*: **[proposed · health]** cohort count at twenty stations; analysis train only where ≥ *k* eligible patients. **[proposed · mobility]** count trips matching criteria at regional operators; detailed origin–destination analysis only where volumes suffice. **[proposed · cultural heritage]** first ask which archives hold documents mentioning a person or place; then send an OCR/NER container train only to those. **[literature]** Content-Based Router; feasibility queries in cohort-discovery networks.

*Implications*: the Handler evaluates a **condition on results** to derive the next target set — small, bounded orchestration that covers many practical needs; two trains (or one parametrised train with a mode) and a run model with phases.

### P8 — Train composition (dependent trains)

The output of one train becomes a parameter of a *different* train, possibly from another provider, at the same or other stations.

*Cases*: **[proposed · health]** cohort-selection train yields a pseudonym list; a statistical analysis train, parametrised with it, runs afterwards. **[proposed · agriculture × climate]** a drought-index train over meteorological stations yields a list of affected regions, which parametrises a yield-analysis train over agricultural cooperatives' stations — **cross-domain by construction**. **[proposed · energy × mobility]** an EV-charging-load train over grid operators' stations feeds a traffic-flow analysis train over road-authority stations. **[literature]** Process Manager.

*Implications*: the Handler holds a **workflow** (DAG of trains and target sets); typed parameters so outputs bind to inputs; results of step 1 are consumer data the Handler may or may not be allowed to hold.

### P9 — Recurring / standing run

The same plan is re-executed on a schedule or trigger; each execution is a new run; target sets may be re-resolved (P2b).

*Cases*: **[given, extrapolated · health]** the time-to-groin metric recomputed periodically for monitoring. **[proposed · energy]** monthly grid-loss statistics. **[proposed · environment]** daily air-quality exposure indices. **[proposed · cultural heritage]** nightly re-indexing of newly published collection records. The prototype already has `Run.shouldStartAt` (one-shot scheduling).

*Implications*: mostly Handler-side (schedules, run history, diffs between runs); agreements with validity windows covering repeated visits.

### P10 — Station referral / peer forwarding (choreographed hop)

A visited station passes the train on to the next station (or tells the train where to go) without the Handler in the loop; the Handler receives progress notifications and the final result.

*Cases*: **[given, variant · health]** the choreographed time-to-groin — a container train with embedded routing asks the hospital's station for the ambulance service's station and moves on. **[proposed · supply chain]** a supplier's station forwards the traceability train to its own suppliers' stations. **[proposed · logistics]** a shipment-tracking train handed from port-authority station to carrier station to customs station following the consignment.

*Implications*: **station-to-station dispatch** (a station acting as a Train Handler towards a peer), trust between stations, a credential/agreement the train can present at the next station without returning home, progress reporting to the originating Handler; largest impact on the station architecture.

### Orthogonal aspects (apply to any pattern)

- **Human-in-the-loop suspension**: any hop may enter *pending approval* (ADR-008); runs need a visible "waiting for approval at X" state and a timeout policy. In the EHDS setting this is where a data-permit decision by a health data access body would sit (Section 6).
- **Partial results and failure**: what the run delivers when some branches fail or are refused — nothing, the partial set with provenance, or a re-plan.
- **Provenance**: the itinerary as executed (stations, agreements, order, timings) as a PROV-O record of the run — the basis of the Handler's *itinerary map* and *replay* views.
- **Budget**: hops, stations, wall-clock time and cost limits as run parameters.

## 4. Cross-cutting concern: linking records across stations

P3, P4 and P8 only work if hops can refer to the same subject. Options: (a) a **linkage or pseudonymisation station** (trusted third party) appearing as a hop and translating identifiers between organisational pseudonym spaces; (b) the origin station releases a linkage key under an ODRL duty ("may be used only to query station Y within 24 h"); (c) matching on quasi-identifiers. Option (a) makes the TTP a first-class ecosystem element with its own station type; option (b) makes *content travelling onward* a policy object distinct from *results delivered*. Outside personal data the same problem appears as **entity resolution** — batch numbers, object identifiers, addresses, cadastral parcels, grid connection points — and is usually solved with shared persistent identifiers rather than pseudonymisation; the architecture should treat "linkage mechanism" as a pluggable concern, not a health-specific one.

## 5. Cross-domain interoperability

Domain-agnosticism means each domain can run FDT on its own; the stronger property is that **one itinerary can cross domains** — time-to-groin (health + emergency transport), health × environment (air-quality exposure per postcode area joined with cardiovascular outcomes), agriculture × climate × water, energy × mobility, cultural heritage × research. What cross-domain itineraries require of the architecture, to be validated:

1. **Domain-neutral core, domain profiles on top.** Station self-description and dataset metadata use a neutral core (DCAT-AP / FDP) with domain application profiles layered per dataset (e.g. the health, geospatial and mobility DCAT-AP extensions), so that a Handler can discover and plan across domains without understanding every profile, and a train can still find the domain-specific fields it needs.
2. **Link keys that cross domains are mostly spatial, temporal and administrative** — place (addresses, postcode areas, administrative units, coordinates), time, organisation identifiers — rather than personal identifiers. FDT-O / `fdt-commons` should standardise how a station declares the join keys a dataset supports, so that a cross-domain plan can check joinability before dispatch.
3. **One agreement chain, several ODRL profiles.** Each hop's controller may author conditions in a different profile (DUO+DPV for health, licence-oriented profiles for open government or heritage data, contractual profiles for industrial data). Matching must work per hop with the hop's profile, while the run-level record shows the consumer one coherent set of obligations (e.g. the strictest deletion duty applies to the merged result).
4. **Identity across federations.** Consumers arrive with identities from different federations (research/education federations, sector federations, business identities/wallets). The VC-ready party model (ADR-010) is what makes a cross-domain chain feasible; the station should accept several trusted issuers rather than assume one federation.
5. **Vocabulary alignment as a service.** Cross-domain trains need mappings (a diagnosis code to a service category, a postcode area to a NUTS region). Whether this is a train's own concern, a reusable "alignment station", or a Handler function is an open design question — see Section 8.
6. **Directories across domains.** Station Directories today index stations of one community; cross-domain planning needs either federated directories or a directory-of-directories, and directory search by join key and domain profile (P2b).

Demonstrating (2) and (3) on a real two-domain case — time-to-groin is the natural candidate — would be the most convincing evidence that FDT is a general data-visiting platform rather than a health tool.

## 6. Alignment with IDSA, the Dataspace Protocol, Gaia-X, the European Data Spaces and the EHDS

Requirement stated by Luiz (11 Sep 2026): the design must be alignable with the IDSA architecture and components and with the aspirations of the EHDS and the other European Data Spaces. The candidate mapping that stood here in v0.2 has been checked against the current texts and replaced by a **requirements register**, `fdt-data-space-alignment.md` (same folder), which records for each requirement its source, the FDT element affected, the status against the July 2026 architecture, a proposal and a horizon (v1 / v2 / EHDS 2029). Headlines:

- The normative IDSA reference today is the **IDSA Rulebook 2026-2** with the **Dataspace Protocol 2025-1** and **Decentralized Claims Protocol 1.0** (both submitted to ISO/IEC JTC 1 as PAS); IDS-RAM 4.2 is archived but remains the reference for connector anatomy and usage control. The Rulebook explicitly recognises "code to data" (the consumer "provides a data asset containing code (source code, compiled library, signed container) to the participant providing the data") and "confined compute" for high-sensitivity data — FDT's paradigm has a citable home.
- Cheapest high-value alignment steps for v1: make the station's FDP catalogue a DSP-conformant `dcat:Catalog` (one `odrl:Offer` per dataset, a distribution per mechanism, a data service per station); adopt the DSP structural rules for offers and agreements (unique ids, `target`, `assigner`, `assignee`, `timestamp`) as SHACL shapes in `fdt-commons`; document the mapping of FDT agreement and job states onto the DSP contract-negotiation and transfer-process state machines; model trains as contracted assets.
- Identity: keep federated OIDC for v1 as the Rulebook's "functionally equivalent" option; plan the VC phase as DCP (which also serves Gaia-X); name the FDT governance authority for trusted issuers.
- Regulation: the Data Act's essential requirements for data-space participants apply since 12 Sep 2025 (machine-readable descriptions of content, restrictions, vocabularies, APIs; interoperable automated agreement execution); the DGA may qualify a public Handler/Directory/Garage operator as a data intermediation service — legal check needed; from 26 Mar 2029 EHDS secondary use requires access "only through a secure processing environment" (Art. 73) — an SPE-conformant station profile is the design target, and the *pending approval* state is where an HDAB data permit plugs in.
- Cross-domain cases should be drawn from the European data spaces (health, agriculture, manufacturing, energy, mobility, finance, public administration, skills, Green Deal, cultural heritage, tourism, media, language, research); Simpl-Live instances (EHDS2, EOSC) are DSP-based, so DSP conformance is the practical interoperability path.

## 7. Summary matrix

| Pattern | Route decided by | Known | Topology | State between hops | Aggregation | Termination | Query/API trains? | Domains in sample |
|---|---|---|---|---|---|---|---|---|
| P1 Single visit | owner | before | single | — | — | fixed | yes | health · heritage · public admin |
| P2 Static fan-out | owner (P2b: directory query) | before / at dispatch | parallel | none | consumer / Handler | fixed | yes | health · agriculture · energy · mobility |
| P3 Static sequence | owner | before | sequence | results → next hop | train or Handler | fixed | yes (orchestrated) | health · manufacturing · public admin |
| P4 Discovery chain | data at each station | per hop | tree | results + linkage keys | Handler / train | data condition + budget | yes, orchestrated only | health+transport · heritage · supply chain · (finance) |
| P5 Iterative rounds | orchestrator | per round | loop | aggregate → all | Handler / aggregator | convergence / limit | unusual | health · energy · mobility · manufacturing |
| P6 Hierarchical aggregation | owner | before | hierarchy | aggregates upward | aggregator stations | fixed | yes | health · statistics · agriculture |
| P7 Two-phase conditional | Handler from results | per phase | parallel → filtered | condition only | Handler | fixed (2 phases) | yes | health · mobility · heritage |
| P8 Train composition | owner (DAG) | before | DAG | typed outputs → inputs | Handler / consumer | fixed | yes | health · agri×climate · energy×mobility |
| P9 Recurring | owner (schedule) | before | any, repeated | none across runs | per run | schedule end | yes | health · energy · environment · heritage |
| P10 Station referral | visited station / train | per hop | sequence / tree | inside train | train | data condition + budget | no | health · supply chain · logistics |

Design drivers chosen (11 Sep 2026): **P4, P5, P7, P8** as first-class alongside P2; the rest are recorded as future.

## 8. Questions that determine architectural impact — and the decisions taken (11 Sep 2026)

1. **Real counterparts for the [proposed] cases** — Luiz: many exist in involved projects; real stakeholders are **not involved directly for now** ("if we get real-world cases online, we use"). Cases stay [proposed] with fictional actors until then. Missing candidates (write trains, negotiate-only visits, resident/event-driven trains) remain open.
2. **May the Handler see intermediate results?** — **Only non-personal / aggregate data** released by a station's result inspection (ADR-015). Orchestration works on aggregates, next-hop lists and opaque pseudonyms; record-level joins happen in stations or through a linkage station.
3. **Agreement scope for multi-hop runs** — **Per hop, negotiated on arrival**; *pending approval* mid-chain is acceptable and handled by timeouts and partial-result policies (ADR-014). A framework-agreement convenience layer is an open issue.
4. **Linkage** — **A Linkage Station type in FDT-O** (identifier translation as an interaction mechanism, visited under its own agreement, wrapping existing TTPs); datasets declare pseudonym spaces and join keys (ADR-022).
5. **Station-to-station forwarding (P10)** — **Not in v1; designed for** (ADR-016). In v1 a choreographing train returns to the Handler between hops.
6. **Where the itinerary language lives** — **fdt-commons: FDT-O vocabulary + SHACL shapes + JSON-LD**, shared by Handler and stations; expressible as DSP/ODRL where overlapping (ADR-023).
7. **Cross-domain vocabulary alignment** — **Alignment stations/services discoverable via the Directory, plus per-dataset vocabulary and join-key self-description** so joinability is checkable at planning time (ADR-024).
8. **Depth of data-space alignment** — DSP **v1 mapping + shapes, v2 endpoints** (ADR-019); trains as contracted assets (ADR-020); federated governance with multi-network stations (ADR-017); natural persons by deployment profile (ADR-018); Gaia-X alignable, not compliant (ADR-021).

State carriage between hops: **all three mechanisms** (inside the train, via the orchestrator, via a linkage station) are supported and chosen per plan (ADR-016).

## 9. Failure and partial-result semantics per pattern (ADR-026, accepted 12 Sep 2026)

A run over several stations rarely ends with every visit delivered. This section fixes the vocabulary of what can go wrong at a visit, what a plan may say about it, and what each pattern does with a missing visit. It is recorded as ADR-026 in `fdt-ecosystem-architecture.md` (accepted 12 Sep 2026) and realised in `fdt-commons` v0.3 (`fdt-run:FailurePolicy`, visit outcomes, completeness record).

### 9.1 Visit outcomes

Every visit ends in exactly one terminal outcome. The first two are successes; the rest are the ways a visit can be missing from a result.

| Outcome | Meaning | Who decides | Agreement afterwards |
|---|---|---|---|
| **Delivered** | Results (or onward state) released after inspection; `inspection.outcome` is *passed* or *redacted* (an aggregation threshold removed cells) | station PEP 3 | active → fulfilled |
| **Skipped** | Never dispatched: not selected by a phase condition (P7), pruned with a failed branch (P4/P8), or dropped by the failure policy | Handler | none |
| **Refused** | Matching failed, or the controller denied approval | station PDP / controller | rejected |
| **TimedOut** | Approval pending past the plan's wait, or the budget deadline passed while the visit was queued or pending | Handler | rejected (request withdrawn) |
| **Rejected** | A checkpoint refused the visit after an agreement existed: payload validation (PEP 2) or result inspection (PEP 3, e.g. k-anonymity duty) | station | active (the agreement stands; the *visit* is rejected) |
| **Failed** | Technical failure: adapter error, container crash, network | station or Handler | active |
| **Revoked** | The controller revoked the agreement while the visit was queued or running; the visit stops at the next checkpoint (station ADR-008) | controller | revoked |

*Refused* and *Rejected* are deliberately distinct: a refusal is a governance decision before any data is touched; a rejection is a compliance decision at a checkpoint. Both are shown to the consumer with the station's stated reason, because the consumer is a party to that hop's negotiation (ADR-014). A *Skipped* station is reported with its cause — *not selected*, *pruned*, or *dropped* — because "your count was below the threshold" and "the station refused" must never be confused in a two-phase result.

### 9.2 What a plan may say — the failure policy

A plan carries one `fdt-run:FailurePolicy` (required from `fdt-commons` v0.3). It has one reaction per non-success outcome and a completeness threshold.

| Outcome | Allowed reactions | Default |
|---|---|---|
| Refused | **SkipBranch** (drop the station and, in tree patterns, everything discovered only through it) · **FailRun** | SkipBranch |
| TimedOut (approval) | **SkipBranch** · **FailRun** · **Wait** (keep waiting until the budget deadline; only then apply SkipBranch) | SkipBranch, with `approvalWait` (duration) before it applies |
| Rejected | **SkipBranch** · **FailRun** | SkipBranch |
| Failed | **Retry** (`maxRetries`, then SkipBranch) · **SkipBranch** · **FailRun** | Retry, `maxRetries` 2 |
| Revoked | **SkipBranch** · **FailRun** | FailRun for sequence-shaped patterns (P3, P8 along a dependency), SkipBranch otherwise |
| Completeness | `minDeliveredStations` (absolute) or `minDeliveredFraction` (0–1) over the stations the plan *intended* to visit; when neither is given, every intended station must deliver | all intended |

*FailRun* terminates the run: queued visits are withdrawn, running visits are asked to stop at their next checkpoint, and nothing is delivered. *Wait* is only meaningful for approval timeouts and is bounded by the budget deadline (an itinerary with *Wait* must have a deadline). Retries reuse the existing agreement — a technical failure does not renegotiate — and are recorded as attempts of one visit.

### 9.3 What the run delivers

The run ends **Finished** when every intended station delivered; **PartiallyDelivered** when the completeness threshold is met but some intended stations did not deliver; **FailedRun** when the threshold is not met or *FailRun* fired; **Stopped** when a person stopped it. A partial delivery is never silent: the run record carries a **completeness statement** — for every intended station its outcome, cause and, where the station gave one, its reason; the counts per outcome; and the statement "aggregate over *n* of *m* intended stations" that the Handler shows with the merged result. Because the merged result is a PROV-O derivation from the delivered visits, a result derived from a *Revoked* visit is identifiable afterwards; what must then happen to it is whatever the duties of the revoked agreement say (deletion duty, reporting duty), not something the run model decides.

### 9.4 Per pattern

| Pattern | A missing visit means | Notes |
|---|---|---|
| **P1 Single visit** | the run has no result | Completeness is trivially all-or-nothing; Retry applies to Failed. |
| **P2 Fan-out** (incl. P2b) | an aggregate over fewer stations | The natural home of `minDeliveredFraction`; the completeness statement lists the missing stations. For P2b the *intended* set is the directory answer at dispatch. |
| **P3 Sequence** | the chain is broken at that step | SkipBranch is only possible for a step marked `optional`; otherwise the outcome is FailRun. Revocation of an earlier step's agreement while a later step runs does not stop the later step (its own agreement stands) but is recorded. |
| **P4 Discovery chain** | that branch of the tree is pruned | Stations discovered *only* through the missing station become Skipped (*pruned*). The stop condition keeps being evaluated over what was delivered; the budget still applies. Completeness is counted over intended stations *known so far*, and the statement names pruned subtrees. The linkage hop is special: if the linkage station refuses or fails, every downstream branch depending on translated pseudonyms is pruned — so a plan with `ViaLinkageStation` should set FailRun on the linkage hop unless a partial answer is useful. |
| **P5 Iterative rounds** | one participant is missing from round *k* | Two admissible policies, chosen in the plan: **DropForRemainingRounds** (the station leaves the federation for the rest of the run; the aggregate is recomputed over the remaining set and the completeness statement records from which round) or **Wait**. Rejoining is not allowed in v1 (it would mix aggregates computed over different sets). The convergence condition (ADR-025) reads only delivered rounds. |
| **P6 Hierarchical aggregation** | if a *leaf* is missing, its aggregator reports over fewer leaves; if an *aggregator* is missing, all its leaves are lost | Completeness is therefore counted in leaves, and the aggregator's own envelope must state how many leaves it aggregated (a declared output field, so the plan can compare it). |
| **P7 Two-phase** | phase 1 missing → the station is Skipped with cause *not evaluated* (never *not selected*); phase 2 missing → an aggregate over fewer selected stations | The completeness threshold applies to phase 2 over the *selected* set; the result states both "selected *s* of *m*" and "delivered *d* of *s*". |
| **P8 Composition (DAG)** | every phase depending on the missing output is Skipped (*pruned*) | A phase may declare `optional`, in which case dependants run with the input absent and must say so in their output. Revocation follows the dependency edges. |
| **P9 Recurring** | one occurrence is partial or failed | The schedule is not cancelled; each occurrence has its own run record and completeness statement; a plan may set `maxConsecutiveFailures` after which the schedule pauses and the owner is notified. |
| **P10 Station referral (choreographed)** | the train returns with the refusal or failure recorded in its own envelope | The Handler learns of it only when the train returns (v1: between hops); it cannot intervene mid-hop, so the train itself must honour the plan's failure policy — the same `FailurePolicy` travels with the train. |

### 9.5 What this asks of the components

The **station** reports every non-success with a machine-readable outcome and a reason text at the checkpoint where it happened (already in the visit protocol as compliance events). The **Handler** applies the policy, keeps the intended set explicit (so completeness is computable), evaluates stop and phase conditions only over delivered envelopes, and renders the completeness statement next to the itinerary map — the map's *Not selected*, *Refused*, *Waiting*, *Failed* states are these outcomes. The **Individual Gateway** shows a controller the consequence of a revocation before confirming it: which running visits stop and which derived results become identifiable (mock-up G2 already says "the gateway shows which agreements are affected").

## 10. Next steps

With the decisions above recorded as ADR-014–024 in `fdt-ecosystem-architecture.md`, the remaining work on this catalogue is to anchor cases — with fictional actors for now — per driver pattern (P4, P5, P7, P8) including at least one outside life sciences and one cross-domain, to specify failure and partial-result semantics per pattern, and to define the run-description vocabulary in `fdt-commons`. *Status 11 Sep 2026 (later the same day):* the run-description vocabulary exists (`fdt-commons` v0.3, ADR-023) and the **conditions** that P4, P5 and P7 depend on — phase conditions, next-hop selectors, stop conditions — are JMESPath predicates and selectors over JSON visit-result and run-state envelopes (**ADR-025**, accepted 12 Sep 2026), under the rule *the train computes, the plan compares*: a condition can only read the aggregate fields a train declares as output, which is also why per-record branching in P4 happens through pseudonym lists carried via a linkage station and never in the Handler. Itinerary screens for P4 and P7 (H5, H6) and the Individual Gateway (G1, G2) are on the design canvas; failure and partial-result semantics per pattern are §9 (ADR-026, accepted).

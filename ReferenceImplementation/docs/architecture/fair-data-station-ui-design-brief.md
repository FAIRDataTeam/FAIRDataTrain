# Design Brief — FAIR Data Station Console (UI mock-up)

| | |
|---|---|
| **Client** | Luiz Olavo Bonino da Silva Santos — FAIR Data Train project |
| **Date** | 2 July 2026 |
| **Deliverable** | High-fidelity mock-up screens of the FAIR Data Station console, for discussion with colleagues |
| **Audience of the mock-up** | Research colleagues, potential adopters (hospitals, research institutes), future development team |
| **Companion document** | `fair-data-station-architecture.md` (same folder) — authoritative on concepts and terminology |

## 1. What the product is

The **FAIR Data Station** is the node in the FAIR Data Train ecosystem that hosts data and lets computation visit it, instead of the data being shipped out. Trains (packaged queries, API calls, or containerized algorithms) arrive at the station; the station checks them against machine-readable usage policies, executes the permitted ones against local data sources, and returns only the results. Everything is governed by **agreements** negotiated in ODRL between the **data controller** (who has authority over the data) and the **data consumer** (the party behind the train), enforced and audited by the station.

The mock-up is for the **station console**: a single web application with **role-based views** covering everyone who works *at* the station. It is the trust surface of the system — a hospital data steward should look at it and feel: *I can see everything that touches my data, and nothing moves without my rules.*

## 2. Design direction

Visual language is the **designer's choice**, within these constraints:

- It must read as **trustworthy and calm** in institutional contexts (hospitals, universities) — this is governance software, not a growth dashboard.
- **Clarity above density**: policy and audit content is legally meaningful; ambiguity is a design failure.
- **Accessibility**: WCAG 2.2 AA minimum; color never the sole carrier of state; keyboard-navigable patterns.
- Web application, desktop-first (1440px reference), gracefully usable at tablet width. Dark mode optional, not required.
- The FDT project has no fixed brand; a light identity (name, mark, restrained palette) may be proposed as part of the work.

## 3. Users and roles

One console, three roles. Role switching should be visible in the frame (e.g., role badge in the header); a user can hold several roles (in a personal station, one person holds all).

**Station Owner (operator).** Runs the station: which interaction mechanisms (adapters) are enabled, resource quotas, hosted controllers, dispatch mode (push/poll), station health. Cares about: is the station healthy, what is running, is anything stuck or abusive.

**Data Controller (data steward / researcher who owns data).** Governs *their* resources on the station: authors access conditions (ODRL offers), reviews and approves agreement requests flagged for manual approval, watches who did what with their data. Cares about: control, evidence, and low-effort policy management. **Critical multi-tenancy rule**: a controller sees only their own resources, policies, agreements, and audit trail — never another controller's.

**Auditor (read-only).** Compliance officer or the controller/owner in review mode: searches the audit trail, inspects any decision's justification chain (event → job → agreement → offer/request → identities).

## 4. Core domain objects the UI must make tangible

- **Resource / dataset** — data hosted or fronted by the station; each carries a controller binding and FAIR metadata.
- **Access condition (ODRL Offer)** — controller-authored policy on resources: permissions, prohibitions, duties (e.g. "research purpose only; no commercial use; results deleted after 30 days; manual approval required").
- **Access request (ODRL Request)** — what a train asks for: consumer identity, purpose, requested actions.
- **Agreement** — the matched, signed contract. Lifecycle: *requested → matched → pending approval → active → fulfilled / expired / revoked* (plus *rejected*). The UI treats these states as first-class, color-and-icon coded.
- **Job** — one train execution under an agreement, passing three policy checkpoints (arrival, pre-execution, result inspection). Lifecycle: queued → checking → running → inspecting results → delivered / rejected / failed.
- **Interaction mechanism / adapter** — how trains interact: SPARQL, SQL, API/FHIR, Docker container. Enabled per station; Docker runs sandboxed.
- **Audit event** — append-only; every event links to the agreement that governed it.

**A key design challenge**: ODRL policies are machine-readable graphs. The UI must render them as **human-readable condition summaries** (e.g. sentence-style: "Allows *analysis* for *approved research purposes*, prohibits *re-identification*, requires *result deletion within 30 days*") with the formal representation one click away, and offer a **guided policy builder** (structured choices, not raw RDF) for authoring.

## 5. Screens to mock (10)

1. **Station dashboard (owner home).** Health and activity at a glance: station identity + capacity class; adapters enabled/disabled with status; jobs today (queued/running/delivered/rejected); pending approvals count; recent audit highlights; dispatch mode (push/poll) indicator.
2. **Jobs monitor.** Live table of jobs: train name, consumer organization, controller's dataset, mechanism, agreement ref, current checkpoint state, duration. Row expands to a **checkpoint timeline** (PEP 1 → PEP 2 → execution → PEP 3) showing each decision and its justification. Filter by state/mechanism/controller.
3. **Job detail.** One job end-to-end: what arrived, identity chain, the governing agreement (linked), execution log summary, result inspection outcome, obligations scheduled (e.g. "delete results by 1 Aug 2026"), full audit slice.
4. **Datasets (controller view).** The controller's resources: metadata completeness, attached conditions, activity sparkline, "who can currently reach this" summary.
5. **Policy builder (controller).** Guided ODRL offer authoring: pick resources → allow/prohibit actions → constraints (purpose, time window, consumer type) → duties (deletion, reporting) → toggle "require my approval per agreement" → live human-readable preview + formal view tab. Show validation ("this condition conflicts with…").
6. **Approvals inbox (controller).** Queue of pending agreements: who is asking, for what data, stated purpose, requested actions, matching result explanation ("your conditions were met except: requires manual approval"). Approve / deny with reason; deadline indicator (timeout behavior).
7. **Agreement detail.** The contract rendered for humans: parties (with identity provenance — issuer, subject), state timeline matching the lifecycle above, conditions in force, jobs executed under it, revoke action (controller) with consequence warning ("running jobs will be stopped at the next checkpoint").
8. **Audit explorer (auditor).** Searchable event stream with powerful filters (time, actor, dataset, agreement, decision outcome); every event expandable to its justification chain; export.
9. **Station settings (owner).** Adapters on/off with per-adapter config summary (Docker shows sandbox posture: "no network egress, 4 CPU / 8 GB limits"); hosted controllers management; identity providers (OIDC) trusted; dispatch mode; deployment profile indicator (personal / team / enterprise).
10. **Public catalog page (unauthenticated).** How the station presents itself to the outside: FAIR metadata, datasets with human-readable access conditions, supported interaction mechanisms, "how to send a train here" (points to Train Handler), station capacity class.

If a **clickable flow** is feasible within the effort, prioritize this journey: *Approvals inbox → agreement detail → approve → agreement active → job appears in monitor → job detail with delivered results.* It demonstrates the whole value proposition.

## 6. Realistic sample data (use this, not lorem ipsum)

- Station: **"University of Twente Data Station"**, enterprise profile, capacity class L, adapters SPARQL + SQL + FHIR enabled, Docker enabled with sandbox.
- Controllers: **Cardiology Research Group** (Dr. A. Jansen), **Semantics, Cybersecurity & Services group** (Dr. L.O. Bonino), **Personal station demo**: "Dr. Bonino's activity data" for the personal-scale contrast if a settings variant is shown.
- Datasets: "Heart failure cohort 2019–2025 (FHIR)", "Cardiac MRI features (SQL)", "Rare disease variants (SPARQL)".
- Consumers: "EU-CardioNet consortium (Radboud UMC)", "HealthAI B.V." (show a denial for commercial purpose to demonstrate prohibitions).
- Agreements/jobs in assorted states, including one *pending approval*, one *revoked*, one job *rejected at result inspection* ("aggregate below k-anonymity threshold").

## 7. Tone of language in the UI

Plain, precise, non-legalistic English; verbs for actions ("Approve", "Revoke", never "OK"). Policy summaries in controlled sentence patterns. Never show raw IRIs by default; always label with human names, IRIs on hover/expand.

## 8. Out of scope

Train authoring/marketplace UI (Train Handler's domain), FDP metadata editing workflows beyond dataset basics, mobile layouts, user management/IdP admin screens, marketing site.

## 9. Deliverables requested from Claude Design

1. High-fidelity mock-ups of the 10 screens (1440px desktop).
2. A short design-system sheet: palette, type scale, spacing, the agreement/job **state color-and-icon system**, and the human-readable policy rendering pattern.
3. The approval clickable flow (Section 5), if feasible.
4. Brief rationale notes per screen (what was optimized for).

## 10. Reference material

- `fair-data-station-architecture.md` — component architecture, roles, agreement lifecycle (Section 6.4 state machine matches the states above), runtime flows.
- Diagrams in `diagrams/` — especially `uml-state-agreement-lifecycle.svg` (state system) and `uml-sequence-negotiation.svg` (approval flow).
- ODRL Information Model 2.2 (https://www.w3.org/TR/odrl-model/) — only for terminology; the UI must not expose raw ODRL.

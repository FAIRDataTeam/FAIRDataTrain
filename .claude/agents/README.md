# Agent roster

Nine agents, split by **what breaks if the work is wrong** rather than by which files get
edited. The model tier follows from that: the tasks where a mistake is invisible until it
discloses someone's data, or is silently copied into every component, get the strongest
model; the tasks whose correctness is a command that passes or fails get a cheaper one.

| Agent | Owns | Model | Why this tier |
|---|---|---|---|
| `contract-steward` | `fdt-commons`, `FDT-O` — shapes, schemas, vocabularies, the ontology, the protocol | opus | A contract error is generated into every component and caught by nothing. The deepest reasoning in the project: SHACL, OWL, ODRL and DSP semantics at once. |
| `policy-engine` | ODRL evaluation, agreements, PEP 1–3, disclosure rules, failure policy | opus | A mistake here discloses a medical record. PEP 3 has to be adversarially right, not plausibly right — opus won this exact task in the benchmark. |
| `verifier` | Re-running and attacking claims; adversarial fixtures | fable | Its whole value is catching what everyone else's tests missed — so it runs a *different* model from the implementers on purpose. In the benchmark, opus and fable found overlapping but non-identical defect sets from identical inputs. Model diversity as a correctness mechanism. |
| `station-dev` | Station app, protocol server, orchestrator, metadata, adapters | opus | Substantial engineering against a fixed contract; wrong code fails visibly at a checkpoint. |
| `handler-dev` | Run model, conditions, orchestration patterns, PROV-O records | opus | Same, plus the ADR-015 no-record-level-data rule to hold onto. |
| `console-dev` | The three consoles, the itinerary map, the replay scrubber | opus | Judgement about what a controller understands — the map and the justification chains are genuinely hard UI. |
| `tech-writer` | Conformance material, operator and controller guides, ADR drafts | opus | Writing for an audience that cannot ask a follow-up question. |
| `contract-codegen` | Model/type generation, fixture wiring, scaffolding, plumbing, refactors | sonnet | Specified work whose correctness criterion is a command that passes or fails. |
| `scout` | Read-only search across repos and architecture documents | haiku | Locating things. Cheap, parallel, and the answer is checkable at a glance. |

## Routing

**By work package.** WP-0.2 and any contract change → `contract-steward`. WP-0.3 →
`contract-codegen`. WP-0.4, WP-1.1, WP-1.4, WP-2.5, WP-2.6, WP-3.3, WP-4.3 → `station-dev`.
WP-1.2, WP-1.3, WP-2.2, WP-2.4 → `policy-engine`. WP-1.5, WP-2.1, WP-2.3, WP-3.1, WP-3.2,
WP-4.1 → `handler-dev`. WP-2.7, WP-3.5 → `console-dev`. WP-4.4 → `tech-writer`.

**Three rules that override the table.**

1. **Contract changes never happen inside a component.** If any agent finds it needs a term,
   shape, schema or endpoint the contracts lack, it stops and hands off to `contract-steward`,
   which changes `fdt-commons` first — version bump, `FINDINGS.md` line, validators — before
   any code is written against it. A provisional term invented in a component is a fork of
   the contract that no validator will catch.
2. **`verifier` runs before a work package is called done**, independently, on the acceptance
   criterion — not on the implementer's summary of it.
3. **`policy-engine` reviews anything that decides what leaves a station**, even when
   `station-dev` or `handler-dev` wrote it.

## The standing instruction in every definition

Every agent carries the same rule, because this project has been bitten by its absence three
times — unparseable fixtures that a lenient validator accepted, a namespace disjunction that
left the shapes constraining nothing, and an acceptance criterion naming a fixture that does
not exist:

> **Verify, never assert.** Claim only what you ran, name the tool and version, show the real
> output. A check that cannot fail is not evidence. Never buy a green run by weakening a
> check. If something could not be made to work, say so plainly and say why.

## Benchmark

The tiers above were set by running real M0/M1 deliverables — pydantic model generation from
the JSON Schemas, the station self-description at `GET /`, and the WP-1.3 ODRL evaluator —
on adjacent model pairs in identical sandboxes, scored on whether the machine-checkable pass
condition actually passed and on whether the agent noticed the contract defects the task
contained. Two tiers moved from the initial guess as a result. See `benchmark.md`.

The benchmark's most valuable output was not the ranking: it was **eleven contract defects**
(`fdt-commons` findings 12–22, plus Q9 and Q10), every one invisible to `make check`, found
because agents were asked to *build something real* against the contracts rather than read
them. That is the argument for running acceptance criteria early, and for `verifier`.

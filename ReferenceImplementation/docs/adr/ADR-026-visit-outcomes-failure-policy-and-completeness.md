# ADR-026 — Visit outcomes, failure policy and completeness statement

| | |
|---|---|
| **Status** | Accepted (proposed 11 Sep 2026; confirmed by Luiz 12 Sep 2026). |
| **Deciders** | Luiz Olavo Bonino da Silva Santos |
| **Source** | Extracted verbatim on 12 September 2026 from *FAIR Data Train — Ecosystem Architecture, v0.1.4*, §Architecture Decision Records (`docs/architecture/fdt-ecosystem-architecture.md` in this repository, `FAIR Data Train/fair-data-station-architecture/` in the project folder). The source document remains normative; edit there and re-extract. |

## Context

Multi-station runs routinely end with some visits refused, timed out, rejected at a checkpoint, failed or revoked; the plan model had only an ad-hoc `onApprovalTimeout` string and a `partialResults` flag, and the pattern catalogue listed failure semantics as open.

## Decision

(1) Seven terminal **visit outcomes** — Delivered, Skipped (not selected / pruned / dropped), Refused, TimedOut, Rejected, Failed, Revoked — with *Refused* (governance, before data) kept distinct from *Rejected* (compliance, at a checkpoint), and every non-success carrying the station's reason. (2) Every plan carries one **failure policy**: a reaction per outcome (SkipBranch, FailRun, Wait for approval timeouts, Retry with `maxRetries` for technical failures; DropForRemainingRounds for P5) and a **completeness threshold** (`minDeliveredStations` or `minDeliveredFraction` over the *intended* stations; default: all). (3) Run end states Finished / PartiallyDelivered / FailedRun / Stopped, and a **completeness statement** in the run record: per intended station its outcome, cause and reason; counts; "aggregate over *n* of *m*". (4) Pattern-specific rules as tabled in `fdt-itinerary-patterns.md` §9 (sequence steps fail the run unless optional; discovery-chain branches are pruned and the stop condition reads delivered envelopes only; two-phase reports *selected s of m* and *delivered d of s*; iterative rounds drop a station for the remaining rounds rather than let it rejoin; recurring schedules survive a failed occurrence). (5) Retries reuse the agreement; results derived from a revoked visit are identifiable through PROV-O and fall under the revoked agreement's duties.

## Alternatives

all-or-nothing runs (simple, but unusable for fan-out over dozens of stations); silent partial results (misleading, and incompatible with the transparency the Rulebook and EHDS ask of processing); re-planning on failure (v2 candidate — substitute stations from the Directory).

## Consequences

`fdt-run:FailurePolicy`, outcome and cause individuals, `fdt-run:Completeness`, `intendedStation`; `onApprovalTimeout`/`partialResults` retired; run-state envelope gains per-outcome counters usable in ADR-025 conditions; the itinerary map's state vocabulary is the outcome vocabulary; the Gateway previews revocation consequences.

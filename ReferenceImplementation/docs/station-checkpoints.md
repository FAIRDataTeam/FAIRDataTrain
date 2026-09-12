# Station checkpoints — the PoC's sockets and what v1 puts in them

| | |
|---|---|
| **Status** | Implementation note, 12 September 2026. Derived by reading `FAIRDataTeam/FAIRDataStation` (Java PoC, branch `develop`) against the v1 architecture. Not normative — the station architecture and ADR-001–027 are |
| **Purpose** | The PoC defines the checkpoint *sequence* and almost none of the checks. This says which v1 mechanism belongs at each one, and which sockets are empty |

## What the PoC actually does

`GenericTrainInteraction.interact()` runs four named stages, and every stage boundary emits a
job event — so the PoC already has ADR-027's "every decision is an event" instinct, without
the justifications.

```
Fetch          fetch train metadata by URI · fetch payload metadata · fetch payload
Validation     train metadata · train type · payload resource · payload metadata · parse payload
AccessControl  checkAccess()
Execution      execute · process result · prepare and send artifacts
```

`JobStatus` is `PREPARED → QUEUED → RUNNING → FINISHED | ABORTING | ABORTED | ERRORED | FAILED`.

## The three things the PoC tells us

**1. `AccessControlService.checkAccess()` is an empty method with no arguments.**

```java
public void checkAccess() {
    // TODO: arguments? some basic check?
}
```

That signature is the most useful thing in the PoC, because the first design question is
exactly the one its `// TODO: arguments?` asks: *what does the station need in hand at this
point?* In v1 it needs four things — the train's ODRL request, the controller's offers for
the visited dataset **restricted to the visit's network**, the station owner's policy, and the
evidenced identity of whoever submitted the train. None of the four exists in the PoC.

This one empty socket is where both the negotiation (ADR-007/008) and PEP 2 go, and they are
not the same checkpoint: negotiation *produces* an agreement, PEP 2 *checks* one is active.

**2. The result is inspected on the FHIR path and not on the SPARQL path.**

```
FHIR:    … → Execution: FHIR response received → Validation: Validating FHIR response
                                               → Execution: Preparing and sending artifact(s)
SPARQL:  … → Execution: Executing query → executeQuery(…) → artifacts
```

The FHIR adapter validates its response before releasing artefacts. The SPARQL adapter does
not — results go straight out. This is not an oversight to copy: it shows that **result
inspection sitting inside the adapter means each adapter decides whether to inspect**, and one
of two adapters decided not to.

PEP 3 therefore belongs in the orchestrator, after the adapter returns and before the envelope
is assembled — adapter-independent, unskippable, and the same rules whatever produced the
result. Record-level leakage through something labelled an aggregate is the main correctness
risk in the system; an inspection an adapter can opt out of does not address it.

**3. There is no notion of who submitted the train.**

Nothing in the PoC carries a train owner, submitter or any identity. The check for "who
submitted this train" has nothing to build on: it is PEP 1 verifying a bearer token against
the trusted issuers **of the network the visit is dispatched under** (ADR-010/017), which is
also where `consumerType` and the other eligibility facts must come from.

## The mapping

| PoC checkpoint | v1 | State |
|---|---|---|
| Fetch: train metadata, payload | PEP 1 — fetch descriptor and payload; **verify the payload digest against the train's Garage offer** | digest check absent |
| Validation: train metadata, type | PEP 1 — descriptor against its JSON Schema, train against `TrainShape`, mechanism supported and *enabled* | type-only |
| — | PEP 1 — **token verified against the network's trusted issuers**; train owner established | absent |
| — | PEP 1 — the ODRL request against `RequestShape` | absent |
| — | **Negotiation** — offer × request × station policy → agreement; `requested → matched → active \| pending-approval \| refused` | absent |
| `checkAccess()` | PEP 2 — an agreement exists, is active, covers this action, within quota | empty stub |
| Validation: computation requirements | PEP 2 — declared requirements against capacity and sandbox posture | absent |
| Execution | the adapter's `execute()` behind the SPI | present |
| Validation: FHIR response | **PEP 3** — aggregation threshold, permitted output fields per the declared `outputSchema`, no record-level classes; outcome `passed` / `redacted` / `rejected` | FHIR only, inside the adapter |
| Execution: prepare and send artifacts | result envelope with `inspection.outcome`; onward state `Aggregate` or `Pseudonym`, never record-level | present, ungated |
| every stage boundary | an event **with a justification naming the rule** (ADR-027) | events yes, justifications no |

`JobStatus` also needs the ADR-026 vocabulary: the PoC's `FAILED` currently covers a refused
request, a rejected result and a crashed adapter, which are three different things and are
reported verbatim to the consumer in a completeness statement.

## Two consequences for the contracts

Both follow from the requirement that the agreement be *immutable and auditable*; see
`fdt-commons/FINDINGS.md` findings 23–25 and `OPEN-QUESTIONS.md` Q11.

- An agreement that records only what was granted cannot be audited later, because the
  eligibility facts that justified granting it are not in it. It needs both — the granted
  permissions as live terms, and the evidence as a record.
- `fdt-p:derivedFromOffer` and `fdt-p:derivedFromRequest` are bare IRIs pointing at mutable
  resources. An audit that has to dereference them reconstructs whatever the offer says
  *today*, not what it said at 10:12:05 when the agreement was concluded.

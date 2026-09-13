# ADR-039 — Delegated standing, and the auditor as a party

| | |
|---|---|
| **Status** | **Accepted**, 13 September 2026 — answered by Luiz on the two parts of Q21 item 12 that were still open. The answers as given are in `OPEN-QUESTIONS.md` under Q21; anything here beyond them is drafting, and is marked where it goes furthest. |
| **Deciders** | Luiz Olavo Bonino da Silva Santos |
| **Relates to** | ADR-008 (approval), ADR-011 (three parties, three credentials), ADR-013 (a delegate may not countermand a prohibition — Q13.4), ADR-018 (natural persons as controllers), ADR-027 (every decision is an event with a justification), ADR-031 (a credential proves what metadata names), ADR-032, ADR-035 (standing at a station — **extended here**); **Q21** item 12, **Q13** decision 3 |

## Context

ADR-035 settled who has standing at a station and how each party proves it: the network's trusted
issuer for anything crossing organisations, and a credential configured out of band for whoever
administers a component, because "who may restart this station" is not a network concept. It left
two parts of Q21 item 12 open.

**Delegation.** Q13 decision 3 already requires an approval to record *who decided, and under what
authority — a delegate, a data access committee, a `[METC ref.]`*. The station had no notion of a
delegate at all: a controller token names a controller, and everyone holding it is that controller
as far as the station can tell. So the field Q13 asked for could only ever have been filled in
with the controller's own name, and the record would have said something true and useless.

**The auditor.** ADR-027 makes every station decision an event with a justification, and the trail
is written and kept. The parties who can read it are the operator, for their own station, and the
controller, for their own data. The party the trail exists for — whoever checks that a station did
what it said — has no way in. In practice that means an operator exports it for them, which makes
the party checking the station depend on the station's operator to hand them what to check. That
is Q12's custody problem one level out, and ADR-038 has just decided the same argument the other
way for agreements.

## Decision

**Two parties are added to ADR-035's list, and neither of them gains anything the controller did
not already have.**

### 1. A controller may delegate to a named person or body

1. A delegate acts **on behalf of a named controller**, for that controller's data only, and
   **inherits their standing without being able to exceed it.** ADR-034's chain is unchanged:
   network ≥ station ≥ controller ≥ delegate.
2. **Q13.4 binds a delegate exactly as it binds a controller.** They may supply evidence the
   machine lacks — the ordinary case, and the reason a person is in the loop at all — and they may
   **not** countermand a prohibition, which is the controller's own standing instruction about
   their own data.
3. **Every decision records the delegate and the authority** they acted under, which is the field
   Q13 decision 3 asked for and this makes answerable. *The controller decided* and *a delegate
   decided for the controller* are different facts, and the record says which.
4. **Delegation to the Individual Gateway is not decided here.** A controller delegating to a
   person is one party authorising another; a controller delegating to software is a different
   claim about who is accountable for the decision, and it needs its own ADR. ADR-018's Gateway
   acting for a natural person who *is* the controller is unaffected — that is not delegation, it
   is the controller's own agent.

### 2. The auditor is a party with a read-only surface

1. **Read-only, and enforced by the surface rather than by convention.** An auditor cannot
   approve, refuse, publish a condition, or change a setting. There is no write path to disable,
   because there is no write path.
2. **Scoped.** An auditor's credential names what they may read — a whole station, or one
   controller's data. Which requests are being made of whose data is itself disclosure (the reason
   a controller sees their own queue and nobody else's), and an audit surface that ignored that
   would be a way around the controller separation rather than a check on it.
3. **Their reads are events.** An audit trail that records every decision and not the fact that
   somebody read it has a hole in exactly the place a misuse would go.
4. **The credential is configured out of band**, on ADR-035's pattern, because who may audit this
   deployment is a question about this deployment. A station with no auditor credential configured
   has no audit surface at all, which is honest rather than broken: nobody has been given standing.

*Drafting beyond the answers:* the answers were "a named person or body, recorded" and "yes, a
read-only surface, scoped and recorded". Points 1.2, 1.4, 2.1 and 2.4 are this draft's reading of
what those mean against the decisions already in force.

## Alternatives

| | Why not |
|---|---|
| **No delegation; one credential, one controller** | Simplest, and it makes Q13 decision 3's record unfillable. A data access committee is how this decision is actually taken in the field; a model in which the committee is indistinguishable from the controller cannot record what happened. |
| **Delegation as a claim in the controller's own credential** | Tempting — no new party — and it makes the delegation invisible to the station, which then cannot record it. The point of the decision is the record. |
| **The operator exports the trail for the auditor** | No new surface and no new credential, and the party checking the station depends on the station's operator to be given what to check. ADR-038 has just refused the same shape of argument for agreements. |
| **An auditor with full read access to every station they can reach** | Scope-free is simpler to build and turns an audit credential into a way to read every controller's queue at once. |

## Consequences

- **`station-admin-api.yaml` and the controller API gain a delegate**, and the approval record
  gains the delegate and their authority. `fdt-commons` first, under the change protocol.
- **A new audit surface and a new credential** (`FDT_STATION_AUDITOR_TOKENS`, on the controller-token
  pattern: credential → what it may read). It is a work package, not a paragraph.
- **Read events are a new event kind**, and they will be the highest-volume kind on a busy station.
  The trail's retention and its own access rules need saying somewhere — this ADR does not say them.
- **ADR-011's "three parties" is now four**, and the phrase appears throughout the code and the
  documents. It stays accurate about *decision-making* parties; the auditor decides nothing, which
  is the whole design. Where the code says three, it should say what it means rather than count.
- **Q21 item 12 is closed**, together with the third part, which needed no draft: an owner may not
  publish a parametrised instance of a train type in v1, because parameters travel with the visit
  and a published instance would be an asset whose licence, withdrawal and digest ADR-036 has
  answered only for the type.

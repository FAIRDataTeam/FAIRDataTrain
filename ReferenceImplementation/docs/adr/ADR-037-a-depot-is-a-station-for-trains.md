# ADR-037 — A Depot is a station for trains, and a creator is asked through their Gateway

| | |
|---|---|
| **Status** | **Accepted**, 13 September 2026 — answered by Luiz in the Q25 interview. The answer as given is in `OPEN-QUESTIONS.md` under Q25; anything here beyond it is drafting, and is marked where it goes furthest. |
| **Deciders** | Luiz Olavo Bonino da Silva Santos |
| **Relates to** | ADR-008 (human-in-the-loop approval), ADR-011 (three parties, three credentials), ADR-018 (natural persons as controllers; the Individual Gateway), ADR-026 (outcome vocabulary), ADR-029 (the Depot is the authority for a train), ADR-032 (where a machine may not grant it may not refuse), ADR-036 (a train's three parties); **Q25** |
| **Companion** | ADR-036, which settled who the parties are; this settles what happens when one of them has to be asked |

## Context

ADR-036 gave the Depot a write surface and made taking a train an evaluation of the creator's
licence — an `odrl:Offer` over the train as an asset, judged by the same rule a station uses for
data (`protocol/agreement-derivation.md`, unchanged, and the cross-evaluator test that holds the
two implementations to one rule).

`fdts:OfferShape` admits `fdt-p:requiresManualApproval` on any offer, a creator's licence
included. A station meeting that flag parks the case and shows it to the data controller. A Depot
implementing ADR-036 had nowhere to put it, and ADR-032 made the gap sharp rather than merely
awkward: where a machine may not grant it may not refuse either, so a Depot facing the flag may
not conclude the agreement **and** may not say the licence refused, because the creator has not
refused anything. `train-depot-api.yaml` offered three answers — 201, 403 and 409 — and none of
them is *nobody has decided*.

The interim default (Q25) was 403 with the distinction carried in words: *this licence is not one
a Depot can conclude*, naming the clause, never using the word Refused. It was chosen on the
reasoning that **a Depot has nobody to ask** — the creator is somewhere else entirely, and the
Depot's operator is the wrong party by construction, holding the bytes and answerable for nothing
about the code.

That reasoning was wrong, and it was wrong in an instructive way. Both of its premises are true.
The conclusion does not follow from them, because **a station's data controller is also somewhere
else, is also not the operator, and is asked anyway.** Being elsewhere is the normal condition of
the party who decides; reaching them is what the controller surface and the Individual Gateway
exist for. "There is nobody to ask" was a statement about what had been built into the Depot, not
a fact about the architecture.

## Decision

**A Train Depot is a station whose assets are trains, and a Train Creator is asked the way a data
controller is asked — through their own Individual Gateway.**

1. **The shape is the same.** A Depot holds assets that a party controls, publishes conditions
   over them, negotiates access on arrival, and issues one agreement per grant. That is a station
   (ADR-001, ADR-007, ADR-014) with trains where the data would be. The Depot's *creator* is the
   station's *data controller*; the Depot's *operator* is the station's *station owner*; ADR-011's
   separation of the two carries over unchanged, and so does its rule that each party gets its own
   credential.
2. **`POST /trains/{train}/take` gains a fourth answer: the negotiation is pending.** Nothing has
   been granted and nothing has been refused. This is the state ADR-032 requires and the contract
   could not express, and the response says so in ADR-026's own vocabulary — *pending* is not
   *Refused*, and a consumer must never be shown one as the other.
3. **The creator is notified through their Individual Gateway** (ADR-018), exactly as a natural
   person who controls data receives a request to consent. The Depot sends the case; the Gateway
   is the creator's agent and the place the creator already looks.
4. **The Depot keeps the case until it is decided**, and keeps it as a station does: the pending
   request, what the asker asked for, what the licence requires, and the Depot's own recommendation
   with the evidence behind it (ADR-032 — withholding the analysis because a machine may not
   decide leaves the person with less basis, not more independence).
5. **A decision is an event with a justification** (ADR-027), and the creator–owner agreement
   records the mode that applied and who decided under what authority, as Q13 decision 3 requires
   of a station.

### What this does *not* say

It does not say a Depot is a Data Station in FDT-O's type hierarchy, and nothing in the ontology
changes here. A train is an executable asset and never a `dcat:Dataset` (ADR-020); a Depot
serving a catalogue of trains is not serving a catalogue of data, and a registry harvesting both
must keep them apart. The claim is about the **shape of the interaction** — control, conditions,
negotiation, approval, agreement — not about the class of the thing.

*Drafting beyond the answer:* points 2, 4 and 5, and the paragraph above, are the draft's
reading of what follows from "a Depot is station-shaped". The answer given was the analogy and
the routing through the Gateway.

## Alternatives

| | Why not |
|---|---|
| **403 with the distinction in words** (the interim default) | It spends a refusal code on a case that is not a refusal, and relies on every client reading the prose to avoid reporting a Refused that nobody decided. It was the least-wrong answer inside the contract as it stood, which is a fact about the contract. |
| **202 and the asker approaches the creator out of band** | Honest about the state and silent about the mechanism. It makes every creator invent their own approval channel, and makes the ecosystem's one auditable decision path stop at the Depot's door. |
| **Forbid the flag on a train offer by shape** | Considered, and it is the tidy answer: a licence needing a person is a licence that is not published through a Depot, and "email me" is a legitimate way to license software. It was rejected because it solves the problem by removing the case rather than by serving it, and the case is real — a creator who wants to know who is running their train before they run it is asking for something reasonable. |
| **The Depot's operator decides** | The operator holds the bytes and is answerable for nothing about the code (ADR-036). Letting them conclude a licence over somebody else's work is the precise inversion ADR-011 exists to prevent. |

## Consequences

- **`train-depot-api.yaml` gains a pending state and an approval surface**, and the Depot gains
  somewhere to keep a case. `fdt-commons` changes first, under the change protocol.
- **The Depot gains a party surface it did not have** — a creator's credential, distinct from the
  operator's admin token, on the ADR-035 pattern.
- **The Individual Gateway gains a second kind of request.** It carried consent requests about a
  person's data; it now also carries approval requests about a person's train. The Gateway's own
  work package has to say whether those are one queue or two.
- **A Depot now holds a record of who asked for what**, which the Q25 default was written to
  avoid. That cost is accepted here on the ground that it is the same record a station holds for
  its controllers, held for the same reason, and that the alternative is not *no record* but *no
  answer*. It does not weaken ADR-036's separate decision that a Depot notifies nobody about a
  **withdrawal**: that would be a list of who is interested, which nobody supplies and nobody can
  consent to. This is a list of who asked, which is what asking is.
- **The cross-evaluator test grows.** One rule, two evaluators already holds the station's and the
  Depot's licence evaluation to a single implementation of the derivation rule; the approval path
  is now the second thing they have in common, and the test should say so before the second
  implementation of it exists.
- **Q25's residual question is closed by the answer**, not left open: a creator's offer may carry
  the flag, because there is now a party to meet it.

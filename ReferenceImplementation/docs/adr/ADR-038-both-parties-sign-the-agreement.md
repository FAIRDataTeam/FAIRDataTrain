# ADR-038 — Both parties sign the agreement

| | |
|---|---|
| **Status** | **Accepted**, 13 September 2026 — answered by Luiz on Q12's remaining half. The answer as given is in `OPEN-QUESTIONS.md` under Q12; anything here beyond it is drafting, and is marked where it goes furthest. |
| **Deciders** | Luiz Olavo Bonino da Silva Santos |
| **Relates to** | ADR-007 (ODRL), ADR-011 (controller ≠ operator), ADR-014 (one agreement per hop), ADR-027 (every decision is an event), ADR-028 (counter-signed agreements — **extended here**), ADR-035 (standing at a station); `protocol/agreement-derivation.md` §6; **Q12** |

## Context

Q12 required an agreement to be immutable for later audits and accessible to both parties, and
settled most of what that needs: granted terms and evidence, digests pinning what it was derived
from, and two-party retention — the Handler fetches and keeps it at `negotiation.active`.

ADR-028 added the mechanism that makes retention worth something: the **train owner** signs the
canonical form of the agreement without its signature node, with a real Ed25519 key, and
publishes the public key in a JWKS beside its self-description, so a verifier needs nothing from
the station. *A party is not a witness.*

One side was left unsigned, and it is the side where the custody problem lives. **The station
writes the agreement, keeps the record, and is the party the controller is trusting.** A digest
protects the two parties from each other; a single signature protects the party who did not sign
from the party who did. Nothing protects against the station, and the station is the one holding
the pen.

Q12 recorded the alternatives as an append-only log or a counter-signature, and marked it as
needing an ADR rather than a shape: `AgreementShape` can express digests and cannot express
custody.

## Decision

**An agreement carries a signature from each party to it.** Not a signature and a counter-
signature: two signatures, one per side, over the same canonical form.

1. **The assignee signs**, as ADR-028 already has it — the train owner, Ed25519, over the
   canonical agreement without its signature nodes (`agreement-derivation.md` §6), key published
   in the Handler's JWKS.
2. **The assigner signs too.** The assigner of the agreement is the **data controller** whose
   conditions it was derived from. Where the controller holds their own key, the controller's
   signature is what binds. Where they do not, the **station signs as their agent**, with the
   station's key.
3. **The agreement records which of those two happened.** *The controller signed* and *the station
   signed for the controller* are different facts with different weight, and an agreement that let
   them be confused would make the mechanism worth less than no mechanism: a supervisory authority
   reading a signature has to know whether the party or the party's software asserted it. So a
   signature names its signer, its role — assigner or assignee — and, where it is an agent's, the
   party it was made on behalf of.
4. **`fdt-p:countersignature` generalises to `fdt-p:signature`**, with the role and the on-behalf-of
   recorded on it. The existing counter-signature is the assignee's instance of it. This is a
   contract change and goes through the change protocol: `fdt-commons` first, `VERSION` bump,
   `FINDINGS.md` line, validators green, then consumers.

*Drafting beyond the answer:* the answer was that both parties sign. Points 2's fallback (the
station signing as the controller's agent), 3 and 4 are this draft's reading of what it takes to
mean it — in particular, point 3 exists because a controller without a key is the ordinary case
today, and an agent's signature presented as a party's would quietly restore the problem.

## Alternatives

| | Why not |
|---|---|
| **Digests plus two-party retention alone** (what is built) | Real protection between the two parties and worth nothing to a third who kept nothing — a data controller asking under what terms their data was touched, or a regulator, must decide which of two documents is the original with no way to tell. That third party is the one the record exists for. |
| **An append-only log with a periodically published root** | Strongest: a rewrite becomes detectable by anyone, with no key distribution at all. It is also infrastructure — a log, a publication schedule, a verifier — and it answers a question about *the station's whole history* when the question asked was about *this agreement*. Not excluded later; it composes with signatures rather than replacing them. |
| **The controller signs, always** | The right end state and not reachable yet: it needs every controller to hold a key and a console that can use it, and a station whose controllers have no keys would be unable to conclude any agreement at all. Point 2's fallback is the bridge, and point 3 stops the bridge from being mistaken for the destination. |
| **The station signs, always** | Simple and circular. The station is a party; its signature over its own record is the assertion under dispute. |

## Consequences

- **`fdt-commons` gains `fdt-p:signature`, its role, and its on-behalf-of**, with
  `fdt-p:countersignature` becoming the assignee's case of it. `AgreementShape` requires both
  sides, and `tools/derivation.py` checks them — a shape that required only "at least one
  signature" would pass every unilateral agreement.
- **The station needs a signing key** in its configuration, and a way to publish the public half,
  on the ADR-028 pattern. A station with no key configured cannot conclude agreements, and should
  say so at startup rather than at the moment somebody's visit fails.
- **A controller key becomes a real thing to design**, with S4 and S5 as the surfaces that would
  use it. It is not built here and it is the reason point 3 exists.
- **Verification is symmetric**: a verifier who holds the agreement and can reach two JWKS
  documents can check it without asking either party for anything. That is the property; the rest
  is bookkeeping.
- **Existing fixtures change.** `agr-m1-01` and the other published agreements carry one signature
  today. Regenerating them is part of the contract change, and the counter-example — an agreement
  signed by one side only — is worth having, because it is what every agreement in the repository
  currently looks like.

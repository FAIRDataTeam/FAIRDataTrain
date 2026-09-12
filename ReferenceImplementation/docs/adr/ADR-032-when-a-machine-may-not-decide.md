# ADR-032 — Where a machine may not grant, it may not refuse either

| | |
|---|---|
| **Status** | **Accepted**, 13 September 2026 — decided by Luiz in the M5 decision interview. |
| **Deciders** | Luiz Olavo Bonino da Silva Santos |
| **Relates to** | ADR-007/008 (negotiation and manual approval), ADR-011 (controllers), ADR-017 (networks), ADR-026 (outcomes), ADR-027 (every decision is an event); `fdt-commons` Q13, findings 26, 27 |

## Context

Some authorisation may happen automatically; in other settings regulation does not permit an
automated authorisation, and the system must present the case to a human. Q13 established where
that rule lives — **on the network membership**, with trusted issuers and governance (ADR-017),
not on the controller's offer, because the controller can edit their own offer and a regulator's
rule is not theirs to relax.

Two sub-questions stayed open. Whether a machine forbidden to *grant* may still *refuse*. And
what must be recorded when a human decided.

The first is a legal question wearing technical clothes. An automated refusal is still an
adverse decision taken by a machine about a person's or an institution's request.

## Decision

**1. In a network that bars automated authorisation, a machine may not refuse either.** Both
directions are adverse decisions and both go to a human.

**2. The station still does the work, and presents it.** It evaluates the request against the
conditions and produces a **recommendation with its evidence** — "the conditions require a
research purpose and the train declares a commercial purpose" — for a person to decide on. The
machine's analysis is not withheld because the machine may not decide; withholding it would
leave the human with less basis, not more independence.

**3. The agreement records four things beyond `approval.controller` and `approval.expiresAt`:**

* **the mode and the rule** — automatic-permitted, human-required-by-regulation, or
  human-by-controller-preference — and the specific rule that imposed it, so nobody has to
  guess later whether a human was legally necessary or merely preferred;
* **who decided and under what authority** — a delegate, a data access committee, an ethics
  reference — as a pseudonym the station can resolve in its own audit log and the agreement
  cannot, since the agreement is immutable and held by both parties;
* **what they were shown** — the pinned match summary and the system's recommendation at the
  moment of decision (finding 27), without which no decision can be reviewed, because nobody can
  tell whether the person saw the constraint that mattered;
* **whether they followed or departed from the recommendation**, and their stated reason if they
  departed.

**4. Q13's earlier decisions stand.** A human may supply evidence the machine lacked — that is
the ordinary case, not an override. A human may not override a prohibition that fired: the
controller's own instruction about their own data is not a delegate's to countermand.

## Alternatives

**Refusals may be automatic** — the flag governs granting only. This was the code's default and
the more workable reading: a refusal is reversible by resubmission, carries a stated reason, and
discloses nothing. Rejected because the regime that bars automated authorisation is generally
barring automated adverse decisions, and reading it narrowly is the implementer's convenience
rather than the regulator's meaning.

**Automatic only when unambiguous** — a machine may refuse on a clear-cut ground (a prohibition
fired, the network does not match) but not on an eligibility fact it could not verify. Tempting,
and it matches how the failures actually arise. Rejected because the station would be
classifying its own grounds as clear-cut, and that classification is exactly what a disappointed
consumer would dispute.

## Consequences

* **The PDP's output is a recommendation, not only a verdict.** WP-1.3's evaluator gains a mode
  in which it decides nothing and explains everything. The explanation is the same analysis
  either way, which is the point.
* **ADR-026 needs an outcome for it.** "Recommended refuse, awaiting a human" is neither Refused
  nor Rejected — no controller has decided anything yet — and the existing pending-approval
  state was framed around grants. The vocabulary has to carry an adverse recommendation that is
  not yet a decision, and the console must not label it as one.
* **Fan-out gets slower in restricted networks, deliberately.** Every non-matching request there
  becomes a queue item. That is the cost of the regime and the reason a network chooses it.
* **M2 demonstrates both regimes.** WP-5.4 puts stations in at least two networks: one permits
  automated decisions and refuses the commercial request automatically, the other bars them and
  produces a recommendation awaiting a person. The difference becomes visible rather than
  asserted.
* **The controller API must carry all of it** — the recommendation, the evidence, the decision,
  and what was shown. That API still has no contract anywhere (acceptance sweep, item I), and
  this ADR sets what it has to carry.

# ADR-035 — Standing: who may act at a station, and on whose behalf

| | |
|---|---|
| **Status** | **Accepted**, 13 September 2026 — answered by Luiz in the Q21 interview. The twelve answers as given are listed in `OPEN-QUESTIONS.md` under Q21; anything here beyond them is drafting, and is marked where it goes furthest. |
| **Deciders** | Luiz Olavo Bonino da Silva Santos |
| **Relates to** | ADR-010/017 (visit tokens, networks), ADR-011 (three parties, three credentials), ADR-012 (agreements), ADR-026 (outcome vocabulary), ADR-027 (every decision is an event), ADR-031 (credentials prove what metadata names), ADR-032, ADR-034 (narrowing); Q13, **Q21** |
| **Companion** | ADR-036, which does the same for a train's parties and the Depot |

## Context

Q21 was opened as "who may change how a station is configured?" and grew, because every screen
that *writes* turned out to need the same missing thing. By the end of WP-5.5 it blocked four:
the Depot's publish and withdraw surface, station **S4** (the access-condition builder), station
**S5** (agreement detail), and **H2's dispatch step** — H2 composes a `fdt-run:Plan` and stops,
because starting a run means dispatching a train on somebody's behalf and nothing said who may
do that for whom.

The placeholder in force was a bearer token per party, configured out of band
(`FDT_STATION_ADMIN_TOKEN`, `FDT_STATION_CONTROLLER_TOKENS`). It is the right *shape* — ADR-011
already says three parties ask three different things of a station and each needs its own
credential — and it says nothing about where any of those credentials comes from, whether the
three are three people, or what happens when one is taken away.

## Decision

### 1. Identity has two sources, split by the question being asked

**Anything that crosses organisations** — a data consumer, a data controller, a train creator, a
train owner — is identified by **the network's trusted issuer**, the same source that issues
visit tokens (ADR-031, `fdt-net:trustedIssuer`). This is what makes a claim about a party
checkable by someone who has never met them, which is the whole reason a network has a trust
anchor at all.

**Whoever administers a component** is identified by a **credential configured out of band** on
that component. "Who may restart this station" is not a network concept, and a station that
could not be administered while its network's identity provider was down would have made an
operational dependency out of a governance one.

A station in two networks therefore has two issuers for cross-organisation claims and one local
credential for its own administration. That is not a compromise; the two questions have
different answers because they are different questions.

### 2. Operator, controller and auditor are roles, and one principal may hold several

A small station is administered by the person who also controls its data. Software that made
that impossible would be describing an institution rather than a protocol.

Separation of duties remains available and is a **deployment policy**: a deployment may require
distinct principals, and where it does, the station publishes that it does, so a controller can
see whether anyone else can change their conditions. What the software enforces is that each
role's *surface* is separate (§4), not that the people are.

### 3. A visit may be dispatched under either kind of credential, and the station records which

An organisation credential naming a human agent, or a person's credential carrying an
affiliation claim. Both are accepted, and **the station records what was presented**, verbatim,
in the visit's events.

"Verbatim" is the load-bearing word, and it is ADR-026's rule one level up: a station that
normalised both forms into one would be reporting something nobody said. A completeness
statement names the requester as they presented themselves, and a controller's queue shows the
two kinds of requester as two kinds, because they are.

### 4. Access conditions and agreements belong to the controller, for their own datasets only

S4 and S5 are the controller's screens. An operator may see **that** conditions exist and
**that** agreements were reached — they operate the machine and must be able to tell it is
working — and may not see what they say or change them.

This is ADR-011's separation made enforceable rather than descriptive. It holds even where one
person holds both roles: they act as one or the other, with the credential for that role, and
the event says which.

### 5. A controller may narrow the decision mode for their own data, and never widen it

ADR-034 established that a station's decision mode narrows and never widens what its network
permits. This extends the same rule by one step, in the same direction:

> **network ≥ station ≥ controller**, each able to narrow and none able to widen.

A controller may require that decisions about *their* datasets go to a person, even where the
network and the operator would both allow a machine. They cannot make a station more automated
than its operator chose, and neither can make it more automated than its network permits.

Nobody can be moved into a more automated regime than they accepted. That is the property, and
it is the same property at all three levels.

### 6. Revocation does not reach into a visit that is already running

A withdrawn credential — an operator leaves, a controller's mandate ends — affects new requests.

- **A visit already running continues.** An agreement was reached and a visit is not
  re-authorised mid-flight. Ending it would produce a run that failed for a reason having
  nothing to do with the data, reported to a consumer in ADR-026's vocabulary as though the
  station had decided something about their request.
- **A queued approval waits for whoever holds the role now**, and keeps the rule it arrived
  under — which is what the station already does, and this makes it normative.

## What here is drafting rather than an answer

Marked so that it can be disagreed with separately from the decisions.

- **§2's "a deployment may require distinct principals, and publishes that it does."** The answer
  was that the three are roles and one principal may hold several. Making separation of duties a
  *declarable* deployment policy, and making a station publish which regime it is under, is
  drafting — it follows from ADR-032's principle that a controller should be able to see which
  regime is deciding about their data, but it was not asked.
- **§3's "verbatim."** The answer was that either credential form is accepted and the station
  records which. That a station must not normalise the two into one is ADR-026's rule carried one
  level up, and it is an inference.
- **§5's precedence chain.** "Narrow, never widen" was the answer; writing it as
  network ≥ station ≥ controller, and stating that the property is the same at all three levels,
  is drafting.

## Alternatives considered

**One identity model for everything, from the network's issuer.** Cleanest to audit. Rejected
because it makes administering a station depend on network governance being reachable, and
because a station in two networks would have two sources of operator identity for one machine.

**Three principals, always distinct.** Strongest governance story. Rejected because the
single-operator station in the mock-ups could not then exist, and the software would be refusing
a deployment that is perfectly legitimate and extremely common.

**One dispatch credential form.** Simpler to validate. Rejected in both directions: an
organisation-only form makes "who ran this train against my data" unanswerable beyond the
organisation; a person-only form makes every station evaluate an affiliation claim to know who
its agreement is with.

**Either role may set conditions, with an event naming who (ADR-027 as the whole control).**
Simplest to build, and accountability after the fact is real accountability. Rejected because a
controller would find out *after* their conditions had been changed, and the thing ADR-011
separates is precisely the power to decide about other people's data.

**A controller's lever is only their offer.** Conditions a machine cannot evaluate already go to
a person, so a controller can get human review by expressing it as a condition. Rejected as
indirect: it makes a plain requirement into a puzzle, and leaves the controller unable to *see*
which regime is deciding about their data — which is what ADR-032 exists to make visible.

**Immediate revocation everywhere.** Rejected: a departing employee could end other people's
runs, and the consumer would be told in outcome words that misdescribe why.

## Consequences

**What this unblocks.** S4 and S5 can be built, against the controller credential ADR-011
already names. H2's dispatch step can be built once a dispatch credential exists in a form the
console can present (§3).

**What has to be built.** A role is now something a component reads from a credential rather
than infers from which token was used, so each component needs the mapping from an issuer's
claims to a role — and the placeholder tokens stay as the degenerate case of it, which is what
makes a testbed possible. The station gains a per-dataset decision-mode narrowing set by the
controller, evaluated after the operator's and the network's (§5), and each change is an event
with a justification (ADR-027).

**What it costs.** Two identity sources means two failure modes, and an operator debugging a
station has to know which one they are looking at. The separation in §4 means a station cannot
be configured end to end with one credential even where one person holds both roles — they have
to act as each in turn. That is the point, and it will be reported as friction.

**What is still open.** *Delegation*: whether a controller may delegate their standing to a
person or to the Individual Gateway acting for them (WP-2.4). *The auditor*: whether it is a
real third party with a read surface across controllers, or only a way of describing the event
log. §2 names three roles; only two of them have surfaces here.

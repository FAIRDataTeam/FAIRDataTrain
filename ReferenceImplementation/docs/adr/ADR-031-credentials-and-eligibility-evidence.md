# ADR-031 — A credential proves what metadata only names

| | |
|---|---|
| **Status** | **Accepted**, 13 September 2026 — decided by Luiz in the M5 decision interview. |
| **Deciders** | Luiz Olavo Bonino da Silva Santos |
| **Relates to** | ADR-010 (identity — this amends its v1), ADR-011 (controllers), ADR-017 (networks), ADR-020/029 (the train and its owner); `fdt-commons` Q14-C, finding 51 |

## Context

M2's scenario turns on a request being refused because its purpose is commercial. To decide
that, a station must know the requesting party's class — `fdt-p:consumerType`, an Eligibility
constraint — and **nothing said where that fact comes from**. It was recorded as Q14-C.

Two things are true at once. FDT-O already says who is responsible for a visiting train:
`fdt-o:TrainOwner` is defined as the agent on whose behalf the train visits a station, and it is
part of the train's metadata. And a party's own metadata is not evidence about that party.

That second point is not a quibble. `fdt-commons` finding 51 had just removed exactly this
pattern from the network case: requiring a policy to carry its network's description meant a
train's owner would have republished who a network trusts, letting the party being judged
nominate its own verifier. Reading `consumerType` out of Depot-published train metadata would
reintroduce the same inversion one layer down.

ADR-010 names OIDC bearer tokens as v1 and DCP presentations as v2. Verifiable credentials were
always the destination; the question was whether v1 waits.

## Decision

**1. Metadata names; a credential proves.** A train's metadata names the responsible party
(`fdt-o:TrainOwner`). That is a *reference*, not evidence, and a station believes nothing on the
strength of it. The binding is established by a **W3C Verifiable Credential** presented with the
visit, proving that the caller acts for that party and carrying the attributes eligibility
depends on.

**2. A mismatch is a rejection at PEP 1.** If the party the credential proves is not the party
the train's metadata names, the visit is Rejected — not silently preferred one way or the other.

**3. Verifiable credentials enter v1, for eligibility attributes only.** OIDC keeps doing
authentication, which it already does and which PEP 1 already verifies against the issuers the
network trusts. Credentials carry the eligibility facts — consumer type, legal basis — which are
precisely the facts a station cannot verify today and must therefore fail closed on
(`agreement-derivation.md` §5).

**4. ADR-010's v2 is unchanged.** Full DCP presentation, carrying identity as well as
attributes, remains the destination. This starts it where it pays for itself.

## Alternatives

**A verified token claim.** Have the network's identity provider assert the organisation class
in the token PEP 1 already verifies. Cheapest by far, and evidence from a trusted issuer.
Rejected because it constrains every identity provider in every network to carry FDT's
eligibility vocabulary, and it puts attribute assertion in the hands of whoever runs
authentication rather than whoever is competent to accredit.

**Self-asserted, failing closed.** Let the consumer state it in the ODRL request, treat it as
unevidenced, and require a human to supply the evidence. This is what the code does today and it
is not wrong — but it makes every commercial-purpose case a pending approval, which is a poor
use of a person for a fact a credential can carry.

**From the network membership record.** The network authority records each party's class and the
station reads it. Keeps judgement with the governance body. Rejected as the primary mechanism: a
third lookup on the decision path, a stale record silently changes an outcome, and the network
authority becomes an operational bottleneck for every new consumer.

**Full DCP in v1.** Architecturally clean and where this ends up. Rejected for now only because
nothing in the testbed issues a credential, so M2 would block on building an issuer, a holder
and a verifier before any of its own content.

## Consequences

* **Q14-C closes.** WP-1.3's second clause and M2's commercial refusal have a specified source
  for `consumerType`.
* **Something must issue credentials in the testbed.** A fictional accreditation issuer, its
  keys, and a holder the Handler can present from. New work in M5 or M2, and it is the first
  piece of the DCP path.
* **The evidence block gains a credential reference.** `agreement-derivation.md` already records
  eligibility facts, who attested them and when; an attestation can now be a credential, and the
  agreement should say which one and who issued it — without copying the raw claims into a
  document that is immutable and held by both parties.
* **PEP 1 gains a check it did not have**: the proven party against the named party. It needs a
  counter-example fixture, like every other checkpoint rule.
* **A station that cannot verify a credential must fail closed**, as it does for any unevidenced
  eligibility fact. A verifier that quietly accepts an unverifiable presentation would be worse
  than not having one.

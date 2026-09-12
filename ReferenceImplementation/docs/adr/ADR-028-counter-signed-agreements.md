# ADR-028 — Agreements are counter-signed by the train owner

| | |
|---|---|
| **Status** | **Accepted**, 13 September 2026 — accepted by Luiz in the M5 decision interview. Proposed 12 September 2026, chosen as Q14-B; drafted because it adds a mechanism the architecture did not have. Adoption into `fdt-ecosystem-architecture.md` follows. |
| **Deciders** | Luiz Olavo Bonino da Silva Santos |
| **Relates to** | ADR-007/008 (negotiation), ADR-010 (identity), ADR-014 (one agreement per hop), ADR-027 (every decision is an event); `fdt-commons` findings 23–25, 28; `protocol/agreement-derivation.md` §6 |

## Context

The requirement is that an access agreement be **immutable for later audits** and **accessible
to the station and the train owner**. Q12 settled most of what that needs: the agreement carries
the granted terms and the evidence that justified them, pins what it derived from by digest, and
is fetched and kept by the Train Handler at `negotiation.active`, so both parties hold a copy.

One half was left open, and it is the uncomfortable half. **The station writes the agreement and
is a party to it.** A digest makes a rewrite detectable by whoever kept the original — that is
real protection between the two parties, and it is worth nothing to a third party who kept
nothing and must now decide which of two documents is the original. A data controller asking
"under what terms was my data touched" is exactly such a third party, and so is a supervisory
authority.

Nothing in ADR-010 helps here. OIDC access tokens prove who *called*; they are short-lived
bearer credentials, they are not held by the party, and they cannot be presented later to show
what that party agreed to. Proving who *called* and proving who *agreed* are different
questions with different lifetimes.

## Decision

**The train owner counter-signs the agreement, with a real signing key.**

1. The station concludes the agreement and emits `negotiation.active`.
2. The Handler fetches it, checks that its terms are what it asked for, and **signs the
   canonical form of the agreement without the signature node** — URDNA2015 canonical N-Quads,
   sorted, sha256 (`agreement-derivation.md` §6) — with an **Ed25519** key.
3. The station stores the signature on the agreement as `fdt-p:countersignature`, naming the
   key by IRI.
4. The Handler **publishes the public key** in a JWKS beside its self-description, so a verifier
   needs nothing from the station: a party is not a witness.

An agreement without a counter-signature remains valid and enforceable — the controller granted
access, and that does not depend on the consumer's cooperation. It is a *one-party* record, and
`GET /agreements/{id}` says which kind it is.

## Alternatives

**Digests and two-party retention alone** (Q12's decision, the status quo ante). Simplest, and
sufficient against accident and against a station that edits its records without the Handler
noticing. It does not survive the case where the two parties disagree in front of a third:
each holds a document, neither can prove which came first.

**An append-only hash chain per station** — each agreement records the digest of the previous
one. Cheap, and it makes a silent edit break everything after it. But a chain is only as good as
an external witness to its head, and v1 has nowhere to publish one; it would offer more
assurance than it delivers.

**Rejected as insufficient, not as wrong.** Both remain compatible with this decision and either
could be added later.

## Consequences

- **Handlers need signing keys, which v1 did not require.** Key generation, publication in a
  JWKS, rotation and revocation become part of the Handler's deliverables (WP-1.5, WP-2.3), and
  the key's lifecycle is longer than a token's. This is the real cost of the decision.
- **Two key systems exist side by side**: OIDC tokens for authentication at PEP 1, Ed25519 keys
  for agreement signatures. They are deliberately not merged; merging them would tie the ability
  to prove an old agreement to the lifetime of an access credential.
- **Verification is available to anyone** holding the agreement and able to fetch the Handler's
  JWKS — including a controller through the Individual Gateway, which is where it matters.
- **A station cannot forge a counter-signature**, and cannot quietly alter a counter-signed
  agreement: any change moves the canonical digest and the signature stops verifying.
- **A station can still refuse to show an agreement at all.** This decision addresses
  falsification, not suppression. Suppression is what the Handler's own retained copy addresses.
- `tools/derivation.py` verifies signatures on every `make check`, against the published key —
  not merely their presence. Mutation-tested: one character changed in the signature, or any
  term changed after signing, and the check fails naming which.

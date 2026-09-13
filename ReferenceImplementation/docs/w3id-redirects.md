# The `w3id.org/fdt/` redirects — drafted, not opened

**Q1.** Four IRIs are referenced by every shape, every example, the ontology and one JSON Schema,
and none of them resolves. `FAIRDataTeam/w3id.org` exists and is public, so this is redirect
configuration rather than new infrastructure.

**Decided 13 September 2026: draft the mapping now, open nothing yet.** Two separate reasons, and
they are worth keeping apart because they lift at different times.

* **`fdt-o#` is not blocked on Q6** — it is served from `FDT-O`, which is already public. It is
  blocked on **Q5**: FDT-O's `master` still carries the pre-D2 ontology, whose namespace and terms
  the shapes no longer match. A redirect to `master` would resolve, which is worse than not
  resolving: a stranger gets a confident answer that disagrees with every shape and fixture in the
  project. It waits for PR #1 to land, and then points at a **tag**, not a branch.
* **The other three are blocked on Q6** — they come from `fdt-commons`, which stays private. A
  redirect into a private repository answers 404 for everyone outside, which reads as a broken
  contract rather than an unpublished one.

Nothing here is published. This file exists so that the mapping is written down and reviewed while
the reasoning is fresh, rather than reconstructed by whoever revisits Q6.

## The mapping

| IRI | Referenced by | Serve from | Unblocked by |
|---|---|---|---|
| `https://w3id.org/fdt/fdt-o#` | every shape, every example, the ontology itself | `FDT-O/ontology/fdt-o.ttl` at a tag | **Q5** (PR #1 lands, then tag) |
| `https://w3id.org/fdt/fdt-o` | `vocab/fdt-profile.ttl`'s `owl:imports` | the same file | **Q5** |
| `https://w3id.org/fdt/run/context.jsonld` | `examples/plan-time-to-groin.jsonld` | `fdt-commons/contexts/fdt-run.context.jsonld` | **Q6** |
| `https://w3id.org/fdt/schemas/*` | `schemas/run-state.schema.json`'s `$ref` (finding 15) | `fdt-commons/schemas/` | **Q6** |

The first two are one file reached two ways: `fdt-o` is the ontology document and `fdt-o#` is the
term namespace, which is the ordinary hash-namespace arrangement and needs no special handling
beyond content negotiation.

## What the redirect has to get right

**Content negotiation, not a single target.** A browser asking for `text/html` and a reasoner
asking for `text/turtle` must not receive the same bytes. `w3id.org` supports this through
`.htaccess` rewrite rules keyed on `Accept`; the Turtle is the normative artefact and HTML
documentation is optional and does not exist yet, so until it does the honest configuration serves
Turtle to everybody rather than redirecting HTML requests to a page that is not there.

**A tag, never a branch and never `HEAD`.** An ontology IRI is cited by documents that outlive it.
A redirect that follows a moving branch means the meaning of `fdt-o:hasControllingRights` can
change under a fixture that was validated against it, and nothing anywhere would report that.

**Raw content, with the right media type.** `raw.githubusercontent.com` serves `.ttl` as
`text/plain`, which rdflib and pySHACL will parse only if told the format out of band — so a
consumer following the IRI and asking for `text/turtle` gets something it cannot use. This is the
one part of the mapping that is not a one-line rewrite, and it is the part to check first when
somebody reports that the IRI "resolves but does not work".

## What does not change

Validators resolve all four locally and never touch the network, so `make check` is offline and
deterministic (`fdt-commons` finding 13). That stays true after the redirects land: CI must not
start depending on `w3id.org` being up, and a validator that silently fell back to the network
would be a validator whose result depends on somebody else's DNS.

## What is still owed when this is opened

WP-0.2's second acceptance clause — "`fdt-commons` profile `owl:imports` resolves" — cannot pass
until the first two rows land, and **WP-4.4** ("a station implemented only from `fdt-commons` plus
the conformance material passes the suite") cannot be demonstrated by a third party until all four
do. Both are unrunnable for a reason that is a decision rather than a defect, and both should say
so where they are recorded rather than reading as work nobody has done.

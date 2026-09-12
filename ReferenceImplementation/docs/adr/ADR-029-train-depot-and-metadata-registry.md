# ADR-029 — The Train Depot, and one metadata registry for stations and trains

| | |
|---|---|
| **Status** | **Accepted**, 12 September 2026 — decided by Luiz in the WP-1.5 session. Drafted here because it changes the component set the architecture names, and because the rename reaches into FDT-O. |
| **Deciders** | Luiz Olavo Bonino da Silva Santos |
| **Relates to** | ADR-017 (networks), ADR-020 (trains as contracted assets), ADR-010 (identity), ADR-028 (counter-signed agreements); WP-3.4 (Directory v0 and Garage v0); `fdt-commons` findings 34, 36, 42 |
| **Supersedes** | the "Train Garage" and "Station Directory" of `fdt-ecosystem-architecture.md` as two separately-designed services |

## Context

The plan names two discovery components and designs them apart: a **Train Garage** publishing
trains, and a **Station Directory** listing stations. Building a testbed made the question
concrete — what are these two applications, and how do they differ? — and the answer turned out
not to be "two catalogues of different things".

Two separate facts came out of it.

**They are not the same kind of component.** One of them is consulted when a decision is taken
about somebody's data. PEP 1 rejects a train whose descriptor digest does not match the one the
train's publisher states; PEP 2 hashes the payload bytes and compares them with the digest the
agreement pinned (`fdt-commons` findings 36, 42, and WP-1.4). A wrong answer there is a security
failure. Nothing about a station listing has that property: a stale or missing entry gives a
Handler a poor choice of station, and every decision that follows is still taken at the station,
against a token, under an agreement.

**Discovery is one problem, not two.** Once the authoritative half is removed, what is left —
"find the stations in this network that support SPARQL", "find trains for this theme" — is a
metadata registry indexing records published by other parties. That is the FDP Index / FAIR
Discovery pattern, and it already indexes whatever resource types the publishing FDPs define:
the ERDERA VP Index carries biobanks and guidelines alongside datasets. Stations and trains are
two more such types, not a reason for a second kind of component.

## Decision

**1. The Train Garage is renamed the Train Depot**, and the rename goes all the way into the
ontology: `fdt-o:GarageCatalog` becomes `fdt-o:DepotCatalog`, `fdt-p:trainGarage` becomes
`fdt-p:trainDepot`. These are IRIs no `w3id.org` redirect publishes yet (Q1), so this is the one
moment the change costs nothing downstream. It is a breaking change to FDT-O, taken deliberately
and before publication rather than never.

**2. The Depot is an authority.** It holds trains: the payload bytes, `fdt-o:artifactDigest`,
the declared parameters, the declared output schema, the train owner's own `odrl:Offer` over the
train as an asset, and the owner's public signing keys (ADR-028). A station resolves a train
against a Depot at PEP 1, and what it gets back has to be right.

**3. The Directory is a metadata registry, and only that.** It harvests and indexes the records
Depots and Stations publish. It is not a trust anchor and does not need to be: membership of a
network is proven by the credential in the token PEP 1 verifies against the issuers the network
trusts (ADR-010/017), and eligibility is established from evidence at negotiation. A Directory
entry is a discovery hint. Nothing may be granted on the strength of one.

**4. Trains stay `fdt-o:Train`, and `fdt-o:Train` becomes abstract.** Only its concrete
subclasses — `fdt-o:SPARQLTrain`, `fdt-o:FHIRTrain`, `fdt-o:DockerTrain` and the rest — have
instances, so a train is classified as exactly what it is and `fdt-o:Train` is entailed rather
than asserted. `:TrainShape` already requires a concrete type; the ontology gains the axiom that
makes it true rather than merely checked.

**5. A train *plays the role of* `odrl:Asset`; it is not a subclass of one.** The current
`fdt-o:Train rdfs:subClassOf odrl:Asset` is dropped. `odrl:target` has range `odrl:Asset`, so
being the target of an offer or a request gives a train that role exactly where access
conditions apply, and nowhere else. ADR-020 is unchanged in substance — a train is an executable
asset and never a `dcat:Dataset` — and becomes more precise about how it is one.

## Alternatives

**Keep two components.** Defensible while the Directory was imagined as a station registry with
its own semantics. It does not survive the observation that an Index already indexes arbitrary
published resource types: two components would mean two harvesters, two query surfaces and two
sets of freshness semantics for one problem.

**Make the Depot an index too, and let stations trust it.** Rejected. It puts a discovery
service on the path of a security decision, and makes every station's PEP 1 only as trustworthy
as the harvest interval of a third party.

**Rename in product and documentation only, leaving `fdt-o:GarageCatalog` in place.** A term IRI
is an identifier and not a label, so this is legitimate and costs nothing today. Rejected
because the IRIs are not published: the cost of the rename will never be lower, and a permanent
mismatch between the word everyone says and the word every graph contains is a tax on every
reader of the ontology thereafter.

**Keep old terms as `owl:equivalentClass` aliases.** Rejected for the same reason — it buys
compatibility nobody needs yet, at the price of two names for one thing in every graph a
reasoner touches.

## Consequences

* **FDT-O v3**, breaking. `DepotCatalog`, `trainDepot`, `Train` made abstract, `Train ⊑
  odrl:Asset` dropped. Every shape, fixture, example and generated model rebinds; the open
  PR #1 (Q5) is affected. `make check` is the gate, as always.
* **The fixtures get simpler.** `ex:train/gene-disease a fdt-o:Train, fdt-o:SPARQLTrain,
  odrl:Asset` becomes `a fdt-o:SPARQLTrain`: two of those three types are now entailed.
* **WP-3.4 is re-scoped** from "Directory v0 and Garage v0" to a Depot (authoritative, serves
  payloads and keys) and a registry (harvests and indexes). The Depot gains work the Garage did
  not have — serving bytes, publishing JWKS — and the registry loses the trust role.
* **`fdt-run:targetQuery` still has no grammar** (acceptance sweep, item G). The registry's query
  surface is a contract the discovery plans depend on, and it has to be written before M3.
* **Freshness becomes visible.** A harvested record can name a station that has stopped
  answering. The registry shows when it harvested rather than implying currency; a push to a
  station that is gone fails, and the run's failure policy decides.
* **No decision is taken here about UIs.** What applications exist is settled; what they look
  like is the console work, and the testbed milestone.

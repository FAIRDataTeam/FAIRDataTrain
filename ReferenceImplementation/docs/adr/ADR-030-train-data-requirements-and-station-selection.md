# ADR-030 — A train declares the data it needs, and that is what selects a station

| | |
|---|---|
| **Status** | **Accepted**, 13 September 2026 — decided by Luiz in the M5 decision interview. |
| **Deciders** | Luiz Olavo Bonino da Silva Santos |
| **Relates to** | ADR-013 (coordination), ADR-019 (catalogues), ADR-024 (alignment stations), ADR-025 (conditions), ADR-029 (the registry); `fdt-commons` Q16, sweep item G |
| **Supersedes** | `fdt-run:targetQuery` as an unspecified string |

## Context

A plan selects the stations a train will visit. `fdt-run:targetQuery` is the property that
carries the selector; the term is declared, every discovery fixture has one, and **no grammar
ever said what the string means**. Nothing reads one. It blocked WP-5.3's scope, WP-3.1 and
WP-3.2, and it was recorded as Q16.

Framing it as "what query language?" was the wrong question. Station selection is not primarily
a search over labels and themes: it is a question about **whether a station holds the data the
train needs in order to run at all**. A train that requires a diagnosis code and an admission
timestamp cannot run where those do not exist, whatever the catalogue says about the theme.

FDT-O already models half of this and has since v2: `fdt-o:hasRequirement` relates a train to an
`fdt-o:InputRequirement`, which has as part a `dcat:Dataset` description that `dct:conformsTo` a
shape. `example-instances/train-description-with-requirements.ttl` carries a worked example with
a real SHACL shape. What was missing was the station side of the match, and an answer for data
that is not RDF.

## Decision

**1. A train declares the semantic data model of the data it requires**, as its
`fdt-o:InputRequirement`, and the model is expressed in **SHACL**. This is the existing FDT-O
structure, now made normative rather than illustrative.

**2. Non-RDF data is mapped to RDF with RML.** A station whose data is not RDF publishes an
[RML](https://rml.io/) mapping from its source — relational, CSV, JSON, XML — and matching
happens over the mapped view. RML generalises R2RML to arbitrary sources, so one mapping
language covers every station rather than one per format.

**3. A station publishes a SHACL shape per hosted dataset, generated from the RML mapping where
the data is not natively RDF.** An RML mapping already states which classes and predicates it
produces, so the shape is derived rather than written twice. A native-RDF station writes its
shape directly. Matching is then always shape against shape.

**4. Matching is structural coverage.** A station matches when, for every target class and
property path the train's shape requires, the station's shape declares the same path with a
compatible datatype or node kind. It is decidable, it is cheap enough to run over an index, and
— the property that matters most — it can say *which* required property is missing.

**5. Selection is the conjunction of the data requirement and a small set of non-data
constraints** — interaction mechanism, network, processing location — stated separately in the
plan. They are separate because they fail differently, and a consumer must be able to tell "no
station holds your data" from "no station in this network may process in the EU". ADR-026's
completeness statement depends on that distinction being available.

## Alternatives

**SPARQL over the harvested index.** Maximally expressive and the obvious first thought.
Rejected: every registry would have to expose SPARQL, plans would stop being portable between
registries whose harvests differ in shape, and a discovery selector becomes a general probe of
an index nobody scoped for that.

**Conformance IRIs only** — the train requires profile P, the station declares P, selection is
IRI equality. Representation-neutral and trivial. Rejected as the whole answer because it admits
no partial match and can explain nothing: a station either claims the profile or does not, and
nothing can say which property was missing or how close a station came. Retained as a fast path
where a community has agreed profiles: an IRI match is a coverage match.

**A new representation-neutral requirement language**, with per-station bindings, so no station
need ever produce RDF. Rejected: it means designing and maintaining a language that does not
exist, and a second modelling layer for every participant, when RML already maps anything to RDF
and SHACL already describes RDF.

**Exemplar-instance probing** — the train ships exemplar data and a station checks it can answer
against it. Rejected as the mechanism, because it cannot be indexed or reasoned over and it runs
the train's logic somewhere before any agreement exists. Kept in mind as a future *additional*
check a station may apply on arrival, where it is a PEP 2 question and not a discovery one.

**SHACL shape subsumption instead of structural coverage.** The theoretically right relation,
and it has no standard algorithm and is undecidable in general. Structural coverage is a
deliberate approximation.

## Consequences

* **`fdt-run:targetQuery` is replaced.** A plan states a data requirement — its own, or by
  reference the train's — and a set of non-data constraints. The run vocabulary and
  `run.shapes.ttl` change; the discovery fixtures change with them. Q16 closes.
* **WP-5.3, WP-3.1 and WP-3.2 unblock.** The registry now has a specified query surface: index
  the shapes stations publish, answer a requirement with the stations that cover it, and say why
  the others did not.
* **Stations must publish what their data conforms to.** No fixture does today. This is new work
  on `station-catalog.shapes.ttl`, on the station's self-description, and on the M1 and M2
  fixtures.
* **Structural coverage will sometimes be wrong in the permissive direction.** A station can
  cover a shape and still disappoint on arrival — the values are absent, or the mapping is
  stale. That failure then happens at the station, under an agreement, where failures are
  supposed to happen, and the run's failure policy decides. It must never be wrong in the
  restrictive direction silently: a station excluded from a run is a fact the completeness
  statement has to carry.
* **RML is a W3C Community Group specification, not a Recommendation** (R2RML is a
  Recommendation, for relational sources only). This is a real dependency risk and is recorded
  rather than hidden. The mitigation is that the mapping is a station-side artefact: a station
  that cannot express its source in RML can publish a hand-written shape instead and take
  responsibility for keeping it true.
* **A generated shape cannot drift from its mapping; a hand-written one can.** Where a station
  writes its own shape, nothing connects the declaration to the data, and only a failed visit
  reveals the gap. Stations should generate wherever they can.
* **The output side already works this way.** A train's `fdt-o:generatesOutput` carries
  `dct:conformsTo` a schema, which PEP 3 enforces. Inputs now use the same idiom, which is one
  concept in the ontology rather than two.

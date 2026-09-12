# ADR-033 — A controller may offer part of a dataset

| | |
|---|---|
| **Status** | **Accepted**, 13 September 2026 — decided by Luiz in the M5 decision interview. |
| **Deciders** | Luiz Olavo Bonino da Silva Santos |
| **Relates to** | ADR-011 (controllers), ADR-019 (catalogues), ADR-020/029 (assets), ADR-025 (conditions); `fdt-commons` Q11 |

## Context

A controller who will release aggregate outcomes but not free-text notes, or 2019–2024 but not
2025, needs somewhere to say so. The contracts had nowhere: `odrl:target` on an offer is a whole
`fdt-o:HostedDataset`, `DatasetShape` requires at least one offer per dataset, and the catalogue
shapes have no notion of a part. Recorded as Q11.

The interim default was to express the narrowing as a **constraint on the permission** and
enforce it at PEP 3 — the machinery already exists. It works, and it has one consequence that
does not: the catalogue stops telling the truth about what is on offer. A consumer browsing a
station sees a dataset and an offer; what they can actually obtain is narrower, and nothing in
the published metadata says so. The console's "who can reach this" view becomes misleading, which
for a governance surface is worse than missing.

## Decision

**`fdt-o:DatasetPart`** — an explicit part of a hosted dataset, with **its own IRI, its own data
controller and its own offers**.

A part is a first-class thing in the catalogue: it is discoverable, it can be the `odrl:target`
of an offer, and what is on offer is what the catalogue says is on offer.

## Alternatives

**A constraint on the permission** (the interim default). Nothing new in the ontology, and PEP 3
already enforces constraints. Rejected as the permanent answer because the catalogue no longer
advertises what is available, so discovery and the governance consoles both mislead — and
because a part frequently has a *different controller* from its whole, which a constraint on
someone else's offer cannot express at all.

**A `dcat:Distribution` per releasable view**, each with its own offer. DSP-friendly,
distributions are already first-class and per-mechanism, and the catalogue tells the truth.
Rejected because a distribution is a *representation* of a dataset, not a subset of it; using it
for subsets overloads a term whose meaning is already settled, and the controller must model
every view up front while combinations multiply.

## Consequences

* **FDT-O v4**, additive rather than breaking: `fdt-o:DatasetPart`, its relation to the whole,
  and the shapes that go with it. Coming so soon after the v3 rename is not ideal; it is additive
  and the IRIs are still unpublished (Q1), so the cost is still low.
* **Every catalogue consumer must learn the term.** A station catalogue may now list parts as
  well as datasets, and a consumer that ignores them sees less than is on offer.
* **`sh:class fdt-o:HostedDataset` constraints need revisiting** wherever an offer's target is
  shaped: a part is a legitimate target and is not a hosted dataset.
* **PEP 3 keeps its job.** A part is what may be *offered*; what actually leaves is still
  inspected against the train's declared output and the agreement's duties. Making parts explicit
  does not move the enforcement, it makes the offer honest about its scope.
* **A part with its own controller is the interesting case** and the one the alternatives could
  not express: it is how a dataset with mixed provenance — a cohort holding both institutional
  and individually-controlled records — is governed at all. It connects directly to the
  Individual Gateway, where a person is the controller of a part of somebody else's dataset.
* **Q11 closes**, and WP-1.3's evaluator scope and WP-2.5's catalogue can both be specified.

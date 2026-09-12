# ADR-020 — Trains are contracted assets (executables, not datasets); the Garage is a catalogue of train offers

| | |
|---|---|
| **Status** | Accepted; **amended 11 Sep 2026** after the `fdt-commons` probe. |
| **Deciders** | Luiz Olavo Bonino da Silva Santos |
| **Source** | Extracted verbatim on 12 September 2026 from *FAIR Data Train — Ecosystem Architecture, v0.1.4*, §Architecture Decision Records (`docs/architecture/fdt-ecosystem-architecture.md` in this repository, `FAIR Data Train/fair-data-station-architecture/` in the project folder). The source document remains normative; edit there and re-extract. |

## Context

Data-space practice treats provider-side code as a contracted asset; stations need to reason about which trains they accept. The first wording typed trains as `dcat:Dataset`; Luiz rejected this — trains are executable things, not datasets — and released FDT-O (a prototype) for free editing.

## Decision

A train is an `odrl:Asset` (so it can be the target of its provider's `odrl:Offer`: licence, permitted purposes and stations) and a `dcat:Resource` (so a Garage can catalogue it); it is **never** a `dcat:Dataset`. Its executable artefact is an FDT-O `Payload` (`fdt-o:hasPayload`: media type, download URL, sha256 digest), never a `dcat:Distribution`; it declares parameters, outputs, mechanisms, supported coordination styles (query/API trains: orchestrated only, ADR-013) and provenance. The Garage is an FDT-O `GarageCatalog` (⊑ `dcat:Catalog`) listing trains via `dcat:resource`; stations may require a train's offer/attestation at arrival and controllers may constrain allowed trains or garages.

## Alternatives

train as `dcat:Dataset` (rejected: category error, and it drags hosted-data rules onto trains); train as `dcat:DataService` (rejected: a train is not an endpoint).

## Consequences

FDT-O edits: `fdt-o:Train ⊑ odrl:Asset, dcat:Resource`; the closed `rdf:type` list in `TrainShape` replaced by `sh:class fdt-o:Train`; parameter, coordination and digest properties; `GarageCatalog`, `StationCatalog` and `HostedDataset` classes; the invalid `PayloadShape` fixed. Trains are not DSP catalogue entries (the DSP Catalog Protocol knows only `dcat:Dataset`) — a data space that wants to see trains needs a mapping wrapper. Garage API redefined; negotiation *about* the train possible in v2. Probe evidence: `fdt-commons/FINDINGS.md` v0.2, findings 3–4.

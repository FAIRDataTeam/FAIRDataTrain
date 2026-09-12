# ADR-027 — The visit protocol is the ecosystem's data plane: descriptor, events, envelope, two dispatch directions

| | |
|---|---|
| **Status** | Accepted (12 Sep 2026; requested by Luiz as the next contract to define). |
| **Deciders** | Luiz Olavo Bonino da Silva Santos |
| **Source** | Extracted verbatim on 12 September 2026 from *FAIR Data Train — Ecosystem Architecture, v0.1.4*, §Architecture Decision Records (`docs/architecture/fdt-ecosystem-architecture.md` in this repository, `FAIR Data Train/fair-data-station-architecture/` in the project folder). The source document remains normative; edit there and re-extract. |

## Context

§7 named a "visit protocol" contract but nothing specified how a Handler and a station actually talk; every pattern (ADR-023), the failure policy (ADR-026), the conditions (ADR-025) and the itinerary map depend on it, and a station must be able to take part in any pattern by implementing exactly one interface. Firewalled sites cannot accept inbound connections (station ADR-004).

## Decision

`fdt-commons/protocol/` specifies **FDT Visit Protocol v1** (`https://w3id.org/fdt/visit-protocol/v1`): (1) one **visit descriptor** (JSON Schema) carries everything a station needs for one visit — visit/run/plan IRIs, hop and phase, the train by Garage IRI with its payload digest, parameter values, either an ODRL request (negotiation on arrival, ADR-014) or an existing agreement, the plan's onward-state expectation (ADR-015/016), the reporting mode and the Handler's patience (`approvalWait`, `deadline`); (2) every station decision and state change is a **visit event** (JSON Schema) with a justification chain — the ordered event stream is the source of truth for the itinerary map and the audit explorer, delivered at least once and de-duplicated on id; (3) the **result envelope** is the ADR-025 `VisitResult` object extended with artefacts, the onward-state hand-over, a routing instruction for choreographed trains, scheduled obligations and a provenance link; (4) two OpenAPI descriptions: the **Station API** (`POST /visits`, status, events incl. SSE, result, artefacts, cancel, agreements read-only) and the **Handler API** (`GET pending-visits` for poll dispatch, `ack`, `POST events`, `PUT result`, `PUT artifacts`), so a poll-mode station never needs an inbound port; (5) the visit IRI is the idempotency key; retries increment `attempt` under the same agreement; the station verifies the payload digest against the train's Garage offer before anything runs (ADR-020); (6) security v1 = OIDC bearer tokens trusted per network (ADR-010/017) plus per-visit capability tokens for callbacks; v2 = DCP. Controller actions (approve, revoke, suspend, withdraw), metadata/catalogue and Directory/Garage stay in their own contracts.

## Alternatives

adopt DSP Transfer Process messages now (rejected for v1: DSP has no checkpoint events, pending approval, onward state or justifications — the mapping in `mapping/state-machines.md` is kept for the v2 binding); a message queue between Handler and station (rejected: hospitals will not expose brokers; HTTP + callbacks/poll suffices); station-to-station forwarding in v1 (deferred, ADR-016).

## Consequences

the Handler prototype needs the pending-visits endpoint and the callback receiver; the station implements one API for all patterns; fixtures for hop 1 of the time-to-groin run are the first conformance material; a JSON-LD context for descriptors and events, SSE framing and artefact size limits are draft-2 items.

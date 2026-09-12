# End-to-end scenarios

The milestone scenarios, run against the **real components** — not against fakes of each other.
A component's own tests can only show that it behaves as its author expected; these show that
two of them agree, which is the thing neither can establish alone.

`make e2e` builds one environment with every Python component installed and runs them here.

| | |
|---|---|
| `test_m1.py` | **M1 — one visit.** The Handler drives `plan-gene-disease-single.jsonld`; the station runs the train through PEP 1, negotiation, PEP 2, the SPARQL adapter and PEP 3. A second plan differing in **one parameter** produces the opposite outcome, and the run reports it in ADR-026's words. |

The station runs in-process, over ASGI rather than a socket: same code, same protocol, no port
and no timing. What that does *not* cover is the wire — TLS, proxies, and a station that is
slow rather than instant. `make up` and a compose file are WP-4.3.

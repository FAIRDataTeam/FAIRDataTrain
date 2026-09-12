# End-to-end scenarios

The milestone scenarios, run against the **real components** — not against fakes of each other.
A component's own tests can only show that it behaves as its author expected; these show that
two of them agree, which is the thing neither can establish alone.

`make e2e` builds one environment with every Python component installed and runs them here.

| | |
|---|---|
| `test_m1.py` | **M1 — one visit.** The Handler drives `plan-gene-disease-single.jsonld`; the station runs the train through PEP 1, negotiation, PEP 2, the SPARQL adapter and PEP 3. A second plan differing in **one parameter** produces the opposite outcome, and the run reports it in ADR-026's words. |
| `test_depot.py` | **WP-5.2 — the same visit, with a real Train Depot.** Three components now: the Handler asks the Depot what the train is, the station asks the *same* Depot, and neither reads a train from a file. The digest is traced end to end — the bytes the Depot serves, hashed; the digest it publishes; the digest the Handler put in the descriptor; the one PEP 1 checked — so no number in that chain is copied between two files. A Depot whose bytes do not match its own catalogue withholds the train, and the run stops before a station is asked to judge anything. |

The station runs in-process, over ASGI rather than a socket: same code, same protocol, no port
and no timing. What that does *not* cover is the wire — TLS, proxies, and a station that is
slow rather than instant. `make up` and a compose file are WP-4.3.

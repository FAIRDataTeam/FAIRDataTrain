# Adversarial probes

These are not tests of the implementation — there is no implementation yet. They are tests of
the **contracts**, and each one asks the same question: *can this check fail?*

They were written during the 12 September 2026 design review and each corresponds to a finding
in `fdt-commons/FINDINGS.md`. Every instance they build is one a conformant processor accepts
and a human would reject:

| Probe | Asks | Finding |
|---|---|---|
| `agreement_probes.py` | can an agreement grant what its offer never offered, target another dataset, name another assignee, permit `RecordLevel` onward state? | 28 |
| `schema_probes.py` | can a refusal have no reason, an `active` no agreement, a `delivered` envelope no inspection block and record-level fields? | 29 |
| `descriptor_request_probe.py` | does the hop-1 descriptor's embedded ODRL request satisfy `RequestShape`, and does it agree with the Turtle request of the same IRI? | 31 |

## Status

| Probe | Finding | Now reports |
|---|---|---|
| `schema_probes.py` | 29 — **fixed in v0.7** | **invalid** on all six. It is a regression test. |
| `agreement_probes.py` | 28 — open | CONFORMS on five of seven. Needs the normative derivation rule (finding 19, Q12), not a schema change. |
| `descriptor_request_probe.py` | 31 — open | the descriptor's request still violates `RequestShape` and still disagrees with the Turtle request of the same IRI. A fixture decision. |

A probe reporting CONFORMS or VALID **is** the finding. When the gap it exposes is closed it
starts reporting violations, and at that point it has become a regression test — keep it.

Run them against a checkout with `pyshacl`, `rdflib` and `jsonschema` installed; paths are
relative to the metaproject root.

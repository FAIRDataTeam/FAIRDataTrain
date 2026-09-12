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

**They are expected to report CONFORMS and VALID today.** That is the finding. As each gap is
closed, the corresponding probe should start reporting violations, and at that point it becomes
a regression test and moves into the normal suite.

Run them against a checkout with `pyshacl`, `rdflib` and `jsonschema` installed; paths are
relative to the metaproject root.

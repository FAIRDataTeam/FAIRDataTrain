# ADR-034 — Run modes supply defaults; a station's decision mode narrows, never widens

| | |
|---|---|
| **Status** | **Accepted**, 13 September 2026 — asked for by Luiz after WP-5.4 landed. |
| **Deciders** | Luiz Olavo Bonino da Silva Santos |
| **Relates to** | ADR-008 (manual approval), ADR-017 (networks), ADR-027 (every decision is an event), ADR-032 (where a machine may not grant it may not refuse either); Q19, Q20, Q21 |

## Context

ADR-032 put the automation regime where it belongs: on the **network membership**, because a
regulator's rule is not the controller's to relax and certainly not the station operator's.
`fdt-net:permitsAutomatedDecision` had no default — a deployment had to say which regime it was
in — and Q19 settled what a station does with a network that says nothing: **silence bars
automated decisions**, because the two errors are not symmetric.

That is correct and it is unusable as a way to bring a testbed up. Every station in a
development deployment queues every visit to a person who does not exist, and the scenario
looks like a component failure rather than a configuration gap — which Q19 itself recorded as
the cost of the default.

Two separate things were missing, and conflating them is the mistake this ADR exists to avoid.

1. **A deployment needs to say what kind of deployment it is.** Somebody bringing the ecosystem
   up on a laptop wants the machine to decide; somebody running a station over real data wants a
   person to. That is a property of the *deployment*, not of the data and not of the network.
2. **A station operator needs a dial of their own.** An operator may want a person in the loop
   for reasons no network and no controller expressed — a new deployment, a quarter under
   scrutiny, a dataset they have just started serving. Today the only lever is
   `fdt-p:requiresManualApproval`, which is the *controller's*, on the *offer*, and an operator
   editing it would be forging a controller's instruction about their own data.

## Decision

**1. A run mode, which supplies defaults and nothing else.** `development` or `production`,
configured once per deployment. It defaults two things:

| | `development` | `production` |
|---|---|---|
| decision mode, if none configured | `automated` | `manual` |
| a membership that states no automation regime | permitted, and marked as assumed | **refuses to start** |

**The default run mode is `production`.** A station started with no configuration at all must be
the safe one. Development is opted into, which is the right way round: a testbed is always
configured deliberately, and a production deployment is the one most likely to be configured by
someone in a hurry.

A run mode never overrides anything stated. A membership that states its regime keeps it in both
run modes; a configured decision mode is used in both.

**The two defaults are deliberately not symmetric, and the reason is that one of them would be
published.** A station's self-description restates the facts of the networks it is a member of,
`fdt-net:permitsAutomatedDecision` among them, so that a registry or a Handler can read it
without first resolving the network (`fdts:NetworkShape` requires it). A station that filled that
field in from its own run mode would be publishing **its own assumption as the network's
published rule**, to a registry that will index it and to Handlers that will act on it. So in
`production` an unstated regime is a startup failure, not a default: a configuration error the
operator fixes in a minute, rather than a claim about a regulator's rule that travels. Q19 is
untouched — it says what *silence* means, and in production the station now never has to decide
what silence means, because it will not run without an answer.

In `development` the same field is filled in and the deployment is a testbed by construction.
The `assumedRegime` marker of decision 5 is what keeps its artefacts distinguishable.

**2. A station decision mode, which narrows and never widens.** `fdt-p:decisionMode` on the
station — `automated`, `semi-automated`, `manual`:

* **`automated`** — wherever the network permits, the station concludes the negotiation itself,
  in either direction.
* **`semi-automated`** — the station concludes a **grant** itself where every condition of the
  offer is satisfied, and sends every **adverse** outcome to a person with its recommendation and
  the evidence behind it.
* **`manual`** — the station concludes nothing; every outcome goes to a person.

The ceiling is always the network's. In a network that bars automated decisions the mode changes
nothing: everything goes to a person either way, and the agreement records
`fdt-p:HumanRequiredByRegulation` naming the network, not the station. An operator who selects
`automated` there is told so rather than shown their own selection reflected back.

**3. `semi-automated` is not the asymmetry ADR-032 forbids.** ADR-032 refused to let a machine
barred from granting still refuse, because refusing is an adverse decision taken by a machine
about somebody's request. `semi-automated` runs the asymmetry the other way: the machine takes
only the **non-adverse** action and a person takes every adverse one. The cost falls on the
refused party as latency, not as a decision taken about them by a machine.

**4. A fourth authorisation mode.** `fdt-p:HumanByStationPolicy`, distinct from
`fdt-p:HumanByControllerPreference` because the station operator and the data controller are not
the same party (ADR-011). A controller reading an audit trail must be able to tell "I asked for
this" from "whoever runs the station holding my data asked for it": the two are relaxed by
different people, and a controller who read the second as the first would believe they had a
safeguard they do not have.

Precedence, when more than one rule applies, follows ADR-032's existing rule — name the one
nobody else in the loop may relax: **network, then station, then controller.**

**5. An assumed regime is marked as assumed.** `fdt-p:automationRegimeAssumed` on the agreement
and `approval.assumedRegime` on the event, true when the network published no regime and the run
mode supplied one. `authorisationMode` says *what* applied; this says the rule was **not
published but inherited from how the process was started**. Without it, a development
deployment's automatic agreements are indistinguishable from a production deployment's, and
"development configuration reached somewhere it was not meant to" is the failure the whole run
mode invents the possibility of.

**6. Changing the mode is recorded, with a reason.** An append-only history, starting with the
station's own record of what it started as — otherwise the first change would appear out of
nothing and the state before it would be unknown. A controller asking why an agreement was
reached automatically last Tuesday needs to find out what the station was configured to do last
Tuesday. Changing the mode does not reach visits already awaiting a person: those were queued
under the rule that applied when they arrived.

## Alternatives

**One setting, not two** — let the run mode itself be the decision mode. Rejected: they answer
different questions and have different lifetimes. A run mode is chosen once, by whoever deploys;
a decision mode is changed by whoever operates, possibly weekly. Collapsing them means an
operator who wants a person in the loop has to tell their station it is a development deployment,
and then everything else the run mode defaults comes along with it.

**Let the operator set the network regime too** — one screen, all of it editable. Rejected
outright: the regime belongs to the network's governance authority, and an operator who could
edit it could edit away a regulator's rule from the UI of the thing the rule constrains.

**Default the regime to `barred` in production rather than refusing to start.** Symmetric with
the decision-mode default, and it fails safe at the point of decision. Rejected because the
station does not only *decide* with that field — it **publishes** it. A station quietly
publishing "this network bars automated decisions" because nobody told it otherwise is asserting
a regulator's rule to every registry that harvests it, and the assertion is no more true than the
opposite one would have been. Failing safe on a decision and failing safe on a published claim
are different problems, and only the first has a safe direction.

**`semi-automated` means "automatic on clear-cut grounds"** — the machine refuses when a
prohibition fired or the network does not match, and defers when an eligibility fact is missing.
ADR-032 already rejected this reading for the network's regime, and the objection carries over
unchanged: the station would be classifying its own grounds as clear-cut, and that
classification is exactly what a disappointed consumer would dispute.

## Consequences

* **`make check` gains a fourth authorisation mode** and a fixture that uses it — a station
  whose operator put a person in the loop where neither network nor controller asked for one.
* **The station gains an admin API** (`station-admin-api.yaml`) and the station console an admin
  section. Its authentication is a placeholder: a bearer token configured out of band, with
  writes refused in a production deployment that has none. The real identity model is WP-2.4's
  (**Q21**).
* **The evaluator asks the question twice per negotiation** — what mode applies to a grant, and
  what mode applies to an adverse outcome — because under `semi-automated` they differ. That is
  the whole content of `semi-automated` and it is why the admin API reports both.
* **A development deployment's agreements can be told apart.** Not prevented from existing —
  marked. Prevention would need the station to know which networks are real, which it cannot.
* **Q20 records what is mine and not Luiz's**: the precise meaning of `semi-automated` above was
  filled in, not given. It is the conservative reading — strictly safer than `automated` and
  strictly more available than `manual` — and it is overturnable.

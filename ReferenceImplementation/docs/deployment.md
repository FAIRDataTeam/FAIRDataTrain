# Deploying a Data Station: run modes, decision modes, and what each defaults

> Normative for the settings it names. The rules come from ADR-032 (where a machine may not
> grant, it may not refuse either) and ADR-034 (run modes supply defaults; a station's decision
> mode narrows, never widens). Q19, Q20 and Q21 in `OPEN-QUESTIONS.md` record what was decided
> by default rather than by Luiz.

A station is configured by three things that are often confused, and they answer different
questions:

| | Answers | Set by | Changes how often |
|---|---|---|---|
| **Deployment profile** | what *kind of station* this is | whoever deploys | once |
| **Run mode** | what *kind of deployment* this is | whoever deploys | once |
| **Decision mode** | how much of a negotiation this station concludes *by itself* | whoever operates | whenever they like |

They are independent. An institutional station can be brought up as a testbed, and a personal
station can be somebody's real one.

## Run mode

`FDT_STATION_RUN_MODE` — `development` or `production`. **The default is `production`**, because
a station started with no configuration at all has to be the safe one. Development is opted
into, which is the right way round: a testbed is always brought up deliberately, and a
production deployment is the one most likely to be configured by somebody in a hurry.

A run mode **supplies defaults and overrides nothing**. Anything you configure is used in both.

| | `development` | `production` |
|---|---|---|
| decision mode, if none configured | `automated` | `manual` |
| a membership that states no automation regime | read as permitting, and every decision marked as assumed | **the station refuses to start** |
| the admin API | writable without a credential | writable only with `FDT_STATION_ADMIN_TOKEN` |

### Why the second row is not symmetric

Because `permits_automated_decision` is not only *read*, it is **published**. A station's
self-description restates the facts of its networks — including this one — so that a metadata
registry or a Train Handler can read a network's regime without first resolving the network, and
`fdts:NetworkShape` requires it. A station that filled that field in from its own run mode would
be asserting **a regulator's rule nobody told it**, to a registry that will index the assertion
and to Handlers that will act on it. "Assume barred" is no more true than "assume permitted".

Failing safe on a decision and failing safe on a published claim are different problems, and
only the first has a safe direction. So in production it is a startup error — a configuration
gap an operator closes in a minute — rather than a claim that travels.

In development the same field is filled in, the deployment is a testbed by construction, and
every artefact produced under the assumption is marked: `approval.assumedRegime` on the event,
`fdt-p:automationRegimeAssumed` on the agreement. That marker is what lets a development
deployment's agreements be told apart from a production one's, which is the failure the run mode
creates the possibility of and therefore has to answer for.

## Decision mode

`FDT_STATION_DECISION_MODE` — `automated`, `semi-automated` or `manual`. Also settable at
runtime from the station console's **Configuration** screen, or over the admin API
(`fdt-commons/protocol/openapi/station-admin-api.yaml`).

* **`automated`** — wherever the network permits it, the station concludes the negotiation
  itself, granting and refusing.
* **`semi-automated`** — the station concludes a **grant** itself where every condition of the
  offer is met, and sends every **adverse** outcome to a person with its recommendation and the
  evidence behind it.
* **`manual`** — the station concludes nothing; every outcome goes to a person.

**It narrows and never widens.** The ceiling is the network's: in a network whose
`fdt-net:permitsAutomatedDecision` is false, the station decides nothing in either direction
whatever this is set to, and the agreement records `HumanRequiredByRegulation` naming the
network. Selecting `automated` there changes nothing, and the console shows the effective mode
rather than reflecting your selection back at you.

**`semi-automated` is not the asymmetry ADR-032 forbids.** There, a machine barred from granting
that still refused would be taking an adverse decision it was not trusted to take. Here the
machine takes only the non-adverse action and a person takes every adverse one. The cost falls
on the refused party as latency, not as a decision taken about them by a machine. The precise
meaning was taken as a default rather than decided — see **Q20**.

### Who is recorded as having asked for a person

Three parties can put one in the loop, and they are not the same party (ADR-011). Which applied
is recorded on the agreement as `fdt-p:authorisationMode` with the rule that imposed it:

| Mode | Set by | On |
|---|---|---|
| `HumanRequiredByRegulation` | the network's governance authority | `fdt-net:permitsAutomatedDecision` |
| `HumanByStationPolicy` | the station **operator** | this decision mode |
| `HumanByControllerPreference` | the data **controller** | `fdt-p:requiresManualApproval` on their offer |

When more than one applies, the mode names the one nobody else in the loop may relax:
**network, then station, then controller.** A controller who drops their own preference tomorrow
must not thereby turn a legally-required human decision into an automatic one.

## The admin credential

`FDT_STATION_ADMIN_TOKEN` — the station operator's own credential, configured out of band. It is
**not** a network credential and grants nothing about data: it answers who may change how this
station is configured, which is not the question a visit's token answers.

In production, a station with no admin token accepts no writes at all and says so in
`GET /admin/decision-mode` (`writable: false`), so the console disables the selector with the
reason rather than offering a control whose every use returns 401. This is a placeholder until
WP-2.4 gives the operator, the controller and the auditor a real identity model — see **Q21**.

## The controller's credentials, and where their conditions live

`FDT_STATION_CONTROLLER_TOKENS` — a JSON object mapping a bearer token to the **data controller**
it proves. Three parties ask three different things of a station and each has its own credential
(ADR-011): a visit's token says who is visiting on behalf of which consumer, the admin token says
who may configure the station, and this says whose data somebody speaks for. A station with none
configured serves no controller surface at all, which is honest rather than broken: it means
nobody has been given standing to act as a controller here.

`FDT_STATION_CONDITIONS_DIR` — where a controller's own access conditions are kept. A condition is
an `odrl:Offer` the station publishes and evaluates against (ADR-007, ADR-017), and until
`fdt-commons` finding 73 the only way to change one was to edit the deployment's metadata as the
station's **operator** — so the party ADR-011 exists to separate from the operator had to become
one.

Without the directory the station publishes the conditions it was deployed with and answers `501`
to a change, saying so. That is deliberate and it is not a permission problem: a condition written
into memory is a governance decision the controller was told had taken effect, and that the next
restart undoes — their terms would silently widen back, which is the direction nobody checks.

**A controller's conditions may not contradict each other** (Q26,
`fdt-commons/protocol/condition-consistency.md`). Several conditions over one dataset in one
network are fine and are evaluated as the **union** — two offers are two things on offer, and a
standing research permission beside a narrower arrangement with one named collaboration is an
ordinary thing to want. What the station refuses is a pair that cannot both hold: the negotiator
tries each offer until one does not refuse, so a prohibition standing beside a permission it
covers does nothing at all, and that is how a controller narrows their terms and narrows nothing.
The station answers `409`, names the condition and the rule pair, and changes nothing.

The check is deliberately conservative. Only `odrl:eq` on a shared left operand proves two rules
apart, and `odrl:includedIn` is followed transitively and **upward only** — prohibiting
`odrl:use` reaches a permission on `fdt-p:runQuery`, and prohibiting `runQuery` beside a
permission on `use` is a narrowing, which is quite possibly what was meant. Anything the station
cannot prove apart comes back to the controller to be made explicit: a false contradiction costs
one edit, and a missed one is an access rule that silently does not apply.

Conditions that arrive in the **metadata a station was deployed with** are reported rather than
refused, and are kept as given. Choosing between them would be the silent resolution this rule
exists to prevent, taken by the party least entitled to take it, and refusing to start would turn
one controller's metadata defect into an outage for every other controller at the station.

## The signing keys, and what a station cannot do without one

`FDT_STATION_SIGNING_KEY` — a JWK Set holding this station's Ed25519 key, with the private half.
ADR-038: an agreement carries a signature from **each** party, and the station signs the
assigner's side. Without a key it publishes its catalogue, says so loudly at startup, and
**concludes no agreement at all** — every visit that reaches negotiation rests at
`negotiation.requested` with the reason naming this setting.

That refusal is deliberately not a *Refused*. Refused is a data controller's governance decision
about access and is reported verbatim to a data consumer (ADR-026); a station operator's missing
configuration recorded in the controller's name would put a decision in the record that the
controller never took.

The station signs as the **controller's agent**, and the agreement says so: `fdt-p:signedBy` names
the station and `fdt-p:onBehalfOf` names the controller. *The controller signed* and *the station
signed for the controller* are different facts with different weight, and a record that let them
be confused would be worth less than no signature — a verifier would read the weaker as the
stronger. A controller holding their own key is the end state and is not built; the agent's
signature is the bridge, and it is marked as one.

`GET /keys` publishes the public half. Only the public half: the document is built from the public
key rather than by filtering the private one, so there is no code path that can serve `d`.

`FDT_STATION_PARTY_KEYS` — party IRI → the **public** keys this station will accept an assignee's
signature from, as `{"<party IRI>": {"keys": [<JWK>, …]}}`. The same shape the Depot uses for
creators, and for the same reason: **where the key comes from is the whole of the security here.**
A station that fetched the key from wherever the signature pointed would establish only that the
signer holds the key they nominated — anyone can name any party and publish a key set at a URL
they control. The binding is configuration, out of band.

A station told about nobody accepts nothing and says `UnknownKey`, which is a key-distribution
problem reported as one. The four refusals are kept apart on purpose: `UnknownKey` says nothing is
wrong with the signature, `DoesNotVerify` says the signature is wrong, `WrongParty` is valid
cryptography by somebody who is not the assignee, and `WrongDigest` means the two sides are not
looking at the same document. One answer for all four would send a train owner hunting a forgery
that never happened.

**Nothing runs half-signed.** The station signs, emits `negotiation.awaiting-signature` with the
digest, and waits; the Handler checks the terms and that signature, signs the assignee's side at
`POST /visits/{id}/agreement/signature`, and only then is the agreement active and the run queued.
The exchange is the Handler's step because a station cannot reach a Handler that chose
`mode: poll`. On the Handler's side the key is `--signing-key`, with `--owner` naming the train
owner it signs for.

## Bringing the testbed up

```sh
# a station for the testbed: it decides for itself, and says so on everything it produces
FDT_STATION_RUN_MODE=development fdt-station serve

# the same station, but with a person in the loop for anything adverse
FDT_STATION_RUN_MODE=development FDT_STATION_DECISION_MODE=semi-automated fdt-station serve
```

```sh
# a production station. Every membership states its automation regime or this does not start.
FDT_STATION_RUN_MODE=production \
FDT_STATION_PROFILE=institutional \
FDT_STATION_DECISION_MODE=manual \
FDT_STATION_ADMIN_TOKEN="$(openssl rand -hex 32)" \
fdt-station serve
```

The console is pointed at a station by URL, never by a compiled-in origin:

```sh
cd FDTConsole && npm run dev     # then open station.html#/admin?station=http://localhost:8000
```

## Every station setting

`FDT_STATION_*`, from `fdt_station/core/config.py`. A `FDT_STATION_*` variable that matches no
setting is a **startup error**, not a silently ignored typo: configuration that was meant to be
read and was not is exactly as broken as configuration that is wrong.

| Variable | Default | What it is |
|---|---|---|
| `FDT_STATION_PROFILE` | `personal` | `personal`, `institutional`, `linkage` — a set of defaults for everything below |
| `FDT_STATION_RUN_MODE` | `production` | `development` or `production` (above) |
| `FDT_STATION_DECISION_MODE` | the run mode's | `automated`, `semi-automated`, `manual` (above) |
| `FDT_STATION_ADMIN_TOKEN` | none | the operator's credential for the admin API |
| `FDT_STATION_CONTROLLER_TOKENS` | none | JSON object, token → data controller IRI. None means no controller surface is served |
| `FDT_STATION_CONDITIONS_DIR` | none | where a controller's access conditions are kept. None means the station publishes what it was deployed with and answers 501 to a change |
| `FDT_STATION_SIGNING_KEY` | none | JWK Set with this station's Ed25519 signing key. **None means it concludes no agreements** (ADR-038) and says so at startup |
| `FDT_STATION_PARTY_KEYS` | none | party IRI → the public keys an assignee's signature is accepted from. None means every such signature is an `UnknownKey` |
| `FDT_STATION_IRI` | the profile's | the IRI the station is known by |
| `FDT_STATION_BASE_URL` | the profile's | public base URL; the dispatch endpoint **is** this and nothing appended, so a path prefix goes here |
| `FDT_STATION_ADAPTERS` | the profile's | JSON list; the enabled adapters are the *only* mechanisms the station advertises |
| `FDT_STATION_MEMBERSHIPS` | the profile's | JSON list of network memberships |
| `FDT_STATION_DATASETS` | none | JSON list; a station serves a dataset because a source is configured for it and for no other reason |
| `FDT_STATION_AUTH_REQUIRED` | `true` | turning it off is a visible act of configuration, never a default |
| `FDT_STATION_CORS_ORIGINS` | none | browser origins allowed to read this station, comma-separated — what CORS calls the allowed origins. **Empty means no browser may**, which is why a console reports that a station did not answer until this is set (Q23). `scheme://host[:port]` and nothing else: a trailing slash is refused at start-up, because it would match nothing and say so only on somebody's screen. `*` means any page on the web — reasonable for a public catalogue, never reasonable together with `FDT_STATION_AUTH_REQUIRED=false` |
| `FDT_STATION_DATABASE_URL` | the profile's | SQLite in `personal`, PostgreSQL otherwise |
| `FDT_STATION_DEPOT_URL` | none | the Train Depot trains are resolved against (ADR-029) |
| `FDT_STATION_CONTRACTS_DIR` | found | where `fdt-commons` is; the station will not start without it |
| `FDT_STATION_STREAM_IDLE_TIMEOUT` | `30.0` | how long an idle SSE stream stays open — a transport bound, never an outcome |

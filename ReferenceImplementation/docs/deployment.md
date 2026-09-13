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
| `FDT_STATION_IRI` | the profile's | the IRI the station is known by |
| `FDT_STATION_BASE_URL` | the profile's | public base URL; the dispatch endpoint **is** this and nothing appended, so a path prefix goes here |
| `FDT_STATION_ADAPTERS` | the profile's | JSON list; the enabled adapters are the *only* mechanisms the station advertises |
| `FDT_STATION_MEMBERSHIPS` | the profile's | JSON list of network memberships |
| `FDT_STATION_DATASETS` | none | JSON list; a station serves a dataset because a source is configured for it and for no other reason |
| `FDT_STATION_AUTH_REQUIRED` | `true` | turning it off is a visible act of configuration, never a default |
| `FDT_STATION_DATABASE_URL` | the profile's | SQLite in `personal`, PostgreSQL otherwise |
| `FDT_STATION_DEPOT_URL` | none | the Train Depot trains are resolved against (ADR-029) |
| `FDT_STATION_CONTRACTS_DIR` | found | where `fdt-commons` is; the station will not start without it |
| `FDT_STATION_STREAM_IDLE_TIMEOUT` | `30.0` | how long an idle SSE stream stays open — a transport bound, never an outcome |

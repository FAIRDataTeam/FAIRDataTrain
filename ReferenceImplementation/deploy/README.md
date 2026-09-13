# Running the testbed

```
make up          # build the images and bring it all up in Docker
make status      # is each one answering, and is the thing answering ours?
make down        # stop it
make logs        # follow everything
```

Then open **<http://localhost:8405>** — the consoles are in there too, so Docker is the only
thing you need installed.

## What comes up, and why each one is here

| | port | why |
|---|---|---|
| **station-ut** | 8400 | the station the M1 scenario visits. Its network permits automated decisions and the operator has chosen `automated`, so a request whose every condition is met is granted without anybody being asked |
| **station-oosterlicht** | 8401 | in two networks that **differ on whether a machine may decide**. In the regional stroke network Oost it concludes nothing in either direction (ADR-032) — not even a refusal — and puts the case to a person |
| **depot** | 8402 | the authority for a train (ADR-029): the concrete class, the parameters, the input requirement, and the payload digest a station checks at PEP 1. It can also be **taken from** and **withdrawn from** (ADR-036) — see below |
| **registry** | 8403 | an index of what the others publish, harvested once at start-up. Explicitly **not** a trust anchor |
| **handler** | 8404 | drives `plan-gene-disease-single.jsonld` against the UT station on startup, so there is a finished run to watch |
| **consoles** | 8405 | all six bundles, built and served as files |

Two stations rather than one is the point. With one, the testbed shows the automated path and
quietly implies it is the only one; the pair is what makes ADR-032 visible — the same request
granted by a machine in one network and, in the other, neither granted nor refused by one.

The `seed` container does the two things that have to happen once everything is up: the
registry's first harvest, and **one visit at Oosterlicht under the Oost network**, which is why
console S3 has something in it. Without it the approvals queue is empty and ADR-032 is a
paragraph. It runs `deploy/testbed.py seed` and exits.

## Credentials

Three parties ask three different things of a station, and each has its own credential
(ADR-011). The testbed configures two of them — both are Q21's placeholder:

* `testbed-operator` — the station operator. Needed by **S1** (the visit counts), **S2** and
  **S7**: those are other parties' traffic, and a station that served them to whoever asked
  would be publishing one consumer's business to the next.
* `testbed-controller` — the data controller at Oosterlicht. Needed by **S3**, whose queue is
  scoped to the controller presenting it.

Neither is a network credential and neither grants anything about data.

## The images

One Dockerfile, built into the repository `fdt_testbed/*` — `docker images 'fdt_testbed/*'` is
the set, and `make down` removes the containers and touches nothing else on the machine.

| image | what it is |
|---|---|
| `fdt_testbed/station:dev` | `FAIRDataStation-py`. **Both** stations run it; the only difference between them is which profile they are handed |
| `fdt_testbed/depot:dev` | `TrainDepot` |
| `fdt_testbed/registry:dev` | `FDTRegistry` |
| `fdt_testbed/handler:dev` | `FAIRDataTrainHandler` |
| `fdt_testbed/console:dev` | the consoles, built with node and served by nginx — the toolchain does not survive into the running image |
| `fdt_testbed/tools:dev` | the network namespace, and the seeding |

The build context is the whole metaproject, because an image needs both a component and the
contracts it validates against: a station that shipped without `fdt-commons` would start and
then refuse every visit it was given, which is a failure that looks like a protocol error and is
a packaging one. **The image reproduces the checkout's layout** — `/fdt/fdt-commons`,
`/fdt/FDT-O`, `/fdt/deploy` — so a profile is the same file in a container and out of one.

Every container runs as a user that could not administer the machine it is on.

These are not the deployment profiles. Those are WP-4.3's, there are three of them, and they
differ in exactly the ways a testbed does not have to care about: no volumes here, no database,
no restart policy. `make down && make up` is a clean testbed, and a component that dies stays
dead so that you can see that it did.

## One address space, and why

Every service shares the `net` container's network stack, so `localhost:8400` inside any
container is `localhost:8400` on the host. That is not a convenience. It is what makes the
addresses these components publish about themselves *true*.

A registry indexes what a station and a Depot published, **including where they are**, and a
console follows what the registry indexed: the Handler console's H1 resolves a train by fetching
the Depot URL the registry recorded, because the Depot is the authority and the index is an
index (ADR-029). That fetch is made by a browser, on the host. Under ordinary compose networking
the registry would have to harvest `http://depot:8402` — an address no browser can reach — so
either the index would be full of URLs that work in one place only, or every component would
have to advertise one address and be harvested at another.

The cost is that `ports:` may appear on `net` and nowhere else, which is why every published
port is in one block of `compose.yaml`. `tests/e2e/test_compose.py` checks that block against
the profiles, and checks that each one is published to **this machine and no further**: the
stations run with `FDT_STATION_AUTH_REQUIRED=false`, which is a deliberate act of configuration
for a testbed and also a door that must not open onto a café's wifi.

## Changing a component

```
make up-processes     # the same testbed, straight out of the checkout
```

Then `npm run dev` in `FDTConsole/`. This is the short loop: a container build stands between
every edit and the screen, which is the opposite of what a testbed is for. It needs each
component's `.venv`, which `make test` builds — run that once first.

The addresses are identical either way, so `make status` works against whichever is running,
and a console you already have open does not need to be told anything new.

## One description, two ways to run it

`deploy/testbed.py` says what the testbed is made of: which components, from which profiles, on
which ports, with which identity each must publish. The compose does not repeat any of it. Each
service runs `testbed.py exec <name>` and is health-checked with `testbed.py health <name>`, so
the containers and the processes are two ways of running one description rather than two
descriptions that agree for a while.

`tests/e2e/test_compose.py` is what keeps it that way, and it is worth knowing what it found:
the first run of the compose bound every component to the loopback address *inside its own
container*, where the health check — which asks 127.0.0.1 from inside that same namespace —
reported all five healthy while nothing on the host could reach any of them. A container can
always talk to itself. Only a question asked from outside can tell the difference, which is why
`make up` ends by asking one.

## Profiles

`deploy/profiles/*.env` — `KEY=value`, read by `deploy/env.py`. **A value is taken verbatim to
the end of the line**: no quote stripping, no `$VAR`, and `#` is not a comment inside a value.
Every one of those conveniences would corrupt a profile here — half the IRIs in this ecosystem
carry a fragment, and `https://w3id.org/fdt/network#StationRole` truncated at `#` is a different
IRI that still parses.

They are read by each component's **own** settings class, not by a format of the testbed's own:
a station that behaved differently under the testbed than under its own settings file would be
demonstrating the testbed rather than the station. `tests/e2e/test_testbed.py` loads every
profile through `StationSettings`, `RegistrySettings` and `DepotSettings`, so a renamed field
fails in `make e2e` rather than in front of somebody who has just run `make up`.

### The Depot's write surface, in this testbed

A Depot with no store publishes a curated corpus and accepts neither a publication nor a
withdrawal; it answers `501` and says so. This one has a store, an operator IRI and a
credential, so two of the three operations can be watched:

```sh
# take the gene-disease train under its creator's licence — this changes nothing the Depot serves
curl -X POST http://localhost:8402/trains/gene-disease/take \
     -H 'Content-Type: application/json' \
     -d "{\"request\": $(python3 -c 'import json,sys;print(json.dumps(open(sys.argv[1]).read()))' \
          fdt-commons/examples/train-taken.ttl)}"

# withdraw one as the agent operating this Depot — which says nothing about the code
curl -X POST http://localhost:8402/trains/time-to-groin/withdraw \
     -H 'Authorization: Bearer fdt-testbed-depot-operator' \
     -H 'Content-Type: application/json' \
     -d '{"reason": "Carried no longer, on this Depot operator'"'"'s instruction."}'

# and it is still here: 200, with the withdrawal on it, and nobody new may take it
curl http://localhost:8402/trains/time-to-groin | grep wasInvalidatedBy
```

**Publishing is deliberately not configured.** A Depot resolves a creator's keys from its own
configuration and never from the submission — a key fetched from wherever the submitter pointed
would prove only that they hold the key they nominated — so without `FDT_DEPOT_CREATOR_KEYS`
this Depot has been told about nobody and refuses every signature as an unknown key. The profile
says where to point it.

The store is `.testbed/depot-store`, which resolves to the checkout on a developer's machine and
to a directory inside the container under `make up`. Compose declares no volume for it, so
`make down && make up` is still a clean testbed.

Under Docker the profiles are also read a second time, by compose's own `.env` parser, which has
both of the conveniences listed above. The two agree today;
`test_compose_reads_a_profile_exactly_as_the_runner_does` is what says so tomorrow. It needs
Docker, and `FDT_REQUIRE_DOCKER=1` turns its skip into a failure.

Each instance's port lives in its own profile as `FDT_TESTBED_PORT`, beside the `base_url` it
publishes, so the address a component advertises and the socket it is served on cannot drift
apart. Nothing else knows a port: the entrypoint reads it, the nginx config is substituted from
it, and the compose's published-ports block is checked against it.

## Why a console can read a station at all

Every console is served from one origin and reads components on others — the Handler's console
reads a Handler, a registry and a Depot on one page — so it can never be same-origin with all of
them. A browser discards each of those responses unless the component names the page's origin in
a header, and a console with no header to go on reports that the component did not answer.

So every profile names the two origins this testbed serves consoles from: the consoles' own
container on 8405, and `npm run dev` on 5173. Nothing is allowed by default anywhere in this
ecosystem (Q23) — machine clients are unaffected, because the same-origin policy is a browser's
rule about pages rather than a server's rule about clients.

This is worth knowing because no test could have found it: a test client has no same-origin
policy, so every suite passed while every console, opened in a browser, was refused.
`tests/e2e/test_browser.py` now sends the header a browser sends.

## Ports

8400–8405, chosen because 8000, 8080, 8081 and 5173 are what everything else on a developer's
machine already wants.

## What `make status` checks

That each port answers **and that the thing answering is ours** — every component publishes its
own IRI at `/`, and the check is a string search for it. This is not belt and braces: the first
run of this script reported a station as healthy on port 8000, where there was no station. A
container somebody had left running answered, and the runner had asked only whether *something*
did.

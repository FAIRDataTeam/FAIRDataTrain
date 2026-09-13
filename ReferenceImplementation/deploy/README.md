# Running the testbed

```
make up          # two stations, a Depot, a registry, a Handler — and one seeded approval
make status      # is each one answering, and is the thing answering ours?
```

Then, in `FDTConsole/`, `npm run dev` and open the URLs `make up` prints.

`make up` needs each component's `.venv`, which `make test` builds. Run it once first.

## What comes up, and why each one is here

| | port | why |
|---|---|---|
| **station-ut** | 8400 | the station the M1 scenario visits. Its network permits automated decisions and the operator has chosen `automated`, so a request whose every condition is met is granted without anybody being asked |
| **station-oosterlicht** | 8401 | in two networks that **differ on whether a machine may decide**. In the regional stroke network Oost it concludes nothing in either direction (ADR-032) — not even a refusal — and puts the case to a person |
| **depot** | 8402 | the authority for a train (ADR-029): the concrete class, the parameters, the input requirement, and the payload digest a station checks at PEP 1 |
| **registry** | 8403 | an index of what the others publish, harvested once at start-up. Explicitly **not** a trust anchor |
| **handler** | 8404 | drives `plan-gene-disease-single.jsonld` against the UT station on startup, so there is a finished run to watch |

Two stations rather than one is the point. With one, the testbed shows the automated path and
quietly implies it is the only one; the pair is what makes ADR-032 visible — the same request
granted by a machine in one network and, in the other, neither granted nor refused by one.

The runner seeds **one visit at Oosterlicht under the Oost network**, which is why console S3
has something in it. Without it the approvals queue is empty and ADR-032 is a paragraph.

## Credentials

Three parties ask three different things of a station, and each has its own credential
(ADR-011). The testbed configures two of them — both are Q21's placeholder:

* `testbed-operator` — the station operator. Needed by **S1** (the visit counts), **S2** and
  **S7**: those are other parties' traffic, and a station that served them to whoever asked
  would be publishing one consumer's business to the next.
* `testbed-controller` — the data controller at Oosterlicht. Needed by **S3**, whose queue is
  scoped to the controller presenting it.

Neither is a network credential and neither grants anything about data.

## Ports

8400–8404, chosen because 8000/8080/8081 are what everything else on a developer's machine
already wants. Each instance's port lives in its own profile as `FDT_TESTBED_PORT`, beside the
`base_url` it publishes, so the address a station advertises and the socket it is served on
cannot drift apart. `tests/e2e/test_testbed.py` checks that they agree.

## Profiles

`deploy/profiles/*.env` — `KEY=value`, read by `deploy/env.py` and handed to each subprocess as
its environment. **A value is taken verbatim to the end of the line**: no quote stripping, no
`$VAR`, and `#` is not a comment inside a value. Every one of those conveniences would corrupt a
profile here — half the IRIs in this ecosystem carry a fragment, and
`https://w3id.org/fdt/network#StationRole` truncated at `#` is a different IRI that still parses.

They are read by each component's **own** settings class, not by a format of the testbed's own:
a station that behaved differently under `make up` than under its own settings file would be
demonstrating the testbed rather than the station. `tests/e2e/test_testbed.py` loads every
profile through `StationSettings`, `RegistrySettings` and `DepotSettings`, so a renamed field
fails in `make e2e` rather than in front of somebody who has just run `make up`.

## Processes, not containers

Every component is a Python package in this checkout with a `serve` command, so the shortest
path from a working tree to something you can click on is to start five of them. Containers are
a packaging question (WP-4.3) and would put a build between every edit and the browser, which is
the opposite of what a testbed is for.

## What `make status` checks

That each port answers **and that the thing answering is ours** — every component publishes its
own IRI at `/`, and the check is a string search for it. This is not belt and braces: the first
run of this script reported a station as healthy on port 8000, where there was no station. A
Docker container somebody had left running answered, and the runner had asked only whether
*something* did.

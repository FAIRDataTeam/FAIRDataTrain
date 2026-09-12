# FAIR Data Train

The FAIR Data Train (FDT) is a "code visits data" platform: trains — executable queries, API
calls, scripts and containers — travel to data stations, run inside policy checkpoints, and
release only inspected aggregates. The data does not move.

## Where things are

| | |
|---|---|
| [`ReferenceImplementation/`](ReferenceImplementation/) | **the v1 implementation** — the metaproject, with each component as a submodule. Start there. |
| [`specs/`](specs/) | the published specification site |
| [`TrainHandler/`](TrainHandler/) | the 2022 Train Handler prototype, kept for reference |

Earlier prototypes live in their own repositories and are not evolved:
[`FAIRDataStation`](https://github.com/FAIRDataTeam/FAIRDataStation) (Java),
[`TrainHandler-server`](https://github.com/FAIRDataTeam/TrainHandler-server),
[`TrainHandler-client`](https://github.com/FAIRDataTeam/TrainHandler-client) and
[`TrainOrchestrator`](https://github.com/FAIRDataTeam/TrainOrchestrator).

## Getting started

```sh
git clone --recurse-submodules https://github.com/FAIRDataTeam/FAIRDataTrain.git
cd FAIRDataTrain/ReferenceImplementation
make check
```

`make check` runs every contract validator — the SHACL shapes, the JSON Schemas, the visit
protocol fixtures and the JSON-LD round-trip. See
[`ReferenceImplementation/README.md`](ReferenceImplementation/README.md) for the components,
the ground rules and the milestones.

## Licence

MIT — see [`LICENSE`](LICENSE).

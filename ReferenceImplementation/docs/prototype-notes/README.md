# Notes for the prototype repositories

Five public repositories in `FAIRDataTeam` are earlier work that the reference implementation
supersedes, and nothing in any of them says so. A newcomer searching the organisation finds two
things called a data station and four called a train handler, with no marker saying which is
current — Q7.

**Decided 13 September 2026: a note at the top of each README.** Lineage, not abandonment. The
repositories stay where they are, stay clonable, and stop being mistaken for current work.

**Each file here is the block to paste at the top of that repository's README**, above everything
else. Pushing them is an act on the `FAIRDataTeam` organisation and is Luiz's; they are drafted
here so the exact text is reviewable before anything lands on a public repository.

| File | Repository | Default branch | Last commit on it |
|---|---|---|---|
| [`FAIRDataStation.md`](FAIRDataStation.md) | `FAIRDataStation` (Java) | `develop` | 30 May 2025 |
| [`TrainHandler.md`](TrainHandler.md) | `TrainHandler` (umbrella) | `master` | 15 Feb 2023 |
| [`TrainHandler-server.md`](TrainHandler-server.md) | `TrainHandler-server` (Java/Spring) | `develop` | 3 Mar 2023 |
| [`TrainHandler-client.md`](TrainHandler-client.md) | `TrainHandler-client` (Vue) | `develop` | 23 Apr 2025 |
| [`TrainOrchestrator.md`](TrainOrchestrator.md) | `TrainOrchestrator` (Python) | `main` | 18 Aug 2025 |

## What the notes say, and what they deliberately do not

They **state facts and name the successor**. They do not say *deprecated*, *unsupported* or *do
not use*: those are judgements about other people's running code, and this reference
implementation has not replaced any of it in production. Anyone deciding whether to build on a
prototype can see the dates.

They **name the successor without linking to it**. `FAIRDataStation-py`, `FAIRDataTrainHandler`
and `FDTConsole` are private until Q6 flips, and a link that 404s tells the reader the project is
broken rather than that the repository is not yet public. Each note links to
[`FAIRDataTrain`](https://github.com/FAIRDataTeam/FAIRDataTrain) instead, which is public today
and is where the current work is described. **When Q6 flips, the names become links** — that is
the one edit these notes will need.

The dates in every note were read from the repositories on 13 September 2026 rather than
remembered. `OPEN-QUESTIONS.md`'s D1 had described all four Train Handler repositories as "the
Java 17 / Spring Boot prototypes", and one of them is: writing these notes is what found it.

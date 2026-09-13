# ADR-040 — A Depot pings its registry; the registry announces nothing

| | |
|---|---|
| **Status** | **Accepted**, 13 September 2026 — answered by Luiz on Q24's remaining half. The answer as given is in `OPEN-QUESTIONS.md` under Q24. |
| **Deciders** | Luiz Olavo Bonino da Silva Santos |
| **Relates to** | ADR-006 (conform to the FDP specification), ADR-026 (outcome vocabulary; "gone" ≠ "never here"), ADR-029 (a registry is an index and not a trust anchor), ADR-036 (a withdrawn train stays addressable; a Depot notifies nobody); **Q24**, `fdt-commons` finding 67 |

## Context

ADR-036 made a withdrawn train stay addressable at its Depot: the IRI, the bytes and the digest
still resolve, marked with who withdrew it, when and why, so a finished run stays explicable and a
past envelope can still be checked against the bytes that produced it. It also decided the Depot
**notifies nobody**, and gave the reason — a notification list is a record of who is doing what
with whose train, held by a party with no business knowing.

Q24 asked what a *registry* does with such a train, and took the default that it stays resolvable
by IRI and is never offered in search: a registry that put a withdrawn train in front of somebody
composing a plan would be making a recommendation it has no standing to make, and dropping it
entirely would recreate finding 67's confusion between *gone* and *never here*.

The leftover was whether a registry that has indexed a withdrawn train should **tell** anybody —
the Handler that resolved it last week, the stations that ran it. The draft argument was that
ADR-036's reasoning carries over and the answer is silence there too.

## Decision

**The registry announces nothing, and the Depot pings the registry.**

1. **No announcements from the index.** A registry keeps no list of who resolved what, and tells
   nobody when an entry changes. ADR-036's argument holds here unchanged.
2. **The Depot pings its registry when its content changes** — a publication, a withdrawal, a
   description that has moved on. This is the FDP pattern already: when an FDP's content changes it
   pings the Index, and the Index re-harvests.
3. **A ping carries what changed, not who cares.** That is the whole reason this is not the thing
   ADR-036 refused. The Depot says *this train's description has moved on, come and look*; it does
   not say, and does not need to know, which Handlers resolved it or which stations ran it. No list
   of interested parties exists anywhere, so there is none to keep, leak or be compelled to produce.
4. **The index is then current at the moment somebody looks**, which is when they can act on it —
   rather than at the moment somebody decided to tell them, which is a decision the Depot would
   have had to make about parties it knows nothing about.

## Alternatives

| | Why not |
|---|---|
| **Notify the Handlers that resolved it** | Gives the consumer the earliest possible warning and requires the registry to keep who-asked-for-what. That record is the thing ADR-036 refused to let a Depot keep, and it does not become acceptable by moving one component to the left. |
| **A withdrawal feed anybody may poll** | Nobody registers, so no list of interested parties exists — the same property the decision has. It was not chosen because it is a second surface answering a question the index already answers: a poller of the feed is a poller of the index, with one more thing to keep in step. Reconsider if a consumer ever needs withdrawals without the rest of the index. |
| **Harvest on a schedule only, with no ping** | What a registry can always fall back to, and it is the failure mode rather than the design: the index is stale for however long the schedule says, and the staleness is invisible. The ping is an optimisation of freshness, not a correctness mechanism — a registry must remain correct without it. |

## Consequences

- **The Depot gains an outbound call** and therefore a configured registry endpoint, a retry
  policy, and a failure that must not be fatal: a Depot whose registry is unreachable has still
  published or withdrawn the train, and must say so. The ping is best-effort by construction.
- **`FDTRegistry` gains a ping endpoint** and re-harvests the pinging Depot on receipt. It must
  authenticate the pinger enough to know which Depot to re-read, and must not trust the ping's
  *content* — it fetches, as ADR-029 requires, because a registry is an index and not a trust
  anchor.
- **A ping is a hint, never a fact.** The registry re-harvests and believes what it reads from the
  Depot; a ping that claims a withdrawal changes nothing by itself.
- **`tools/coverage.py` stays deliberately unaffected**: whether a station holds the data a train
  needs is a fact about the station, and does not change because the train was withdrawn.
- **Nothing here gives a Handler an early warning.** That is the accepted cost, stated plainly: a
  consumer whose plan names a train withdrawn yesterday learns when they next resolve it, and the
  answer they get is complete — withdrawn, by whom, when and why — which is more than a
  notification would have carried.

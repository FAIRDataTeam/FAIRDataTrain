# ADR-036 — A train's three parties, and what a Depot may be asked to do

| | |
|---|---|
| **Status** | **Accepted**, 13 September 2026 — answered by Luiz in the Q21 interview. The twelve answers as given are listed in `OPEN-QUESTIONS.md` under Q21; anything here beyond them is drafting, and is marked where it goes furthest. |
| **Deciders** | Luiz Olavo Bonino da Silva Santos |
| **Relates to** | ADR-011 (three parties, three credentials), ADR-012 (agreements), ADR-020 (a train is an executable asset), ADR-026 (outcome vocabulary), ADR-028 (signatures), ADR-029 (the Depot is the authority for a train), ADR-031; **Q21**, Q5, Q22 |
| **Companion** | ADR-035, which does the same for a station's parties |

## Context

ADR-029 made the Depot the authority for a train — its concrete class, its parameters, its input
requirement, the payload bytes and the digest it computes rather than repeats, and "the owner's
offer and public keys". It gave the Depot no way to be *written to*: every train it serves is
loaded from a corpus on disk. Publishing and withdrawing were left to Q21, because putting a
train into a Depot means saying who put it there.

FDT-O already distinguishes two of the parties. `fdt-o:TrainOwner` is "the agent(s) who sent a
Train to a Data Station — therefore, the Train is visiting a Station on behalf of the Train
Owner", and `fdt-o:StationOwner` is the party responsible for operating a station. There is
**no term for whoever wrote the train**. The only thing near it is a `dct:creator` restriction,
and it is on the wrong class: FDT-O states that every `foaf:Agent` has a `fdt-o:Train` as its
creator, which says that every controller and every station owner was created by a train
(finding 68).

So the party who authors a train and the party who sends it to a station have been the same word
in the model and are obviously not the same party in practice: a group publishes an analysis
train, and a dozen research organisations each take it and run it against data they have
negotiated for themselves.

## Decision

### 1. Three parties, named

| | who | what they are answerable for |
|---|---|---|
| **Train Creator** (`fdt-o:TrainProvider`) | the agent — person or organisation — who created the train | the code, the declared parameters, the declared output, and the licence under which anyone may take it |
| **Train Owner** | the agent who takes a train and sends it to stations | this visit: the train is visiting *on behalf of* the owner, and it is the owner a controller is deciding about |
| **Depot administrator** | the agent who operates the Depot | that the Depot serves what was published, and that it can stop serving something it must stop serving |

**The class already existed.** `fdt-o:TrainProvider` — "the agent(s) (organization or person)
who created the Train" — has been in FDT-O since the legacy OWL, and this ADR was first drafted
saying no such term existed. It has no `rdfs:label` (one of the 49 in finding 64), which is why
it could not be found by anybody looking for a creator, and it is used by nothing: no shape, no
example, no code. A distinction that lives only in a class definition is one nothing can be
wrong about, which is how it survived five milestones unexercised (finding 69).

So nothing is added and nothing is renamed. `fdt-o:TrainProvider` gains the label **"Train
Creator"**, a `skos:definition` of what a creator is answerable for, and the
`fdt-o:hasControllingRights` restriction its three sibling parties already had — it was the only
one of the four defined as a bare `foaf:Agent` subclass. The IRI keeps the word *Provider*: a
published IRI is a promise, the term is decades-adjacent to the legacy ontology, and "who made
this" is what it always meant. The cost is real and permanent — the word on screen differs from
the word in the IRI — and it was taken deliberately over renaming a published term.

The backwards `dct:creator` restriction is turned the right way round in the same change
(finding 68). Both go on the Q5 branch, which is where FDT-O is currently edited.

### 2. A train is published by its creator, and the Depot verifies a signature

A submission is signed with a key the Depot already publishes in its JWKS (ADR-028, ADR-029).
The Depot checks a signature; it does **not** run an account system and is **not** an identity
provider. That keeps it the authority for a train — the thing ADR-029 made it — without making
it a second place where people have logins.

### 3. The creator registers a usage licence, and taking a train is evaluated against it

The creator publishes an `odrl:Offer` over the train **as an asset** (ADR-020: a train is an
executable asset, never a `dcat:Dataset`). Becoming a Train Owner is a request against that
offer, evaluated by the Depot exactly as a station evaluates a controller's offer over a dataset
(ADR-012), and what comes out is a **creator–owner agreement** naming the licence, both parties
and the payload digest.

So "it is only possible if the licence allows" is something that **happened**, with a record, and
not something that was intended. It is the same ODRL evaluator in its second deployment, which is
the point: a licence that is evaluated by different machinery from the one that evaluates a
controller's offer would disagree with it eventually, over exactly the clauses that are hard.

**No station checks this agreement.** It is between creator and owner, and a station that
demanded to see it would be making itself a party to a licence between two other organisations
and giving PEP 1 a new way to refuse a visit that is otherwise entirely in order.

### 4. Withdrawal leaves the train addressable, marked, with a reason and a time

A train may be withdrawn by its creator or by the Depot administrator — the second because a
Depot that cannot take down what it is compelled to take down is a legal problem rather than a
design-purity one.

Either way the IRI and the digest **still resolve**, and the answer says *withdrawn*, when, and
why. A finished run stays explicable and a past envelope can still be checked against the bytes
that produced it. Deleting the record instead would make a station unable to explain a decision
it had already made and justified, which is ADR-027 undone retroactively — and it would do it at
exactly the moment somebody is asking questions.

Withdrawal is a state on the train, not a notification to anybody (§Alternatives).

## What here is drafting rather than an answer

- **§1's "answerable for" column.** The three parties and what each is were given. Assigning the
  declared parameters and declared output to the creator's answerability, rather than the
  owner's, is drafting — and it is the one that will matter, because it decides who a station
  complains to when a train's declared output and its actual output disagree.
- **§3's "same ODRL evaluator, second deployment of it."** The answer was that the Depot
  evaluates the licence and issues an agreement. That it must be the *same* evaluator as the
  station's, and that a forked one would disagree over exactly the hard clauses, is an
  engineering judgement stated here as a constraint.
- **§4's "withdrawal is a state, not a notification."** Follows from the option chosen, which had
  no notification in it; stated explicitly because the alternative is easy to add later and hard
  to remove.

## Alternatives considered

**`dct:creator` on the train and no class at all.** Rejected: the property is how a train points
at its creator, and it is used for exactly that in `fdts:TrainOfferShape`; what it cannot do is
carry the definition of the role or be the domain of anything. `fdt-o:TrainOwner` did not settle
for `dct:contributor` either.

**Renaming `fdt-o:TrainProvider` to `fdt-o:TrainCreator`.** This was the answer first given, on
my statement that no such term existed — a statement that was wrong. With the term in hand the
question became a rename of a published IRI rather than a new class, and it was decided against:
nothing in this ecosystem uses it, but the legacy OWL is published and a deprecation that nobody
needs is a cost paid by everyone downstream. "Provider" is the wrong word and the label is where
that gets fixed.

**The owner publishes to the Depot.** Fewer parties to model. Rejected: a creator would then
have no standing at the Depot over their own artefact, and one train taken by twelve
organisations would be published twelve times — twelve digests, twelve descriptions, and no way
for a station to tell it had already run this code.

**Either party may publish, and the Depot records which.** Rejected as the worst of both: a
consumer reading the index would have to decide what a train published by a non-creator means,
and would have nothing to decide it with.

**The licence is published and nothing evaluates it.** How most data licences actually work.
Rejected because it makes §3 a statement of intent, and because the ecosystem's whole claim is
that conditions are evaluated rather than asserted.

**The Handler refuses to compose a plan the licence forbids.** Cheapest, and the check lives
with the party it constrains. Rejected for that same reason: it can be skipped by anyone who
writes their own Handler, and the FDT protocol is meant to survive a client that does not
cooperate.

**A station checks the creator–owner agreement at PEP 1.** Strongest chain of custody. Rejected
in §3.

**Withdrawal notifies every station that resolved the train.** Strongest governance. Rejected
because it requires the Depot to keep a list of who resolved which train — a record of who is
doing what with whose train, held by a party that has no business knowing, and created as a side
effect of a takedown mechanism.

**Deletion on withdrawal (410 Gone).** Rejected in §4.

## Consequences

**The Depot gains a write surface**: publish (signed, by the creator), take (evaluated against
the creator's offer, producing an agreement), withdraw (by creator or administrator, leaving a
marked record). Three operations, each of which has to appear in `train-depot-api.yaml` in
`fdt-commons` **before** any of it is written, with shapes for the creator's offer and the
creator–owner agreement and fixtures that fail for the right reasons.

**FDT-O changes**, on the Q5 branch: `fdt-o:TrainProvider` gains a label, a definition and the
restriction it was missing, and the `dct:creator` restriction moves to `fdt-o:Train` where it
belongs. The first is the first of Q22's 49 unlabelled terms to be **decided** rather than
transcribed, and it is the case that question is about: the label could not be guessed from the
IRI, because the IRI says the wrong word. 49 → 48.

**A second ODRL evaluation appears in the ecosystem**, in a component that had none. The Depot
now needs the pySHACL and ODRL machinery the station has, and the two must not fork: whatever a
station concludes about a clause, a Depot must conclude about the same clause.

**H1 gains something to show and H2 gains its missing half**: a train's page can name its
creator, its licence and its owner, and the console can say why a train may not be taken.

**What is still open.** Whether an owner may re-publish a *parametrised instance* of a train
type under their own name — "takes a train type and submits it" suggests a second resource in
the Depot, and §2 currently gives the creator sole authority over what is published. Left until
somebody needs it, because inventing it now would be inventing the parameters too.

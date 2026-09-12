#!/usr/bin/env python3
"""Can the time-to-groin chain actually be run, hop by hop? (Q14 decision A)

`make check` was green on this fixture set while the chain could not run at any hop: the
train is a fdt-o:DockerTrain, every ODRL offer permitted fdt-p:runQuery, and two of the
stations on the chain supported no container mechanism at all. No shape says that an offer
must permit the action the visiting train performs, or that a station must support the
train's mechanism — so no shape could fail.

This probe asks those two questions of the merged fixture graph, per hop:

  1. does the station support the mechanism the train implements?
  2. does the offer over the station's dataset permit an action the train's request asks?

Exit 1 if either fails for any hop. Run it against a fixture set with one offer reverted to
fdt-p:runQuery and it fails — that is the mutation test in `docs/reviews/`.
"""
import sys
import os
from rdflib import Graph, Namespace, URIRef

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
EX = Namespace("https://example.org/fdt/")
FDT_O = Namespace("https://w3id.org/fdt/fdt-o#")
ODRL = Namespace("http://www.w3.org/ns/odrl/2/")
DCAT = Namespace("http://www.w3.org/ns/dcat#")
DCT = Namespace("http://purl.org/dc/terms/")

# the chain of plan B, in visiting order, as the run fixtures record it
CHAIN = ["station/noorderlicht", "station/linkage-oost", "station/rav-oost",
         "station/zuiderlicht", "station/hap-oost"]
TRAIN = EX["train/time-to-groin"]
REQUEST = EX["request/ttg-2026q3"]


def load(commons):
    g = Graph()
    for f in ("network-and-stations.ttl", "trains-and-plans.ttl", "policies.ttl"):
        g.parse(os.path.join(commons, "examples", f), format="turtle")
    return g


def actions_of(g, policy):
    return {o for rule in (ODRL.permission, ODRL.prohibition, ODRL.obligation)
            for r in g.objects(policy, rule) for o in g.objects(r, ODRL.action)}


def main(commons):
    g = load(commons)
    asked = actions_of(g, REQUEST)
    mechanisms = set(g.objects(TRAIN, FDT_O.implementsInteractionMechanism))
    print(f"train    {TRAIN.split('/')[-1]}  implements "
          f"{', '.join(sorted(str(m).split('#')[-1] for m in mechanisms))}")
    print(f"request  asks {', '.join(sorted(str(a).split('#')[-1] for a in asked))}\n")

    failures, gaps = [], []
    for local in CHAIN:
        st = EX[local]
        name = local.split("/")[-1]
        supported = set(g.objects(st, FDT_O.supportsInteractionMechanism))
        # a linkage station offers translation, not the train's own mechanism (ADR-022)
        is_linkage = (st, None, FDT_O.LinkageStation) in g or \
            URIRef(str(FDT_O) + "LinkageStation") in set(g.objects(st, URIRef(
                "http://www.w3.org/1999/02/22-rdf-syntax-ns#type")))
        mech_ok = is_linkage or bool(mechanisms & supported)
        print(f"{name:<14} supports "
              f"{', '.join(sorted(str(m).split('#')[-1] for m in supported)) or '—'}")
        if not mech_ok:
            failures.append(f"{name}: supports no mechanism the train implements")

        datasets = [d for cat in g.subjects(DCT.publisher, st)
                    for d in g.objects(cat, DCAT.dataset)]
        if not datasets:
            gaps.append(name)
            print(f"{'':<14}   publishes no dataset — nothing for the hop to visit")
            continue
        for ds in datasets:
            for offer in g.objects(ds, ODRL.hasPolicy):
                granted = actions_of(g, offer)
                overlap = granted & asked
                label = str(offer).split("/")[-1]
                shown = ', '.join(sorted(str(a).split('#')[-1] for a in overlap)) or "NOTHING"
                print(f"{'':<14}   offer {label}: grants {shown} of what the request asks")
                if not overlap:
                    failures.append(
                        f"{name}: offer {label} permits "
                        f"{sorted(str(a).split('#')[-1] for a in granted)}, "
                        f"the request asks {sorted(str(a).split('#')[-1] for a in asked)}")

    print()
    for f in failures:
        print(f"FAIL  {f}")
    for gname in gaps:
        print(f"GAP   {gname} is on the chain but publishes no dataset "
              f"(fdt-commons FINDINGS 34)")
    if failures:
        print(f"\n{len(failures)} hop(s) of the chain cannot run.")
        return 1
    print(f"Every hop of the chain can run: {len(CHAIN) - len(gaps)} station(s) checked, "
          f"{len(gaps)} with no dataset to visit.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "fdt-commons")))

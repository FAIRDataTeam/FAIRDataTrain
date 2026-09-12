"""visit-protocol.md §4 says negotiation.request is 'validated by RequestShape'. Nothing in
tests/ does that. Do it: extract the JSON-LD request from the descriptor fixture, parse it,
validate against the policy shapes with the fixture set as context, and compare its actions
and constraints with the Turtle request ttg-2026q3 and the offer evt-registry-research."""
import glob, json, os
import rdflib, pyshacl
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
C = os.path.join(ROOT, "fdt-commons")
doc = json.load(open(os.path.join(C, "examples/protocol/visit-descriptor-ttg-hop1.json")))
req = doc["negotiation"]["request"]
# The fixture's context is the remote ODRL context. Try it; fall back to an inline equivalent
# for the few terms used so the probe is offline-deterministic.
ODRL = "http://www.w3.org/ns/odrl/2/"
inline_ctx = {"@vocab": ODRL, "odrl": ODRL,
  "target": {"@id": "odrl:target", "@type": "@id"}, "assignee": {"@id": "odrl:assignee", "@type": "@id"},
  "profile": {"@id": "odrl:profile", "@type": "@id"}, "action": {"@id": "odrl:action", "@type": "@id"},
  "leftOperand": {"@id": "odrl:leftOperand", "@type": "@id"}, "operator": {"@id": "odrl:operator", "@type": "@id"},
  "rightOperand": {"@id": "odrl:rightOperand", "@type": "@id"}, "permission": {"@id": "odrl:permission"},
  "constraint": {"@id": "odrl:constraint"}, "Request": "odrl:Request", "Permission": "odrl:Permission"}
g = rdflib.Graph()
try:
    g.parse(data=json.dumps(req), format="json-ld")
    src = "remote ODRL context"
except Exception as e:
    req2 = dict(req); req2["@context"] = inline_ctx
    g.parse(data=json.dumps(req2), format="json-ld"); src = f"inline context (remote failed: {type(e).__name__})"
print(f"parsed descriptor request with {src}: {len(g)} triples")
for s, p, o in sorted(g, key=lambda t: (str(t[0]), str(t[1]))):
    print("   ", s.n3(g.namespace_manager) if not isinstance(s, rdflib.BNode) else "_:b", p.n3(g.namespace_manager), o.n3(g.namespace_manager) if not isinstance(o, rdflib.BNode) else "_:b")
shapes = rdflib.Graph()
for f in glob.glob(os.path.join(C, "shapes", "*.ttl")): shapes.parse(f, format="turtle")
ctx = rdflib.Graph()
for f in sorted(glob.glob(os.path.join(C, "examples", "*.ttl"))) + sorted(glob.glob(os.path.join(C, "vocab", "*.ttl"))) + [os.path.join(ROOT, "FDT-O/ontology/fdt-o-v2-delta.ttl")]:
    ctx.parse(f, format="turtle")
# the JSON-LD request has the same IRI as the Turtle one: replace the Turtle description (as validate.py does for the plan)
REQ = rdflib.URIRef("https://example.org/fdt/request/ttg-2026q3")
def cbd(gr, root):
    out, seen, stack = rdflib.Graph(), set(), [root]
    while stack:
        s = stack.pop()
        if s in seen: continue
        seen.add(s)
        for p, o in gr.predicate_objects(s):
            out.add((s, p, o))
            if isinstance(o, rdflib.BNode): stack.append(o)
    return out
ttl_req = cbd(ctx, REQ)
for t in ttl_req: ctx.remove(t)
conforms, _, text = pyshacl.validate(ctx + g, shacl_graph=shapes, inference="none", advanced=True)
print(f"\nRequestShape/PolicyCommonShape on the descriptor's request: {'CONFORMS' if conforms else 'VIOLATES'}")
for line in text.splitlines():
    if "Message:" in line or "Result Path" in line: print("   ", line.strip())
# actions: descriptor request vs Turtle request vs offer
def actions(gr, pol):
    return sorted({str(a).split('#')[-1].split('/')[-1] for perm in gr.objects(pol, rdflib.URIRef(ODRL+"permission")) for a in gr.objects(perm, rdflib.URIRef(ODRL+"action"))})
def leftops(gr, pol):
    return sorted({str(l).split('#')[-1].split('/')[-1] for perm in gr.objects(pol, rdflib.URIRef(ODRL+"permission")) for c in gr.objects(perm, rdflib.URIRef(ODRL+"constraint")) for l in gr.objects(c, rdflib.URIRef(ODRL+"leftOperand"))})
full = rdflib.Graph()
for f in glob.glob(os.path.join(C, "examples", "*.ttl")): full.parse(f, format="turtle")
OFF = rdflib.URIRef("https://example.org/fdt/offer/evt-registry-research"); AGR = rdflib.URIRef("https://example.org/fdt/agreement/agr-9a01")
print("\nactions  descriptor request:", actions(g, REQ)); print("actions  Turtle request    :", actions(full, REQ))
print("actions  offer             :", actions(full, OFF)); print("actions  agreement agr-9a01:", actions(full, AGR))
print("leftOps  descriptor request:", leftops(g, REQ)); print("leftOps  Turtle request    :", leftops(full, REQ)); print("leftOps  offer             :", leftops(full, OFF)); print("leftOps  agreement         :", leftops(full, AGR))
print("descriptor train.type:", doc["train"]["type"], "| mechanism:", doc["train"]["mechanism"])

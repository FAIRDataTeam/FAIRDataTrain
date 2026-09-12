"""Probe what AgreementShape actually rejects. Each probe adds one agreement to the valid
fixture set + vocab + ontology and reports whether pySHACL conforms."""
import glob, os, sys
import rdflib, pyshacl
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
C = os.path.join(ROOT, "fdt-commons")
shapes = rdflib.Graph()
for f in glob.glob(os.path.join(C, "shapes", "*.ttl")): shapes.parse(f, format="turtle")
base_files = sorted(glob.glob(os.path.join(C, "examples", "*.ttl"))) + sorted(glob.glob(os.path.join(C, "vocab", "*.ttl"))) + [os.path.join(ROOT, "FDT-O", "ontology", "fdt-o-v2-delta.ttl")]
PRE = """
@prefix xsd:    <http://www.w3.org/2001/XMLSchema#> .
@prefix odrl:   <http://www.w3.org/ns/odrl/2/> .
@prefix dspace: <https://w3id.org/dspace/2025/1/> .
@prefix fdt-p:  <https://w3id.org/fdt/profile#> .
@prefix ex:     <https://example.org/fdt/> .
"""
PROBES = {
 "A: agreement with NO permission, NO prohibition, NO duty (empty grant)": """
ex:agreement\\/probe-a a odrl:Agreement ; odrl:profile <https://w3id.org/fdt/profile> ;
  odrl:target ex:dataset\\/noorderlicht-evt-registry ; odrl:assigner ex:party\\/noorderlicht-neurology ; odrl:assignee ex:party\\/stroke-network-oost-qi ;
  dspace:timestamp "2026-09-11T10:12:05Z"^^xsd:dateTime ; fdt-p:underNetwork ex:net\\/stroke-oost ;
  fdt-p:derivedFromOffer ex:offer\\/evt-registry-research ; fdt-p:derivedFromRequest ex:request\\/ttg-2026q3 .
""",
 "B: agreement granting an action the offer never offered (executeContainer, RecordLevel onward) and dropping the k-anonymity duty": """
ex:agreement\\/probe-b a odrl:Agreement ; odrl:profile <https://w3id.org/fdt/profile> ;
  odrl:target ex:dataset\\/noorderlicht-evt-registry ; odrl:assigner ex:party\\/noorderlicht-neurology ; odrl:assignee ex:party\\/stroke-network-oost-qi ;
  dspace:timestamp "2026-09-11T10:12:05Z"^^xsd:dateTime ; fdt-p:underNetwork ex:net\\/stroke-oost ;
  fdt-p:derivedFromOffer ex:offer\\/evt-registry-research ; fdt-p:derivedFromRequest ex:request\\/ttg-2026q3 ;
  odrl:permission [ a odrl:Permission ; odrl:action fdt-p:executeContainer ] ;
  odrl:permission [ a odrl:Permission ; odrl:action fdt-p:carryOnward ;
      odrl:constraint [ odrl:leftOperand fdt-p:onwardStateClass ; odrl:operator odrl:eq ; odrl:rightOperand fdt-p:RecordLevel ] ] .
""",
 "C: agreement whose target, assigner and network differ from the offer it claims to derive from": """
ex:agreement\\/probe-c a odrl:Agreement ; odrl:profile <https://w3id.org/fdt/profile> ;
  odrl:target ex:dataset\\/rav-rides ; odrl:assigner ex:party\\/jansen ; odrl:assignee ex:party\\/healthai ;
  dspace:timestamp "2026-09-11T10:12:05Z"^^xsd:dateTime ; fdt-p:underNetwork ex:net\\/personal-demo ;
  fdt-p:derivedFromOffer ex:offer\\/evt-registry-research ; fdt-p:derivedFromRequest ex:request\\/ttg-2026q3 ;
  odrl:permission [ a odrl:Permission ; odrl:action fdt-p:runQuery ] .
""",
 "D: agreement with no odrl:profile and no underNetwork": """
ex:agreement\\/probe-d a odrl:Agreement ;
  odrl:target ex:dataset\\/noorderlicht-evt-registry ; odrl:assigner ex:party\\/noorderlicht-neurology ; odrl:assignee ex:party\\/stroke-network-oost-qi ;
  dspace:timestamp "2026-09-11T10:12:05Z"^^xsd:dateTime ;
  fdt-p:derivedFromOffer ex:offer\\/evt-registry-research ; fdt-p:derivedFromRequest ex:request\\/ttg-2026q3 ;
  odrl:permission [ a odrl:Permission ; odrl:action fdt-p:runQuery ] .
""",
 "E: agreement derived from a request assigned to a DIFFERENT party than the agreement's assignee": """
ex:agreement\\/probe-e a odrl:Agreement ; odrl:profile <https://w3id.org/fdt/profile> ;
  odrl:target ex:dataset\\/noorderlicht-evt-registry ; odrl:assigner ex:party\\/noorderlicht-neurology ; odrl:assignee ex:party\\/healthai ;
  dspace:timestamp "2026-09-11T10:12:05Z"^^xsd:dateTime ; fdt-p:underNetwork ex:net\\/stroke-oost ;
  fdt-p:derivedFromOffer ex:offer\\/evt-registry-research ; fdt-p:derivedFromRequest ex:request\\/ttg-2026q3 ;
  odrl:permission [ a odrl:Permission ; odrl:action fdt-p:runQuery ] .
""",
 "F: offer with requiresManualApproval on BOTH true and false is caught? (maxCount 1)": """
ex:offer\\/probe-f a odrl:Offer ; odrl:profile <https://w3id.org/fdt/profile> ;
  odrl:target ex:dataset\\/rav-rides ; odrl:assigner ex:party\\/rav-oost-board ; fdt-p:policyKind fdt-p:AccessPolicy ;
  fdt-p:underNetwork ex:net\\/stroke-oost ; fdt-p:requiresManualApproval true, false ;
  odrl:permission [ a odrl:Permission ; odrl:action fdt-p:runQuery ] .
""",
 "G: request whose fdt-p:train is a dataset IRI, not a train (nodeKind only)": """
ex:request\\/probe-g a odrl:Request ; odrl:profile <https://w3id.org/fdt/profile> ;
  odrl:assignee ex:party\\/healthai ; fdt-p:train ex:dataset\\/rav-rides ; fdt-p:underNetwork ex:net\\/stroke-oost ;
  odrl:permission [ a odrl:Permission ; odrl:action fdt-p:runQuery ;
      odrl:constraint [ odrl:leftOperand odrl:purpose ; odrl:operator odrl:eq ; odrl:rightOperand <https://w3id.org/dpv#ResearchAndDevelopment> ] ] .
""",
}
for name, ttl in PROBES.items():
    g = rdflib.Graph()
    for f in base_files: g.parse(f, format="turtle")
    g.parse(data=PRE + ttl, format="turtle")
    conforms, _, text = pyshacl.validate(g, shacl_graph=shapes, inference="none", advanced=True)
    print(f"[{'CONFORMS' if conforms else 'violates'}] {name}")
    if not conforms:
        for line in text.splitlines():
            if "Message:" in line: print("      ", line.strip())

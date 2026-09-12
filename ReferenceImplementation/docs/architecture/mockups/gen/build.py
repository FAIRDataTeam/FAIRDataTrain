import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
import handler, station, system, itinerary, gateway, more

OUT = os.path.join(os.path.dirname(__file__), "..")
W, H = 1440, 1080
GX, GY = 1440 + 120, 1080 + 160

def write(name, html):
    html = html.replace("class=mono>", 'class="mono">').replace("class=faint>", 'class="faint">')
    with open(os.path.join(OUT, f"{name}.dc.html"), "w", encoding="utf-8") as f:
        f.write(html)

# Main = Handler run monitor (the screen that best shows the value: live itinerary map)
main_html = handler.h3()
write("Main", main_html)

order_h = ["HandlerTrains", "HandlerPlan", "HandlerRunReplay"]   # Main sits between Plan and Replay
order_s = ["StationDashboard", "StationJobs", "StationApprovals", "StationPolicy", "StationAgreement", "StationDatasets", "StationAudit", "StationSettings", "StationPublic"]
for k in order_h: write(k, handler.SCREENS[k]())
for k in order_s: write(k, (station.SCREENS.get(k) or more.SCREENS[k])())
for k, fn in itinerary.SCREENS.items(): write(k, fn())
for k, fn in gateway.SCREENS.items(): write(k, fn())
for k, fn in more.SCREENS.items():
    if k not in order_s: write(k, fn())
write("DesignSystem", system.SCREENS["DesignSystem"]())

artboards = []
# page 1: Handler — row of 4: Trains, Plan, Main (live run), Replay
row = ["HandlerTrains", "HandlerPlan", "Main", "HandlerRunReplay"]
row2 = ["HandlerRunDiscovery", "HandlerRunTwoPhase", "HandlerRunRounds", "HandlerRunComposition"]
grow = ["GatewayOverview", "GatewayResource", "GatewayCondition", "GatewayApproval"]
titles = {"HandlerTrains": "H1 · Trains catalogue", "HandlerPlan": "H2 · New plan (parameters, stations, itinerary map)",
          "Main": "H3 · Run monitor (live itinerary map)", "HandlerRunReplay": "H4 · Finished run (replay + results)",
          "StationDashboard": "S1 · Station dashboard (owner)", "StationJobs": "S2 · Jobs monitor (checkpoint timeline)",
          "StationApprovals": "S3 · Approvals inbox (controller)", "StationPolicy": "S4 · Access condition builder (controller)",
          "StationAgreement": "S5 · Agreement detail", "DesignSystem": "Design system sheet",
          "HandlerRunDiscovery": "H5 · Discovery-chain run (P4, time-to-groin)", "HandlerRunTwoPhase": "H6 · Two-phase run (P7)",
          "GatewayOverview": "G1 · Individual Gateway — overview", "GatewayResource": "G2 · Individual Gateway — resource detail",
          "HandlerRunRounds": "H7 · Iterative rounds (P5, v2 preview)", "HandlerRunComposition": "H8 · Composition run (P8) — completeness statement",
          "GatewayCondition": "G3 · Condition editor (per network)", "GatewayApproval": "G4 · Approval detail with run consequence",
          "StationDatasets": "S6 · Datasets (controller)", "StationAudit": "S7 · Audit explorer (auditor)", "StationSettings": "S8 · Station settings (owner)", "StationPublic": "S9 · Public catalogue page (unauthenticated)"}
for i, k in enumerate(row):
    artboards.append({"file": f"{k}.dc.html", "x": i * GX, "y": 0, "w": W, "h": H, "title": titles[k], "page": "handler"})
for i, k in enumerate(row2):
    artboards.append({"file": f"{k}.dc.html", "x": i * GX, "y": GY, "w": W, "h": H, "title": titles[k], "page": "handler"})
for i, k in enumerate(grow):
    artboards.append({"file": f"{k}.dc.html", "x": i * GX, "y": 0, "w": W, "h": H, "title": titles[k], "page": "gateway"})
for i, k in enumerate(order_s):
    x = (i % 3) * GX; y = (i // 3) * GY
    artboards.append({"file": f"{k}.dc.html", "x": x, "y": y, "w": W, "h": H, "title": titles[k], "page": "station"})
artboards.append({"file": "DesignSystem.dc.html", "x": 0, "y": 0, "w": W, "h": H, "title": titles["DesignSystem"], "page": "system"})

annotations = [
    {"id": "h-note", "page": "handler", "x": 0, "y": -150, "w": 640,
     "text": "Train Handler — data consumer / train owner view. H1–H4: pick a train, set parameters, choose stations (fan-out), watch the run on the itinerary map, replay it afterwards. Second row: H5 discovery chain (P4, time-to-groin), H6 two-phase (P7), H7 iterative rounds (P5, a v2 pattern — one station dropped for the remaining rounds), H8 composition (P8, cross-domain DAG with a pruned phase and the completeness statement). Conditions follow ADR-025 (JMESPath), outcomes and failure policy ADR-026 (both proposed)."},
    {"id": "h-map", "page": "handler", "x": 2 * GX, "y": -150, "w": 520,
     "text": "Itinerary map: appears once a plan is defined (H2), updates live while running (H3), becomes a time scrubber after the run (H4). Edge colour + label = state of that visit; dashed = not yet started."},
    {"id": "g-note", "page": "gateway", "x": 0, "y": -150, "w": 640,
     "text": "Individual Gateway — one controller (here an organisation, the Cardiology Research Group; the same screens serve a natural-person controller in the personal profile) across all stations hosting its data: resources, conditions per network, approvals, agreements, audit slice, revoke / suspend / withdraw (opt-out). G3: one condition per network, published to the hosting station. G4: the approval decision shown with what it does to the consumer’s run (refused ≠ not selected, ADR-026). ADR-017/018, register A8, C8, G8."},
    {"id": "s-note", "page": "station", "x": 0, "y": -150, "w": 640,
     "text": "Data Station console — one app, role-based views (owner / controller / auditor). S1–S2 are owner views; S3–S6 controller views (Cardiology Research Group); S7 auditor; S8 owner settings; S9 the public, unauthenticated catalogue page. This completes the ten screens of the July brief. Sample data follows the brief; every state pairs colour, icon and label."},
    {"id": "s-flow", "page": "station", "x": 2 * GX, "y": GY, "w": 520,
     "text": "Approval journey to demo: S3 approve request agr-8f24 → it becomes an active agreement like agr-8f19 in S5 (lifecycle, jobs under it) → its jobs appear in S2 with checkpoint decisions → results reach the consumer on the Handler side (H4). Bracketed items such as [METC ref.] are placeholders, not facts."},
]
canvas = {"artboards": artboards, "annotations": annotations,
          "pages": [{"id": "handler", "name": "Train Handler"}, {"id": "gateway", "name": "Individual Gateway"}, {"id": "station", "name": "Data Station"}, {"id": "system", "name": "Design system"}],
          "launch": {"view": "canvas", "page": "handler"}}
with open(os.path.join(OUT, "canvas.json"), "w") as f:
    json.dump(canvas, f, indent=2)
print("built", len(artboards), "artboards")

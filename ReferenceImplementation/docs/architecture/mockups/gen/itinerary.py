from base import *
from handler import map_svg

# ---- H5 Discovery-chain run (P4 time-to-groin) ------------------------------------------
def h5():
    nodes = {
        "h":  dict(x=130, y=155, label="Train Handler", sub="Stroke network Oost · orchestrator", kind="handler"),
        "evt": dict(x=400, y=155, label="Noorderlicht MC", sub="EVT centre · hop 1", state="delivered", note="214 pts"),
        "lnk": dict(x=670, y=155, label="Linkage station Oost", sub="pseudonym translation · hop 2", state="delivered", note="pseudonyms"),
        "rav": dict(x=940, y=58, label="Ambulancezorg Oost", sub="ride registration · hop 3", state="pending", note="since 10:44"),
        "zui": dict(x=940, y=155, label="Zuiderlicht MC", sub="referring stroke centre · hop 3", state="running", note="since 10:46"),
        "hap": dict(x=940, y=252, label="Huisartsenpost Oost", sub="last-known-well · hop 4, optional", state="queued", note="discovered", dim=True),
    }
    edges = [("h", "evt", "delivered", ""), ("evt", "lnk", "delivered", ""), ("lnk", "rav", "pending", ""),
             ("lnk", "zui", "running", ""), ("zui", "hap", "queued", "")]
    mapcard = card(f'<div style="padding:8px">{map_svg(nodes, edges, w=1136, h=290, nw=220, note_top=True, note="Live · 10:49:02 · stations after hop 1 were named by the EVT centre’s result; each hop negotiates its own agreement (ADR-014)")}</div>',
                   title="Itinerary map — discovery chain", aside=f'<div style="display:flex;gap:8px">{btn("Replay", "secondary", "skipb")}{btn("Stop run", "danger", "stop")}</div>', style="flex:0 0 auto")
    budget = card(f'''<div style="padding:14px 18px;display:flex;flex-direction:column;gap:12px">
        <div style="display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px">
          <div><div class="label">Hops</div><div style="font-family:'Source Serif 4',Georgia,serif;font-size:26px;font-weight:600">3 <span class="muted" style="font-size:14px;font-weight:400">of max 4</span></div></div>
          <div><div class="label">Stations</div><div style="font-family:'Source Serif 4',Georgia,serif;font-size:26px;font-weight:600">5 <span class="muted" style="font-size:14px;font-weight:400">of max 40</span></div></div>
          <div><div class="label">Deadline</div><div style="font-family:'Source Serif 4',Georgia,serif;font-size:26px;font-weight:600">15 Oct</div></div>
        </div>
        <div style="font-size:13px"><b>Stop</b> <span class="muted">— onset found for every patient, or nothing discovered and nothing pending</span> · <b>Failure policy</b> <span class="muted">— refused / timed out (2 d): skip branch · failed: retry once · completeness ≥ 2 stations</span></div>
        <div style="display:flex;gap:10px;align-items:flex-start;padding:10px 12px;background:{PAL["amber_tint"]};border-radius:6px;font-size:13px">{icon("clock",16,PAL["amber"])}<span><b>Waiting for approval at Regio Oost Ambulancezorg</b> — controller decides within 47 h; the referring-centre branch continues meanwhile.</span></div>
        <div style="display:flex;gap:10px;align-items:flex-start;font-size:13px">{icon("lock",16,PAL["green"])}<span><b>What left each station:</b> Noorderlicht MC → 214 pseudonyms + aggregates (inspected at PEP 3); Linkage station → translated pseudonyms only. <b>Handler holds</b> aggregates and next-hop lists only.</span></div>
      </div>''', title="Budget, stop condition and onward state")
    agreements = card(f'''<div style="padding:4px 6px 0">{table(["Hop", "Station", "Agreement", "State"], [
        ["1", "<b>Noorderlicht MC</b>", '<span class="mono">agr-9a01</span>', badge("active")],
        ["2", "<b>Linkage station Oost</b>", '<span class="mono">agr-9a02</span>', badge("active")],
        ["3", "<b>Ambulancezorg Oost</b>", '<span class="mono">req-9a03</span>', badge("pending")],
        ["3", "<b>Zuiderlicht MC</b>", '<span class="mono">agr-9a04</span>', badge("active")],
        ["4", "<b>Huisartsenpost Oost</b>", '<span class="faint">not requested yet</span>', badge("queued", "Discovered")],
      ], widths=["44px", "", "100px", "160px"])}</div>''', title="Agreements — one per hop")
    onward = card(f'''<div style="padding:14px 18px;display:flex;flex-direction:column;gap:10px;font-size:13px">
        <div style="display:flex;gap:10px;align-items:flex-start">{icon("lock",16,PAL["green"])}<span><b>What left each station:</b> Noorderlicht MC → 214 pseudonyms + aggregate counts (no record-level fields, inspected at PEP 3); Linkage station → translated pseudonyms only.</span></div>
        <div style="display:flex;gap:10px;align-items:flex-start">{icon("eye",16,PAL["muted"])}<span><b>What the Handler holds:</b> aggregates and next-hop lists only (ADR-015).</span></div>
        <div style="display:flex;gap:10px;align-items:flex-start">{icon("file",16,PAL["muted"])}<span><b>Delivered so far:</b> door-to-groin distribution (median 46 min, n = 214) vs NVN/NVvR norm &lt; 30 / &lt; 75 min.</span></div>
      </div>''', title="Onward state and results")
    agreements = agreements.replace("<td>", '<td style="padding:8px 12px">')
    body = (f'<div style="display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px">'
            f'{kpi("Run state", "Waiting", state="waiting")}{kpi("Pattern", "Discovery chain", sub="P4 · orchestrated · quarterly (P9)")}'
            f'{kpi("Visits", "5", sub="2 delivered · 1 running · 1 waiting · 1 discovered")}{kpi("Started", "10:00", sub="today · elapsed 49 min")}</div>'
            f'{mapcard}'
            f'<div style="display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:18px;min-height:0">{budget}{agreements}</div>')
    return shell("handler", "Runs", "Time-to-groin — region Oost · run 2026-Q3", body, role="Train owner", org="Stroke network Oost — QI group", user="R. Bakker",
                 crumbs=["Runs", "Time-to-groin 2026-Q3"], subtitle="Plan “Time-to-groin — region Oost, per quarter” · period 2026-Q2 · benchmark norms NVN/NVvR 2021", badge_count={"Runs": 1})

# ---- H6 Two-phase run (P7) -----------------------------------------------------------------
def h6():
    labels = [("Noorderlicht MC", "n = 134"), ("UT Data Station", "n = 88"), ("Zuiderlicht MC", "n = 61"),
              ("Academic Hospital", "n = 12"), ("Regional Clinic", "n = 7"), ("Oosterlicht Kliniek", "n = 0")]
    states = ["running", "running", "delivered", "skipped", "skipped", "skipped"]
    notes = ["phase 2 · 03:12", "phase 2 · 02:40", "phase 2 · 10:52", "below threshold", "below threshold", "below threshold"]
    nodes = {"h": dict(x=140, y=290, label="Train Handler", sub="EU-CardioNet · orchestrator", kind="handler"),
             "cond": dict(x=470, y=290, label="Phase 1 → condition", sub="phase1.count ≥ 50 · 6 counts in", kind="handler")}
    ys = [60, 152, 244, 336, 428, 520]
    for i, ((lab, sub), st, nt) in enumerate(zip(labels, states, notes)):
        nodes[f"s{i}"] = dict(x=830, y=ys[i], label=lab, sub=sub, state=st, note=nt, dim=(st == "skipped"))
    edges = [("h", "cond", "delivered", "")] + [("cond", f"s{i}", states[i] if states[i] != "skipped" else "queued", "") for i in range(6)]
    phases = (f'<div style="display:flex;align-items:center;gap:12px;padding:12px 18px;border-bottom:1px solid {PAL["line2"]}">'
              f'<span class="chip" style="background:{PAL["green_tint"]};color:{PAL["green"]}">{icon("check",13)}<span>Phase 1 · Feasibility count · 6 stations (directory query) · done 10:41</span></span>'
              f'{icon("chev",16,PAL["muted"])}<span class="chip" style="background:{PAL["blue_tint"]};color:{PAL["blue"]}">{icon("swap",13)}<span>Condition · phase1.count ≥ 50 → 3 of 6 selected</span></span>'
              f'{icon("chev",16,PAL["muted"])}<span class="chip">{icon("play",13)}<span>Phase 2 · Analysis · 3 stations · running</span></span></div>')
    mapcard = card(f'{phases}<div style="padding:8px">{map_svg(nodes, edges, w=1136, h=590, nw=220, note="Stations below the threshold were not sent the analysis train; only their counts (aggregates) reached the Handler")}</div>',
                   title="Itinerary map — two-phase conditional", aside=f'<div style="display:flex;gap:8px">{btn("Replay", "secondary", "skipb")}{btn("Stop run", "danger", "stop")}</div>', style="flex:0 0 auto")
    body = (f'<div style="display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px">'
            f'{kpi("Run state", "Running", state="running")}{kpi("Pattern", "Two-phase", sub="P7 · orchestrated · target set from directory query")}'
            f'{kpi("Phase 1", "6 / 6", sub="counts delivered · 3 above threshold")}{kpi("Phase 2", "1 / 3", sub="delivered · 2 running")}</div>{mapcard}')
    return shell("handler", "Runs", "Heart-failure phenotyping · feasibility → analysis", body, role="Train owner",
                 crumbs=["Runs", "HF phenotyping #3"], subtitle="Plan “Feasibility count, then analysis where n ≥ 50” · stations resolved at dispatch: mechanism = FHIR, theme = heart failure, network = health research NL",
                 badge_count={"Runs": 2})

SCREENS = {"HandlerRunDiscovery": h5, "HandlerRunTwoPhase": h6}

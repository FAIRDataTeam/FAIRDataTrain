from base import *

# ---- itinerary map (SVG) ----------------------------------------------------
def map_svg(nodes, edges, w=636, h=430, note=None, ghost=False, nw=200, note_top=False):
    """nodes: id -> dict(x,y,label,sub,state,kind,note)   edges: list of (a,b,state,label) — label unused"""
    hw = nw // 2
    out = [f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" style="display:block;font-family:Source Sans 3,system-ui,sans-serif">']
    out.append('<defs>' + "".join(
        f'<marker id="arr-{k}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse">'
        f'<path d="M0 0L10 5 0 10z" fill="{PAL[k]}"/></marker>' for k in ["grey", "blue", "amber", "green", "red", "teal"]) + '</defs>')
    out.append(f'<rect width="{w}" height="{h}" fill="{PAL["surface"]}"/>')
    for a, b, st, lab in edges:
        A, B = nodes[a], nodes[b]
        col = STATES[st][1]
        x1, y1 = A["x"] + hw, A["y"]; x2, y2 = B["x"] - hw, B["y"]
        cx = (x1 + x2) / 2
        dash = ' stroke-dasharray="6 6"' if st in ("queued", "requested", "pending", "scheduled") else ""
        dimmed = ghost or B.get("dim")
        out.append(f'<path d="M{x1} {y1} C {cx} {y1}, {cx} {y2}, {x2} {y2}" fill="none" stroke="{PAL[col]}" stroke-width="2"{dash} marker-end="url(#arr-{col})" opacity="{0.4 if dimmed else 1}"/>')
        if lab:
            out.append(f'<text x="{(x1+x2)/2}" y="{(y1+y2)/2 - 8}" text-anchor="middle" font-size="11.5" fill="{PAL["muted"]}">{lab}</text>')
    for nid, n in nodes.items():
        st = n.get("state"); col = PAL[STATES[st][1]] if st else PAL["line"]
        x, y = n["x"], n["y"]
        kind = n.get("kind", "station")
        fill = PAL["handler_tint"] if kind == "handler" else PAL["surface"]
        stroke = PAL["handler"] if kind == "handler" else col
        sub = n["sub"]; maxc = int((nw - 46) / 6.1)
        if len(sub) > maxc: sub = sub[:maxc - 1].rstrip() + "…"
        label = n["label"]; maxl = int((nw - 46) / 8.2)
        if len(label) > maxl: label = label[:maxl - 1].rstrip() + "…"
        out.append(f'<g opacity="{0.5 if (ghost and st in ("queued","scheduled")) or n.get("dim") else 1}">')
        out.append(f'<rect x="{x-hw}" y="{y-30}" width="{nw}" height="60" rx="8" fill="{fill}" stroke="{stroke}" stroke-width="{2 if kind!="handler" else 1.5}"/>')
        ic = "train" if kind == "handler" else "station"
        out.append(f'<g transform="translate({x-hw+12},{y-20})">{icon(ic, 18, PAL["handler"] if kind=="handler" else PAL["muted"])}</g>')
        out.append(f'<text x="{x-hw+38}" y="{y-6}" font-size="13.5" font-weight="600" fill="{PAL["ink"]}">{label}</text>')
        out.append(f'<text x="{x-hw+38}" y="{y+12}" font-size="11.5" fill="{PAL["muted"]}">{sub}</text>')
        if st and kind != "handler":
            lab, ck, ick = STATES[st]
            if n.get("note"): lab = lab + " · " + n["note"]
            bw = int(len(lab) * 6.3 + 32)
            out.append(f'<g transform="translate({x-hw},{y+38})"><rect width="{bw}" height="20" rx="10" fill="{PAL[ck+"_tint"]}"/>'
                       f'<g transform="translate(7,3)">{icon(ick, 13, PAL[ck], 2)}</g>'
                       f'<text x="25" y="14" font-size="11.5" font-weight="600" fill="{PAL[ck]}">{lab}</text></g>')
        out.append('</g>')
    if note:
        out.append(f'<text x="16" y="{18 if note_top else h-14}" font-size="12" fill="{PAL["faint"]}">{note}</text>')
    out.append('</svg>')
    return "".join(out)

def stations_nodes(states, hx=120, sx=470, ys=(90, 220, 350), labels=None, notes=None, hsub="EU-CardioNet · orchestrator"):
    labels = labels or [("UT Data Station", "Rare disease variants"),
                        ("Radboudumc Station", "Cardiogenetics graph"),
                        ("Noorderlicht MC", "Clinical genetics annotations")]
    notes = notes or [None] * len(states)
    nodes = {"h": dict(x=hx, y=ys[1], label="Train Handler", sub=hsub, kind="handler")}
    for i, ((lab, sub), st, nt) in enumerate(zip(labels, states, notes)):
        nodes[f"s{i}"] = dict(x=sx, y=ys[i], label=lab, sub=sub, state=st, note=nt)
    return nodes

TYPE_ICON = {"SPARQL": "code", "SQL": "db", "FHIR": "api", "Docker": "box", "Python": "code"}

def train_card(title, ttype, mech, garage, params, stations, desc, selected=False, note=None):
    bd = PAL["handler"] if selected else PAL["line"]
    n = f'<div style="margin-top:8px;font-size:12.5px;color:{PAL["amber"]};display:flex;gap:6px;align-items:center">{icon("alert",14,PAL["amber"])}<span>{note}</span></div>' if note else ""
    return (f'<div class="card" style="padding:16px 18px;border-color:{bd};display:flex;flex-direction:column;gap:8px;{"box-shadow:0 0 0 2px "+PAL["handler_tint"] if selected else ""}">'
            f'<div style="display:flex;justify-content:space-between;align-items:flex-start;gap:10px"><h3>{title}</h3>'
            f'<span class="chip" style="height:22px;font-size:12px;white-space:nowrap;flex:0 0 auto">{icon(TYPE_ICON[ttype],13)}<span>{ttype} · {mech}</span></span></div>'
            f'<div class="muted" style="font-size:13px;min-height:38px">{desc}</div>'
            f'<div style="display:flex;flex-wrap:wrap;gap:4px 10px;font-size:12.5px;color:{PAL["muted"]};margin-top:2px">'
            f'<span style="white-space:nowrap">{garage}</span><span style="white-space:nowrap">· {params} parameter{"s" if params!=1 else ""}</span><span style="white-space:nowrap">· {stations} compatible stations</span></div>{n}</div>')

# ---- H1 Train catalogue ---------------------------------------------------------
def h1():
    filters = (f'<div style="display:flex;gap:10px;align-items:center">'
               f'<span class="input" style="width:200px;justify-content:space-between"><span>All garages</span>{icon("chevd",14)}</span>'
               f'<span class="input" style="width:200px;justify-content:space-between"><span>All train types</span>{icon("chevd",14)}</span>'
               f'<span class="input" style="width:220px;justify-content:space-between"><span>Compatible with: any station</span>{icon("chevd",14)}</span>'
               f'<span class="chip">{icon("check",13)}<span>Parametrisable</span></span>'
               f'<span class="muted" style="margin-left:auto;font-size:13px">6 trains · synced 09:12 from 4 garages</span></div>')
    grid = '<div style="display:grid;grid-template-columns:repeat(2, minmax(0,1fr));gap:14px;align-content:start">' + "".join([
        train_card("Gene–disease associations", "SPARQL", "Query", "FDT Community Garage", 4, 4,
                   "Finds diseases associated with given genes (or genes for given diseases) from annotation graphs.", selected=True),
        train_card("Heart-failure cohort count", "FHIR", "API", "FDT Community Garage", 3, 6,
                   "Counts patients matching diagnosis codes in a period; returns aggregate only."),
        train_card("Cardiac MRI feature extraction", "Docker", "Container", "Cardiology Garage", 1, 2,
                   "Runs a containerised model over local imaging features; returns per-cohort summaries."),
        train_card("Time-to-groin discovery", "Docker", "Container", "Stroke Network Garage", 2, 3,
                   "Traces symptom onset → groin puncture across hospitals and ambulance services.",
                   note="Discovery-chain itinerary (P4) · orchestrated or choreographed"),
        train_card("Air-quality exposure by postcode area", "SQL", "Query", "Environment Data Garage", 2, 2,
                   "Modelled NO₂ / PM2.5 exposure per postcode area and year — for cross-domain health–environment studies."),
        train_card("Federated logistic regression", "Python", "Script", "Cardiology Garage", 4, 2,
                   "Iterative model fitting across stations; aggregator combines rounds.",
                   note="Iterative rounds (P5) · planned for v2"),
    ]) + '</div>'
    detail = card(f'''
      <div style="padding:18px;display:flex;flex-direction:column;gap:12px">
        <div><div class="label">Selected train</div><h2 style="margin-top:4px">Gene–disease associations</h2>
          <div class="muted" style="font-size:13px;margin-top:2px">v1.3 · provided by SCS group (UT)</div></div>
        <dl class="kv" style="grid-template-columns:120px minmax(0,1fr)">
          <dt>Type</dt><dd>{icon("code",14)} SPARQL query train (<span class=mono>fdt-o:SPARQLTrain</span>)</dd>
          <dt>Returns</dt><dd>Tabular result (CSV), aggregate — no record-level data</dd>
          <dt>Requests</dt><dd>Action <em>run query</em> · purpose <em>approved research</em></dd>
        </dl>
        <div><div class="label" style="margin-bottom:8px">Parameters</div>
          {table(["Name", "Type", "Default"], [
              ["<b>mode</b>", "enum (2 values)", "genes→diseases"],
              ["<b>terms</b>", "gene symbols / disease IRIs", "—"],
              ["<b>min_evidence</b>", "integer ≥ 1", "1"],
              ["<b>limit</b>", "rows per station", "10 000"]])}
        </div>
        <div><div class="label" style="margin-bottom:8px">Payload (template)</div>
          <pre class="mono" style="margin:0;padding:12px;background:{PAL["ground"]};border-radius:6px;font-size:12px;line-height:1.5;white-space:pre-wrap">SELECT ?disease (COUNT(?ev) AS ?n) WHERE &#123;
  VALUES ?sym &#123; $terms &#125; ?g rdfs:label ?sym .
  ?ev :gene ?g ; :disease ?disease &#125;
GROUP BY ?disease HAVING (?n &gt;= $min_evidence)</pre></div>
        <div style="display:flex;gap:10px;margin-top:auto">{btn("Plan a run", "primary", "map")}{btn("Compatible stations", "secondary", "station")}</div>
      </div>''', style="display:flex;flex-direction:column")
    body = f'{filters}<div style="display:grid;grid-template-columns:minmax(0,1fr) 400px;gap:18px;flex:1;min-height:0">{grid}{detail}</div>'
    return shell("handler", "Trains", "Trains", body, role="Train owner",
                 subtitle="Trains available from your garages. Select one to see its parameters and plan a run.",
                 actions=btn("Add garage", "secondary", "plus"))

# ---- H2 Plan a run (parametrised submission) --------------------------------------
def h2():
    steps = stepper(["Train", "Parameters", "Stations", "Review &amp; run"], 3)
    params = card(f'''
      <div style="padding:18px;display:grid;grid-template-columns:200px minmax(0,1fr) 170px;gap:18px 28px">
        <div><div class="label" style="margin-bottom:8px">Mode</div>
          <div style="display:flex;flex-direction:column;gap:8px">
            <label style="display:flex;gap:10px;align-items:center"><span style="width:18px;height:18px;border-radius:50%;border:5px solid {PAL["handler"]};display:inline-block"></span><span><b>Genes → related diseases</b></span></label>
            <label style="display:flex;gap:10px;align-items:center;color:{PAL["muted"]}"><span style="width:18px;height:18px;border-radius:50%;border:1.5px solid {PAL["line"]};display:inline-block"></span><span>Diseases → related genes</span></label>
          </div></div>
        <div><div class="label" style="margin-bottom:8px">Gene symbols</div>
          <div class="input" style="height:auto;min-height:36px;padding:5px 8px;flex-wrap:wrap;gap:6px">
            <span class="chip" style="height:24px">TTN {icon("x",12)}</span><span class="chip" style="height:24px">MYH7 {icon("x",12)}</span><span class="chip" style="height:24px">LMNA {icon("x",12)}</span>
            <span class="faint">Add symbol…</span></div>
          <div class="faint" style="font-size:12px;margin-top:6px">Validated against HGNC symbols · 3 of max 50</div></div>
        <div style="display:flex;flex-direction:column;gap:14px"><div><div class="label" style="margin-bottom:8px">Min. evidence count</div><span class="input" style="width:120px">2</span></div>
        <div><div class="label" style="margin-bottom:8px">Result limit / station</div><span class="input" style="width:120px">5 000 rows</span></div></div>
      </div>''', title="Parameters — Gene–disease associations v1.3", aside=f'<a href="#">Edit train choice</a>')
    def chk(on=True):
        return (f'<span style="display:inline-block;width:16px;height:16px;border-radius:4px;background:{PAL["handler"]}">{icon("check",16,"#fff",2.5)}</span>' if on
                else f'<span style="display:inline-block;width:16px;height:16px;border-radius:4px;border:1.5px solid {PAL["line"]}"></span>')
    def st_cell(name, dataset, conds):
        return (f'<b>{name}</b> <span class="muted" style="font-size:12.5px">· {dataset}</span>'
                f'<div style="font-size:13px;margin-top:3px">{conds}</div>')
    st_rows = [
        [chk(), st_cell("UT Data Station", "Rare disease variants · SCS group",
                        policy_sentence([("Allows", "<em>run query</em> for approved research", "green"), ("prohibits", "commercial use", "red")])), "SPARQL", badge("enabled", "Auto-match")],
        [chk(), st_cell("Radboudumc Station", "Cardiogenetics graph · Human Genetics",
                        policy_sentence([("Allows", "<em>run query</em> for approved research", "green"), ("requires", "controller approval per agreement", "amber")])), "SPARQL", badge("pending", "Approval required")],
        [chk(), st_cell("Noorderlicht MC", "Clinical genetics annotations",
                        policy_sentence([("Allows", "<em>run query</em> for approved research", "green"), ("requires", "result deletion within 30 days", "amber")])), "SPARQL", badge("enabled", "Auto-match")],
        [chk(False), st_cell("Erasmus MC Station", "Variant knowledge base", "<span class='faint'>Access conditions unavailable — station unreachable</span>"), "SPARQL", badge("unreachable")],
    ]
    stations = card(f'<div style="padding:4px 6px 0">{table(["", "Station · dataset · access conditions", "Mechanism", "Matching"], st_rows, widths=["32px","","90px","160px"])}</div>',
                    title="Stations — 3 of 4 compatible selected", aside=f'<span class="muted" style="font-size:13px">advertising <span class=mono>fdt-inst:SPARQL</span></span>')
    nodes = stations_nodes(["scheduled", "scheduled", "scheduled"], hx=100, sx=310, ys=(60, 160, 260), hsub="EU-CardioNet",
                           labels=[("UT Data Station", "Rare disease variants"), ("Radboudumc", "Cardiogenetics graph"), ("Noorderlicht MC", "Clinical genetics")])
    edges = [("h", "s0", "scheduled", ""), ("h", "s1", "scheduled", ""), ("h", "s2", "scheduled", "")]
    summary = card(f'''
      <div style="padding:16px 18px;display:flex;flex-direction:column;gap:14px">
        <div><div class="label">Itinerary</div>
          <div style="margin-top:6px;display:flex;align-items:center;gap:8px"><b>Fan-out</b><span class="muted">— same train to 3 stations, simultaneously</span></div>
          <div class="faint" style="font-size:12px;margin-top:4px">Other patterns: sequence, discovery chain, two-phase, composition (v1) · rounds, hierarchy (v2)</div></div>
        {map_svg(nodes, edges, w=404, h=330, ghost=True, nw=180)}
        <dl class="kv" style="grid-template-columns:110px minmax(0,1fr);font-size:13px">
          <dt>Purpose</dt><dd>Approved research — cardiomyopathy genetics study <span class="faint">[METC ref.]</span></dd>
          <dt>Consumer</dt><dd>EU-CardioNet consortium · M. de Vries (Radboudumc)</dd>
          <dt>Start</dt><dd>Now · results kept 30 days · artifacts not published</dd>
        </dl>
        <div style="display:flex;gap:10px;margin-top:4px">{btn("Create plan and run", "primary", "play")}{btn("Save plan only", "secondary")}</div>
      </div>''', title="Plan summary")
    body = (f'{steps}<div style="display:grid;grid-template-columns:minmax(0,1fr) 440px;gap:18px;flex:1;min-height:0">'
            f'<div style="display:flex;flex-direction:column;gap:18px">{params}{stations}</div>{summary}</div>')
    return shell("handler", "Plans", "New plan", body, role="Train owner", crumbs=["Plans", "New plan"],
                 subtitle="Choose a train, set its parameters, pick the stations — the itinerary map shows what will be visited.")

# ---- H3 Run monitor (live map) ----------------------------------------------------
def h3():
    nodes = stations_nodes(["delivered", "pending", "running"], notes=["10:47 · 1 204 rows", "since 10:44", "since 10:46"], ys=(130, 300, 470))
    edges = [("h", "s0", "delivered", ""), ("h", "s1", "pending", ""), ("h", "s2", "running", "")]
    mapcard = card(f'<div style="padding:8px">{map_svg(nodes, edges, w=636, h=590, nw=220, note="Live · updated 10:49:02 · edge and badge colour follow the state of each visit")}</div>',
                   title="Itinerary map", aside=f'<div style="display:flex;gap:8px">{btn("Replay", "secondary", "skipb")}{btn("Stop run", "danger", "stop")}</div>')
    def checkpoints(done, current=None, failed=None):
        names = ["Arrival", "Agreement", "Execute", "Inspect", "Deliver"]
        out = '<div style="display:flex;align-items:center;gap:4px">'
        for i, n in enumerate(names):
            if i < done: col, ic = PAL["green"], "check"
            elif i == current: col, ic = PAL["amber" if n == "Agreement" else "teal"], "clock" if n == "Agreement" else "play"
            else: col, ic = PAL["line"], "circle"
            out += f'<span title="{n}" style="display:inline-flex">{icon(ic, 15, col, 2)}</span>'
            if i < 4: out += f'<span style="width:12px;height:1px;background:{PAL["line"]}"></span>'
        return out + '</div>'
    jobs = card(f'''
      <div style="padding:4px 6px 0">{table(["Station", "Checkpoints", "State"], [
        ["<b>UT Data Station</b><div class='muted mono' style='font-size:11.5px'>agr-8f21 · 04:51</div>", checkpoints(5), badge("delivered")],
        ["<b>Radboudumc Station</b><div class='muted mono' style='font-size:11.5px'>agr-8f22 · 05:06</div>", checkpoints(1, 1), badge("pending")],
        ["<b>Noorderlicht MC</b><div class='muted mono' style='font-size:11.5px'>agr-8f23 · since 10:46</div>", checkpoints(2, 2), badge("running")],
      ], widths=["190px", "", "150px"])}</div>''', title="Visits (3 jobs)", style="flex:0 0 auto")
    feed_rows = [
        ("10:46:31", "Noorderlicht MC", "Checkpoint 2 passed — agreement <span class=mono>agr-8f23</span> active, quotas satisfied; query executing"),
        ("10:47:12", "UT Data Station", "Results delivered — checkpoint 3 passed: aggregate table, 1 204 rows, no record-level fields"),
        ("10:44:30", "Radboudumc Station", "Agreement matched; controller approval required (Dept. of Human Genetics) — timeout in 47 h"),
        ("10:42:05", "Train Handler", "Run #14 started · train dispatched to 3 stations (push: 2, poll: 1)"),
    ]
    feed = card('<div style="padding:6px 18px 10px;display:flex;flex-direction:column">' + "".join(
        f'<div style="display:flex;flex-direction:column;gap:2px;padding:9px 0;border-bottom:1px solid {PAL["line2"]};font-size:13px">'
        f'<div style="display:flex;gap:10px"><span class="mono muted">{t}</span><span style="font-weight:600">{who}</span></div><span>{what}</span></div>' for t, who, what in feed_rows) + '</div>',
        title="Events", aside='<a href="#">Open full log</a>')
    body = (f'<div style="display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px">'
            f'{kpi("Run state", "Running", state="running")}{kpi("Visits", "3", sub="1 delivered · 1 running · 1 waiting")}'
            f'{kpi("Waiting for approval", "1", sub="Radboudumc · since 10:44")}{kpi("Started", "10:42", sub="today · elapsed 06:57")}</div>'
            f'<div style="display:grid;grid-template-columns:minmax(0,1fr) 480px;gap:18px;flex:1;min-height:0">{mapcard}'
            f'<div style="display:flex;flex-direction:column;gap:18px;min-height:0">{jobs}{feed}</div></div>')
    return shell("handler", "Runs", "Gene–disease associations · run #14", body, role="Train owner",
                 crumbs=["Runs", "Run #14"], subtitle="Plan “Cardiomyopathy genes, 3 stations” · parameters: genes → diseases · TTN, MYH7, LMNA",
                 badge_count={"Runs": 1})

# ---- H4 Finished run: results + replay -------------------------------------------
def h4():
    nodes = stations_nodes(["delivered", "active", "delivered"], notes=["10:47", "approved 11:36", "10:52"], ys=(80, 200, 320))
    edges = [("h", "s0", "delivered", ""), ("h", "s1", "active", ""), ("h", "s2", "delivered", "")]
    # scrubber
    events = [("10:42:05", "grey"), ("10:42:58", "green"), ("10:44:30", "amber"), ("10:46:31", "teal"), ("10:47:12", "green"),
              ("10:52:01", "green"), ("11:36:10", "green"), ("11:36:15", "teal"), ("11:39:48", "green"), ("11:39:50", "green")]
    ticks = ""
    for i, (t, c) in enumerate(events):
        x = 20 + i * (500 / (len(events) - 1))
        cur = i == 6
        ticks += (f'<circle cx="{x}" cy="24" r="{7 if cur else 5}" fill="{PAL[c]}" stroke="{PAL["surface"]}" stroke-width="2"/>'
                  + (f'<line x1="{x}" y1="0" x2="{x}" y2="48" stroke="{PAL["ink"]}" stroke-width="1.5"/>' if cur else ""))
    scrub = (f'<div style="padding:10px 18px 14px;display:flex;flex-direction:column;gap:8px">'
             f'<div style="display:flex;align-items:center;gap:14px">'
             f'<div style="display:flex;gap:6px">{btn("", "secondary", "skipb", title="Previous step")}{btn("", "primary", "play", title="Play")}{btn("", "secondary", "skipf", title="Next step")}</div>'
             f'<div style="flex:1"><svg width="540" height="48" viewBox="0 0 540 48" style="display:block"><line x1="20" y1="24" x2="520" y2="24" stroke="{PAL["line"]}" stroke-width="3"/>'
             f'<line x1="20" y1="24" x2="{20 + 6 * (500/9)}" y2="24" stroke="{PAL["handler"]}" stroke-width="3"/>{ticks}</svg></div>'
             f'<span class="mono muted" style="width:90px;text-align:right">step 7 / 10</span></div>'
             f'<div style="display:flex;gap:12px;align-items:baseline;padding-left:4px;font-size:13.5px"><span class="mono" style="font-weight:600">11:36:10</span>'
             f'<span><b>Radboudumc Station</b> — controller (Dept. of Human Genetics) approved agreement <span class=mono>agr-8f22</span>; state <em>pending approval → active</em>. Execution starts at the next step.</span></div></div>')
    steps = [
        ("1", "10:42:05", "Train Handler", "Run started · dispatched to 3 stations", "grey"),
        ("2", "10:42:58", "UT Data Station", "Agreement agr-8f21 active (auto-matched)", "green"),
        ("3", "10:44:30", "Radboudumc Station", "Matched · waiting for controller approval", "amber"),
        ("4", "10:46:31", "Noorderlicht MC", "Executing (checkpoint 2 passed)", "teal"),
        ("5", "10:47:12", "UT Data Station", "Results delivered · inspection passed · 1 204 rows", "green"),
        ("6", "10:52:01", "Noorderlicht MC", "Results delivered · inspection passed · 302 rows", "green"),
        ("7", "11:36:10", "Radboudumc Station", "Approved by controller · agreement active", "green"),
        ("8", "11:36:15", "Radboudumc Station", "Executing (checkpoint 2 passed)", "teal"),
        ("9", "11:39:48", "Radboudumc Station", "Results delivered · inspection passed · 1 912 rows", "green"),
        ("10", "11:39:50", "Train Handler", "Run finished · 3 of 3 delivered · merged result ready", "green"),
    ]
    steplist = '<div style="border-top:1px solid ' + PAL["line2"] + ';padding:6px 18px 8px;display:flex;flex-direction:column">' + "".join(
        f'<div style="display:flex;gap:10px;align-items:center;padding:3px 8px;border-radius:6px;font-size:12.5px;line-height:18px;{"background:"+PAL["handler_tint"]+";font-weight:600" if n=="7" else ""}">'
        f'<span style="width:8px;height:8px;border-radius:50%;background:{PAL[c]};flex:0 0 8px"></span><span class="mono muted" style="width:56px">{t}</span>'
        f'<span style="width:150px;flex:0 0 150px">{who}</span><span class="muted">{what}</span></div>'
        for n, t, who, what, c in steps) + '</div>'
    mapcard = card(f'<div style="padding:8px 8px 0">{map_svg(nodes, edges, w=636, h=396, nw=220, note_top=True, note="Replay · map shows the run as it was at 11:36:10 (step 7 of 10)")}</div>{scrub}{steplist}',
                   title="Itinerary replay", aside=f'<span class="muted" style="font-size:13px">Finished 11:39:50 · total 57 min 45 s (52 min waiting for approval)</span>')
    artifacts = card(f'''<div style="padding:4px 6px 0">{table(["Station", "Artifact", "Rows", "Inspection"], [
        ["<b>UT Data Station</b>", '<a href="#">gene-disease.csv</a> <span class="faint">38 KB</span>', "1 204", badge("delivered", "Passed")],
        ["<b>Radboudumc Station</b>", '<a href="#">gene-disease.csv</a> <span class="faint">61 KB</span>', "1 912", badge("delivered", "Passed")],
        ["<b>Noorderlicht MC</b>", '<a href="#">gene-disease.csv</a> <span class="faint">11 KB</span>', "302", badge("delivered", "Passed")],
      ], widths=["170px", "", "60px", "100px"])}
      <div style="padding:12px 12px 14px;display:flex;justify-content:space-between;align-items:center;border-top:1px solid {PAL["line2"]}">
        <div><b>Merged result</b> <span class="muted">· 3 418 rows · union by disease IRI</span></div>{btn("Download all", "primary", "download")}</div></div>''',
        title="Results (3 of 3 delivered)")
    obligations = card(f'''<div style="padding:14px 18px;display:flex;flex-direction:column;gap:10px;font-size:13px">
        <div style="display:flex;gap:10px;align-items:flex-start">{icon("cal",16,PAL["amber"])}<span><b>Delete results by 11 Oct 2026</b> — duty from Noorderlicht MC agreement <span class=mono>agr-8f23</span></span></div>
        <div style="display:flex;gap:10px;align-items:flex-start">{icon("file",16,PAL["muted"])}<span><b>Provenance record</b> — stations visited, agreements, parameters, timings (<a href="#">PROV-O, JSON-LD</a>)</span></div>
        <div style="display:flex;gap:10px;align-items:flex-start">{icon("lock",16,PAL["muted"])}<span>Results stayed with the consumer; the Handler stored artifact references only</span></div>
      </div>''', title="Obligations and provenance")
    body = (f'<div style="display:grid;grid-template-columns:minmax(0,1fr) 480px;gap:18px;flex:1;min-height:0">{mapcard}'
            f'<div style="display:flex;flex-direction:column;gap:18px">{artifacts}{obligations}</div></div>')
    return shell("handler", "Results", "Gene–disease associations · run #14", body, role="Train owner",
                 crumbs=["Results", "Run #14"], subtitle="Finished · 3 stations · walk through every step of the run with the replay controls",
                 actions=btn("Run again", "secondary", "play"))

SCREENS = {"HandlerTrains": h1, "HandlerPlan": h2, "HandlerRunLive": h3, "HandlerRunReplay": h4}

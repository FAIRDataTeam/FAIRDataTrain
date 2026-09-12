from base import *
from handler import map_svg
from station import checkpoint_timeline

SERIF = "font-family:'Source Serif 4',Georgia,serif"

def note_box(text, col="ground", ic="eye", icol=None):
    icol = icol or PAL["muted"]
    bg = PAL[col] if col in PAL else col
    return (f'<div style="display:flex;gap:10px;align-items:flex-start;padding:10px 12px;background:{bg};border-radius:6px;font-size:13px">'
            f'{icon(ic,16,icol)}<span>{text}</span></div>')

# =====================================================================================
# H7 — Iterative rounds (P5): federated model fit; one station dropped for remaining rounds
# =====================================================================================
def h7():
    labels = [("Noorderlicht MC", "n = 1 240"), ("UT Data Station", "n = 880"), ("Zuiderlicht MC", "n = 610"), ("Regional Clinic", "n = 130")]
    states = ["delivered", "running", "running", "dropped"]
    notes = ["round 7 · 11:02", "round 7 · since 11:03", "round 7 · since 11:03", "since round 4"]
    nodes = {"h": dict(x=160, y=169, label="Train Handler", sub="EU-CardioNet · orchestrator + aggregator", kind="handler")}
    ys = [40, 126, 212, 298]
    for i, ((lab, sub), st, nt) in enumerate(zip(labels, states, notes)):
        nodes[f"s{i}"] = dict(x=560, y=ys[i], label=lab, sub=sub, state=st, note=nt, dim=(st == "dropped"))
    nodes["agg"] = dict(x=960, y=169, label="Aggregate · round 7", sub="pooled coefficients → sent back to all", kind="handler")
    edges = [("h", f"s{i}", states[i] if states[i] != "dropped" else "queued", "") for i in range(4)] + \
            [(f"s{i}", "agg", "delivered" if i == 0 else ("running" if i in (1, 2) else "queued"), "") for i in range(4)]
    rounds = ""
    for r in range(1, 8):
        st = "delivered" if r < 7 else "running"
        col = PAL["green" if r < 7 else "teal"]
        extra = f' · <span style="color:{PAL["amber"]};font-weight:600">Regional Clinic dropped</span>' if r == 4 else ""
        rounds += (f'<div style="display:flex;flex-direction:column;gap:4px;align-items:center;min-width:104px">'
                   f'<span style="width:26px;height:26px;border-radius:50%;background:{col};color:#fff;display:inline-flex;align-items:center;justify-content:center;font-size:12px;font-weight:700">{r}</span>'
                   f'<span style="font-size:12px;color:{PAL["muted"]};text-align:center">Δ {["0.412","0.198","0.087","0.041","0.019","0.0072","…"][r-1]}{extra}</span></div>')
        if r < 7: rounds += f'<span style="flex:1;height:2px;background:{PAL["line"]};margin-top:12px"></span>'
    roundbar = (f'<div style="display:flex;align-items:flex-start;gap:6px;padding:8px 18px 6px;border-bottom:1px solid {PAL["line2"]}">{rounds}'
                f'<span class="muted" style="font-size:12px;margin:6px 0 0 14px">stop when <b>max |Δβ| &lt; 0.001</b> or 20 rounds</span></div>')
    mapcard = card(f'{roundbar}<div style="padding:8px">{map_svg(nodes, edges, w=1136, h=356, nw=220)}</div>',
                   title="Itinerary map — iterative rounds", aside=f'<div style="display:flex;gap:8px">{btn("Replay", "secondary", "skipb")}{btn("Stop run", "danger", "stop")}</div>', style="flex:0 0 auto")
    conv = card(f'''<div style="padding:12px 18px;display:flex;flex-direction:column;gap:10px;font-size:13px">
        {note_box("<b>Stop condition</b> <span class='mono'>latest.result.max_abs_delta &lt; `0.001` || round &gt;= `20`</span> — the train reports its own delta; the plan only compares (ADR-025).", "ground", "code")}
        {note_box("<b>Round 4:</b> Regional Clinic timed out on approval renewal → <b>dropped for remaining rounds</b>. The result will say “fitted over 3 of 4 intended stations, n = 2 730”; the aggregate restarted from round 4 over the remaining three.", "amber_tint", "alert", PAL["amber"])}
      </div>''', title="Convergence and failure policy")
    agreements = card(f'''<div style="padding:4px 6px 0">{table(["Station", "Agreement", "Rounds", "State"], [
        ["<b>Regional Clinic</b>", '<span class="mono">agr-7c13</span>', "1–3", badge("timedout", "Timed out · dropped")],
        ["<b>Noorderlicht MC</b>", '<span class="mono">agr-7c10</span>', "1–7", badge("active")],
        ["<b>UT Data Station</b>", '<span class="mono">agr-7c11</span>', "1–7", badge("active")],
        ["<b>Zuiderlicht MC</b>", '<span class="mono">agr-7c12</span>', "1–7", badge("active")],
      ], widths=["170px", "100px", "70px", ""])}</div>''', title="Agreements — one per station, valid for all rounds")
    strip = (f'<div style="display:flex;gap:18px;align-items:center;font-size:13.5px">{badge("running")}'
             f'<span><b>P5 iterative rounds</b> · orchestrated · Handler aggregates</span><span class="muted">27 visits · 7 rounds × 4 stations − 1 dropped</span><span class="muted">elapsed 1 h 04 · ≈ 9 min per round</span></div>')
    body = (f'{strip}{mapcard}<div style="display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:18px;min-height:0">{conv}{agreements}</div>')
    return shell("handler", "Runs", "Heart-failure risk model · federated fit", body, role="Train owner",
                 crumbs=["Runs", "HF risk model #2"], subtitle="Plan “Federated logistic regression, 4 stations” · pattern P5 iterative rounds · v2 preview (pattern planned for v2)", badge_count={"Runs": 2})

# =====================================================================================
# H8 — Composition (P8): cross-domain DAG (agriculture × weather × soil); one phase rejected → dependant pruned
# =====================================================================================
def h8():
    nodes = {
        "A": dict(x=170, y=60, label="Agrarisch Datastation Oost", sub="A · parcel yields 2020–2025", state="delivered", note="typed output: yield/grid"),
        "B": dict(x=170, y=150, label="Weerdata station", sub="B · weather aggregates per grid", state="delivered", note="typed output: gdd, rain/grid"),
        "C": dict(x=170, y=236, label="Bodemkaart station", sub="C · soil class per grid", state="rejected", note="PEP 3 · k &lt; 5", dim=True),
        "D": dict(x=560, y=105, label="Model station (UT)", sub="D · yield–weather model (container)", state="delivered", note="inputs A + B; C absent"),
        "E": dict(x=560, y=236, label="Model station (UT)", sub="E · soil-adjusted model (container)", state="pruned", note="needs C", dim=True),
        "F": dict(x=950, y=150, label="Train Handler", sub="F · merge + report (consumer)", kind="handler"),
    }
    edges = [("A", "D", "delivered", "yield/grid"), ("B", "D", "delivered", "gdd, rain/grid"), ("C", "E", "queued", "soil/grid"),
             ("A", "E", "queued", ""), ("D", "F", "delivered", "model coefficients"), ("E", "F", "queued", "")]
    mapcard = card(f'<div style="padding:8px">{map_svg(nodes, edges, w=1136, h=296, nw=230, note_top=True, note="Typed outputs flow along the DAG on the 1 km grid (ADR-024). C rejected at inspection → E pruned (ADR-026); D declared C optional and ran without it.")}</div>',
                   title="Itinerary map — train composition (DAG)", aside=f'<div style="display:flex;gap:8px">{btn("Replay", "secondary", "skipb")}{btn("Download report", "primary", "download")}</div>', style="flex:0 0 auto")
    rows = [
        ["A", "<b>Agrarisch Datastation Oost</b>", "parcel yields → grid", badge("delivered"), '<span class="muted">—</span>'],
        ["B", "<b>Weerdata station</b>", "weather → grid", badge("redacted"), "2 grid cells with &lt; 5 parcels removed by the station"],
        ["C", "<b>Bodemkaart station</b>", "soil class → grid", badge("rejected"), "“Result contains 41 cells below the aggregation threshold k = 5 (controller duty).”"],
        ["D", "<b>Model station (UT)</b>", "model over A + B", badge("delivered"), "ran with optional input C absent — stated in its output"],
        ["E", "<b>Model station (UT)</b>", "soil-adjusted model", badge("pruned"), "depends on C"],
    ]
    completeness = card(f'''<div style="padding:12px 18px 0;display:flex;gap:14px;align-items:baseline">
        <span style="{SERIF};font-size:22px;font-weight:600">Delivered 3 of 5 phases</span><span class="muted" style="font-size:13px">completeness threshold: phases A, B, D required — met</span></div>
      <div style="padding:4px 6px 0">{table(["", "Station", "Output", "Outcome", "Stated reason / note"], rows, widths=["28px", "230px", "150px", "170px", ""])}</div>
      <div style="padding:6px 18px 8px">{note_box("Carried verbatim in the report (ADR-026): “Yield–weather model over 3 of 5 intended phases; soil adjustment not performed — soil-class output rejected at Bodemkaart station (aggregation threshold).” Results derived from B are marked <em>redacted</em> in provenance.", "ground", "file")}</div>''',
      title="Completeness statement — what the consumer receives")
    strip = (f'<div style="display:flex;gap:18px;align-items:center;font-size:13.5px">{badge("partial")}'
             f'<span><b>P8 composition</b> · orchestrated · DAG of 5 phases</span><span class="muted">join key: 1 km grid — checked against all three datasets at planning</span><span class="muted">domains: agriculture · meteorology · soil</span></div>')
    body = f'{strip}{mapcard}{completeness}'
    return shell("handler", "Runs", "Yield vs. weather 2020–2025 · region Oost", body, role="Train owner", org="Agro-climate study group (fictional)", user="P. Kuiper",
                 crumbs=["Runs", "Yield vs. weather #1"], subtitle="Plan “Compose parcel yields, weather and soil on the 1 km grid” · finished 12 Sep 09:41 · partially delivered", badge_count={"Runs": 2})

# =====================================================================================
# G3 — Gateway: condition editor for one network (controller authors once, per network)
# =====================================================================================
def g3():
    def check(label, on=True, kind="allow"):
        col = PAL["green"] if kind == "allow" else PAL["red"]
        box = (f'<span style="width:18px;height:18px;border-radius:4px;background:{col};display:inline-flex;align-items:center;justify-content:center">{icon("check",14,"#fff",3)}</span>'
               if on else f'<span style="width:18px;height:18px;border-radius:4px;border:1.5px solid {PAL["line"]};display:inline-block"></span>')
        return f'<label style="display:flex;gap:10px;align-items:center;{"" if on else "color:"+PAL["muted"]}">{box}<span>{label}</span></label>'
    def section(title, inner, n):
        return (f'<div style="display:flex;gap:14px;padding:14px 0;border-bottom:1px solid {PAL["line2"]}">'
                f'<span style="width:26px;height:26px;border-radius:50%;background:{PAL["gateway"]};color:#fff;display:inline-flex;align-items:center;justify-content:center;font-size:12px;font-weight:700;flex:0 0 26px">{n}</span>'
                f'<div style="flex:1;display:flex;flex-direction:column;gap:10px"><h3>{title}</h3>{inner}</div></div>')
    netpick = (f'<div style="display:flex;gap:8px;flex-wrap:wrap">'
               f'<span class="chip" style="background:{PAL["gateway"]};color:#fff">{icon("map",13)}<span>Cardio network Oost</span></span>'
               f'<span class="chip" style="background:{PAL["ground"]};color:{PAL["muted"]}">{icon("map",13)}<span>Health research NL — “Research use of the HF cohort” v3 in force</span></span></div>'
               f'<div class="muted" style="font-size:12.5px">A condition applies in one network (ADR-017). The same resource can carry a different condition per network; each network’s station evaluates only its own.</div>')
    res = section("Network and resources", netpick + f'<div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:4px"><span class="chip">{icon("db",13)}<span>HF cohort — regional extract · Regional cardiology station</span> {icon("x",12)}</span>'
                  f'<span class="chip">{icon("db",13)}<span>Echo measurements 2022–2026 · Regional cardiology station</span> {icon("x",12)}</span></div>', 1)
    acts = section("Actions", f'<div style="display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px 24px">'
                   f'<div><div class="label" style="margin-bottom:6px;color:{PAL["green"]}">Allow</div><div style="display:flex;flex-direction:column;gap:6px">{check("Run query — aggregate results")}{check("Execute container (sandboxed)", False)}{check("Carry pseudonyms onward via Linkage station Oost", False)}</div></div>'
                   f'<div><div class="label" style="margin-bottom:6px;color:{PAL["red"]}">Prohibit</div><div style="display:flex;flex-direction:column;gap:6px">{check("Commercial use", True, "prohibit")}{check("Re-identification attempts", True, "prohibit")}</div></div></div>', 2)
    cons = section("Constraints", f'<div style="display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px">'
                   f'<div><div class="label" style="margin-bottom:6px">Purpose</div><span class="input" style="justify-content:space-between">Quality improvement {icon("chevd",14)}</span></div>'
                   f'<div><div class="label" style="margin-bottom:6px">Consumer</div><span class="input" style="justify-content:space-between">Members of this network {icon("chevd",14)}</span></div>'
                   f'<div><div class="label" style="margin-bottom:6px">Trains</div><span class="input" style="justify-content:space-between">From garage “Cardio network Oost” only {icon("chevd",14)}</span></div></div>', 3)
    duties = section("Duties and approval", f'<div style="display:flex;flex-direction:column;gap:6px">{check("Aggregates only above k = 10")}{check("Delete results within 90 days")}{check("Report use to the network’s QI board yearly", False)}</div>'
                     f'<div style="display:flex;align-items:center;gap:12px;margin-top:4px">{toggle(False, "gateway")}<span><b>Approve each agreement manually</b> <span class="muted">— off: network members are pre-vetted by the network’s governance authority</span></span></div>', 4)
    editor = card(f'<div style="padding:2px 18px 6px">{res}{acts}{cons}{duties}</div>'
                  f'<div style="padding:14px 18px;display:flex;gap:10px;justify-content:flex-end">{btn("Save as draft", "secondary")}{btn("Publish to Regional cardiology station", "primary", "policy")}</div>', style="flex:1")
    preview = card(f'''<div style="padding:0 18px"><div style="display:flex;border-bottom:1px solid {PAL["line2"]}"><span class="tab active">Plain language</span><span class="tab">Formal (ODRL)</span><span class="tab">Where it lands</span></div></div>
      <div style="padding:16px 18px;display:flex;flex-direction:column;gap:14px;font-size:14px">
        <div style="{SERIF};font-size:16px;line-height:1.6">In <b>Cardio network Oost</b>, for <b>HF cohort — regional extract</b> and <b>Echo measurements 2022–2026</b>, this condition
          {policy_sentence([("allows", "<em>aggregate queries</em> for <em>quality improvement</em> by <em>network members</em>, with trains from the network garage only", "green"),
                            ("prohibits", "<em>commercial use</em> and <em>re-identification</em>", "red"),
                            ("requires", "<em>aggregates above k = 10</em> and <em>deletion within 90 days</em>", "amber")])}</div>
        {note_box("<b>Check:</b> your other condition on the same extract (Health research NL) allows research use with k = 5. Both can be in force — a consumer in both networks gets whichever network its plan runs under; nothing is merged.", "amber_tint", "alert", PAL["amber"])}
        {note_box("<b>Where it lands:</b> published as an <span class='mono'>odrl:Offer</span> on the two datasets at <b>Regional cardiology station</b>, under network <span class='mono'>cardio-oost</span>. The station owner’s policy still applies on top (containers: no egress).", "ground", "station")}
        <dl class="kv" style="grid-template-columns:120px minmax(0,1fr);font-size:13px">
          <dt>Version</dt><dd>“Regional QI use” v2 — replaces v1 (active, 2 agreements; they keep v1 until renewal)</dd>
          <dt>Formal</dt><dd class="mono">odrl:Offer · 1 permission · 2 prohibitions · 2 duties · fdt-p:underNetwork</dd></dl>
      </div>''', title="Preview")
    body = f'<div style="display:grid;grid-template-columns:minmax(0,1fr) 460px;gap:18px;flex:1;min-height:0">{editor}{preview}</div>'
    return shell("gateway", "Conditions", "Edit condition — Regional QI use", body, role="Data controller",
                 crumbs=["Conditions", "Regional QI use v2"], subtitle="Cardiology Research Group · one condition, one network, published to the station that hosts the data", badge_count={"Approvals": 2})

# =====================================================================================
# G4 — Gateway: approval detail with the consequence preview (which visit of which run)
# =====================================================================================
def g4():
    matching = (f'<div style="display:flex;flex-direction:column;gap:8px;font-size:13.5px">'
                f'<div style="display:flex;gap:10px;align-items:flex-start">{icon("check",16,PAL["green"],2.5)}<span>Purpose <em>approved research</em> — allowed by “Research use of the HF cohort” v3 (Health research NL)</span></div>'
                f'<div style="display:flex;gap:10px;align-items:flex-start">{icon("check",16,PAL["green"],2.5)}<span>Action <em>run query (aggregate)</em> — allowed; the train declares outputs <span class="mono">count, by_year[]</span> only</span></div>'
                f'<div style="display:flex;gap:10px;align-items:flex-start">{icon("check",16,PAL["green"],2.5)}<span>Train <b>Heart-failure cohort count v2.1</b> from garage <em>Community</em> — digest verified, offer accepted by UT Data Station</span></div>'
                f'<div style="display:flex;gap:10px;align-items:flex-start">{icon("clock",16,PAL["amber"],2.5)}<span><b>Requires your approval</b> — this dataset is marked “approve each agreement manually”</span></div></div>')
    context = card(f'''<div style="padding:14px 18px;display:flex;flex-direction:column;gap:10px;font-size:13px">
        <div><div class="label">Part of run</div><div style="margin-top:4px"><b>HF phenotyping #3</b> · plan “Feasibility count, then analysis where n ≥ 50” · pattern P7 two-phase · EU-CardioNet</div></div>
        <div><div class="label">This visit</div><div style="margin-top:4px">Phase 1 of 2 · hop 1 · one of 6 stations · the run is <b>waiting for you</b> (approval wait 5 days, then the plan waits until its deadline 30 Nov)</div></div>
        <div><div class="label">If you approve</div><div style="margin-top:4px">Agreement becomes active; the count runs in the station sandbox; only <span class="mono">count</span> and <span class="mono">by_year[]</span> leave; if count ≥ 50 the analysis train will ask again (new agreement, new approval).</div></div>
        <div><div class="label">If you deny</div><div style="margin-top:4px">The visit ends <b>Refused</b> with your reason; the run continues at the other 5 stations and reports “selected s of 5” — your station is listed as refused, never as “below threshold”.</div></div>
      </div>''', title="What this decision does to the run (ADR-025/026)")
    detail = card(f'''<div style="padding:16px 18px;display:flex;flex-direction:column;gap:14px;flex:1">
      <div style="display:flex;flex-direction:column;gap:14px">
        <div><div class="label">Who is asking</div>
          <div style="margin-top:6px;display:flex;gap:10px;align-items:center">{avatar("MV", PAL["handler"])}<div><b>M. de Vries</b> — EU-CardioNet consortium<div class="muted" style="font-size:12.5px">Radboudumc · identity issued by SURFconext · verified 10:44 · consumer type academic</div></div></div></div>
        <div><div class="label">For what</div>
          <div style="margin-top:6px"><b>Heart failure cohort 2019–2025</b> (FHIR)<div class="muted" style="font-size:12.5px">hosted at UT Data Station · network Health research NL · request <span class="mono">req-8f24</span></div></div></div>
      </div>
      <div><div class="label">Stated purpose</div>
        <div style="margin-top:6px;padding:12px 14px;background:{PAL["ground"]};border-radius:6px;font-size:13.5px">“Feasibility count for a multi-centre heart-failure phenotyping study; aggregate counts per diagnosis code and year.” <span class="faint">[study reference]</span></div></div>
      <div><div class="label" style="margin-bottom:8px">How your condition matched</div>{matching}</div>
      <div><div class="label" style="margin-bottom:8px">Decision</div>
        <div class="input" style="height:auto;min-height:56px;align-items:flex-start;padding:10px;color:{PAL["faint"]}">Reason (recorded in the agreement, the run’s completeness statement and the audit trail)…</div></div>
      <div style="display:flex;gap:10px;margin-top:auto">{btn("Approve — activate agreement", "primary", "shield")}{btn("Deny with reason", "danger", "x")}</div>
    </div>''', style="display:flex;flex-direction:column")
    queue = card(f'''<div style="display:flex;flex-direction:column">
      <div style="padding:14px 18px;border-bottom:1px solid {PAL["line2"]};background:{PAL["gateway_tint"]};border-left:3px solid {PAL["gateway"]}">
        <div style="display:flex;justify-content:space-between"><b>EU-CardioNet consortium</b>{badge("pending")}</div>
        <div style="font-size:13px;margin-top:2px">Heart failure cohort 2019–2025 · <span class="muted">UT Data Station</span></div>
        <div class="muted" style="font-size:12.5px;margin-top:4px">Requested 10:44 · <span style="color:{PAL["amber"]};font-weight:600">4 d 20 h left</span></div></div>
      <div style="padding:14px 18px;border-bottom:1px solid {PAL["line2"]}">
        <div style="display:flex;justify-content:space-between"><b>Erasmus-like cardiology group</b>{badge("pending")}</div>
        <div style="font-size:13px;margin-top:2px">Cardiac MRI features · <span class="muted">UT Data Station</span></div>
        <div class="muted" style="font-size:12.5px;margin-top:4px">Container train v2 · requested yesterday 16:20 · 29 h left</div></div>
      <div style="padding:12px 18px" class="label">Decided this week — all stations</div>
      <div style="padding:0 18px 14px;display:flex;flex-direction:column;gap:10px;font-size:13px">
        <div style="display:flex;justify-content:space-between;gap:8px"><span>HealthAI B.V. · HF cohort · UT</span>{badge("refused")}</div>
        <div style="display:flex;justify-content:space-between;gap:8px"><span>Regional stroke QI group · regional extract</span>{badge("active")}</div></div></div>''', title="Approvals waiting for me (2)")
    body = f'<div style="display:grid;grid-template-columns:290px minmax(0,1fr) 330px;gap:18px;flex:1;min-height:0">{queue}{detail}{context}</div>'
    return shell("gateway", "Approvals", "Approve or deny — req-8f24", body, role="Data controller",
                 crumbs=["Approvals", "req-8f24"], subtitle="Cardiology Research Group · the same decision, wherever the data is hosted — with what it does to the consumer’s run", badge_count={"Approvals": 2})

# =====================================================================================
# S6 — Datasets (controller view): completeness, conditions, activity, who can reach it
# =====================================================================================
def spark(vals, col, w=120, h=28):
    mx = max(vals) or 1
    pts = " ".join(f"{i*(w/(len(vals)-1)):.1f},{h-2-(v/mx)*(h-6):.1f}" for i, v in enumerate(vals))
    return f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}"><polyline points="{pts}" fill="none" stroke="{col}" stroke-width="1.75"/><circle cx="{w}" cy="{h-2-(vals[-1]/mx)*(h-6):.1f}" r="2.5" fill="{col}"/></svg>'

def meter(pct, col):
    return (f'<span style="display:inline-flex;align-items:center;gap:8px"><span style="width:90px;height:6px;border-radius:3px;background:{PAL["line2"]};display:inline-block;overflow:hidden">'
            f'<span style="display:block;width:{pct}%;height:100%;background:{col}"></span></span><span style="font-size:12.5px;font-weight:600">{pct}%</span></span>')

def s6():
    rows = [
        [f'<b>Heart failure cohort 2019–2025</b><div class="muted" style="font-size:12px">FHIR · pseudonym space UT · join keys: pc4, timestamp</div>', meter(92, PAL["green"]),
         "Research use of the HF cohort v3", spark([3,5,4,8,6,9,7,11,9,12,10,14], PAL["station"]), "4 consumers · 5 agreements", badge("pending", "1 pending")],
        [f'<b>Cardiac MRI features</b><div class="muted" style="font-size:12px">SQL · pseudonym space UT</div>', meter(78, PAL["amber"]),
         "Research use of the HF cohort v3", spark([1,0,2,1,3,2,2,4,3,3,5,4], PAL["station"]), "2 consumers · 2 agreements", badge("pending", "1 pending")],
        [f'<b>Echo measurements 2022–2026</b><div class="muted" style="font-size:12px">SQL · no join keys declared</div>', meter(41, PAL["red"]),
         f'<span style="color:{PAL["amber"]};font-weight:600">No condition — not reachable</span>', spark([0,0,0,0,0,0,0,0,0,0,0,0], PAL["faint"]), "—", '<span class="faint">—</span>'],
    ]
    tbl = card(f'<div style="padding:4px 6px 0">{table(["Dataset", "Metadata completeness", "Condition in force", "Jobs · 12 weeks", "Who can reach it", "Approvals"], rows, selected=2, widths=["", "150px", "210px", "140px", "160px", "110px"])}</div>',
               title="My datasets on this station (3)", aside=f'{btn("Register dataset", "primary", "plus")}')
    missing = card(f'''<div style="padding:14px 18px;display:flex;flex-direction:column;gap:10px;font-size:13px">
        <div style="{SERIF};font-size:18px;font-weight:600">Echo measurements 2022–2026 — 41 % complete</div>
        <div class="muted">Metadata is what makes the dataset findable in the Station Directory and joinable by a Handler (ADR-024). Missing:</div>
        <div style="display:flex;flex-direction:column;gap:6px">
          <div style="display:flex;gap:10px;align-items:center">{icon("x",16,PAL["red"],2.5)}<span><b>Access condition</b> — without one no train can be matched; controllers’ offers are what the DSP catalogue publishes</span></div>
          <div style="display:flex;gap:10px;align-items:center">{icon("x",16,PAL["red"],2.5)}<span><b>Join keys</b> — pseudonym space and/or spatial-temporal unit</span></div>
          <div style="display:flex;gap:10px;align-items:center">{icon("x",16,PAL["red"],2.5)}<span><b>Vocabulary / profile</b> (<span class="mono">dct:conformsTo</span>) — e.g. an echo measurement profile</span></div>
          <div style="display:flex;gap:10px;align-items:center">{icon("alert",16,PAL["amber"],2.5)}<span><b>Theme and keywords</b> — recommended for the Directory</span></div>
          <div style="display:flex;gap:10px;align-items:center">{icon("check",16,PAL["green"],2.5)}<span>Title, description, controller binding, licence, interaction mechanism (SQL)</span></div>
        </div>
        <div style="display:flex;gap:10px">{btn("Add access condition", "primary", "policy")}{btn("Edit metadata", "secondary")}</div>
      </div>''', title="Selected dataset")
    reach = card(f'''<div style="padding:14px 18px;display:flex;flex-direction:column;gap:10px;font-size:13px">
        <div class="label">Heart failure cohort 2019–2025 · who can currently reach it</div>
        <div style="display:flex;flex-direction:column;gap:8px">
          <div style="display:flex;justify-content:space-between"><span><b>EU-CardioNet consortium</b> · 2 agreements</span>{badge("active")}</div>
          <div style="display:flex;justify-content:space-between"><span><b>Radboudumc Genetics</b> · 1 agreement</span>{badge("active")}</div>
          <div style="display:flex;justify-content:space-between"><span><b>Regional stroke QI group</b> · 1 agreement</span>{badge("fulfilled")}</div>
          <div style="display:flex;justify-content:space-between"><span><b>HealthAI B.V.</b> · commercial purpose</span>{badge("refused")}</div></div>
        {note_box("Anyone else must match “Research use of the HF cohort” v3 and wait for your approval. The public catalogue shows the condition in plain language, not who holds agreements.", "ground", "eye")}
      </div>''', title="Reach")
    body = (f'{tbl}<div style="display:grid;grid-template-columns:minmax(0,1fr) 440px;gap:18px;flex:1;min-height:0">{missing}{reach}</div>')
    return shell("station", "Datasets", "My datasets", body, role="Data controller · Cardiology Research Group",
                 subtitle="What you host here, how complete its description is, which condition governs it, and who can reach it today", badge_count={"Approvals": 2})

# =====================================================================================
# S7 — Audit explorer (auditor): event stream with justification chain
# =====================================================================================
def s7():
    filt = (f'<div style="display:flex;gap:10px;flex-wrap:wrap;padding:12px 18px;border-bottom:1px solid {PAL["line2"]}">'
            f'<span class="input" style="min-width:230px;justify-content:space-between">Last 24 hours {icon("cal",14)}</span>'
            f'<span class="input" style="justify-content:space-between">Actor: any {icon("chevd",14)}</span>'
            f'<span class="input" style="justify-content:space-between">Dataset: any {icon("chevd",14)}</span>'
            f'<span class="input" style="justify-content:space-between">Agreement: any {icon("chevd",14)}</span>'
            f'<span class="input" style="justify-content:space-between;color:{PAL["red"]};font-weight:600">Outcome: rejected · refused {icon("chevd",14)}</span>'
            f'<span style="flex:1"></span>{btn("Export slice (JSON-LD / CSV)", "secondary", "download")}</div>')
    ev = [
        ("10:58:00", "rejected", "PEP 3 · result inspection", "job-31b7", "Heart failure cohort 2019–2025", "EU-CardioNet", "agr-8f19", True),
        ("10:44:10", "pending", "Matching → pending approval", "req-8f24", "Heart failure cohort 2019–2025", "EU-CardioNet", "—", False),
        ("09:12:33", "refused", "Matching · prohibition", "req-8e90", "Heart failure cohort 2019–2025", "HealthAI B.V.", "—", False),
        ("08:40:02", "revoked", "Controller revocation", "agr-8c02", "Cardiac MRI features", "Erasmus-like group", "agr-8c02", False),
        ("yesterday 17:05", "rejected", "PEP 2 · payload validation", "job-30f9", "Rare disease variants", "Radboudumc Genetics", "agr-8e77", False),
    ]
    rows = []
    for t, s, what, obj, ds, actor, agr, sel in ev:
        rows.append([f'<span class="mono muted">{t}</span>', badge(s), f"<b>{what}</b>", f'<span class="mono">{obj}</span>', ds, actor, f'<span class="mono">{agr}</span>'])
    stream = card(f'{filt}<div style="padding:4px 6px 0">{table(["Time", "Outcome", "Event", "Object", "Dataset", "Actor", "Agreement"], rows, selected=0, widths=["120px", "130px", "", "90px", "", "150px", "90px"])}</div>',
                  title="Event stream — 5 of 1 284 events match", style="flex:1;display:flex;flex-direction:column;min-height:0")
    chain = card(f'''<div style="padding:14px 18px;display:flex;flex-direction:column;gap:10px;font-size:13px">
        <div style="{SERIF};font-size:18px;font-weight:600">job-31b7 rejected at result inspection</div>
        <div class="muted">Justification chain — every link is a stored object, exportable as PROV-O:</div>
        <div style="display:flex;flex-direction:column;gap:6px">
          <div style="display:flex;gap:10px">{icon("policy",16,PAL["station"])}<span><b>Duty</b> “aggregates above k = 5” · offer <span class="mono">Research use of the HF cohort v3</span> · authored by Cardiology Research Group (A. Jansen) 3 Mar 2026</span></div>
          <div style="display:flex;gap:10px">{icon("file",16,PAL["station"])}<span><b>Agreement</b> <span class="mono">agr-8f19</span> · assigner Cardiology Research Group · assignee EU-CardioNet · timestamp 11 Sep 10:12 · carries the duty</span></div>
          <div style="display:flex;gap:10px">{icon("train",16,PAL["station"])}<span><b>Train</b> Heart-failure cohort count v2.1 · payload digest <span class="mono">sha256:3b0c…f5a2</span> verified at PEP 1</span></div>
          <div style="display:flex;gap:10px">{icon("eye",16,PAL["red"])}<span><b>Inspection</b> · 2 of 38 cells with count &lt; 5 · rule <span class="mono">k-anonymity(k=5)</span> · decision <b>reject</b>, nothing delivered · consumer notified with this reason at 10:58:01</span></div>
          <div style="display:flex;gap:10px">{icon("user",16,PAL["muted"])}<span><b>Identity</b> · M. de Vries · issuer SURFconext · claim set hash <span class="mono">a91c…</span></span></div>
        </div>
        <div style="display:flex;gap:10px">{btn("Open job", "secondary")}{btn("Open agreement", "secondary")}{btn("Export chain", "secondary", "download")}</div>
      </div>''', title="Selected event")
    body = f'<div style="display:grid;grid-template-columns:minmax(0,1fr) 440px;gap:18px;flex:1;min-height:0">{stream}{chain}</div>'
    return shell("station", "Audit", "Audit explorer", body, role="Auditor", user="K. Meijer",
                 subtitle="Every checkpoint decision, negotiation step and controller action on this station — searchable, each with its justification chain", badge_count={"Approvals": 2})

# =====================================================================================
# S8 — Station settings (owner): adapters + sandbox posture, controllers, identity, dispatch, profile
# =====================================================================================
def s8():
    def arow(name, mech, on, detail):
        return (f'<div style="display:flex;align-items:center;gap:12px;padding:10px 0;border-bottom:1px solid {PAL["line2"]}">{toggle(on)}'
                f'{icon(mech,18,PAL["muted"])}<div style="flex:1"><b>{name}</b><div class="muted" style="font-size:12.5px">{detail}</div></div>{btn("Configure", "ghost", "settings")}</div>')
    adapters = card(f'''<div style="padding:4px 18px 8px">
        {arow("SPARQL", "code", True, "GraphDB endpoint · read-only user · query timeout 120 s · result cap 50 000 rows")}
        {arow("SQL", "db", True, "PostgreSQL read replica · statement timeout 60 s · schema allow-list")}
        {arow("API / FHIR", "api", True, "FHIR R4 facade · aggregate operations only · 14 queries/job max")}
        {arow("Docker container", "box", True, "Sandbox: <b>no network egress</b> · 4 CPU / 8 GB · read-only mounts · 30 min wall clock · images from trusted garages only")}
        {arow("Identifier translation", "swap", False, "Not a linkage station — leave off unless this station operates a pseudonym service (ADR-022)")}
      </div>''', title="Interaction mechanisms")
    controllers = card(f'''<div style="padding:4px 6px 0">{table(["Controller", "Type", "Datasets", "Gateway"], [
        [f'<div style="display:flex;gap:10px;align-items:center">{avatar("CR", PAL["station"])}<b>Cardiology Research Group</b></div>', "Organisation", "3", badge("synced", "Gateway linked")],
        [f'<div style="display:flex;gap:10px;align-items:center">{avatar("SC", PAL["handler"])}<b>SCS group (UT)</b></div>', "Organisation", "1", badge("synced", "Gateway linked")],
        [f'<div style="display:flex;gap:10px;align-items:center">{avatar("AJ", PAL["gateway"])}<b>A. Jansen (personal data)</b></div>', "Natural person", "1", badge("pending", "Invitation sent")],
      ], widths=["", "110px", "70px", "150px"])}</div><div style="padding:10px 18px">{btn("Invite controller", "secondary", "plus")}</div>''', title="Hosted data controllers")
    identity = card(f'''<dl class="kv" style="padding:14px 18px;grid-template-columns:150px minmax(0,1fr);font-size:13px">
        <dt>Trusted issuers</dt><dd>SURFconext (OIDC) · LS-AAI (OIDC) · <span class="muted">v2: DCP trusted-issuer lists per network</span></dd>
        <dt>Networks</dt><dd>Health research NL (station role) · Cardio network Oost (station role) · <a href="#">join a network…</a></dd>
        <dt>Dispatch</dt><dd>Push <b>and</b> poll · poll every 30 s · Handler allow-list: 2 handlers</dd>
        <dt>Processing location</dt><dd>Netherlands (NL) · declared in the self-description (register F4)</dd>
        <dt>Capacity class</dt><dd>L · 8 concurrent jobs · queue depth 40</dd>
        <dt>Self-description</dt><dd>FDP endpoint <a href="#">/fdp</a> · DSP catalogue <a href="#">/catalog</a> · regenerated from this page on save</dd>
      </dl>''', title="Identity, networks and dispatch")
    profile = card(f'''<div style="padding:14px 18px;display:flex;flex-direction:column;gap:10px;font-size:13px">
        <div style="display:flex;gap:8px"><span class="chip" style="background:{PAL["ground"]};color:{PAL["muted"]}">Personal</span><span class="chip" style="background:{PAL["ground"]};color:{PAL["muted"]}">Team</span><span class="chip" style="background:{PAL["station"]};color:#fff">Enterprise</span></div>
        <div>PostgreSQL (HA) · external queue · strict egress · all mechanisms · audit retention 10 years</div>
        {note_box("<b>EHDS secure-processing-environment variant</b> (from 2029): available as a profile switch once the implementing acts are out; it adds output checking duties and permit references to every agreement (register G1–G3).", "ground", "shield")}
      </div>''', title="Deployment profile")
    body = (f'<div style="display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:18px;flex:1;min-height:0">'
            f'<div style="display:flex;flex-direction:column;gap:18px">{adapters}{profile}</div>'
            f'<div style="display:flex;flex-direction:column;gap:18px">{controllers}{identity}</div></div>')
    return shell("station", "Settings", "Station settings", body, role="Station owner", user="R. Willems",
                 subtitle="What this station runs, whom it hosts, whom it trusts — every change here is republished as the station’s self-description",
                 badge_count={"Approvals": 2}, actions=btn("Save and republish self-description", "primary", "check"))

# =====================================================================================
# S9 — Public catalogue page (unauthenticated)
# =====================================================================================
def s9():
    def ds(title, mech, cond, keys, theme):
        chips = "".join('<span class="chip" style="height:22px;font-size:12px">' + m + '</span>' for m in mech)
        return (f'<div style="padding:14px 0;border-bottom:1px solid {PAL["line2"]};display:grid;grid-template-columns:minmax(0,1fr) 300px;gap:18px">'
                f'<div><div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap"><b style="font-size:15px">{title}</b>{chips}</div>'
                f'<div style="margin-top:6px;font-size:13.5px">{cond}</div>'
                f'<div class="muted" style="margin-top:6px;font-size:12.5px">Join keys: {keys} · Theme: {theme}</div></div>'
                f'<div style="display:flex;flex-direction:column;gap:6px;align-items:flex-end;justify-content:center">{btn("Send a train here", "primary", "train")}<span class="muted" style="font-size:12px">opens in your Train Handler</span></div></div>')
    header = (f'<div style="display:flex;justify-content:space-between;align-items:flex-start;gap:18px;padding:4px 0 18px">'
              f'<div><div style="{SERIF};font-size:30px;font-weight:600;line-height:1.15">University of Twente Data Station</div>'
              f'<div class="muted" style="margin-top:8px;max-width:70ch;font-size:14px">A FAIR Data Station: your analysis travels to the data, runs inside this station’s policy checkpoints, and only inspected aggregates leave. Member of <b>Health research NL</b> and <b>Cardio network Oost</b>.</div></div>'
              f'<div style="display:flex;gap:8px;flex-wrap:wrap;justify-content:flex-end">{badge("healthy", "Station healthy")}<span class="chip">Enterprise · capacity L</span><span class="chip">Processing in NL</span></div></div>')
    datasets = card('<div style="padding:0 18px">' +
        ds("Heart failure cohort 2019–2025", ["FHIR"], policy_sentence([("allows", "aggregate queries for approved research by academic or non-profit consumers", "green"), ("prohibits", "commercial use", "red"), ("requires", "k ≥ 5, deletion in 30 days, controller approval", "amber")]), "pseudonym space UT · postcode-4 · timestamp", "cardiovascular diseases") +
        ds("Cardiac MRI features", ["SQL"], policy_sentence([("allows", "aggregate queries and sandboxed containers for approved research", "green"), ("requires", "k ≥ 5, controller approval", "amber")]), "pseudonym space UT", "cardiac imaging") +
        ds("Rare disease variants", ["SPARQL"], policy_sentence([("allows", "SPARQL queries for research by network members", "green"), ("prohibits", "re-identification", "red")]), "none declared", "rare diseases · genomics") +
        '</div>', title="Datasets hosted here (3)", aside='<span class="muted" style="font-size:13px">conditions shown in plain language · formal ODRL in the machine-readable catalogue</span>')
    how = card(f'''<div style="padding:14px 18px;display:flex;flex-direction:column;gap:10px;font-size:13px">
        <div style="display:flex;gap:10px">{icon("train",18,PAL["station"])}<span><b>1. Pick a train</b> in a Train Handler — a query, API call or container from a garage this station trusts.</span></div>
        <div style="display:flex;gap:10px">{icon("policy",18,PAL["station"])}<span><b>2. Your request is matched</b> against the controller’s condition; some datasets need the controller’s approval (you see the deadline).</span></div>
        <div style="display:flex;gap:10px">{icon("shield",18,PAL["station"])}<span><b>3. The train runs here</b>, inside the sandbox; results are inspected before anything leaves.</span></div>
        <div style="display:flex;gap:10px">{icon("download",18,PAL["station"])}<span><b>4. You receive aggregates</b> and a provenance record; obligations (e.g. deletion) are listed with them.</span></div>
        <dl class="kv" style="grid-template-columns:150px minmax(0,1fr);font-size:13px;margin-top:6px">
          <dt>Mechanisms</dt><dd>SPARQL · SQL · FHIR API · Docker (sandboxed, no egress)</dd>
          <dt>Dispatch endpoint</dt><dd class="mono" style="font-size:12.5px">station.utwente.nl/fdt/v1</dd>
          <dt>Machine-readable</dt><dd><a href="#">FDP metadata</a> · <a href="#">DSP catalogue</a> · <a href="#">self-description</a></dd>
          <dt>Operated by</dt><dd>University of Twente — ICT services · <a href="#">contact</a></dd>
        </dl></div>''', title="How to send a train here")
    body = f'{header}<div style="display:grid;grid-template-columns:minmax(0,1fr) 420px;gap:18px;flex:1;min-height:0">{datasets}{how}</div>'
    # unauthenticated page: no console sidebar — a plain public chrome with the station wordmark and a sign-in link
    return f"""<!doctype html>
<html><head><meta charset="utf-8"><script src="./support.js"></script></head>
<body><x-dc><helmet>{FONT_LINK}<style>{css("station")}</style></helmet>
<div style="width:1440px;height:1080px;display:flex;flex-direction:column;background:{PAL['ground']};overflow:hidden;position:relative">
  <header style="height:60px;display:flex;align-items:center;justify-content:space-between;padding:0 48px;border-bottom:1px solid {PAL['line']};background:{PAL['surface']}">
    {wordmark("station")}
    <div style="display:flex;align-items:center;gap:18px;font-size:13.5px"><a href="#">Datasets</a><a href="#">How it works</a><a href="#">Networks</a><a href="#">Machine-readable</a>{btn("Sign in to the console", "secondary", "user")}</div>
  </header>
  <main style="flex:1;padding:28px 48px 28px;display:flex;flex-direction:column;gap:18px;min-height:0;max-width:1440px">{body}</main>
</div></x-dc></body></html>"""

SCREENS = {"HandlerRunRounds": h7, "HandlerRunComposition": h8, "GatewayCondition": g3, "GatewayApproval": g4,
           "StationDatasets": s6, "StationAudit": s7, "StationSettings": s8, "StationPublic": s9}

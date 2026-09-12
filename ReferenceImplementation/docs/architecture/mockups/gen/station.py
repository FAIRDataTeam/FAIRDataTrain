from base import *

def adapter_row(name, mech, state, detail):
    return (f'<div style="display:flex;align-items:center;gap:12px;padding:10px 0;border-bottom:1px solid {PAL["line2"]}">'
            f'{icon(mech, 18, PAL["muted"])}<div style="flex:1"><b>{name}</b><div class="muted" style="font-size:12.5px">{detail}</div></div>{badge(state)}</div>')

# ---- S1 Dashboard (owner) -----------------------------------------------------------
def s1():
    kpis = (f'<div style="display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:14px">'
            f'{kpi("Station", "Healthy", state="healthy")}{kpi("Jobs today", "27", sub="2 queued · 3 running · 20 delivered · 2 rejected")}'
            f'{kpi("Pending approvals", "2", sub="oldest 19 h · timeout 48 h")}{kpi("Active agreements", "14", sub="2 controllers")}'
            f'{kpi("Dispatch", "Push + poll", sub="poll every 30 s · Handler reachable")}</div>')
    adapters = card(f'''<div style="padding:4px 18px 8px">
        {adapter_row("SPARQL", "code", "enabled", "GraphDB endpoint · 1 dataset · 11 jobs today")}
        {adapter_row("SQL", "db", "enabled", "PostgreSQL read replica · 1 dataset · 4 jobs today")}
        {adapter_row("API / FHIR", "api", "enabled", "FHIR R4 facade · 1 dataset · 9 jobs today")}
        {adapter_row("Docker container", "box", "enabled", "Sandboxed executor · no network egress · 4 CPU / 8 GB · 3 jobs today")}
      </div>''', title="Interaction mechanisms", aside='<a href="#">Settings</a>')
    controllers = card(f'''<div style="padding:4px 6px 0">{table(["Controller", "Datasets", "Conditions", "Pending"], [
        [f'<div style="display:flex;gap:10px;align-items:center">{avatar("CR", PAL["station"])}<div><b>Cardiology Research Group</b><div class="muted" style="font-size:12px">Dr. A. Jansen</div></div></div>', "2", "3 offers", badge("pending", "2 pending")],
        [f'<div style="display:flex;gap:10px;align-items:center">{avatar("SC", PAL["handler"])}<div><b>Semantics, Cybersecurity &amp; Services</b><div class="muted" style="font-size:12px">Dr. L.O. Bonino</div></div></div>', "1", "1 offer", '<span class="faint">—</span>'],
      ])}</div>''', title="Hosted data controllers", aside='<a href="#">Manage</a>')
    audit_rows = [
        ("10:58", "rejected", "Result inspection rejected job <span class=mono>job-31b7</span> — aggregate below k-anonymity threshold (k = 5)"),
        ("10:47", "delivered", "Results delivered to EU-CardioNet · job <span class=mono>job-31c0</span> · Rare disease variants"),
        ("10:44", "pending", "Agreement request <span class=mono>agr-8f24</span> from EU-CardioNet awaits approval · Heart failure cohort 2019–2025"),
        ("10:12", "active", "Agreement <span class=mono>agr-8f19</span> approved by controller (Cardiology Research Group)"),
        ("09:12", "rejected", "Request from HealthAI B.V. rejected at matching — purpose <em>commercial</em> is prohibited"),
    ]
    audit = card('<div style="padding:6px 18px 10px">' + "".join(
        f'<div style="display:flex;flex-direction:column;gap:4px;padding:9px 0;border-bottom:1px solid {PAL["line2"]};font-size:13px">'
        f'<div style="display:flex;gap:10px;align-items:center"><span class="mono muted">{t}</span>{badge(s)}</div><span>{w}</span></div>' for t, s, w in audit_rows) + '</div>',
        title="Recent audit highlights", aside='<a href="#">Audit explorer</a>')
    identity = card(f'''<dl class="kv" style="padding:14px 18px;grid-template-columns:130px minmax(0,1fr);font-size:13px">
        <dt>Identifier</dt><dd class="mono">https://station.utwente.nl/</dd>
        <dt>Profile</dt><dd>Enterprise · PostgreSQL (HA) · external queue</dd>
        <dt>Capacity class</dt><dd>L</dd>
        <dt>Identity providers</dt><dd>SURFconext (OIDC) · LS-AAI (OIDC)</dd>
        <dt>Metadata</dt><dd>FDP endpoint <a href="#">/fdp</a> · self-description derived from configuration · last published 09:00</dd>
      </dl>''', title="Station identity")
    body = (f'{kpis}<div style="display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:18px;flex:1;min-height:0">'
            f'<div style="display:flex;flex-direction:column;gap:18px">{adapters}{identity}</div>'
            f'<div style="display:flex;flex-direction:column;gap:18px">{controllers}{audit}</div></div>')
    return shell("station", "Dashboard", "University of Twente Data Station", body, role="Station owner",
                 subtitle="Friday 11 September 2026 · everything that touches hosted data passes through this station’s policy checkpoints",
                 badge_count={"Approvals": 2}, user="R. Willems")

# ---- S2 Jobs monitor with checkpoint timeline ------------------------------------------
def checkpoint_timeline():
    steps = [
        ("PEP 1 · Arrival", "green", "check", "10:55:02", "Consumer authenticated via SURFconext (EU-CardioNet · M. de Vries). Payload valid against <span class=mono>PayloadShape</span>. Mechanism FHIR supported."),
        ("PEP 2 · Pre-execution", "green", "check", "10:55:04", "Agreement <span class=mono>agr-8f19</span> active until 30 Nov 2026. Purpose <em>approved research</em> matches. Station quota: 3 of 8 concurrent jobs."),
        ("Execution", "green", "check", "10:57:41", "FHIR adapter · 2 min 37 s · 14 queries · 0 errors."),
        ("PEP 3 · Result inspection", "red", "x", "10:58:00", "<b>Rejected.</b> Aggregate contains 2 cells with count &lt; 5 — violates duty <em>k-anonymity threshold k = 5</em> from the controller’s offer. Nothing delivered; consumer notified with this reason."),
    ]
    out = f'<div style="display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:0;padding:14px 18px 16px;background:{PAL["ground"]}">'
    for i, (name, col, ic, t, txt) in enumerate(steps):
        line = f'<span style="flex:1;height:2px;background:{PAL[col] if i < 3 else "transparent"}"></span>' if i < 3 else ''
        out += (f'<div style="display:flex;flex-direction:column;gap:8px;padding-right:18px">'
                f'<div style="display:flex;align-items:center;gap:8px"><span style="width:26px;height:26px;border-radius:50%;background:{PAL[col]};display:inline-flex;align-items:center;justify-content:center">{icon(ic,15,"#fff",2.5)}</span>{line}</div>'
                f'<div><b>{name}</b> <span class="mono muted" style="font-size:12px;margin-left:6px">{t}</span></div>'
                f'<div style="font-size:13px;color:{PAL["ink"]}">{txt}</div></div>')
    out += '</div>'
    return out

def s2():
    filters = (f'<div style="display:flex;gap:10px;align-items:center">'
               f'<span class="chip">{icon("x",12)}<span>State: any</span></span><span class="chip">{icon("x",12)}<span>Mechanism: any</span></span>'
               f'<span class="chip">{icon("x",12)}<span>Controller: all</span></span>'
               f'<span class="input" style="width:220px;justify-content:space-between"><span>Today</span>{icon("cal",14)}</span>'
               f'<span class="muted" style="margin-left:auto;font-size:13px">27 jobs · live</span></div>')
    rows = [
        ["<span class=mono>job-31c4</span>", "<b>Cardiac MRI feature extraction</b><div class='muted' style='font-size:12px'>EU-CardioNet</div>", "Cardiac MRI features", "Docker", '<a href="#" class=mono>agr-8f20</a>', badge("running"), "06:12"],
        ["<span class=mono>job-31c3</span>", "<b>Heart-failure cohort count</b><div class='muted' style='font-size:12px'>EU-CardioNet</div>", "Heart failure cohort 2019–2025", "FHIR", '<a href="#" class=mono>agr-8f19</a>', badge("checking"), "00:04"],
        ["<span class=mono>job-31c0</span>", "<b>Gene–disease associations</b><div class='muted' style='font-size:12px'>EU-CardioNet</div>", "Rare disease variants", "SPARQL", '<a href="#" class=mono>agr-8f21</a>', badge("delivered"), "04:51"],
        ["<span class=mono>job-31b7</span>", "<b>Heart-failure cohort count</b><div class='muted' style='font-size:12px'>EU-CardioNet</div>", "Heart failure cohort 2019–2025", "FHIR", '<a href="#" class=mono>agr-8f19</a>', badge("rejected"), "02:58"],
    ]
    tbl = table(["Job", "Train · consumer", "Dataset", "Mechanism", "Agreement", "State", "Duration"], rows, selected=3,
                widths=["90px", "", "220px", "90px", "90px", "150px", "80px"])
    more = table(["", "", "", "", "", "", ""], [
        ["<span class=mono>job-31b2</span>", "<b>Rare variant frequency</b><div class='muted' style='font-size:12px'>Radboudumc Genetics</div>", "Rare disease variants", "SPARQL", '<a href="#" class=mono>agr-8e77</a>', badge("delivered"), "00:41"],
        ["<span class=mono>job-31a9</span>", "<b>Heart-failure cohort count</b><div class='muted' style='font-size:12px'>HealthAI B.V.</div>", "Heart failure cohort 2019–2025", "FHIR", '<span class="faint">no agreement</span>', badge("rejected") + '<div class="muted" style="font-size:11.5px;margin-top:3px">at arrival · no agreement</div>', "00:01"],
    ], widths=["90px", "", "220px", "90px", "90px", "150px", "80px"]).replace("<thead>", "<thead style='display:none'>")
    expanded = (f'<div style="border-top:2px solid {PAL["red"]};border-bottom:1px solid {PAL["line2"]}">'
                f'<div style="display:flex;justify-content:space-between;align-items:center;padding:12px 18px 0;background:{PAL["ground"]}">'
                f'<h3>Checkpoint timeline — job-31b7</h3><div style="display:flex;gap:10px">{btn("Open job", "secondary", "chev")}{btn("Open agreement", "ghost", "file")}</div></div>'
                f'{checkpoint_timeline()}</div>')
    body = f'{filters}' + card(f'<div style="padding:4px 6px 0">{tbl}</div>{expanded}<div style="padding:0 6px 6px">{more}</div>', style="flex:1;overflow:hidden")
    return shell("station", "Jobs", "Jobs", body, role="Station owner",
                 subtitle="Every visit, with the decision taken at each policy checkpoint. Expand a row for the justification chain.",
                 badge_count={"Approvals": 2}, user="R. Willems", actions=btn("Export", "secondary", "download"))

# ---- S3 Approvals inbox (controller) ------------------------------------------------
def s3():
    queue = card(f'''<div style="display:flex;flex-direction:column">
      <div style="padding:14px 18px;border-bottom:1px solid {PAL["line2"]};background:{PAL["station_tint"]};border-left:3px solid {PAL["station"]}">
        <div style="display:flex;justify-content:space-between"><b>EU-CardioNet consortium</b>{badge("pending")}</div>
        <div style="font-size:13px;margin-top:2px">Heart failure cohort 2019–2025 (FHIR)</div>
        <div class="muted" style="font-size:12.5px;margin-top:4px">Requested 10:44 · <span style="color:{PAL["amber"]};font-weight:600">47 h left</span> before automatic rejection</div></div>
      <div style="padding:14px 18px;border-bottom:1px solid {PAL["line2"]}">
        <div style="display:flex;justify-content:space-between"><b>Erasmus MC — Cardiology</b>{badge("pending")}</div>
        <div style="font-size:13px;margin-top:2px">Cardiac MRI features</div>
        <div class="muted" style="font-size:12.5px;margin-top:4px">Requested yesterday 16:20 · 29 h left</div></div>
      <div style="padding:12px 18px" class="label">Decided this week</div>
      <div style="padding:0 18px 14px;display:flex;flex-direction:column;gap:10px;font-size:13px">
        <div style="display:flex;justify-content:space-between;gap:8px"><span>HealthAI B.V. · Heart failure cohort</span>{badge("rejected")}</div>
        <div style="display:flex;justify-content:space-between;gap:8px"><span>Radboudumc Genetics · Cardiac MRI features</span>{badge("active")}</div>
      </div></div>''', title="Pending approvals (2)")
    matching = (f'<div style="display:flex;flex-direction:column;gap:8px;font-size:13.5px">'
                f'<div style="display:flex;gap:10px;align-items:flex-start">{icon("check",16,PAL["green"],2.5)}<span>Purpose <em>approved research</em> — allowed by your condition “Research use of the HF cohort”</span></div>'
                f'<div style="display:flex;gap:10px;align-items:flex-start">{icon("check",16,PAL["green"],2.5)}<span>Action <em>run query (aggregate)</em> — allowed; record-level export is prohibited and was not requested</span></div>'
                f'<div style="display:flex;gap:10px;align-items:flex-start">{icon("check",16,PAL["green"],2.5)}<span>Consumer type <em>academic / non-profit</em> — verified from SURFconext organisation claim</span></div>'
                f'<div style="display:flex;gap:10px;align-items:flex-start">{icon("clock",16,PAL["amber"],2.5)}<span><b>Requires your approval</b> — your condition marks this dataset as “approve each agreement manually”</span></div></div>')
    detail = card(f'''<div style="padding:18px;display:flex;flex-direction:column;gap:18px;flex:1">
      <div style="display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px">
        <div><div class="label">Who is asking</div>
          <div style="margin-top:6px;display:flex;gap:10px;align-items:center">{avatar("MV", PAL["handler"])}<div><b>M. de Vries</b> — EU-CardioNet consortium<div class="muted" style="font-size:12.5px">Radboudumc · identity issued by SURFconext · verified 10:44</div></div></div></div>
        <div><div class="label">For what</div>
          <div style="margin-top:6px"><b>Heart failure cohort 2019–2025</b> (FHIR) <div class="muted" style="font-size:12.5px">request <span class=mono>agr-8f24</span> · 1 of your 2 datasets on this station</div></div></div>
      </div>
      <div><div class="label">Stated purpose and requested actions</div>
        <div style="margin-top:6px;padding:12px 14px;background:{PAL["ground"]};border-radius:6px;font-size:13.5px">
          “Feasibility count for a multi-centre heart-failure phenotyping study; aggregate counts per diagnosis code and year.” <span class="faint">[study reference]</span><br>
          <span class="muted">Requests:</span> <em>run query</em> (FHIR, aggregate) · train <b>Heart-failure cohort count v2.1</b> · results retained 30 days</div></div>
      <div><div class="label" style="margin-bottom:8px">How your conditions matched</div>{matching}</div>
      <div><div class="label" style="margin-bottom:8px">Decision</div>
        <div class="input" style="height:auto;min-height:64px;align-items:flex-start;padding:10px;color:{PAL["faint"]}">Reason (recorded in the agreement and the audit trail)…</div></div>
      <div style="display:flex;gap:10px;margin-top:auto">{btn("Approve — activate agreement", "primary", "shield")}{btn("Deny with reason", "danger", "x")}{btn("Ask a question", "secondary")}</div>
    </div>''', style="display:flex;flex-direction:column")
    body = f'<div style="display:grid;grid-template-columns:400px minmax(0,1fr);gap:18px;flex:1;min-height:0">{queue}{detail}</div>'
    return shell("station", "Approvals", "Approvals", body, role="Data controller · Cardiology Research Group",
                 subtitle="Agreements that met your conditions but need your explicit approval. You see only your own datasets.",
                 badge_count={"Approvals": 2})

# ---- S4 Policy builder (controller) -----------------------------------------------------
def s4():
    def section(title, inner, n):
        return (f'<div style="display:flex;gap:14px;padding:16px 0;border-bottom:1px solid {PAL["line2"]}">'
                f'<span style="width:26px;height:26px;border-radius:50%;background:{PAL["station"]};color:#fff;display:inline-flex;align-items:center;justify-content:center;font-size:12px;font-weight:700;flex:0 0 26px">{n}</span>'
                f'<div style="flex:1;display:flex;flex-direction:column;gap:10px"><h3>{title}</h3>{inner}</div></div>')
    def check(label, on=True, kind="allow"):
        col = PAL["green"] if kind == "allow" else PAL["red"]
        box = (f'<span style="width:18px;height:18px;border-radius:4px;background:{col};display:inline-flex;align-items:center;justify-content:center">{icon("check",14,"#fff",3)}</span>'
               if on else f'<span style="width:18px;height:18px;border-radius:4px;border:1.5px solid {PAL["line"]};display:inline-block"></span>')
        return f'<label style="display:flex;gap:10px;align-items:center;{"" if on else "color:"+PAL["muted"]}">{box}<span>{label}</span></label>'
    resources = section("Resources", f'<div style="display:flex;gap:8px;flex-wrap:wrap"><span class="chip">{icon("db",13)}<span>Heart failure cohort 2019–2025 (FHIR)</span> {icon("x",12)}</span>'
                        f'<span class="chip">{icon("db",13)}<span>Cardiac MRI features</span> {icon("x",12)}</span><span class="btn btn-ghost" style="height:26px;padding:0 6px">{icon("plus",14)} Add dataset</span></div>', 1)
    actions = section("Actions", f'<div style="display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px 24px">'
                      f'<div><div class="label" style="margin-bottom:6px;color:{PAL["green"]}">Allow</div><div style="display:flex;flex-direction:column;gap:6px">{check("Run query — aggregate results")}{check("Run query — record level", False)}{check("Execute container (sandboxed)")}</div></div>'
                      f'<div><div class="label" style="margin-bottom:6px;color:{PAL["red"]}">Prohibit</div><div style="display:flex;flex-direction:column;gap:6px">{check("Commercial use", True, "prohibit")}{check("Re-identification attempts", True, "prohibit")}{check("Onward transfer of results", False, "prohibit")}</div></div></div>', 2)
    constraints = section("Constraints", f'<div style="display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px">'
                          f'<div><div class="label" style="margin-bottom:6px">Purpose</div><span class="input" style="justify-content:space-between">Approved research (DPV) {icon("chevd",14)}</span></div>'
                          f'<div><div class="label" style="margin-bottom:6px">Consumer type</div><span class="input" style="justify-content:space-between">Academic or non-profit {icon("chevd",14)}</span></div>'
                          f'<div><div class="label" style="margin-bottom:6px">Valid</div><span class="input" style="justify-content:space-between">Until 31 Dec 2027 {icon("cal",14)}</span></div></div>', 3)
    duties = section("Duties", f'<div style="display:flex;flex-direction:column;gap:6px">{check("Delete results within 30 days")}{check("Aggregates only above k-anonymity threshold k = 5")}{check("Report publications using the data", False)}</div>', 4)
    approval = section("Approval", f'<div style="display:flex;align-items:center;gap:12px">{toggle(True)}<span><b>Approve each agreement manually</b> <span class="muted">— matched requests wait in your Approvals inbox (48 h timeout)</span></span></div>', 5)
    builder = card(f'<div style="padding:2px 18px 6px">{resources}{actions}{constraints}{duties}{approval}</div>'
                   f'<div style="padding:14px 18px;display:flex;gap:10px;justify-content:flex-end">{btn("Save as draft", "secondary")}{btn("Publish condition", "primary", "policy")}</div>', style="flex:1")
    preview = card(f'''<div style="padding:0 18px"><div style="display:flex;border-bottom:1px solid {PAL["line2"]}"><span class="tab active">Plain language</span><span class="tab">Formal (ODRL)</span></div></div>
      <div style="padding:16px 18px;display:flex;flex-direction:column;gap:14px;font-size:14px">
        <div style="font-family:'Source Serif 4',Georgia,serif;font-size:16px;line-height:1.6">
          For <b>Heart failure cohort 2019–2025</b> and <b>Cardiac MRI features</b>, this condition
          {policy_sentence([("allows", "<em>running aggregate queries</em> and <em>executing sandboxed containers</em> for <em>approved research</em> by <em>academic or non-profit</em> consumers until <em>31 Dec 2027</em>", "green"),
                            ("prohibits", "<em>commercial use</em> and <em>re-identification attempts</em>", "red"),
                            ("requires", "<em>deletion of results within 30 days</em> and <em>aggregates above k = 5</em>", "amber"),
                            ("and requires", "<em>your approval of each agreement</em>", "amber")])}
        </div>
        <div style="display:flex;gap:10px;align-items:flex-start;padding:12px 14px;background:{PAL["amber_tint"]};border-radius:6px;font-size:13px">{icon("alert",18,PAL["amber"])}
          <span><b>Check:</b> “Run query — record level” is not allowed, but the duty “aggregates above k = 5” only applies to aggregate results — fine. If you later allow record-level queries, add a duty covering them or the condition becomes inconsistent.</span></div>
        <div style="display:flex;gap:10px;align-items:flex-start;padding:12px 14px;background:{PAL["ground"]};border-radius:6px;font-size:13px">{icon("eye",18,PAL["muted"])}
          <span>Effective access is this condition <b>and</b> the station owner’s policy (currently: no network egress for containers; 8 concurrent jobs).</span></div>
        <dl class="kv" style="grid-template-columns:120px minmax(0,1fr);font-size:13px">
          <dt>Profile</dt><dd>FDT core + DUO/DPV (health)</dd><dt>Replaces</dt><dd>“Research use of the HF cohort” v3 (active, 6 agreements)</dd>
          <dt>Formal</dt><dd class="mono">odrl:Offer · 2 permissions · 2 prohibitions · 2 duties</dd></dl>
      </div>''', title="Preview")
    body = f'<div style="display:grid;grid-template-columns:minmax(0,1fr) 460px;gap:18px;flex:1;min-height:0">{builder}{preview}</div>'
    return shell("station", "Access conditions", "Edit access condition", body, role="Data controller · Cardiology Research Group",
                 crumbs=["Access conditions", "Research use of the HF cohort"], subtitle="Structured choices, rendered as plain language as you go — the formal ODRL is one tab away.",
                 badge_count={"Approvals": 2})

# ---- S5 Agreement detail -----------------------------------------------------------------
def s5():
    def state_step(key, when, note, current=False, future=False):
        lab, col, ic = STATES[key]
        c = PAL["line"] if future else PAL[col]
        return (f'<div style="display:flex;gap:12px;align-items:flex-start;padding:8px 0">'
                f'<span style="width:24px;height:24px;border-radius:50%;background:{c};display:inline-flex;align-items:center;justify-content:center;flex:0 0 24px;{"box-shadow:0 0 0 3px "+PAL[col+"_tint"] if current else ""}">{icon(ic,14,"#fff",2.5)}</span>'
                f'<div><div style="display:flex;gap:10px;align-items:baseline"><b style="{"color:"+PAL["faint"] if future else ""}">{lab}</b><span class="mono muted" style="font-size:12px">{when}</span></div>'
                f'<div class="muted" style="font-size:12.5px">{note}</div></div></div>')
    timeline = card(f'''<div style="padding:8px 18px 12px">
        {state_step("requested", "09:40:12", "Request carried by train “Heart-failure cohort count v2.1”")}
        {state_step("matched", "09:40:14", "Offer “Research use of the HF cohort” v3 × request — all conditions met")}
        {state_step("pending", "09:40:14", "Dataset flagged for manual approval · 48 h timeout")}
        {state_step("active", "10:12:05", "Approved by A. Jansen: “Feasibility count only — approved.”", current=True)}
        {state_step("fulfilled", "—", "When the run’s obligations are met", future=True)}
      </div>''', title="Lifecycle")
    parties = card(f'''<div style="padding:14px 18px;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px">
        <div><div class="label">Assigner · data controller</div><div style="margin-top:6px;display:flex;gap:10px;align-items:center">{avatar("AJ", PAL["station"])}<div><b>Cardiology Research Group</b><div class="muted" style="font-size:12.5px">Dr. A. Jansen · University of Twente</div></div></div>
          <div class="muted" style="font-size:12px;margin-top:6px">Identity: SURFconext · subject <span class="mono">a.jansen@…</span> · proof: OIDC token</div></div>
        <div><div class="label">Assignee · data consumer</div><div style="margin-top:6px;display:flex;gap:10px;align-items:center">{avatar("MV", PAL["handler"])}<div><b>EU-CardioNet consortium</b><div class="muted" style="font-size:12.5px">M. de Vries · Radboudumc</div></div></div>
          <div class="muted" style="font-size:12px;margin-top:6px">Identity: SURFconext · org claim verified · proof: OIDC token</div></div>
      </div>''', title="Parties")
    conditions = card(f'''<div style="padding:14px 18px;font-family:'Source Serif 4',Georgia,serif;font-size:15.5px;line-height:1.6">
        On <b>Heart failure cohort 2019–2025</b>, {policy_sentence([("allows", "<em>running aggregate queries</em> for <em>approved research</em> until <em>30 Nov 2026</em>", "green"),
        ("prohibits", "<em>commercial use</em> and <em>re-identification attempts</em>", "red"), ("requires", "<em>deletion of results within 30 days</em> and <em>aggregates above k = 5</em>", "amber")])}
        <div style="font-family:'Source Sans 3',system-ui,sans-serif;font-size:13px;margin-top:10px" class="muted">Derived from offer <a href="#">Research use of the HF cohort v3</a> and request <a href="#" class="mono">req-2c91</a> · <a href="#">Formal ODRL agreement</a></div>
      </div>''', title="Conditions in force")
    jobs = card(f'''<div style="padding:4px 6px 0">{table(["Job", "Train", "State", "When"], [
        ["<span class=mono>job-31c3</span>", "Heart-failure cohort count v2.1", badge("checking"), "11:39"],
        ["<span class=mono>job-31b7</span>", "Heart-failure cohort count v2.1", badge("rejected") + '<div class="muted" style="font-size:11.5px;margin-top:3px">at result inspection</div>', "10:58"],
      ], widths=["90px", "", "170px", "70px"])}</div>''', title="Jobs under this agreement (2)", aside='<a href="#">Audit slice</a>')
    revoke = card(f'''<div style="padding:14px 18px;display:flex;flex-direction:column;gap:10px;font-size:13px">
        <div style="display:flex;gap:10px;align-items:flex-start">{icon("alert",18,PAL["red"])}<span>Revoking takes effect at the next checkpoint: <b>job-31c3 will be stopped</b> before execution, and no new jobs will be accepted under <span class=mono>agr-8f19</span>. The consumer is notified with your reason. Results already delivered are covered by the deletion duty.</span></div>
        <div style="display:flex;gap:10px">{btn("Revoke agreement", "danger", "slash")}{btn("Suspend new jobs", "secondary", "pause")}</div></div>''', title="Controller actions")
    body = (f'<div style="display:grid;grid-template-columns:minmax(0,1fr) 420px;gap:18px;flex:1;min-height:0">'
            f'<div style="display:flex;flex-direction:column;gap:18px">{parties}{conditions}{jobs}</div>'
            f'<div style="display:flex;flex-direction:column;gap:18px">{timeline}{revoke}</div></div>')
    return shell("station", "Agreements", "Agreement agr-8f19", body, role="Data controller · Cardiology Research Group",
                 crumbs=["Agreements", "agr-8f19"], subtitle="EU-CardioNet consortium × Cardiology Research Group · Heart failure cohort 2019–2025 · " + badge("active", size="md"),
                 badge_count={"Approvals": 2}, actions=btn("Download signed agreement", "secondary", "download"))

SCREENS = {"StationDashboard": s1, "StationJobs": s2, "StationApprovals": s3, "StationPolicy": s4, "StationAgreement": s5}

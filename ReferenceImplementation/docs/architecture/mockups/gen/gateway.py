from base import *

# Individual Gateway — one controller (here an organisation: Cardiology Research Group) across the stations hosting its data.
# The same screens serve a natural-person controller in the personal profile (ADR-018).

def netchip(name, col="gateway"):
    return f'<span class="chip" style="height:22px;font-size:12px;background:{PAL[col+"_tint"]};color:{PAL[col+"_dark"]}">{icon("map",12)}<span>{name}</span></span>'

# ---- G1 Overview -------------------------------------------------------------------------------
def g1():
    kpis = (f'<div style="display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:14px">'
            f'{kpi("Resources", "4", sub="on 3 stations · 2 networks")}{kpi("Conditions", "3", sub="1 draft awaiting publication")}'
            f'{kpi("Pending approvals", "2", sub="oldest 19 h · across all stations")}{kpi("Active agreements", "9", sub="4 consumers")}'
            f'{kpi("Jobs on my data", "31", sub="last 7 days · 1 rejected at inspection")}</div>')
    res_rows = [
        ["<b>Heart failure cohort 2019–2025</b><div class='muted' style='font-size:12px'>FHIR · UT Data Station · 5 agreements</div>", netchip("Health research NL"), "Research use of the HF cohort v3", badge("pending", "1 pending")],
        ["<b>Cardiac MRI features</b><div class='muted' style='font-size:12px'>SQL · UT Data Station · 2 agreements</div>", netchip("Health research NL"), "Research use of the HF cohort v3", badge("pending", "1 pending")],
        ["<b>HF cohort — regional extract</b><div class='muted' style='font-size:12px'>FHIR · Regional cardiology station · 2 agreements</div>", netchip("Cardio network Oost", "handler"), "Regional QI use v1", '<span class="faint">—</span>'],
        ["<b>Echo measurements 2022–2026</b><div class='muted' style='font-size:12px'>SQL · Regional cardiology station · 0 agreements</div>", netchip("Cardio network Oost", "handler"), '<span style="color:' + PAL["amber"] + ';font-weight:600">No condition — not reachable</span>', '<span class="faint">—</span>'],
    ]
    resources = card(f'<div style="padding:4px 6px 0">{table(["Resource · station", "Network", "Condition in force", "Approvals"], res_rows, widths=["", "170px", "220px", "110px"])}</div>',
                     title="My resources across stations", aside='<a href="#">All resources</a>')
    approvals = card(f'''<div style="padding:6px 18px 10px;display:flex;flex-direction:column">
        <div style="display:flex;flex-direction:column;gap:4px;padding:10px 0;border-bottom:1px solid {PAL["line2"]};font-size:13px">
          <div style="display:flex;justify-content:space-between"><b>EU-CardioNet consortium</b>{badge("pending")}</div>
          <span>Heart failure cohort 2019–2025 · <span class="muted">UT Data Station · Health research NL</span></span>
          <span class="muted">Feasibility count · requested 10:44 · <span style="color:{PAL["amber"]};font-weight:600">47 h left</span></span></div>
        <div style="display:flex;flex-direction:column;gap:4px;padding:10px 0;font-size:13px">
          <div style="display:flex;justify-content:space-between"><b>Erasmus-like cardiology group</b>{badge("pending")}</div>
          <span>Cardiac MRI features · <span class="muted">UT Data Station · Health research NL</span></span>
          <span class="muted">Container train v2 · requested yesterday 16:20 · 29 h left</span></div>
        <div style="padding-top:10px">{btn("Open approvals", "primary", "inbox")}</div></div>''', title="Approvals waiting for me (2)")
    activity_rows = [
        ("10:58", "rejected", "UT Data Station rejected job <span class='mono'>job-31b7</span> at result inspection — k-anonymity duty (k = 5)"),
        ("10:12", "active", "You approved <span class='mono'>agr-8f19</span> · EU-CardioNet · Heart failure cohort 2019–2025"),
        ("09:12", "rejected", "HealthAI B.V. request rejected at matching — commercial purpose prohibited by your condition"),
        ("yesterday", "active", "Regional QI use v1 published on Regional cardiology network station"),
    ]
    activity = card('<div style="padding:6px 18px 10px">' + "".join(
        f'<div style="display:flex;flex-direction:column;gap:4px;padding:9px 0;border-bottom:1px solid {PAL["line2"]};font-size:13px">'
        f'<div style="display:flex;gap:10px;align-items:center"><span class="mono muted">{t}</span>{badge(s)}</div><span>{w}</span></div>' for t, s, w in activity_rows[:3]) + '</div>',
        title="Activity on my data (all stations)", aside='<a href="#">Full audit slice</a>')
    body = (f'{kpis}<div style="display:grid;grid-template-columns:minmax(0,1fr) 380px;gap:18px;flex:1;min-height:0">'
            f'<div style="display:flex;flex-direction:column;gap:18px;min-height:0">{resources}{activity}</div><div>{approvals}</div></div>')
    return shell("gateway", "Overview", "Cardiology Research Group", body, role="Data controller",
                 subtitle="One place to govern your data wherever it is hosted — conditions, approvals and the audit trail across 3 stations in 2 networks",
                 badge_count={"Approvals": 2}, actions=btn("New condition", "primary", "policy"))

# ---- G2 Resource detail with revoke / opt-out -------------------------------------------------------------
def g2():
    header = card(f'''<div style="padding:16px 18px;display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:16px">
        <div><div class="label">Hosted at</div><div style="margin-top:4px"><b>UT Data Station</b><div class="muted" style="font-size:12.5px">owner: University of Twente · enterprise profile · NL</div></div></div>
        <div><div class="label">Networks</div><div style="margin-top:6px;display:flex;gap:6px;flex-wrap:wrap">{netchip("Health research NL")}{netchip("Cardio network Oost", "handler")}</div></div>
        <div><div class="label">Join keys</div><div style="margin-top:4px;font-size:13px">Pseudonym space UT · postcode-4 area · timestamp</div></div>
        <div><div class="label">Controller</div><div style="margin-top:4px"><b>Cardiology Research Group</b><div class="muted" style="font-size:12.5px">steward: A. Jansen (delegated)</div></div></div>
      </div>''')
    conditions = card(f'''<div style="padding:4px 6px 0">{table(["Network", "Condition", "State"], [
        [netchip("Health research NL"), "<b>Research use of the HF cohort</b> v3<div style='font-size:13px;margin-top:4px'>" + policy_sentence([("allows", "aggregate queries for approved research", "green"), ("prohibits", "commercial use", "red"), ("requires", "deletion in 30 days, k ≥ 5, my approval", "amber")]) + "</div>", badge("active", "Published")],
        [netchip("Cardio network Oost", "handler"), "<b>Regional QI use</b> v1<div style='font-size:13px;margin-top:4px'>" + policy_sentence([("allows", "aggregate queries for quality improvement by network members", "green"), ("requires", "k ≥ 10", "amber")]) + "</div>", badge("active", "Published")],
      ], widths=["190px", "", "120px"])}</div>
      <div style="padding:12px 18px;display:flex;gap:10px;border-top:1px solid {PAL["line2"]}">{btn("Edit condition", "secondary", "policy")}{btn("Add condition for another network", "ghost", "plus")}</div>''',
      title="Conditions per network (ADR-017: evaluated per network)")
    agreements = card(f'''<div style="padding:4px 6px 0">{table(["Agreement", "Consumer", "Network", "State", "Jobs"], [
        ['<span class="mono">agr-8f19</span>', "EU-CardioNet consortium", netchip("Health research NL"), badge("active"), "2"],
        ['<span class="mono">agr-8e77</span>', "Radboudumc Genetics", netchip("Health research NL"), badge("active"), "5"],
        ['<span class="mono">agr-8d10</span>', "Regional stroke QI group", netchip("Cardio network Oost", "handler"), badge("fulfilled"), "3"],
        ['<span class="mono">req-8f24</span>', "EU-CardioNet consortium", netchip("Health research NL"), badge("pending"), "—"],
      ], widths=["100px", "", "190px", "140px", "60px"])}</div>''', title="Agreements over this resource (4)", aside='<a href="#">Audit slice</a>')
    actions = card(f'''<div style="padding:14px 18px;display:flex;flex-direction:column;gap:12px;font-size:13px">
        <div style="display:flex;gap:10px;align-items:flex-start">{icon("slash",18,PAL["red"])}<span><b>Revoke an agreement</b> — takes effect at the station’s next checkpoint; running jobs stop before execution; consumer notified with your reason.</span></div>
        <div style="display:flex;gap:10px;align-items:flex-start">{icon("pause",18,PAL["amber"])}<span><b>Suspend new agreements</b> on this resource in one network while keeping existing ones.</span></div>
        <div style="display:flex;gap:10px;align-items:flex-start">{icon("x",18,PAL["red"])}<span><b>Withdraw the resource</b> — the station stops advertising it; the gateway shows which agreements are affected. For a natural-person controller this is the <b>opt-out</b> (EHDS from 2029; Wkz from 2027).</span></div>
        <div style="display:flex;gap:10px;margin-top:4px;flex-wrap:wrap">{btn("Revoke…", "danger", "slash")}{btn("Suspend new agreements", "secondary", "pause")}{btn("Withdraw resource", "secondary", "x")}</div>
      </div>''', title="Controller actions")
    body = (f'{header}<div style="display:grid;grid-template-columns:minmax(0,1fr) 400px;gap:18px;flex:1;min-height:0">'
            f'<div style="display:flex;flex-direction:column;gap:18px;min-height:0">{conditions}{agreements}</div><div>{actions}</div></div>')
    return shell("gateway", "My resources", "Heart failure cohort 2019–2025", body, role="Data controller",
                 crumbs=["My resources", "Heart failure cohort 2019–2025"], subtitle="FHIR · hosted at UT Data Station · reachable in 2 networks under 2 conditions",
                 badge_count={"Approvals": 2}, actions=btn("Download audit slice", "secondary", "download"))

SCREENS = {"GatewayOverview": g1, "GatewayResource": g2}

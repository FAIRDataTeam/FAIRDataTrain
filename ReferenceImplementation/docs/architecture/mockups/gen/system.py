from base import *

def swatch(name, hexv, note=""):
    return (f'<div style="display:flex;flex-direction:column;gap:6px"><span style="height:56px;border-radius:8px;background:{hexv};border:1px solid {PAL["line"]}"></span>'
            f'<div style="font-weight:600;font-size:13px">{name}</div><div class="mono muted" style="font-size:12px">{hexv}</div><div class="muted" style="font-size:12px">{note}</div></div>')

def system_sheet():
    agreement = ["requested", "matched", "pending", "active", "fulfilled", "expired", "revoked", "rejected"]
    job = ["queued", "checking", "running", "inspecting", "delivered", "rejected", "failed"]
    run = ["scheduled", "running", "waiting", "partial", "finished", "failed"]
    def row(title, keys, note):
        return (f'<div style="display:grid;grid-template-columns:150px minmax(0,1fr);gap:16px;align-items:start;padding:12px 0;border-bottom:1px solid {PAL["line2"]}">'
                f'<div><b>{title}</b><div class="muted" style="font-size:12px">{note}</div></div>'
                f'<div style="display:flex;flex-wrap:wrap;gap:8px">{"".join(badge(k, size="md") for k in keys)}</div></div>')
    states = card(f'''<div style="padding:4px 18px 8px">
        {row("Agreement", agreement, "ODRL agreement lifecycle (architecture §6.4)")}
        {row("Job", job, "one visit; three checkpoints PEP 1 · PEP 2 · PEP 3")}
        {row("Run (Handler)", run, "one execution of a plan across stations")}
        <div style="padding:12px 0 4px;font-size:13px" class="muted">Colour is never the only carrier: every state pairs a hue with an icon and a label. Five hues cover all lifecycles — grey (not yet), blue (in progress, machine), amber (waiting on a person), green (good end), red (bad end); teal marks live execution.</div>
      </div>''', title="State system")
    palette = card(f'''<div style="padding:16px 18px;display:grid;grid-template-columns:repeat(8,minmax(0,1fr));gap:14px">
        {swatch("Ground", PAL["ground"], "page background")}{swatch("Surface", PAL["surface"], "cards, tables")}{swatch("Ink", PAL["ink"], "text")}{swatch("Muted", PAL["muted"], "secondary text")}
        {swatch("Handler accent", PAL["handler"], "Train Handler")}{swatch("Station accent", PAL["station"], "Data Station")}{swatch("Line", PAL["line"], "borders")}{swatch("Amber", PAL["amber"], "human waits, duties")}
      </div>''', title="Palette — one FDT identity, two accents")
    type_ = card(f'''<div style="padding:16px 18px;display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:24px">
        <div><div class="label">Headings · Source Serif 4 (600)</div>
          <h1 style="margin-top:8px">Agreement agr-8f19</h1><h2 style="margin-top:6px">Conditions in force</h2><h3 style="margin-top:6px">Checkpoint timeline</h3>
          <div class="muted" style="font-size:13px;margin-top:8px">26 / 18 / 15 px · serif signals “document of record”, used for titles and rendered policy text</div></div>
        <div><div class="label">UI text · Source Sans 3 (400–600)</div>
          <div style="margin-top:8px;font-size:14px">Body 14 px · <b>emphasis 600</b> · <span class="muted">secondary</span> · <span class="mono">identifiers in mono 12.5 px</span></div>
          <div style="margin-top:8px;font-size:13px">Small 13 px for table cells and notes · labels 12 px uppercase, letter-spaced</div>
          <div class="muted" style="font-size:13px;margin-top:8px">Spacing: 4 px base; 18 px card gutters; 32 px page margins; controls 36 px high; radii 6 px (controls) / 8 px (cards)</div></div>
      </div>''', title="Type and spacing")
    policy = card(f'''<div style="padding:16px 18px;display:flex;flex-direction:column;gap:12px">
        <div style="font-family:'Source Serif 4',Georgia,serif;font-size:16px;line-height:1.6">For <b>[resources]</b>, this condition
          {policy_sentence([("allows", "<em>[actions]</em> for <em>[purpose]</em> by <em>[consumer type]</em> until <em>[date]</em>", "green"),
                            ("prohibits", "<em>[actions]</em>", "red"), ("requires", "<em>[duties]</em>", "amber")])}</div>
        <div class="muted" style="font-size:13px">Controlled sentence pattern for ODRL: permissions in green (<b>allows</b>), prohibitions in red (<b>prohibits</b>), duties in amber (<b>requires</b>); constraints inline in italics. Raw IRIs never by default — labels first, IRI on hover or in the formal tab. Verbs for actions: Approve, Deny, Revoke, Publish — never “OK”.</div>
      </div>''', title="Human-readable policy pattern")
    icons = card('<div style="padding:16px 18px;display:flex;flex-wrap:wrap;gap:18px">' + "".join(
        f'<div style="display:flex;flex-direction:column;align-items:center;gap:6px;width:64px">{icon(k, 22, PAL["ink"])}<span class="mono muted" style="font-size:11px">{k}</span></div>'
        for k in ["train", "station", "map", "play", "check", "shield", "clock", "search", "swap", "x", "slash", "alert", "file", "cal", "hourglass", "lock", "eye", "code", "db", "api", "box", "inbox", "policy", "audit"]) + '</div>',
        title="Icons — stroke 1.75, 24-grid, one style")
    body = (f'<div style="display:grid;grid-template-columns:minmax(0,1fr) 520px;gap:18px;flex:1;min-height:0">'
            f'<div style="display:flex;flex-direction:column;gap:18px">{states}{policy}</div>'
            f'<div style="display:flex;flex-direction:column;gap:18px">{palette}{type_}{icons}</div></div>')
    return f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
  {FONT_LINK}
  <style>{css("station")}</style>
</helmet>
<div style="width:1440px;height:1080px;background:{PAL['ground']};overflow:hidden;padding:28px 32px;box-sizing:border-box;display:flex;flex-direction:column;gap:18px">
  <div><div class="label">FAIR Data Train consoles</div><h1 style="margin-top:4px">Design system sheet</h1>
    <div class="muted" style="margin-top:4px">Shared by the Train Handler and the Data Station console · “institutional calm” direction · WCAG 2.2 AA contrast targets</div></div>
  {body}
</div>
</x-dc>
</body>
</html>
"""

SCREENS = {"DesignSystem": system_sheet}

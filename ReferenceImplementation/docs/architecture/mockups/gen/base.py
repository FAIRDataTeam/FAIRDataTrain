# Shared vocabulary for the FDT console mock-ups (Handler + Station).
# Static artboards: no data-dc-script needed.

FONT_LINK = '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,500;8..60,600&amp;family=Source+Sans+3:wght@400;500;600&amp;display=swap">'

PAL = dict(
    ground="#f6f4ef", surface="#ffffff", ink="#1e2a2e", muted="#5c6b71", faint="#8b979c",
    line="#e2ddd4", line2="#ece8e0",
    handler="#1f6f78", handler_dark="#175a61", handler_tint="#e3f0f1",
    station="#365c8d", station_dark="#2b4a73", station_tint="#e5ecf5",
    gateway="#7a4d78", gateway_dark="#5f3b5d", gateway_tint="#f1e7f0",
    # state colours (never the sole carrier: always paired with an icon + label)
    grey="#6b7a80", grey_tint="#eef0f1",
    blue="#3b6fb6", blue_tint="#e6eef8",
    amber="#a8690f", amber_tint="#faefd9",
    green="#2e7d5b", green_tint="#e3f2ea",
    red="#b3413a", red_tint="#f9e6e4",
    teal="#1f6f78", teal_tint="#e3f0f1",
)

ICONS = {
    "circle": '<circle cx="12" cy="12" r="8"/>',
    "dashed": '<circle cx="12" cy="12" r="8" stroke-dasharray="3 3"/>',
    "clock": '<circle cx="12" cy="12" r="8"/><path d="M12 8v4l3 2"/>',
    "play": '<path d="M8 6l10 6-10 6z"/>',
    "check": '<path d="M5 12l5 5 9-10"/>',
    "shield": '<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z"/><path d="M9 12l2 2 4-4"/>',
    "x": '<path d="M6 6l12 12M18 6L6 18"/>',
    "slash": '<circle cx="12" cy="12" r="8"/><path d="M6.5 6.5l11 11"/>',
    "alert": '<path d="M12 3l10 18H2z"/><path d="M12 10v4M12 17.5v.5"/>',
    "search": '<circle cx="11" cy="11" r="6"/><path d="M20 20l-4.5-4.5"/>',
    "swap": '<path d="M4 8h13l-3-3M20 16H7l3 3"/>',
    "file": '<path d="M7 3h7l5 5v13H7z"/><path d="M14 3v5h5"/><path d="M9.5 15l2 2 3.5-4"/>',
    "cal": '<rect x="4" y="5" width="16" height="15" rx="1.5"/><path d="M4 10h16M9 3v4M15 3v4"/>',
    "hourglass": '<path d="M7 3h10M7 21h10M8 3c0 5 4 6 4 9s-4 4-4 9M16 3c0 5-4 6-4 9s4 4 4 9"/>',
    "train": '<rect x="5" y="3" width="14" height="14" rx="2.5"/><path d="M5 11h14M9 17l-2 4M15 17l2 4M9 14h.01M15 14h.01"/>',
    "station": '<path d="M3 21h18M5 21V9l7-5 7 5v12"/><path d="M10 21v-6h4v6"/>',
    "grid": '<rect x="4" y="4" width="7" height="7" rx="1"/><rect x="13" y="4" width="7" height="7" rx="1"/><rect x="4" y="13" width="7" height="7" rx="1"/><rect x="13" y="13" width="7" height="7" rx="1"/>',
    "list": '<path d="M8 6h12M8 12h12M8 18h12M4 6h.01M4 12h.01M4 18h.01"/>',
    "inbox": '<path d="M4 13l2-8h12l2 8v6H4z"/><path d="M4 13h5l1 2h4l1-2h5"/>',
    "policy": '<path d="M6 3h12v18H6z"/><path d="M9 8h6M9 12h6M9 16h4"/>',
    "settings": '<circle cx="12" cy="12" r="3"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3M4.9 4.9l2.1 2.1M17 17l2.1 2.1M4.9 19.1L7 17M17 7l2.1-2.1"/>',
    "audit": '<path d="M4 4h16v16H4z"/><path d="M8 14l3-3 2 2 3-4"/>',
    "db": '<ellipse cx="12" cy="6" rx="8" ry="3"/><path d="M4 6v12c0 1.7 3.6 3 8 3s8-1.3 8-3V6M4 12c0 1.7 3.6 3 8 3s8-1.3 8-3"/>',
    "map": '<path d="M3 6l6-2 6 2 6-2v14l-6 2-6-2-6 2z"/><path d="M9 4v14M15 6v14"/>',
    "chev": '<path d="M9 6l6 6-6 6"/>',
    "chevd": '<path d="M6 9l6 6 6-6"/>',
    "plus": '<path d="M12 5v14M5 12h14"/>',
    "user": '<circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 3.6-7 8-7s8 3 8 7"/>',
    "link": '<path d="M10 14a4 4 0 005.7 0l3-3a4 4 0 00-5.7-5.7l-1 1"/><path d="M14 10a4 4 0 00-5.7 0l-3 3a4 4 0 005.7 5.7l1-1"/>',
    "download": '<path d="M12 4v11M7 10l5 5 5-5M4 20h16"/>',
    "pause": '<path d="M8 5v14M16 5v14"/>',
    "skipb": '<path d="M18 5v14L8 12z"/><path d="M6 5v14"/>',
    "skipf": '<path d="M6 5v14l10-7z"/><path d="M18 5v14"/>',
    "stop": '<rect x="6" y="6" width="12" height="12" rx="1"/>',
    "lock": '<rect x="5" y="11" width="14" height="10" rx="1.5"/><path d="M8 11V7a4 4 0 018 0v4"/>',
    "eye": '<path d="M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>',
    "cpu": '<rect x="6" y="6" width="12" height="12" rx="1.5"/><path d="M9 2v4M15 2v4M9 18v4M15 18v4M2 9h4M2 15h4M18 9h4M18 15h4"/>',
    "code": '<path d="M8 6l-6 6 6 6M16 6l6 6-6 6"/>',
    "api": '<path d="M4 12h4M16 12h4"/><rect x="8" y="8" width="8" height="8" rx="2"/>',
    "box": '<path d="M12 3l9 5-9 5-9-5z"/><path d="M3 8v8l9 5 9-5V8M12 13v8"/>',
}

def icon(name, size=16, color="currentColor", sw=1.75, extra=""):
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" '
            f'stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" {extra}>'
            f'{ICONS[name]}</svg>')

# ---- state system (shared by both consoles) ---------------------------------
# key: (label, colour key, icon)
STATES = {
    # agreement lifecycle
    "requested":  ("Requested", "grey", "dashed"),
    "matched":    ("Matched", "blue", "swap"),
    "pending":    ("Pending approval", "amber", "clock"),
    "active":     ("Active", "green", "shield"),
    "fulfilled":  ("Fulfilled", "green", "file"),
    "expired":    ("Expired", "grey", "hourglass"),
    "revoked":    ("Revoked", "red", "slash"),
    "rejected":   ("Rejected", "red", "x"),
    # job lifecycle
    "queued":     ("Queued", "grey", "dashed"),
    "checking":   ("Checking", "blue", "search"),
    "running":    ("Running", "teal", "play"),
    "inspecting": ("Inspecting results", "blue", "eye"),
    "delivered":  ("Delivered", "green", "check"),
    "failed":     ("Failed", "red", "alert"),
    # run / misc
    "scheduled":  ("Scheduled", "grey", "cal"),
    "negotiating":("Negotiating", "blue", "swap"),
    "partial":    ("Partially delivered", "amber", "alert"),
    "finished":   ("Finished", "green", "check"),
    "waiting":    ("Waiting for approval", "amber", "clock"),
    "enabled":    ("Enabled", "green", "check"),
    "disabled":   ("Disabled", "grey", "slash"),
    "healthy":    ("Healthy", "green", "check"),
    "synced":     ("Synced", "green", "check"),
    "unreachable":("Unreachable", "red", "alert"),
    "skipped":    ("Not selected", "grey", "slash"),
    # ADR-026 visit outcomes (12 Sep 2026)
    "refused":    ("Refused", "red", "slash"),
    "timedout":   ("Timed out", "grey", "hourglass"),
    "pruned":     ("Pruned", "grey", "dashed"),
    "dropped":    ("Dropped", "grey", "slash"),
    "stopped":    ("Stopped", "grey", "stop"),
    "redacted":   ("Delivered · redacted", "green", "check"),
}

def badge(key, label=None, size="sm"):
    lab, col, ic = STATES[key]
    lab = label or lab
    c = PAL[col]; tint = PAL[col + "_tint"]
    pad = "2px 8px 2px 6px" if size == "sm" else "4px 10px 4px 8px"
    fs = "12px" if size == "sm" else "13px"
    return (f'<span style="display:inline-flex;align-items:center;gap:5px;padding:{pad};border-radius:999px;'
            f'background:{tint};color:{c};font-size:{fs};font-weight:600;line-height:16px;white-space:nowrap">'
            f'{icon(ic, 13, sw=2)}<span>{lab}</span></span>')

def dot(key, size=10):
    _, col, _ = STATES[key]
    return f'<span style="display:inline-block;width:{size}px;height:{size}px;border-radius:50%;background:{PAL[col]}"></span>'

# ---- CSS -------------------------------------------------------------------
def css(app):
    accent = PAL[app]; accent_dark = PAL[app + "_dark"]; tint = PAL[app + "_tint"]
    return f"""
    body {{ margin:0; background:{PAL['ground']}; color:{PAL['ink']}; font-family:"Source Sans 3", "Segoe UI", system-ui, sans-serif; font-size:14px; line-height:1.45; -webkit-font-smoothing:antialiased; }}
    a {{ color:{accent}; text-decoration:none; }} a:hover {{ color:{accent_dark}; text-decoration:underline; }}
    h1,h2,h3 {{ font-family:"Source Serif 4", Georgia, "Times New Roman", serif; font-weight:600; margin:0; letter-spacing:-0.01em; }}
    h1 {{ font-size:26px; line-height:32px; }} h2 {{ font-size:18px; line-height:24px; }} h3 {{ font-size:15px; line-height:20px; }}
    table {{ border-collapse:collapse; width:100%; }}
    th {{ text-align:left; font-size:12px; font-weight:600; color:{PAL['muted']}; text-transform:uppercase; letter-spacing:.04em; padding:10px 12px; border-bottom:1px solid {PAL['line']}; }}
    td {{ padding:11px 12px; border-bottom:1px solid {PAL['line2']}; vertical-align:middle; }}
    tr.selected td {{ background:{tint}; }}
    .mono {{ font-family:"SFMono-Regular", Menlo, Consolas, monospace; font-size:12.5px; }}
    .muted {{ color:{PAL['muted']}; }} .faint {{ color:{PAL['faint']}; }}
    .card {{ background:{PAL['surface']}; border:1px solid {PAL['line']}; border-radius:8px; overflow:hidden; }}
    .btn {{ display:inline-flex; align-items:center; gap:6px; height:36px; padding:0 14px; border-radius:6px; font-weight:600; font-size:14px; border:1px solid transparent; white-space:nowrap; }}
    .btn-primary {{ background:{accent}; color:#fff; }}
    .btn-secondary {{ background:{PAL['surface']}; color:{PAL['ink']}; border-color:{PAL['line']}; }}
    .btn-danger {{ background:{PAL['surface']}; color:{PAL['red']}; border-color:{PAL['red']}; }}
    .btn-ghost {{ background:transparent; color:{accent}; }}
    .input {{ display:flex; align-items:center; height:36px; padding:0 10px; border:1px solid {PAL['line']}; border-radius:6px; background:{PAL['surface']}; color:{PAL['ink']}; }}
    .label {{ font-size:12px; font-weight:600; color:{PAL['muted']}; letter-spacing:.03em; text-transform:uppercase; }}
    .chip {{ display:inline-flex; align-items:center; gap:6px; height:26px; padding:0 8px 0 10px; border-radius:999px; background:{tint}; color:{accent_dark}; font-weight:600; font-size:13px; }}
    .kv {{ display:grid; grid-template-columns: 160px minmax(0,1fr); gap:6px 16px; font-size:14px; }}
    .kv dt {{ color:{PAL['muted']}; }} .kv dd {{ margin:0; }}
    .nav a {{ display:flex; align-items:center; gap:10px; height:38px; padding:0 12px; border-radius:6px; color:{PAL['ink']}; font-weight:500; }}
    .nav a.active {{ background:{tint}; color:{accent_dark}; font-weight:600; }}
    .tab {{ padding:10px 2px; margin-right:22px; font-weight:600; color:{PAL['muted']}; border-bottom:2px solid transparent; }}
    .tab.active {{ color:{accent_dark}; border-bottom-color:{accent}; }}
    """

# ---- shell -----------------------------------------------------------------
HANDLER_NAV = [("Trains", "train"), ("Stations", "station"), ("Plans", "map"), ("Runs", "play"), ("Results", "download")]
STATION_NAV = [("Dashboard", "grid"), ("Jobs", "list"), ("Datasets", "db"), ("Access conditions", "policy"),
               ("Approvals", "inbox"), ("Agreements", "file"), ("Audit", "audit"), ("Settings", "settings")]
GATEWAY_NAV = [("Overview", "grid"), ("My resources", "db"), ("Conditions", "policy"), ("Approvals", "inbox"),
               ("Agreements", "file"), ("Activity", "audit"), ("Networks", "map"), ("Settings", "settings")]

def wordmark(app):
    accent = PAL[app]
    name = {"handler": "Train Handler", "station": "Data Station", "gateway": "Individual Gateway"}[app]
    mark = ('<svg width="28" height="28" viewBox="0 0 28 28" aria-hidden="true">'
            f'<rect x="1" y="1" width="26" height="26" rx="7" fill="{accent}"/>'
            '<path d="M7 18h14M9 10h10M12 6v4M16 6v4M10 18v3M18 18v3M9 14h10" stroke="#fff" stroke-width="2" stroke-linecap="round" fill="none"/></svg>')
    return (f'<div style="display:flex;align-items:center;gap:10px">{mark}'
            f'<div style="line-height:1.1"><div style="font-family:\'Source Serif 4\',Georgia,serif;font-weight:600;font-size:15px">{name}</div>'
            f'<div style="font-size:11px;color:{PAL["muted"]};letter-spacing:.06em;text-transform:uppercase">FAIR Data Train</div></div></div>')

def shell(app, active, title, body, *, role=None, crumbs=None, org=None, user=None, actions="", subtitle=None, badge_count=None):
    nav = {"handler": HANDLER_NAV, "station": STATION_NAV, "gateway": GATEWAY_NAV}[app]
    accent = PAL[app]
    items = ""
    for lab, ic in nav:
        cls = ' class="active"' if lab == active else ""
        count = ""
        if badge_count and lab in badge_count:
            count = (f'<span style="margin-left:auto;background:{PAL["amber"]};color:#fff;border-radius:999px;font-size:11px;'
                     f'font-weight:700;padding:1px 7px">{badge_count[lab]}</span>')
        items += f'<a href="#"{cls}>{icon(ic, 18)}<span>{lab}</span>{count}</a>'
    role_html = ""
    if role:
        role_html = (f'<span style="display:inline-flex;align-items:center;gap:6px;height:26px;padding:0 10px;border-radius:6px;'
                     f'border:1px solid {PAL["line"]};background:{PAL["surface"]};font-size:12.5px;font-weight:600;color:{PAL["muted"]}">'
                     f'{icon("user", 14)}<span>{role}</span></span>')
    crumb_html = ""
    if crumbs:
        parts = [f'<a href="#">{c}</a>' if i < len(crumbs) - 1 else f'<span class="muted">{c}</span>' for i, c in enumerate(crumbs)]
        sep = ' <span class="faint">/</span> '
        crumb_html = f'<div style="display:flex;gap:8px;font-size:13px;margin-bottom:6px">{sep.join(parts)}</div>'
    sub_html = f'<div class="muted" style="margin-top:4px;font-size:14px">{subtitle}</div>' if subtitle else ""
    org = org or {"handler": "EU-CardioNet consortium", "station": "University of Twente Data Station", "gateway": "Cardiology Research Group"}[app]
    user = user or {"handler": "M. de Vries", "station": "A. Jansen", "gateway": "A. Jansen"}[app]
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
  <style>{css(app)}</style>
</helmet>
<div style="width:1440px;height:1080px;display:flex;background:{PAL['ground']};overflow:hidden;position:relative">
  <aside style="width:224px;flex:0 0 224px;display:flex;flex-direction:column;background:{PAL['surface']};border-right:1px solid {PAL['line']};padding:18px 14px">
    {wordmark(app)}
    <nav class="nav" style="display:flex;flex-direction:column;gap:2px;margin-top:26px">{items}</nav>
    <div style="margin-top:auto;padding:12px;border-top:1px solid {PAL['line2']};display:flex;flex-direction:column;gap:6px">
      <div style="font-weight:600;font-size:13px">{org}</div>
      <div class="muted" style="font-size:12.5px">{user}</div>
    </div>
  </aside>
  <div style="flex:1;display:flex;flex-direction:column;min-width:0">
    <header style="height:56px;display:flex;align-items:center;justify-content:space-between;padding:0 32px;border-bottom:1px solid {PAL['line']};background:{PAL['surface']}">
      <div class="input" style="width:340px;height:32px;gap:8px;color:{PAL['faint']}">{icon("search", 15)}<span>{"Search resources, agreements, stations…" if app == "gateway" else "Search trains, stations, runs…"}</span></div>
      <div style="display:flex;align-items:center;gap:12px">{role_html}<span style="width:30px;height:30px;border-radius:50%;background:{accent};color:#fff;display:inline-flex;align-items:center;justify-content:center;font-weight:600;font-size:12px">{''.join(w[0] for w in user.replace('.', ' ').split()[-2:]) if user else 'U'}</span></div>
    </header>
    <main style="flex:1;padding:24px 32px 28px;display:flex;flex-direction:column;gap:18px;min-height:0">
      <div style="display:flex;align-items:flex-end;justify-content:space-between;gap:16px">
        <div>{crumb_html}<h1>{title}</h1>{sub_html}</div>
        <div style="display:flex;gap:10px">{actions}</div>
      </div>
      {body}
    </main>
  </div>
</div>
</x-dc>
</body>
</html>
"""

# ---- small components -------------------------------------------------------
def btn(label, kind="secondary", ic=None, title=None):
    i = icon(ic, 16) if ic else ""
    t = f' title="{title}" aria-label="{title}"' if title else ""
    lab = f'<span>{label}</span>' if label else ""
    return f'<span class="btn btn-{kind}"{t}>{i}{lab}</span>'

def card(inner, style="", title=None, aside=""):
    head = ""
    if title:
        head = (f'<div style="display:flex;align-items:center;justify-content:space-between;padding:14px 18px;border-bottom:1px solid {PAL["line2"]}">'
                f'<h2>{title}</h2><div>{aside}</div></div>')
    return f'<section class="card" style="{style}">{head}{inner}</section>'

def kpi(label, value, sub=None, state=None):
    s = badge(state) if state else (f'<span class="muted" style="font-size:13px">{sub}</span>' if sub else "")
    return (f'<div class="card" style="padding:16px 18px;display:flex;flex-direction:column;gap:6px">'
            f'<div class="label">{label}</div>'
            f'<div style="font-family:\'Source Serif 4\',Georgia,serif;font-size:30px;line-height:34px;font-weight:600">{value}</div>{s}</div>')

def table(headers, rows, selected=None, widths=None):
    ths = "".join((f'<th style="width:{widths[i]}">{h}</th>' if widths and widths[i] else f'<th>{h}</th>') for i, h in enumerate(headers))
    trs = ""
    for i, r in enumerate(rows):
        cls = ' class="selected"' if selected is not None and i == selected else ""
        trs += f'<tr{cls}>' + "".join(f'<td>{c}</td>' for c in r) + '</tr>'
    return f'<table><thead><tr>{ths}</tr></thead><tbody>{trs}</tbody></table>'

def stepper(steps, current):
    out = '<div style="display:flex;align-items:center;gap:10px">'
    for i, s in enumerate(steps):
        done = i < current; cur = i == current
        bg = PAL["handler"] if (done or cur) else PAL["surface"]
        fg = "#fff" if (done or cur) else PAL["muted"]
        bd = PAL["handler"] if (done or cur) else PAL["line"]
        inner = icon("check", 14, "#fff", 2.5) if done else f'<span style="font-size:12px;font-weight:700">{i+1}</span>'
        out += (f'<div style="display:flex;align-items:center;gap:8px"><span style="width:24px;height:24px;border-radius:50%;background:{bg};color:{fg};'
                f'border:1px solid {bd};display:inline-flex;align-items:center;justify-content:center">{inner}</span>'
                f'<span style="font-weight:{600 if cur else 500};color:{PAL["ink"] if cur else PAL["muted"]}">{s}</span></div>')
        if i < len(steps) - 1:
            out += f'<span style="width:40px;height:1px;background:{PAL["line"]}"></span>'
    return out + '</div>'

def policy_sentence(parts):
    """Human-readable policy summary: list of (verb, text, colour-key)."""
    segs = []
    for verb, text, col in parts:
        segs.append(f'<span style="color:{PAL[col]};font-weight:600">{verb}</span> {text}')
    return '<span style="line-height:1.6">' + "; ".join(segs) + '.</span>'

def toggle(on=True, app="station"):
    bg = PAL[app] if on else PAL["line"]
    x = 18 if on else 2
    return (f'<span style="display:inline-block;width:36px;height:20px;border-radius:999px;background:{bg};position:relative">'
            f'<span style="position:absolute;top:2px;left:{x}px;width:16px;height:16px;border-radius:50%;background:#fff"></span></span>')

def avatar(initials, color):
    return (f'<span style="width:28px;height:28px;border-radius:50%;background:{color};color:#fff;display:inline-flex;align-items:center;'
            f'justify-content:center;font-size:11px;font-weight:700">{initials}</span>')

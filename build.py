#!/usr/bin/env python3
"""Build static site from tools.json into dist/. Usage: python3 build.py"""
import json, html, re, shutil, datetime, pathlib
from collections import Counter
from urllib.parse import quote
CONFIG = {"site_name": "Toolsmith Weekly",  # <- swap the brand name here
          "tagline": "The newest AI tools and models, sorted every Friday.",
          "base_url": "https://toolsmithweekly.com",  # no trailing slash; canonical URLs, sitemap, robots
          "subscribe_url": "https://toolsmithweekly.beehiiv.com/subscribe",
          "suggest_email": "hello@toolsmithweekly.com"}
CONFIG["base_url"] = CONFIG["base_url"].rstrip("/")
# Links and assets stay relative (style.css, tools/<slug>.html, ../index.html) so they
# work on the custom-domain root and in a local dist/ preview.
# beehiiv's public subscribe page does not prefill ?email=, so signup is a link there.
N = CONFIG["site_name"]; R = pathlib.Path(__file__).parent; OUT = R / "dist"
BASE = CONFIG["base_url"]
VALUE = CONFIG["tagline"]
# Verdicts cite public reports. The site does not claim a hands-on check of its own.
METHOD = "Verdicts based on public reports and benchmarks, re-checked twice a week."
e = lambda s: html.escape(str(s), quote=True)
slug = lambda s: re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
tools = json.load(open(R / "tools.json"))
for t in tools:
    t["slug"] = slug(t["name"])
    t.setdefault("date_added", "2026-10-21")
tools.sort(key=lambda t: (t["date_added"], t["name"]), reverse=True)
TODAY = datetime.date.today()
NEW_CUTOFF = TODAY - datetime.timedelta(days=7)
LAUNCH = datetime.date(2026, 10, 20)  # initial batch; do not badge these
def is_new(t):
    # Website only. The newsletter archive does not render this badge.
    # Hidden for the launch batch: date_added must be after 2026-10-20 and within 7 days.
    added = datetime.date.fromisoformat(t["date_added"])
    return added > LAUNCH and NEW_CUTOFF <= added <= TODAY
# Homepage teaser. Names must exist in tools.json. Swap the list each Friday.
PICKS = ["Claude Code", "Lovable", "n8n", "Godot AI"]
ISSUES = [{"title": "Issue #1", "when": "Coming Friday, Oct 23",
           "note": "The first letter goes out Friday, October 23, 2026. No link until it is sent."}]
# Reader-facing names for the categories stored in tools.json. Unknown categories
# fall through to the raw name so a new one still appears in the grid and the filters.
CAT_LABEL = {
    "coding agents": "Coding agents",
    "vibe-coding app builders": "Vibe coding",
    "AI agents/automation": "Automation",
    "gaming/game dev": "Gaming",
    "general": "Creative",
}
CAT_BLURB = {
    "coding agents": "Editors and terminal agents that change a codebase.",
    "vibe-coding app builders": "Prompt-to-app builders for sites and web apps.",
    "AI agents/automation": "Workflow tools and agents that run a task for you.",
    "gaming/game dev": "Engines, assets, and tools for making games.",
    "general": "Voice, image, and other creative tools.",
}
CAT_ORDER = list(CAT_LABEL)
VERDICTS = [
    ("use", "Use it", "Worth using now for the job it claims."),
    ("try", "Try it", "Worth a short trial before you rely on it."),
    ("wait", "Wait", "Price, access, or the evidence is not settled."),
    ("skip", "Skip", "Closed, shutting down, or a poor fit."),
]
VERDICT_LABEL = {key: label for key, label, _ in VERDICTS}
suggest_href = "mailto:" + CONFIG["suggest_email"] + "?" + "&".join([
    "subject=" + quote("Tool suggestion for Toolsmith Weekly"),
    "body=" + quote("I'm an indie developer.\n\nTool name:\nWebsite:\nWhat it does:\nWhy it belongs in Toolsmith Weekly:\n")])
# Pixel anvil, side view. "+" is the lit top face, "#" is the body. 40 columns.
ANVIL_ROWS = [
    "................++++++++++++++++++......",
    "..............+++++++++++++++++++++.....",
    "............++++++++++++++++++++++++....",
    "........############################....",
    "....################################....",
    ".####################################...",
    "######################################..",
    "................########................",
    "................########................",
    "............################............",
    "........########################........",
    "....################################....",
    ".######################################.",
    ".#######.......................########.",
    ".######.........................#######.",
]
def anvil_svg():
    rects = []
    for y, row in enumerate(ANVIL_ROWS):
        x = 0
        while x < len(row):
            if row[x] == ".":
                x += 1
                continue
            ch = row[x]
            x2 = x + 1
            while x2 < len(row) and row[x2] == ch:
                x2 += 1
            fill = "#ffffff" if ch == "+" else "#b9b4ea"
            rects.append(f'<rect x="{x}" y="{y}" width="{x2 - x}" height="1" fill="{fill}"/>')
            x = x2
    h = len(ANVIL_ROWS)
    return (
        f'<svg class="anvil" viewBox="0 0 40 {h}" width="400" height="{h * 10}" '
        'aria-hidden="true" focusable="false" shape-rendering="crispEdges">'
        + "".join(rects) + "</svg>"
    )
CSS = """:root{--bg:#08071a;--card:#141228;--bd:rgba(216,214,255,.16);--tx:#f4f2ff;--mu:#c9c6e2;--ac:#d7defe;--ink:#141228}
*{box-sizing:border-box}[hidden]{display:none!important}
html{color-scheme:dark}
body{margin:0;font:17px/1.6 ui-sans-serif,system-ui,-apple-system,"Segoe UI",Helvetica,Arial,sans-serif;background-color:var(--bg);background-image:radial-gradient(880px 460px at 110% -8%,rgba(108,86,210,.22),transparent 52%),radial-gradient(720px 420px at -12% -6%,rgba(48,78,170,.16),transparent 48%);color:var(--tx)}
a{color:var(--ac)}img,svg{max-width:100%;height:auto}
:focus-visible{outline:2px solid var(--ac);outline-offset:3px}
.skip{position:absolute;left:12px;top:-48px;background:var(--ac);color:var(--ink);padding:10px 14px;border-radius:8px;z-index:30;font-weight:700;text-decoration:none}
.skip:focus{top:12px}
.sr{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}
.w{max-width:1120px;margin:auto;padding:0 24px}
header{position:sticky;top:0;z-index:10;background:#08071a;border-bottom:1px solid var(--bd)}
.bar{display:flex;gap:18px;align-items:center;flex-wrap:wrap;min-height:68px;position:relative}
.logo{font-weight:700;font-size:1.02rem;letter-spacing:-.02em;color:var(--tx);text-decoration:none;white-space:nowrap}
.nav-toggle{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}
.nav-btn{display:none;margin-left:auto;background:transparent;color:var(--tx);border:1px solid var(--bd);border-radius:999px;padding:8px 14px;min-height:44px;font:inherit;cursor:pointer}
.nav-btn .m-close{display:none}
.nav-toggle:focus-visible + .nav-btn{outline:2px solid var(--ac);outline-offset:3px}
header nav{display:flex;gap:4px 16px;align-items:center;flex-wrap:nowrap;margin-left:auto}
header nav a{color:var(--mu);text-decoration:none;min-height:44px;display:inline-flex;align-items:center}
header nav a.on{color:var(--tx)}
header nav a:hover{color:var(--tx)}
a.btn{display:inline-flex;align-items:center;justify-content:center;background:var(--ac);color:var(--ink);text-decoration:none;border-radius:999px;padding:12px 18px;min-height:44px;font-weight:700;letter-spacing:-.01em}
a.btn:hover{background:#eef1ff}
header nav a.btn{color:var(--ink);padding:8px 14px;min-height:40px}
.hero{position:relative;overflow:hidden;padding:48px 0 36px;border-bottom:1px solid var(--bd)}
.hero:before{content:"";position:absolute;inset:0;background-image:linear-gradient(rgba(255,255,255,.035) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.035) 1px,transparent 1px);background-size:64px 64px;mask-image:radial-gradient(circle at 72% 40%,#000,transparent 72%);pointer-events:none}
.orb{position:absolute;border-radius:50%;pointer-events:none}
.orb-a{width:520px;height:520px;right:-40px;top:-140px;background:radial-gradient(circle,rgba(132,112,255,.28),rgba(132,112,255,0) 68%);animation:drift 16s ease-in-out infinite}
.orb-b{width:340px;height:340px;left:-80px;bottom:-180px;background:radial-gradient(circle,rgba(64,100,220,.18),rgba(64,100,220,0) 70%);animation:drift 20s ease-in-out infinite reverse}
.hero-grid{position:relative;z-index:1;display:grid;grid-template-columns:1.25fr .9fr;gap:28px;align-items:center}
.eyebrow,.kicker{margin:0 0 12px;font-size:.8125rem;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:var(--ac)}
.hero h1{margin:0 0 12px;max-width:none;font-size:clamp(2.35rem,3.6vw,3.45rem);line-height:1.05;letter-spacing:-.042em;font-weight:700}
.lede{margin:0 0 18px;max-width:36rem;font-size:1.05rem;line-height:1.45;color:var(--mu)}
.actions{display:flex;gap:16px;align-items:center;flex-wrap:wrap;margin:0}
.actions a:not(.btn){font-weight:650;text-underline-offset:3px}
.sec-head > a,.actions a:not(.btn),.band-head a{min-height:44px;display:inline-flex;align-items:center}
.hero-art{position:relative;display:grid;place-items:center;min-height:220px}
.anvil-glow{position:absolute;width:240px;height:140px;border-radius:50%;background:radial-gradient(circle,rgba(150,140,255,.34),rgba(150,140,255,0) 70%);transform:translateY(28px)}
.anvil{position:relative;width:min(100%,380px);image-rendering:pixelated}
.metrics{position:relative;z-index:1;display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-top:28px}
.metric{display:flex;flex-direction:column;justify-content:space-between;gap:6px;min-height:92px;padding:16px 18px;border-radius:16px;border:1px solid var(--bd);background:rgba(10,8,28,.55);color:inherit;text-decoration:none}
a.metric:hover{border-color:rgba(215,222,254,.6);background:#1b1836}
.metric b{color:var(--tx);font-size:1.35rem;letter-spacing:-.03em;line-height:1.15}
.metric span{color:var(--mu);font-size:.92rem}
.rise{animation:rise .7s cubic-bezier(.16,.84,.32,1) both}
.d2{animation-delay:.06s}.d3{animation-delay:.12s}.d4{animation-delay:.18s}.d5{animation-delay:.24s}
h1,h2,h3{font-weight:700;letter-spacing:-.03em;line-height:1.15}
h2{margin:0;font-size:clamp(1.6rem,2.4vw,2.05rem)}
.page{padding:56px 0 88px}
.pagehead{margin:0 0 28px;max-width:40rem}
.pagehead h1{margin:0 0 10px;font-size:clamp(2.1rem,4vw,3.1rem);letter-spacing:-.04em;line-height:1.05}
.band{padding:52px 0 56px}
.band-alt{background:#0e0c24;box-shadow:inset 0 1px 0 var(--bd),inset 0 -1px 0 var(--bd)}
.band-head{display:flex;justify-content:space-between;align-items:center;gap:12px 20px;margin:0 0 14px}
.band-head h2{font-size:1.25rem}
.sec{margin:48px 0}
.sec-head{display:flex;justify-content:space-between;align-items:center;gap:16px 28px;flex-wrap:wrap;margin-bottom:18px}
.sec-head p,.intro{color:var(--mu);margin:8px 0 0;max-width:40rem}
.bento{display:grid;grid-template-columns:1.35fr 1fr 1fr;gap:12px}
.bento .featured{grid-row:span 2}
.bento .pick:last-child{grid-column:2 / span 2}
a.pick,a.catcard,.card,.vk,.panel,.issue{background:rgba(20,18,40,.9);border:1px solid var(--bd);border-radius:16px}
a.pick,a.catcard{text-decoration:none;color:inherit;display:flex;flex-direction:column;gap:8px;min-height:100%;padding:16px;transition:border-color .2s ease,background .2s ease,transform .2s ease}
a.pick:hover,a.catcard:hover{transform:translateY(-3px);border-color:rgba(215,222,254,.6);background:#1b1836}
a.pick h3{margin:0;color:var(--tx);font-size:1.05rem}
.featured h3{font-size:1.55rem;letter-spacing:-.03em}
.featured .clamp{-webkit-line-clamp:3}
a.pick p{margin:0;color:var(--mu);font-size:.95rem}
a.pick .checked{margin-top:auto}
.clamp{display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.cats{display:grid;grid-template-columns:repeat(5,1fr);gap:12px}
a.catcard{min-height:118px;justify-content:space-between}
a.catcard strong{color:var(--tx);font-size:1rem}
a.catcard .num{color:var(--tx);font-size:1.7rem;letter-spacing:-.04em;font-variant-numeric:tabular-nums;line-height:1}
.vkey{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}
.vk{padding:16px}
.vk p{margin:10px 0 0;color:var(--mu);font-size:.95rem}
.split{display:grid;grid-template-columns:1.15fr .85fr;gap:16px}
.panel{padding:24px}
.panel h2,.panel h3{margin:0 0 8px}
.mu{color:var(--mu)}
.ctl{display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin:0 0 10px}
.ctl #cnt{margin:0}
input,select{background:#100e24;color:var(--tx);border:1px solid var(--bd);border-radius:12px;padding:12px 14px;min-height:48px;font:inherit}
input::placeholder{color:#b7b3d0;opacity:1}
input:hover,select:hover{border-color:rgba(215,222,254,.45)}
#q{flex:1;min-width:220px}
.chips{display:flex;gap:8px;flex-wrap:wrap}
.chip{background:transparent;border:1px solid var(--bd);color:var(--tx);border-radius:999px;padding:8px 14px;min-height:44px;cursor:pointer;font:inherit}
.chip:hover{border-color:var(--ac)}
.chip.on{background:var(--ac);color:var(--ink);border-color:var(--ac);font-weight:700}
.appbar{position:sticky;top:69px;z-index:8;background:#08071a;border-bottom:1px solid var(--bd);padding:12px 0 10px}
.dirhead{padding:32px 0 4px}
.dirhead h1{margin:0;font-size:clamp(1.8rem,3vw,2.4rem);letter-spacing:-.04em}
.dirgrid{padding:18px 0 72px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:12px;margin:0}
.card{padding:14px;display:flex;flex-direction:column;gap:8px;transition:border-color .2s ease,transform .2s ease}
.card:hover{border-color:rgba(215,222,254,.5);transform:translateY(-2px)}
.card .name{margin:0;font-size:1.02rem}.card .name a{color:var(--tx);text-decoration:none}
.card .name a:hover{color:var(--ac)}
.card .clamp{margin:0;color:var(--mu);font-size:.92rem}
.v{display:inline-flex;align-items:center;gap:7px;font-weight:700;font-size:.82rem;line-height:1;padding:5px 10px 5px 8px;border-radius:999px;letter-spacing:.04em;text-transform:uppercase}
.v:before{content:"";width:7px;height:7px;border-radius:50%;background:currentColor;flex:none}
.v-use{background:#0f3d2c;color:#c9fbe0}.v-try{background:#0c3a52;color:#cfefff}.v-wait{background:#3f320f;color:#ffe6ad}.v-skip{background:#4a1824;color:#ffd0d8}
.badge-new{display:inline-block;font-weight:700;font-size:.8rem;padding:4px 8px;border-radius:999px;background:#16324f;color:#d5ecff;letter-spacing:.04em;text-transform:uppercase}
.cat,.checked,.price{font-size:.92rem;color:var(--mu)}
.bucket{margin:36px 0 8px}
.bucket .count{color:var(--mu);font-weight:600;font-size:1rem}
.issue{padding:20px;margin:16px 0}
footer{border-top:1px solid var(--bd);padding:28px 0 40px;color:var(--mu);font-size:.95rem}
footer nav{display:flex;gap:4px 18px;flex-wrap:wrap}
footer nav a{color:var(--mu);text-decoration:none;min-height:44px;display:inline-flex;align-items:center}
footer nav a:hover{color:var(--tx)}
footer p{margin:8px 0 0;max-width:46rem}
dl dt{color:var(--mu);margin-top:16px;font-size:.8rem;letter-spacing:.08em;text-transform:uppercase}dl dd{margin:4px 0 0}
.vrow{display:flex;flex-wrap:wrap;align-items:center;gap:8px 10px}
.back{margin:8px 0 0}
.empty{margin:8px 0 0}
@keyframes rise{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:none}}
@keyframes drift{0%,100%{transform:translate3d(0,0,0)}50%{transform:translate3d(0,18px,0) scale(1.05)}}
@keyframes floaty{0%,100%{transform:translateY(0)}50%{transform:translateY(-8px)}}
.anvil{animation:floaty 7.5s ease-in-out infinite}
@media(max-width:1120px){
.nav-btn{display:inline-flex}
header nav{display:none;width:100%;flex-direction:column;align-items:stretch;gap:0;margin-left:0;padding:4px 0 14px}
.nav-toggle:checked ~ nav{display:flex}
.nav-toggle:checked + .nav-btn .m-open{display:none}
.nav-toggle:checked + .nav-btn .m-close{display:inline}
header nav a{min-height:48px}
header nav a.btn{display:flex;margin-top:8px;text-align:center}
}
@media(max-width:980px){
.hero{padding:32px 0 28px}
.hero-grid,.split,.metrics{grid-template-columns:1fr}
.hero-art{order:-1;justify-content:start;min-height:0;margin-bottom:4px}
.anvil{width:200px}
.anvil-glow{width:180px;height:100px}
.orb-a{width:280px;height:280px;right:-80px;top:-140px}
.bento{grid-template-columns:1fr 1fr}
.bento .featured,.bento .pick:last-child{grid-row:auto;grid-column:1 / -1}
.vkey{grid-template-columns:1fr 1fr}
.cats{grid-template-columns:repeat(3,1fr)}
.band{padding:36px 0 40px}
}
@media(max-width:640px){
.w{padding:0 18px}
.bento,.vkey,.metrics{grid-template-columns:1fr}
.cats{grid-template-columns:1fr 1fr}
.cats a:last-child{grid-column:1 / -1}
.actions{flex-direction:column;align-items:stretch}
.hero .btn{width:100%}
.page{padding:28px 0 56px}
.chips{flex-wrap:nowrap;overflow-x:auto}
.chip{flex:none}
.appbar{top:64px}
}
@media(prefers-reduced-motion:reduce){
.rise,.orb,.anvil{animation:none}
a.pick,a.catcard,.card{transition:none}
a.pick:hover,a.catcard:hover,.card:hover{transform:none}
}"""
_MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")
def checked_iso(t):
    # Last review date. Missing verdict_checked falls back to date_added so new tools still build.
    return t.get("verdict_checked") or t["date_added"]
def fmt_date(iso):
    d = datetime.date.fromisoformat(iso)
    return f"{_MONTHS[d.month - 1]} {d.day}, {d.year}"
def vlabel(t):
    return VERDICT_LABEL.get(t["verdict"], t["verdict"])
def cat_label(name):
    return CAT_LABEL.get(name, name)
def verdict_stamp(t):
    iso = checked_iso(t)
    return f'<span class="checked">Verdict checked <time datetime="{e(iso)}">{e(fmt_date(iso))}</time></span>'
def verdict_checked_row(t):
    iso = checked_iso(t)
    return f'<dt>Verdict checked</dt><dd><time datetime="{e(iso)}">{e(fmt_date(iso))}</time></dd>'
NAV = [
    ("index.html", "Home", "home"),
    ("tools/", "Tool Directory", "tools"),
    ("verdicts/", "Current Verdicts", "verdicts"),
    ("this-week.html", "This Week", "week"),
    ("newsletter/", "Newsletter Archive", "news"),
    ("suggest/", "Suggest a Tool", "suggest"),
]
def section_of(path):
    if path in ("index.html", ""):
        return "home"
    if path.startswith("tools/"):
        return "tools"
    if path.startswith("verdicts/"):
        return "verdicts"
    if path.startswith("this-week"):
        return "week"
    if path.startswith("newsletter/"):
        return "news"
    if path.startswith("suggest/"):
        return "suggest"
    return ""
def nav_html(depth, path):
    p = "../" * depth
    sec = section_of(path)
    links = []
    for href, label, key in NAV:
        cls = ' class="on"' if key == sec else ""
        links.append(f'<a href="{p}{href}"{cls}>{label}</a>')
    links.append(f'<a class="btn" href="{e(CONFIG["subscribe_url"])}">Subscribe</a>')
    return ('<input class="nav-toggle" id="nav-toggle" type="checkbox" aria-controls="site-nav">'
            '<label class="nav-btn" for="nav-toggle"><span class="m-open">Menu</span>'
            '<span class="m-close">Close</span></label>'
            '<nav id="site-nav" aria-label="Primary">' + "".join(links) + "</nav>")
def foot_html(depth):
    p = "../" * depth
    links = "".join(f'<a href="{p}{href}">{label}</a>' for href, label, _ in NAV)
    links += f'<a href="{e(CONFIG["subscribe_url"])}">Subscribe</a>'
    return (f'<nav aria-label="Footer">{links}</nav>'
            f'<p>{e(N)}. {e(VALUE)} {e(METHOD)}</p>')
def schema_graph(extra=None):
    # Organization and WebSite on every page. SearchAction matches the directory ?q= filter.
    graph = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "Organization",
                "@id": f"{BASE}/#organization",
                "name": N,
                "url": f"{BASE}/",
                "email": CONFIG["suggest_email"],
                "description": VALUE,
                "logo": {"@type": "ImageObject", "url": f"{BASE}/og.jpg", "width": 1200, "height": 630},
            },
            {
                "@type": "WebSite",
                "@id": f"{BASE}/#website",
                "name": N,
                "url": f"{BASE}/",
                "description": VALUE + " Straight verdicts: use it, try it, wait, or skip.",
                "publisher": {"@id": f"{BASE}/#organization"},
                "potentialAction": {
                    "@type": "SearchAction",
                    "target": BASE + "/tools/?q={search_term_string}",
                    "query-input": "required name=search_term_string",
                },
            },
        ],
    }
    if extra:
        graph["@graph"].extend(extra)
    raw = json.dumps(graph, ensure_ascii=False).replace("<", "\\u003c")
    return f'<script type="application/ld+json">{raw}</script>'
def item_list(name, items):
    return {
        "@type": "ItemList",
        "name": name,
        "numberOfItems": len(items),
        "itemListElement": [
            {"@type": "ListItem", "position": i, "name": t["name"], "url": f"{BASE}/tools/{t['slug']}.html"}
            for i, t in enumerate(items, 1)
        ],
    }
def page(title, desc, body, path, depth=0, nodes=None, bleed=False):
    p = "../" * depth
    canon = f"{BASE}/{path}"
    img = f"{BASE}/og.jpg"
    metas = (
        f'<meta property="og:title" content="{e(title)}">'
        f'<meta property="og:description" content="{e(desc)}">'
        f'<meta property="og:type" content="website">'
        f'<meta property="og:url" content="{canon}">'
        f'<meta property="og:image" content="{img}">'
        f'<meta property="og:image:width" content="1200">'
        f'<meta property="og:image:height" content="630">'
        f'<meta name="twitter:card" content="summary_large_image">'
        f'<meta name="twitter:image" content="{img}">'
        f'<link rel="canonical" href="{canon}">'
        f'<meta name="theme-color" content="#08071a">'
        f'<meta name="color-scheme" content="dark">'
    )
    inner = body if bleed else f'<div class="w page">{body}</div>'
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title><meta name="description" content="{e(desc)}">{metas}
<link rel="stylesheet" href="{p}style.css">{schema_graph(nodes)}</head><body>
<a class="skip" href="#content">Skip to content</a>
<header><div class="w"><div class="bar"><a class="logo" href="{p}index.html">{e(N)}</a>{nav_html(depth, path)}</div></div></header>
<main id="content">{inner}</main><footer><div class="w">{foot_html(depth)}</div></footer></body></html>"""
def badge_html(t):
    # Website cards only. Callers on the newsletter archive must not use this.
    return '<span class="badge-new">New this week</span>' if is_new(t) else ""
def card(t, prefix, level="h2"):
    badge = badge_html(t)
    return f"""<article class="card" data-cat="{e(t['category'])}" data-date="{t['date_added']}" data-checked="{e(checked_iso(t))}" data-text="{e((t['name']+' '+t['description']+' '+' '.join(t['use_cases'])+' '+t['category']).lower())}">
<div class="vrow">{badge}<span class="v v-{e(t['verdict'])}">{e(vlabel(t))}</span></div><{level} class="name"><a href="{prefix}{t['slug']}.html">{e(t['name'])}</a></{level}>
<p class="clamp">{e(t['verdict_reason'])}</p><p class="checked">{e(cat_label(t['category']))} · {verdict_stamp(t)}</p></article>"""
def pick_card(t, featured=False):
    cls = "pick featured" if featured else "pick"
    return f"""<a class="{cls}" href="tools/{t['slug']}.html"><span class="v v-{e(t['verdict'])}">{e(vlabel(t))}</span><h3>{e(t['name'])}</h3><p class="clamp">{e(t['verdict_reason'])}</p><span class="cat">{e(cat_label(t['category']))}</span>{verdict_stamp(t)}</a>"""
SIGNUP = f"""<div class="panel" id="signup"><p class="kicker">Free</p><h2>Get the Friday letter</h2><p class="mu">One email a week: the newest tools, with a verdict.</p>
<p><a class="btn" href="{e(CONFIG['subscribe_url'])}">Subscribe free</a></p>
<p class="mu">Opens the Toolsmith Weekly letter on beehiiv.</p></div>"""
by_name = {t["name"]: t for t in tools}
missing = [name for name in PICKS if name not in by_name]
if missing:
    raise SystemExit("Homepage picks missing from tools.json: " + ", ".join(missing))
picks = [by_name[name] for name in PICKS]
counts = Counter(t["category"] for t in tools)
known = [c for c in CAT_ORDER if c in counts]
extra = sorted(c for c in counts if c not in CAT_LABEL)
categories = known + extra
shutil.rmtree(OUT, ignore_errors=True)
(OUT / "tools").mkdir(parents=True)
(OUT / "verdicts").mkdir(parents=True)
(OUT / "newsletter").mkdir(parents=True)
(OUT / "issues").mkdir(parents=True)
(OUT / "suggest").mkdir(parents=True)
(OUT / "style.css").write_text(CSS)
shutil.copyfile(R / "brand" / "og.jpg", OUT / "og.jpg")
shutil.copyfile(R / "CNAME", OUT / "CNAME")
def cat_href(name):
    return "tools/?cat=" + quote(name, safe="")
cat_cards = "".join(
    f'<a class="catcard" href="{cat_href(c)}"><span class="num">{counts[c]}</span><strong>{e(cat_label(c))}</strong></a>'
    for c in categories)
verdict_key = "".join(
    f'<article class="vk"><span class="v v-{key}">{e(label)}</span><p>{e(blurb)}</p></article>'
    for key, label, blurb in VERDICTS)
latest_issue = ISSUES[0]
checked_dates = sorted({checked_iso(t) for t in tools})
if len(checked_dates) == 1:
    checked_html = f'Verdicts checked <time datetime="{e(checked_dates[0])}">{e(fmt_date(checked_dates[0]))}</time>'
else:
    checked_html = (
        f'Verdicts checked <time datetime="{e(checked_dates[0])}">{e(fmt_date(checked_dates[0]))}</time>'
        f' to <time datetime="{e(checked_dates[-1])}">{e(fmt_date(checked_dates[-1]))}</time>'
    )
pick_html = "".join(pick_card(t, i == 0) for i, t in enumerate(picks))
home = f"""<section class="hero"><div class="orb orb-a" aria-hidden="true"></div><div class="orb orb-b" aria-hidden="true"></div>
<div class="w hero-grid"><div class="hero-copy">
<h1 class="rise">{e(VALUE)}</h1>
<p class="lede rise d2">Use, try, wait, or skip. {e(METHOD)}</p>
<p class="actions rise d3"><a class="btn" href="{e(CONFIG['subscribe_url'])}">Subscribe free</a><a href="tools/">Open the directory</a></p>
</div><div class="hero-art" aria-hidden="true"><div class="anvil-glow"></div>{anvil_svg()}</div></div>
<div class="w"><div class="metrics rise d4"><div class="metric"><b>{len(tools)}</b><span>Tools</span></div><div class="metric"><b><time datetime="{e(checked_dates[-1])}">{e(fmt_date(checked_dates[-1]))}</time></b><span>Verdicts checked</span></div><a class="metric" href="#how"><b>Public sources</b><span>Re-checked twice a week</span></a></div></div></section>
<section class="band" id="picks"><div class="w"><div class="band-head"><h2>This week's picks</h2><a href="this-week.html">See this week</a></div>
<div class="bento">{pick_html}</div></div></section>
<section class="band band-alt" id="categories"><div class="w"><div class="band-head"><h2>Browse by category</h2><a href="tools/">Full directory</a></div>
<div class="cats">{cat_cards}</div></div></section>
<section class="band" id="how"><div class="w"><div class="band-head"><h2>How we verdict</h2><a href="verdicts/">See current verdicts</a></div>
<p class="lede">{e(METHOD)} Each verdict links the report it came from.</p>
<div class="vkey">{verdict_key}</div></div></section>
<section class="band band-alt" id="letter"><div class="w"><div class="split"><article class="panel"><p class="kicker">Newsletter</p><h2>{e(latest_issue['title'])}</h2><p>{e(latest_issue['when'])}</p><p class="mu">{e(latest_issue['note'])}</p><p><a href="newsletter/">Newsletter archive</a></p></article>{SIGNUP}</div></div></section>"""
(OUT / "index.html").write_text(page(
    f"{N} — the newest AI tools, sorted every Friday",
    f"{VALUE} Straight verdicts: use it, try it, wait, or skip.",
    home, "index.html", nodes=[item_list("This week's picks", picks)], bleed=True))
cats = sorted(counts)
chips = '<button class="chip on" data-c="">All</button>' + "".join(
    f'<button class="chip" data-c="{e(c)}">{e(cat_label(c))}</button>' for c in cats)
JS = """<script>const q=document.getElementById('q'),s=document.getElementById('sort'),g=document.getElementById('grid'),cs=[...document.querySelectorAll('.chip')];let cat='';
const cards=[...g.children],cnt=document.getElementById('cnt');function sync(){const u=new URL(location.href);const v=q.value.trim();if(v)u.searchParams.set('q',v);else u.searchParams.delete('q');if(cat)u.searchParams.set('cat',cat);else u.searchParams.delete('cat');history.replaceState(null,'',u);}
function run(){const v=q.value.toLowerCase().trim();let n=0;
const o=[...cards].sort((a,b)=>s.value==='newest'?b.dataset.date.localeCompare(a.dataset.date):s.value==='oldest'?a.dataset.date.localeCompare(b.dataset.date):a.querySelector('.name').textContent.localeCompare(b.querySelector('h3').textContent));
o.forEach(c=>{const ok=(!cat||c.dataset.cat===cat)&&(!v||c.dataset.text.includes(v));c.hidden=!ok;n+=ok;g.appendChild(c)});cnt.textContent=n+(n===1?' tool':' tools');}
q.oninput=()=>{sync();run()};s.onchange=run;cs.forEach(b=>b.onclick=()=>{cs.forEach(x=>x.classList.remove('on'));b.classList.add('on');cat=b.dataset.c;sync();run()});
const params=new URLSearchParams(location.search);const want=params.get('cat')||'';const hit=cs.find(b=>b.dataset.c===want);if(hit){cs.forEach(x=>x.classList.remove('on'));hit.classList.add('on');cat=want;}
const initialQ=params.get('q')||'';if(initialQ)q.value=initialQ;run();</script>"""
directory = f"""<div class="w dirhead"><h1>Tool directory</h1></div>
<div class="appbar"><div class="w"><div class="ctl"><label class="sr" for="q">Search</label><input id="q" type="search" placeholder="Search tools, use cases" autocomplete="off"><label class="sr" for="sort">Sort</label><select id="sort"><option value="newest">Newest</option><option value="oldest">Oldest</option><option value="az">A–Z</option></select><p class="mu" id="cnt">{len(tools)} tools</p></div>
<div class="chips" role="group" aria-label="Filter by category">{chips}</div></div></div>
<div class="w dirgrid"><div class="grid" id="grid">{''.join(card(t, "") for t in tools)}</div></div>{JS}"""
(OUT / "tools" / "index.html").write_text(page(
    f"Tool directory — {N}",
    f"Searchable directory of {len(tools)} AI tools, with a use, try, wait, or skip verdict on each.",
    directory, "tools/", 1, nodes=[item_list("Tool directory", tools)], bleed=True))
buckets = []
for key, label, blurb in VERDICTS:
    group = [t for t in tools if t["verdict"] == key]
    if group:
        inner = f'<div class="grid">{"".join(card(t, "../tools/", "h3") for t in group)}</div>'
    else:
        inner = '<p class="empty mu">Nothing in this bucket right now.</p>'
    buckets.append(
        f'<section class="bucket" id="{key}"><h2><span class="v v-{key}">{e(label)}</span> <span class="count">{len(group)}</span></h2>'
        f'<p class="mu">{e(blurb)}</p>{inner}</section>')
(OUT / "verdicts" / "index.html").write_text(page(
    f"Current verdicts — {N}",
    "Tools grouped under Use it, Try it, Wait, and Skip, with the date each verdict was checked.",
    f'<header class="pagehead"><p class="kicker">Checked {e(fmt_date(checked_dates[-1]))}</p><h1>Current verdicts</h1><p class="lede">Grouped by the latest check. The stamp is the day that verdict was last reviewed.</p></header>{"".join(buckets)}',
    "verdicts/", 1, nodes=[item_list("Current verdicts", tools)]))
latest = max(datetime.date.fromisoformat(t["date_added"]) for t in tools)
cut = latest - datetime.timedelta(days=7)
wk = [t for t in tools if datetime.date.fromisoformat(t["date_added"]) > cut]
week_grid = f"<div class='grid'>{''.join(card(t, 'tools/') for t in wk)}</div>" if wk else "<p class='mu'>Nothing new in the last seven days.</p>"
(OUT / "this-week.html").write_text(page(
    f"This week in AI tools — {N}",
    f"AI tools added in the week ending {latest}.",
    f'<header class="pagehead"><p class="kicker">Added through {e(fmt_date(latest.isoformat()))}</p><h1>This week</h1><p class="lede">{len(wk)} tools added in the 7 days up to {e(fmt_date(latest.isoformat()))}.</p></header>{week_grid}<div class="sec">{SIGNUP}</div>',
    "this-week.html"))
for t in tools:
    b = f"""<p class="back"><a href="index.html">Tool directory</a> · {e(cat_label(t['category']))}</p><h1>{e(t['name'])}</h1><p class="vrow">{badge_html(t)}<span class="v v-{e(t['verdict'])}">{e(vlabel(t))}</span> {verdict_stamp(t)}</p><p>{e(t['verdict_reason'])}</p><p>{e(t['description'])}</p>
<dl><dt>Use cases</dt><dd><ul>{''.join(f'<li>{e(u)}</li>' for u in t['use_cases'])}</ul></dd><dt>Pricing</dt><dd>{e(t['pricing'])}</dd><dt>Website</dt><dd><a href="{e(t['url'])}" rel="noopener">{e(t['url'])}</a></dd>
<dt>Source</dt><dd><a href="{e(t['source'])}" rel="noopener">{e(t['source'])}</a></dd>{verdict_checked_row(t)}<dt>Added</dt><dd><time datetime="{e(t['date_added'])}">{e(fmt_date(t['date_added']))}</time></dd></dl>
<p><a href="../verdicts/#{e(t['verdict'])}">More {e(vlabel(t))} verdicts</a></p>
<script type="application/ld+json">{json.dumps({"@context":"https://schema.org","@type":"SoftwareApplication","name":t["name"],"url":t["url"],"applicationCategory":t["category"],"description":t["description"],"dateModified":checked_iso(t)})}</script>"""
    (OUT / "tools" / f"{t['slug']}.html").write_text(page(
        f"{t['name']} review: {vlabel(t)} — {N}",
        f"{t['name']}: {t['description']} Verdict: {vlabel(t)} — {t['verdict_reason']}"[:300],
        b, f"tools/{t['slug']}.html", 1))
issue_cards = "".join(
    f'<article class="issue"><h2 style="margin:0 0 6px">{e(i["title"])}</h2><p style="margin:0">{e(i["when"])}</p><p class="mu" style="margin:8px 0 0">{e(i["note"])}</p></article>'
    for i in ISSUES)
(OUT / "newsletter" / "index.html").write_text(page(
    f"Newsletter Archive — {N}",
    "Archive of Toolsmith Weekly letters. Issue 1 arrives Friday, October 23, 2026.",
    f'<header class="pagehead"><p class="kicker">Letters</p><h1>Newsletter Archive</h1><p class="lede">The weekly letter. Upcoming letters are listed here, and a link is added only after the letter is sent.</p></header>{issue_cards}<div class="sec">{SIGNUP}</div>',
    "newsletter/", 1))
# Old /issues/ path. Meta refresh plus a plain link. Kept out of the sitemap.
(OUT / "issues" / "index.html").write_text(f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Newsletter Archive — {e(N)}</title>
<meta name="robots" content="noindex">
<meta http-equiv="refresh" content="0; url=../newsletter/">
<link rel="canonical" href="{BASE}/newsletter/">
<meta name="description" content="The newsletter archive has moved.">
<link rel="stylesheet" href="../style.css"></head><body>
<main class="w" style="padding:48px 0"><h1>Newsletter Archive</h1>
<p>This page has moved.</p>
<p><a href="../newsletter/">Go to the newsletter archive</a></p></main></body></html>""")
suggest_body = f"""<header class="pagehead"><p class="kicker">For builders</p><h1>Suggest a tool</h1><p class="lede">Indie developers: send a tool you built, or one you want a straight verdict on.</p></header>
<p><a class="btn" href="{e(suggest_href)}">Suggest a tool by email</a></p>
<p class="mu">Opens your mail app to {e(CONFIG['suggest_email'])} with the subject filled in. No account and no third-party form.</p><div class="sec">{SIGNUP}</div>"""
(OUT / "suggest" / "index.html").write_text(page(
    f"Suggest a tool — {N}",
    "Indie developers can email a tool suggestion to Toolsmith Weekly.",
    suggest_body, "suggest/", 1))
urls = ["index.html", "tools/", "verdicts/", "this-week.html", "newsletter/", "suggest/"] + [f"tools/{t['slug']}.html" for t in tools]
(OUT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + "".join(f"<url><loc>{BASE}/{u}</loc></url>" for u in urls) + "</urlset>")
(OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {BASE}/sitemap.xml\n")
new_count = sum(is_new(t) for t in tools)
llms = [
    f"# {N}",
    "",
    f"> {VALUE}",
    "",
    f"{N} sorts new AI tools for coding, vibe coding, automation, games, and creative work. {METHOD} Each tool has a use, try, wait, or skip verdict, and the date on a verdict is the day it was last checked. The directory currently lists {len(tools)} tools. Tools added after 2026-10-20 and within the last 7 days are marked New this week on the website only. That badge is not used in the newsletter.",
    "",
    "## Pages",
    "",
    f"- [Home]({BASE}/): Landing page with this week's picks, categories, how verdicts work, and the latest letter.",
    f"- [Tool directory]({BASE}/tools/): Search, filter by category, and sort the full list. Newest is the default sort. Category links use a ?cat= query. A text search uses ?q=.",
    f"- [Current verdicts]({BASE}/verdicts/): Tools grouped under Use it, Try it, Wait, and Skip, with the date each verdict was checked.",
    f"- [This week]({BASE}/this-week.html): Tools added in the seven days up to the newest date in the directory.",
    f"- [Newsletter archive]({BASE}/newsletter/): The weekly letter. Issue 1 is coming Friday, October 23, 2026. The old /issues/ path redirects here.",
    f"- [Suggest a tool]({BASE}/suggest/): Indie developers can email {CONFIG['suggest_email']} with a tool suggestion.",
    f"- [Subscribe]({CONFIG['subscribe_url']}): Free weekly letter on beehiiv.",
    "",
    "## Tools",
    "",
]
for t in tools:
    mark = " New this week." if is_new(t) else ""
    llms.append(f"- [{t['name']}]({BASE}/tools/{t['slug']}.html): {vlabel(t)} — {t['description']}{mark}")
(OUT / "llms.txt").write_text("\n".join(llms) + "\n")
print(f"Built {len(tools)} tool pages into {OUT} ({new_count} new this week as of {TODAY})")

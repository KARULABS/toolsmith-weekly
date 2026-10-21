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
CSS = """:root{--bg:#07051f;--ink:#040030;--card:#141244;--bd:#2c2866;--tx:#f4f2fb;--mu:#b7b3d6;--ac:#b7c4ff}
*{box-sizing:border-box}[hidden]{display:none!important}
body{margin:0;font:16px/1.55 system-ui,sans-serif;background:var(--bg);color:var(--tx)}
a{color:var(--ac)}img{max-width:100%;height:auto}
.w{max-width:1120px;margin:auto;padding:0 20px}
header{background:var(--ink);border-bottom:1px solid var(--bd);position:sticky;top:0;z-index:5}
.bar{display:flex;gap:16px;align-items:center;flex-wrap:wrap;padding:12px 0;min-height:60px}
.logo{font-weight:800;font-size:1.05rem;letter-spacing:.01em;color:var(--tx);text-decoration:none;white-space:nowrap}
.nav-toggle{position:absolute;left:-999px}
.nav-btn{display:none;margin-left:auto;background:transparent;color:var(--tx);border:1px solid var(--bd);border-radius:8px;padding:6px 12px;font:inherit;cursor:pointer}
.nav-btn .m-close{display:none}
header nav{display:flex;gap:14px;align-items:center;flex-wrap:nowrap;margin-left:auto}
header nav a{color:var(--mu);text-decoration:none}
header nav a.on{color:var(--tx)}
a.btn{display:inline-block;background:var(--ac);color:#140e30;text-decoration:none;border-radius:8px;padding:10px 16px;font-weight:700}
header nav a.btn{color:#140e30}
.hero{display:grid;grid-template-columns:1.15fr .85fr;gap:28px;align-items:center;background:var(--ink);border:1px solid var(--bd);border-radius:16px;padding:28px;margin:28px 0 8px}
.hero h1{margin:0 0 8px;font-size:2.4rem;letter-spacing:-.03em;line-height:1.1}
.lede{font-size:1.2rem;margin:0 0 18px}
.actions{display:flex;gap:16px;align-items:center;flex-wrap:wrap;margin:0}
.hero-mark{width:100%;max-height:250px;object-fit:contain;object-position:center;border-radius:12px;background:var(--ink)}
h2{font-size:1.35rem;margin:0}
.sec{margin:36px 0}
.sec-head{display:flex;justify-content:space-between;align-items:baseline;gap:12px;flex-wrap:wrap;margin-bottom:12px}
.sec-head p,.intro{color:var(--mu);margin:6px 0 0}
.picks{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}
a.pick{background:var(--card);border:1px solid var(--bd);border-radius:12px;padding:14px;text-decoration:none;color:inherit;display:flex;flex-direction:column;gap:8px;min-height:100%}
a.pick:hover{border-color:var(--ac)}
a.pick h3{margin:0;color:var(--tx);font-size:1.05rem}
a.pick p{margin:0;color:var(--mu);font-size:.92rem}
.cats{display:grid;grid-template-columns:repeat(auto-fill,minmax(190px,1fr));gap:12px}
a.catcard{display:flex;flex-direction:column;gap:6px;background:var(--card);border:1px solid var(--bd);border-radius:12px;padding:14px;text-decoration:none;color:inherit;min-height:100%}
a.catcard:hover{border-color:var(--ac)}
a.catcard strong{color:var(--tx)}
a.catcard span{color:var(--mu);font-size:.92rem}
.vkey{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-top:12px}
.vk{background:var(--card);border:1px solid var(--bd);border-radius:12px;padding:14px}
.vk p{margin:8px 0 0;color:var(--mu);font-size:.92rem}
.split{display:grid;grid-template-columns:1.15fr .85fr;gap:12px}
.panel{background:var(--card);border:1px solid var(--bd);border-radius:12px;padding:18px}
.panel h2,.panel h3{margin:0 0 8px}
.mu{color:var(--mu)}
.ctl{display:flex;gap:8px;flex-wrap:wrap;margin:18px 0}
input,select{background:var(--card);color:var(--tx);border:1px solid var(--bd);border-radius:8px;padding:10px 12px;font-size:1rem}
#q{flex:1;min-width:220px}
.chips{display:flex;gap:6px;flex-wrap:wrap}
.chip{background:var(--card);border:1px solid var(--bd);color:var(--tx);border-radius:999px;padding:6px 12px;cursor:pointer;font-size:.9rem}
.chip.on{background:var(--ac);color:#140e30;border-color:var(--ac)}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:14px;margin:16px 0 40px}
.card{background:var(--card);border:1px solid var(--bd);border-radius:12px;padding:16px;display:flex;flex-direction:column;gap:6px}
.card h3{margin:0;font-size:1.1rem}.card h3 a{color:var(--tx);text-decoration:none}
.v{display:inline-block;font-weight:700;font-size:.75rem;padding:2px 8px;border-radius:6px;text-transform:uppercase;letter-spacing:.03em}
.v-use{background:#1f5f3a;color:#b8f5cf}.v-try{background:#1d4e6e;color:#c5e8ff}.v-skip{background:#6b2330;color:#ffc4cc}.v-wait{background:#6a5520;color:#ffe7a8}
.badge-new{display:inline-block;font-weight:700;font-size:.75rem;padding:2px 8px;border-radius:6px;background:#16324f;color:#c5e4ff;text-transform:uppercase}
.cat{font-size:.8rem;color:var(--mu)}
.bucket{margin:28px 0 8px}
.bucket .count{color:var(--mu);font-weight:500;font-size:.95rem}
.issue{background:var(--card);border:1px solid var(--bd);border-radius:12px;padding:16px;margin:14px 0}
footer{border-top:1px solid var(--bd);padding:22px 0 32px;color:var(--mu);font-size:.9rem;margin-top:12px}
footer nav{display:flex;gap:8px 16px;flex-wrap:wrap}
footer nav a{color:var(--mu);text-decoration:none}
footer p{margin:10px 0 0}
dl dt{color:var(--mu);margin-top:14px;font-size:.85rem;text-transform:uppercase}dl dd{margin:4px 0 0}
.vrow{display:flex;flex-wrap:wrap;align-items:center;gap:8px}
.checked{font-size:.8rem;color:var(--mu)}
@media(max-width:1040px){
.nav-btn{display:inline-block}
header nav{display:none;width:100%;flex-direction:column;align-items:stretch;gap:2px;margin-left:0;padding:4px 0 12px}
.nav-toggle:checked ~ nav{display:flex}
.nav-toggle:checked + .nav-btn .m-open{display:none}
.nav-toggle:checked + .nav-btn .m-close{display:inline}
header nav a{padding:8px 0}
header nav a.btn{display:block;margin-top:6px;text-align:center}
}
@media(max-width:900px){
.hero,.split{grid-template-columns:1fr}
.vkey,.picks{grid-template-columns:1fr 1fr}
.hero h1{font-size:2rem}
.hero-mark{max-width:480px}
}
@media(max-width:560px){
.picks,.vkey{grid-template-columns:1fr}
.hero{padding:20px}
.actions{flex-direction:column;align-items:stretch}
.hero a.btn{text-align:center}
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
    return ('<input class="nav-toggle" id="nav-toggle" type="checkbox">'
            '<label class="nav-btn" for="nav-toggle"><span class="m-open">Menu</span>'
            '<span class="m-close">Close</span></label><nav>' + "".join(links) + "</nav>")
def foot_html(depth):
    p = "../" * depth
    links = "".join(f'<a href="{p}{href}">{label}</a>' for href, label, _ in NAV)
    links += f'<a href="{e(CONFIG["subscribe_url"])}">Subscribe</a>'
    return (f'<nav>{links}</nav><p>{e(N)}. {e(VALUE)} Verdicts come from linked public sources unless stated otherwise.</p>')
def page(title, desc, body, path, depth=0):
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
        f'<meta name="theme-color" content="#040030">'
    )
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title><meta name="description" content="{e(desc)}">{metas}
<link rel="stylesheet" href="{p}style.css"></head><body>
<header><div class="w"><div class="bar"><a class="logo" href="{p}index.html">{e(N)}</a>{nav_html(depth, path)}</div></div></header>
<main class="w">{body}</main><footer><div class="w">{foot_html(depth)}</div></footer></body></html>"""
def badge_html(t):
    # Website cards only. Callers on the newsletter archive must not use this.
    return '<span class="badge-new">New this week</span>' if is_new(t) else ""
def card(t, prefix):
    badge = badge_html(t)
    return f"""<article class="card" data-cat="{e(t['category'])}" data-date="{t['date_added']}" data-checked="{e(checked_iso(t))}" data-text="{e((t['name']+' '+t['description']+' '+' '.join(t['use_cases'])+' '+t['category']).lower())}">
<span class="cat">{e(cat_label(t['category']))} · added {e(fmt_date(t['date_added']))}</span><h3><a href="{prefix}{t['slug']}.html">{e(t['name'])}</a></h3>
<div class="vrow">{badge}<span class="v v-{e(t['verdict'])}">{e(vlabel(t))}</span> {verdict_stamp(t)}</div><p class="mu" style="margin:2px 0 0">{e(t['verdict_reason'])}</p><p style="margin:4px 0">{e(t['description'])}</p><span class="cat">{e(t['pricing'])}</span></article>"""
def pick_card(t):
    return f"""<a class="pick" href="tools/{t['slug']}.html"><span class="cat">{e(cat_label(t['category']))}</span><h3>{e(t['name'])}</h3><span class="vrow"><span class="v v-{e(t['verdict'])}">{e(vlabel(t))}</span> {verdict_stamp(t)}</span><p>{e(t['verdict_reason'])}</p></a>"""
SIGNUP = f"""<div class="panel" id="signup"><h2>Get the Friday letter</h2><p class="mu">One email a week: the newest tools, with a verdict.</p>
<p><a class="btn" href="{e(CONFIG['subscribe_url'])}">Subscribe free</a></p>
<p class="mu">Free. Opens the Toolsmith Weekly letter on beehiiv.</p></div>"""
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
shutil.copyfile(R / "brand" / "header-anvil.jpg", OUT / "anvil.jpg")
shutil.copyfile(R / "CNAME", OUT / "CNAME")
def cat_href(name):
    return "tools/?cat=" + quote(name, safe="")
cat_cards = "".join(
    f'<a class="catcard" href="{cat_href(c)}"><strong>{e(cat_label(c))}</strong>'
    f'<span>{counts[c]} {"tool" if counts[c] == 1 else "tools"}</span>'
    f'<span>{e(CAT_BLURB.get(c, "Tools filed under " + c + "."))}</span></a>'
    for c in categories)
verdict_key = "".join(
    f'<article class="vk"><span class="v v-{key}">{e(label)}</span><p>{e(blurb)}</p></article>'
    for key, label, blurb in VERDICTS)
latest_issue = ISSUES[0]
home = f"""<section class="hero"><div>
<h1>{e(N)}</h1>
<p class="lede">{e(VALUE)}</p>
<p class="actions"><a class="btn" href="{e(CONFIG['subscribe_url'])}">Subscribe free</a><a href="tools/">Browse the directory</a></p>
</div><img class="hero-mark" src="anvil.jpg" alt="" width="1280" height="720"></section>
<section class="sec" id="picks"><div class="sec-head"><div><h2>This week's picks</h2><p>Four from the current list. Open a card for the full verdict.</p></div><a href="this-week.html">See this week</a></div>
<div class="picks">{''.join(pick_card(t) for t in picks)}</div></section>
<section class="sec" id="categories"><div class="sec-head"><div><h2>Browse by category</h2><p>Jump into the directory with that filter already on.</p></div><a href="tools/">Full directory</a></div>
<div class="cats">{cat_cards}</div></section>
<section class="sec" id="how"><div class="sec-head"><div><h2>How we verdict</h2><p>Four buckets. Each tool links the public source the verdict came from.</p></div><a href="verdicts/">See current verdicts</a></div>
<div class="vkey">{verdict_key}</div></section>
<section class="sec" id="letter"><div class="split"><article class="panel"><h2>Latest letter</h2><p style="margin:0 0 6px">{e(latest_issue['when'])}</p><h3 style="margin:0 0 8px">{e(latest_issue['title'])}</h3><p class="mu">{e(latest_issue['note'])}</p><p><a href="newsletter/">Newsletter archive</a></p></article>{SIGNUP}</div></section>"""
(OUT / "index.html").write_text(page(
    f"{N} — the newest AI tools, sorted every Friday",
    f"{VALUE} Straight verdicts: use it, try it, wait, or skip.",
    home, "index.html"))
cats = sorted(counts)
chips = '<button class="chip on" data-c="">All</button>' + "".join(
    f'<button class="chip" data-c="{e(c)}">{e(cat_label(c))}</button>' for c in cats)
JS = """<script>const q=document.getElementById('q'),s=document.getElementById('sort'),g=document.getElementById('grid'),cs=[...document.querySelectorAll('.chip')];let cat='';
const cards=[...g.children],cnt=document.getElementById('cnt');function run(){const v=q.value.toLowerCase().trim();let n=0;
const o=[...cards].sort((a,b)=>s.value==='newest'?b.dataset.date.localeCompare(a.dataset.date):s.value==='oldest'?a.dataset.date.localeCompare(b.dataset.date):a.querySelector('h3').textContent.localeCompare(b.querySelector('h3').textContent));
o.forEach(c=>{const ok=(!cat||c.dataset.cat===cat)&&(!v||c.dataset.text.includes(v));c.hidden=!ok;n+=ok;g.appendChild(c)});cnt.textContent=n+' tools';}
q.oninput=run;s.onchange=run;cs.forEach(b=>b.onclick=()=>{cs.forEach(x=>x.classList.remove('on'));b.classList.add('on');cat=b.dataset.c;const u=new URL(location.href);if(cat)u.searchParams.set('cat',cat);else u.searchParams.delete('cat');history.replaceState(null,'',u);run()});
const want=new URLSearchParams(location.search).get('cat')||'';const hit=cs.find(b=>b.dataset.c===want);if(hit){cs.forEach(x=>x.classList.remove('on'));hit.classList.add('on');cat=want;}run();</script>"""
directory = f"""<h1>Tool directory</h1><p class="mu">Search, filter, and sort every tool. Newest is the default.</p>
<div class="ctl"><input id="q" type="search" placeholder="Search tools, use cases…" aria-label="Search"><select id="sort" aria-label="Sort"><option value="newest">Newest</option><option value="oldest">Oldest</option><option value="az">A–Z</option></select></div>
<div class="chips">{chips}</div><p class="mu" id="cnt"></p><div class="grid" id="grid">{''.join(card(t, "") for t in tools)}</div>{JS}"""
(OUT / "tools" / "index.html").write_text(page(
    f"Tool directory — {N}",
    f"Searchable directory of {len(tools)} AI tools, with a use, try, wait, or skip verdict on each.",
    directory, "tools/", 1))
buckets = []
for key, label, blurb in VERDICTS:
    group = [t for t in tools if t["verdict"] == key]
    if group:
        inner = f'<div class="grid">{"".join(card(t, "../tools/") for t in group)}</div>'
    else:
        inner = '<p class="mu">Nothing in this bucket right now.</p>'
    buckets.append(
        f'<section class="bucket" id="{key}"><h2>{e(label)} <span class="count">{len(group)}</span></h2>'
        f'<p class="mu">{e(blurb)}</p>{inner}</section>')
(OUT / "verdicts" / "index.html").write_text(page(
    f"Current verdicts — {N}",
    "Tools grouped under Use it, Try it, Wait, and Skip, with the date each verdict was checked.",
    f'<h1>Current verdicts</h1><p class="mu">Grouped by the latest check. The stamp is the day that verdict was last reviewed.</p>{"".join(buckets)}',
    "verdicts/", 1))
latest = max(datetime.date.fromisoformat(t["date_added"]) for t in tools)
cut = latest - datetime.timedelta(days=7)
wk = [t for t in tools if datetime.date.fromisoformat(t["date_added"]) > cut]
week_grid = f"<div class='grid'>{''.join(card(t, 'tools/') for t in wk)}</div>" if wk else "<p class='mu'>Nothing new in the last seven days.</p>"
(OUT / "this-week.html").write_text(page(
    f"This week in AI tools — {N}",
    f"AI tools added in the week ending {latest}.",
    f"<h1>This week</h1><p class='mu'>{len(wk)} tools added in the 7 days up to {latest.isoformat()}.</p>{week_grid}<div class='sec'>{SIGNUP}</div>",
    "this-week.html"))
for t in tools:
    b = f"""<p class="cat" style="margin-top:24px"><a href="index.html">← Tool directory</a> · {e(cat_label(t['category']))}</p><h1>{e(t['name'])}</h1><p class="vrow">{badge_html(t)}<span class="v v-{e(t['verdict'])}">{e(vlabel(t))}</span> {verdict_stamp(t)}</p><p>{e(t['verdict_reason'])}</p><p>{e(t['description'])}</p>
<dl><dt>Use cases</dt><dd><ul>{''.join(f'<li>{e(u)}</li>' for u in t['use_cases'])}</ul></dd><dt>Pricing</dt><dd>{e(t['pricing'])}</dd><dt>Website</dt><dd><a href="{e(t['url'])}" rel="noopener">{e(t['url'])}</a></dd>
<dt>Source</dt><dd><a href="{e(t['source'])}" rel="noopener">{e(t['source'])}</a></dd>{verdict_checked_row(t)}<dt>Added</dt><dd><time datetime="{e(t['date_added'])}">{e(fmt_date(t['date_added']))}</time></dd></dl>
<p><a href="../verdicts/#{e(t['verdict'])}">More {e(vlabel(t))} verdicts</a></p>
<script type="application/ld+json">{json.dumps({"@context":"https://schema.org","@type":"SoftwareApplication","name":t["name"],"url":t["url"],"applicationCategory":t["category"],"description":t["description"]})}</script>"""
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
    f"<h1>Newsletter Archive</h1><p class='mu'>The weekly letter. Upcoming letters are listed here, and a link is added only after the letter is sent.</p>{issue_cards}<div class='sec'>{SIGNUP}</div>",
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
suggest_body = f"""<h1>Suggest a tool</h1><p>Indie developers: send a tool you built, or one you want a straight verdict on.</p>
<p><a href="{e(suggest_href)}">Suggest a tool by email</a></p>
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
    f"{N} sorts new AI tools for coding, vibe coding, automation, games, and creative work. Each tool has a use, try, wait, or skip verdict based on a linked public source. The date on a verdict is the day it was last checked. Tools added after 2026-10-20 and within the last 7 days are marked New this week on the website only. That badge is not used in the newsletter.",
    "",
    "## Pages",
    "",
    f"- [Home]({BASE}/): Landing page with this week's picks, categories, how verdicts work, and the latest letter.",
    f"- [Tool directory]({BASE}/tools/): Search, filter by category, and sort the full list. Newest is the default sort. Category links use a ?cat= query.",
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

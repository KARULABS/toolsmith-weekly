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
# Shown in the footer. The site does not claim a hands-on check of its own.
SOURCE_NOTE = "Where our info comes from: official pricing pages, docs and public announcements, linked on every tool page. Written with AI help and reviewed for accuracy."
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
ISSUES = [{"title": "Issue #1", "when": "Coming Oct 23, 2026",
           "note": "The first letter goes out Oct 23, 2026. No link until it is sent."}]
# Reader-facing names for the categories stored in tools.json. Unknown categories
# fall through to the raw name so a new one still appears in the grid and the filters.
CAT_LABEL = {
    "coding agents": "Coding Agents",
    "vibe-coding app builders": "Vibe Coding",
    "AI agents/automation": "Automation",
    "gaming/game dev": "Gaming",
}
CAT_ORDER = list(CAT_LABEL)
# Neutral first sentence of Our Take. Not shown as a label.
GUIDE = {
    "use": "Worth using now for the job it claims.",
    "try": "Worth a short trial before you rely on it.",
    "wait": "Price, access, or the evidence is not settled.",
    "skip": "Closed, shutting down, or a poor fit.",
}
suggest_href = "mailto:" + CONFIG["suggest_email"] + "?" + "&".join([
    "subject=" + quote("Tool suggestion for Toolsmith Weekly"),
    "body=" + quote("I'm an indie developer.\n\nTool name:\nWebsite:\nWhat it does:\nWhy it belongs in Toolsmith Weekly:\n")])
# Side-view pixel anvil. Horn left, flat face, heel, waist, two feet.
# h and t are the steel top, b the body, d the deep shade. Sparks are separate rects.
ANVIL_FILL = {
    "h": "#8d98c4",
    "t": "#5b6690",
    "b": "#3c4670",
    "m": "#2c365c",
    "d": "#1b2140",
}
SPARKS = (
    (4, 2, "#ffc94a"), (8, 1, "#fff2c2"), (11, 3, "#ff8a3d"), (14, 2, "#ffc94a"),
    (6, 4, "#ff8a3d"), (16, 1, "#fff2c2"), (9, 5, "#ffc94a"), (13, 4, "#ff8a3d"),
)
def anvil_grid():
    w, h = 58, 32
    g = [["."] * w for _ in range(h)]
    def rect(x, y, rw, rh, c):
        for yy in range(y, y + rh):
            for xx in range(x, x + rw):
                g[yy][xx] = c
    def put(x, y, c):
        if 0 <= x < w and 0 <= y < h:
            g[y][x] = c
    for x in range(2, 18):
        y_top = round(15 - 6 * ((x - 2) / 15))
        for y in range(y_top, 16):
            put(x, y, "b")
        put(x, y_top, "h")
        if g[y_top + 1][x] == "b":
            g[y_top + 1][x] = "t"
    rect(18, 8, 26, 1, "h")
    rect(18, 9, 26, 1, "t")
    rect(18, 10, 26, 6, "b")
    rect(44, 10, 8, 6, "b")
    rect(26, 16, 12, 5, "m")
    rect(14, 21, 32, 3, "b")
    rect(12, 24, 13, 4, "b")
    rect(35, 24, 13, 4, "b")
    filled = set("bmht")
    for y in range(h):
        for x in range(w):
            if g[y][x] not in ("b", "m"):
                continue
            below = y + 1 < h and (g[y + 1][x] in filled or g[y + 1][x] == "d")
            above = y > 0 and g[y - 1][x] in filled
            right = x + 1 < w and (g[y][x + 1] in filled or g[y][x + 1] == "d")
            if (not below) and above:
                g[y][x] = "d"
            elif (not right) and below:
                g[y][x] = "d"
    return g
def anvil_svg():
    grid = anvil_grid()
    rects = []
    for y, row in enumerate(grid):
        x = 0
        while x < len(row):
            ch = row[x]
            if ch not in ANVIL_FILL:
                x += 1
                continue
            x2 = x + 1
            while x2 < len(row) and row[x2] == ch:
                x2 += 1
            rects.append(
                f'<rect x="{x}" y="{y}" width="{x2 - x}" height="1" fill="{ANVIL_FILL[ch]}"/>')
            x = x2
    sparks = "".join(
        f'<rect class="spark" x="{x}" y="{y}" width="1" height="1" fill="{fill}"/>'
        for x, y, fill in SPARKS)
    height = len(grid)
    width = len(grid[0])
    return (
        f'<svg class="anvil" viewBox="0 0 {width} {height}" '
        'aria-hidden="true" focusable="false" shape-rendering="crispEdges">'
        + "".join(rects) + f'<g class="sparks">{sparks}</g></svg>'
    )
def mark_svg():
    # Header mark. Same steel and spark colors, drawn to read at 22px.
    rects = []
    def r(x, y, w, h, fill):
        rects.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}"/>')
    r(2, 1, 1, 1, "#fff2c2")
    r(5, 2, 1, 1, "#ffc94a")
    r(4, 3, 1, 1, "#ff8a3d")
    r(2, 5, 12, 1, "#8d98c4")
    r(1, 6, 14, 1, "#5b6690")
    r(2, 7, 12, 1, "#3c4670")
    r(6, 8, 4, 2, "#3c4670")
    r(4, 10, 8, 1, "#2c365c")
    r(3, 11, 3, 2, "#1b2140")
    r(10, 11, 3, 2, "#1b2140")
    return ('<svg class="mark" viewBox="0 0 16 16" aria-hidden="true" focusable="false" '
            f'shape-rendering="crispEdges">{"".join(rects)}</svg>')
def pix(rows, fill="#ffc94a"):
    rects = []
    for y, row in enumerate(rows):
        x = 0
        while x < len(row):
            if row[x] != "#":
                x += 1
                continue
            x2 = x + 1
            while x2 < len(row) and row[x2] == "#":
                x2 += 1
            rects.append(f'<rect x="{x}" y="{y}" width="{x2 - x}" height="1" fill="{fill}"/>')
            x = x2
    return "".join(rects)
CAT_ICON = {
    "coding agents": (
        "............",
        "............",
        "..##....##..",
        ".##......##.",
        "##........##",
        "##........##",
        ".##......##.",
        "..##....##..",
        "............",
        "......##....",
        "......##....",
        "............",
    ),
    "vibe-coding app builders": (
        "............",
        ".....##.....",
        ".....##.....",
        ".....##.....",
        ".....##.....",
        "############",
        ".....##.....",
        ".....##.....",
        ".....##.....",
        ".....##.....",
        "............",
        "............",
    ),
    "AI agents/automation": (
        "............",
        "..###..###..",
        "..#.#..#.#..",
        "..###..###..",
        "....#..#....",
        "....####....",
        "....#..#....",
        "..###..###..",
        "..#.#..#.#..",
        "..###..###..",
        "............",
        "............",
    ),
    "gaming/game dev": (
        "............",
        "...######...",
        "..########..",
        ".##.#..#.##.",
        ".##.#..#.##.",
        "..########..",
        "...######...",
        "............",
        "............",
        "............",
        "............",
        "............",
    ),
}
def cat_icon(name):
    rows = CAT_ICON.get(name, CAT_ICON["coding agents"])
    return ('<svg class="caticon" viewBox="0 0 12 12" aria-hidden="true" focusable="false" '
            f'shape-rendering="crispEdges">{pix(rows)}</svg>')
CSS = """:root{--bg:#070b1a;--bg2:#0b1124;--card:#0f1630;--card-h:#141c3b;--bd:rgba(148,163,214,.14);--bd-h:rgba(148,163,214,.32);--tx:#eef2ff;--mu:#9aa6c7;--ac:#ff8a3d;--ac2:#ffc94a;--ink:#140a02;--sans:ui-sans-serif,system-ui,-apple-system,"Segoe UI",Helvetica,Arial,sans-serif;--mono:ui-monospace,"JetBrains Mono",Menlo,monospace}
*{box-sizing:border-box}[hidden]{display:none!important}
html{color-scheme:dark}
body{margin:0;font:17px/1.6 var(--sans);background-color:var(--bg);background-image:radial-gradient(900px 480px at 78% -10%,rgba(255,138,61,.10),transparent 60%),radial-gradient(800px 500px at 10% -10%,rgba(56,92,200,.14),transparent 60%);color:var(--tx)}
a{color:var(--ac);text-underline-offset:3px;text-decoration-color:rgba(255,138,61,.5)}
a:hover{color:var(--ac);text-decoration-color:var(--ac)}
img,svg{max-width:100%;height:auto}
:focus-visible{outline:2px solid var(--ac);outline-offset:3px}
.skip{position:absolute;left:12px;top:-48px;background:var(--ac);color:var(--ink);padding:10px 14px;border-radius:8px;z-index:30;font-weight:700;text-decoration:none}
.skip:focus{top:12px}
.sr{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}
.w{max-width:1120px;margin:auto;padding:0 24px}
header{position:sticky;top:0;z-index:10;background:rgba(7,11,26,.72);backdrop-filter:saturate(160%) blur(12px);-webkit-backdrop-filter:saturate(160%) blur(12px);border-bottom:1px solid var(--bd)}
.bar{display:flex;gap:18px;align-items:center;flex-wrap:wrap;min-height:60px;position:relative}
.logo{display:inline-flex;align-items:center;gap:10px;font-weight:650;font-size:1rem;letter-spacing:-.02em;color:var(--tx);text-decoration:none;white-space:nowrap}
.mark{width:22px;height:22px;flex:none;display:block;image-rendering:pixelated}
.nav-toggle{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}
.nav-btn{display:none;margin-left:auto;background:transparent;color:var(--tx);border:1px solid var(--bd);border-radius:8px;padding:8px 14px;min-height:44px;font:inherit;cursor:pointer}
.nav-btn .m-close{display:none}
.nav-toggle:focus-visible + .nav-btn{outline:2px solid var(--ac);outline-offset:3px}
header nav{display:flex;gap:4px 18px;align-items:center;flex-wrap:nowrap;margin-left:auto}
header nav a{color:var(--mu);text-decoration:none;font-size:.875rem;min-height:60px;display:inline-flex;align-items:center}
header nav a.on{color:var(--tx);box-shadow:inset 0 -2px 0 var(--ac)}
header nav a:hover{color:var(--tx)}
a.btn{display:inline-flex;align-items:center;justify-content:center;background:linear-gradient(180deg,#ff9a52,#ff7a24);color:#140a02;text-decoration:none;border:0;border-radius:10px;padding:12px 18px;min-height:44px;font-weight:600;letter-spacing:-.01em;box-shadow:0 0 0 1px rgba(255,170,90,.5) inset,0 6px 20px -6px rgba(255,122,36,.55)}
a.btn:hover{color:#140a02;transform:translateY(-1px)}
a.btn.secondary{background:transparent;color:var(--tx);box-shadow:none;border:1px solid var(--bd-h)}
a.btn.secondary:hover{color:var(--ac);border-color:var(--ac);background:transparent}
header nav a.btn{color:#140a02;padding:8px 14px;min-height:36px;border-radius:8px}
header nav a.btn:hover{color:#140a02}
.hero{position:relative;overflow:hidden;padding:96px 0 64px;border-bottom:1px solid var(--bd)}
.hero:before{content:"";position:absolute;inset:0;background-image:linear-gradient(rgba(148,163,214,.06) 1px,transparent 1px),linear-gradient(90deg,rgba(148,163,214,.06) 1px,transparent 1px);background-size:32px 32px;mask-image:radial-gradient(60% 70% at 70% 40%,#000,transparent);pointer-events:none}
.orb{position:absolute;border-radius:50%;pointer-events:none}
.orb-a{width:560px;height:420px;right:-60px;top:-120px;background:radial-gradient(circle,rgba(255,138,61,.16),transparent 68%);animation:drift 16s ease-in-out infinite}
.hero-grid{position:relative;z-index:1;display:grid;grid-template-columns:1.2fr .8fr;gap:40px;align-items:center}
.eyebrow,.kicker,dl dt,.metric span{margin:0 0 12px;font-family:var(--mono);font-size:.75rem;font-weight:500;letter-spacing:.08em;text-transform:uppercase;color:var(--mu)}
h1{margin:0 0 14px;max-width:14ch;font-size:clamp(2.5rem,5.2vw,4.25rem);line-height:1.02;letter-spacing:-.045em;font-weight:650;color:var(--tx)}
h2{margin:0;font-size:clamp(1.5rem,2.4vw,2rem);letter-spacing:-.035em;font-weight:650;line-height:1.15}
h3{font-weight:650;letter-spacing:-.03em;line-height:1.15}
.lede{margin:0 0 22px;max-width:38rem;font-size:1.125rem;line-height:1.5;color:var(--mu)}
.hero .lede{opacity:1}
.actions{display:flex;gap:12px;align-items:center;flex-wrap:wrap;margin:0}
.sec-head > a,.actions a:not(.btn),.band-head a{min-height:44px;display:inline-flex;align-items:center}
.hero-art{position:relative;display:grid;place-items:center;padding:8px 0 12px}
.anvil-glow{position:absolute;left:50%;top:68%;width:min(88%,380px);height:180px;transform:translate(-50%,-50%);border-radius:50%;background:radial-gradient(circle,rgba(255,138,61,.42),rgba(255,138,61,0) 68%);pointer-events:none}
.anvil{position:relative;z-index:1;display:block;width:min(100%,420px);height:auto;image-rendering:pixelated;animation:floaty 7.5s ease-in-out infinite}
.spark{animation:spark 2.4s steps(4) infinite}
.sparks .spark:nth-child(2n){animation-delay:.6s}
.sparks .spark:nth-child(3n){animation-delay:1.2s}
.metrics{position:relative;z-index:1;display:grid;grid-template-columns:repeat(2,1fr);gap:0;margin-top:56px;border:1px solid var(--bd);border-radius:16px;background:rgba(11,17,36,.6);overflow:hidden}
.metric{display:flex;flex-direction:column;justify-content:center;gap:6px;min-height:0;padding:18px 22px;border:0;border-radius:0;background:transparent;color:inherit;text-decoration:none}
.metric + .metric{border-left:1px solid var(--bd)}
a.metric:hover{background:rgba(255,138,61,.06)}
.metric b{color:var(--tx);font-family:var(--mono);font-size:1.1rem;font-weight:500;letter-spacing:-.03em;line-height:1.2}
.metric{min-width:0}
.metric span{margin:0;line-height:1.35}
.rise{animation:rise .7s cubic-bezier(.16,.84,.32,1) both}
.d2{animation-delay:.06s}.d3{animation-delay:.12s}.d4{animation-delay:.18s}.d5{animation-delay:.24s}
.page{padding:56px 0 96px}
.pagehead{margin:0 0 28px;max-width:40rem}
.pagehead h1{margin:0 0 10px}
.band{padding:88px 0}
.band-alt{background:var(--bg2);box-shadow:inset 0 1px 0 var(--bd),inset 0 -1px 0 var(--bd)}
.band-head{display:flex;justify-content:space-between;align-items:center;gap:12px 20px;margin:0 0 28px}
.band-head a{font-size:.875rem;color:var(--mu);text-decoration:none}
.band-head a:hover{color:var(--ac)}
.band-head a::after{content:" →";color:var(--ac)}
.sec{margin:48px 0}
.sec-head{display:flex;justify-content:space-between;align-items:center;gap:16px 28px;flex-wrap:wrap;margin-bottom:18px}
.sec-head p,.intro{color:var(--mu);margin:8px 0 0;max-width:40rem}
.bento{display:grid;grid-template-columns:minmax(0,1.35fr) minmax(0,1fr);gap:12px;align-items:stretch}
.bento .featured{grid-row:span 3}
.pick,.catcard,.panel,.issue{background:linear-gradient(180deg,#0f1630,rgba(15,22,48,.6));border:1px solid var(--bd);border-radius:12px;box-shadow:0 1px 0 rgba(255,255,255,.04) inset,0 8px 24px -12px rgba(0,0,0,.6);padding:20px}
.pick,a.catcard{text-decoration:none;color:inherit;display:flex;flex-direction:column;gap:10px}
.pick,.catcard{transition:border-color .2s ease,background .2s ease,transform .2s ease}
.pick:hover,a.catcard:hover{border-color:var(--bd-h);background:#141c3b;transform:translateY(-2px)}
.pick h3{margin:0;color:var(--tx);font-size:1.05rem}
.pick h3 a{color:var(--tx);text-decoration:none}
.pick h3 a:hover{color:var(--ac)}
.pick p{margin:0;color:var(--mu);font-size:.95rem}
.featured{position:relative;overflow:hidden;padding:28px;gap:12px;justify-content:space-between}
.featured .more{align-self:flex-start;font-weight:600;color:var(--ac);text-decoration:none}
.featured .more:hover{color:var(--ac)}
.featured::before,#signup::before{content:"";position:absolute;inset:0;background:radial-gradient(500px 260px at 0 0,rgba(255,138,61,.12),transparent 60%);pointer-events:none}
.featured > *,#signup > *{position:relative;z-index:1}
.featured h3{font-size:1.75rem;letter-spacing:-.03em}
.featured .clamp{-webkit-line-clamp:5}
.clamp{display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.cats{display:grid;grid-template-columns:repeat(__CATN__,1fr);gap:12px}
.caticon{width:24px;height:24px;display:block;image-rendering:pixelated}
a.catcard{min-height:0;justify-content:space-between}
a.catcard strong{color:var(--tx);font-size:1rem;font-weight:600}
a.catcard .num{color:var(--ac2);font-family:var(--mono);font-size:2.25rem;font-weight:500;letter-spacing:-.04em;font-variant-numeric:tabular-nums;line-height:1}
.split{display:grid;grid-template-columns:1.15fr .85fr;gap:16px}
#signup{position:relative;overflow:hidden}
.panel h2,.panel h3{margin:0 0 8px}
.mu{color:var(--mu)}
input,select{background:var(--bg2);color:var(--tx);border:1px solid var(--bd);border-radius:10px;padding:12px 14px;min-height:48px;font:inherit}
input::placeholder{color:var(--mu);opacity:1}
input:hover,select:hover{border-color:var(--bd-h)}
.dirsearch{display:block;width:100%;font-size:1.15rem;padding:16px 18px;border-radius:12px;background:var(--card);margin:4px 0 0}
.dirsearch:focus{outline:2px solid var(--ac);border-color:var(--ac)}
.letters{display:flex;flex-wrap:wrap;gap:6px;margin:14px 0 16px}
.letters a{font-family:var(--mono);font-size:.85rem;color:var(--mu);text-decoration:none;min-width:36px;min-height:36px;display:inline-flex;align-items:center;justify-content:center;border-radius:8px;border:1px solid var(--bd)}
.letters a.on,.letters a:hover{color:var(--ink);background:var(--ac);border-color:var(--ac);text-decoration:none}
.dirbar{display:flex;flex-wrap:wrap;gap:12px 18px;align-items:center;justify-content:space-between;margin:0 0 16px}
.dirtools{display:flex;gap:12px;align-items:center;flex-wrap:wrap}
.dirtools #cnt{margin:0;font-family:var(--mono);font-size:.85rem}
.toggle{display:inline-flex;align-items:center;gap:8px;min-height:44px;cursor:pointer;color:var(--tx)}
.toggle input{width:18px;height:18px;min-height:18px;padding:0;accent-color:var(--ac)}
.chips{display:flex;gap:8px;flex-wrap:wrap}
.chip{background:transparent;border:1px solid var(--bd);color:var(--tx);border-radius:999px;padding:8px 14px;min-height:44px;cursor:pointer;font:inherit}
.chip:hover{border-color:var(--ac)}
.chip.on{background:#eef2ff;color:#070b1a;border-color:#eef2ff;font-weight:650}
.rows{display:flex;flex-direction:column;gap:6px}
.row{display:grid;grid-template-columns:minmax(10.5rem,.95fr) minmax(0,1.7fr) 15rem;gap:2px 18px;align-items:center;min-height:58px;padding:8px 14px;border:1px solid var(--bd);border-radius:12px;background:linear-gradient(180deg,#0f1630,rgba(15,22,48,.6));box-shadow:0 1px 0 rgba(255,255,255,.04) inset;transition:border-color .2s ease,background .2s ease}
.row:hover{border-color:var(--bd-h);background:#141c3b}
.row .name{margin:0;min-width:0;font-size:1rem;letter-spacing:-.02em;line-height:1.25;min-height:2.5em;display:flex;align-items:center;flex-wrap:wrap}
.row .name a{min-width:0;max-width:100%;color:var(--tx);text-decoration:none}
.row .name a:hover{color:var(--ac)}
.row .desc,.row .meta{margin:0;color:var(--mu);font-size:.92rem}
.row .desc{line-height:1.35;max-height:1.35em;overflow:hidden}
.row .meta{display:flex;flex-direction:column;align-items:flex-start;gap:1px}
.row .price{color:var(--tx);white-space:nowrap}
.row .badge-new{margin-left:8px;vertical-align:2px}
.badge-new{display:inline-block;font-weight:650;font-size:.7rem;padding:4px 8px;border-radius:999px;background:rgba(255,138,61,.12);color:var(--ac2);letter-spacing:.04em;text-transform:uppercase}
.cat,.checked,.price{font-size:.92rem;color:var(--mu)}
time,.num,.count,.metric b{font-family:var(--mono)}
.quiet{margin:22px 0 0;color:var(--mu)}
.issue{position:relative;margin:16px 0}
.issue h2{margin:0 0 6px;font-family:var(--mono);font-weight:500;color:var(--ac2);font-size:1.35rem}
.issue .when{margin:0;font-family:var(--mono);color:var(--mu)}
.issue{box-shadow:inset 0 1px 0 var(--ac),0 1px 0 rgba(255,255,255,.04) inset,0 8px 24px -12px rgba(0,0,0,.6)}
footer{border-top:1px solid var(--bd);padding:48px 0 64px;color:var(--mu);font-size:.85rem}
footer nav{display:flex;gap:4px 18px;flex-wrap:wrap}
footer nav a{color:var(--mu);text-decoration:none;min-height:44px;display:inline-flex;align-items:center}
footer nav a:hover{color:var(--ac)}
footer p{margin:8px 0 0;max-width:46rem}
footer .sources{margin-top:12px;max-width:40rem;line-height:1.5}
dl dt{margin-top:16px}dl dd{margin:4px 0 0}
.vrow{display:flex;flex-wrap:wrap;align-items:center;gap:8px 10px}
.back{margin:0 0 14px;color:var(--mu)}
.back a{color:var(--mu)}
.back a:hover{color:var(--ac)}
.tool-hero{display:grid;grid-template-columns:minmax(0,1fr) 320px;gap:48px;align-items:start}
.tool-hero h1{max-width:none;font-size:clamp(2.25rem,4vw,3.5rem);line-height:1.05}
.sum{margin:18px 0 0;max-width:40rem;font-size:1.25rem;line-height:1.5;color:var(--tx)}
.take{margin:32px 0 0;padding:22px 24px;border-radius:16px;border:1px solid var(--bd);background:linear-gradient(180deg,rgba(255,138,61,.07),rgba(15,22,48,.4));box-shadow:inset 0 1px 0 rgba(255,138,61,.35)}
.take h2{margin:0 0 8px;font-size:1.2rem;letter-spacing:-.02em}
.take p{margin:0;max-width:44rem;color:var(--tx);font-size:1.05rem;line-height:1.55}
.facts{position:sticky;top:84px;padding:20px;border-radius:16px;border:1px solid var(--bd);background:linear-gradient(180deg,#0f1630,rgba(15,22,48,.6));box-shadow:0 1px 0 rgba(255,255,255,.04) inset,0 8px 24px -12px rgba(0,0,0,.6)}
.facts dt:first-child{margin-top:0}
.facts .btn{width:100%;margin-top:18px}
@keyframes rise{from{transform:translateY(12px)}to{transform:none}}
@keyframes drift{0%,100%{transform:translate3d(0,0,0)}50%{transform:translate3d(0,18px,0) scale(1.04)}}
@keyframes floaty{0%,100%{transform:translateY(0)}50%{transform:translateY(-8px)}}
@keyframes spark{0%,100%{opacity:1}50%{opacity:.15}}
@media(max-width:1120px){
.nav-btn{display:inline-flex}
header nav{display:none;width:100%;flex-direction:column;align-items:stretch;gap:0;margin-left:0;padding:4px 0 14px}
.nav-toggle:checked ~ nav{display:flex}
.nav-toggle:checked + .nav-btn .m-open{display:none}
.nav-toggle:checked + .nav-btn .m-close{display:inline}
header nav a{min-height:48px}
header nav a.on{box-shadow:inset 2px 0 0 var(--ac)}
header nav a.btn{display:flex;margin-top:8px;text-align:center}
}
@media(max-width:980px){
.hero-grid,.split,.tool-hero{grid-template-columns:1fr}
.facts{position:static}
.hero-art{order:-1;justify-content:center;margin-bottom:8px}
.anvil{width:220px}
.anvil-glow{width:200px;height:120px}
.orb-a{width:280px;height:220px;right:-80px;top:-100px}
.cats{grid-template-columns:1fr 1fr}
.bento{grid-template-columns:1fr 1fr}
}
@media(max-width:640px){
.w{padding:0 18px}
.hero{padding:40px 0}
.metrics{margin-top:36px}
.metric{padding:14px}
.metric b{font-size:.9rem}
.metric span{font-size:.65rem}
.bento{grid-template-columns:1fr}
.row{grid-template-columns:1fr;gap:2px;min-height:0;padding:10px 12px}
.row .name{min-height:0}
.bento .featured{grid-row:auto}
.actions{flex-direction:column;align-items:stretch}
.hero .btn{width:100%}
.band{padding:56px 0}
.chips{flex-wrap:nowrap;overflow-x:auto}
.chip{flex:none}
}
@media(prefers-reduced-motion:reduce){
.rise,.orb,.anvil,.spark{animation:none}
.pick,a.catcard,.row,a.btn{transition:none}
.pick:hover,a.catcard:hover,.row:hover,a.btn:hover{transform:none}
}
"""
_MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")
def checked_iso(t):
    # Last review date. Missing verdict_checked falls back to date_added so new tools still build.
    return t.get("verdict_checked") or t["date_added"]
def fmt_date(iso):
    d = datetime.date.fromisoformat(iso)
    return f"{_MONTHS[d.month - 1]} {d.day}, {d.year}"
def cat_label(name):
    return CAT_LABEL.get(name, name)
def verdict_stamp(t):
    iso = checked_iso(t)
    return f'<span class="checked">Last checked <time datetime="{e(iso)}">{e(fmt_date(iso))}</time></span>'
def has_free_tier(t):
    # "No free plan" must not count. A word "free" in the pricing line does.
    pricing = t["pricing"]
    if re.search(r"\bno free\b", pricing, re.I):
        return False
    return bool(re.search(r"\bfree\b", pricing, re.I))
_PRICE_RE = re.compile(
    r"(?P<cur>[$€])\s*(?P<num>\d+(?:\.\d+)?)"
    r"(?:/\s*(?:user|seat|member))?"
    r"(?:/\s*(?P<unit>mo|month|yr|year)|\s+per\s+(?:[\w]+\s+){0,3}(?P<per>year|yr))?",
    re.I,
)
def price_line(t):
    # One short line for the directory. The tool page keeps the full pricing sentence.
    pricing = " ".join(t["pricing"].split())
    low = pricing.lower()
    if "pricing unverified" in low:
        return "Pricing unverified"
    if "signups stopped" in low or "stopped new signups" in low:
        return "Signups closed"
    if "shutting down" in low:
        when = re.search(r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},\s+\d{4}", pricing)
        return f"Shuts down {when.group(0)}" if when else "Shutting down"
    if re.search(r"free,\s*open source", low):
        return "Free, open source"
    free = has_free_tier(t)
    scope = pricing
    if re.search(r"new plans\s*:", pricing, re.I):
        scope = re.split(r"new plans\s*:\s*", pricing, flags=re.I, maxsplit=1)[-1]
    def pick(text):
        for match in _PRICE_RE.finditer(text):
            if match.group("num") in ("0", "0.0", "0.00"):
                continue
            unit = (match.group("unit") or match.group("per") or "").lower()
            suffix = "/mo" if unit in ("mo", "month") else "/yr" if unit in ("yr", "year") else ""
            num = match.group("num")
            if num.endswith(".00"):
                num = num[:-3]
            return f"{match.group('cur')}{num}{suffix}"
        return None
    outside = re.sub(r"\([^)]*\)", " ", scope)
    amount = pick(outside) or pick(scope)
    if amount and not re.search(r"/(?:mo|yr)$", amount) and re.search(r"\ba month\b", scope, re.I):
        amount += "/mo"
    if not amount:
        if free and re.search(r"\bpaid\b", low):
            return "Free tier"
        if free:
            return "Free"
        return "Paid only"
    if free:
        return f"Free tier, from {amount}"
    return f"From {amount}"
def letter_of(name):
    first = name[:1].upper()
    return first if first.isalpha() else "#"
NAV = [
    ("index.html", "Home", "home"),
    ("tools/", "Tool Directory", "tools"),
    ("this-week.html", "This Week", "week"),
    ("newsletter/", "Newsletter Archive", "news"),
    ("suggest/", "Suggest a Tool", "suggest"),
]
def section_of(path):
    if path in ("index.html", ""):
        return "home"
    if path.startswith("tools/"):
        return "tools"
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
            f'<p>{e(N)}. {e(VALUE)}</p>'
            f'<p class="sources">{e(SOURCE_NOTE)}</p>')
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
                "description": VALUE,
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
        f'<meta name="theme-color" content="#070b1a">'
        f'<meta name="color-scheme" content="dark">'
    )
    # .page only sets vertical padding. Nest it so it does not wipe the .w gutters.
    inner = body if bleed else f'<div class="w"><div class="page">{body}</div></div>'
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title><meta name="description" content="{e(desc)}">{metas}
<link rel="stylesheet" href="{p}style.css">{schema_graph(nodes)}</head><body>
<a class="skip" href="#content">Skip to content</a>
<header><div class="w"><div class="bar"><a class="logo" href="{p}index.html">{mark_svg()}{e(N)}</a>{nav_html(depth, path)}</div></div></header>
<main id="content">{inner}</main><footer><div class="w">{foot_html(depth)}</div></footer></body></html>"""
def badge_html(t):
    # Website cards only. Callers on the newsletter archive must not use this.
    return '<span class="badge-new">New this week</span>' if is_new(t) else ""
def row(t, prefix):
    # Every tool is in the HTML. Filters only hide rows; they do not inject them.
    letter = letter_of(t["name"])
    text = " ".join([t["name"], t["description"], t["pricing"], t["category"], *t["use_cases"]]).lower()
    badge = badge_html(t)
    free = "1" if has_free_tier(t) else "0"
    return (
        f'<article class="row" id="{e(t["slug"])}" data-cat="{e(t["category"])}" '
        f'data-date="{e(t["date_added"])}" data-name="{e(t["name"].lower())}" data-free="{free}" '
        f'data-letter="{e(letter)}" data-text="{e(text)}">'
        f'<h2 class="name"><a href="{prefix}{t["slug"]}.html">{e(t["name"])}</a>{badge}</h2>'
        f'<p class="desc" data-full="{e(t["description"])}">{e(t["description"])}</p>'
        f'<p class="meta"><span class="price">{e(price_line(t))}</span>'
        f'<span class="cat">{e(cat_label(t["category"]))}</span></p></article>'
    )
def pick_card(t, featured=False):
    href = f'tools/{t["slug"]}.html'
    if featured:
        return (f'<article class="pick featured">'
                f'<h3><a href="{href}">{e(t["name"])}</a></h3>'
                f'<p class="clamp">{e(t["description"])}</p>'
                f'<p class="meta"><span class="cat">{e(cat_label(t["category"]))}</span> · '
                f'<span class="price">{e(t["pricing"])}</span></p>'
                f'<a class="more" href="{href}">See the listing →</a></article>')
    return (f'<a class="pick" href="{href}">'
            f'<h3>{e(t["name"])}</h3>'
            f'<p class="clamp">{e(t["description"])}</p>'
            f'<span class="cat">{e(cat_label(t["category"]))}</span>'
            f'<span class="price">{e(t["pricing"])}</span></a>')
SIGNUP = f"""<div class="panel" id="signup"><p class="kicker">Free</p><h2>Get the Friday letter</h2><p class="mu">One email a week: the newest tools, with the facts.</p>
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
(OUT / "style.css").write_text(CSS.replace("__CATN__", str(len(categories))))
shutil.copyfile(R / "brand" / "og.jpg", OUT / "og.jpg")
shutil.copyfile(R / "CNAME", OUT / "CNAME")
def cat_href(name):
    return "tools/?cat=" + quote(name, safe="")
cat_cards = "".join(
    f'<a class="catcard" href="{cat_href(c)}">{cat_icon(c)}<span class="num">{counts[c]}</span><strong>{e(cat_label(c))}</strong></a>'
    for c in categories)
latest_issue = ISSUES[0]
checked_dates = sorted({checked_iso(t) for t in tools})
pick_html = "".join(pick_card(t, i == 0) for i, t in enumerate(picks))
latest = max(datetime.date.fromisoformat(t["date_added"]) for t in tools)
cut = latest - datetime.timedelta(days=7)
wk = [t for t in tools if datetime.date.fromisoformat(t["date_added"]) > cut]
launch_only = bool(wk) and all(t["date_added"] == LAUNCH.isoformat() for t in wk)
week_link = "See launch week" if launch_only else "See this week"
home = f"""<section class="hero"><div class="orb orb-a" aria-hidden="true"></div>
<div class="w hero-grid"><div class="hero-copy">
<h1 class="rise">{e(VALUE)}</h1>
<p class="actions rise d2"><a class="btn" href="{e(CONFIG['subscribe_url'])}">Subscribe free</a><a class="btn secondary" href="tools/">Browse the directory</a></p>
</div><div class="hero-art" aria-hidden="true"><div class="anvil-glow"></div>{anvil_svg()}</div></div>
<div class="w"><div class="metrics rise d3"><div class="metric"><b>{len(tools)}</b><span>Tools</span></div><div class="metric"><b><time datetime="{e(checked_dates[-1])}">{e(fmt_date(checked_dates[-1]))}</time></b><span>Last checked</span></div></div></div></section>
<section class="band" id="picks"><div class="w"><div class="band-head"><h2>This week's picks</h2><a href="this-week.html">{week_link}</a></div>
<div class="bento">{pick_html}</div></div></section>
<section class="band band-alt" id="categories"><div class="w"><div class="band-head"><h2>Browse by category</h2><a href="tools/">Full directory</a></div>
<div class="cats">{cat_cards}</div></div></section>
<section class="band" id="letter"><div class="w"><div class="split"><article class="panel"><p class="kicker">Newsletter</p><h2>{e(latest_issue['title'])}</h2><p>{e(latest_issue['when'])}</p><p class="mu">{e(latest_issue['note'])}</p><p><a href="newsletter/">Newsletter archive</a></p></article>{SIGNUP}</div></div></section>"""
(OUT / "index.html").write_text(page(
    f"{N} — the newest AI tools, sorted every Friday",
    VALUE,
    home, "index.html", nodes=[item_list("This week's picks", picks)], bleed=True))
cats = sorted(counts)
chips = '<button class="chip on" data-c="">All</button>' + "".join(
    f'<button class="chip" data-c="{e(c)}">{e(cat_label(c))}</button>' for c in cats)
first_slug = {}
for t in sorted(tools, key=lambda t: t["name"].lower()):
    first_slug.setdefault(letter_of(t["name"]), t["slug"])
letters = "".join(
    f'<a href="#{e(slug_id)}" data-l="{e(letter)}">{e(letter)}</a>'
    for letter, slug_id in first_slug.items())
JS = """<script>
const q=document.getElementById('q'),s=document.getElementById('sort'),g=document.getElementById('grid'),
free=document.getElementById('free'),empty=document.getElementById('empty'),cnt=document.getElementById('cnt');
const cs=[...document.querySelectorAll('.chip')],ls=[...document.querySelectorAll('.letters a')];
const rows=[...g.children];
let cat='',letter='';
function sync(){
  const u=new URL(location.href);
  const v=q.value.trim();
  if(v)u.searchParams.set('q',v);else u.searchParams.delete('q');
  if(cat)u.searchParams.set('cat',cat);else u.searchParams.delete('cat');
  if(s.value&&s.value!=='az')u.searchParams.set('sort',s.value);else u.searchParams.delete('sort');
  if(free.checked)u.searchParams.set('free','1');else u.searchParams.delete('free');
  if(letter)u.searchParams.set('letter',letter);else u.searchParams.delete('letter');
  history.replaceState(null,'',u);
}
function run(){
  const v=q.value.toLowerCase().trim();
  const o=[...rows].sort((a,b)=>{
    if(s.value==='az')return a.dataset.name.localeCompare(b.dataset.name);
    return b.dataset.date.localeCompare(a.dataset.date)||b.dataset.name.localeCompare(a.dataset.name);
  });
  let n=0;
  o.forEach(c=>{
    const ok=(!cat||c.dataset.cat===cat)&&(!v||c.dataset.text.includes(v))&&(!free.checked||c.dataset.free==='1')&&(!letter||c.dataset.letter===letter);
    c.hidden=!ok;if(ok)n++;g.appendChild(c);
  });
  cnt.textContent=n+(n===1?' tool':' tools');
  empty.hidden=n!==0;
  fitDesc();
}
function fitDesc(){
  document.querySelectorAll('.row .desc').forEach(el=>{
    if(el.closest('.row').hidden||el.clientWidth===0) return;
    const full=(el.dataset.full||el.textContent).trim();
    el.dataset.full=full;
    el.textContent=full;
    if(el.scrollHeight<=el.clientHeight+1) return;
    const words=full.split(/\\s+/);
    let lo=1, hi=words.length, best=words[0];
    while(lo<=hi){
      const mid=(lo+hi)>>1;
      el.textContent=words.slice(0,mid).join(' ')+'\u2026';
      if(el.scrollHeight<=el.clientHeight+1){best=el.textContent; lo=mid+1;}
      else hi=mid-1;
    }
    el.textContent=best;
  });
}
window.addEventListener('resize', fitDesc);
q.oninput=()=>{sync();run()};
s.onchange=()=>{sync();run()};
free.onchange=()=>{sync();run()};
cs.forEach(b=>b.onclick=()=>{cs.forEach(x=>x.classList.remove('on'));b.classList.add('on');cat=b.dataset.c;sync();run()});
ls.forEach(a=>a.addEventListener('click',ev=>{
  ev.preventDefault();
  letter=letter===a.dataset.l?'':a.dataset.l;
  ls.forEach(x=>x.classList.toggle('on',x.dataset.l===letter));
  sync();run();
}));
const params=new URLSearchParams(location.search);
const want=params.get('cat')||'';
const hit=cs.find(b=>b.dataset.c===want);
if(hit){cs.forEach(x=>x.classList.remove('on'));hit.classList.add('on');cat=want;}
const initialQ=params.get('q')||'';
if(initialQ)q.value=initialQ;
if(params.get('sort')==='newest')s.value='newest';
if(params.get('free')==='1')free.checked=true;
const L=(params.get('letter')||'').toUpperCase();
if(ls.some(a=>a.dataset.l===L)){letter=L;ls.forEach(x=>x.classList.toggle('on',x.dataset.l===letter));}
run();
</script>"""
directory = f"""<header class="pagehead"><h1>Tool directory</h1>
<p class="lede">{len(tools)} tools. Search by name, or narrow by category, letter, and free tier.</p></header>
<label class="sr" for="q">Search tools</label>
<input class="dirsearch" id="q" type="search" placeholder="Search by name, job, or price" autocomplete="off">
<nav class="letters" aria-label="Jump to letter">{letters}</nav>
<div class="dirbar">
<div class="chips" role="group" aria-label="Filter by category">{chips}</div>
<div class="dirtools">
<label class="toggle" for="free"><input id="free" type="checkbox"> Free tier</label>
<label class="sr" for="sort">Sort</label>
<select id="sort" aria-label="Sort"><option value="az" selected>A to Z</option><option value="newest">Newest</option></select>
<p class="mu" id="cnt">{len(tools)} tools</p>
</div></div>
<div class="rows" id="grid">{''.join(row(t, '') for t in sorted(tools, key=lambda t: t['name'].lower()))}</div>
<p class="quiet" id="empty" hidden>No tools match that search.</p>
{JS}"""
(OUT / "tools" / "index.html").write_text(page(
    f"Tool directory — {N}",
    f"Searchable directory of {len(tools)} AI tools for coding, vibe coding, automation, and games.",
    directory, "tools/", 1, nodes=[item_list("Tool directory", sorted(tools, key=lambda t: t["name"].lower()))]))
# Old verdicts URL. Noindex redirect, kept out of the sitemap.
(OUT / "verdicts" / "index.html").write_text(f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Tool directory — {e(N)}</title>
<meta name="robots" content="noindex">
<meta http-equiv="refresh" content="0; url=../tools/">
<link rel="canonical" href="{BASE}/tools/">
<meta name="description" content="The tool directory lists every tool.">
<link rel="stylesheet" href="../style.css"></head><body>
<main class="w" style="padding:48px 0"><h1>Tool directory</h1>
<p>This page has moved.</p>
<p><a href="../tools/">Go to the tool directory</a></p></main></body></html>""")
week_grid = f'<div class="rows">{"".join(row(t, "tools/") for t in wk)}</div>' if wk else "<p class='mu'>Nothing new in the last seven days.</p>"
if launch_only:
    week_name = "Launch week"
    week_kicker = "First batch"
    week_lede = f"The first batch of tools, added {fmt_date(LAUNCH.isoformat())}."
else:
    week_name = "This week"
    week_kicker = f"Added through {fmt_date(latest.isoformat())}"
    week_lede = f"{len(wk)} tools added in the 7 days up to {fmt_date(latest.isoformat())}."
(OUT / "this-week.html").write_text(page(
    f"{week_name} — {N}",
    week_lede,
    f'<header class="pagehead"><p class="kicker">{e(week_kicker)}</p><h1>{e(week_name)}</h1><p class="lede">{e(week_lede)}</p></header>{week_grid}<div class="sec">{SIGNUP}</div>',
    "this-week.html"))
def take_paragraph(t):
    # One plain paragraph: how to approach it, then the sourced detail.
    guide = GUIDE.get(t["verdict"], "").strip()
    reason = t["verdict_reason"].strip()
    parts = [p for p in (guide, reason) if p]
    return " ".join(parts)
for t in tools:
    b = f"""<div class="tool-hero"><div class="tool-copy"><p class="back"><a href="index.html">Tool directory</a> · {e(cat_label(t['category']))}</p><h1>{e(t['name'])}</h1><p class="vrow">{badge_html(t)}{verdict_stamp(t)}</p><p class="sum">{e(t['description'])}</p>
<script type="application/ld+json">{json.dumps({"@context":"https://schema.org","@type":"SoftwareApplication","name":t["name"],"url":t["url"],"applicationCategory":t["category"],"description":t["description"],"dateModified":checked_iso(t)})}</script></div>
<aside class="facts" aria-label="Facts"><dl><dt>Use cases</dt><dd><ul>{''.join(f'<li>{e(u)}</li>' for u in t['use_cases'])}</ul></dd><dt>Pricing</dt><dd>{e(t['pricing'])}</dd><dt>Website</dt><dd><a href="{e(t['url'])}" rel="noopener">{e(t['url'])}</a></dd>
<dt>Source</dt><dd><a href="{e(t['source'])}" rel="noopener">{e(t['source'])}</a></dd><dt>Added</dt><dd><time datetime="{e(t['date_added'])}">{e(fmt_date(t['date_added']))}</time></dd></dl>
<a class="btn" href="{e(t['url'])}" rel="nofollow noopener">Visit website</a></aside></div>
<section class="take" aria-labelledby="our-take"><h2 id="our-take">Our Take</h2><p>{e(take_paragraph(t))} <a href="{e(t['source'])}" rel="noopener">Source</a></p></section>"""
    (OUT / "tools" / f"{t['slug']}.html").write_text(page(
        f"{t['name']} — {N}",
        f"{t['name']}: {t['description']}"[:300],
        b, f"tools/{t['slug']}.html", 1))
issue_cards = "".join(
    f'<article class="issue"><h2>{e(i["title"])}</h2><p class="when">{e(i["when"])}</p><p class="mu">{e(i["note"])}</p></article>'
    for i in ISSUES)
(OUT / "newsletter" / "index.html").write_text(page(
    f"Newsletter Archive — {N}",
    "Archive of Toolsmith Weekly letters. Issue 1 arrives Oct 23, 2026.",
    f'<header class="pagehead"><p class="kicker">Letters</p><h1>Newsletter Archive</h1><p class="lede">The weekly letter. Upcoming letters are listed here, and a link is added only after the letter is sent.</p></header>{issue_cards}<div class="sec">{SIGNUP}</div>',
    "newsletter/", 1))
# Alias paths. Meta refresh plus a plain link. Kept out of the sitemap.
def alias_page(folder):
    (OUT / folder).mkdir(parents=True, exist_ok=True)
    (OUT / folder / "index.html").write_text(f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Newsletter Archive — {e(N)}</title>
<meta name="robots" content="noindex">
<meta http-equiv="refresh" content="0; url=../newsletter/">
<link rel="canonical" href="{BASE}/newsletter/">
<meta name="description" content="The newsletter archive has moved.">
<link rel="stylesheet" href="../style.css"></head><body>
<main class="w" style="padding:48px 0"><h1>Newsletter Archive</h1>
<p>This page has moved.</p>
<p><a href="../newsletter/">Go to the newsletter archive</a></p></main></body></html>""")
for alias in ("issues", "archive", "newsletters"):
    alias_page(alias)
suggest_body = f"""<header class="pagehead"><p class="kicker">For builders</p><h1>Suggest a tool</h1><p class="lede">Indie developers: send a tool you built, or one you want listed.</p></header>
<p><a class="btn" href="{e(suggest_href)}">Suggest a tool by email</a></p>
<p class="mu">Opens your mail app to {e(CONFIG['suggest_email'])} with the subject filled in. No account and no third-party form.</p><div class="sec">{SIGNUP}</div>"""
(OUT / "suggest" / "index.html").write_text(page(
    f"Suggest a tool — {N}",
    "Indie developers can email a tool suggestion to Toolsmith Weekly.",
    suggest_body, "suggest/", 1))
urls = ["index.html", "tools/", "this-week.html", "newsletter/", "suggest/"] + [f"tools/{t['slug']}.html" for t in tools]
(OUT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + "".join(f"<url><loc>{BASE}/{u}</loc></url>" for u in urls) + "</urlset>")
(OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {BASE}/sitemap.xml\n")
new_count = sum(is_new(t) for t in tools)
llms = [
    f"# {N}",
    "",
    f"> {VALUE}",
    "",
    f"{N} lists new AI tools for coding, vibe coding, automation, and games. {SOURCE_NOTE} The directory currently lists {len(tools)} tools. Tools added after 2026-10-20 and within the last 7 days are marked New this week on the website only. That badge is not used in the newsletter. The first batch is labeled Launch week.",
    "",
    "## Pages",
    "",
    f"- [Home]({BASE}/): Landing page with this week's picks, categories, and the latest letter.",
    f"- [Tool directory]({BASE}/tools/): Search, filter by category, free tier, and letter, and sort the full list. A to Z is the default sort. Newest is available from the sort control and from ?sort=newest. Category links use a ?cat= query. A text search uses ?q=.",
    f"- [This week]({BASE}/this-week.html): Tools added in the seven days up to the newest date in the directory.",
    f"- [Newsletter archive]({BASE}/newsletter/): The weekly letter. Issue 1 is coming Oct 23, 2026. /issues/, /archive/, and /newsletters/ redirect here.",
    f"- [Suggest a tool]({BASE}/suggest/): Indie developers can email {CONFIG['suggest_email']} with a tool suggestion.",
    f"- [Subscribe]({CONFIG['subscribe_url']}): Free weekly letter on beehiiv.",
    "",
    "## Tools",
    "",
]
for t in tools:
    mark = " New this week." if is_new(t) else ""
    llms.append(f"- [{t['name']}]({BASE}/tools/{t['slug']}.html): {t['description']}{mark}")
(OUT / "llms.txt").write_text("\n".join(llms) + "\n")
print(f"Built {len(tools)} tool pages into {OUT} ({new_count} new this week as of {TODAY})")

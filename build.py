#!/usr/bin/env python3
"""Build static site from tools.json into dist/. Usage: python3 build.py"""
import json, html, math, re, shutil, datetime, pathlib
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
# A letter with published false stays in the repo (path + body) but is not built.
# The archive and homepage show the title and the coming date only: no note,
# no page, and no link. Flip published to true to write the page, add it to
# the sitemap, and turn the note and the links back on.
def issue_is_live(issue):
    return bool(issue.get("published")) and bool(issue.get("path")) and bool(issue.get("body"))
def issue_when(issue):
    if issue_is_live(issue):
        return issue["when"]
    return issue.get("coming") or issue["when"]
ISSUES = [
    {
        "id": "1",
        "title": "Issue #1",
        "headline": "Patch PHP. Check LiteLLM. Then Fix Your TV.",
        "when": "Friday, Oct 23, 2026",
        "coming": "Coming Oct 23, 2026",
        "note": "AI found a decade-old hole in PHP, LiteLLM shipped a poisoned release, and people are using coding agents to strip the ads off their TVs.",
        "path": "newsletter/1/",
        "date": "2026-10-23",
        "body": "content/issue-1.html",
        "published": False,
    },
]
# Reader-facing names for the categories stored in tools.json. Unknown categories
# fall through to the raw name so a new one still appears in the grid and the filters.
CAT_LABEL = {
    "coding agents": "Coding Agents",
    "vibe-coding app builders": "Vibe Coding",
    "AI agents/automation": "Automation",
    "gaming/game dev": "Gaming",
    "Security": "Security",
}
CAT_ORDER = list(CAT_LABEL)
# Neutral first sentence of Our Take. Not shown as a label.
# "wait" has no stock sentence. That line was unverified boilerplate.
GUIDE = {
    "use": "Worth using now for the job it claims.",
    "try": "Worth a short trial before you rely on it.",
    "wait": "",
    "skip": "Closed, shutting down, or a poor fit.",
}
_TAKE_BOILERPLATE = "Price, access, or the evidence is not settled."
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
    "Security": (
        "............",
        "...######...",
        "..########..",
        ".##########.",
        ".###....###.",
        ".###.##.###.",
        ".###.##.###.",
        "..########..",
        "...######...",
        "....####....",
        ".....##.....",
        "............",
    ),
}
def cat_icon(name):
    rows = CAT_ICON.get(name, CAT_ICON["coding agents"])
    return ('<svg class="caticon" viewBox="0 0 12 12" aria-hidden="true" focusable="false" '
            f'shape-rendering="crispEdges">{pix(rows)}</svg>')
def star_grid():
    # Regular five-point star on a 32×32 grid. Ten vertices of one pentagram:
    # outer radius R, inner radius cos(72°)/cos(36°) ≈ 0.382R, top point up.
    # Coverage-sampled, then mirrored so the left and right points match.
    n = 32
    cx = cy = (n - 1) / 2
    R = 14.8
    inner = math.cos(math.radians(72)) / math.cos(math.radians(36))
    pts = []
    for i in range(5):
        ang = math.radians(-90 + i * 72)
        pts.append((cx + R * math.cos(ang), cy + R * math.sin(ang)))
        iang = ang + math.radians(36)
        pts.append((cx + R * inner * math.cos(iang), cy + R * inner * math.sin(iang)))
    def inside(x, y):
        c = False
        j = len(pts) - 1
        for i, (xi, yi) in enumerate(pts):
            xj, yj = pts[j]
            if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / ((yj - yi) or 1e-12) + xi):
                c = not c
            j = i
        return c
    samples = 8
    offs = [(i + 0.5) / samples for i in range(samples)]
    need = samples * samples * 0.5
    mask = [[False] * n for _ in range(n)]
    for y in range(n):
        for x in range(n):
            hits = sum(1 for oy in offs for ox in offs if inside(x + ox, y + oy))
            mask[y][x] = hits >= need
    for y in range(n):
        for x in range(n // 2):
            mask[y][n - 1 - x] = mask[y][x]
    grid = [["."] * n for _ in range(n)]
    for y in range(n):
        for x in range(n):
            if not mask[y][x]:
                continue
            edge = any(
                not (0 <= x + dx < n and 0 <= y + dy < n and mask[y + dy][x + dx])
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
            )
            grid[y][x] = "o" if edge else "#"
    return ["".join(row) for row in grid]
def star_rects(rows):
    fills = {"o": "#B37800", "#": "#F5B301"}
    parts = []
    for y, row in enumerate(rows):
        x = 0
        while x < len(row):
            fill = fills.get(row[x])
            if not fill:
                x += 1
                continue
            x2 = x + 1
            while x2 < len(row) and row[x2] == row[x]:
                x2 += 1
            parts.append(f'<rect x="{x}" y="{y}" width="{x2 - x}" height="1" fill="{fill}"/>')
            x = x2
    return "".join(parts)
def star_svg():
    rows = star_grid()
    return ('<svg class="star-mark" viewBox="0 0 32 32" aria-hidden="true" focusable="false" '
            f'shape-rendering="crispEdges">{star_rects(rows)}</svg>')
CSS = """:root{--bg:#070b1a;--bg2:#0b1124;--card:#0f1630;--card-h:#141c3b;--bd:rgba(148,163,214,.14);--bd-h:rgba(148,163,214,.32);--tx:#eef2ff;--mu:#9aa6c7;--ac:#ff8a3d;--ac2:#ffc94a;--ink:#140a02;--sans:ui-sans-serif,system-ui,-apple-system,"Segoe UI",Helvetica,Arial,sans-serif;--mono:ui-monospace,"JetBrains Mono",Menlo,monospace}
*{box-sizing:border-box}[hidden]{display:none!important}
html{color-scheme:dark;scroll-behavior:smooth}
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
.band-stars{position:relative;background:radial-gradient(880px 380px at 0 0,rgba(255,138,61,.18),transparent 58%),linear-gradient(180deg,#121c3f,#0c1430);box-shadow:inset 0 1px 0 rgba(255,138,61,.55),inset 0 -1px 0 var(--bd)}
.band-stars .band-head{flex-wrap:wrap;row-gap:8px}
.band-stars h2{font-size:clamp(1.85rem,3.2vw,2.75rem)}
.star-mark{display:inline-block;width:32px;height:32px;margin-right:10px;vertical-align:-0.08em;image-rendering:pixelated;flex:none}
.sec{margin:48px 0}
.sec-head{display:flex;justify-content:space-between;align-items:center;gap:16px 28px;flex-wrap:wrap;margin-bottom:18px}
.sec-head p,.intro{color:var(--mu);margin:8px 0 0;max-width:40rem}
.bento{display:grid;grid-template-columns:minmax(0,1.35fr) minmax(0,1fr);gap:12px;align-items:stretch}
.pick,.catcard,.panel,.issue{background:linear-gradient(180deg,#0f1630,rgba(15,22,48,.6));border:1px solid var(--bd);border-radius:12px;box-shadow:0 1px 0 rgba(255,255,255,.04) inset,0 8px 24px -12px rgba(0,0,0,.6);padding:20px}
.pick,a.catcard{text-decoration:none;color:inherit;display:flex;flex-direction:column;gap:10px}
.pick,.catcard{transition:border-color .2s ease,background .2s ease,transform .2s ease}
.pick:hover,a.catcard:hover{border-color:var(--bd-h);background:#141c3b;transform:translateY(-2px)}
.band-stars .pick{border-color:#ff8a3d;box-shadow:0 0 0 1px rgba(255,138,61,.35),0 0 22px -4px rgba(255,138,61,.55),0 14px 28px -14px rgba(0,0,0,.75),inset 0 1px 0 rgba(255,255,255,.05)}
.band-stars .pick:hover{border-color:#ffb07a;background:#141c3b;transform:translateY(-4px);box-shadow:0 0 0 1px rgba(255,138,61,.45),0 0 32px -4px rgba(255,138,61,.7),0 18px 34px -14px rgba(0,0,0,.8),inset 0 1px 0 rgba(255,255,255,.06)}
.pick h3{margin:0;color:var(--tx);font-size:1.05rem;font-weight:650}
.pick h3 a{color:var(--tx);text-decoration:none}
.pick h3 a:hover{color:var(--ac)}
.pick p{margin:0;color:var(--mu);font-size:.95rem}
.featured{position:relative;overflow:hidden;padding:28px;gap:12px;justify-content:flex-start}
.featured .more{align-self:flex-start;font-weight:600;color:var(--ac);text-decoration:none}
.featured .more:hover{color:var(--ac)}
.featured::before,#signup::before{content:"";position:absolute;inset:0;background:radial-gradient(500px 260px at 0 0,rgba(255,138,61,.12),transparent 60%);pointer-events:none}
.featured > *,#signup > *{position:relative;z-index:1}
.featured h3{font-size:1.75rem;letter-spacing:-.03em}
.featured .clamp{-webkit-line-clamp:5}
.clamp{display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.pick .reason{margin:6px 0 10px;font-size:.95rem;line-height:1.35;font-weight:600;letter-spacing:-.01em;color:var(--tx);text-wrap:balance;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;padding-left:10px;box-shadow:inset 2px 0 0 var(--ac)}
.pick .reason + p{color:var(--mu);font-size:.875rem}
.pick .pick-src{margin:0;font-family:var(--mono);font-size:.75rem;letter-spacing:.03em}
.pick .pick-src a{color:var(--mu);text-decoration:none}
.pick .pick-src a:hover{color:var(--ac)}
.bento .featured .reason{font-size:clamp(1.15rem,1.6vw,1.35rem);line-height:1.3;letter-spacing:-.02em;margin:10px 0 14px;padding-left:12px;-webkit-line-clamp:3;color:#fff}
.cats{display:grid;grid-template-columns:repeat(__CATN__,1fr);gap:12px}
.caticon{width:24px;height:24px;display:block;image-rendering:pixelated}
a.catcard{min-height:0;justify-content:space-between}
a.catcard strong{color:var(--tx);font-size:1rem;font-weight:600}
a.catcard .num{color:var(--ac2);font-family:var(--mono);font-size:2.25rem;font-weight:500;letter-spacing:-.04em;font-variant-numeric:tabular-nums;line-height:1}
.split{display:grid;grid-template-columns:1.15fr .85fr;gap:16px}
#signup{position:relative;overflow:hidden}
#signup h2{font-size:clamp(1.35rem,2vw,1.7rem);line-height:1.2}
#signup .sub{margin:0;color:var(--tx);line-height:1.5}
#signup .points{margin:14px 0 18px;padding:0;list-style:none}
#signup .points li{position:relative;margin:0 0 10px;padding-left:16px;line-height:1.45}
#signup .points li:last-child{margin-bottom:0}
#signup .points li:before{content:"";position:absolute;left:0;top:.55em;width:6px;height:6px;border-radius:50%;background:var(--ac)}
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
.dirtools #cnt{margin:0;font-family:var(--mono);font-size:.85rem;white-space:nowrap}
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
.mbadge{display:inline-flex;align-items:center;gap:5px;margin-left:8px;padding:3px 7px 3px 4px;border:1px solid;border-radius:2px;background:#0b1124;font-family:var(--mono);font-size:.72rem;font-weight:650;letter-spacing:.02em;line-height:1.2;white-space:nowrap}
.mbadge .phone{width:12px;height:18px;flex:none;display:block;image-rendering:pixelated}
.mbadge.m-full{color:#ffc94a;border-color:#ffc94a}
.mbadge.m-partial{color:#ff9a52;border-color:#ff8a3d}
.mbadge.m-none{color:#eef2ff;border-color:#8d98c4}
.mbadge.m-unverified{color:#d7deef;border-color:#9aa6c7;border-style:dashed}
.mobile-fact{margin:0 0 4px;padding-bottom:14px;border-bottom:1px solid var(--bd)}
.facts .mobile-fact + dl{margin-top:14px}
.mobile-line{margin:0;font-size:.95rem;line-height:1.45}
.mobile-k{font-weight:650}
.mobile-k.m-full{color:#ffc94a}
.mobile-k.m-partial{color:#ff9a52}
.mobile-k.m-none{color:#eef2ff}
.mobile-k.m-unverified{color:#d7deef}
.mobile-note{color:var(--mu)}
.mobile-src{font-family:var(--mono);font-size:.75rem;letter-spacing:.03em;white-space:nowrap}
.mobile-desc{margin:8px 0 0;color:#d6dcf0;font-size:.95rem;line-height:1.5}
.cat,.checked,.price{font-size:.92rem;color:var(--mu)}
time,.num,.count,.metric b{font-family:var(--mono)}
.quiet{margin:22px 0 0;color:var(--mu)}
.issue{position:relative;margin:16px 0}
.issue h2{margin:0 0 6px;font-family:var(--mono);font-weight:500;color:var(--ac2);font-size:1.35rem}
.issue h2 a{color:inherit;text-decoration:none}
.issue h2 a:hover{color:var(--ac)}
.issue .headline{margin:0 0 8px;color:var(--tx);font-size:1.05rem;font-weight:650;letter-spacing:-.02em}
.issue .when{margin:0;font-family:var(--mono);color:var(--mu)}
.issue{box-shadow:inset 0 1px 0 var(--ac),0 1px 0 rgba(255,255,255,.04) inset,0 8px 24px -12px rgba(0,0,0,.6)}
.letter{max-width:68ch}
.letter h1{max-width:none}
.letter h2{margin:36px 0 12px;max-width:none}
.letter h3{margin:22px 0 8px;font-size:1.15rem}
.letter p,.letter li{font-size:1.0625rem;line-height:1.7;color:#d6dcf0}
.letter li{margin:0 0 10px}
.letter ul,.letter ol{margin:0 0 16px;padding-left:1.25rem}
.letter li::marker{color:var(--ac)}
.letter code{font-family:var(--mono);font-size:.92em}
.letter .meta{margin:0 0 18px;font-family:var(--mono);color:var(--mu)}
.letter-banner{display:block;width:min(100%,720px);height:auto;margin:0 0 24px;background:#000;image-rendering:pixelated}
.dirlist{margin:0;padding-left:1.25rem}
.dirlist li{margin:0 0 8px}
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
.tool-copy{grid-column:1;grid-row:1;min-width:0}
.facts{grid-column:2;grid-row:1 / span 2;min-width:0}
.overview{grid-column:1;grid-row:2;min-width:0}
.tool-hero h1{max-width:none;font-size:clamp(2.25rem,4vw,3.5rem);line-height:1.05}
.sum{margin:18px 0 0;max-width:40rem;font-size:1.25rem;line-height:1.5;color:var(--tx)}
.overview{max-width:68ch;margin-top:8px}
.overview h2{margin:0 0 16px;max-width:none;font-size:clamp(1.6rem,2.4vw,2rem);line-height:1.15;letter-spacing:-.03em;font-weight:650;color:var(--tx)}
.overview .toc{display:flex;flex-wrap:wrap;gap:8px 16px;margin:0}
.overview .toc a{font-size:.95rem;text-decoration:none}
.overview section,.overview .whatsnew{scroll-margin-top:84px;margin:36px 0 0}
.overview h3{display:flex;align-items:center;gap:10px;margin:0 0 12px;font-size:1.15rem;font-weight:650;letter-spacing:-.02em;color:var(--tx)}
.overview h3::before{content:"";width:8px;height:8px;flex:none;background:var(--ac)}
.overview p,.overview li{font-size:1.0625rem;line-height:1.7;color:#d6dcf0}
.overview p{margin:0 0 14px}
.overview li{margin:0 0 8px}
.overview ul,.overview ol{margin:0;padding-left:1.25rem}
.overview li::marker{color:var(--ac)}
.whatsnew{padding:16px 18px 16px 16px;border:1px solid var(--ac);border-radius:12px;box-shadow:inset 3px 0 0 var(--ac);background:rgba(255,138,61,.06)}
.whatsnew .label{margin:0 0 8px;font-family:var(--mono);font-size:.75rem;font-weight:500;letter-spacing:.08em;text-transform:uppercase;color:var(--ac2)}
.whatsnew .src{margin:12px 0 0}
.overview .disclosure{margin:28px 0 0}
.overview .disclosure em{font-style:italic}
.overview code{font-family:var(--mono);font-size:.92em}
.tbl{overflow-x:auto;max-width:100%;width:100%}
.tbl table{width:100%;border-collapse:collapse;min-width:28rem}
.tbl caption{caption-side:top;text-align:left;margin:0 0 8px;padding:0;font-weight:650;color:var(--tx)}
.tbl th,.tbl td{text-align:left;padding:10px 12px;border-bottom:1px solid var(--bd);vertical-align:top;font-size:1.0625rem;line-height:1.5;color:#d6dcf0}
.tbl th{color:var(--tx);font-weight:650;font-size:.85rem}
hr.rule{border:0;border-top:1px solid var(--bd);margin:0}
.take{margin:32px 0 0;padding:22px 24px;border-radius:16px;border:1px solid var(--bd);background:linear-gradient(180deg,rgba(255,138,61,.07),rgba(15,22,48,.4));box-shadow:inset 0 1px 0 rgba(255,138,61,.35)}
.rule + .take{margin-top:56px}
.take h2{margin:0 0 8px;font-size:1.2rem;letter-spacing:-.02em}
.take p{margin:0;max-width:44rem;color:var(--tx);font-size:1.05rem;line-height:1.55}
.facts{position:sticky;top:84px;padding:20px;border-radius:16px;border:1px solid var(--bd);background:linear-gradient(180deg,#0f1630,rgba(15,22,48,.6));box-shadow:0 1px 0 rgba(255,255,255,.04) inset,0 8px 24px -12px rgba(0,0,0,.6)}
.facts dt:first-child{margin-top:0}
.facts a,.overview a,.overview code{overflow-wrap:anywhere}
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
.tool-copy,.facts,.overview{grid-column:1;grid-row:auto}
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
.pick .reason{font-size:.95rem;-webkit-line-clamp:3;margin:4px 0 8px}
.bento .featured .reason{font-size:1.1rem;-webkit-line-clamp:3}
.actions{flex-direction:column;align-items:stretch}
.hero .btn{width:100%}
.band{padding:56px 0}
.chips{flex-wrap:nowrap;overflow-x:auto}
.chip{flex:none}
.overview p,.overview li{font-size:1rem;line-height:1.65}
.overview section,.overview .whatsnew{margin-top:22px}
.overview h2{margin-bottom:10px}
.rule + .take{margin-top:32px}
.tbl th,.tbl td{font-size:1rem}
}
@media(prefers-reduced-motion:reduce){
html{scroll-behavior:auto}
.rise,.orb,.anvil,.spark{animation:none}
.pick,a.catcard,.row,a.btn{transition:none}
.pick:hover,a.catcard:hover,.row:hover,a.btn:hover,.band-stars .pick:hover{transform:none}
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
    if re.search(r"free,\s*open source", low) or re.search(r"free and open source", low):
        return "Free, open source"
    free = has_free_tier(t)
    scope = pricing
    if re.search(r"new plans\s*:", pricing, re.I):
        scope = re.split(r"new plans\s*:\s*", pricing, flags=re.I, maxsplit=1)[-1]
    def pick(text):
        for match in _PRICE_RE.finditer(text):
            if match.group("num") in ("0", "0.0", "0.00"):
                continue
            # A trial credit grant is not the plan price.
            if text[match.end():].lstrip().lower().startswith("credit"):
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
PHONE_ROWS = (
    "####",
    "#..#",
    "#..#",
    "#..#",
    "#..#",
    ".##.",
)
def phone_svg():
    # Pixel handset for the directory badge. currentColor matches the badge text.
    return ('<svg class="phone" viewBox="0 0 4 6" aria-hidden="true" focusable="false" '
            f'shape-rendering="crispEdges">{pix(PHONE_ROWS, "currentColor")}</svg>')
MOBILE_LABEL = {
    "full": "Fully supported",
    "partial": "Partial",
    "none": "Not supported",
    "unverified": "not confirmed",
}
MOBILE_BADGE = {
    "full": "Full",
    "partial": "Partial",
    "none": "None",
    "unverified": "Not confirmed",
}
def mobile_status(t):
    status = t.get("mobile")
    if status not in MOBILE_LABEL:
        raise SystemExit(f"{t['name']} has mobile {status!r}; expected full, partial, none, or unverified")
    for key in ("mobile_note", "mobile_source", "mobile_description"):
        if not str(t.get(key) or "").strip():
            raise SystemExit(f"{t['name']} is missing {key}")
    return status
def mobile_badge(t):
    # Directory rows. Full, Partial, None, or Not confirmed.
    status = mobile_status(t)
    return (f'<span class="mbadge m-{status}">'
            f'{phone_svg()}<span class="sr">Mobile: </span>{e(MOBILE_BADGE[status])}</span>')
def mobile_fact(t):
    # Tool page. The note and source stay off when mobile support is not confirmed.
    status = mobile_status(t)
    line = f'<span class="mobile-k m-{status}">Mobile: {e(MOBILE_LABEL[status])}</span>'
    if status != "unverified":
        line += (f' <span class="mobile-note">{e(t["mobile_note"])}</span>'
                 f' <a class="mobile-src" href="{e(t["mobile_source"])}" rel="noopener">source</a>')
    return (f'<div class="mobile-fact"><p class="mobile-line">{line}</p>'
            f'<p class="mobile-desc">{e(t["mobile_description"])}</p></div>')
def issue_for(t):
    # Tool pages link a letter only while that issue is published.
    cid = str(t.get("covered_in") or "")
    if not cid:
        return None
    match = next((issue for issue in ISSUES if issue.get("id") == cid), None)
    if match is None:
        raise SystemExit(f"{t['name']} covered_in {cid!r} does not match an issue")
    if not issue_is_live(match):
        return None
    return match
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
        f'<h2 class="name"><a href="{prefix}{t["slug"]}.html">{e(t["name"])}</a>{badge}{mobile_badge(t)}</h2>'
        f'<p class="desc" data-full="{e(t["description"])}">{e(t["description"])}</p>'
        f'<p class="meta"><span class="price">{e(price_line(t))}</span>'
        f'<span class="cat">{e(cat_label(t["category"]))}</span></p></article>'
    )
def pick_reason_html(t):
    # Headline under the name. Omit the element when there is no reason.
    reason = str(t.get("pick_reason") or "").strip()
    if not reason:
        return ""
    return f'<p class="reason">{e(reason)}</p>'
def pick_source_html(t):
    src = str(t.get("pick_source") or "").strip()
    if not src:
        return ""
    return f'<p class="pick-src"><a href="{e(src)}" rel="noopener">Source</a></p>'
def pick_card(t, featured=False):
    href = f'tools/{t["slug"]}.html'
    why = pick_reason_html(t)
    src = pick_source_html(t)
    badge = badge_html(t)
    if featured:
        return (f'<article class="pick featured">'
                f'<h3><a href="{href}">{e(t["name"])}</a></h3>'
                f'{badge}{why}{src}'
                f'<p class="clamp">{e(t["description"])}</p>'
                f'<p class="meta"><span class="cat">{e(cat_label(t["category"]))}</span> · '
                f'<span class="price">{e(price_line(t))}</span></p>'
                f'<a class="more" href="{href}">See the listing →</a></article>')
    return (f'<article class="pick">'
            f'<h3><a href="{href}">{e(t["name"])}</a></h3>'
            f'{badge}{why}{src}'
            f'<p class="clamp">{e(t["description"])}</p>'
            f'<span class="cat">{e(cat_label(t["category"]))}</span>'
            f'<span class="price">{e(price_line(t))}</span></article>')
def weekly_picks(items):
    # Optional pick_rank. A ranked pick with a blank reason stops the build.
    picks = [t for t in items if t.get("pick_rank") is not None]
    if not picks:
        raise SystemExit("No homepage picks: set pick_rank on the tools for this week")
    seen = {}
    for t in picks:
        rank = t.get("pick_rank")
        if isinstance(rank, bool) or not isinstance(rank, int):
            raise SystemExit(f"{t['name']} has pick_rank {rank!r}, which is not an integer")
        if rank in seen:
            raise SystemExit(f"{t['name']} and {seen[rank]} both have pick_rank {rank}")
        seen[rank] = t["name"]
        if not str(t.get("pick_reason") or "").strip():
            raise SystemExit(f"{t['name']} has pick_rank but no pick_reason")
        if not str(t.get("pick_source") or "").strip():
            raise SystemExit(f"{t['name']} has pick_rank but no pick_source")
    picks.sort(key=lambda t: (t["pick_rank"], t["name"].lower()))
    return picks
SIGNUP = f"""<div class="panel" id="signup"><p class="kicker">Get the Weekly Roundup</p><h2>{e("The week's new AI tools, every Friday")}</h2>
<p class="sub">{e("One short, free email with the newest AI tool drops, from big launches to indie projects. Each one comes with a plain-English summary, what it costs, and a direct link.")}</p>
<ul class="points"><li>{e("Catch new AI tools the week they ship, including small indie projects")}</li>
<li>{e("Get what each tool does and what it costs, explained in plain language")}</li>
<li>{e("Go straight to each tool with a direct link, or browse the full directory at ")}<a href="{e(BASE)}/tools/">toolsmithweekly.com</a></li></ul>
<p><a class="btn" href="{e(CONFIG['subscribe_url'])}">Subscribe free</a></p></div>"""
picks = weekly_picks(tools)
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
shutil.copyfile(R / "brand" / "header-anvil.jpg", OUT / "header-anvil.jpg")
shutil.copyfile(R / "logo.png", OUT / "logo.png")
shutil.copyfile(R / "CNAME", OUT / "CNAME")
def letter_panel(issue):
    # Homepage teaser. A published letter links to its page and shows its note.
    # An unpublished letter is the title and the coming date, with no note and no issue link.
    live = issue_is_live(issue)
    title = (issue.get("headline") or issue["title"]) if live else issue["title"]
    bits = [f'<p class="kicker">Newsletter</p><h2>{e(title)}</h2>',
            f'<p>{e(issue_when(issue))}</p>']
    if live:
        bits.append(f'<p class="mu">{e(issue["note"])}</p>')
        bits.append(f'<p><a href="{e(issue["path"])}">Read {e(issue["title"])}</a></p>')
    bits.append('<p><a href="newsletter/">Newsletter archive</a></p>')
    return f'<article class="panel">{"".join(bits)}</article>'
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
<section class="band band-stars" id="picks"><div class="w"><div class="band-head"><h2>{star_svg()}This Week's Stars</h2><a href="this-week.html">{week_link}</a></div>
<div class="bento">{pick_html}</div></div></section>
<section class="band band-alt" id="categories"><div class="w"><div class="band-head"><h2>Browse by category</h2><a href="tools/">Full directory</a></div>
<div class="cats">{cat_cards}</div></div></section>
<section class="band" id="letter"><div class="w"><div class="split">{letter_panel(latest_issue)}{SIGNUP}</div></div></section>"""
(OUT / "index.html").write_text(page(
    f"{N} — the newest AI tools, sorted every Friday",
    VALUE,
    home, "index.html", nodes=[item_list("This Week's Stars", picks)], bleed=True))
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
  cnt.textContent='Showing '+n+(n===1?' tool':' tools');
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
<p class="lede">Search by name, or narrow by category, letter, and free tier.</p></header>
<label class="sr" for="q">Search tools</label>
<input class="dirsearch" id="q" type="search" placeholder="Search by name, job, or price" autocomplete="off">
<nav class="letters" aria-label="Jump to letter">{letters}</nav>
<div class="dirbar">
<div class="chips" role="group" aria-label="Filter by category">{chips}</div>
<div class="dirtools">
<label class="toggle" for="free"><input id="free" type="checkbox"> Free tier</label>
<label class="sr" for="sort">Sort</label>
<select id="sort" aria-label="Sort"><option value="az" selected>A to Z</option><option value="newest">Newest</option></select>
<p class="mu" id="cnt" aria-live="polite">Showing {len(tools)} tools</p>
</div></div>
<div class="rows" id="grid">{''.join(row(t, '') for t in sorted(tools, key=lambda t: t['name'].lower()))}</div>
<p class="quiet" id="empty" hidden>No tools match that search.</p>
{JS}"""
(OUT / "tools" / "index.html").write_text(page(
    f"Tool directory — {N}",
    f"Searchable directory of {len(tools)} AI tools for coding, vibe coding, automation, games, and security.",
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
# This Week leads with the ranked picks and the sourced reason on each card.
# Other tools still inside the seven-day window stay below that list.
pick_block = f'<div class="bento">{"".join(pick_card(t, i == 0) for i, t in enumerate(picks))}</div>'
others = [t for t in wk if t.get("pick_rank") is None]
if others:
    also = (f'<div class="sec"><h2>Also added in the last 7 days</h2>'
            f'<p class="mu">{len(others)} other tools added in the 7 days up to {e(fmt_date(latest.isoformat()))}.</p>'
            f'<div class="rows">{"".join(row(t, "tools/") for t in others)}</div></div>')
elif not wk and not picks:
    also = "<p class='mu'>Nothing new in the last seven days.</p>"
else:
    also = ""
if launch_only and not picks:
    week_name = "Launch week"
    week_kicker = "First batch"
    week_lede = f"The first batch of tools, added {fmt_date(LAUNCH.isoformat())}."
else:
    week_name = "This week"
    week_kicker = latest_issue["title"] if issue_is_live(latest_issue) else f"Added through {fmt_date(latest.isoformat())}"
    week_lede = "This week's picks, each with a short reason and a source."
(OUT / "this-week.html").write_text(page(
    f"{week_name} — {N}",
    week_lede,
    f'<header class="pagehead"><p class="kicker">{e(week_kicker)}</p><h1>{e(week_name)}</h1><p class="lede">{e(week_lede)}</p></header>{pick_block}{also}<div class="sec">{SIGNUP}</div>',
    "this-week.html", nodes=[item_list("This week's picks", picks)]))
def take_paragraph(t):
    # The written take for this tool, with no verdict label or stock guide line.
    # No stock verdict sentence: every take is written per tool.
    return " ".join(t["verdict_reason"].replace(_TAKE_BOILERPLATE, "").split())
def _lines(value):
    if value is None:
        return []
    if isinstance(value, str):
        return [value] if value.strip() else []
    return [v for v in value if str(v).strip()]
def rich(value):
    # Editorial markdown: links, bold, and code. Wording stays as written.
    text = e(value)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(
        r"\[([^\]]+)\]\(([^)]+)\)",
        lambda m: f'<a href="{m.group(2)}" rel="noopener">{m.group(1)}</a>',
        text,
    )
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    return text
def _paras(value):
    return "".join(f"<p>{rich(p)}</p>" for p in _lines(value))
def pricing_parts(pricing):
    # A string is prose. A list, or plans inside an object, is a plan list.
    if isinstance(pricing, dict):
        return str(pricing.get("text") or ""), list(pricing.get("plans") or [])
    if isinstance(pricing, list):
        return "", pricing
    if isinstance(pricing, str):
        return pricing, []
    return "", []
def pricing_html(pricing, tool_name):
    # items (or format "text") stay prose and a list. plans become a table at 3 or more.
    if isinstance(pricing, dict) and not pricing.get("plans") and (pricing.get("items") or pricing.get("format") == "text"):
        parts = []
        if str(pricing.get("text") or "").strip():
            parts.append(f"<p>{rich(pricing['text'])}</p>")
        items = [item for item in pricing.get("items") or [] if str(item).strip()]
        if items:
            parts.append("<ul>" + "".join(f"<li>{rich(item)}</li>" for item in items) + "</ul>")
        note = str(pricing.get("note") or "").strip()
        if note:
            parts.append(f"<p>{rich(note)}</p>")
        return "".join(parts)
    text, plans = pricing_parts(pricing)
    plans = [p for p in plans if p]
    if len(plans) >= 3:
        intro = f"<p>{rich(text)}</p>" if text.strip() else ""
        has_detail = any(isinstance(p, dict) and (p.get("detail") or p.get("notes")) for p in plans)
        heads = ["Plan", "Price"] + (["Detail"] if has_detail else [])
        body = []
        for p in plans:
            if isinstance(p, str):
                cells = [p, ""] + ([""] if has_detail else [])
            else:
                cells = [p.get("name") or "", p.get("price") or ""]
                if has_detail:
                    cells.append(p.get("detail") or p.get("notes") or "")
            body.append("<tr>" + "".join(f"<td>{rich(c)}</td>" for c in cells) + "</tr>")
        head = "".join(f"<th scope=\"col\">{e(h)}</th>" for h in heads)
        table = (f'<div class="tbl"><table><caption>{e(tool_name)} plans</caption>'
                 f"<thead><tr>{head}</tr></thead><tbody>{''.join(body)}</tbody></table></div>")
        note = ""
        if isinstance(pricing, dict) and str(pricing.get("note") or "").strip():
            note = f"<p>{rich(pricing['note'])}</p>"
        return intro + table + note
    bits = []
    if text.strip():
        bits.append(f"<p>{rich(text)}</p>")
    for p in plans:
        if isinstance(p, str):
            bits.append(f"<p>{rich(p)}</p>")
            continue
        line = " — ".join(x for x in (p.get("name"), p.get("price")) if x)
        detail = p.get("detail") or p.get("notes") or ""
        if detail:
            line = f"{line}. {detail}" if line else detail
        if line:
            bits.append(f"<p>{rich(line)}</p>")
    return "".join(bits)
def whats_new_html(raw):
    # One paragraph, several paragraphs, or a list. Omit the aside when there is nothing new.
    if not raw:
        return ""
    if isinstance(raw, str):
        raw = {"paragraphs": [raw]}
    if isinstance(raw, list):
        raw = {"paragraphs": raw}
    if not isinstance(raw, dict):
        return ""
    paragraphs = []
    text = raw.get("text")
    if isinstance(text, list):
        paragraphs.extend(text)
    elif str(text or "").strip():
        paragraphs.append(text)
    paragraphs.extend(raw.get("paragraphs") or [])
    items = list(raw.get("items") or raw.get("list") or [])
    paragraphs = [p for p in paragraphs if str(p).strip()]
    items = [item for item in items if str(item).strip()]
    if not paragraphs and not items:
        return ""
    body = "".join(f"<p>{rich(p)}</p>" for p in paragraphs)
    if items:
        body += "<ul>" + "".join(f"<li>{rich(item)}</li>" for item in items) + "</ul>"
    src = str(raw.get("source_url") or "").strip()
    date = str(raw.get("date") or "").strip()
    bits = []
    if src:
        bits.append(f'<a href="{e(src)}" rel="noopener">Source</a>')
    if date:
        bits.append(f'<time datetime="{e(date)}">{e(fmt_date(date))}</time>')
    line = f'<p class="src">{" · ".join(bits)}</p>' if bits else ""
    return f'<aside class="whatsnew" id="whats-new"><p class="label">What\'s new</p>{body}{line}</aside>'
def overview_html(t):
    # Absent overview renders nothing. Empty sections are left out, including What's new.
    ov = t.get("overview")
    if not isinstance(ov, dict):
        return ""
    blocks = []
    links = []
    def add_section(anchor, title, inner):
        if not inner:
            return
        links.append(f'<a href="#{anchor}">{e(title)}</a>')
        blocks.append(f'<section id="{anchor}"><h3>{e(title)}</h3>{inner}</section>')
    add_section("what-it-is", "What it is", _paras(ov.get("what_it_is")))
    fresh = whats_new_html(ov.get("whats_new"))
    if fresh:
        links.append('<a href="#whats-new">What\'s new</a>')
        blocks.append(fresh)
    features = _lines(ov.get("key_features"))
    if features:
        add_section("key-features", "Key features",
                    "<ul>" + "".join(f"<li>{rich(item)}</li>" for item in features) + "</ul>")
    steps = _lines(ov.get("getting_started"))
    if steps:
        add_section("getting-started", "Getting started",
                    "<ol>" + "".join(f"<li>{rich(item)}</li>" for item in steps) + "</ol>")
    add_section("pricing", "Pricing", pricing_html(ov.get("pricing"), t["name"]))
    notes = _lines(ov.get("good_to_know"))
    if notes:
        add_section("good-to-know", "Good to know",
                    "<ul>" + "".join(f"<li>{rich(item)}</li>" for item in notes) + "</ul>")
    if not blocks:
        return ""
    disclosure = str(ov.get("disclosure") or "").strip()
    note = f'<p class="disclosure"><em>{rich(disclosure)}</em></p>' if disclosure else ""
    toc = f'<nav class="toc" aria-label="On this page">{"".join(links)}</nav>'
    return f'<article class="overview"><h2>{e(t["name"])} overview</h2>{toc}{"".join(blocks)}{note}</article>'
_MONEY = re.compile(r"([$€])\s*(\d{1,3}(?:,\d{3})+|\d+(?:\.\d+)?)")
def _offer(plan):
    if isinstance(plan, str):
        return {"@type": "Offer", "description": plan}
    offer = {"@type": "Offer", "name": plan.get("name") or "Plan"}
    found = _MONEY.search(str(plan.get("price") or ""))
    if found:
        offer["priceCurrency"] = "USD" if found.group(1) == "$" else "EUR"
        offer["price"] = found.group(2).replace(",", "")
    detail = plan.get("detail") or plan.get("notes") or ""
    if detail:
        offer["description"] = detail
    return offer
def software_offers(t):
    # No ratings. Plan rows become offers. Prose pricing, including an items list, stays one offer.
    pricing = (t.get("overview") or {}).get("pricing")
    text, plans = pricing_parts(pricing)
    plans = [p for p in plans if p]
    if plans:
        offers = [_offer(p) for p in plans]
        if len(offers) == 1:
            return offers[0]
        return {"@type": "AggregateOffer", "offerCount": len(offers), "offers": offers}
    parts = []
    if str(text or "").strip():
        parts.append(str(text).strip())
    if isinstance(pricing, dict):
        parts.extend(str(item).strip() for item in (pricing.get("items") or []) if str(item).strip())
        if str(pricing.get("note") or "").strip():
            parts.append(str(pricing["note"]).strip())
    return {"@type": "Offer", "description": " ".join(parts) if parts else t["pricing"]}
def software_ld(t):
    data = {
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": t["name"],
        "url": t["url"],
        "applicationCategory": t["category"],
        "description": t["description"],
        "offers": software_offers(t),
        "dateModified": checked_iso(t),
    }
    raw = json.dumps(data, ensure_ascii=False).replace("<", "\\u003c")
    return f'<script type="application/ld+json">{raw}</script>'
for t in tools:
    ov = overview_html(t)
    rule = '<hr class="rule">' if ov else ""
    covered = issue_for(t)
    issue_crumb = ""
    issue_fact = ""
    signup = ""
    if covered:
        issue_href = f'../{covered["path"]}'
        featured = f'Featured in {covered["title"]}'
        issue_crumb = f' · <a href="{e(issue_href)}">{e(featured)}</a>'
        issue_fact = f'<dt>Letter</dt><dd><a href="{e(issue_href)}">{e(featured)}</a></dd>'
        signup = f'<div class="sec">{SIGNUP}</div>'
    b = f"""<div class="tool-hero"><div class="tool-copy"><p class="back"><a href="index.html">Tool directory</a> · {e(cat_label(t['category']))}{issue_crumb}</p><h1>{e(t['name'])}</h1><p class="vrow">{badge_html(t)}{verdict_stamp(t)}</p><p class="sum">{e(t['description'])}</p>
{software_ld(t)}</div>
<aside class="facts" aria-label="Facts">{mobile_fact(t)}<dl><dt>Use cases</dt><dd><ul>{''.join(f'<li>{e(u)}</li>' for u in t['use_cases'])}</ul></dd><dt>Pricing</dt><dd>{e(t['pricing'])}</dd><dt>Website</dt><dd><a href="{e(t['url'])}" rel="noopener">{e(t['url'])}</a></dd>
<dt>Source</dt><dd><a href="{e(t['source'])}" rel="noopener">{e(t['source'])}</a></dd><dt>Added</dt><dd><time datetime="{e(t['date_added'])}">{e(fmt_date(t['date_added']))}</time></dd>{issue_fact}</dl>
<a class="btn" href="{e(t['url'])}" rel="nofollow noopener">Visit website</a></aside>
{ov}</div>
{rule}
<section class="take" aria-labelledby="our-take"><h2 id="our-take">Our Take</h2><p>{e(take_paragraph(t))} <a href="{e(t['source'])}" rel="noopener">Source</a></p></section>
{signup}"""
    (OUT / "tools" / f"{t['slug']}.html").write_text(page(
        f"{t['name']} — {N}",
        f"{t['name']}: {t['description']}"[:300],
        b, f"tools/{t['slug']}.html", 1))
def issue_card(issue):
    # Archive cards. A published letter links to its page. An upcoming letter
    # is the title and coming date only: no headline, no note, no link.
    live = issue_is_live(issue)
    href = issue["path"].removeprefix("newsletter/") if live else ""
    title = f'<a href="{e(href)}">{e(issue["title"])}</a>' if href else e(issue["title"])
    headline = f'<p class="headline">{e(issue["headline"])}</p>' if live and issue.get("headline") else ""
    note = f'<p class="mu">{e(issue["note"])}</p>' if live else ""
    read = f'<p><a href="{e(href)}">Read the letter</a></p>' if href else ""
    return (f'<article class="issue"><h2>{title}</h2>{headline}'
            f'<p class="when">{e(issue_when(issue))}</p>{note}{read}</article>')
issue_cards = "".join(issue_card(i) for i in ISSUES)
(OUT / "newsletter" / "index.html").write_text(page(
    f"Newsletter Archive — {N}",
    "Archive of Toolsmith Weekly letters. Upcoming letters are listed with no link until they are sent.",
    f'<header class="pagehead"><p class="kicker">Letters</p><h1>Newsletter Archive</h1><p class="lede">The weekly letter. A link is added when the letter is published.</p></header>{issue_cards}<div class="sec">{SIGNUP}</div>',
    "newsletter/", 1))
def write_issue(issue):
    depth = issue["path"].strip("/").count("/") + 1
    prefix = "../" * depth
    letter = (R / issue["body"]).read_text().replace("__DIRECTORY__", f"{prefix}tools/")
    listed = [t for t in tools if str(t.get("covered_in") or "") == issue.get("id")]
    listed.sort(key=lambda t: (t.get("pick_rank") is None, t.get("pick_rank") or 0, t["name"].lower()))
    items = "".join(f'<li><a href="{prefix}tools/{t["slug"]}.html">{e(t["name"])}</a></li>' for t in listed)
    directory = ""
    if items:
        directory = (f'<section class="sec"><h2>In the directory</h2>'
                     f'<p>These tools from the letter are listed at <a href="{prefix}tools/">toolsmithweekly.com</a>.</p>'
                     f'<ul class="dirlist">{items}</ul></section>')
    body = (f'<article class="letter"><img class="letter-banner" src="{prefix}header-anvil.jpg" alt="Toolsmith Weekly">'
            f'<p class="kicker">{e(issue["title"])}</p><h1>{e(issue["headline"])}</h1>'
            f'<p class="meta">{e(issue["when"])}</p><p class="lede">{e(issue["note"])}</p>{letter}</article>'
            f'{directory}<div class="sec">{SIGNUP}</div>')
    article = {
        "@type": "Article",
        "headline": issue["headline"],
        "datePublished": issue["date"],
        "description": issue["note"],
        "url": f"{BASE}/{issue['path']}",
        "publisher": {"@id": f"{BASE}/#organization"},
        "mainEntityOfPage": f"{BASE}/{issue['path']}",
    }
    dest = OUT.joinpath(*issue["path"].strip("/").split("/"))
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "index.html").write_text(page(
        f"{issue['headline']} — {N}",
        issue["note"],
        body, issue["path"], depth, nodes=[article]))
for issue in ISSUES:
    if issue_is_live(issue):
        write_issue(issue)
# Alias paths. Meta refresh plus a plain link. Kept out of the sitemap.
def alias_page(folder):
    # One level for /issues/. Two levels for /newsletter/2/, which used to be the letter.
    depth = folder.strip("/").count("/") + 1
    up = "../" * depth
    (OUT / folder).mkdir(parents=True, exist_ok=True)
    (OUT / folder / "index.html").write_text(f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Newsletter Archive — {e(N)}</title>
<meta name="robots" content="noindex">
<meta http-equiv="refresh" content="0; url={up}newsletter/">
<link rel="canonical" href="{BASE}/newsletter/">
<meta name="description" content="The newsletter archive has moved.">
<link rel="stylesheet" href="{up}style.css"></head><body>
<main class="w" style="padding:48px 0"><h1>Newsletter Archive</h1>
<p>This page has moved.</p>
<p><a href="{up}newsletter/">Go to the newsletter archive</a></p></main></body></html>""")
for alias in ("issues", "archive", "newsletters", "newsletter/2"):
    alias_page(alias)
suggest_body = f"""<header class="pagehead"><p class="kicker">For builders</p><h1>Suggest a tool</h1><p class="lede">Indie developers: send a tool you built, or one you want listed.</p></header>
<p><a class="btn" href="{e(suggest_href)}">Suggest a tool by email</a></p>
<p class="mu">Opens your mail app to {e(CONFIG['suggest_email'])} with the subject filled in. No account and no third-party form.</p><div class="sec">{SIGNUP}</div>"""
(OUT / "suggest" / "index.html").write_text(page(
    f"Suggest a tool — {N}",
    "Indie developers can email a tool suggestion to Toolsmith Weekly.",
    suggest_body, "suggest/", 1))
issue_urls = [i["path"] for i in ISSUES if issue_is_live(i)]
urls = ["index.html", "tools/", "this-week.html", "newsletter/"] + issue_urls + ["suggest/"] + [f"tools/{t['slug']}.html" for t in tools]
(OUT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + "".join(f"<url><loc>{BASE}/{u}</loc></url>" for u in urls) + "</urlset>")
(OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {BASE}/sitemap.xml\n")
new_count = sum(is_new(t) for t in tools)
llms = [
    f"# {N}",
    "",
    f"> {VALUE}",
    "",
    f"{N} lists new AI tools for coding, vibe coding, automation, games, and security. {SOURCE_NOTE} The directory currently lists {len(tools)} tools. Tools added after 2026-10-20 and within the last 7 days are marked New this week on the website only. That badge is not used in the newsletter. The first batch is labeled Launch week.",
    "",
    "## Pages",
    "",
    f"- [Home]({BASE}/): Landing page with This Week's Stars, categories, and the latest letter.",
    f"- [Tool directory]({BASE}/tools/): Search, filter by category, free tier, and letter, and sort the full list. A to Z is the default sort. Newest is available from the sort control and from ?sort=newest. Category links use a ?cat= query. A text search uses ?q=.",
    f"- [This week]({BASE}/this-week.html): This week's picks, each with a sourced reason, plus other tools added in the seven days up to the newest date in the directory.",
    f"- [Newsletter archive]({BASE}/newsletter/): The weekly letter. Issue #1 is listed as Coming Oct 23, 2026, with no link until it is sent. /newsletter/2/, /issues/, /archive/, and /newsletters/ redirect here.",
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

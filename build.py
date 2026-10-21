#!/usr/bin/env python3
"""Build static site from tools.json into dist/. Usage: python3 build.py"""
import json, html, re, shutil, datetime, pathlib
from urllib.parse import quote
CONFIG = {"site_name": "Toolsmith Weekly",  # <- swap the brand name here
          "tagline": "Tested, not hyped. The newest AI tools, with a straight verdict.",
          "base_url": "https://toolsmithweekly.com",  # no trailing slash; canonical URLs, sitemap, robots
          "subscribe_url": "https://toolsmithweekly.beehiiv.com/subscribe",
          "suggest_email": "hello@toolsmithweekly.com"}
CONFIG["base_url"] = CONFIG["base_url"].rstrip("/")
# Links and assets stay relative (style.css, tools/<slug>.html, ../index.html) so they
# work on the custom-domain root and in a local dist/ preview.
# beehiiv's public subscribe page does not prefill ?email=, so signup is a link there.
N = CONFIG["site_name"]; R = pathlib.Path(__file__).parent; OUT = R / "dist"
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
    added = datetime.date.fromisoformat(t["date_added"])
    return added > LAUNCH and NEW_CUTOFF <= added <= TODAY
ISSUES = [{"title": "Issue #1", "when": "Coming Friday, Oct 23",
           "note": "The first letter goes out Friday, October 23, 2026. No link until it is sent."}]
suggest_href = "mailto:" + CONFIG["suggest_email"] + "?" + "&".join([
    "subject=" + quote("Tool suggestion for Toolsmith Weekly"),
    "body=" + quote("I'm an indie developer.\n\nTool name:\nWebsite:\nWhat it does:\nWhy it belongs in Toolsmith Weekly:\n")])
CSS = """:root{--bg:#0d0f14;--card:#161a22;--bd:#262c38;--tx:#e6e9ef;--mu:#9aa3b2;--ac:#7c9cff}
*{box-sizing:border-box}[hidden]{display:none!important}body{margin:0;font:16px/1.5 system-ui,sans-serif;background:var(--bg);color:var(--tx)}
a{color:var(--ac)}.w{max-width:1100px;margin:auto;padding:0 16px}header{border-bottom:1px solid var(--bd)}
header .w{display:flex;gap:16px;align-items:center;padding:14px 16px;flex-wrap:wrap}.logo{font-weight:800;font-size:1.25rem;color:var(--tx);text-decoration:none}
nav a{margin-right:14px;color:var(--mu);text-decoration:none}h1{font-size:1.8rem;margin:28px 0 6px}.mu{color:var(--mu)}
.ctl{display:flex;gap:8px;flex-wrap:wrap;margin:18px 0}input,select{background:var(--card);color:var(--tx);border:1px solid var(--bd);border-radius:8px;padding:10px 12px;font-size:1rem}
#q{flex:1;min-width:220px}.chips{display:flex;gap:6px;flex-wrap:wrap}.chip{background:var(--card);border:1px solid var(--bd);color:var(--tx);border-radius:999px;padding:6px 12px;cursor:pointer;font-size:.9rem}
.chip.on{background:var(--ac);color:#000;border-color:var(--ac)}.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:14px;margin:16px 0 40px}
.card{background:var(--card);border:1px solid var(--bd);border-radius:12px;padding:16px;display:flex;flex-direction:column;gap:6px}.card h3{margin:0;font-size:1.1rem}.card h3 a{color:var(--tx);text-decoration:none}
.v{display:inline-block;font-weight:700;font-size:.75rem;padding:2px 8px;border-radius:6px;text-transform:uppercase}.v-use{background:#1f5f3a;color:#b8f5cf}.v-skip{background:#6b2330;color:#ffc4cc}.v-wait{background:#6a5520;color:#ffe7a8}
.badge-new{display:inline-block;font-weight:700;font-size:.75rem;padding:2px 8px;border-radius:6px;background:#16324f;color:#c5e4ff;text-transform:uppercase}
.cat{font-size:.8rem;color:var(--mu)}.sig{background:var(--card);border:1px solid var(--bd);border-radius:12px;padding:20px;margin:30px 0}
a.btn{display:inline-block;background:var(--ac);color:#000;text-decoration:none;border-radius:8px;padding:10px 16px;font-weight:700}
.issue{background:var(--card);border:1px solid var(--bd);border-radius:12px;padding:16px;margin:14px 0}
footer{border-top:1px solid var(--bd);padding:20px 0;color:var(--mu);font-size:.85rem}
footer nav a{color:var(--mu);margin-right:14px;text-decoration:none}footer p{margin:8px 0 0}
dl dt{color:var(--mu);margin-top:14px;font-size:.85rem;text-transform:uppercase}dl dd{margin:4px 0 0}"""
def page(title, desc, body, path, depth=0):
    p = "../" * depth
    base = CONFIG["base_url"]
    canon = f"{base}/{path}" if base else ""
    img = f"{base}/og.jpg" if base else ""
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
    ) if canon else '<meta name="twitter:card" content="summary_large_image">'
    nav = (f'<a href="{p}index.html">Directory</a><a href="{p}this-week.html">This week</a>'
           f'<a href="{p}issues/">Past issues</a><a href="{p}suggest/">Suggest a tool</a>'
           f'<a href="{p}index.html#signup">Newsletter</a>')
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title><meta name="description" content="{e(desc)}">{metas}
<link rel="stylesheet" href="{p}style.css"></head><body>
<header><div class="w"><a class="logo" href="{p}index.html">{e(N)}</a><nav>{nav}</nav></div></header>
<main class="w">{body}</main><footer><div class="w"><nav class="foot">{nav}</nav><p>{e(N)} — {e(CONFIG["tagline"])} Verdicts are based on linked public sources unless stated otherwise.</p></div></footer></body></html>"""
def card(t, p=""):
    badge = '<span class="badge-new">New this week</span> ' if is_new(t) else ""
    return f"""<article class="card" data-cat="{e(t['category'])}" data-date="{t['date_added']}" data-text="{e((t['name']+' '+t['description']+' '+' '.join(t['use_cases'])+' '+t['category']).lower())}">
<span class="cat">{e(t['category'])} · added {t['date_added']}</span><h3><a href="{p}tools/{t['slug']}.html">{e(t['name'])}</a></h3>
<div>{badge}<span class="v v-{t['verdict']}">{t['verdict']}</span> <span class="mu">{e(t['verdict_reason'])}</span></div><p style="margin:4px 0">{e(t['description'])}</p><span class="cat">💲 {e(t['pricing'])}</span></article>"""
SIGNUP = f"""<section class="sig" id="signup"><h2 style="margin-top:0">Get the weekly verdicts</h2><p class="mu">One email a week: what to use, skip, or wait on.</p>
<p><a class="btn" href="{e(CONFIG['subscribe_url'])}">Subscribe free</a></p>
<p class="mu">Free. Opens the Toolsmith Weekly letter on beehiiv.</p></section>"""
shutil.rmtree(OUT, ignore_errors=True); (OUT / "tools").mkdir(parents=True); (OUT / "issues").mkdir(parents=True); (OUT / "suggest").mkdir(parents=True)
(OUT / "style.css").write_text(CSS)
shutil.copyfile(R / "brand" / "og.jpg", OUT / "og.jpg")
cats = sorted({t["category"] for t in tools})
chips = '<button class="chip on" data-c="">All</button>' + "".join(f'<button class="chip" data-c="{e(c)}">{e(c)}</button>' for c in cats)
JS = """<script>const q=document.getElementById('q'),s=document.getElementById('sort'),g=document.getElementById('grid'),cs=[...document.querySelectorAll('.chip')];let cat='';
const cards=[...g.children],cnt=document.getElementById('cnt');function run(){const v=q.value.toLowerCase().trim();let n=0;
const o=[...cards].sort((a,b)=>s.value==='newest'?b.dataset.date.localeCompare(a.dataset.date):s.value==='oldest'?a.dataset.date.localeCompare(b.dataset.date):a.querySelector('h3').textContent.localeCompare(b.querySelector('h3').textContent));
o.forEach(c=>{const ok=(!cat||c.dataset.cat===cat)&&(!v||c.dataset.text.includes(v));c.hidden=!ok;n+=ok;g.appendChild(c)});cnt.textContent=n+' tools';}
q.oninput=run;s.onchange=run;cs.forEach(b=>b.onclick=()=>{cs.forEach(x=>x.classList.remove('on'));b.classList.add('on');cat=b.dataset.c;run()});run();</script>"""
home = f"""<h1>The newest AI tools, with a verdict</h1><p class="mu">{e(CONFIG['tagline'])} For agent builders, vibe coders, and game devs.</p>
<div class="ctl"><input id="q" type="search" placeholder="Search tools, use cases…" aria-label="Search"><select id="sort" aria-label="Sort"><option value="newest">Newest</option><option value="oldest">Oldest</option><option value="az">A–Z</option></select></div>
<div class="chips">{chips}</div><p class="mu" id="cnt"></p><div class="grid" id="grid">{''.join(card(t) for t in tools)}</div>{SIGNUP}{JS}"""
(OUT / "index.html").write_text(page(f"{N} — AI tools directory: tested, not hyped", f"Searchable directory of {len(tools)} new AI tools for coding agents, vibe coding, automation and game dev, each with a use/skip/wait verdict.", home, "index.html"))
latest = max(datetime.date.fromisoformat(t["date_added"]) for t in tools); cut = latest - datetime.timedelta(days=7)
wk = [t for t in tools if datetime.date.fromisoformat(t["date_added"]) > cut]
(OUT / "this-week.html").write_text(page(f"This week in AI tools — {N}", f"AI tools added in the week ending {latest}.", f"<h1>This week</h1><p class='mu'>{len(wk)} tools added in the 7 days up to {latest}.</p><div class='grid'>{''.join(card(t) for t in wk)}</div>{SIGNUP}", "this-week.html"))
for t in tools:
    badge = '<span class="badge-new">New this week</span> ' if is_new(t) else ""
    b = f"""<p class="cat" style="margin-top:24px"><a href="../index.html">← All tools</a> · {e(t['category'])}</p><h1>{e(t['name'])}</h1><p>{badge}<span class="v v-{t['verdict']}">{t['verdict']}</span> {e(t['verdict_reason'])}</p><p>{e(t['description'])}</p>
<dl><dt>Use cases</dt><dd><ul>{''.join(f'<li>{e(u)}</li>' for u in t['use_cases'])}</ul></dd><dt>Pricing</dt><dd>{e(t['pricing'])}</dd><dt>Website</dt><dd><a href="{e(t['url'])}" rel="noopener">{e(t['url'])}</a></dd>
<dt>Source</dt><dd><a href="{e(t['source'])}" rel="noopener">{e(t['source'])}</a></dd><dt>Added</dt><dd>{t['date_added']}</dd></dl>{SIGNUP}
<script type="application/ld+json">{json.dumps({"@context":"https://schema.org","@type":"SoftwareApplication","name":t['name'],"url":t['url'],"applicationCategory":t['category'],"description":t['description']})}</script>"""
    (OUT / "tools" / f"{t['slug']}.html").write_text(page(f"{t['name']} review: {t['verdict'].upper()} — {N}", f"{t['name']}: {t['description']} Verdict: {t['verdict']} — {t['verdict_reason']}"[:300], b, f"tools/{t['slug']}.html", 1))
issue_cards = "".join(
    f'<article class="issue"><h2 style="margin:0 0 6px">{e(i["title"])}</h2><p style="margin:0">{e(i["when"])}</p><p class="mu" style="margin:8px 0 0">{e(i["note"])}</p></article>'
    for i in ISSUES)
(OUT / "issues" / "index.html").write_text(page(f"Past issues — {N}", "Archive of Toolsmith Weekly letters. Issue 1 arrives Friday, October 23, 2026.", f"<h1>Past issues</h1><p class='mu'>The weekly letter. Upcoming issues are listed here, and a link is added only after the letter is sent.</p>{issue_cards}{SIGNUP}", "issues/", 1))
suggest_body = f"""<h1>Suggest a tool</h1><p>Indie developers: send a tool you built, or one you want a straight verdict on.</p>
<p><a href="{e(suggest_href)}">Suggest a tool by email</a></p>
<p class="mu">Opens your mail app to {e(CONFIG['suggest_email'])} with the subject filled in. No account and no third-party form.</p>{SIGNUP}"""
(OUT / "suggest" / "index.html").write_text(page(f"Suggest a tool — {N}", "Indie developers can email a tool suggestion to Toolsmith Weekly.", suggest_body, "suggest/", 1))
urls = ["index.html", "this-week.html", "issues/", "suggest/"] + [f"tools/{t['slug']}.html" for t in tools]
base = CONFIG["base_url"]
(OUT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + "".join(f"<url><loc>{base}/{u}</loc></url>" for u in urls) + "</urlset>")
shutil.copyfile(R / "CNAME", OUT / "CNAME")
(OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {base}/sitemap.xml\n")
new_count = sum(is_new(t) for t in tools)
llms = [
    f"# {N}",
    "",
    f"> {CONFIG['tagline']}",
    "",
    f"{N} is a directory of new AI tools for coding agents, vibe coding, automation, and game development. Each tool has a use, skip, or wait verdict based on a linked public source. Tools added after 2026-10-20 and within the last 7 days are marked New this week.",
    "",
    "## Pages",
    "",
    f"- [Directory]({base}/index.html): Search, filter by category, and sort the full list. Newest is the default sort.",
    f"- [This week]({base}/this-week.html): Tools added in the seven days up to the newest date in the directory.",
    f"- [Past issues]({base}/issues/): Archive of the weekly letter. Issue 1 is coming Friday, October 23, 2026.",
    f"- [Suggest a tool]({base}/suggest/): Indie developers can email {CONFIG['suggest_email']} with a tool suggestion.",
    f"- [Subscribe]({CONFIG['subscribe_url']}): Free weekly letter on beehiiv.",
    "",
    "## Tools",
    "",
]
for t in tools:
    mark = " New this week." if is_new(t) else ""
    llms.append(f"- [{t['name']}]({base}/tools/{t['slug']}.html): {t['verdict'].upper()} — {t['description']}{mark}")
(OUT / "llms.txt").write_text("\n".join(llms) + "\n")
print(f"Built {len(tools)} tool pages into {OUT} ({new_count} new this week as of {TODAY})")

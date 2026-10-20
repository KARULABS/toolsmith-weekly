#!/usr/bin/env python3
"""Build static site from tools.json into dist/. Usage: python3 build.py"""
import json, html, re, shutil, datetime, pathlib
CONFIG = {"site_name": "Toolsmith Weekly",  # <- swap the brand name here
          "tagline": "Tested, not hyped. The newest AI tools, with a straight verdict.",
          "base_url": "https://karulabs.github.io/toolsmith-weekly"}  # no trailing slash; canonical URLs + sitemap
CONFIG["base_url"] = CONFIG["base_url"].rstrip("/")
# Links and assets stay relative (style.css, tools/<slug>.html, ../index.html) so they
# resolve under the GitHub Pages project subpath and in a local dist/ preview.
N = CONFIG["site_name"]; R = pathlib.Path(__file__).parent; OUT = R / "dist"
e = lambda s: html.escape(str(s), quote=True)
slug = lambda s: re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
tools = json.load(open(R / "tools.json"))
for t in tools: t["slug"] = slug(t["name"])
tools.sort(key=lambda t: (t["date_added"], t["name"]), reverse=True)
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
.cat{font-size:.8rem;color:var(--mu)}.sig{background:var(--card);border:1px solid var(--bd);border-radius:12px;padding:20px;margin:30px 0}.sig form{display:flex;gap:8px;flex-wrap:wrap}
button{background:var(--ac);color:#000;border:0;border-radius:8px;padding:10px 16px;font-weight:700;cursor:pointer}footer{border-top:1px solid var(--bd);padding:20px 0;color:var(--mu);font-size:.85rem}
dl dt{color:var(--mu);margin-top:14px;font-size:.85rem;text-transform:uppercase}dl dd{margin:4px 0 0}"""
def page(title, desc, body, path, depth=0):
    p = "../" * depth
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title><meta name="description" content="{e(desc)}"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}"><meta property="og:type" content="website"><meta name="twitter:card" content="summary">
{f'<link rel="canonical" href="{CONFIG["base_url"]}/{path}">' if CONFIG["base_url"] else ''}<link rel="stylesheet" href="{p}style.css"></head><body>
<header><div class="w"><a class="logo" href="{p}index.html">{e(N)}</a><nav><a href="{p}index.html">Directory</a><a href="{p}this-week.html">This week</a><a href="{p}index.html#signup">Newsletter</a></nav></div></header>
<main class="w">{body}</main><footer><div class="w">{e(N)} — {e(CONFIG["tagline"])} Verdicts are based on linked public sources unless stated otherwise.</div></footer></body></html>"""
def card(t, p=""):
    return f"""<article class="card" data-cat="{e(t['category'])}" data-date="{t['date_added']}" data-text="{e((t['name']+' '+t['description']+' '+' '.join(t['use_cases'])+' '+t['category']).lower())}">
<span class="cat">{e(t['category'])} · added {t['date_added']}</span><h3><a href="{p}tools/{t['slug']}.html">{e(t['name'])}</a></h3>
<div><span class="v v-{t['verdict']}">{t['verdict']}</span> <span class="mu">{e(t['verdict_reason'])}</span></div><p style="margin:4px 0">{e(t['description'])}</p><span class="cat">💲 {e(t['pricing'])}</span></article>"""
SIGNUP = f"""<section class="sig" id="signup"><h2 style="margin-top:0">Get the weekly verdicts</h2><p class="mu">One email a week: what to use, skip, or wait on.</p>
<!-- TODO: replace this placeholder form with the beehiiv embed code (beehiiv dashboard → Grow → Subscribe Forms → Embed). -->
<form onsubmit="event.preventDefault();this.querySelector('button').textContent='Coming soon';"><input type="email" required placeholder="you@example.com" aria-label="Email"><button>Subscribe</button></form></section>"""
shutil.rmtree(OUT, ignore_errors=True); (OUT / "tools").mkdir(parents=True)
(OUT / "style.css").write_text(CSS)
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
    b = f"""<p class="cat" style="margin-top:24px"><a href="../index.html">← All tools</a> · {e(t['category'])}</p><h1>{e(t['name'])}</h1><p><span class="v v-{t['verdict']}">{t['verdict']}</span> {e(t['verdict_reason'])}</p><p>{e(t['description'])}</p>
<dl><dt>Use cases</dt><dd><ul>{''.join(f'<li>{e(u)}</li>' for u in t['use_cases'])}</ul></dd><dt>Pricing</dt><dd>{e(t['pricing'])}</dd><dt>Website</dt><dd><a href="{e(t['url'])}" rel="noopener">{e(t['url'])}</a></dd>
<dt>Source</dt><dd><a href="{e(t['source'])}" rel="noopener">{e(t['source'])}</a></dd><dt>Added</dt><dd>{t['date_added']}</dd></dl>{SIGNUP}
<script type="application/ld+json">{json.dumps({"@context":"https://schema.org","@type":"SoftwareApplication","name":t['name'],"url":t['url'],"applicationCategory":t['category'],"description":t['description']})}</script>"""
    (OUT / "tools" / f"{t['slug']}.html").write_text(page(f"{t['name']} review: {t['verdict'].upper()} — {N}", f"{t['name']}: {t['description']} Verdict: {t['verdict']} — {t['verdict_reason']}"[:300], b, f"tools/{t['slug']}.html", 1))
urls = ["index.html", "this-week.html"] + [f"tools/{t['slug']}.html" for t in tools]
(OUT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + "".join(f"<url><loc>{CONFIG['base_url']}/{u}</loc></url>" for u in urls) + "</urlset>")
print(f"Built {len(tools)} tool pages into {OUT}")

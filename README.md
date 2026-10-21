# Toolsmith Weekly — AI tools directory (static)

Live site: https://toolsmithweekly.com/

Brand, tagline, and canonical base URL live in `CONFIG` at the top of `build.py`. `base_url` is `https://toolsmithweekly.com` (no trailing slash) so canonical tags, Open Graph URLs, `sitemap.xml`, and the `robots.txt` sitemap line use that domain. Page links and the stylesheet are relative (`style.css`, `tools/….html`, `../index.html`), so they work on the custom-domain root and in a local `dist/` preview. The repo-root `CNAME` (`toolsmithweekly.com`) is copied into `dist/` on every build.

## Add a tool
Append an object to `tools.json`:
```json
{"name":"Tool","url":"https://...","category":"coding agents","description":"One line.",
 "use_cases":["..."],"pricing":"Free; Pro $X/mo","verdict":"use|skip|wait",
 "verdict_reason":"One line.","verdict_checked":"YYYY-MM-DD","date_added":"YYYY-MM-DD","source":"https://source-link"}
```
Categories: `coding agents`, `vibe-coding app builders`, `AI agents/automation`, `gaming/game dev`, `general` (new ones get a filter chip automatically). Every fact needs a source link. `verdict_checked` is the date that verdict was last re-reviewed. It is optional: if you omit it, the site shows `date_added`. Cards, tool pages, and a future Current verdicts page all read it through `checked_iso()` / `verdict_stamp()` in `build.py`.

## Build & preview
```
python3 build.py                     # writes dist/ (no dependencies, Python 3.8+)
cd dist && python3 -m http.server 8765
```
Output: `dist/index.html` (search, category filter, Newest/Oldest/A–Z sort, “New this week” badges), `dist/this-week.html`, `dist/issues/` (past letters), `dist/suggest/` (mailto for indie devs), `dist/tools/<slug>.html` (one SEO page per tool with title, meta description, Open Graph, JSON-LD), `dist/og.jpg` (1200×630 share image), `dist/sitemap.xml`, `dist/robots.txt`, `dist/llms.txt`, and `dist/CNAME`.

## Deploy (GitHub Pages)
Pushes to `main` run `.github/workflows/pages.yml`. The workflow runs `python3 build.py` and deploys `dist/` with `actions/upload-pages-artifact` and `actions/deploy-pages`.

In the repository settings, Pages → Build and deployment → Source must be **GitHub Actions**. `dist/` is generated output and is listed in `.gitignore`.

## Newsletter
Every signup box links to the public beehiiv page `https://toolsmithweekly.beehiiv.com/subscribe`. That page does not prefill an email address, so the site uses a “Subscribe free” link and no API key.

## Suggest a tool
`/suggest/` is a `mailto:hello@toolsmithweekly.com` link with a subject and a short body for indie developers. No third-party form.

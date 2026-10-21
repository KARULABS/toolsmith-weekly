# Toolsmith Weekly — AI tools directory (static)

Live site: https://toolsmithweekly.com/

Brand, the one-line value prop, and the canonical base URL live in `CONFIG` at the top of `build.py`. `base_url` is `https://toolsmithweekly.com` (no trailing slash) so canonical tags, Open Graph URLs, `sitemap.xml`, and the `robots.txt` sitemap line use that domain. Page links and the stylesheet are relative (`style.css`, `tools/….html`, `../index.html`), so they work on the custom-domain root and in a local `dist/` preview. The repo-root `CNAME` (`toolsmithweekly.com`) is copied into `dist/` on every build.

## Add a tool
Append an object to `tools.json`:
```json
{"name":"Tool","url":"https://...","category":"coding agents","description":"One line.",
 "use_cases":["..."],"pricing":"Free; Pro $X/mo","verdict":"use|try|wait|skip",
 "verdict_reason":"One line.","verdict_checked":"YYYY-MM-DD","date_added":"YYYY-MM-DD","source":"https://source-link"}
```
Categories: `coding agents`, `vibe-coding app builders`, `AI agents/automation`, `gaming/game dev`, `general` (new ones get a filter chip and a category tile automatically). Reader-facing labels live in `CAT_LABEL` in `build.py`. Every fact needs a source link. `verdict_checked` is the date that verdict was last re-reviewed. It is optional: if you omit it, the site shows `date_added`. Cards, tool pages, and the Current verdicts page all read it through `checked_iso()` / `verdict_stamp()`.

Homepage "This week's picks" are the four names in `PICKS` at the top of `build.py`. Swap that list each Friday. The build stops if a name is missing from `tools.json`.

## Build & preview
```
python3 build.py                     # writes dist/ (no dependencies, Python 3.8+)
cd dist && python3 -m http.server 8765
```
Output:

- `dist/index.html` — landing page: hero, this week's picks, category grid, how verdicts work, latest letter, signup
- `dist/tools/` — searchable directory (category filter, Newest/Oldest/A–Z sort). `?cat=` opens a category.
- `dist/tools/<slug>.html` — one page per tool, with Open Graph and JSON-LD
- `dist/verdicts/` — tools grouped under Use it, Try it, Wait, and Skip
- `dist/this-week.html` — tools added in the last seven days
- `dist/newsletter/` — newsletter archive
- `dist/issues/` — meta refresh to `/newsletter/` (not listed in the sitemap)
- `dist/suggest/` — mailto for indie devs
- `dist/anvil.jpg` and `dist/og.jpg` — brand header and 1200×630 share image
- `dist/sitemap.xml`, `dist/robots.txt`, `dist/llms.txt`, `dist/CNAME`

"New this week" badges are website-only (directory, this week, and tool pages). They stay off the newsletter archive. Tools dated 2026-10-20 are the launch batch and are not badged.

## Deploy (GitHub Pages)
Pushes to `main` run `.github/workflows/pages.yml`. The workflow runs `python3 build.py` and deploys `dist/` with `actions/upload-pages-artifact` and `actions/deploy-pages`.

In the repository settings, Pages → Build and deployment → Source must be **GitHub Actions**. `dist/` is generated output and is listed in `.gitignore`.

## Newsletter
Every signup box links to the public beehiiv page `https://toolsmithweekly.beehiiv.com/subscribe`. That page does not prefill an email address, so the site uses a "Subscribe free" link and no API key. The nav label is Subscribe. The archive is "Newsletter Archive" at `/newsletter/`.

## Suggest a tool
`/suggest/` is a `mailto:hello@toolsmithweekly.com` link with a subject and a short body for indie developers. No third-party form.

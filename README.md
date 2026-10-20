# Toolsmith Weekly — AI tools directory (static)

Live site: https://karulabs.github.io/toolsmith-weekly/

Brand, tagline, and canonical base URL live in `CONFIG` at the top of `build.py`. `base_url` is `https://karulabs.github.io/toolsmith-weekly` (no trailing slash) so canonical tags and `sitemap.xml` use the GitHub Pages project subpath. Page links and the stylesheet are relative (`style.css`, `tools/….html`, `../index.html`), so they resolve under `/toolsmith-weekly/` and still work if you preview `dist/` locally.

## Add a tool
Append an object to `tools.json`:
```json
{"name":"Tool","url":"https://...","category":"coding agents","description":"One line.",
 "use_cases":["..."],"pricing":"Free; Pro $X/mo","verdict":"use|skip|wait",
 "verdict_reason":"One line.","date_added":"YYYY-MM-DD","source":"https://source-link"}
```
Categories: `coding agents`, `vibe-coding app builders`, `AI agents/automation`, `gaming/game dev`, `general` (new ones get a filter chip automatically). Every fact needs a source link.

## Build & preview
```
python3 build.py                     # writes dist/ (no dependencies, Python 3.8+)
cd dist && python3 -m http.server 8765
```
Output: `dist/index.html` (search, category filter, newest/oldest/A–Z sort), `dist/this-week.html` (tools added in the 7 days up to the newest `date_added`), `dist/tools/<slug>.html` (one SEO page per tool with title, meta description, OpenGraph, JSON-LD), `dist/sitemap.xml`.

## Deploy (GitHub Pages)
Pushes to `main` run `.github/workflows/pages.yml`. The workflow runs `python3 build.py` and deploys `dist/` with `actions/upload-pages-artifact` and `actions/deploy-pages`.

In the repository settings, Pages → Build and deployment → Source must be **GitHub Actions**. `dist/` is generated output and is listed in `.gitignore`.

## Newsletter
The signup form is a placeholder. Search `build.py` for `TODO` and paste the beehiiv embed code there.

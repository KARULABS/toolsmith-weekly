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
Categories: `coding agents`, `vibe-coding app builders`, `AI agents/automation`, `gaming/game dev`, `Security` (new ones get a filter chip and a category tile automatically). Reader-facing labels are title case in `CAT_LABEL` in `build.py`: Coding Agents, Vibe Coding, Automation, Gaming, Security. There is no separate `general` category. Every fact needs a source link. If a price is not on a public page, write `Pricing unverified` instead of a number. Facts come from official pricing pages, docs, and public announcements, linked on every tool page, written with AI help and reviewed for accuracy. Do not write that the site tested a tool, and do not add an aside that the source does not support. `verdict` and `verdict_reason` stay in the data and are used only to write the Our Take paragraph. The site does not print Use, Try, Wait, or Skip labels. On a tool page, facts come first. An optional `overview` object renders before Our Take when it is present: `what_it_is` (paragraphs), `whats_new` (one paragraph, several paragraphs, or a list, plus `source_url` and `date`; the callout is omitted when there is nothing new), `key_features`, `getting_started`, `pricing` (a string or an `items` list stays prose; `plans` become a table only when there are 3 or more), `good_to_know`, `sources` (kept on the object; not its own section), and `disclosure` (an italic line at the end of the overview). Our Take follows as a visible card: one short paragraph plus the source link. `verdict_checked` is optional: if you omit it, the site shows `date_added` as Last checked. Tool pages show that stamp once.

Homepage "This Week's Stars" are the tools in `tools.json` that set `pick_rank` (an integer). Lower rank is first, and rank 1 is the featured card. Each ranked tool also needs `pick_reason` (one or two plain sentences on why it is picked this week) and `pick_source` (the announcement or changelog URL). On the card, the reason is the bold line under the tool name, the source link sits under that, and the tool's description stays underneath. The same picks, with the same reason and source, lead the This Week page. The build stops if a ranked pick has no `pick_reason`, no `pick_source`, a non-integer rank, or a rank shared with another tool. Optional `covered_in` is an issue id, or a list of issue ids when a tool is in more than one letter. The build also scans each issue body for listing links (`tools/<slug>.html`, including the `__DIRECTORY__` placeholder) and fills in any issue those links point at, so a tool page links back even when `covered_in` was left blank. While an issue has `published` set to true, the tool page links "Featured in Issue #1" once per issue and includes the signup box. An unpublished issue keeps the id and hides that link.

## Build & preview
```
python3 build.py                     # writes dist/ (no dependencies, Python 3.8+)
cd dist && python3 -m http.server 8765
```
Output:

- `dist/index.html` — product homepage: full-width hero, This Week's Stars, category tiles, letter and signup
- `dist/tools/` — directory with a search box, A–Z jump links, category chips, a free-tier toggle, a New this week toggle, and compact rows. The intro does not state a tool total. A count beside the filters reads "Showing N tools" and updates as the filters change. Each row shows a one-line price summary, such as `Free tier, from $20/mo` or `Pricing unverified`, plus a Full, Partial, None, or Not confirmed badge. The tool page keeps the full pricing sentence. `?cat=` opens a category. `?q=` fills the search box. `?new=1` checks New this week. `?free=1` checks Free tier. `?letter=` selects a letter. `?sort=newest` sorts newest first. Those combine. A to Z is the default sort, including in the static HTML. Newest stays available. The New this week check runs in the browser from `date_added`: after 2026-10-20 and within the last 7 days, using the visitor's local date so it does not go stale between builds.
- `dist/tools/<slug>.html` — one page per tool, with Open Graph and JSON-LD (`SoftwareApplication`: name, url, category, offers; no ratings). Facts come first. A long overview renders only when that tool has an `overview` object, then Our Take.
- `dist/verdicts/` — meta refresh to `/tools/` (not listed in the sitemap)
- `dist/this-week.html` — This Week's Picks first (tools with `pick_rank`, each linking to its listing, plus a Read Issue link to the latest published letter), then Newly Added: other tools that pass the same New this week rule. That section links to `/tools/?new=1` sorted newest first. The launch batch is not listed as new, and the New this week badge is not repeated on this page. Row descriptions use the same word-boundary ellipsis as the directory. The initial batch is labeled Launch week only when it is the whole window.
- `dist/newsletter/` — newsletter archive. A letter is built and linked only when its `published` field is true. Issue #1 is published at `dist/newsletter/1/`. An unpublished letter stays in the archive and on the homepage as its title and coming date, with no page, no link, and no letter note. The letter body stays in `content/`.
- `dist/newsletter/2/`, `dist/issues/`, `dist/archive/`, and `dist/newsletters/` — meta refresh to `/newsletter/` (not listed in the sitemap)
- `dist/suggest/` — mailto for indie devs
- `dist/og.jpg` — 1200×630 share image. The homepage anvil is an inline pixel drawing, not a photo.
- `dist/sitemap.xml`, `dist/robots.txt`, `dist/llms.txt`, `dist/CNAME`

"New this week" badges are website-only (directory, homepage, and tool pages). They stay off the newsletter archive and off the This Week page. The visitor's browser shows the badge when `date_added` is after 2026-10-20 and within the last 7 days, so a Friday build does not leave a stale badge up. Tools dated 2026-10-20 are the launch batch and are not badged.

## Deploy (GitHub Pages)
Pushes to `main` run `.github/workflows/pages.yml`. The workflow runs `python3 build.py` and deploys `dist/` with `actions/upload-pages-artifact` and `actions/deploy-pages`.

In the repository settings, Pages → Build and deployment → Source must be **GitHub Actions**. `dist/` is generated output and is listed in `.gitignore`.

## Newsletter
Every signup box links to the public beehiiv page `https://toolsmithweekly.beehiiv.com/subscribe`. That page does not prefill an email address, so the site uses a "Subscribe free" link and no API key. The nav label is Subscribe. The archive is "Newsletter Archive" at `/newsletter/`. A letter is linked from that archive only when `published` is true in `ISSUES` in `build.py`. `/newsletter/2/`, `/issues/`, `/archive/`, and `/newsletters/` redirect there.

## Suggest a tool
`/suggest/` is a `mailto:hello@toolsmithweekly.com` link with a subject and a short body for indie developers. No third-party form.

## Mobile
Each tool in `tools.json` has `mobile` (`full`, `partial`, `none`, or `unverified`), plus `mobile_note`, `mobile_source`, and `mobile_description`. A tool page shows `Mobile: Fully supported`, `Mobile: Partial`, or `Mobile: Not supported`, then the note and a source link. `unverified` shows `Mobile: not confirmed` and no note. The description under that line is one or two plain sentences from the note and source. Directory rows show a Full, Partial, None, or Not confirmed badge.

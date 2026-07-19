# ninjaapps.net

Static site for **NinjaApps** — iOS games & utilities. Design: "Paper Dojo"
(warm paper, ink, vermillion accent, hairline grids). Hosted on GitHub Pages
at [ninjaapps.net](https://ninjaapps.net). No build step: plain HTML + one
shared stylesheet.

## Structure

```
index.html                   landing page (cards for every app)
style.css                    all styles + design tokens (light/dark)
assets/theme.js              theme-toggle wiring
privacy/index.html           privacy hub (links each app's policy)
games/<slug>/index.html      one page per app
games/<slug>/privacy.html    one privacy policy per app
games/<slug>/terms.html      terms — needed by anything with an IAP
games/<slug>/support.html    support page — ASC's support field needs a URL
games/_template/             copy this to add a new app
tools/check-site.py          structural checks — run before every commit
404.html                     not-found page
CNAME                        custom domain for GitHub Pages
```

## Checks

```sh
python3 tools/check-site.py
```

No build step means no compiler to catch a link that rotted when a page moved.
This script covers that: it verifies the promised pages exist, that internal
links resolve, that `sitemap.xml` and the pages on disk agree in both
directions, that canonicals are self-consistent, that no `{{TOKEN}}` or
`<CONFIRM …>` placeholder escaped the template — and that the URLs **baked
into the Smalti binary** still resolve. Run it before every commit.

## Adding a new app

1. Copy `games/_template/` to `games/<slug>/` and replace every `{{TOKEN}}`
   in both files (`{{EFFECTIVE_DATE}}` is `YYYY-MM-DD`). Remove the
   `noindex` meta line at the top of each copied file.
2. Add a card on `index.html` under `#games` and bump the `group-count`.
3. Add a row on `privacy/index.html` and bump its count.
4. Add every new URL to `sitemap.xml` and to `MANIFEST` in
   `tools/check-site.py`.
5. Run the checker.

Apps that sell anything need `terms.html` and `support.html` too — copy
Smalti's and rewrite them. App Store Connect's support field will not accept
a `mailto:`, so the web page is mandatory, not a nicety.

## Load-bearing URLs

Smalti ships these three addresses hardcoded in its binary
(`MosaicRush/UI/Components.swift`, `enum AppLinks`):

```
https://ninjaapps.net/games/smalti/privacy.html
https://ninjaapps.net/games/smalti/terms.html
https://ninjaapps.net/games/smalti/support.html
```

Moving or renaming those pages ships a dead legal link to App Review and to
everyone who already installed the app. Change them only alongside a game
release, and update `BAKED_IN_URLS` in `tools/check-site.py` at the same time.

## Placeholder inventory (TODO)

- Striped boxes (`.ph`) are asset slots: hero art on the landing page, the
  Smalti app icon (1024×1024), and three screenshots (1290×2796).
- Smalti's App Store button is inert (`.btn-quiet`) until the App Store
  Connect record exists — search `TODO` across the repo.
- `support@ninjaapps.net` must be a live mailbox before submission; the
  support page promises a 24–48 h reply.

## Local preview

```sh
python3 -m http.server 8000   # then open http://localhost:8000
```

Pages also open fine directly from disk (`file://`) except `404.html`,
which uses absolute paths (it can be served from any URL).

## Theme

Light/dark toggle persists in `localStorage` (`ninjaapps-theme`); first visit
follows `prefers-color-scheme`. A blocking snippet in each `<head>` sets
`data-theme` before paint to avoid flashing.

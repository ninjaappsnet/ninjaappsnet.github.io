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

## Legal page versioning

Published privacy/terms are never retro-edited in substance. The canonical
URL (`games/smalti/privacy.html`) always serves the **latest** version — it
is baked into the app binary and must not move. To change substance:

1. Snapshot the outgoing page beside it: `privacy-v1.0.html` (keep its
   `<link rel="canonical">` pointing at itself, add `noindex`).
2. Rewrite the canonical page with the new version number and effective date.
3. Add a **Version history** section on the canonical page linking every
   archived version with its effective date.
4. Keep archived versions out of `sitemap.xml` (they are `noindex`); list
   them in `MANIFEST` in `tools/check-site.py` so their existence — and the
   history links — stay enforced.
5. Run `python3 tools/check-site.py`.

Typo and navigation fixes don't need a bump; anything touching meaning does.
The same rule (and the ASC privacy-label same-release requirement) lives in
the game repo's PUBLISHING_TODO.

## Localized legal pages

App Store Connect requires a Privacy Policy URL on **every** localization of
the app record, not just English, and blocks review until each is filled. So
Smalti's policy ships in all twelve App Store languages:

```
games/smalti/privacy.html            en  (canonical, baked into the binary)
games/smalti/privacy-<code>.html     de es fr it ja ko pl pt-br ru tr zh-hans
```

Rules the checker enforces (`check_localized_privacy`):

- Each page is self-canonical, carries `<html lang>` matching its code, and
  declares the **full** set of `hreflang` alternates plus `x-default` → English.
- The map of ASC locale → page lives in `LOCALIZED_PRIVACY` in
  `tools/check-site.py`. Adding an App Store language means adding a page,
  a `MANIFEST` entry, a `sitemap.xml` row, and an entry in that map — plus a
  link in the `.langs` row on all twelve existing pages.

The English page is the authoritative text and every translation says so in a
`.tnote` line. A substantive change therefore means re-translating: bump the
version on all twelve, or the set falls out of sync silently. Note the ASC
locale codes are not the filenames — `es-ES` → `privacy-es.html`,
`zh-Hans` → `privacy-zh-hans.html`.

The webfont subsets cover Latin, Latin-ext and Japanese only, so `style.css`
hands the Cyrillic, Hangul and Simplified-Chinese pages a system font stack;
without it those pages mix two typefaces mid-sentence and render Chinese Han
with Japanese glyph forms.

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

## Assets

Smalti's icon and screenshots are real (WebP, captured 2026-07-20 from the
iPhone 16 Pro Max simulator). Source masters live in the game repo at
`mosaic-rush/marketing/` — icon at 1024, screenshots at 1320×2868, sized for
App Store reuse. Web copies: `assets/icon-smalti-144.webp` (landing card),
`games/smalti/icon-320.webp` (hero), `games/smalti/shot-*.webp` (750px wide).

## Placeholder inventory (TODO)

- One striped box (`.ph`) left: the hero art / studio mark on the landing page.
- Smalti's App Store button is live (id `6792641328`). `.btn-quiet` and the
  `games/_template/` placeholder stay for the next app — search `TODO`.
- Smalti's press fact sheet still says `RELEASE — TBD 2026`; set the real
  date once the app is public.
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

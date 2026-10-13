# ninjaapps.net

Static site for **NinjaApps** — iOS games & Mac apps. Design: "Paper Dojo"
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
games/smalti/daily/          landing page for the daily share link (see Universal links)
.well-known/apple-app-site-association   which URLs iOS hands to the Smalti app
apps/<slug>/                 same four pages for a non-game app (apps/dayfolio/)
games/_template/             copy this to add a new app
assets/brand/                brand exports + the two banner .html sources
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

It also guards the daily share link's two halves: the `apple-app-site-association`
file must parse, name the Smalti app, and match the daily path (with and without
the trailing slash) and nothing broader; and the landing page must stay static,
request nothing off-origin, and carry a social card whose image exists.

The Smalti marketing pages (`STALE_CLAIMS` in the script) are held to the game's
code, not to last quarter's copy: the check fails on a claim the app has
retired (395 levels, nine packs, Masterpiece Commission, "handcrafted", daily
leaderboards, two attempts, an iPad date, "TBD") and on a page that stops stating
the catalog numbers the code defines (`CATALOG`: 411 levels, 10 Rooms, 40 free).
The source of those numbers is the game repo: `Catalog.packs` in
`MosaicRush/Model/Content.swift` and `Tunables.freeFourPieceLevels` in
`MosaicRush/Model/GameConfig.swift`. When the game changes, change `CATALOG`, the
copy and the check in the same commit. The published privacy policy and terms
are not in that list on purpose: they are versioned, never retro-edited (see
below), so a claim they carry that the app has since retired is fixed by a new
version.

## Social

Every page footer carries the same four profiles, in the same order:

```
YouTube    https://www.youtube.com/@NinjaAppsnet
Instagram  https://www.instagram.com/ninjaappsnet/
TikTok     https://www.tiktok.com/@ninjaapps
X          https://x.com/NinjaAppsnet
```

The order is a judgement about the channels, not alphabetical — YouTube and
Instagram carry the trailer and finished-artwork material, TikTok is the
widest-reach discovery channel, X is mostly press and dev community. It lives
in `SOCIAL` in `tools/check-site.py`, and `check_social` enforces that all
nineteen footers agree with it, so reordering means editing every page. The
same list is repeated as `sameAs` in the `Organization` JSON-LD on
`index.html` (that is what ties the profiles to the domain for a search
engine), and `check_same_as` keeps the two in step.

The marks are inline single-path SVGs in the footer's own ink, not brand
colours: four saturated logos would outshout the one accent the palette is
built around, and every one of the four brands permits a single-colour mark.
Inline, because the site sends no visitor request off-origin — the same reason
the webfonts are self-hosted. Each link carries its platform name as an
`aria-label` and each `<svg>` is `aria-hidden`, so the name is announced once;
the row's own label is translated per page (`NAV_LABEL` in the injector), the
four brand names are not.

`games/smalti/press.html` repeats the handles as text on the fact sheet, where
a journalist looks for them.

## Adding a new app

1. Copy `games/_template/` to `games/<slug>/` and replace every `{{TOKEN}}`
   in both files (`{{EFFECTIVE_DATE}}` is `YYYY-MM-DD`). Remove the
   `noindex` meta line at the top of each copied file.
2. Add a card on `index.html` under `#games` and bump the `group-count`.
3. Add a row on `privacy/index.html` and bump its count.
4. Copy the footer's `<nav class="social">` block onto every new page —
   `check_social` will fail the build until you do (see **Social** above).
5. Add every new URL to `sitemap.xml` and to `MANIFEST` in
   `tools/check-site.py`.
6. Run the checker.

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

Two more addresses are just as fixed. Every install fetches
`games/smalti/config/v1.json`. And from Smalti 1.2.2 every share link a player
sends points at `https://ninjaapps.net/games/smalti/daily/?d=YYYY-MM-DD`, so that
path is in `BAKED_IN_URLS` as well: links, once sent, cannot be recalled.

## Universal links (the daily share link)

Smalti 1.2.2 shares `https://ninjaapps.net/games/smalti/daily/?d=YYYY-MM-DD`
in place of the old `mosaicrush://daily/<day>` link, which means nothing to
anyone without the app and is often not even tappable in a chat app. The link
carries one thing, the day the sharer played (their own local day key): no
account, no identifier.

- **App installed:** iOS opens the app and never shows the page. That takes two
  halves: this site's `/.well-known/apple-app-site-association`, and
  `applinks:ninjaapps.net` in the app's entitlements (an app-repo change that
  ships with 1.2.2; the 1.2.1 binary does not have it, so nothing opens in-app
  until a player updates). The entitlement names the apex: `www.` 301s to it.
- **Anyone else**, a browser that does not hand links over, or a pasted URL:
  `games/smalti/daily/index.html`. It is static. One inline script reads an
  optional `?d=`, accepts it only if it is exactly one real calendar day from
  2026-07-01 (the first daily) to two days after the visitor's own date (time
  zones span 26 hours), and prints it in the visitor's locale ("I restored the
  mosaic for 13 October 2026"). Anything else leaves the default line. The
  script requests nothing, stores nothing and sets no cookie, and the page loads
  only same-origin files; `check-site.py` enforces both. (The sitewide theme
  toggle still keeps its one `ninjaapps-theme` preference in `localStorage`, as
  on every page.) The App Store link is a plain text button to
  `https://apps.apple.com/app/id6792641328`, because a badge image would be a
  third-party request.
- **"Open today's puzzle"** on that page is `mosaicrush://daily`, not the same
  https URL. iOS keeps a tap on a same-site link inside Safari rather than
  handing it to the app, so an https link there would just reload the page. The
  scheme is registered by 1.2.1 and already opens today's daily (a link's day is
  ignored on purpose: an old link never resurrects an old board). The page also
  carries the Smart App Banner like the other Smalti pages, with `app-argument`
  set to that scheme link, so Safari's own "Open" button lands on the daily too.
- **The file** is `.well-known/apple-app-site-association`: exact name, no
  extension, JSON. `appIDs` is `745BCAQCQ4.net.ninjaapps.games.mosaicrush` (team
  id + bundle id, from the game's `project.yml`). The iOS 13+ `components` list
  matches `/games/smalti/daily` and `/games/smalti/daily/*`, so with and without
  the trailing slash and with any query, and nothing else: the privacy policy,
  support and press pages keep opening in the browser. A legacy `paths` entry
  repeats it for iOS 12 and older. Smalti requires iOS 17, so it is dead weight
  kept because it is harmless.
- **GitHub Pages.** `/.well-known` is published only because `.nojekyll`
  exists: Jekyll would silently drop dot-directories, so never delete it. Pages
  serves an extensionless file as `application/octet-stream` and cannot set
  headers. The file is valid JSON regardless, and the zone sits behind
  Cloudflare, so if Apple's validator ever objects to the content type, a
  Response Header Transform Rule setting `Content-Type: application/json` for
  that one path is the fix; not moving the file and not giving it an extension.
  The URL must answer `200` directly. Apple does not follow redirects.
- **Checking it** after every change:

  ```sh
  curl -sSI https://ninjaapps.net/.well-known/apple-app-site-association   # 200, no Location
  curl -s   https://ninjaapps.net/.well-known/apple-app-site-association | python3 -m json.tool
  curl -si  https://app-site-association.cdn-apple.com/a/v1/ninjaapps.net  # what iOS will see
  ```

  Devices read Apple's CDN copy, not the site. It refreshes on its own schedule,
  hours rather than minutes, and answers a miss with `cache-control:
  max-age=3600`, so a probe made before the file existed can pin a 404 for an
  hour. A rejection carries an `apple-failure-reason` header saying what it did
  not like. While building the app side, `applinks:ninjaapps.net?mode=developer`
  skips the CDN on a development-signed build, on a device with Settings →
  Developer → Associated Domains Development switched on.

## Assets

Dayfolio (`apps/dayfolio/`) is a Mac app, so its screenshots are 1440×900 desktop
captures (WebP with alpha, 1200px wide, `shot-*.webp`) laid out two across by
`.grid-2` + `figure.shot`. Its App Store button is a dashed `.btn-quiet` span
until the app is live; swap in the real link (see the TODO comment in
`apps/dayfolio/index.html`) and add `<meta name="apple-itunes-app">` at release.

Smalti's icon and screenshots are real (WebP, captured 2026-07-20 from the
iPhone 16 Pro Max simulator). Source masters live in the game repo at
`mosaic-rush/marketing/` — icon at 1024, screenshots at 1320×2868, sized for
App Store reuse. Web copies: `assets/icon-smalti-144.webp` (landing card),
`games/smalti/icon-320.webp` (hero), `games/smalti/shot-*.webp` (750px wide).

## Placeholder inventory (TODO)

- One striped box (`.ph`) left: the hero art / studio mark on the landing page.
- Smalti's App Store button is live (id `6792641328`). `.btn-quiet` and the
  `games/_template/` placeholder stay for the next app — search `TODO`.
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

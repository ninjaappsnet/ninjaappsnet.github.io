# ninjaapps.net

Static site for **NinjaApps** — games and apps for iPhone, iPad and Mac. Design: "Paper Dojo"
(warm paper, ink, vermillion accent, hairline grids). Hosted on GitHub Pages
at [ninjaapps.net](https://ninjaapps.net). Plain HTML + one shared stylesheet,
with no build step for the hand-written pages. Dayfolio's guide, template and
article pages are generated from Markdown by a standard-library script, and the
output is committed (see **Dayfolio pages**).

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
apps/dayfolio/archive-format.html   the .dayfolio file format, generated (see Dayfolio)
apps/dayfolio/privacy-v1.0.html     version 1.0 of the policy, archived (noindex);
apps/dayfolio/terms-v1.0.html       the same for the terms
games/_template/             copy this to add a new app
assets/brand/                brand exports + the two banner .html sources
tools/check-site.py          structural checks — run before every commit
tools/archive-page.py        regenerates apps/dayfolio/archive-format.html from the app repo's doc
tools/dayfolio-build.py      builds Dayfolio's guide, templates and articles pages, keeps the Dayfolio
                             sub-navigation current, and writes sitemap.xml and robots.txt
tools/test_*.py              the Python tools' own tests (python3 -m unittest)
content/dayfolio/<section>/  Markdown sources of those pages: guide, templates, articles
apps/dayfolio/guide/ …       generated from content/dayfolio/ (also templates/, articles/): never edit
apps/dayfolio/social-card.png  the Dayfolio pages' social card (source: assets/brand/dayfolio-card.html)
404.html                     not-found page
CNAME                        custom domain for GitHub Pages
```

## Checks

```sh
python3 tools/check-site.py
python3 -m unittest discover -s tools -p 'test_*.py'   # after touching a tool
```

`check-site.py` also runs `tools/dayfolio-build.py --check`, so a generated page
that differs from its source fails it. No build step means no compiler to catch a link that rotted when a page moved.
This script covers that: it verifies the promised pages exist, that internal
links resolve, that `sitemap.xml` and the pages on disk agree in both
directions, that canonicals are self-consistent, that no `{{TOKEN}}` or
`<CONFIRM …>` placeholder escaped the template — and that the URLs **baked
into the Smalti binary** still resolve. Run it before every commit.

It also guards the daily share link's two halves: the `apple-app-site-association`
file must parse, name the Smalti app, and match the daily path (with and without
the trailing slash) and nothing broader; and the landing page must stay static,
request nothing off-origin, and carry a social card whose image exists.
`check-site.py` reads the page; it cannot run it. The `?d=` reader's behaviour
(strict dates, the visitor's locale, the day never shifting with time zone) is
covered by a separate dependency-free test: `node tools/test-daily-page.mjs`.
Run it after touching the script in `games/smalti/daily/index.html`.

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

Dayfolio's pages are held to the app the same way (`check_dayfolio`, `DAYFOLIO_*`
in the script). The product, support, privacy and terms pages fail on a claim the
first copy made and the app has outgrown (`$9.99`, "coming soon", the "Mac App
Store", "premium", "free trial"), and on losing a fact: the five prices, the App
Store link and Smart App Banner id, the refund sentence, the free tier's "one
journal and 100 entries", the anchors the app opens (`#quick-note-link`) and one
anchor per permission on the privacy policy. The policy must name its version
and link the archived one; the archived versions must stay `noindex` and link
back. The landing page and the privacy hub are held to the same retired claims
and must say Dayfolio is for iPhone, iPad and Mac. The prices and ids are the
app repo's (`docs/product-spec.md` §3.7b, D223–D225); when they change, change
`DAYFOLIO_PRICES`, the copy and the App Store Connect products in the same
commit. `STALE_CLAIMS`' iPad rule (a Smalti claim) skips the landing page, which
also introduces Dayfolio.

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
in `SOCIAL` in `tools/check-site.py`, and `check_social` enforces that every
page's footer agrees with it, so reordering means editing every page. The
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
5. Run `python3 tools/dayfolio-build.py`, which writes `sitemap.xml` from every
   indexable page, and add every new URL to `MANIFEST` in `tools/check-site.py`.
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

Dayfolio's pages follow it. `apps/dayfolio/privacy.html` and `terms.html` are
version 1.1, effective 2026-10-15, the first to cover iPhone and iPad. Version 1.0
(effective 2026-09-29, the Mac app) stays readable as `privacy-v1.0.html` and
`terms-v1.0.html`: `noindex`, self-canonical, a line at the top saying which
dates it was in force and linking the current version, and each is in `MANIFEST`
but not in `sitemap.xml`. The canonical page's version history says what 1.1
changed, including what goes past the permissions the app asks for (what a file
keeps inside it, the mirror folder and the Spotlight index as second copies of
your text, where the quick-note key is kept). The next substantive change
snapshots 1.1 as `privacy-v1.1.html` first.

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

Dayfolio's apps ship addresses too (`AboutCopy` and `HelpMenu` in the app repo's
`DayfolioFeatures/State/`; the app's tests pin them), and these have no extension,
which GitHub Pages serves from the `.html` file:

```
https://ninjaapps.net/apps/dayfolio/support                      Settings › Help and feedback; Help › Dayfolio Help (Mac)
https://ninjaapps.net/apps/dayfolio/privacy                      Settings › About › Privacy policy
https://ninjaapps.net/apps/dayfolio/support#quick-note-link      Help › Writing notes from links (Mac)
```

The `#quick-note-link` section of `support.html` carries the two shell snippets
from the app repo's `docs/quick-note-link.md`, which a test there keeps equal to
the line the Mac's Settings shows. When that doc changes, change the section's
two `<pre>` blocks to match. Keep `support.html`, `privacy.html` and the
`quick-note-link` id where they are; `check_dayfolio` fails if one goes. The App Store Connect record's privacy,
support and marketing URLs also point into `apps/dayfolio/`, so no page there
moves. The store link, `https://apps.apple.com/app/id6817388897`, is on the
product page and in its Smart App Banner; it answers 404 until the app is
released.

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
  headers. Apple's CDN accepted it anyway on the first deploy (2026-10-13): it
  re-serves the file byte for byte as `application/json` with
  `Apple-Origin-Format: json`. Should a later fetch ever be refused over the
  type, the zone sits behind Cloudflare, so a Response Header Transform Rule
  setting `Content-Type: application/json` for that one path is the fix; not
  moving the file and not giving it an extension. The URL must answer `200`
  directly. Apple does not follow redirects.
- **Checking it** after every change:

  ```sh
  curl -sSI https://ninjaapps.net/.well-known/apple-app-site-association   # 200, no Location
  curl -s   https://ninjaapps.net/.well-known/apple-app-site-association | python3 -m json.tool
  curl -si  https://app-site-association.cdn-apple.com/a/v1/ninjaapps.net  # what iOS will see
  ```

  Devices read Apple's CDN copy, not the site. Two CDNs answer for it (Akamai,
  `23.196.227.x`, and Fastly, `151.101.x.x`), each with its own cache. A failed
  fetch is cached for an hour (`cache-control: max-age=3600`) and the response
  says why in `apple-failure-reason`. What the first deploy (2026-10-13)
  showed: Akamai had the file about two minutes after the deploy finished and
  kept it through its hourly refresh. Fastly held a 404, cached by a probe made
  before the file existed, then a `503 Service Unavailable` from this site that
  could not be reproduced (Cloudflare was reporting incidents that day), and
  took the file on its next fetch, an hour later. A bad answer from one edge is
  therefore not a verdict on the file: pin each edge with
  `curl -si --resolve app-site-association.cdn-apple.com:443:<ip> https://app-site-association.cdn-apple.com/a/v1/ninjaapps.net`
  and wait out the hour. Do not probe the CDN before the file is live. While building the app side, `applinks:ninjaapps.net?mode=developer`
  skips the CDN on a development-signed build, on a device with Settings →
  Developer → Associated Domains Development switched on.

## Tracking

None, and `check-site.py` keeps it that way (`check_no_trackers`): no analytics,
no cookies, no third-party request, no form, and no inline script that talks to
the network or stores anything. The one thing kept on a visitor's device is the
light/dark choice (`ninjaapps-theme` in `localStorage`, written by
`assets/theme.js`). GitHub Pages logs visitor IP addresses for security, and the
privacy policy says we cannot see those logs.

What this repo does not control is the zone in front of it. The domain is
proxied by Cloudflare. Its Email Address Obfuscation rewrites every email address
in a page into an encoded link and injects its own same-origin
`/cdn-cgi/scripts/…/email-decode.min.js`: not analytics, but without JavaScript
the press and support pages show "[email protected]" instead of the address. That
is a zone setting (Scrape Shield), not a file here. Cloudflare Web Analytics, if
it were ever switched on, would inject a beacon into every HTML page with no
commit to this repo, so the live check is
`curl -s https://ninjaapps.net/ | grep -i beacon` (empty today).

## Assets

Dayfolio (`apps/dayfolio/`) is on iPhone, iPad and Mac, but its pictures are still
the Mac's: four 1440×900 desktop captures (WebP with alpha, 1200px wide,
`shot-*.webp`) laid out two across by `.grid-2` + `figure.shot`, under a note that
says so. The library picture (`shot-library.webp`) is no longer used, because it
shows 74 templates and the app has 75 in 16 packs; the file stays on disk for
whoever re-shoots it. There are no iPhone or iPad pictures yet: add them as a
second `.grid` when the App Store set (the captioned, light pictures) is accepted,
not from the catalogue PNGs. Its App Store button is a plain `.btn` to
`https://apps.apple.com/app/id6817388897`, with the Smart App Banner in the page's
head, as Smalti's.

`apps/dayfolio/archive-format.html` is **generated**, never edited. The Dayfolio
repo's `docs/dayfolio-archive-format.md` is the source (its tests keep it true to
the code); regenerate the page with

```sh
python3 tools/archive-page.py /path/to/dayfolio/docs/dayfolio-archive-format.md
```

and commit the result. The tool is standard library only; it reads the page's
header, footer and head from `apps/dayfolio/index.html` and stops, rather than
guesses, at Markdown it does not know. A link to a file that lives only in the
Dayfolio repo (an ADR) is kept as plain text.

Smalti's screenshots are real (WebP, captured 2026-07-20 from the iPhone 16 Pro
Max simulator, 750px wide: `games/smalti/shot-*.webp`). The game has moved on
since: stars and par are gone and the main menu was redesigned, so the set is
due a recapture alongside the 1.2.2 store screenshots.

Smalti's icon is the **shipping medallion**, exported from the app's asset
catalog (`MosaicRush/Assets.xcassets/AppIcon.appiconset` in the game repo:
`AppIcon.png`, `-dark`, `-tinted`) — not from the game repo's `marketing/icon/`
or `marketing/press/icons/`, which held the retired flat-grid mark until they
were replaced. Web copies are lossy WebP (q95): `assets/icon-smalti-144.webp`
(landing card) and `games/smalti/icon-320.webp` (hero, and the daily page).

The press kit, `games/smalti/smalti-press-kit.zip`, keeps one layout:
`README.txt`, `icons/` (1024 / 180 / 60 px × light, dark, tinted — light and dark
opaque RGB, tinted RGBA, resized with Lanczos), `wordmark/`, `screenshots/` and
`smalti-fact-sheet.pdf`. The PDF is the game repo's
`marketing/press/smalti-fact-sheet.html` rendered with headless Chrome the way
that repo renders it (A4, no header or footer, the Google Fonts import dropped so
the Georgia fallback is used, which reproduces its committed PDF pixel for
pixel), with the icon swapped for the medallion. Re-render and re-zip whenever
the sheet or the icon changes; the size quoted on the press page must follow.
`check-site.py` refuses the retired icon, by hash, anywhere on the site and keeps
the kit's layout and icon sizes.

## Dayfolio pages

Every page under `apps/dayfolio/` shares one shell, `render_page` in
`tools/dayfolio-build.py`: the head (title, description, canonical, Open Graph
and Twitter card, JSON-LD, the Smart App Banner), the site header and footer as
the product page has them, and the Dayfolio sub-navigation (Overview, Guide,
Templates, Articles, Support), a band under the header. The guide, template and
article pages are Markdown in `content/dayfolio/<section>/`: each section's
`index.md` is the section page, and every other file a page at
`/apps/dayfolio/<section>/<slug>/`. Front matter, one `name: value` per line
(no quotes, no comments):

```
---
title: Getting started
description: Make your first journal, write today’s page and choose the templates that fit your work.
slug: getting-started
date: 2026-10-20
order: 1
---
```

- `title`: 60 characters at most; the `<title>` adds " — Dayfolio — NinjaApps".
- `description`: 50 to 160 characters, for search results and the social card.
- `slug`: the URL, lowercase words and hyphens. `date`: the day it was published,
  `YYYY-MM-DD`; `updated` is optional. Neither goes on an `index.md`.
- `order`: the reading order, on guide and template pages; articles list newest first.
- Optional: `heading` (the h1, when it says more than the title), and `image` with
  `image_alt` (a social card of the page's own, next to it; the default is
  `social-card.png`).

Pictures live next to the page they are on (`apps/dayfolio/guide/<slug>/`), as WebP
under 500 KB, and the Markdown names them by a relative path:
`![What the picture shows](iphone-today.webp "An optional caption")`. A picture on
a line of its own is a figure (a portrait one is drawn phone-sized), consecutive
picture lines sit side by side, and `> **Tip:** …` is a callout. Links between
pages are relative URLs (`../reports/#billable`). Then

```sh
python3 tools/dayfolio-build.py
```

writes the pages, refreshes the sub-navigation on the hand-written Dayfolio pages,
and rewrites `sitemap.xml` and `robots.txt`; commit what it wrote. It stops,
naming the file and line, at a missing field, a picture with no alt text or not in
WebP, a second h1, or copy against the site's rules: straight quotes (write ’ ‘ “ ”),
exclamation marks, emoji. A generated page names its source in a comment at its
top; a page whose source is gone is removed by the next build.

`check-site.py` holds every Dayfolio page, generated or not, to a unique title and
description, a canonical URL, the banner, a social card (unless noindex), alt text,
one h1 and headings that step down one level at a time, ids used once, tags that
close, JSON-LD that parses, and anchors that exist. The product page's
`SoftwareApplication` JSON-LD must offer what the page states (free, and
`DAYFOLIO_PRICES`), with no ratings or reviews. The social card is a screenshot of
`assets/brand/dayfolio-card.html`:

```sh
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new \
  --hide-scrollbars --window-size=1200,630 --virtual-time-budget=5000 \
  --screenshot=apps/dayfolio/social-card.png "file://$PWD/assets/brand/dayfolio-card.html"
```

## Placeholder inventory (TODO)

- One striped box (`.ph`) left: the hero art / studio mark on the landing page.
- Smalti's App Store button is live (id `6792641328`). `.btn-quiet` and the
  `games/_template/` placeholder stay for the next app — search `TODO`.
- Dayfolio's App Store button (id `6817388897`) is wired and answers 404 until
  the app is released; the product page has no iPhone or iPad pictures yet (see
  Assets). `.btn-quiet` is no longer used on it.
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

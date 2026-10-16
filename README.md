# ninjaapps.net

Static site for **NinjaApps** — games and apps for iPhone, iPad and Mac. Design: "Paper Dojo"
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
apps/dayfolio/archive-format.html   the .dayfolio file format, generated (see Dayfolio)
apps/dayfolio/privacy-v1.0.html     version 1.0 of the policy, archived (noindex);
apps/dayfolio/terms-v1.0.html       the same for the terms
apps/dayfolio/media/                the product page's pictures and the iPhone app preview (see Assets)
games/_template/             copy this to add a new app
assets/brand/                brand exports + the two banner .html sources
tools/check-site.py          structural checks — run before every commit
tools/archive-page.py        regenerates apps/dayfolio/archive-format.html from the app repo's doc
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

`check_dayfolio_media` holds the product page's pictures and film: at least one
`media/iphone-…`, `ipad-…` and `mac-….webp`, each with alt text and the width and
height it really is; none of the retired dark Mac captures, or the note that
excused them; and one `<video>` of `media/app-preview-iphone.mp4` that has
controls, is muted and plays inline over a poster frame, never by itself. The
film must be an MP4 whose `moov` box comes before its media, so it plays while it
downloads. The link check follows `poster` as well as `href` and `src`.

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

One file is fixed the same way. The iPhone app preview,
`https://ninjaapps.net/apps/dayfolio/media/app-preview-iphone.mp4`, is named in
the supplemental materials of Dayfolio's App Store featuring nomination (the app
repo's `docs/buy-listing.md`, D2001, D2091), a link Apple's editors are sent. Keep
the film at that address and replace it in place when the preview is filmed
again; `check_dayfolio_media` fails if it goes.

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

Dayfolio's product page (`apps/dayfolio/`) shows the App Store's captioned, light
pictures across iPhone, iPad and Mac, from the app repo's `build/asc-upload/buy/web/`
(D2091, D2095): `media/iphone-first-page.webp` and `iphone-client-report.webp`
(880×1912, two thirds of 1320×2868), `media/ipad-person.webp` (1032×1376, half of
2064×2752), and `media/mac-performance-review.webp` and `mac-quick-entry.webp`
(1440×900, half of 2880×1800): lossy WebP at quality 90, sRGB. `.devices` lays them
out. On a desktop the two iPhones and the iPad share a row at one height, and the
two Macs the next; narrower, the iPhones pair up and the rest take a row each; on a
phone every picture takes a row, an iPhone's no wider than 300px. They are opaque,
so a hairline frames each instead of the drop shadow a window capture gets. Above
them, the iPhone app preview, `media/app-preview-iphone.mp4` (886×1920, 25.83 s,
H.264 with a silent AAC track, copied byte for byte), plays in a `<video>` with
controls, muted and inline, `preload="none"`, over `media/app-preview-iphone-poster.webp`,
its frame at 3 s. The dark Mac captures (`shot-*.webp`) are gone from the site; git
history has them. To swap a picture, convert the new PNG to the same size and keep
its name, or change the page and its `width` and `height` with it (the checker reads
the WebP's own size). The page links `style.css?v=2026-10-16`, not `style.css`:
Cloudflare serves the stylesheet from its edge cache and tells browsers to keep it
for four hours, so new markup would otherwise meet the old rules (on 2026-10-16 the
film drew at its full 886×1920 until the query was added). Change the date whenever
this page's markup needs a rule `style.css` didn't have. Its App Store button is a plain `.btn` to
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

## Placeholder inventory (TODO)

- One striped box (`.ph`) left: the hero art / studio mark on the landing page.
- Smalti's App Store button is live (id `6792641328`). `.btn-quiet` and the
  `games/_template/` placeholder stay for the next app — search `TODO`.
- Dayfolio's App Store button (id `6817388897`) is wired and answers 404 until
  the app is released. `.btn-quiet` is no longer used on it.
- `support@ninjaapps.net` must be a live mailbox before submission; the
  support page promises a 24–48 h reply.

## Local preview

```sh
python3 -m http.server 8000   # then open http://localhost:8000
```

Pages also open fine directly from disk (`file://`) except `404.html`,
which uses absolute paths (it can be served from any URL).

To look at a page at a phone's width from the command line, mind that headless
Chrome never makes its window narrower than 500px: `--window-size=390,1800` lays
the page out 500px wide and crops the picture to 390, so a phone layout looks cut
off when it isn't. Draw the page in an iframe that is 390px wide instead, with
site isolation off so the frame's lazy pictures load before the shot is taken:

```sh
printf '<body style="margin:0"><iframe src="%s" style="border:0;width:390px;height:9000px"></iframe>' \
  https://ninjaapps.net/apps/dayfolio/ > /tmp/frame.html
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new \
  --user-data-dir="$(mktemp -d)" --hide-scrollbars --window-size=500,9000 \
  --disable-site-isolation-trials --disable-features=IsolateOrigins,site-per-process \
  --blink-settings=preferredColorScheme=1 --virtual-time-budget=15000 \
  --screenshot=/tmp/phone.png file:///tmp/frame.html
```

The shot is 500px wide; its left 390px are the phone. `preferredColorScheme=1` asks
for the light theme and `0` for the dark one; without it the page follows the Mac's
appearance.

## Theme

Light/dark toggle persists in `localStorage` (`ninjaapps-theme`); first visit
follows `prefers-color-scheme`. A blocking snippet in each `<head>` sets
`data-theme` before paint to avoid flashing.

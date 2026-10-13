#!/usr/bin/env python3
"""Structural checks for ninjaapps.net.

No build step means no compiler to catch a dead link after a page is renamed
or deleted. This script is the substitute: run it before every commit.

    python3 tools/check-site.py

Checks:
  1. Every page the site promises to publish exists (MANIFEST below).
  2. Pages that were deliberately removed stay removed.
  3. No unreplaced {{TOKEN}} or <CONFIRM ...> placeholders outside _template/.
  4. Every internal href/src resolves to a file on disk.
  5. sitemap.xml and the published pages agree, both directions.
  6. Each page's <link rel="canonical"> matches its own path.
  7. Smalti's privacy policy exists in every App Store language, with a
     matching lang attribute and a complete set of hreflang alternates.
  8. The URLs baked into the Smalti binary resolve to real pages.
  9. Every page's footer carries the same social row, in the same order,
     and the landing page's sameAs agrees with it.
 10. Universal links: the apple-app-site-association file is publishable,
     parses, names the Smalti app, and matches the daily share path (with and
     without the trailing slash) and nothing broader.
 11. The daily share page keeps its contract: static, nothing requested
     off-origin, nothing stored or sent by its script, a social card whose
     image exists.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import urldefrag, urlparse

ROOT = Path(__file__).resolve().parent.parent
ORIGIN = "https://ninjaapps.net"

# Pages the site commits to publishing.
#
# Legal versioning (see README): the canonical privacy/terms URL always
# serves the LATEST version. When substance changes, snapshot the outgoing
# page as e.g. games/smalti/privacy-v1.0.html (noindex, out of the sitemap),
# link it from the canonical page's Version history section, and add it HERE
# so its continued existence is enforced. Never retro-edit a published
# version's substance in place.
MANIFEST = [
    "index.html",
    "404.html",
    "privacy/index.html",
    "games/smalti/index.html",
    "games/smalti/privacy.html",
    "games/smalti/terms.html",
    "games/smalti/support.html",
    "games/smalti/press.html",
    "games/smalti/daily/index.html",
    "apps/dayfolio/index.html",
    "apps/dayfolio/privacy.html",
    "apps/dayfolio/terms.html",
    "apps/dayfolio/support.html",
    *(f"games/smalti/privacy-{s}.html" for s in (
        "de", "es", "fr", "it", "ja", "ko", "pl", "pt-br", "ru", "tr", "zh-hans",
    )),
]

# Smalti's privacy policy, per App Store Connect localization. ASC requires a
# Privacy Policy URL on EVERY localization of the app record, not just English,
# and blocks review until each one is filled — so each of these pages is a
# submission dependency, not a nicety. `hreflang code -> page`; English is also
# x-default. Adding an App Store language means adding a page here.
LOCALIZED_PRIVACY = {
    "en": "games/smalti/privacy.html",
    "de": "games/smalti/privacy-de.html",
    "es-ES": "games/smalti/privacy-es.html",
    "fr": "games/smalti/privacy-fr.html",
    "it": "games/smalti/privacy-it.html",
    "ja": "games/smalti/privacy-ja.html",
    "ko": "games/smalti/privacy-ko.html",
    "pl": "games/smalti/privacy-pl.html",
    "pt-BR": "games/smalti/privacy-pt-br.html",
    "ru": "games/smalti/privacy-ru.html",
    "tr": "games/smalti/privacy-tr.html",
    "zh-Hans": "games/smalti/privacy-zh-hans.html",
}

# Placeholder apps removed 2026-07-19. Guard against a copy-paste revival.
REMOVED = [
    "apps/shadow-dash",
    "apps/kunai-drop",
    "apps/tatami-trials",
    "apps/focus-dojo",
    "apps/scanblade",
    "games/shadow-dash",
    "games/kunai-drop",
    "games/tatami-trials",
    "games/focus-dojo",
    "games/scanblade",
]

# Hardcoded in the Smalti binary (MosaicRush/UI/Components.swift, enum AppLinks).
# Changing either side without the other ships a dead legal link to App Review.
BAKED_IN_URLS = [
    f"{ORIGIN}/games/smalti/privacy.html",
    f"{ORIGIN}/games/smalti/terms.html",
    # ASC's support field needs a web page; the in-app link is a mailto.
    f"{ORIGIN}/games/smalti/support.html",
    # Self-hosted remote config: every installed copy of Smalti fetches this
    # (SelfHostedRemoteConfig.swift). Moving or deleting it silently pins all
    # installs to their shipped defaults forever.
    f"{ORIGIN}/games/smalti/config/v1.json",
    # The daily share link, https://ninjaapps.net/games/smalti/daily/?d=YYYY-MM-DD
    # (REVIEW_RESPONSE_PLAN_2026-10-13 item 15, shipping in 1.2.2). Every link a
    # player ever shares points here, forever; the AASA file below is what makes
    # an installed Smalti open it instead of this page.
    f"{ORIGIN}/games/smalti/daily/",
]

# Universal links for that share link. iOS reads this file (through Apple's
# CDN) once an app declares applinks:ninjaapps.net in its entitlements.
APP_ID = "745BCAQCQ4.net.ninjaapps.games.mosaicrush"  # team id . bundle id (project.yml)
AASA = ".well-known/apple-app-site-association"
DAILY_PAGE = "games/smalti/daily/index.html"
DAILY_PATH = "/games/smalti/daily/"

# The studio's profiles, in the order every footer lists them. The order is a
# judgement about the channels, not alphabetical: YouTube and Instagram carry
# the trailer and finished-artwork material the games are actually sold on,
# TikTok is the widest-reach discovery channel, and X is mostly press and dev
# community. It lives here because reordering it means reordering the footer on
# every page, and a footer that disagrees with its neighbours is the failure
# mode this catches. `label -> profile URL`; the label is the accessible name.
SOCIAL = [
    ("YouTube", "https://www.youtube.com/@NinjaAppsnet"),
    ("Instagram", "https://www.instagram.com/ninjaappsnet/"),
    ("TikTok", "https://www.tiktok.com/@ninjaapps"),
    ("X", "https://x.com/NinjaAppsnet"),
]

# The template is meant to keep its placeholders. assets/brand/ holds the two
# banner sources — 1500x500 and 2560x1440 pages that exist to be screenshotted
# into PNGs, never linked and never served as pages, so the canonical and
# sitemap rules below do not apply to them.
EXEMPT_DIRS = {"games/_template", "apps/_template", "assets/brand"}

errors: list[str] = []


def fail(msg: str) -> None:
    errors.append(msg)


def is_exempt(path: Path) -> bool:
    rel = path.relative_to(ROOT).as_posix()
    return any(rel.startswith(d + "/") for d in EXEMPT_DIRS)


def published_pages() -> list[Path]:
    return sorted(
        p for p in ROOT.rglob("*.html")
        if ".git" not in p.parts and not is_exempt(p)
    )


def url_for(page: Path) -> str:
    rel = page.relative_to(ROOT).as_posix()
    return f"{ORIGIN}/{rel[:-len('index.html')] if rel.endswith('index.html') else rel}"


def check_manifest() -> None:
    for rel in MANIFEST:
        if not (ROOT / rel).is_file():
            fail(f"manifest: missing page {rel}")


def check_removed() -> None:
    for rel in REMOVED:
        if (ROOT / rel).exists():
            fail(f"removed: {rel} is back on disk")


def check_placeholders() -> None:
    for page in published_pages():
        text = page.read_text(encoding="utf-8")
        rel = page.relative_to(ROOT).as_posix()
        for token in set(re.findall(r"\{\{[A-Z0-9_]+\}\}", text)):
            fail(f"placeholder: {rel} still has {token}")
        if "<CONFIRM" in text or "&lt;CONFIRM" in text:
            fail(f"placeholder: {rel} still has a <CONFIRM ...> marker")


def check_links() -> None:
    pattern = re.compile(r'(?:href|src)\s*=\s*"([^"]+)"')
    for page in published_pages():
        rel = page.relative_to(ROOT).as_posix()
        for raw in pattern.findall(page.read_text(encoding="utf-8")):
            target, _ = urldefrag(raw)
            if not target or urlparse(target).scheme or target.startswith("//"):
                continue  # external, mailto:, data:, or a same-page anchor
            base = ROOT if target.startswith("/") else page.parent
            resolved = (base / target.lstrip("/")).resolve()
            if resolved.is_dir():
                resolved = resolved / "index.html"
            if not resolved.is_file():
                fail(f"dead link: {rel} -> {raw}")


def is_noindex(page: Path) -> bool:
    return 'name="robots" content="noindex"' in page.read_text(encoding="utf-8")


def check_sitemap() -> None:
    sitemap = ROOT / "sitemap.xml"
    if not sitemap.is_file():
        fail("sitemap: sitemap.xml is missing")
        return
    listed = set(re.findall(r"<loc>([^<]+)</loc>", sitemap.read_text(encoding="utf-8")))
    # noindex pages (404, archived legal versions like privacy-v1.0.html)
    # deliberately stay out of the sitemap — and must not sneak into it.
    indexable = {url_for(p) for p in published_pages() if not is_noindex(p)}
    noindexed = {url_for(p) for p in published_pages() if is_noindex(p)}
    for url in sorted(listed - indexable):
        if url in noindexed:
            fail(f"sitemap: lists {url}, which is noindex")
        else:
            fail(f"sitemap: lists {url}, which has no page on disk")
    for url in sorted(indexable - listed):
        fail(f"sitemap: {url} is published but not listed")


def check_canonicals() -> None:
    pattern = re.compile(r'<link\s+rel="canonical"\s+href="([^"]+)"')
    for page in published_pages():
        if page.name == "404.html":
            continue
        rel = page.relative_to(ROOT).as_posix()
        found = pattern.search(page.read_text(encoding="utf-8"))
        if not found:
            fail(f"canonical: {rel} has no <link rel=canonical>")
        elif found.group(1) != url_for(page):
            fail(f"canonical: {rel} points at {found.group(1)}, expected {url_for(page)}")


def check_localized_privacy() -> None:
    """Every translation exists, declares its own language, and points at all
    the others. A half-wired set is worse than none: Google would treat the
    translations as duplicates, and a missing page is a blocked submission."""
    for code, rel in LOCALIZED_PRIVACY.items():
        page = ROOT / rel
        if not page.is_file():
            fail(f"localized privacy: {code} page {rel} is missing")
            continue
        text = page.read_text(encoding="utf-8")

        declared = re.search(r'<html\s+lang="([^"]+)"', text)
        if not declared:
            fail(f"localized privacy: {rel} has no lang on <html>")
        elif declared.group(1) != code:
            fail(f"localized privacy: {rel} declares lang={declared.group(1)}, expected {code}")

        alts = dict(re.findall(
            r'<link\s+rel="alternate"\s+hreflang="([^"]+)"\s+href="([^"]+)"', text))
        expected = {c: f"{ORIGIN}/{p}" for c, p in LOCALIZED_PRIVACY.items()}
        expected["x-default"] = f"{ORIGIN}/{LOCALIZED_PRIVACY['en']}"
        for want, url in expected.items():
            if want not in alts:
                fail(f"localized privacy: {rel} is missing hreflang={want}")
            elif alts[want] != url:
                fail(f"localized privacy: {rel} hreflang={want} points at {alts[want]}, expected {url}")
        for extra in sorted(set(alts) - set(expected)):
            fail(f"localized privacy: {rel} declares unknown hreflang={extra}")


def check_baked_in_urls() -> None:
    for url in BAKED_IN_URLS:
        rel = url[len(ORIGIN) + 1:]
        page = ROOT / rel
        if page.is_dir():
            page = page / "index.html"
        if not page.is_file():
            fail(f"binary URL: {url} does not resolve (Smalti ships this link)")


def check_social() -> None:
    """Every page carries the same social row, in the same order, with the
    marks hidden from screen readers and the link carrying the name. A page
    that quietly falls behind is the whole risk here: nineteen hand-edited
    footers drift, and a visitor on the Korean privacy page gets a different
    set of profiles than one on the landing page."""
    for page in published_pages():
        rel = page.relative_to(ROOT).as_posix()
        text = page.read_text(encoding="utf-8")
        footer = re.search(r"<footer>(.*?)</footer>", text, re.S)
        if not footer:
            fail(f"social: {rel} has no <footer>")
            continue
        block = footer.group(1)

        nav = re.search(r'<nav class="social" aria-label="[^"]+">(.*?)</nav>', block, re.S)
        if not nav:
            fail(f"social: {rel} footer has no labelled <nav class=social>")
            continue

        links = re.findall(
            r'<a href="([^"]+)"[^>]*\saria-label="([^"]+)"', nav.group(1))
        want = [(url, label) for label, url in SOCIAL]
        if links != want:
            fail(f"social: {rel} lists {links}, expected {want}")

        # A visible platform mark next to a link that already says "YouTube"
        # is announced twice unless the mark opts out.
        marks = re.findall(r"<svg[^>]*>", nav.group(1))
        if len(marks) != len(SOCIAL):
            fail(f"social: {rel} has {len(marks)} marks for {len(SOCIAL)} links")
        for mark in marks:
            if 'aria-hidden="true"' not in mark:
                fail(f"social: {rel} has an <svg> mark that is not aria-hidden")


def check_same_as() -> None:
    """The landing page's Organization sameAs is how a search engine learns
    that these four profiles and this domain are one studio. It only works
    while it agrees with the footer."""
    page = ROOT / "index.html"
    found = re.search(
        r'<script type="application/ld\+json">(.*?)</script>',
        page.read_text(encoding="utf-8"), re.S)
    if not found:
        fail("sameAs: index.html has no application/ld+json block")
        return
    import json
    try:
        data = json.loads(found.group(1))
    except json.JSONDecodeError as exc:
        fail(f"sameAs: index.html ld+json does not parse ({exc})")
        return
    if data.get("sameAs") != [url for _, url in SOCIAL]:
        fail(f"sameAs: index.html lists {data.get('sameAs')}, "
             f"expected {[url for _, url in SOCIAL]}")


def aasa_matches(pattern: str, path: str) -> bool:
    """Apple's path pattern: `*` is zero or more characters, `?` exactly one,
    anchored at both ends. (The `$(alpha)`-style variables are not used here.)"""
    rx = "".join(".*" if c == "*" else "." if c == "?" else re.escape(c) for c in pattern)
    return re.fullmatch(rx, path) is not None


def aasa_components_allow(components: list, path: str) -> bool:
    """iOS 13+ format: the first component whose `/` pattern matches decides;
    `exclude` turns a match into a refusal."""
    for comp in components:
        pattern = comp.get("/")
        if pattern is None or aasa_matches(pattern, path):
            return not comp.get("exclude", False)
    return False


def aasa_paths_allow(paths: list, path: str) -> bool:
    """Pre-iOS-13 format: first match wins; a `NOT ` prefix is a refusal."""
    for entry in paths:
        refuse = entry.startswith("NOT ")
        if aasa_matches(entry[4:] if refuse else entry, path):
            return not refuse
    return False


# What the daily share path must and must not cover. The negatives matter as
# much: a pattern that quietly grows to /games/smalti/* would hand the privacy
# policy and the support page to the app, which cannot show them.
AASA_OPENS = [DAILY_PATH.rstrip("/"), DAILY_PATH, f"{DAILY_PATH}index.html"]
AASA_LEAVES = [
    "/", "/games/smalti/", "/games/smalti/privacy.html", "/games/smalti/support.html",
    "/games/smalti/press.html", "/games/smalti/dailyx", "/games/smalti/daily-archive/",
    "/apps/dayfolio/",
]


def check_aasa() -> None:
    # A Jekyll build drops dot-directories; .nojekyll is what lets GitHub Pages
    # publish /.well-known at all.
    if not (ROOT / ".nojekyll").is_file():
        fail("aasa: .nojekyll is missing, so GitHub Pages would not publish /.well-known")
    path = ROOT / AASA
    if not path.is_file():
        fail(f"aasa: {AASA} is missing (exact name, no extension)")
        return
    raw = path.read_bytes()
    if len(raw) > 128 * 1024:
        fail("aasa: file is over Apple's 128 KB limit")
    try:
        data = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        fail(f"aasa: {AASA} is not valid JSON ({exc})")
        return

    # Guard the matcher itself, so a bug in it cannot wave a wrong file through.
    probe = [("/a/*", "/a/", True), ("/a/*", "/a", False), ("/a/*", "/a/b/c", True),
             ("/a", "/a/", False), ("/a?c", "/abc", True), ("/a?c", "/ac", False)]
    for pattern, sample, want in probe:
        if aasa_matches(pattern, sample) != want:
            fail(f"aasa: internal matcher is wrong for {pattern!r} vs {sample!r}")

    details = data.get("applinks", {}).get("details") if isinstance(data, dict) else None
    if not isinstance(details, list) or not details:
        fail("aasa: applinks.details is missing or empty")
        return
    modern = legacy = 0
    for detail in details:
        ids = detail.get("appIDs", [detail["appID"]] if "appID" in detail else [])
        if ids != [APP_ID]:
            fail(f"aasa: a details entry names {ids}, expected exactly [{APP_ID!r}]")
        if "components" in detail:
            modern += 1
            allow = lambda p, d=detail: aasa_components_allow(d["components"], p)
        elif "paths" in detail:
            legacy += 1
            allow = lambda p, d=detail: aasa_paths_allow(d["paths"], p)
        else:
            fail("aasa: a details entry has neither components nor paths")
            continue
        kind = "components" if "components" in detail else "paths"
        for sample in AASA_OPENS:
            if not allow(sample):
                fail(f"aasa: {kind} do not open the app for {sample}")
        for sample in AASA_LEAVES:
            if allow(sample):
                fail(f"aasa: {kind} are too broad: they also open the app for {sample}")
    if not modern:
        fail("aasa: no components entry (the iOS 13+ format; Smalti requires iOS 17)")


def check_daily_page() -> None:
    page = ROOT / DAILY_PAGE
    if not page.is_file():
        fail(f"daily: {DAILY_PAGE} is missing")
        return
    text = page.read_text(encoding="utf-8")

    # Nothing the page loads may come from another origin: the app's privacy
    # label is "Data Not Collected", and a stranger's first contact with Smalti
    # must not hand their address to a third party. Outbound <a> links are fine.
    fetch_rel = re.compile(
        r"stylesheet|icon|preload|prefetch|preconnect|dns-prefetch|modulepreload|manifest", re.I)
    for tag in re.finditer(r"<(script|img|iframe|source|video|audio|embed|object|link)\b([^>]*)>",
                           text, re.I):
        name, attrs = tag.group(1).lower(), tag.group(2)
        rel = re.search(r'\brel="([^"]*)"', attrs)
        if name == "link" and not (rel and fetch_rel.search(rel.group(1))):
            continue
        for attr in re.findall(r'\b(?:src|href|data|poster)="([^"]*)"', attrs):
            if re.match(r"(?:https?:)?//", attr):
                fail(f"daily: <{name}> loads {attr}, which is off-origin")
    for style in re.findall(r"<style\b[^>]*>(.*?)</style>|\bstyle=\"([^\"]*)\"", text, re.S):
        if re.search(r"@import|url\(\s*['\"]?(?:https?:)?//", "".join(style)):
            fail("daily: a style rule requests something off-origin")

    # Inline scripts may format a date and nothing else: no network, no cookies,
    # no storage of their own (the sitewide theme snippet only reads storage).
    for script in re.findall(r"<script\b(?![^>]*\bsrc=)[^>]*>(.*?)</script>", text, re.S | re.I):
        if "ninjaapps-theme" in script:
            continue  # the shared pre-paint theme snippet, identical on every page
        for banned in (r"fetch\s*\(", r"XMLHttpRequest", r"sendBeacon", r"new\s+Image\b",
                       r"document\.cookie", r"localStorage", r"sessionStorage", r"indexedDB",
                       r"WebSocket", r"EventSource", r"import\s*\("):
            if re.search(banned, script):
                fail(f"daily: the inline script uses {banned}")

    required = [
        "https://apps.apple.com/app/id6792641328",
        "A calm daily mosaic puzzle. No ads, no account, no data collected.",
        "Get Smalti on the App Store",
        "Already have it?",
        "Open today",
    ]
    for need in required:
        if need.lower() not in text.lower():
            fail(f"daily: the page does not say {need!r}")
    for meta in (r'property="og:title"', r'property="og:description"', r'property="og:image"',
                 r'property="og:url"', r'name="twitter:card"', r'name="description"',
                 r'name="apple-itunes-app" content="app-id=6792641328'):
        if not re.search(rf"<meta\s+{meta}", text):
            fail(f"daily: missing <meta {meta}>")
    if re.search(r'name="robots"[^>]*noindex', text):
        fail("daily: the share page must stay indexable (it is in the sitemap)")


def check_social_cards() -> None:
    """A card whose image 404s is worse than no card: every chat app that
    unfurls the link shows a broken box."""
    for page in published_pages():
        rel = page.relative_to(ROOT).as_posix()
        text = page.read_text(encoding="utf-8")
        for url in re.findall(
                r'<meta\s+(?:property="og:image"|name="twitter:image")\s+content="([^"]+)"', text):
            if not url.startswith(ORIGIN + "/"):
                fail(f"social card: {rel} points its image off-origin: {url}")
            elif not (ROOT / url[len(ORIGIN) + 1:]).is_file():
                fail(f"social card: {rel} image {url} is not on disk")


def main() -> int:
    for check in (
        check_manifest,
        check_removed,
        check_placeholders,
        check_links,
        check_sitemap,
        check_canonicals,
        check_localized_privacy,
        check_baked_in_urls,
        check_social,
        check_same_as,
        check_aasa,
        check_daily_page,
        check_social_cards,
    ):
        check()

    if errors:
        print(f"FAIL — {len(errors)} problem(s):\n")
        for err in errors:
            print(f"  · {err}")
        return 1

    print(f"OK — {len(published_pages())} pages, no problems found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

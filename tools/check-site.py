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
 11. The daily share page keeps its contract: it says what the app promises
     and carries a social card whose image exists.
 12. The Smalti marketing pages carry no claim the app has retired, and do
     carry the catalog numbers the code defines (CATALOG below).
 13. The press kit zip keeps its layout and the retired flat-grid icon ships
     nowhere (kit, hero, landing card).
 14. No page loads anything from another origin, posts a form, or runs an
     inline script that talks to the network or stores anything: the site has
     no analytics, trackers or cookies, and must not get any.
 15. Dayfolio's pages say what the app does: the five prices, the App Store
     link and Smart App Banner, the refund sentence, the free tier and the
     anchors the app opens, and none of the claims the first copy made
     ($9.99, "coming soon", the "Mac App Store"). The privacy policy and terms
     name their version and link the archived one. The URLs the app opens
     (/apps/dayfolio/support, /privacy, /support#quick-note-link) resolve.
"""

from __future__ import annotations

import hashlib
import json
import re
import struct
import sys
import zipfile
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
    "apps/dayfolio/archive-format.html",
    # Dayfolio's published version 1.0 of each (README: Legal page versioning).
    "apps/dayfolio/privacy-v1.0.html",
    "apps/dayfolio/terms-v1.0.html",
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

# What the app's code says the catalog is (Model/Content.swift Catalog: 411
# journey levels in 10 Rooms; Tunables.freeFourPieceLevels = 5 puts the free
# band at 40). The copy below is checked against these, not the other way round.
CATALOG = {"levels": 411, "rooms": 10, "free": 40}

# Pages whose copy describes the shipping game. The published privacy policy and
# terms are deliberately NOT here: they are versioned, never retro-edited (README,
# "Legal page versioning"), so any claim they carry that the app has since retired
# is fixed by a new version, not by this list.
MARKETING_PAGES = [
    "index.html",
    "games/smalti/index.html",
    "games/smalti/press.html",
    "games/smalti/support.html",
    DAILY_PAGE,
]

# Claims the app no longer makes, or never made. A hit means the copy drifted
# from the code again. `(?i)` patterns ignore case; the rest are exact. An
# optional third item lists pages the rule does not apply to.
STALE_CLAIMS = [
    (r"\b395\b",
     "the catalog is 411 levels in 10 Rooms (395 is the nine-Room ascent without The Heirloom Set)"),
    (r"(?i)\b(?:nine|9)\s+packs?\b", "10 Rooms"),
    (r"(?i)(?<!hint )\bpacks?\b",
     "the player-facing word is Room (CONTEXT.md); only hint packs keep the word"),
    (r"(?i)masterpiece commission", "say Commission"),
    (r"(?i)hand-?crafted|handmade",
     "levels are generated and the reward art is AI-generated (docs/asset-provenance.md): never claim hand-made"),
    (r"(?i)leaderboards|depth board",
     "claim no leaderboards: the daily boards were removed 2026-09-12, and the one board the "
     "game still submits to (Daily Excavation depth) has no in-game screen"),
    (r"\bTBD\b", "Smalti has been on the App Store since August 2026"),
    # The landing page also introduces Dayfolio, which is an iPhone, iPad and Mac app.
    (r"\biPad\b", "no iPad promise or date (TARGETED_DEVICE_FAMILY = 1)", ("index.html",)),
    (r"(?i)two attempts|attempts? left", "the daily has been unmetered since 2026-09-12"),
    (r"(?i)\bfifty-one\b|\b51 (?:journey )?levels", "the free band is 40 levels"),
    (r"\bAtelier Endless\b|\bEndless\b", "the mode is called Daily Excavation"),
    (r"(?i)streak freezes?|\bfreezes\b",
     "streak freezes retire in 1.2.2; promise or deny nothing until it ships"),
    (r"(?i)premium unlock|honest premium", "the player-facing word is the Unlock (CONTEXT.md)"),
]

# Numbers the pages must state, so a fix that only deletes the old claim and
# never states the new one is caught too.
REQUIRED_FACTS = {
    "index.html": [f"{CATALOG['levels']} levels"],
    "games/smalti/index.html": [
        f"{CATALOG['levels']} levels", f"{CATALOG['rooms']} Rooms",
        f"{CATALOG['free']} journey levels",
    ],
    "games/smalti/press.html": [
        f"{CATALOG['levels']} levels", f"{CATALOG['rooms']} Rooms",
        f"{CATALOG['rooms']} Commissions", f"{CATALOG['free']} journey levels",
        "August 2026",
    ],
}

# Dayfolio (apps/dayfolio/) is one App Store record for iPhone, iPad and Mac. Its
# pages are held to the app's own decisions, not to the first copy: the five
# purchases and their US prices are D223-D225 (docs/product-spec.md §3.7b in the
# app repo), the free tier is D224 as changed by D1623 and D1624, and the website
# brief is D1625. The privacy policy and terms are versioned like Smalti's: the
# canonical page serves the latest, the archived ones are only held to exist,
# stay out of the index and link back.
DAYFOLIO_DIR = "apps/dayfolio"
DAYFOLIO_STORE_ID = "6817388897"
DAYFOLIO_STORE_URL = f"https://apps.apple.com/app/id{DAYFOLIO_STORE_ID}"
DAYFOLIO_PRICES = ["$7.99", "$19.99", "$24.99", "$4.99", "$16.99"]
DAYFOLIO_MARKETING = ["index.html", "support.html", "privacy.html", "terms.html"]

DAYFOLIO_STALE_CLAIMS = [
    (r"\$9\.99", "the first copy's Mac price; the purchases are $7.99, $19.99 and $24.99, with two upgrades (D225)"),
    (r"(?i)coming soon", "Dayfolio links the App Store (D1625)"),
    (r"(?i)mac app store", "one App Store record serves iPhone, iPad and Mac"),
    (r"(?i)\b(?:premium|pro version|dayfolio pro)\b",
     "the glossary's word is the purchase, or the full version (CONTEXT.md, Purchase)"),
    (r"(?i)\b(?:free trial|trial period|lite version|demo version)\b",
     "the free version is the Free tier, not a trial (CONTEXT.md, Free tier)"),
]

# What each page must still say. A rewrite that only deletes the old claim and
# never states the new one is caught too. Plain substrings, case-sensitive.
DAYFOLIO_REQUIRED = {
    "index.html": [
        *DAYFOLIO_PRICES,
        DAYFOLIO_STORE_URL,
        f'<meta name="apple-itunes-app" content="app-id={DAYFOLIO_STORE_ID}">',
        "https://reportaproblem.apple.com",
        "one journal and 100 entries",
        "Buy Dayfolio for iPhone and iPad, for Mac, or for all three; "
        "if you own one, the other is an upgrade at the difference",
        'id="price"',
        'href="archive-format.html"',
    ],
    "support.html": [
        *DAYFOLIO_PRICES,
        "Restore purchases",
        "Not what you need? Apple handles refunds at",
        "https://reportaproblem.apple.com",
        'href="archive-format.html"',
        *(f'id="{anchor}"' for anchor in (
            "free-version", "prices", "upgrades", "restore-purchases", "refunds", "archive",
            "mirror-folder", "quick-note-link", "shortcuts", "widgets", "share", "spotlight",
            "handoff", "reminders", "reports")),
    ],
    "privacy.html": [
        "VERSION 1.1",
        "Dayfolio collects nothing",
        'href="privacy-v1.0.html"',
        'id="version-history"',
        # A paragraph per permission and system feature (D1625), plus iCloud and the two Mac features.
        *(f'id="{anchor}"' for anchor in (
            "icloud", "location", "calendar", "camera", "microphone", "notifications", "siri-shortcuts",
            "spotlight", "widgets", "share-extension", "handoff", "focus", "ai", "mirror-folder",
            "quick-note-link")),
        "Advanced Data Protection",
    ],
    "terms.html": ['href="terms-v1.0.html"'],
}

# The landing page and the privacy hub carry a line about Dayfolio too. They are not Dayfolio's pages, so only what
# the first copy got wrong is held against them, and what they must now say.
DAYFOLIO_ELSEWHERE_STALE = DAYFOLIO_STALE_CLAIMS + [
    (r"(?i)\bfor (?:the|your) mac\b", "Dayfolio is on iPhone, iPad and Mac"),
    (r"(?i)\bmac apps\b", "the studio makes games and apps for iPhone, iPad and Mac"),
]
DAYFOLIO_ELSEWHERE_REQUIRED = {
    "index.html": ["calm work journal for iPhone, iPad and Mac"],
    "privacy/index.html": ["iPhone, iPad and Mac"],
}

# The product page's pictures and video (the app repo's D1843, D2001, D2091, D2095). The pictures are the App Store's
# captioned, light set, `media/<platform>-<what>.webp`, at least one for each platform; the four dark Mac captures they
# replaced, and the note that excused them, stay gone. The iPhone app preview plays on the page, and its address is
# named in the featuring nomination (the app repo's docs/buy-listing.md), so it is as fixed as the addresses the app
# opens: moving the file breaks a link Apple's editors were sent.
DAYFOLIO_MEDIA = f"{DAYFOLIO_DIR}/media"
DAYFOLIO_PREVIEW = f"{DAYFOLIO_MEDIA}/app-preview-iphone.mp4"
DAYFOLIO_PREVIEW_URL = f"{ORIGIN}/{DAYFOLIO_PREVIEW}"
DAYFOLIO_PLATFORMS = ("iphone", "ipad", "mac")
DAYFOLIO_RETIRED_PICTURES = [
    "shot-today.webp", "shot-timeline.webp", "shot-calendar.webp", "shot-insights.webp", "shot-library.webp",
    "dark mode on a Mac",
]

# Pages the app itself opens (Packages/DayfolioKit/.../SettingsOverview.swift `AboutCopy`, HelpMenu.swift).
# GitHub Pages serves /support from support.html, so the app's address has no extension. Each is the page and
# the anchor the app opens on it; losing either ships a dead Help item.
DAYFOLIO_APP_URLS = [
    (f"{ORIGIN}/{DAYFOLIO_DIR}/support", "support.html", None),
    (f"{ORIGIN}/{DAYFOLIO_DIR}/privacy", "privacy.html", None),
    (f"{ORIGIN}/{DAYFOLIO_DIR}/support#quick-note-link", "support.html", "quick-note-link"),
]

# The press kit. Same layout every time it is rebuilt, so a journalist's
# bookmarked unzip path never moves.
PRESS_KIT = "games/smalti/smalti-press-kit.zip"
KIT_ROOT = "smalti-press-kit/"
KIT_FILES = {
    f"{KIT_ROOT}README.txt",
    f"{KIT_ROOT}smalti-fact-sheet.pdf",
    *(f"{KIT_ROOT}icons/smalti-icon-{size}{tone}.png"
      for size in (1024, 180, 60) for tone in ("", "-dark", "-tinted")),
    *(f"{KIT_ROOT}wordmark/smalti-wordmark-{tone}.{ext}"
      for tone in ("light", "dark") for ext in ("png", "svg")),
    *(f"{KIT_ROOT}screenshots/{name}.png" for name in (
        "01-main-menu", "02-gameplay-midlevel", "03-completion-card",
        "04-daily-puzzle", "05-daily-calendar")),
}

# SHA-256 of the flat-grid icon Smalti shipped until 1.0.1 (3x3 plain tiles),
# which was still in the press kit and on the site in October 2026 after the
# binary had moved to the medallion mark. Retired artwork must not come back
# from a stale master: the game repo's marketing/press/icons and marketing/icon
# still hold these same bytes until item 23 of its REVIEW_RESPONSE_PLAN replaces
# them, so re-exporting the kit from there would bring the old mark back.
RETIRED_ICONS_SHA256 = {
    "b34a7ad42e080ba68e34ff12476db6a5b58b126c319dd721950ab1b8c01b5e56",  # kit 1024 dark
    "91615eb6a9f4f5622abddc7bab9db9e236667b4aefe9fd7968e53ded8d63a2d6",  # kit 1024 tinted
    "b746be7fb1a350e6a7f2a795f96e57022c5f2554ce4c31346c53166f4ba51801",  # kit 1024
    "cef7d1f8366b7090c915cc6c268d7e74a5f57d8d3f41caac66b9b3478315a23f",  # kit 180 dark
    "2d7357b4ef5fc7b1b16386bcc18e3d2c92cc6179cc50efc51ed5818a8ec4ef28",  # kit 180 tinted
    "96cedd378ffaccc9619835a13a3ac918b834ef1f230d99a8b871d8b056383932",  # kit 180
    "13d90cb5921963de4ff811978e1ec57e7ad227bdd978f8503130ac364f37f000",  # kit 60 dark
    "f81a6e02aff3732b0a40ec494c9543ea93bbd548e00278544fcd1a6f92c687ff",  # kit 60 tinted
    "5769e2e5b624972af60ba8fc3e78dde4e069bdd0d94765b2de4cb78b035f2c6a",  # kit 60
    "ab0f1f7dd01895821e2a97b0525479b083b6178775f1a479ba074559d4b61ece",  # assets/icon-smalti-144.webp
    "05dbfa00c2834e458b7a0b23618ed443da93eae12710b52ed1a759ac57cb17f4",  # games/smalti/icon-320.webp
}
WEB_ICONS = ["assets/icon-smalti-144.webp", "games/smalti/icon-320.webp"]

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
    pattern = re.compile(r'(?:href|src|poster)\s*=\s*"([^"]+)"')
    for page in published_pages():
        rel = page.relative_to(ROOT).as_posix()
        for raw in pattern.findall(page.read_text(encoding="utf-8")):
            target, _ = urldefrag(raw)
            if not target or urlparse(target).scheme or target.startswith("//"):
                continue  # external, mailto:, data:, or a same-page anchor
            target = target.split("?", 1)[0]  # a cache-busting ?v= names the same file
            if not target:
                continue
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
    modern = 0
    for detail in details:
        if not isinstance(detail, dict):
            fail("aasa: a details entry is not an object")
            continue
        ids = detail.get("appIDs", [detail["appID"]] if "appID" in detail else [])
        if ids != [APP_ID]:
            fail(f"aasa: a details entry names {ids}, expected exactly [{APP_ID!r}]")
        if "components" in detail:
            modern += 1
            allow = lambda p, d=detail: aasa_components_allow(d["components"], p)
        elif "paths" in detail:
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


def check_no_trackers() -> None:
    """The site has no analytics, no trackers, no cookies and no third-party
    requests, and the app's privacy label ("Data Not Collected") is only honest
    while that stays true. So on EVERY page: nothing is loaded from another
    origin (outbound <a> links are fine), no form posts anywhere, and no inline
    script talks to the network or stores anything of its own. The shared theme
    snippet is exempt: it only reads the visitor's saved light/dark choice.
    (assets/theme.js, a same-origin file, writes that one preference.)"""
    fetch_rel = re.compile(
        r"stylesheet|icon|preload|prefetch|preconnect|dns-prefetch|modulepreload|manifest", re.I)
    for page in published_pages():
        rel = page.relative_to(ROOT).as_posix()
        text = page.read_text(encoding="utf-8")
        for tag in re.finditer(
                r"<(script|img|iframe|source|video|audio|embed|object|link)\b([^>]*)>", text, re.I):
            name, attrs = tag.group(1).lower(), tag.group(2)
            link_rel = re.search(r'\brel="([^"]*)"', attrs)
            if name == "link" and not (link_rel and fetch_rel.search(link_rel.group(1))):
                continue
            for attr in re.findall(r'\b(?:src|href|data|poster)="([^"]*)"', attrs):
                if re.match(r"(?:https?:)?//", attr):
                    fail(f"tracking: {rel} loads {attr} from another origin (<{name}>)")
        for style in re.findall(r"<style\b[^>]*>(.*?)</style>|\bstyle=\"([^\"]*)\"", text, re.S):
            if re.search(r"@import|url\(\s*['\"]?(?:https?:)?//", "".join(style)):
                fail(f"tracking: {rel} has a style rule that requests something off-origin")
        if re.search(r"<form\b", text, re.I):
            fail(f"tracking: {rel} has a <form>; the site collects nothing")
        for script in re.findall(r"<script\b(?![^>]*\bsrc=)[^>]*>(.*?)</script>", text, re.S | re.I):
            if "ninjaapps-theme" in script:
                continue  # the shared pre-paint theme snippet, identical on every page
            for banned in (r"fetch\s*\(", r"XMLHttpRequest", r"sendBeacon", r"new\s+Image\b",
                           r"document\.cookie", r"localStorage", r"sessionStorage", r"indexedDB",
                           r"WebSocket", r"EventSource", r"import\s*\("):
                if re.search(banned, script):
                    fail(f"tracking: an inline script on {rel} uses {banned}")


def check_daily_page() -> None:
    page = ROOT / DAILY_PAGE
    if not page.is_file():
        fail(f"daily: {DAILY_PAGE} is missing")
        return
    text = page.read_text(encoding="utf-8")

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


def check_stale_claims() -> None:
    for rel in MARKETING_PAGES:
        page = ROOT / rel
        if not page.is_file():
            continue  # check_manifest reports a missing page
        text = page.read_text(encoding="utf-8")
        for pattern, why, *exempt in STALE_CLAIMS:
            if rel in (exempt[0] if exempt else ()):
                continue
            hits: dict[str, int] = {}
            for hit in re.finditer(pattern, text):
                hits[hit.group(0)] = hits.get(hit.group(0), 0) + 1
            for said, count in sorted(hits.items()):
                times = f" (x{count})" if count > 1 else ""
                fail(f"stale claim: {rel} says {said!r}{times} — {why}")
        for fact in REQUIRED_FACTS.get(rel, []):
            if fact not in text:
                fail(f"stale claim: {rel} no longer states {fact!r}")


def webp_size(data: bytes) -> tuple[int, int] | None:
    """The pixel size a WebP file declares (lossy, lossless or extended), or None if it is not one."""
    if data[:4] != b"RIFF" or data[8:12] != b"WEBP" or len(data) < 30:
        return None
    chunk = data[12:16]
    if chunk == b"VP8X":
        return (int.from_bytes(data[24:27], "little") + 1, int.from_bytes(data[27:30], "little") + 1)
    if chunk == b"VP8 " and data[23:26] == b"\x9d\x01\x2a":
        return (int.from_bytes(data[26:28], "little") & 0x3FFF, int.from_bytes(data[28:30], "little") & 0x3FFF)
    if chunk == b"VP8L" and data[20] == 0x2F:
        bits = int.from_bytes(data[21:25], "little")
        return ((bits & 0x3FFF) + 1, ((bits >> 14) & 0x3FFF) + 1)
    return None


def mp4_boxes(path: Path) -> list[bytes]:
    """The types of an MP4 file's top-level boxes, in file order."""
    boxes = []
    with path.open("rb") as f:
        end = f.seek(0, 2)
        offset = 0
        while offset + 8 <= end:
            f.seek(offset)
            head = f.read(16)
            size, kind = struct.unpack(">I4s", head[:8])
            if size == 1:
                size = struct.unpack(">Q", head[8:16])[0]
            elif size == 0:
                size = end - offset
            if size < 8:
                break
            boxes.append(kind)
            offset += size
    return boxes


def check_dayfolio_media() -> None:
    """The product page shows Dayfolio on each platform it is for (DAYFOLIO_PLATFORMS), every picture with alt
    text and the size it is, none of the retired ones, and plays the iPhone preview the featuring nomination
    links (DAYFOLIO_PREVIEW_URL): with controls, muted and inline, over a poster frame, never by itself."""
    rel = f"{DAYFOLIO_DIR}/index.html"
    page = ROOT / rel
    if not page.is_file():
        return  # check_manifest reports a missing page
    text = page.read_text(encoding="utf-8")
    for retired in DAYFOLIO_RETIRED_PICTURES:
        if retired in text:
            fail(f"dayfolio: {rel} still shows {retired!r}; its pictures are the captioned, light set (D2095)")

    shown: set[str] = set()
    for tag in re.findall(r"<img\b[^>]*>", text):
        src = re.search(r'\bsrc="([^"]*)"', tag)
        name = src.group(1) if src else "?"
        alt = re.search(r'\balt="([^"]*)"', tag)
        if not alt or not alt.group(1).strip():
            fail(f"dayfolio: {rel} shows {name} with no alt text")
        width, height = (re.search(rf'\b{dim}="(\d+)"', tag) for dim in ("width", "height"))
        if not (width and height):
            fail(f"dayfolio: {rel} shows {name} without its width and height")
        picture = re.fullmatch(r"media/(\w+)-[a-z0-9-]+\.webp", name)
        if not picture:
            continue
        if picture.group(1) in DAYFOLIO_PLATFORMS:
            shown.add(picture.group(1))
        file = page.parent / name
        size = webp_size(file.read_bytes()) if file.is_file() else None
        if file.is_file() and size is None:
            fail(f"dayfolio: {DAYFOLIO_DIR}/{name} is not a WebP picture")
        elif size and width and height and size != (int(width.group(1)), int(height.group(1))):
            fail(f"dayfolio: {rel} gives {name} as {width.group(1)}x{height.group(1)}, but it is {size[0]}x{size[1]}")
    for platform in DAYFOLIO_PLATFORMS:
        if platform not in shown:
            fail(f"dayfolio: {rel} shows no {platform} picture (media/{platform}-….webp)")

    videos = re.findall(r"<video\b([^>]*)>(.*?)</video>", text, re.S)
    preview = DAYFOLIO_PREVIEW[len(DAYFOLIO_DIR) + 1:]
    if len(videos) != 1:
        fail(f"dayfolio: {rel} has {len(videos)} <video> elements; it plays the iPhone preview, {preview}, once")
    else:
        attrs, inner = videos[0]
        for need in ("controls", "muted", "playsinline"):
            if not re.search(rf"\b{need}\b", attrs):
                fail(f"dayfolio: {rel}'s <video> is missing {need}")
        if re.search(r"\bautoplay\b", attrs):
            fail(f"dayfolio: {rel}'s <video> plays by itself; a visitor starts it")
        if not re.search(r'\bposter="[^"]+"', attrs):
            fail(f"dayfolio: {rel}'s <video> has no poster frame")
        if preview not in re.findall(r'\bsrc="([^"]+)"', attrs + inner):
            fail(f"dayfolio: {rel}'s <video> does not play {preview}")

    # The file the nomination links: there, an MP4, and playable while it downloads (moov before mdat).
    video = ROOT / DAYFOLIO_PREVIEW
    if not video.is_file():
        fail(f"dayfolio: the featuring nomination links {DAYFOLIO_PREVIEW_URL}, but {DAYFOLIO_PREVIEW} is missing")
    else:
        boxes = mp4_boxes(video)
        if not boxes or boxes[0] != b"ftyp":
            fail(f"dayfolio: {DAYFOLIO_PREVIEW} is not an MP4 file")
        elif b"moov" not in boxes or (b"mdat" in boxes and boxes.index(b"moov") > boxes.index(b"mdat")):
            fail(f"dayfolio: {DAYFOLIO_PREVIEW} keeps its moov box after the media, so it cannot play until it has all downloaded")


def check_dayfolio() -> None:
    """Dayfolio's pages say what the app does (see DAYFOLIO_* above), the archived
    legal versions stay archived, and the addresses the app opens still resolve."""
    check_dayfolio_media()
    for name in DAYFOLIO_MARKETING:
        rel = f"{DAYFOLIO_DIR}/{name}"
        page = ROOT / rel
        if not page.is_file():
            continue  # check_manifest reports a missing page
        text = page.read_text(encoding="utf-8")
        for pattern, why in DAYFOLIO_STALE_CLAIMS:
            hits: dict[str, int] = {}
            for hit in re.finditer(pattern, text):
                hits[hit.group(0)] = hits.get(hit.group(0), 0) + 1
            for said, count in sorted(hits.items()):
                times = f" (x{count})" if count > 1 else ""
                fail(f"dayfolio: {rel} says {said!r}{times}: {why}")
        for need in DAYFOLIO_REQUIRED.get(name, []):
            if need not in text:
                fail(f"dayfolio: {rel} no longer says {need!r}")

    for rel, required in DAYFOLIO_ELSEWHERE_REQUIRED.items():
        page = ROOT / rel
        if not page.is_file():
            continue
        text = page.read_text(encoding="utf-8")
        for pattern, why in DAYFOLIO_ELSEWHERE_STALE:
            for said in sorted({hit.group(0) for hit in re.finditer(pattern, text)}):
                fail(f"dayfolio: {rel} says {said!r}: {why}")
        for need in required:
            if need not in text:
                fail(f"dayfolio: {rel} no longer says {need!r}")

    # The archived versions: published as they were, kept out of the index, and a way back to the current one.
    for name in ("privacy", "terms"):
        archived = ROOT / DAYFOLIO_DIR / f"{name}-v1.0.html"
        if not archived.is_file():
            continue
        text = archived.read_text(encoding="utf-8")
        if not is_noindex(archived):
            fail(f"dayfolio: {name}-v1.0.html must be noindex (an archived version)")
        if f'href="{name}.html"' not in text:
            fail(f"dayfolio: {name}-v1.0.html does not link the current version")

    # The addresses the app opens: the page, and the anchor on it.
    for url, target, anchor in DAYFOLIO_APP_URLS:
        page = ROOT / DAYFOLIO_DIR / target
        if not page.is_file():
            fail(f"dayfolio: the app opens {url}, but {DAYFOLIO_DIR}/{target} is missing")
        elif anchor and f'id="{anchor}"' not in page.read_text(encoding="utf-8"):
            fail(f"dayfolio: the app opens {url}, but {target} has no id={anchor!r}")

    # The archive format page is generated (tools/archive-page.py); if it is missing its title it was hand-edited or broken.
    archive_page = ROOT / DAYFOLIO_DIR / "archive-format.html"
    if archive_page.is_file() and "The Dayfolio archive format" not in archive_page.read_text(encoding="utf-8"):
        fail("dayfolio: archive-format.html no longer carries its title; regenerate it with tools/archive-page.py")


def png_size(data: bytes) -> tuple[int, int] | None:
    if data[:8] != b"\x89PNG\r\n\x1a\n" or data[12:16] != b"IHDR":
        return None
    return struct.unpack(">II", data[16:24])


def check_press_kit() -> None:
    kit = ROOT / PRESS_KIT
    if not kit.is_file():
        fail(f"press kit: {PRESS_KIT} is missing")
        return
    try:
        archive = zipfile.ZipFile(kit)
    except zipfile.BadZipFile:
        fail("press kit: the zip is corrupt")
        return
    with archive:
        if archive.testzip() is not None:
            fail("press kit: the zip fails its CRC check")
        names = {n for n in archive.namelist() if not n.endswith("/")}
        for missing in sorted(KIT_FILES - names):
            fail(f"press kit: {missing} is missing from the zip")
        for extra in sorted(names - KIT_FILES):
            fail(f"press kit: {extra} is not part of the kit layout")
        for name in sorted(names & KIT_FILES):
            data = archive.read(name)
            if hashlib.sha256(data).hexdigest() in RETIRED_ICONS_SHA256:
                fail(f"press kit: {name} is the retired flat-grid icon")
            icon = re.fullmatch(KIT_ROOT + r"icons/smalti-icon-(\d+)(?:-dark|-tinted)?\.png", name)
            if icon and png_size(data) != (int(icon.group(1)),) * 2:
                fail(f"press kit: {name} is not a {icon.group(1)}px square PNG")

    # The page quotes the download size; it drifts the moment the kit is rebuilt.
    quoted = re.search(r"press kit \(zip, (\d+(?:\.\d+)?) MB\)",
                       (ROOT / "games/smalti/press.html").read_text(encoding="utf-8"))
    actual = kit.stat().st_size
    if not quoted:
        fail("press kit: press.html no longer states the download size")
    elif not any(abs(float(quoted.group(1)) - actual / unit) <= 1.0 for unit in (1e6, 2**20)):
        fail(f"press kit: press.html says {quoted.group(1)} MB, the zip is {actual / 1e6:.1f} MB")

    for rel in WEB_ICONS:
        icon = ROOT / rel
        if not icon.is_file():
            fail(f"icon: {rel} is missing")
        elif hashlib.sha256(icon.read_bytes()).hexdigest() in RETIRED_ICONS_SHA256:
            fail(f"icon: {rel} is the retired flat-grid icon")


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
        check_no_trackers,
        check_daily_page,
        check_social_cards,
        check_stale_claims,
        check_dayfolio,
        check_press_kit,
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

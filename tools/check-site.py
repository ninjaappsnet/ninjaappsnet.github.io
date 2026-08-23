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
"""

from __future__ import annotations

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

#!/usr/bin/env python3
"""Tests for tools/publish.py, which picks the files the deploy publishes. Standard library only:

    python3 -m unittest discover -s tools -p 'test_*.py'

Each test lays out a tiny site in a temporary folder and asks which of its files go live.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import test_dayfolio_build as tb

publish = tb.load("publish", "publish.py")

PAGE = """<!DOCTYPE html>
<html><head>
<meta property="og:image" content="https://ninjaapps.net/games/x/card.png">
<link rel="preload" href="../../assets/fonts/face.woff2" as="font">
<link rel="stylesheet" href="../../style.css?v=0123456789">
<script src="../../assets/theme.js?v=0123456789" defer></script>
</head><body>
<a href="../../">Home</a> <a href="support.html#faq">Support</a> <a href="https://example.com/x.png">Away</a>
<img src="shot.webp" srcset="shot-400.webp 400w, shot.webp 750w" sizes="74vw" alt="">
<video src="media/film.mp4" poster="media/poster.webp"></video>
</body></html>
"""


class PublishTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        files = {
            "index.html": '<a href="games/x/">X</a>',
            "404.html": '<link rel="stylesheet" href="/style.css?v=1"><img src="/assets/seal.svg" alt="">',
            "games/x/index.html": PAGE,
            "games/x/support.html": "<p>Help</p>",
            "games/x/card.png": "", "games/x/shot.webp": "", "games/x/shot-400.webp": "",
            "games/x/media/film.mp4": "", "games/x/media/poster.webp": "",
            "style.css": "@font-face { src: url(assets/fonts/face2.woff2) format('woff2'); }\n"
                         ".a { background: url('assets/icon.webp'); }\n",
            "assets/theme.js": "", "assets/seal.svg": "", "assets/icon.webp": "",
            "assets/fonts/face.woff2": "", "assets/fonts/face2.woff2": "", "assets/fonts/unused.woff2": "",
            "sitemap.xml": "", "robots.txt": "", ".well-known/apple-app-site-association": "{}",
            "games/smalti/config/v1.json": "{}",
            "games/smalti/social/2026-09-06/clip.mp4": "",
            "assets/brand/seal.png": "", "assets/brand/seal.svg": "",
            "assets/brand/card.html": "<p>A card</p>", "assets/brand/generate.py": "",
            "games/_template/index.html": '<img src="unused.webp" alt="">', "games/_template/unused.webp": "",
            "content/x/guide/a.md": "", "README.md": "", "DESIGN.md": "", ".nojekyll": "", ".gitignore": "",
            "games/x/shot.webp.json": "{}", "tools/check-site.py": "", ".github/workflows/pages.yml": "",
        }
        for rel, text in files.items():
            path = self.root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
        self.published = publish.published_files(self.root)

    def test_every_page_is_published(self):
        for rel in ("index.html", "404.html", "games/x/index.html", "games/x/support.html"):
            self.assertIn(rel, self.published)

    def test_what_a_page_uses_is_published(self):
        for rel in ("style.css", "assets/theme.js", "assets/fonts/face.woff2", "games/x/shot.webp",
                    "games/x/shot-400.webp", "games/x/media/film.mp4", "games/x/media/poster.webp",
                    "games/x/card.png", "assets/seal.svg"):
            self.assertIn(rel, self.published)

    def test_what_the_stylesheet_uses_is_published(self):
        self.assertIn("assets/fonts/face2.woff2", self.published)
        self.assertIn("assets/icon.webp", self.published)

    def test_addresses_fetched_from_outside_are_published(self):
        # The crawlers' files, the universal links file, the config every Smalti install fetches, the social
        # media files posts link to, and the brand images.
        for rel in ("sitemap.xml", "robots.txt", ".well-known/apple-app-site-association",
                    "games/smalti/config/v1.json", "games/smalti/social/2026-09-06/clip.mp4",
                    "assets/brand/seal.png", "assets/brand/seal.svg"):
            self.assertIn(rel, self.published)

    def test_what_nothing_uses_stays_out(self):
        for rel in ("assets/fonts/unused.woff2", "assets/brand/card.html", "assets/brand/generate.py",
                    "games/_template/index.html", "games/_template/unused.webp", "content/x/guide/a.md",
                    "README.md", "DESIGN.md", ".nojekyll", ".gitignore", "games/x/shot.webp.json",
                    "tools/check-site.py", ".github/workflows/pages.yml"):
            self.assertNotIn(rel, self.published)

    def test_copy_writes_only_the_published_files(self):
        with tempfile.TemporaryDirectory() as out:
            publish.copy(self.root, Path(out))
            written = {p.relative_to(out).as_posix() for p in Path(out).rglob("*") if p.is_file()}
        self.assertEqual(written, self.published)


class RealSiteTests(unittest.TestCase):
    def test_the_real_site_keeps_its_fixed_addresses(self):
        published = publish.published_files(tb.TOOLS.parent)
        for rel in ("index.html", "style.css", ".well-known/apple-app-site-association",
                    "games/smalti/config/v1.json", "apps/dayfolio/media/app-preview-iphone.mp4",
                    "assets/brand/ninjaapps-seal-1024.png"):
            self.assertIn(rel, published)
        for rel in ("README.md", "DESIGN.md", "PRODUCT.md", "tools/check-site.py"):
            self.assertNotIn(rel, published)


if __name__ == "__main__":
    unittest.main()

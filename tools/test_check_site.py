#!/usr/bin/env python3
"""Tests for the Dayfolio rules in tools/check-site.py. Standard library only:

    python3 -m unittest discover -s tools -p 'test_*.py'

Each test points the checker at a small site in a temporary folder (the fixture
from test_dayfolio_build.py, built with tools/dayfolio-build.py), breaks one
thing and expects the checker to name it.
"""

from __future__ import annotations

import json
import unittest

import test_dayfolio_build as tb

check = tb.load("check_site", "check-site.py")
build = tb.build
REAL_ROOT = check.ROOT

NAMES = ["iPhone & iPad", "Mac", "All", "Upgrade from Mac", "Upgrade from iPhone & iPad"]
APP = {
    "@context": "https://schema.org",
    "@type": "SoftwareApplication",
    "name": "Dayfolio",
    "operatingSystem": "iOS 26 or later, iPadOS 26 or later, macOS 26 or later",
    "applicationCategory": "BusinessApplication",
    "offers": [{"@type": "Offer", "name": "Free download", "price": "0", "priceCurrency": "USD"}]
    + [{"@type": "Offer", "name": name, "price": price.lstrip("$"), "priceCurrency": "USD"}
       for name, price in zip(NAMES, check.DAYFOLIO_PRICES)],
}


def social(url: str) -> str:
    return (f'<meta property="og:title" content="A title">\n<meta property="og:description" content="Words.">\n'
            f'<meta property="og:url" content="{url}">\n'
            '<meta property="og:image" content="https://ninjaapps.net/apps/dayfolio/social-card.png">\n'
            '<meta name="twitter:card" content="summary_large_image">\n')


def product(app: dict) -> str:
    return tb.PRODUCT.replace(
        "</head>", social("https://ninjaapps.net/apps/dayfolio/")
        + f'<script type="application/ld+json">{json.dumps(app)}</script>\n</head>')


SUPPORT = tb.SUPPORT.replace(
    "</head>", social("https://ninjaapps.net/apps/dayfolio/support.html") + "</head>").replace(
    '<meta name="description" content="The product page.">', '<meta name="description" content="Help.">')

ALL = ("check_dayfolio_pages", "check_anchors", "check_dayfolio_app", "check_robots", "check_dayfolio_build")


class DayfolioRulesTests(unittest.TestCase):
    def setUp(self):
        self.site = tb.Site(self)
        self.site.put("apps/dayfolio/index.html", product(APP))
        self.site.put("apps/dayfolio/support.html", SUPPORT)
        self.site.put("content/dayfolio/guide/a.md", tb.topic("getting-started", "Getting started", 1))
        build.write(self.site.root)
        check.ROOT = self.site.root
        self.addCleanup(setattr, check, "ROOT", REAL_ROOT)

    def problems(self, *names: str) -> list:
        check.errors = []
        for name in names or ALL:
            getattr(check, name)()
        found, check.errors = list(check.errors), []
        return found

    def edit(self, rel: str, old: str, new: str) -> None:
        text = self.site.read(rel)
        self.assertIn(old, text)
        self.site.put(rel, text.replace(old, new, 1))

    def assertProblem(self, needle: str, *names: str) -> None:
        found = self.problems(*names)
        self.assertTrue(any(needle in p for p in found), f"no problem mentions {needle!r}: {found}")

    def test_the_fixture_is_clean(self):
        self.assertEqual(self.problems(), [])

    def test_titles_and_descriptions_are_unique(self):
        self.edit("apps/dayfolio/support.html", "<title>Support — Dayfolio — NinjaApps</title>",
                  "<title>Dayfolio — NinjaApps</title>")
        self.assertProblem("title", "check_dayfolio_pages")
        self.site.put("apps/dayfolio/support.html", SUPPORT)
        self.edit("apps/dayfolio/support.html", 'content="Help."', 'content="The product page."')
        self.assertProblem("description", "check_dayfolio_pages")

    def test_every_page_has_the_banner_a_canonical_and_a_card(self):
        for old, needle in (('<meta name="apple-itunes-app" content="app-id=6817388897">', "Smart App Banner"),
                            ('<link rel="canonical" href="https://ninjaapps.net/apps/dayfolio/support.html">',
                             "canonical"),
                            ('<meta name="twitter:card" content="summary_large_image">', "twitter:card"),
                            ('<meta property="og:image" content="https://ninjaapps.net/apps/dayfolio/social-card.png">',
                             "og:image")):
            with self.subTest(needle=needle):
                self.site.put("apps/dayfolio/support.html", SUPPORT)
                self.edit("apps/dayfolio/support.html", old, "")
                self.assertProblem(needle, "check_dayfolio_pages")

    def test_every_picture_says_what_it_shows(self):
        self.edit("apps/dayfolio/support.html", "<h1>Support</h1>", '<h1>Support</h1>\n<img src="icon-320.webp">')
        self.assertProblem("alt", "check_dayfolio_pages")
        self.site.put("apps/dayfolio/support.html", SUPPORT)
        self.edit("apps/dayfolio/support.html", "<h1>Support</h1>", '<h1>Support</h1>\n<img src="icon-320.webp" alt="">')
        self.assertProblem("alt", "check_dayfolio_pages")

    def test_headings_ids_and_tags_hold_together(self):
        cases = (("<h1>Support</h1>", "<h1>Support</h1><h1>Again</h1>", "h1"),
                 ('<h2 id="quick-note-link">', '<h4 id="quick-note-link">', "h4"),
                 ("<h1>Support</h1>", '<h1>Support</h1><p id="quick-note-link">x</p>', "quick-note-link"),
                 ("<h1>Support</h1>", "<h1>Support</h1><div><p>open</p>", "div"),
                 ("</head>", '<script type="application/ld+json">{"broken": </script></head>', "JSON-LD"))
        for old, new, needle in cases:
            with self.subTest(needle=needle):
                self.site.put("apps/dayfolio/support.html", SUPPORT)
                self.edit("apps/dayfolio/support.html", old, new)
                self.assertProblem(needle, "check_dayfolio_pages")

    def test_an_anchor_that_goes_nowhere_is_reported(self):
        self.edit("apps/dayfolio/support.html", "<h1>Support</h1>",
                  '<h1>Support</h1><a href="index.html#nowhere">x</a><a href="#quick-note-link">y</a>')
        found = self.problems("check_anchors")
        self.assertEqual(len(found), 1, found)
        self.assertIn("index.html#nowhere", found[0])
        self.site.put("content/dayfolio/guide/a.md", tb.topic(
            "getting-started", "Getting started", 1, body="See [support](../../support.html#gone).\n"))
        build.write(self.site.root)
        self.assertProblem("support.html#gone", "check_anchors")

    def test_the_product_page_names_the_app_and_its_prices(self):
        for broken, needle in (({**APP, "offers": APP["offers"][:-1]}, "offers"),
                               ({**APP, "aggregateRating": {"ratingValue": 5}}, "aggregateRating"),
                               ({**APP, "@type": "WebPage"}, "SoftwareApplication"),
                               ({**APP, "operatingSystem": "iOS 26"}, "macOS")):
            with self.subTest(needle=needle):
                self.site.put("apps/dayfolio/index.html", product(broken))
                build.write(self.site.root)
                self.assertProblem(needle, "check_dayfolio_app")

    def test_robots_names_the_sitemap(self):
        self.site.put("robots.txt", "User-agent: *\nAllow: /\n")
        self.assertProblem("robots.txt", "check_robots")

    def test_a_page_that_drifted_from_its_source_is_reported(self):
        self.edit("apps/dayfolio/guide/getting-started/index.html", "Some words.", "Hand edit.")
        self.assertProblem("apps/dayfolio/guide/getting-started/index.html", "check_dayfolio_build")


if __name__ == "__main__":
    unittest.main()

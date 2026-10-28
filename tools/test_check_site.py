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


FLECTO_APP = {
    "@context": "https://schema.org",
    "@type": "SoftwareApplication",
    "name": "FlectoBI",
    "operatingSystem": "macOS 26 or later",
    "applicationCategory": "BusinessApplication",
    "publisher": {"@type": "Organization", "name": "NinjaApps", "url": "https://ninjaapps.net/"},
}
SOON = '<span class="btn btn-quiet btn-soon">Coming to the Mac App Store</span>'


def flecto_social(url: str) -> str:
    return social(url).replace("apps/dayfolio/social-card.png", "apps/flectobi/social-card.png")


def flecto_product(app: dict, extra: str = SOON) -> str:
    return tb.FLECTO_PRODUCT.replace(
        "</head>", flecto_social("https://ninjaapps.net/apps/flectobi/")
        + f'<script type="application/ld+json">{json.dumps(app)}</script>\n</head>').replace(
        "<h1>FlectoBI</h1>", f"<h1>FlectoBI</h1>\n{extra}")


FLECTO_SUPPORT = tb.FLECTO_PRODUCT.replace(
    "</head>", flecto_social("https://ninjaapps.net/apps/flectobi/support.html") + "</head>").replace(
    "<title>FlectoBI — NinjaApps</title>", "<title>Support — FlectoBI — NinjaApps</title>").replace(
    'href="https://ninjaapps.net/apps/flectobi/"', 'href="https://ninjaapps.net/apps/flectobi/support.html"').replace(
    '<meta name="description" content="The product page.">', '<meta name="description" content="Help with FlectoBI.">'
    ).replace("<h1>FlectoBI</h1>", "<h1>Support</h1>")

FLECTO_ALL = ("check_flectobi_pages", "check_flectobi", "check_flectobi_app", "check_dayfolio_build")


class FlectoBIRulesTests(unittest.TestCase):
    def setUp(self):
        self.site = tb.flecto_site(self)
        self.site.put("apps/flectobi/index.html", flecto_product(FLECTO_APP))
        self.site.put("apps/flectobi/support.html", FLECTO_SUPPORT)
        self.site.put("content/flectobi/tutorials/a.md", tb.topic("first-flow", "Your first Flow", 1))
        self.site.put("index.html", '<a href="apps/flectobi/">FlectoBI</a>')
        self.site.put("privacy/index.html", '<a href="../apps/flectobi/privacy.html">FlectoBI</a>')
        build.write(self.site.root)
        check.ROOT = self.site.root
        self.addCleanup(setattr, check, "ROOT", REAL_ROOT)
        self.addCleanup(build.set_store_id, "flectobi", build.FLECTOBI_STORE_ID)

    def problems(self, *names: str) -> list:
        check.errors, check.warnings = [], []
        for name in names or FLECTO_ALL:
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

    def test_the_fixture_is_clean_and_warns_that_the_store_id_and_price_are_due(self):
        self.assertEqual(self.problems(), [])
        self.assertTrue(any("store id" in w and "price" in w for w in check.warnings), check.warnings)

    def test_every_flectobi_page_is_in_the_manifest(self):
        for rel in ("apps/flectobi/index.html", "apps/flectobi/support.html", "apps/flectobi/privacy.html",
                    "apps/flectobi/guide/index.html", "apps/flectobi/tutorials/index.html"):
            self.assertIn(rel, check.MANIFEST)

    def test_no_page_states_a_price_or_calls_it_free(self):
        for claim in ("It costs $29.99.", "A free download.", "Free to download.", "It’s free.", "It's free."):
            with self.subTest(claim=claim):
                self.site.put("apps/flectobi/support.html", FLECTO_SUPPORT)
                self.edit("apps/flectobi/support.html", "<h1>Support</h1>", f"<h1>Support</h1><p>{claim}</p>")
                self.assertProblem("apps/flectobi/support.html", "check_flectobi")
        self.site.put("content/flectobi/guide/b.md", tb.topic("b", "B", 1, body="It costs $5 a month.\n"))
        build.write(self.site.root)
        self.assertProblem("apps/flectobi/guide/b/index.html", "check_flectobi")

    def test_without_a_store_id_no_page_has_a_banner_or_a_store_link(self):
        self.edit("apps/flectobi/support.html", "<title>",
                  '<meta name="apple-itunes-app" content="app-id=1234567890">\n<title>')
        self.assertProblem("Smart App Banner", "check_flectobi")
        self.site.put("apps/flectobi/support.html", FLECTO_SUPPORT)
        self.site.put("apps/flectobi/index.html",
                      flecto_product(FLECTO_APP, '<a class="btn" href="https://apps.apple.com/app/id1">APP STORE</a>'))
        build.write(self.site.root)
        self.assertProblem("Coming to the Mac App Store", "check_flectobi")

    def test_once_the_store_id_is_set_the_product_page_must_state_a_price_and_link_the_store(self):
        build.set_store_id("flectobi", "1234567890")
        build.write(self.site.root)
        found = self.problems("check_flectobi", "check_flectobi_pages")
        self.assertTrue(any("price" in p for p in found), found)
        self.assertTrue(any("https://apps.apple.com/app/id1234567890" in p for p in found), found)
        self.assertTrue(any("apps/flectobi/support.html" in p and "Smart App Banner" in p for p in found), found)
        self.assertFalse(any("store id" in w for w in check.warnings), check.warnings)

    def test_the_per_page_rules_hold_on_flectobi_pages(self):
        cases = (("<h1>Support</h1>", "<h1>Support</h1><h1>Again</h1>", "h1"),
                 ("<h1>Support</h1>", '<h1>Support</h1><img src="icon-320.webp">', "alt"),
                 ("<title>Support — FlectoBI — NinjaApps</title>", "<title>FlectoBI — NinjaApps</title>", "title"),
                 ('<link rel="canonical" href="https://ninjaapps.net/apps/flectobi/support.html">', "", "canonical"),
                 ('<meta name="twitter:card" content="summary_large_image">', "", "twitter:card"),
                 ("</head>", '<script type="application/ld+json">{"broken": </script></head>', "JSON-LD"))
        for old, new, needle in cases:
            with self.subTest(needle=needle):
                self.site.put("apps/flectobi/support.html", FLECTO_SUPPORT)
                build.write(self.site.root)
                self.edit("apps/flectobi/support.html", old, new)
                self.assertProblem(needle, "check_flectobi_pages")

    def test_the_landing_page_and_the_privacy_hub_list_flectobi(self):
        self.site.put("index.html", '<a href="apps/dayfolio/">Dayfolio</a>')
        self.site.put("privacy/index.html", '<a href="../apps/dayfolio/privacy.html">Dayfolio</a>')
        found = self.problems("check_flectobi")
        self.assertTrue(any("index.html" in p and "apps/flectobi/" in p for p in found), found)
        self.assertTrue(any("privacy/index.html" in p for p in found), found)
        self.site.put("index.html", '<a href="apps/flectobi/">FlectoBI</a>')
        self.site.put("privacy/index.html", '<a href="../apps/flectobi/privacy.html">FlectoBI</a>')
        self.assertEqual(self.problems("check_flectobi"), [])

    def test_the_product_page_names_the_mac_app_and_offers_nothing_yet(self):
        for broken, needle in (({**FLECTO_APP, "offers": [{"@type": "Offer", "price": "0"}]}, "offers"),
                               ({**FLECTO_APP, "aggregateRating": {"ratingValue": 5}}, "aggregateRating"),
                               ({**FLECTO_APP, "operatingSystem": "iOS 26"}, "macOS"),
                               ({**FLECTO_APP, "applicationCategory": "Game"}, "BusinessApplication"),
                               ({**FLECTO_APP, "name": "Flecto"}, "FlectoBI")):
            with self.subTest(needle=needle):
                self.site.put("apps/flectobi/index.html", flecto_product(broken))
                build.write(self.site.root)
                self.assertProblem(needle, "check_flectobi_app")


class TemplateGalleryTests(unittest.TestCase):
    """The gallery's pages, as tools/dayfolio-templates.py writes them, pass every Dayfolio rule, and a page that
    drifted from the library is reported."""

    def setUp(self):
        import test_dayfolio_templates as tt
        self.templates = tt.templates
        self.site = tt.Site(self)
        self.site.put("apps/dayfolio/index.html", product(APP))
        self.site.put("apps/dayfolio/support.html", SUPPORT)
        self.templates.write(self.site.root)
        build.write(self.site.root)
        check.ROOT = self.site.root
        self.addCleanup(setattr, check, "ROOT", REAL_ROOT)
        self.page = tt.STANDUP

    def problems(self, *names: str) -> list:
        check.errors = []
        for name in names:
            getattr(check, name)()
        found, check.errors = list(check.errors), []
        return found

    def test_the_gallery_passes_every_dayfolio_rule(self):
        self.assertEqual(self.problems(*ALL, "check_dayfolio_templates", "check_sitemap", "check_canonicals"), [])
        def chrome(problem: str) -> bool:  # the fixture's header and footer: the stylesheet and its face, the site's root
            page, target = problem[len("dead link: "):].split(" -> ")
            target = target.split("?", 1)[0]  # the stylesheet asks by its version (a hash of the file)
            root = "../" * page.count("/")
            return target.endswith(("style.css", "assets/theme.js", "archivo-var-latin.woff2", "privacy.html")) or target in (root, root + "#titles", root + "#studio", root + "privacy/")
        dead = [p for p in self.problems("check_links")
                if p.startswith("dead link: apps/dayfolio/templates/") and not chrome(p)]
        self.assertEqual(dead, [])

    def test_a_page_that_drifted_from_the_library_is_reported(self):
        text = self.site.read(self.page)
        self.site.put(self.page, text.replace("Retry queue is in", "Hand edit", 1))
        found = self.problems("check_dayfolio_templates")
        self.assertTrue(any(self.page in p for p in found), found)



def sheet(src: str, extra: str) -> str:
    return f'<div class="sheet-art"><img class="phone" src="{src}" {extra} alt="A picture" width="750" height="1000"></div>'


class PicturesTests(unittest.TestCase):
    """The home page's pictures: each offers a smaller file, and only the first, the largest paint on a phone,
    is fetched straight away."""

    def setUp(self):
        self.site = tb.Site(self)
        for name, width in (("a", 750), ("a-400", 400), ("b", 624), ("b-400", 400)):
            self.site.put(f"media/{name}.webp", tb.webp(width, 1000))
        check.ROOT = self.site.root
        self.addCleanup(setattr, check, "ROOT", REAL_ROOT)
        self.first = sheet("media/a.webp", 'srcset="media/a-400.webp 400w, media/a.webp 750w" sizes="74vw" fetchpriority="high"')
        self.second = sheet("media/b.webp", 'srcset="media/b-400.webp 400w, media/b.webp 624w" sizes="74vw" loading="lazy"')

    def home(self, *sheets: str) -> list:
        self.site.put("index.html", "<html><body>" + "\n".join(sheets) + "</body></html>")
        check.errors = []
        check.check_pictures()
        found, check.errors = list(check.errors), []
        return found

    def test_the_home_page_as_it_should_be_passes(self):
        self.assertEqual(self.home(self.first, self.second), [])

    def test_a_picture_without_a_smaller_file_is_reported(self):
        found = self.home(self.first, sheet("media/b.webp", 'loading="lazy"'))
        self.assertTrue(any("media/b.webp" in p and "srcset" in p for p in found), found)

    def test_a_picture_below_the_first_that_is_not_lazy_is_reported(self):
        found = self.home(self.first, self.second.replace(' loading="lazy"', ""))
        self.assertTrue(any("media/b.webp" in p and "lazy" in p for p in found), found)

    def test_a_lazy_first_picture_is_reported(self):
        found = self.home(self.first.replace('fetchpriority="high"', 'loading="lazy"'), self.second)
        self.assertTrue(any("media/a.webp" in p for p in found), found)

    def test_a_candidate_whose_width_is_wrong_or_missing_is_reported(self):
        found = self.home(self.first.replace("a-400.webp 400w", "a-400.webp 500w"), self.second)
        self.assertTrue(any("media/a-400.webp" in p and "400" in p for p in found), found)
        found = self.home(self.first.replace("a-400.webp", "gone.webp"), self.second)
        self.assertTrue(any("media/gone.webp" in p for p in found), found)

    def test_candidates_are_checked_on_every_page(self):
        self.site.put("games/x/index.html", '<img src="../../media/a.webp" srcset="../../media/a-400.webp 300w" sizes="1px">')
        found = self.home(self.first, self.second)
        self.assertTrue(any("games/x/index.html" in p for p in found), found)


if __name__ == "__main__":
    unittest.main()

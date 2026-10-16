#!/usr/bin/env python3
"""Tests for tools/dayfolio-build.py and the Markdown handling it shares with
tools/archive-page.py. Standard library only, like the tools:

    python3 -m unittest discover -s tools -p 'test_*.py'

Each test builds a tiny site in a temporary folder: the product page (the shell
takes the header and footer from it), the support page, the pictures the shell
needs and a few Markdown sources. Nothing touches the real site.
"""

from __future__ import annotations

import importlib.util
import json
import re
import struct
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
import zlib
from pathlib import Path

TOOLS = Path(__file__).resolve().parent


def load(name: str, file: str):
    """A tool, as a module, under the name the tools load each other by."""
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(name, TOOLS / file)
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
    return sys.modules[name]


build = load("dayfolio_build", "dayfolio-build.py")
archive = load("archive_page", "archive-page.py")


def png(width: int, height: int) -> bytes:
    def chunk(kind: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
            + chunk(b"IEND", b""))


def webp(width: int, height: int) -> bytes:
    """A WebP header (VP8X) with the canvas size: all the build reads."""
    body = (b"VP8X" + struct.pack("<I", 10) + bytes(4)
            + (width - 1).to_bytes(3, "little") + (height - 1).to_bytes(3, "little"))
    return b"RIFF" + struct.pack("<I", 4 + len(body)) + b"WEBP" + body


PRODUCT = """<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
<meta charset="UTF-8">
<meta name="apple-itunes-app" content="app-id=6817388897">
<title>Dayfolio — NinjaApps</title>
<meta name="description" content="The product page.">
<link rel="canonical" href="https://ninjaapps.net/apps/dayfolio/">
</head>
<body>

<header>
  <a class="wordmark" href="../../">忍 NinjaApps</a>
  <nav>
    <a href="../../#apps">Apps</a>
    <a href="privacy.html">Privacy</a>
  </nav>
</header>

<main>
<h1>Dayfolio</h1>
</main>

<footer>
  <span>© 2026 NinjaApps</span>
  <a class="footer-privacy" href="privacy.html">PRIVACY POLICY</a>
</footer>

</body>
</html>
"""

SUPPORT = PRODUCT.replace("<title>Dayfolio — NinjaApps</title>", "<title>Support — Dayfolio — NinjaApps</title>").replace(
    "https://ninjaapps.net/apps/dayfolio/\"", "https://ninjaapps.net/apps/dayfolio/support.html\"").replace(
    "</header>", '</header>\n\n<nav class="subnav" aria-label="Dayfolio">an old one</nav>').replace(
    "<h1>Dayfolio</h1>", '<h1>Support</h1>\n<h2 id="quick-note-link">Notes from links</h2>')

LONG = "a sentence long enough to describe the page to someone who searched for it"


def source(**fields: str) -> str:
    body = fields.pop("body", "Some words.\n")
    head = "\n".join(f"{key}: {value}" for key, value in fields.items())
    return f"---\n{head}\n---\n\n{body}"


def section(title: str) -> str:
    return source(title=title, description=f"{title}: {LONG}.", body=f"Everything in the {title.lower()}.\n")


def topic(slug: str, title: str, order: int, **extra: str) -> str:
    return source(title=title, description=f"{title}, {LONG}.", slug=slug, date="2026-10-20",
                  order=str(order), **extra)


def article(slug: str, title: str, date: str, **extra: str) -> str:
    return source(title=title, description=f"{title}, {LONG}.", slug=slug, date=date, **extra)


class Site:
    def __init__(self, test: unittest.TestCase):
        tmp = tempfile.TemporaryDirectory()
        test.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.put("apps/dayfolio/index.html", PRODUCT)
        self.put("apps/dayfolio/support.html", SUPPORT)
        self.put("apps/dayfolio/social-card.png", png(1200, 630))
        self.put("apps/dayfolio/icon-320.webp", webp(320, 320))
        self.put("404.html", '<html><head><meta name="robots" content="noindex"><title>404</title></head></html>')
        self.put("robots.txt", "old\n")
        for key, title in (("guide", "Guide"), ("templates", "Templates"), ("articles", "Articles")):
            self.put(f"content/dayfolio/{key}/index.md", section(title))

    def put(self, rel: str, data) -> Path:
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(data, bytes):
            path.write_bytes(data)
        else:
            path.write_text(data, encoding="utf-8")
        return path

    def read(self, rel: str) -> str:
        return (self.root / rel).read_text(encoding="utf-8")

    def built(self) -> dict:
        return build.build_site(self.root)


def jsonld(page: str) -> list:
    return [json.loads(block) for block in
            re.findall(r'<script type="application/ld\+json">(.*?)</script>', page, re.S)]


def meta(page: str, key: str) -> str:
    found = re.search(rf'<meta (?:name|property)="{re.escape(key)}" content="([^"]*)">', page)
    return found.group(1) if found else ""


class FrontMatterTests(unittest.TestCase):
    def test_reads_the_fields_and_the_body(self):
        fields, body, line = build.parse_page(topic("getting-started", "Getting started", 1), "guide/a.md")
        self.assertEqual(fields["title"], "Getting started")
        self.assertEqual(fields["slug"], "getting-started")
        self.assertEqual(fields["order"], "1")
        self.assertEqual(body.strip(), "Some words.")
        self.assertEqual(line, 8)  # the file line the body starts on, for messages

    def test_a_page_without_front_matter_is_refused(self):
        with self.assertRaisesRegex(build.BuildError, "front matter"):
            build.parse_page("Just words.\n", "guide/a.md")

    def test_unknown_and_missing_fields_are_named(self):
        with self.assertRaisesRegex(build.BuildError, "unknown field 'tags'"):
            build.check_fields(build.parse_page(source(title="A", tags="x"), "a.md")[0], "topic", "guide/a.md")
        with self.assertRaisesRegex(build.BuildError, "description"):
            build.check_fields({"title": "A", "slug": "a", "date": "2026-10-20", "order": "1"}, "topic", "guide/a.md")

    def test_slug_date_and_order_are_checked(self):
        good = {"title": "A", "description": "D" * 60, "slug": "a-b", "date": "2026-10-20", "order": "1"}
        build.check_fields(dict(good), "topic", "guide/a.md")
        for key, bad in (("slug", "A B"), ("date", "20 October"), ("date", "2026-02-30"), ("order", "first")):
            with self.subTest(key=key, value=bad), self.assertRaises(build.BuildError):
                build.check_fields({**good, key: bad}, "topic", "guide/a.md")

    def test_title_and_description_lengths(self):
        good = {"title": "A", "description": "D" * 60, "slug": "a", "date": "2026-10-20", "order": "1"}
        with self.assertRaisesRegex(build.BuildError, "title"):
            build.check_fields({**good, "title": "T" * 61}, "topic", "guide/a.md")
        with self.assertRaisesRegex(build.BuildError, "description"):
            build.check_fields({**good, "description": "D" * 161}, "topic", "guide/a.md")


class CopyRuleTests(unittest.TestCase):
    def test_straight_quotes_exclamation_marks_and_emoji_are_reported_with_their_line(self):
        problems = build.lint_copy("Fine line.\nIt's here.\nSay \"hi\".\nWow!\nA \U0001F600 face.\n", "a.md")
        self.assertEqual(len(problems), 4, problems)
        self.assertIn("a.md:2", problems[0])
        self.assertIn("a.md:3", problems[1])
        self.assertIn("a.md:4", problems[2])
        self.assertIn("a.md:5", problems[3])

    def test_code_links_and_pictures_are_left_alone(self):
        text = ("It’s “fine”.\nRun `echo 'hi'!` now.\n![A picture](a.webp \"A caption\")\n"
                "[A link](https://example.com/?a='b')\n```\nprint('hello!')\n```\n")
        self.assertEqual(build.lint_copy(text, "a.md"), [])


class ShellTests(unittest.TestCase):
    def setUp(self):
        self.site = Site(self)
        self.site.put("content/dayfolio/guide/getting-started.md", topic("getting-started", "Getting started", 1))
        self.page = self.site.built()["apps/dayfolio/guide/getting-started/index.html"]

    def test_the_head_carries_what_a_search_engine_and_a_share_sheet_read(self):
        page, url = self.page, "https://ninjaapps.net/apps/dayfolio/guide/getting-started/"
        self.assertIn("<title>Getting started — Dayfolio — NinjaApps</title>", page)
        self.assertEqual(meta(page, "description"), f"Getting started, {LONG}.")
        self.assertIn(f'<link rel="canonical" href="{url}">', page)
        self.assertIn('<meta name="apple-itunes-app" content="app-id=6817388897">', page)
        self.assertEqual(meta(page, "og:url"), url)
        self.assertEqual(meta(page, "og:type"), "article")
        self.assertEqual(meta(page, "og:image"), "https://ninjaapps.net/apps/dayfolio/social-card.png")
        self.assertEqual((meta(page, "og:image:width"), meta(page, "og:image:height")), ("1200", "630"))
        self.assertTrue(meta(page, "og:image:alt"))
        self.assertEqual(meta(page, "twitter:card"), "summary_large_image")
        self.assertEqual(meta(page, "twitter:image"), meta(page, "og:image"))
        self.assertIn('<html lang="en"', page)

    def test_json_ld_names_the_article_and_its_breadcrumbs(self):
        blocks = {block["@type"]: block for block in jsonld(self.page)}
        self.assertEqual(blocks["Article"]["headline"], "Getting started")
        self.assertEqual(blocks["Article"]["datePublished"], "2026-10-20")
        self.assertEqual(blocks["Article"]["mainEntityOfPage"],
                         "https://ninjaapps.net/apps/dayfolio/guide/getting-started/")
        crumbs = [(item["position"], item["name"], item["item"])
                  for item in blocks["BreadcrumbList"]["itemListElement"]]
        self.assertEqual(crumbs, [
            (1, "Dayfolio", "https://ninjaapps.net/apps/dayfolio/"),
            (2, "Guide", "https://ninjaapps.net/apps/dayfolio/guide/"),
            (3, "Getting started", "https://ninjaapps.net/apps/dayfolio/guide/getting-started/"),
        ])

    def test_the_chrome_is_the_product_pages_rebased_to_the_pages_depth(self):
        page = self.page
        self.assertIn('<a class="wordmark" href="../../../../">', page)
        self.assertIn('<a href="../../../../#apps">Apps</a>', page)
        self.assertIn('<a class="footer-privacy" href="../../privacy.html">', page)
        self.assertIn(f'<link rel="stylesheet" href="../../../../style.css?v={build.STYLE_VERSION}">', page)
        self.assertIn('<script src="../../../../assets/theme.js" defer></script>', page)

    def test_the_sub_navigation_marks_the_section(self):
        nav = re.search(r'<nav class="subnav" aria-label="Dayfolio">.*?</nav>', self.page, re.S).group(0)
        links = re.findall(r'<a (?:class="[^"]*" )?href="([^"]+)"(?: aria-current="(\w+)")?>([^<]+)</a>', nav)
        self.assertEqual([(href, label) for href, _, label in links][1:], [
            ("../../", "Overview"), ("../", "Guide"), ("../../templates/", "Templates"),
            ("../../articles/", "Articles"), ("../../support.html", "Support")])
        self.assertEqual([label for _, current, label in links if current], ["Guide"])

    def test_the_page_says_it_is_generated(self):
        self.assertIn("content/dayfolio/guide/getting-started.md", self.page)
        self.assertIn('<h1 class="page-title">Getting started</h1>', self.page)


class SectionTests(unittest.TestCase):
    def setUp(self):
        self.site = Site(self)

    def test_a_section_page_lists_its_pages_in_order(self):
        self.site.put("content/dayfolio/guide/b.md", topic("reports", "Reports", 2))
        self.site.put("content/dayfolio/guide/a.md", topic("getting-started", "Getting started", 1))
        self.site.put("content/dayfolio/articles/x.md", article("brag-document", "A brag document", "2026-10-21"))
        self.site.put("content/dayfolio/articles/y.md", article("self-review", "A self-review", "2026-10-22"))
        built = self.site.built()
        guide = built["apps/dayfolio/guide/index.html"]
        self.assertLess(guide.index('href="getting-started/"'), guide.index('href="reports/"'))
        items = [block for block in jsonld(guide) if block["@type"] == "ItemList"][0]["itemListElement"]
        self.assertEqual([item["url"] for item in items], [
            "https://ninjaapps.net/apps/dayfolio/guide/getting-started/",
            "https://ninjaapps.net/apps/dayfolio/guide/reports/"])
        articles = built["apps/dayfolio/articles/index.html"]
        self.assertLess(articles.index('href="self-review/"'), articles.index('href="brag-document/"'))
        self.assertIn("Everything in the guide.", guide)
        self.assertEqual(meta(guide, "og:type"), "website")

    def test_an_empty_section_says_so(self):
        templates = self.site.built()["apps/dayfolio/templates/index.html"]
        self.assertIn('class="listing-empty"', templates)
        self.assertNotIn('"ItemList"', templates)

    def test_guide_pages_link_the_topic_before_and_after(self):
        for slug, title, order in (("one", "One", 1), ("two", "Two", 2), ("three", "Three", 3)):
            self.site.put(f"content/dayfolio/guide/{slug}.md", topic(slug, title, order))
        two = self.site.built()["apps/dayfolio/guide/two/index.html"]
        pager = re.search(r'<nav class="pager".*?</nav>', two, re.S).group(0)
        self.assertIn('href="../one/"', pager)
        self.assertIn('href="../three/"', pager)

    def test_two_pages_cannot_share_a_slug_or_an_order(self):
        self.site.put("content/dayfolio/guide/a.md", topic("same", "One", 1))
        self.site.put("content/dayfolio/guide/b.md", topic("same", "Two", 2))
        with self.assertRaisesRegex(build.BuildError, "slug"):
            self.site.built()
        self.site.put("content/dayfolio/guide/b.md", topic("other", "Two", 1))
        with self.assertRaisesRegex(build.BuildError, "order"):
            self.site.built()

    def test_an_article_shows_its_date(self):
        self.site.put("content/dayfolio/articles/x.md", article("self-review", "A self-review", "2026-10-22"))
        page = self.site.built()["apps/dayfolio/articles/self-review/index.html"]
        self.assertIn("2026-10-22", page)
        self.assertIn('href="https://apps.apple.com/app/id6817388897"', page)


class MarkdownTests(unittest.TestCase):
    def setUp(self):
        self.site = Site(self)

    def page(self, body: str) -> str:
        self.site.put("content/dayfolio/guide/a.md", topic("a", "A", 1, body=body))
        return self.site.built()["apps/dayfolio/guide/a/index.html"]

    def test_internal_links_stay_links(self):
        page = self.page("Read about [reports](../reports/#billable) and [the app](https://apps.apple.com/app/id6817388897).\n")
        self.assertIn('<a href="../reports/#billable">reports</a>', page)
        self.assertIn('<a href="https://apps.apple.com/app/id6817388897">the app</a>', page)

    def test_a_picture_becomes_a_figure_with_its_size(self):
        self.site.put("apps/dayfolio/guide/a/today.webp", webp(1206, 2622))
        page = self.page('![Today on iPhone, with one entry](today.webp "Today, with the first entry")\n')
        self.assertIn('<img src="today.webp" alt="Today on iPhone, with one entry" width="1206" height="2622"', page)
        self.assertIn("<figcaption>Today, with the first entry</figcaption>", page)
        self.assertIn("figure-portrait", page)

    def test_pictures_side_by_side(self):
        self.site.put("apps/dayfolio/guide/a/one.webp", webp(1206, 2622))
        self.site.put("apps/dayfolio/guide/a/two.webp", webp(1206, 2622))
        page = self.page("![One](one.webp)\n![Two](two.webp)\n")
        self.assertRegex(page, r'<div class="figure-row">\s*<figure')

    def test_a_picture_must_exist_be_webp_and_say_what_it_shows(self):
        self.site.put("apps/dayfolio/guide/a/shot.png", png(10, 10))
        for body, why in (("![Today](missing.webp)\n", "missing.webp"), ("![](shot.png)\n", "alt"),
                          ("![Today](shot.png)\n", "webp")):
            with self.subTest(body=body), self.assertRaisesRegex(build.BuildError, why):
                self.page(body)

    def test_a_tip_is_a_callout(self):
        page = self.page("> **Tip:** Press the key.\n")
        self.assertIn('<aside class="callout"><p><strong>Tip:</strong> Press the key.</p></aside>', page)

    def test_the_title_is_the_only_h1(self):
        with self.assertRaisesRegex(build.BuildError, "h1"):
            self.page("# Another title\n\nWords.\n")

    def test_a_copy_rule_stops_the_build(self):
        with self.assertRaisesRegex(build.BuildError, "a.md:11"):
            self.page("A line.\n\nIt's wrong.\n")


class HandWrittenPagesTests(unittest.TestCase):
    def setUp(self):
        self.site = Site(self)
        self.built = self.site.built()

    def test_the_sub_navigation_goes_in_after_the_header(self):
        product = self.built["apps/dayfolio/index.html"]
        self.assertRegex(product, r'</header>\n\n<nav class="subnav" aria-label="Dayfolio">')
        self.assertRegex(product, r'<a href="\./" aria-current="page">Overview</a>')
        self.assertEqual(product.replace(build.render_subnav("apps/dayfolio/index.html") + "\n\n", ""),
                         PRODUCT)

    def test_an_old_sub_navigation_is_replaced(self):
        support = self.built["apps/dayfolio/support.html"]
        self.assertNotIn("an old one", support)
        self.assertRegex(support, r'<a href="support\.html" aria-current="page">Support</a>')
        self.assertEqual(support.count('class="subnav"'), 1)

    def test_every_dayfolio_page_asks_for_the_stylesheet_by_one_version(self):
        # Cloudflare keeps style.css at its edge, and browsers keep it, for four hours: a page whose markup needs
        # a new rule asks for the stylesheet by a new query, and every Dayfolio page asks by the same one.
        site = Site(self)
        link = '<link rel="stylesheet" href="../../style.css{}">\n</head>'
        site.put("apps/dayfolio/index.html", PRODUCT.replace("</head>", link.format("?v=2026-01-01")))
        site.put("apps/dayfolio/support.html", SUPPORT.replace("</head>", link.format("")))
        site.put("games/smalti/index.html", f"<html><head>{link.format('')}<body></body></html>")
        built = site.built()
        wanted = f'<link rel="stylesheet" href="../../style.css?v={build.STYLE_VERSION}">'
        for rel in ("apps/dayfolio/index.html", "apps/dayfolio/support.html"):
            self.assertIn(wanted, built[rel])
            self.assertEqual(built[rel].count('rel="stylesheet"'), 1)
        self.assertNotIn("games/smalti/index.html", built)  # the rest of the site links style.css as it chooses
        self.assertRegex(build.STYLE_VERSION, r"^\d{4}-\d{2}-\d{2}[a-z]?$")  # the day of the change


class SitemapTests(unittest.TestCase):
    def test_the_sitemap_lists_every_indexable_page_and_robots_points_to_it(self):
        site = Site(self)
        site.put("content/dayfolio/guide/a.md", topic("getting-started", "Getting started", 1))
        built = site.built()
        urls = [loc.text for loc in ET.fromstring(built["sitemap.xml"]).iter(
            "{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
        self.assertEqual(urls, sorted(urls))
        for url in ("https://ninjaapps.net/apps/dayfolio/", "https://ninjaapps.net/apps/dayfolio/support.html",
                    "https://ninjaapps.net/apps/dayfolio/guide/",
                    "https://ninjaapps.net/apps/dayfolio/guide/getting-started/"):
            self.assertIn(url, urls)
        self.assertNotIn("https://ninjaapps.net/404.html", urls)
        self.assertIn("Sitemap: https://ninjaapps.net/sitemap.xml", built["robots.txt"])


class WriteAndCheckTests(unittest.TestCase):
    def setUp(self):
        self.site = Site(self)
        self.site.put("content/dayfolio/guide/a.md", topic("getting-started", "Getting started", 1))

    def test_after_a_build_the_check_is_clean_and_the_build_is_stable(self):
        self.assertTrue(build.write(self.site.root))
        self.assertEqual(build.check(self.site.root), [])
        self.assertEqual(build.write(self.site.root), [])

    def test_the_check_names_a_page_that_differs_from_the_build(self):
        build.write(self.site.root)
        page = self.site.root / "apps/dayfolio/guide/getting-started/index.html"
        page.write_text(page.read_text(encoding="utf-8").replace("Some words.", "Hand edit."), encoding="utf-8")
        problems = build.check(self.site.root)
        self.assertEqual(len(problems), 1, problems)
        self.assertIn("apps/dayfolio/guide/getting-started/index.html", problems[0])

    def test_a_page_whose_source_is_gone_is_reported_and_removed(self):
        build.write(self.site.root)
        (self.site.root / "content/dayfolio/guide/a.md").unlink()
        self.assertTrue(any("getting-started" in p for p in build.check(self.site.root)))
        build.write(self.site.root)
        self.assertFalse((self.site.root / "apps/dayfolio/guide/getting-started/index.html").exists())
        self.assertEqual(build.check(self.site.root), [])

    def test_a_hand_written_page_without_the_sub_navigation_is_reported(self):
        build.write(self.site.root)
        self.site.put("apps/dayfolio/index.html", PRODUCT)
        self.assertTrue(any("apps/dayfolio/index.html" in p for p in build.check(self.site.root)))

    def test_a_hand_written_page_on_another_stylesheet_version_is_reported(self):
        self.site.put("apps/dayfolio/support.html",
                      SUPPORT.replace("</head>", '<link rel="stylesheet" href="../../style.css">\n</head>'))
        build.write(self.site.root)
        self.assertEqual(build.check(self.site.root), [])
        text = self.site.read("apps/dayfolio/support.html")
        self.site.put("apps/dayfolio/support.html", text.replace(f"?v={build.STYLE_VERSION}", "?v=2026-01-01"))
        self.assertTrue(any("apps/dayfolio/support.html" in p for p in build.check(self.site.root)))


class ArchiveMarkdownTests(unittest.TestCase):
    """archive-page.py keeps its own rules: a relative link is a path in the Dayfolio repo, so plain text."""

    def test_the_archive_keeps_relative_links_as_text(self):
        self.assertEqual(archive.convert("See [the ADR](../adr/0001.md) and [Apple](https://apple.com)."),
                         '<p>See the ADR and <a href="https://apple.com">Apple</a>.</p>')

    def test_the_archive_stops_at_a_picture(self):
        with self.assertRaises(ValueError):
            archive.convert("![A picture](a.webp)")

    def test_the_archive_page_renders_through_the_shared_shell(self):
        site = Site(self)
        page = archive.build("Format version 1.\n", root=site.root)
        self.assertIn('<nav class="subnav" aria-label="Dayfolio">', page)
        self.assertIn('<meta name="apple-itunes-app" content="app-id=6817388897">', page)
        self.assertIn("<p>Format version 1.</p>", page)
        self.assertIn('<a class="backlink" href="support.html#archive">', page)


if __name__ == "__main__":
    unittest.main()

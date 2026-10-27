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


def webp(width: int, height: int, alpha: bool = False) -> bytes:
    """A WebP header (VP8X) with the canvas size, and the alpha flag a window capture's transparent corners set:
    all the build reads."""
    body = (b"VP8X" + struct.pack("<I", 10) + bytes([0x10 if alpha else 0]) + bytes(3)
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

    def test_a_long_title_drops_the_studio_name_and_keeps_the_app_name(self):
        # A search result shows about 60 characters: past 65 the studio's name
        # goes, so the words and the app's name stay in view.
        long = "Siri, Shortcuts, widgets, Control Center and Focus"
        self.site.put("content/dayfolio/guide/siri.md", topic("siri", long, 2))
        page = self.site.built()["apps/dayfolio/guide/siri/index.html"]
        self.assertIn(f"<title>{long} — Dayfolio</title>", page)
        self.assertIn("<title>Getting started — Dayfolio — NinjaApps</title>", self.page)

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
        self.assertIn('<a href="../../../../#titles">Titles</a>', page)
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

    def test_no_page_carries_a_label_above_its_title_or_a_decorative_kanji(self):
        self.site.put("content/dayfolio/guide/a.md", topic("getting-started", "Getting started", 1))
        built = self.site.built()
        for rel in ("apps/dayfolio/guide/index.html", "apps/dayfolio/guide/getting-started/index.html"):
            with self.subTest(page=rel):
                page = built[rel]
                self.assertNotIn('class="kicker', page)
                self.assertNotIn("crumbs-mark", page)
                self.assertNotRegex(page, "[←→]")  # arrows are drawn by the stylesheet, not typed
                self.assertNotRegex(page.split("<main>")[1], r"[\u3040-\u30ff\u4e00-\u9fff]")
        crumbs = re.search(r'<nav class="crumbs" aria-label="Breadcrumb">.*?</nav>',
                           built["apps/dayfolio/guide/getting-started/index.html"], re.S).group(0)
        self.assertIn('<a href="../../">Dayfolio</a>', crumbs)

    def test_the_app_box_sends_to_the_store_with_the_ticket(self):
        self.site.put("content/dayfolio/guide/a.md", topic("getting-started", "Getting started", 1))
        box = re.search(r'<aside class="appbox".*?</aside>', self.site.built()["apps/dayfolio/guide/getting-started/index.html"],
                        re.S).group(0)
        self.assertIn('<a class="ticket" href="https://apps.apple.com/app/id6817388897"><span>Get it on the App Store</span></a>',
                      box)

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
                         build.with_header(PRODUCT, "apps/dayfolio/index.html"))

    def test_an_old_sub_navigation_is_replaced(self):
        support = self.built["apps/dayfolio/support.html"]
        self.assertNotIn("an old one", support)
        self.assertRegex(support, r'<a href="support\.html" aria-current="page">Support</a>')
        self.assertEqual(support.count('class="subnav"'), 1)

    def test_every_page_asks_for_the_stylesheet_by_one_version(self):
        # Cloudflare keeps style.css at its edge, and browsers keep it, for four hours: a page whose markup needs
        # a new rule asks for the stylesheet by a new query, and every page on the site asks by the same one.
        site = Site(self)
        link = '<link rel="stylesheet" href="../../style.css{}">\n</head>'
        site.put("apps/dayfolio/index.html", PRODUCT.replace("</head>", link.format("?v=2026-01-01")))
        site.put("apps/dayfolio/support.html", SUPPORT.replace("</head>", link.format("")))
        site.put("games/smalti/index.html", f"<html><head>{link.format('')}<body></body></html>")
        site.put("privacy/index.html", "<html><head><link rel=\"stylesheet\" href=\"../style.css\">\n</head><body></body></html>")
        built = site.built()
        wanted = f'<link rel="stylesheet" href="../../style.css?v={build.STYLE_VERSION}">'
        for rel in ("apps/dayfolio/index.html", "apps/dayfolio/support.html", "games/smalti/index.html"):
            self.assertIn(wanted, built[rel])
            self.assertEqual(built[rel].count('rel="stylesheet"'), 1)
        self.assertIn(f'<link rel="stylesheet" href="../style.css?v={build.STYLE_VERSION}">', built["privacy/index.html"])
        self.assertRegex(build.STYLE_VERSION, r"^\d{4}-\d{2}-\d{2}[a-z]?$")  # the day of the change


    def test_every_page_preloads_the_title_face_once(self):
        # The title face is found only once style.css is read; on a slow phone
        # that wait holds back the first paint of every page, so each page asks
        # for it next to the stylesheet. Building twice must not ask twice.
        site = Site(self)
        site.put("games/smalti/index.html", '<html><head><link rel="stylesheet" href="../../style.css">\n</head><body></body></html>')
        site.put("privacy/index.html", '<html><head><link rel="stylesheet" href="../style.css">\n</head><body></body></html>')
        built = site.built()
        # Low priority: the face comes early but never ahead of the page's main image (a phone's LCP).
        preload = '<link rel="preload" href="{}assets/fonts/archivo-var-latin.woff2" as="font" type="font/woff2" crossorigin fetchpriority="low">'
        self.assertEqual(built["games/smalti/index.html"].count(preload.format("../../")), 1)
        self.assertEqual(built["privacy/index.html"].count(preload.format("../")), 1)
        again = build.with_stylesheet(built["privacy/index.html"], "privacy/index.html")
        self.assertEqual(again.count('rel="preload"'), 1)


def header(page: str) -> str:
    return re.search(r"<header>.*?</header>", page, re.S).group(0)


def menu(page: str) -> list:
    """The studio menu's links: (label, href, aria-current or "")."""
    return [(re.sub(r"<[^>]+>", "", text).strip(), target, current) for target, current, text in re.findall(
        r'<a href="([^"]*)"(?: aria-current="([^"]*)")?>(.*?)</a>', header(page).split("<nav>", 1)[1])]


OLD_HEADER = """<header>
  <a class="wordmark" href="../../">忍 NinjaApps</a>
  <nav>
    <a href="../../#games">Games</a>
    <a href="support.html">Support</a>
    <a href="privacy.html">Privacy</a>
    <button class="theme-toggle" id="themeToggle" aria-label="Toggle theme">◑ 夜</button>
  </nav>
</header>"""


class StudioMenuTests(unittest.TestCase):
    # The menu at the top is the studio's, the same on every page: the titles, the studio, and the
    # privacy hub. What belongs to one title (its guide, its support, its policy) is in its own band below.
    def page(self, lang: str = "en") -> str:
        return f'<html lang="{lang}"><head><link rel="stylesheet" href="../../style.css"></head><body>\n{OLD_HEADER}\n<main></main></body></html>'

    def setUp(self):
        self.site = Site(self)
        self.site.put("games/smalti/index.html", self.page())
        self.site.put("games/smalti/privacy-de.html", self.page("de"))
        self.site.put("games/smalti/daily/index.html", self.page().replace("../../", "../../../"))
        self.site.put("privacy/index.html", self.page().replace("../../", "../"))
        self.built = self.site.built()

    def test_every_page_has_the_same_studio_menu(self):
        for rel, root in (("games/smalti/index.html", "../../"), ("apps/dayfolio/index.html", "../../"),
                          ("apps/dayfolio/support.html", "../../"), ("games/smalti/daily/index.html", "../../../")):
            with self.subTest(rel):
                self.assertEqual(menu(self.built[rel]), [("Titles", root + "#titles", ""), ("Studio", root + "#studio", ""),
                                                         ("Privacy", root + "privacy/", "")])
                self.assertIn(f'<a class="wordmark" href="{root}">NinjaApps</a>', self.built[rel])

    def test_the_privacy_hub_is_marked_as_the_page_you_are_on(self):
        self.assertEqual(menu(self.built["privacy/index.html"])[2], ("Privacy", "./", "page"))

    def test_a_translated_page_has_the_menu_in_its_language(self):
        self.assertEqual([m[0] for m in menu(self.built["games/smalti/privacy-de.html"])], ["Titel", "Studio", "Datenschutz"])

    def test_the_old_marks_and_the_old_theme_button_go(self):
        page = self.built["games/smalti/index.html"]
        self.assertNotIn("忍", header(page))
        self.assertNotIn("夜", header(page))
        self.assertIn('<button class="theme-toggle" id="themeToggle" type="button" aria-label="Switch to dark theme"></button>', page)

    def test_a_game_has_its_own_band_with_the_page_marked(self):
        band = re.search(r'<nav class="subnav" aria-label="Smalti">.*?</nav>', self.built["games/smalti/daily/index.html"], re.S)
        self.assertIsNotNone(band)
        self.assertIn('<a href="./" aria-current="page">Daily</a>', band.group(0))
        self.assertIn('<a href="../support.html">Support</a>', band.group(0))

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

    def test_a_page_without_a_date_stops_the_build_and_fails_the_check(self):
        # The date is the day the page went live, from its own front matter: the build never supplies one.
        for rel, text in (("content/dayfolio/guide/b.md", source(title="B", description=f"B, {LONG}.", slug="b", order="2")),
                          ("content/dayfolio/articles/c.md", source(title="C", description=f"C, {LONG}.", slug="c"))):
            with self.subTest(page=rel):
                site = Site(self)
                site.put(rel, text)
                problems = build.check(site.root)
                self.assertEqual(len(problems), 1, problems)
                self.assertIn(f"{rel}: the field 'date' is missing", problems[0])
                with self.assertRaisesRegex(build.BuildError, "'date' is missing"):
                    build.write(site.root)

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


def mp4(*boxes: bytes) -> bytes:
    """An MP4 file's top-level boxes, empty, in the order given: all the build reads."""
    return b"".join(struct.pack(">I", 8) + kind for kind in boxes)


FLECTO_PRODUCT = PRODUCT.replace('<meta name="apple-itunes-app" content="app-id=6817388897">\n', "").replace(
    "<title>Dayfolio — NinjaApps</title>", "<title>FlectoBI — NinjaApps</title>").replace(
    "apps/dayfolio/", "apps/flectobi/").replace("<h1>Dayfolio</h1>", "<h1>FlectoBI</h1>")


def flecto_site(test: unittest.TestCase) -> "Site":
    """The Dayfolio fixture, with FlectoBI's product page, card, icon and two section pages beside it."""
    site = Site(test)
    site.put("apps/flectobi/index.html", FLECTO_PRODUCT)
    site.put("apps/flectobi/social-card.png", png(1200, 630))
    site.put("apps/flectobi/icon-320.webp", webp(320, 320))
    for key, title in (("guide", "Guide"), ("tutorials", "Tutorials")):
        site.put(f"content/flectobi/{key}/index.md", section(title))
    return site


class ClipTests(unittest.TestCase):
    """A picture line whose file is an .mp4 is a short film: a <video> a visitor starts, over its poster frame."""

    def setUp(self):
        self.site = Site(self)
        self.site.put("apps/dayfolio/guide/a/clip.mp4", mp4(b"ftyp", b"moov", b"mdat"))
        self.site.put("apps/dayfolio/guide/a/clip-poster.webp", webp(1600, 1000))

    def page(self, body: str) -> str:
        self.site.put("content/dayfolio/guide/a.md", topic("a", "A", 1, body=body))
        return self.site.built()["apps/dayfolio/guide/a/index.html"]

    def test_a_clip_is_a_figure_with_a_video_over_its_poster(self):
        page = self.page('![Adding a Step to a Flow](clip.mp4 "Add a Step, and its preview follows")\n')
        figure = re.search(r"<figure[^>]*>.*?</figure>", page, re.S).group(0)
        self.assertIn('class="figure figure-clip figure-landscape"', figure)
        video = re.search(r"<video([^>]*)>", figure).group(1)
        self.assertEqual(video, ' controls muted playsinline preload="none" poster="clip-poster.webp" '
                                'width="1600" height="1000" aria-label="Adding a Step to a Flow"')
        self.assertIn('<source src="clip.mp4" type="video/mp4">', figure)
        self.assertIn("<figcaption>Add a Step, and its preview follows</figcaption>", figure)
        self.assertNotIn("autoplay", figure)

    def test_a_clip_needs_its_poster_its_file_alt_text_and_moov_first(self):
        for body, setup, why in (
                ("![A film](clip.mp4)\n", lambda: (self.site.root / "apps/dayfolio/guide/a/clip-poster.webp").unlink(),
                 "poster"),
                ("![A film](gone.mp4)\n", lambda: None, "gone.mp4"),
                ("![](clip.mp4)\n", lambda: None, "alt"),
                ("![A film](clip.mp4)\n",
                 lambda: self.site.put("apps/dayfolio/guide/a/clip.mp4", mp4(b"ftyp", b"mdat", b"moov")), "moov")):
            with self.subTest(why=why):
                self.setUp()
                setup()
                with self.assertRaisesRegex(build.BuildError, why):
                    self.page(body)


class FlectoBITests(unittest.TestCase):
    """FlectoBI's pages come from the same shell as Dayfolio's: content/flectobi/<section>/ makes
    apps/flectobi/<section>/, with FlectoBI's sub-navigation, title and card, and no App Store id yet."""

    def setUp(self):
        self.site = flecto_site(self)
        self.site.put("content/flectobi/tutorials/first-flow.md", topic("first-flow", "Your first Flow", 1))
        self.site.put("content/flectobi/guide/inputs.md", topic("inputs", "Inputs", 1))
        self.built = self.site.built()
        self.page = self.built["apps/flectobi/tutorials/first-flow/index.html"]

    def test_the_sections_and_their_pages_are_built(self):
        for rel in ("apps/flectobi/guide/index.html", "apps/flectobi/tutorials/index.html",
                    "apps/flectobi/guide/inputs/index.html", "apps/flectobi/tutorials/first-flow/index.html"):
            self.assertIn(rel, self.built)
        self.assertIn("apps/dayfolio/guide/index.html", self.built)  # Dayfolio's are still built beside them

    def test_the_head_names_flectobi_and_carries_no_banner_without_a_store_id(self):
        page, url = self.page, "https://ninjaapps.net/apps/flectobi/tutorials/first-flow/"
        self.assertIn("<title>Your first Flow — FlectoBI — NinjaApps</title>", page)
        self.assertIn(f'<link rel="canonical" href="{url}">', page)
        self.assertEqual(meta(page, "og:image"), "https://ninjaapps.net/apps/flectobi/social-card.png")
        self.assertIn("FlectoBI", meta(page, "og:image:alt"))
        self.assertNotIn("apple-itunes-app", page)
        self.assertNotIn("apps.apple.com", page)
        self.assertIsNone(build.FLECTOBI_STORE_ID)

    def test_the_sub_navigation_is_flectobis(self):
        nav = re.search(r'<nav class="subnav" aria-label="FlectoBI">.*?</nav>', self.page, re.S).group(0)
        links = re.findall(r'<a (?:class="[^"]*" )?href="([^"]+)"(?: aria-current="(\w+)")?>([^<]+)</a>', nav)
        self.assertEqual([(href, label) for href, _, label in links], [
            ("../../", "FlectoBI"), ("../../", "Overview"), ("../../guide/", "Guide"), ("../", "Tutorials"),
            ("../../support.html", "Support")])
        self.assertEqual([label for _, current, label in links if current], ["Tutorials"])

    def test_json_ld_and_breadcrumbs_name_flectobi(self):
        blocks = {block["@type"]: block for block in jsonld(self.page)}
        self.assertEqual(blocks["Article"]["about"]["name"], "FlectoBI")
        self.assertEqual([item["name"] for item in blocks["BreadcrumbList"]["itemListElement"]],
                         ["FlectoBI", "Tutorials", "Your first Flow"])
        self.assertIn('<h1 class="page-title">Tutorials</h1>', self.built["apps/flectobi/tutorials/index.html"])
        self.assertIn("content/flectobi/tutorials/first-flow.md", self.page)

    def test_the_app_box_says_where_flectobi_is_coming_without_a_link_or_a_price(self):
        box = re.search(r'<aside class="appbox".*?</aside>', self.page, re.S).group(0)
        self.assertIn('<span class="ticket-soon">Coming to the Mac App Store</span>', box)
        self.assertNotRegex(box, r"<a [^>]*>[^<]*Coming to the Mac App Store")
        self.assertNotRegex(box, r"\$\d|(?i:\bfree\b)")
        self.assertIn('src="../../icon-320.webp"', box)

    def test_with_a_store_id_every_page_carries_the_banner_and_the_box_links_the_store(self):
        original = build.FLECTOBI_STORE_ID
        self.addCleanup(build.set_store_id, "flectobi", original)
        build.set_store_id("flectobi", "1234567890")
        page = self.site.built()["apps/flectobi/tutorials/first-flow/index.html"]
        self.assertIn('<meta name="apple-itunes-app" content="app-id=1234567890">', page)
        self.assertIn('href="https://apps.apple.com/app/id1234567890"', page)
        self.assertNotIn("Coming to the Mac App Store", page)

    def test_the_hand_written_pages_get_the_sub_navigation_and_the_stylesheet(self):
        product = self.built["apps/flectobi/index.html"]
        self.assertRegex(product, r'</header>\n\n<nav class="subnav" aria-label="FlectoBI">')
        self.assertRegex(product, r'<a href="\./" aria-current="page">Overview</a>')
        self.assertNotIn('aria-label="Dayfolio"', product)

    def test_the_sitemap_lists_flectobis_pages(self):
        urls = [loc.text for loc in ET.fromstring(self.built["sitemap.xml"]).iter(
            "{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
        for url in ("https://ninjaapps.net/apps/flectobi/", "https://ninjaapps.net/apps/flectobi/tutorials/",
                    "https://ninjaapps.net/apps/flectobi/tutorials/first-flow/"):
            self.assertIn(url, urls)

    def test_a_window_capture_is_drawn_wide_with_a_shadow_on_flectobi_only(self):
        self.site.put("apps/flectobi/guide/inputs/window.webp", webp(2400, 1500, alpha=True))
        self.site.put("apps/flectobi/guide/inputs/opaque.webp", webp(2400, 1500))
        self.site.put("content/flectobi/guide/inputs.md", topic("inputs", "Inputs", 1, body=(
            "![A window](window.webp)\n\n![An opaque picture](opaque.webp)\n")))
        self.site.put("apps/dayfolio/guide/a/window.webp", webp(2400, 1500, alpha=True))
        self.site.put("content/dayfolio/guide/a.md", topic("a", "A", 1, body="![A window](window.webp)\n"))
        built = self.site.built()
        flecto = built["apps/flectobi/guide/inputs/index.html"]
        self.assertIn('<figure class="figure figure-landscape figure-wide figure-window"><img src="window.webp"', flecto)
        self.assertIn('<figure class="figure figure-landscape figure-wide"><img src="opaque.webp"', flecto)
        self.assertIn('<figure class="figure figure-landscape"><img src="window.webp"',
                      built["apps/dayfolio/guide/a/index.html"])

    def test_after_a_build_the_check_is_clean_and_a_drifted_page_is_named(self):
        build.write(self.site.root)
        self.assertEqual(build.check(self.site.root), [])
        rel = "apps/flectobi/guide/inputs/index.html"
        self.site.put(rel, self.site.read(rel).replace("Some words.", "Hand edit."))
        self.assertTrue(any(rel in p for p in build.check(self.site.root)))


class StylesheetTests(unittest.TestCase):
    """Every class the shell writes on a figure, a clip or the app box has a rule in the site's style.css, in
    both themes where it draws a colour."""

    def setUp(self):
        self.css = (TOOLS.parent / "style.css").read_text(encoding="utf-8")

    def test_the_figure_clip_and_box_classes_have_rules(self):
        for selector in (".figure-clip", ".figure-wide", ".figure-window", ".btn-soon",
                         '.subnav[aria-label="FlectoBI"] .subnav-app::before'):
            with self.subTest(selector=selector):
                self.assertTrue(selector in self.css, f"style.css has no {selector}")
        self.assertTrue("assets/icon-flectobi-144.webp" in self.css, "no FlectoBI icon in the sub-navigation")
        self.assertTrue(re.search(r'\[data-theme="dark"\][^{]*\.figure-window', self.css),
                        "no dark-theme shadow for a window capture")

    def test_the_stylesheet_is_asked_for_by_the_day_its_figure_rules_came(self):
        self.assertGreaterEqual(build.STYLE_VERSION, "2026-10-27")

    def test_the_ticket_and_the_crumbs_have_rules(self):
        for selector in (".ticket", ".ticket-soon", ".crumbs", ".appbox"):
            with self.subTest(selector=selector):
                self.assertIn(selector + " ", self.css)


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

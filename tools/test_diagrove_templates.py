#!/usr/bin/env python3
"""Tests for tools/diagrove-templates.py, Diagrove's template gallery. Standard library only (the one test of
the picture step needs Pillow, as that step does, and is skipped without it):

    python3 -m unittest discover -s tools -p 'test_*.py'

Each test builds a tiny site in a temporary folder (test_dayfolio_build.py's Diagrove fixture: the product page
the shell takes its header and footer from, the social card, the icon), adds a catalogue of four templates in
three categories, the site's notes on them and their pictures, and runs the generator there. Nothing touches the
real site.
"""

from __future__ import annotations

import copy
import json
import os
import re
import stat
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

import test_dayfolio_build as tb

templates = tb.load("diagrove_templates", "diagrove-templates.py")
build = tb.build


def canvas(name, size=(816, 584), projection="flat", layers=("Steps",)):
    return {"name": name, "size": list(size), "projection": projection, "layers": list(layers)}


CATALOG = {
    "formatVersion": 1,
    "source": "diagrove 1.0 (the app's own templates, in British English)",
    "categories": [
        {"id": "blank", "name": "Blank"},
        {"id": "process", "name": "Process"},
        {"id": "product", "name": "Product"},
    ],
    "templates": [
        {"id": "blank", "name": "Blank diagram", "summary": "An empty canvas to draw on", "category": "blank",
         "blank": True, "isometric": False, "searchWords": ["empty", "whiteboard"],
         "canvases": [canvas("Diagram", (1024, 768), layers=("Layer 1",))], "stencils": [], "connections": 0,
         "plays": False, "binds": False},
        {"id": "flowchart", "name": "Flowchart", "summary": "A bike repair across three swimlanes",
         "category": "process", "blank": False, "isometric": False,
         "searchWords": ["flow chart", "swimlane", "decision"],
         "canvases": [canvas("Bike repair", layers=("Lanes", "Steps", "Key"))],
         "stencils": [{"id": "flowchart.decision", "name": "Decision", "library": "Flowchart"},
                      {"id": "flowchart.terminator", "name": "Start or end", "library": "Flowchart"},
                      {"id": "basic.rounded", "name": "Rounded rectangle", "library": "Basic shapes"}],
         "connections": 12, "plays": False, "binds": False},
        {"id": "orderFulfilment", "name": "Order fulfilment", "summary": "Stations along a belt, from picking to the van",
         "category": "process", "blank": False, "isometric": True, "searchWords": ["pick and pack", "warehouse"],
         "canvases": [canvas("Order fulfilment", (1096, 959), "isometric", ("Floor", "Belt", "Labels"))],
         "stencils": [{"id": "iso.warehouse.conveyor", "name": "Conveyor", "library": "Isometric warehouse"}],
         "connections": 3, "plays": False, "binds": False},
        {"id": "appScreen", "name": "App screen", "summary": "Two phone screens you can tap through in Play",
         "category": "product", "blank": False, "isometric": False, "searchWords": ["mockup", "prototype"],
         "canvases": [canvas("Projects", (720, 786)), canvas("Website", (720, 786))],
         "stencils": [{"id": "ui.phone", "name": "Phone", "library": "Interface"}],
         "connections": 0, "plays": True, "binds": False},
    ],
}

NOTES = {
    "categories": {
        "blank": "Start from nothing: a flat canvas or an isometric one.",
        "process": "Steps, decisions and handoffs, from a swimlane flowchart to a pick-and-pack line.",
        "product": "Screens, flows and pages for the apps and sites you design.",
    },
    "templates": {
        "blank": {"for": "Use it when you know what you want to draw."},
        "flowchart": {"for": "Use a flowchart to show how work moves from step to step, and where it waits on a yes.",
                      "page_title": "Swimlane flowchart template"},
        "orderFulfilment": {"for": "Show the stations an order passes on its way out of a warehouse."},
        "appScreen": {"for": "Sketch an app’s screens and tap through them before anyone writes code."},
    },
}

PICTURES = {  # the template's folder, from apps/diagrove/templates/: its pictures and their sizes
    "process/flowchart": {"flowchart-white.webp": (1632, 1168), "flowchart-ink.webp": (1632, 1168),
                          "flowchart-card.webp": (960, 687)},
    "process/order-fulfilment": {"order-fulfilment-white.webp": (2192, 1918), "order-fulfilment-ink.webp": (2192, 1918),
                                 "order-fulfilment-card.webp": (960, 840)},
    "product/app-screen": {"app-screen-white.webp": (1440, 1572), "app-screen-white-2.webp": (1440, 1572),
                           "app-screen-ink.webp": (1440, 1572), "app-screen-ink-2.webp": (1440, 1572),
                           "app-screen-card.webp": (960, 1048)},
}

OUT = "apps/diagrove/templates"
FLOWCHART = f"{OUT}/process/flowchart/index.html"
APP_SCREEN = f"{OUT}/product/app-screen/index.html"
ISO = f"{OUT}/process/order-fulfilment/index.html"
BLANK = f"{OUT}/blank/blank-diagram/index.html"
PROCESS = f"{OUT}/process/index.html"
GALLERY = f"{OUT}/index.html"


class Site(tb.Site):
    """The build's Diagrove fixture, with a catalogue, its notes and the pictures beside the pages."""

    def __init__(self, test: unittest.TestCase, catalog=None, notes=None, pictures=None):
        super().__init__(test)
        for rel, data in (("apps/diagrove/index.html", tb.DIAGROVE_PRODUCT),
                          ("apps/diagrove/social-card.png", tb.png(1200, 630)),
                          ("apps/diagrove/icon-320.webp", tb.webp(320, 320))):
            self.put(rel, data)
        self.put(templates.CATALOG, json.dumps(CATALOG if catalog is None else catalog, ensure_ascii=False, indent=2))
        self.put(templates.NOTES, json.dumps(NOTES if notes is None else notes, ensure_ascii=False, indent=2))
        for folder, files in (PICTURES if pictures is None else pictures).items():
            for name, (width, height) in files.items():
                self.put(f"{OUT}/{folder}/{name}", tb.webp(width, height))

    def pages(self) -> dict:
        return templates.build(self.root)


def changed(data: dict, change) -> dict:
    data = copy.deepcopy(data)
    change(data)
    return data


def visible(page: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", re.sub(r"<(script|style)\b.*?</\1>|<!--.*?-->", "", page,
                                                                    flags=re.S)))


class CatalogueTests(unittest.TestCase):
    def test_categories_and_templates_keep_the_apps_order_and_get_readable_addresses(self):
        catalog = templates.load_catalog(Site(self).root)
        self.assertEqual([c.id for c in catalog.categories], ["blank", "process", "product"])
        self.assertEqual([t.id for t in catalog.listed("process")], ["flowchart", "orderFulfilment"])
        self.assertEqual(sorted(Site(self).pages()), sorted([
            GALLERY, f"{OUT}/blank/index.html", PROCESS, f"{OUT}/product/index.html",
            BLANK, FLOWCHART, ISO, APP_SCREEN]))

    def test_an_address_is_the_name_in_lowercase_words(self):
        self.assertEqual([templates.slug(n) for n in ("CI/CD pipeline", "SWOT", "Ideas and teams", "Data centre",
                                                       "Before and after", "OKR tree")],
                         ["ci-cd-pipeline", "swot", "ideas-and-teams", "data-centre", "before-and-after", "okr-tree"])

    def test_a_catalogue_the_generator_cannot_trust_is_named(self):
        for change, needle in (
                (lambda c: c["templates"][1].update(category="ideas"), "ideas"),
                (lambda c: c["templates"][1].pop("summary"), "summary"),
                (lambda c: c["templates"].append(copy.deepcopy(c["templates"][1])), "twice"),
                (lambda c: c.update(formatVersion=2), "formatVersion")):
            with self.subTest(needle=needle), self.assertRaises(templates.CatalogError) as caught:
                Site(self, catalog=changed(CATALOG, change)).pages()
            self.assertIn("catalog.json", str(caught.exception))
            self.assertIn(needle, str(caught.exception))


class NotesTests(unittest.TestCase):
    def problem(self, **site) -> str:
        with self.assertRaises(templates.CatalogError) as caught:
            Site(self, **site).pages()
        return str(caught.exception)

    def test_every_template_and_category_needs_the_sites_words(self):
        self.assertIn("appScreen", self.problem(notes=changed(NOTES, lambda n: n["templates"].pop("appScreen"))))
        self.assertIn("product", self.problem(notes=changed(NOTES, lambda n: n["categories"].pop("product"))))

    def test_a_note_for_a_template_the_app_does_not_have_is_named(self):
        message = self.problem(notes=changed(NOTES, lambda n: n["templates"].update(ganttChart={"for": "Plans."})))
        self.assertIn("ganttChart", message)

    def test_notes_follow_the_sites_copy_rules(self):
        for text, needle in (('A "quoted" word.', "straight"), ("Draw it now!", "exclamation")):
            with self.subTest(needle=needle):
                message = self.problem(notes=changed(NOTES, lambda n: n["templates"]["flowchart"].update({"for": text})))
                self.assertIn("notes.json", message)
                self.assertIn(needle, message.lower())

    def test_a_template_with_a_drawing_needs_its_pictures(self):
        pictures = changed(PICTURES, lambda p: p["process/flowchart"].pop("flowchart-ink.webp"))
        message = self.problem(pictures=pictures)
        self.assertIn("flowchart-ink.webp", message)
        self.assertIn("--app", message)


class TemplatePageTests(unittest.TestCase):
    def setUp(self):
        self.pages = Site(self).pages()
        self.page = self.pages[FLOWCHART]

    def test_the_title_is_the_words_people_search_for_or_the_name_and_template(self):
        self.assertIn("<title>Swimlane flowchart template — Diagrove — NinjaApps</title>", self.page)
        self.assertIn('<h1 class="page-title">Swimlane flowchart template</h1>', self.page)
        self.assertIn("<title>App screen template — Diagrove — NinjaApps</title>", self.pages[APP_SCREEN])

    def test_it_shows_the_template_on_white_and_on_ink_paper_as_the_app_renders_it(self):
        figures = re.findall(r'<figure class="([^"]+)"><img src="([^"]+)" alt="([^"]+)" width="(\d+)" height="(\d+)"',
                             self.page)
        self.assertEqual([(f[1], f[3], f[4]) for f in figures],
                         [("flowchart-white.webp", "1632", "1168"), ("flowchart-ink.webp", "1632", "1168")])
        self.assertIn("figure-landscape", figures[0][0])
        self.assertIn("White paper", figures[0][2])
        self.assertIn("Ink paper", figures[1][2])
        self.assertIn("a bike repair across three swimlanes", figures[0][2])
        self.assertIn('loading="lazy"', self.page.split('flowchart-ink.webp"', 1)[1].split(">", 1)[0])

    def test_every_canvas_of_a_template_has_its_picture(self):
        page = self.pages[APP_SCREEN]
        for name in ("app-screen-white.webp", "app-screen-white-2.webp", "app-screen-ink.webp", "app-screen-ink-2.webp"):
            self.assertIn(f'src="{name}"', page)
        self.assertIn("Projects", visible(page))
        self.assertIn("Website", visible(page))

    def test_it_says_what_it_is_for_and_what_is_in_it(self):
        words = visible(self.page)
        self.assertIn("A bike repair across three swimlanes", words)
        self.assertIn("Use a flowchart to show how work moves from step to step", words)
        self.assertIn("Bike repair", words)            # the canvas
        self.assertIn("816 × 584", words)
        self.assertIn("Lanes, Steps and Key", words)   # the layers
        self.assertIn("Decision", words)               # a stencil, with its library
        self.assertIn("Flowchart library", words)
        self.assertIn("12 connected lines", words)
        self.assertIn("“flow chart”, “swimlane” and “decision”", words)

    def test_an_isometric_template_says_so_and_links_the_guide(self):
        words = visible(self.pages[ISO])
        self.assertIn("isometric", words.lower())
        self.assertIn('href="../../../guide/isometric-canvases/"', self.pages[ISO])

    def test_a_template_that_plays_says_how_to_play_it(self):
        words = visible(self.pages[APP_SCREEN])
        self.assertIn("Play", words)
        self.assertIn("Option-Command-P", words)
        self.assertNotIn("Option-Command-P", visible(self.page))

    def test_it_says_how_to_start_from_it_on_the_mac_the_ipad_and_the_command_line(self):
        words = visible(self.page)
        self.assertIn("File › New from template…", words)
        self.assertIn("Shift-Command-N", words)
        self.assertIn("Choose a template", words)
        self.assertIn("diagrove new --template flowchart --paper dark", words)
        self.assertIn("Flowchart 2", words)

    def test_it_links_its_category_related_templates_the_guide_and_the_app_box(self):
        page = self.page
        self.assertIn('href="../"', page)                                    # Process
        self.assertIn('href="../order-fulfilment/"', page)                  # related, in its category
        self.assertNotIn('href="../../product/app-screen/"', page)
        self.assertIn('href="../../../guide/templates/"', page)
        self.assertIn('<aside class="appbox"', page)
        self.assertIn('<span class="ticket-soon">Coming to the App Store</span>', page)

    def test_a_blank_template_has_no_picture_and_says_why(self):
        page = self.pages[BLANK]
        self.assertNotIn("<figure", page)
        self.assertIn("empty", visible(page).lower())

    def test_json_ld_names_the_breadcrumbs(self):
        blocks = {b["@type"]: b for b in tb.jsonld(self.page)}
        self.assertEqual([i["name"] for i in blocks["BreadcrumbList"]["itemListElement"]],
                         ["Diagrove", "Templates", "Process", "Flowchart"])


class ListingPageTests(unittest.TestCase):
    def setUp(self):
        self.pages = Site(self).pages()

    def test_a_category_page_shows_a_card_for_each_template_with_its_picture(self):
        page = self.pages[PROCESS]
        self.assertIn('<h1 class="page-title">Process templates</h1>', page)
        cards = re.findall(r'<a class="card tpl-card" href="([^"]+)">\s*<img src="([^"]+)" alt="([^"]+)" width="(\d+)" '
                           r'height="(\d+)" loading="lazy">', page)
        self.assertEqual(cards, [("flowchart/", "flowchart/flowchart-card.webp", "Flowchart on White paper", "960", "687"),
                                 ("order-fulfilment/", "order-fulfilment/order-fulfilment-card.webp",
                                  "Order fulfilment on White paper", "960", "840")])
        self.assertIn("Steps, decisions and handoffs", visible(page))
        self.assertIn("ItemList", page)

    def test_the_gallery_counts_and_lists_every_category_and_template(self):
        page = self.pages[GALLERY]
        words = visible(page)
        self.assertIn("3 templates in 2 categories", words)
        for name in ("Blank diagram", "Flowchart", "Order fulfilment", "App screen"):
            self.assertIn(name, words)
        self.assertIn('href="process/"', page)
        self.assertIn('href="process/flowchart/"', page)
        self.assertIn('href="../guide/templates/"', page)
        self.assertIn("plus a blank diagram.", words)

    def test_the_gallery_shows_each_category_by_the_picture_of_its_first_template(self):
        page = self.pages[GALLERY]
        art = re.findall(r'<a class="pack-art" href="([^"]+)"><img src="([^"]+)" alt="([^"]+)" width="\d+" '
                         r'height="\d+" loading="lazy"></a>', page)
        self.assertEqual(art, [("process/", "process/flowchart/flowchart-card.webp",
                                "The Process templates, such as Flowchart"),
                               ("product/", "product/app-screen/app-screen-card.webp",
                                "The Product templates, such as App screen")])

    def test_titles_and_descriptions_fit_search_results_and_differ(self):
        titles, descriptions = set(), set()
        for rel, page in self.pages.items():
            with self.subTest(rel=rel):
                title = re.search(r"<title>(.*?)</title>", page).group(1)
                description = re.search(r'<meta name="description" content="([^"]*)">', page).group(1)
                self.assertLessEqual(len(title), 65)
                self.assertTrue(build.DESCRIPTION_MIN <= len(description) <= build.DESCRIPTION_MAX, description)
                titles.add(title)
                descriptions.add(description)
        self.assertEqual(len(titles), len(self.pages))
        self.assertEqual(len(descriptions), len(self.pages))

    def test_each_page_is_held_generated_and_carries_diagroves_band_and_colours(self):
        for rel, page in self.pages.items():
            with self.subTest(rel=rel):
                self.assertIn('<meta name="robots" content="noindex">', page)
                self.assertIn(f"<!-- {templates.GENERATED} from ", page)
                self.assertIn('<nav class="subnav" aria-label="Diagrove">', page)
                self.assertEqual(page.count('<style data-app="diagrove">'), 1)
                self.assertIn('>Templates</a>', page)
        self.assertIn('<a href="./" aria-current="page">Templates</a>', self.pages[GALLERY])


class WriteAndCheckTests(unittest.TestCase):
    def test_after_a_write_the_check_is_clean_and_the_build_leaves_the_pages_alone(self):
        site = Site(self)
        templates.write(site.root)
        self.assertEqual(templates.check(site.root), [])
        build.write(site.root)
        self.assertEqual(templates.check(site.root), [])
        self.assertEqual(build.check(site.root), [])
        self.assertNotIn("apps/diagrove/templates", site.read("sitemap.xml"))  # held: noindex

    def test_the_check_names_a_page_that_differs_and_one_whose_template_left(self):
        site = Site(self)
        templates.write(site.root)
        page = site.root / FLOWCHART
        page.write_text(page.read_text(encoding="utf-8").replace("Bike repair", "Bike"), encoding="utf-8")
        catalog = changed(CATALOG, lambda c: c["templates"].pop(2))
        notes = changed(NOTES, lambda n: n["templates"].pop("orderFulfilment"))
        site.put(templates.CATALOG, json.dumps(catalog))
        site.put(templates.NOTES, json.dumps(notes))
        problems = "\n".join(templates.check(site.root))
        self.assertIn(FLOWCHART, problems)
        self.assertIn(ISO, problems)
        templates.write(site.root)
        self.assertFalse((site.root / ISO).exists())

    def test_a_site_without_the_catalogue_has_nothing_to_check(self):
        site = tb.Site(self)
        self.assertEqual(templates.check(site.root), [])


class AppSourceTests(unittest.TestCase):
    """The --app step reads the app's own words and pictures: its templates from the command-line tool, their
    British spellings and search words from the app's String Catalog, and renders of every canvas on both papers."""

    def test_search_words_come_from_the_catalog_in_british_english(self):
        strings = {"sourceLanguage": "en", "strings": {
            "data center, data centre, server room": {
                "comment": "Search words for the template dataCentre, comma separated: the names people give",
                "localizations": {"en": {"stringUnit": {"value": "data center, data centre, server room"}},
                                  "en-GB": {"stringUnit": {"value": "data centre, data center, server room"}}}},
            "gantt, gantt chart": {"comment": "Search words for the template projectPlan, comma separated",
                                   "localizations": {"en": {"stringUnit": {"value": "gantt, gantt chart"}}}}}}
        words = templates.search_words(strings)
        self.assertEqual(words["dataCentre"], ["data centre", "data center", "server room"])
        self.assertEqual(words["projectPlan"], ["gantt", "gantt chart"])

    def test_what_is_in_a_template_is_read_from_its_text_and_structure(self):
        text = textwrap.dedent("""\
            canvas "Start" {
              size: 720, 786
              layer "Screen" {
                phone { stencil: ui.phone; at: 0, 0; size: 390, 844 }
                go: "Next" { on-click: go "Website" }
                b { stencil: basic.rounded; at: 0, 0 }
                c { stencil: ui.phone; at: 9, 9 }
              }
            }
            canvas "Website" {
              projection: isometric
              layer "Page" { t: "Hi" { bind text: var name } }
            }
            """)
        inspect = {"canvases": [
            {"name": "Start", "size": [720, 786], "layers": [{"name": "Screen"}],
             "graphics": [{"kind": "line", "from": "go.right", "to": "b.left"}, {"kind": "shape"},
                          {"kind": "line", "from": "(0, 0)", "to": "b.top"},
                          {"kind": "line", "from": "b.bottom", "to": "c.top"}]},
            {"name": "Website", "size": [720, 786], "layers": [{"name": "Page"}], "graphics": [{"kind": "shape"}]}]}
        stencils = {"ui.phone": {"id": "ui.phone", "name": "Phone", "library": "Interface"},
                    "basic.rounded": {"id": "basic.rounded", "name": "Rounded rectangle", "library": "Basic shapes"}}
        facts = templates.contents(text, inspect, stencils)
        self.assertEqual(facts["canvases"], [canvas("Start", (720, 786), "flat", ("Screen",)),
                                             canvas("Website", (720, 786), "isometric", ("Page",))])
        self.assertEqual([s["id"] for s in facts["stencils"]], ["ui.phone", "basic.rounded"])
        self.assertEqual(facts["connections"], 2)  # a line with a free end connects nothing
        self.assertTrue(facts["plays"])
        self.assertTrue(facts["binds"])

    @unittest.skipUnless(templates.has_pillow(), "the picture step needs Pillow")
    def test_the_app_step_writes_the_catalogue_and_a_webp_of_every_canvas_on_both_papers(self):
        site = tb.Site(self)
        app = Path(tempfile.mkdtemp())
        self.addCleanup(lambda: __import__("shutil").rmtree(app, ignore_errors=True))
        strings = app / templates.APP_STRINGS
        strings.parent.mkdir(parents=True)
        strings.write_text(json.dumps({"sourceLanguage": "en", "strings": {}}), encoding="utf-8")
        cli = app / "fake-diagrove"
        cli.write_text(FAKE_CLI.replace("PYTHON", sys.executable), encoding="utf-8")
        cli.chmod(cli.stat().st_mode | stat.S_IEXEC)
        templates.sync(site.root, app, cli)
        catalog = json.loads(site.read(templates.CATALOG))
        self.assertEqual([t["id"] for t in catalog["templates"]], ["blank", "flowchart"])
        self.assertEqual(catalog["templates"][1]["name"], "Flowchart")
        self.assertEqual(catalog["templates"][1]["canvases"][0]["name"], "Bike repair")
        folder = site.root / OUT / "process/flowchart"
        self.assertEqual(sorted(p.name for p in folder.iterdir()),
                         ["flowchart-card.webp", "flowchart-ink.webp", "flowchart-white.webp"])
        self.assertEqual(build.image_size(folder / "flowchart-white.webp"), (64, 48))
        self.assertEqual(build.image_size(folder / "flowchart-card.webp"), (64, 48))  # never upscaled
        self.assertFalse(build.has_alpha(folder / "flowchart-white.webp"))
        self.assertFalse((site.root / OUT / "blank").exists())                         # a blank one has no picture


# A stand-in for the diagrove command-line tool: the answers the --app step reads, and a 64 × 48 PNG for render.
FAKE_CLI = """#!PYTHON
import json, sys, struct, zlib
args = sys.argv[1:]
def out(data): print(json.dumps(dict(ok=True, **data)))
def png(path):
    raw = b"".join(b"\\x00" + b"\\xff\\x80\\x00" * 64 for _ in range(48))
    def chunk(kind, data): return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))
    open(path, "wb").write(b"\\x89PNG\\r\\n\\x1a\\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", 64, 48, 8, 2, 0, 0, 0))
                           + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b""))
flow = {"id": "flowchart", "name": "Flowchart", "description": "A bike repair across three swimlanes",
        "category": "process", "categoryName": "Process", "blank": False, "isometric": False}
blank = {"id": "blank", "name": "Blank diagram", "description": "An empty canvas to draw on",
         "category": "blank", "categoryName": "Blank", "blank": True, "isometric": False}
if args[:2] == ["templates", "list"]:
    out({"templates": [blank, flow], "count": 2})
elif args[:2] == ["stencils", "list"]:
    out({"stencils": [{"id": "flowchart.decision", "name": "Decision", "library": "Flowchart"}]})
elif args[0] == "--version":
    print("1.0")
elif args[0] == "new":
    open(args[args.index("-o") + 1], "w").write(args[args.index("--template") + 1])
    out({})
elif args[0] == "text":
    name = open(args[1]).read()
    out({"text": 'canvas "Bike repair" {\\n  d { stencil: flowchart.decision }\\n}\\n' if name == "flowchart"
         else 'canvas "Diagram" {\\n}\\n'})
elif args[0] == "inspect":
    name = open(args[1]).read()
    out({"document": {"canvases": [{"name": "Bike repair" if name == "flowchart" else "Diagram", "size": [32, 24],
                                    "layers": [{"name": "Steps"}], "graphics": []}]}})
elif args[0] == "render":
    png(args[args.index("-o") + 1])
    out({"width": 64, "height": 48})
else:
    sys.exit("unexpected: " + " ".join(args))
"""


if __name__ == "__main__":
    unittest.main()

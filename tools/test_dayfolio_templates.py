#!/usr/bin/env python3
"""Tests for tools/dayfolio-templates.py, the template gallery. Standard library only:

    python3 -m unittest discover -s tools -p 'test_*.py'

Each test builds a tiny site in a temporary folder (test_dayfolio_build.py's fixture: the
product page the shell takes its header and footer from, the social card, the icon), adds a
two-pack library and its examples, and runs the generator there. Nothing touches the real site.
"""

from __future__ import annotations

import copy
import json
import re
import unittest
from pathlib import Path

import test_dayfolio_build as tb

templates = tb.load("dayfolio_templates", "dayfolio-templates.py")
build = tb.build

STATUS = [{"key": "on-track", "label": "On track", "color": "success"},
          {"key": "at-risk", "label": "At risk", "color": "warning"},
          {"key": "blocked", "label": "Blocked", "color": "danger"}]

GENERAL = {"formatVersion": 1, "pack": {
    "id": "general", "industry": "General", "name": "General", "journalName": "Work Log",
    "summary": "Weekly reviews, 1:1s and decisions that fit any kind of work.", "icon": "tray", "color": "slate",
    "order": 0, "defaultTemplate": "general.weekly-review",
    "templates": [
        {"id": "general.weekly-review", "version": 2, "name": "Weekly review", "icon": "calendar", "color": "orange",
         "cadence": "review", "summary": "Energy, mood, wins and lessons — a personal check-in for any job.",
         "includedByDefault": True, "reminder": {"weekdays": [6], "hour": 17, "minute": 0},
         "fields": [
             {"key": "energy", "label": "Energy", "type": "rating"},
             {"key": "mood", "label": "Mood", "type": "mood"},
             {"key": "tags", "label": "Tags", "type": "tags"},
             {"key": "wins", "label": "Wins", "type": "checklist", "prompt": "What went well this week?"},
             {"key": "challenges", "label": "Challenges", "type": "text", "prompt": "What was hard, and why?"},
             {"key": "notes", "label": "Notes", "type": "richText",
              "prompt": "Anything else worth remembering about this week?"}]},
        {"id": "general.1-1-notes", "version": 1, "name": "1:1 notes", "icon": "person.2", "color": "blue",
         "cadence": "onEvent", "summary": "Any recurring one-on-one — with a manager, a mentor, a peer or a report.",
         "includedByDefault": True,
         "fields": [
             {"key": "person", "label": "With", "type": "person"},
             {"key": "meeting-time", "label": "Meeting time", "type": "timeRange"},
             {"key": "action-items", "label": "Action items", "type": "checklist", "carryOver": True,
              "prompt": "What’s still open from last time, and what’s new?"}]}]}}

ENGINEERING = {"formatVersion": 1, "pack": {
    "id": "software-engineering", "industry": "Engineering", "name": "Software Engineering",
    "journalName": "Engineering Log", "summary": "Standups, incidents, plans and reviews for people who ship software.",
    "icon": "chevron.left.forwardslash.chevron.right", "color": "orange", "order": 1,
    "defaultTemplate": "software-engineering.daily-standup", "keywords": ["deploy"],
    "includes": ["general.weekly-review"],
    "templates": [
        {"id": "software-engineering.daily-standup", "version": 3, "name": "Daily standup", "icon": "checklist",
         "color": "orange", "cadence": "daily", "summary": "What you shipped, what you’re on and what’s in the way.",
         "includedByDefault": True, "reminder": {"weekdays": [2, 3, 4, 5, 6], "hour": 9, "minute": 0},
         "fields": [
             {"key": "focus-time", "label": "Focus time", "type": "duration"},
             {"key": "project", "label": "Project", "type": "project", "carryOver": True},
             {"key": "status", "label": "Status", "type": "singleSelect", "options": STATUS},
             {"key": "channels", "label": "Channels", "type": "multiSelect",
              "options": [{"key": "email", "label": "Email", "color": "purple"},
                          {"key": "social", "label": "Social", "color": "info"}]},
             {"key": "pages", "label": "Pages", "type": "number"},
             {"key": "due", "label": "Due date", "type": "date"},
             {"key": "doc", "label": "Doc", "type": "link"},
             {"key": "shipped", "label": "Shipped", "type": "checklist",
              "prompt": "What did you finish since the last standup?"},
             {"key": "blockers", "label": "Blockers", "type": "text", "presentation": "warning",
              "prompt": "Anything in your way?"},
             {"key": "screens", "label": "Screens", "type": "attachment"}]}]}}

EXAMPLES = {
    "general": {
        "general.weekly-review": {"date": "2026-10-16 17:05", "values": {
            "energy": 4, "mood": 5, "tags": ["release", "hiring"],
            "wins": ["[x] Shipped the retry queue", "[ ] Wrote the runbook"],
            "challenges": "Two days lost to a flaky test.",
            "notes": "Pairing helped.\n\n- Keep Friday demos\n- Ask for **one** reviewer"}},
        "general.1-1-notes": {"date": "2026-10-13 10:30", "page_title": "1:1 meeting notes template", "values": {
            "person": ["Maya Ferreira"], "meeting-time": "10:00–10:30",
            "action-items": ["[ ] Draft the hiring plan"]}}},
    "software-engineering": {
        "software-engineering.daily-standup": {"date": "2026-10-15 09:12", "title": "Retry queue is in", "values": {
            "focus-time": 330, "project": ["Payments API", "Observability"], "status": "on-track",
            "channels": ["email", "social"], "pages": 3, "due": "2026-10-23",
            "doc": {"title": "Retry design", "url": "https://docs.example.com/retry"},
            "shipped": ["[x] Retry queue for webhook delivery"],
            "blockers": "Waiting on a staging snapshot.",
            "screens": [["dashboard.png", "PNG picture · 180 KB"]]}}},
}

TEMPLATE_PAGES = ["apps/dayfolio/templates/general/weekly-review/index.html",
                  "apps/dayfolio/templates/general/1-1-notes/index.html",
                  "apps/dayfolio/templates/software-engineering/daily-standup/index.html"]
STANDUP = TEMPLATE_PAGES[2]
GALLERY = "apps/dayfolio/templates/index.html"


class Site(tb.Site):
    """The build's fixture, with the gallery's Markdown gone (this tool owns the gallery) and a library."""

    def __init__(self, test: unittest.TestCase, packs=(GENERAL, ENGINEERING), examples=None):
        super().__init__(test)
        (self.root / "content/dayfolio/templates/index.md").unlink()
        for pack in packs:
            self.put(f"{templates.LIBRARY}/{pack['pack']['id']}.json", json.dumps(pack, ensure_ascii=False, indent=2))
        for pack_id, data in (EXAMPLES if examples is None else examples).items():
            self.put(f"{templates.EXAMPLES}/{pack_id}.json", json.dumps(data, ensure_ascii=False, indent=2))

    def pages(self) -> dict:
        return templates.build(self.root)

    def library(self):
        return templates.load_library(self.root / templates.LIBRARY)


def examples_with(change) -> dict:
    data = copy.deepcopy(EXAMPLES)
    change(data)
    return data


class LibraryTests(unittest.TestCase):
    def test_packs_come_in_their_curated_order_and_each_template_counts_once(self):
        library = Site(self).library()
        self.assertEqual([p.id for p in library.packs], ["general", "software-engineering"])
        self.assertEqual(len(library.templates), 3)
        self.assertEqual([t.id for t in library.listed("software-engineering")],
                         ["software-engineering.daily-standup", "general.weekly-review"])

    def test_an_included_template_has_one_page_under_the_pack_that_owns_it(self):
        library = Site(self).library()
        review = library.templates["general.weekly-review"]
        self.assertEqual(templates.page_path(review), "apps/dayfolio/templates/general/weekly-review/index.html")
        self.assertEqual([p.id for p in library.packs_listing(review.id)], ["general", "software-engineering"])
        self.assertEqual(sorted(Site(self).pages()), sorted(TEMPLATE_PAGES + [
            GALLERY, "apps/dayfolio/templates/general/index.html",
            "apps/dayfolio/templates/software-engineering/index.html"]))

    def test_a_file_the_app_would_refuse_is_named(self):
        for change, needle in (
                (lambda p: p["pack"]["templates"][0]["fields"].append({"key": "x", "label": "X", "type": "colour"}),
                 "colour"),
                (lambda p: p["pack"]["templates"][0]["fields"].append({"key": "s", "label": "S", "type": "singleSelect"}),
                 "options"),
                (lambda p: p["pack"].update(includes=["general.nowhere"]), "general.nowhere"),
                (lambda p: p["pack"].pop("name"), "name")):
            pack = copy.deepcopy(ENGINEERING)
            change(pack)
            with self.subTest(needle=needle), self.assertRaises(templates.LibraryError) as caught:
                Site(self, packs=(GENERAL, pack)).library()
            self.assertIn("software-engineering.json", str(caught.exception))
            self.assertIn(needle, str(caught.exception))


class TextTests(unittest.TestCase):
    def test_durations_read_as_the_app_writes_them(self):
        self.assertEqual([templates.duration_text(m) for m in (330, 120, 45, 0)], ["5h 30m", "2h", "45m", "0m"])

    def test_a_reminder_reads_as_days_and_a_time(self):
        def reminder(days, hour=9, minute=0):
            return templates.reminder_text({"weekdays": days, "hour": hour, "minute": minute})
        self.assertEqual(reminder([2, 3, 4, 5, 6]), "Weekdays at 09:00")
        self.assertEqual(reminder([6], 17, 30), "Fridays at 17:30")
        self.assertEqual(reminder([2, 5]), "Mondays and Thursdays at 09:00")
        self.assertEqual(reminder([1, 7]), "Weekends at 09:00")
        self.assertEqual(reminder([1, 2, 3, 4, 5, 6, 7]), "Every day at 09:00")
        self.assertEqual(templates.reminder_text(None), "None")

    def test_a_template_name_takes_a_or_an_as_it_sounds(self):
        self.assertEqual([templates.indefinite(n) for n in ("Incident postmortem", "A/B experiment log", "On-call handover",
                                                           "Usability test notes", "1:1 notes", "Daily standup")],
                         ["An", "An", "An", "A", "A", "A"])

    def test_straight_quotes_from_the_app_become_curly(self):
        self.assertEqual(templates.smart('A short "today I learned" log, after Gibbs\' cycle'),
                         "A short “today I learned” log, after Gibbs’ cycle")


class ExampleTests(unittest.TestCase):
    def problem(self, examples) -> str:
        with self.assertRaises(templates.LibraryError) as caught:
            Site(self, examples=examples).pages()
        return str(caught.exception)

    def test_every_template_needs_an_example(self):
        message = self.problem(examples_with(lambda d: d["general"].pop("general.1-1-notes")))
        self.assertIn("general.1-1-notes", message)

    def test_every_field_needs_a_sample_value(self):
        message = self.problem(examples_with(
            lambda d: d["general"]["general.weekly-review"]["values"].pop("challenges")))
        self.assertIn("general.weekly-review", message)
        self.assertIn("challenges", message)

    def test_a_value_must_fit_its_field(self):
        values = lambda d: d["software-engineering"]["software-engineering.daily-standup"]["values"]  # noqa: E731
        for change, needle in ((lambda d: values(d).update(status="done"), "status"),
                               (lambda d: values(d).update(channels=["fax"]), "channels"),
                               (lambda d: values(d).update({"focus-time": "a while"}), "focus-time"),
                               (lambda d: values(d).update(pages="three"), "pages"),
                               (lambda d: values(d).update(due="23 Oct"), "due"),
                               (lambda d: values(d).update(doc={"title": "Spec", "url": "https://acme.com/x"}), "doc"),
                               (lambda d: values(d).update(shipped=["Retry queue"]), "shipped"),
                               (lambda d: values(d).update(extra="x"), "extra"),
                               (lambda d: d["general"]["general.weekly-review"]["values"].update(energy=7), "energy"),
                               (lambda d: d["general"]["general.weekly-review"]["values"].update(tags=["Release"]),
                                "tags"),
                               (lambda d: d["general"]["general.1-1-notes"]["values"].update(
                                   {"meeting-time": "10:30-10:00"}), "meeting-time")):
            with self.subTest(needle=needle):
                self.assertIn(needle, self.problem(examples_with(change)))

    def test_sample_text_follows_the_sites_copy_rules(self):
        message = self.problem(examples_with(lambda d: d["general"]["general.weekly-review"]["values"].update(
            challenges='Two days lost to a "flaky" test!')))
        self.assertIn("challenges", message)


def field(key: str, kind: str, carry: bool = False, label: str = "") -> "templates.Field":
    return templates.Field(key, label or key.capitalize(), kind, carry_over=carry)


class CarryOverTests(unittest.TestCase):
    """Which entry a carried field comes from, as the app's EntryFactory picks it (D1638, D2071, D2075)."""

    def test_the_lead_is_the_first_property_row_a_person_or_a_project_carry_over_follows(self):
        person, notes = field("with", "person", label="With"), field("notes", "text")
        self.assertIs(templates.lead_field([notes, person, field("actions", "checklist", True)]), person)
        client = field("client", "project", True)
        self.assertIs(templates.lead_field([client, field("hours", "duration")]), client)
        site = field("site", "project")
        self.assertIs(templates.lead_field([site, field("actions", "checklist", True)]), site)
        self.assertIsNone(templates.lead_field([site, field("result", "singleSelect"), notes]))
        self.assertIsNone(templates.lead_field([site, field("photos", "attachment", True)]))
        self.assertIsNone(templates.lead_field([field("energy", "rating"), person, field("x", "checklist", True)]))

    def test_a_carried_fields_note_names_the_entry_it_comes_from(self):
        note = templates.carry_note
        project, working = field("project", "project", True), field("working-on", "richText", True)
        standup = [field("energy", "rating"), project, working]
        self.assertEqual(note(standup, project),
                         "Carries over: a new entry starts with the value from your last entry with this template.")
        with_, items = field("with", "person", label="With"), field("action-items", "checklist", True)
        self.assertEqual(note([with_, items], items),
                         "Carries over: once you choose who it’s with, it fills with the items you haven’t ticked "
                         "in your last entry with the same person.")
        attendees = field("attendees", "person", label="Attendees")
        self.assertIn("your last entry with the same people.", note([attendees, items], items))
        client, steps = field("client", "project", True, "Client"), field("next-steps", "checklist", True)
        self.assertEqual(note([client, steps], client),
                         "Carries over: a new entry starts with the value from your last entry with this template.")
        self.assertEqual(note([client, steps], steps),
                         "Carries over: a new entry starts with the items you haven’t ticked in your last entry for "
                         "the same client; choose another client and you get that client’s instead.")
        site, actions = field("site", "project", label="Site"), field("actions", "checklist", True)
        self.assertEqual(note([site, field("result", "singleSelect"), actions], actions),
                         "Carries over: once you choose the site, it fills with the items you haven’t ticked in your "
                         "last entry for the same site.")

    def test_the_template_page_carries_the_note_and_a_field_that_cannot_carry_has_none(self):
        one_on_one = Site(self).pages()["apps/dayfolio/templates/general/1-1-notes/index.html"]
        self.assertIn("your last entry with the same person.", one_on_one)
        self.assertNotIn("previous entry with this template", one_on_one)
        self.assertIsNone(templates.carry_note([field("photos", "attachment", True)], field("photos", "attachment", True)))


class SearchTitleTests(unittest.TestCase):
    def test_a_template_can_be_titled_by_the_words_people_search_for(self):
        pages = Site(self).pages()
        one_on_one = pages["apps/dayfolio/templates/general/1-1-notes/index.html"]
        self.assertIn("<title>1:1 meeting notes template — Dayfolio — NinjaApps</title>", one_on_one)
        self.assertIn('<h1 class="page-title">1:1 meeting notes template</h1>', one_on_one)
        self.assertIn("A 1:1 notes entry as Dayfolio draws it", one_on_one)
        self.assertIn("<title>Daily standup template — Dayfolio — NinjaApps</title>", pages[STANDUP])

    def test_a_page_title_keeps_the_builds_rules(self):
        for title, needle in (("1:1 meeting notes template for every kind of recurring one-on-one", "60"),
                              ('"1:1" meeting notes template', "straight quote"),
                              ("Daily standup template", "already")):
            with self.subTest(title=title):
                examples = examples_with(lambda d: d["general"]["general.1-1-notes"].update(page_title=title))
                with self.assertRaises(templates.LibraryError) as caught:
                    Site(self, examples=examples).pages()
                self.assertIn("general.1-1-notes", str(caught.exception))
                self.assertIn(needle, str(caught.exception))


class PageTests(unittest.TestCase):
    def setUp(self):
        self.site = Site(self)
        self.pages = self.site.pages()
        self.standup = self.pages[STANDUP]

    def test_a_template_page_names_every_field_with_its_type_options_and_prompt(self):
        fields = self.standup.split('id="fields"')[1]
        for words in ("Focus time", "Duration", "Status", "Single select", "On track", "At risk", "Blocked",
                      "Multi-select", "Number", "Date", "Link", "Checklist", "Attachment",
                      "What did you finish since the last standup?", "Anything in your way?"):
            self.assertIn(words, fields)
        self.assertIn("carries over", fields.lower())
        self.assertIn("Daily", self.standup)
        self.assertIn("Weekdays at 09:00", self.standup)

    def test_the_example_is_drawn_as_the_app_draws_an_entry(self):
        entry = re.search(r'<article class="entry".*?</article>', self.standup, re.S).group(0)
        for words in ("THURSDAY · WEEK 42", "15 October 2026", "Retry queue is in", "Daily standup", "09:12",
                      "5h 30m", "Payments API", "On track", "entry-tone-success", "entry-dot-purple", "23 Oct 2026",
                      "Retry design", "docs.example.com", "Retry queue for webhook delivery", "entry-well",
                      "Waiting on a staging snapshot.", "dashboard.png", "PNG picture · 180 KB"):
            self.assertIn(words, entry)
        self.assertNotIn("<a ", entry)  # a made-up link is drawn, never followed
        review = self.pages[TEMPLATE_PAGES[0]]
        for words in ("High", "Great", "#release", "Shipped the retry queue", "<strong>one</strong>"):
            self.assertIn(words, review)

    def test_a_template_page_links_its_pack_the_guide_related_templates_and_the_app_store(self):
        review = self.pages[TEMPLATE_PAGES[0]]
        self.assertIn('href="../"', review)                        # its pack
        self.assertIn('href="../../software-engineering/"', review)  # a pack that includes it
        self.assertIn('href="../1-1-notes/"', review)              # a related template
        self.assertIn('href="../../../guide/"', review)            # the guide, until its topic exists
        self.assertIn("https://apps.apple.com/app/id6817388897", review)
        self.site.put("apps/dayfolio/guide/templates-and-fields/index.html", "<html></html>")
        self.assertIn('href="../../../guide/templates-and-fields/"', self.site.pages()[TEMPLATE_PAGES[0]])

    def test_json_ld_breadcrumbs_and_item_lists(self):
        crumbs = [b for b in tb.jsonld(self.standup) if b["@type"] == "BreadcrumbList"][0]
        self.assertEqual([i["name"] for i in crumbs["itemListElement"]],
                         ["Dayfolio", "Templates", "Software Engineering", "Daily standup"])
        pack = self.pages["apps/dayfolio/templates/software-engineering/index.html"]
        items = [b for b in tb.jsonld(pack) if b["@type"] == "ItemList"][0]["itemListElement"]
        self.assertEqual([i["url"] for i in items], [
            "https://ninjaapps.net/apps/dayfolio/templates/software-engineering/daily-standup/",
            "https://ninjaapps.net/apps/dayfolio/templates/general/weekly-review/"])
        gallery = [b for b in tb.jsonld(self.pages[GALLERY]) if b["@type"] == "ItemList"][0]["itemListElement"]
        self.assertEqual([i["name"] for i in gallery], ["General", "Software Engineering"])

    def test_the_gallery_counts_and_lists_every_pack_and_template(self):
        gallery = self.pages[GALLERY]
        self.assertIn("3 templates in 2 packs", gallery)
        for href in ('href="general/"', 'href="software-engineering/"', 'href="general/weekly-review/"',
                     'href="general/1-1-notes/"', 'href="software-engineering/daily-standup/"'):
            self.assertIn(href, gallery)

    def test_a_pack_page_says_how_a_journal_made_from_it_starts(self):
        pack = self.pages["apps/dayfolio/templates/software-engineering/index.html"]
        self.assertIn("Engineering Log", pack)
        self.assertIn("Daily standup", pack)
        self.assertIn("From General", pack)

    def test_titles_and_descriptions_fit_search_results_and_differ(self):
        titles, descriptions = set(), set()
        for path, page in self.pages.items():
            title = tb.meta(page, "og:title")
            description = tb.meta(page, "description")
            self.assertLessEqual(len(title) - len(build.SUFFIX), build.TITLE_MAX, path)
            self.assertTrue(build.DESCRIPTION_MIN <= len(description) <= build.DESCRIPTION_MAX, (path, description))
            titles.add(title)
            descriptions.add(description)
        self.assertEqual(len(titles), len(self.pages))
        self.assertEqual(len(descriptions), len(self.pages))
        self.assertIn("<title>Daily standup template — Dayfolio — NinjaApps</title>", self.standup)

    def test_no_page_carries_a_label_above_its_title_or_a_decorative_kanji(self):
        for path, page in self.pages.items():
            with self.subTest(page=path):
                self.assertNotIn('class="kicker', page)
                self.assertNotIn("crumbs-mark", page)
                self.assertNotRegex(page, "[←→]")  # arrows are drawn by the stylesheet, not typed
                self.assertNotRegex(page.split("<main>")[1], r"[\u3040-\u30ff\u4e00-\u9fff]")

    def test_each_page_says_it_is_generated_and_carries_the_sub_navigation(self):
        for path, page in self.pages.items():
            self.assertIn(f"<!-- {templates.GENERATED}", page, path)
            self.assertIn(build.render_subnav(path), page, path)


class WriteAndCheckTests(unittest.TestCase):
    def setUp(self):
        self.site = Site(self)

    def test_after_a_write_the_check_is_clean_and_the_write_is_stable(self):
        self.assertTrue(templates.write(self.site.root))
        self.assertEqual(templates.check(self.site.root), [])
        self.assertEqual(templates.write(self.site.root), [])

    def test_the_build_keeps_the_pages_and_lists_them_in_the_sitemap(self):
        templates.write(self.site.root)
        build.write(self.site.root)
        self.assertEqual(templates.check(self.site.root), [])
        self.assertEqual(build.check(self.site.root), [])
        sitemap = self.site.read("sitemap.xml")
        self.assertIn("https://ninjaapps.net/apps/dayfolio/templates/general/1-1-notes/", sitemap)

    def test_the_check_names_a_page_that_differs(self):
        templates.write(self.site.root)
        self.site.put(STANDUP, self.site.read(STANDUP).replace("Retry queue is in", "Hand edit"))
        problems = templates.check(self.site.root)
        self.assertEqual(len(problems), 1, problems)
        self.assertIn(STANDUP, problems[0])

    def test_a_template_that_left_the_library_loses_its_page(self):
        templates.write(self.site.root)
        pack = copy.deepcopy(GENERAL)
        pack["pack"]["templates"].pop(1)
        self.site.put(f"{templates.LIBRARY}/general.json", json.dumps(pack))
        self.site.put(f"{templates.EXAMPLES}/general.json",
                      json.dumps({"general.weekly-review": EXAMPLES["general"]["general.weekly-review"]}))
        self.assertTrue(any(TEMPLATE_PAGES[1] in p for p in templates.check(self.site.root)))
        templates.write(self.site.root)
        self.assertFalse((self.site.root / TEMPLATE_PAGES[1]).exists())
        self.assertEqual(templates.check(self.site.root), [])

    def test_the_apps_library_is_copied_in_and_compared(self):
        app = self.site.root / "app/Packages/DayfolioKit/Sources/DayfolioDomain/Resources/Library"
        app.mkdir(parents=True)
        changed = copy.deepcopy(GENERAL)
        changed["pack"]["summary"] = "Weekly reviews and 1:1s that fit any kind of work, changed in the app."
        (app / "general.json").write_text(json.dumps(changed), encoding="utf-8")
        (app / "software-engineering.json").write_text(json.dumps(ENGINEERING), encoding="utf-8")
        templates.write(self.site.root)
        self.assertEqual(templates.check(self.site.root), [])
        problems = templates.check(self.site.root, self.site.root / "app")
        self.assertTrue(any("general.json" in p for p in problems), problems)
        templates.sync(self.site.root, self.site.root / "app")
        templates.write(self.site.root)
        self.assertEqual(templates.check(self.site.root, self.site.root / "app"), [])
        self.assertIn("changed in the app", self.site.read("apps/dayfolio/templates/general/index.html"))

    def test_the_gallery_markdown_and_the_generator_cannot_both_own_the_gallery(self):
        self.site.put("content/dayfolio/templates/index.md", tb.section("Templates"))
        with self.assertRaises(templates.LibraryError) as caught:
            templates.build(self.site.root)
        self.assertIn("content/dayfolio/templates", str(caught.exception))


if __name__ == "__main__":
    unittest.main()

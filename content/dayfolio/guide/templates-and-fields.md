---
title: Journals, forms and fields
description: A journal is one template, its form. Change its fields in Journal settings, then fill an entry fast with the Fill line, last time’s values and a timer.
slug: templates-and-fields
date: 2026-10-16
updated: 2026-11-05
order: 3
---
Every Dayfolio entry starts from the form of the journal it’s in, so you write in the shape of your work instead of facing a blank page. A form is an ordered set of fields: a rating for energy, a duration for focus time, a status with coloured options, a checklist of what shipped, a notes field. Because the values are structured, Dayfolio can chart them in Insights, add them up in reports and carry them from one entry to the next.

A journal has exactly one form, and no other journal shares it. You get a form by making a journal from one of the library’s templates, or from a blank one, in New journal. See [Journals, folders and goals](../journals-and-folders/).

## The template library

The library holds 75 ready-made templates in 16 packs, one for each kind of work: Software Engineering, Consulting & Freelance, Management & Leadership, Healthcare, Education and more. Templates that fit any job, such as Weekly review, 1:1 notes and Decision log, live in the General pack. You can browse them all in the [template gallery](../../templates/).

The library is part of **New journal**: choose a template and it becomes a journal of its own, with its own copy of the form. The journal remembers which template it was based on, and the library’s templates are never changed by your edits. There is no separate Templates screen.

## Change a form

Open the journal’s settings, go to **Form** and choose **Edit form…**. You can also choose ⋯ › *Edit form* on an entry. The Note form of the Notes journal is fixed, so Notes has no form editor.

The editor has two sections, as an entry does: **Properties**, the values at the top of the page, and **Page**, the longer fields underneath.

- **Add a field:** choose *Add field* (⇧⌘N on a Mac) and pick a type.
- **Reorder:** drag a field within its section.
- **Set it up:** select a field to change its label, its prompt (the faint text shown while it’s empty), its options and their colours, or a default value. Switches decide whether it shows in list previews, counts in Insights and charts, carries over from the previous entry, and, for a text field, is drawn as a warning, the way Blockers is.
- **Compare with original** shows what you’ve changed from the library’s version, and can add a removed field back.
- **Preview** shows the entry as it will look.

The form says what it is based on, beside *Compare with original*: “Your form · based on Daily standup · 2 changes”. The count is the fields you added, the library’s you removed, and those you kept and changed, against the library’s current version. A form made from a blank journal, and Notes, have no such line.

Choose **Save form** when you’re done. If you leave with changes, Dayfolio asks “Save changes to “Daily Standup”?” and lists what’s unsaved: “Not saved yet: added “Blockers”, renamed “Done”.” You can save, discard or cancel. If you delete a field that entries use, it says how many: “Used in 3 entries. They keep “Energy”; new entries won’t have it.”

### Field types

| Group | Types |
|---|---|
| Basics | Text, Rich text, Checklist, Heading, Divider |
| Values | Number, Duration, Rating, Mood, Date, Time range |
| Choice | Single select, Multi-select, Tags |
| Links | Person, Project, Link, Attachment |

Rich text keeps bold, italics, headings, lists, checklists, quotes, code blocks and links. With Markdown shortcuts on, typing `**`, `#`, `- [ ]`, `>` or three backticks formats as you write. On iPhone and iPad, the **Aa** menu above the keyboard has Quote, Code block, Indent and Outdent.

### Checklists

A Checklist field shows how far you are in its header: “3 of 5 done”. It counts the field’s own items, shows nothing while the list is empty, and has no ring and no animation. A ticked item is struck through, in a checklist and in a checklist line of rich text, wherever the entry is drawn: the editor, the Timeline, search results, reports, print, PDF and Word. Markdown keeps `- [x]`.

Switch on a checklist’s **Carry over unticked items** and it becomes a *continuous checklist*: what you haven’t ticked moves to the next entry in the journal, and what you ticked stays behind in its own entry. See [Carry-over between entries](../carry-over/).

The **Completed list** is a read-only field that shows what you got done. It lists the items you ticked in a continuous checklist, filled once, when the entry is made. Where a list comes from is set in the field’s settings:

- **Follows** chooses the continuous checklist it reads. By default that is the form’s first one, but it can be another journal’s, listed by journal.
- **Lists** chooses the range: the **Previous entry** (the default, the items ticked in the latest earlier entry that holds the checklist) or **Since this journal’s last entry**, every item ticked in entries dated from the journal’s previous entry up to the new one.

With nothing ticked it says “Nothing completed”. A Completed list isn’t offered by *Add field* on a single entry, and it never carries over. Items ticked in a journal you lock are listed only in a Completed list of a journal you lock, its own included; in any other journal’s they stay out.

![A 1:1 entry on iPhone: Action items at 1 of 2 done with the ticked item struck through, over Done since the last 1:1, which lists the two items ticked last time.](templates-completed-list-iphone.webp)

### What changes when you edit

A change to a form applies to the journal’s new entries from then on. Each entry keeps the fields it was made with, so old entries never change under you. Renaming a field or an option keeps it the same field, so charts and reports stay continuous. Changing a field’s type starts a new field; past entries keep the old one. No other journal is affected, because no other journal uses the form.

When you rename the journal or change its icon or colour, its form takes them too, so new entries carry the journal’s name.

## Fill an entry quickly

### The Fill line

The Fill line fills several fields from one typed line, such as `energy 4, focus 2h, status on track, #release`.

- **On a Mac or an iPad with a keyboard,** press Tab in the entry’s title.
- **On any device,** choose ⋯ › **Fill fields**.

Write each value after the first letters of its field’s name. Durations read as “2h”, “90m”, “1.5h” or “2h30”; ratings as a number from 0 to 5; options by their first letters; people and projects by name; tags anywhere with `#`. Each value previews on its row as you type, and anything Dayfolio can’t read is underlined with the reason. Press Return to write them all at once, as one step you can undo, or Esc to close the line without writing anything. A label the entry doesn’t have, with a clear value, offers to add that field to this entry only.

### Last time’s values

In an entry made today, an empty select, person, project, tags or link field shows the value it had last time, faintly, under “Last time”. Nothing is filled in until you tap it.

- Tap one value to keep it, or keep them all: on iPhone and iPad, the line under the entry’s summary reads “Like Thursday: On track · #payments · Keep all”; on any device, ⋯ › **Keep values from last time** does the same.
- Using the field’s own control replaces its suggestion. Esc hides them all for that entry.
- When you’ve kept the same field’s value three entries in a row, Dayfolio offers to fill it from last time automatically. *Turn on…* opens the template with carry-over switched on for that field, ready to save; *Not now* stops asking about it. See [Carry-over between entries](../carry-over/).

![A new Daily Standup on iPhone, its project carried over and the line under the summary reading “Like Thursday: On track · #release #webhooks · Keep all”.](templates-last-time-iphone.webp)

### Durations and the timer

- On iPhone and iPad, touch and hold a duration, number, rating or mood, then slide to set it. While you type a duration, “−15m” and “+15m” sit beside it.
- On a Mac, ↑ and ↓ step a focused duration by 15 minutes, or a number by 1; add ⇧ for an hour or 10.
- On an entry dated today, every Duration and Time range field has a stopwatch. Start it, work, and Stop adds the minutes to the field (a Time range gets its end time). Touch and hold the stopwatch, or Control-click it on a Mac, to start from 5, 15 or 30 minutes ago. A running timer shows on iPhone’s Lock Screen and in its Dynamic Island, at the bottom of the app on iPhone and iPad, and in the menu bar on a Mac.

### One-off fields

On a Mac, *Add field* on an entry adds a field to that entry alone, without changing the template. On any device, the Fill line offers the same for a label the entry doesn’t have. A one-off field is searchable like any other.


## Related

- [Journals, folders and goals](../journals-and-folders/)
- [Carry-over between entries](../carry-over/)
- [Getting started](../getting-started/)
- [Reports](../reports/)
- The [template gallery](../../templates/): try [Daily standup](../../templates/software-engineering/daily-standup/), [Decision log](../../templates/general/decision-log/) or [Shift debrief](../../templates/healthcare/shift-debrief/)

---
title: Diagrove and Dayfolio
description: What works between Diagrove and Dayfolio today, Send to Dayfolio, Shortcuts and links, and what waits for a Dayfolio update.
slug: dayfolio
date: 2026-10-29
order: 12
---
Diagrove and [Dayfolio](../../../dayfolio/) are made by the same small team, and they’re built to work together. Some of that works today; the rest needs a Dayfolio update that isn’t out yet. This page says plainly which is which, so you know what to expect.

## What works today

| From | To | How |
|---|---|---|
| A diagram | A Dayfolio entry | **Send to Dayfolio** |
| A diagram | A Dayfolio entry | The **Export Canvas as Image** shortcut action |
| A Dayfolio entry’s text | A new diagram | The **Create Diagram from Text** shortcut action |
| A click in a diagram | Dayfolio | A **Run shortcut** action that runs one of Dayfolio’s shortcuts |
| Anywhere a link works | A new diagram | A `diagrove://new?text=…` link |

### Send to Dayfolio

On the Mac, click **Send to Dayfolio** in the toolbar or choose **File › Send to Dayfolio…**. On iPad it’s in the toolbar’s Export menu.

Diagrove opens the share menu (the share sheet on iPad) with two files: a picture of the current canvas, as a PNG, and the whole document, zipped. Choose Dayfolio, and Dayfolio’s share extension takes them into an entry: the picture to look at, and the document kept with it. Any other app in the share menu can take the files too.

[shot: send-to-dayfolio-mac] The Mac, light appearance, the Roadmap template: the share menu open from the toolbar’s Send to Dayfolio button, with Dayfolio among the apps.

### Shortcuts both ways

Diagrove’s two shortcut actions work with Dayfolio’s own:

- **Create Diagram from Text** turns words into a diagram: make a shortcut that takes an entry’s text and passes it on, and an arrow chain such as `Idea -> Plan -> Ship` or an indented list becomes a new diagram. With Apple Intelligence, a description works too.
- **Export Canvas as Image** turns a Diagrove document’s first canvas into a PNG, PDF or SVG file, which the next step of a shortcut can give to Dayfolio.
- In the other direction, a graphic’s **Run shortcut** action can run one of Dayfolio’s shortcuts, such as New entry or Start timer. Click it in Play mode, and the diagram becomes a panel of buttons for your day. See [Play mode and actions](../play-mode-and-actions/).

### A link

`diagrove://new?text=…` opens a new diagram drawn from the text, from any app or note that can open a link. See [Import and export](../import-and-export/).

## What isn’t there yet

Three things wait for a Dayfolio update that isn’t out yet. The first two need Dayfolio to share a summary of your work with Diagrove; the third needs Dayfolio to show diagrams inside entries. There’s no date for any of them, so plan on what works today.

### Bindings to the Dayfolio feed

A [binding](../bindings/) can read **From Dayfolio**: your projects and their hours this week, the running timer, the titles of recent entries. Until Dayfolio shares that summary, these bindings say “Dayfolio isn’t sharing with Diagrove yet” and leave the graphic as you drew it, and in Play mode the live data capsule says “No data from Dayfolio yet”. Your hand-set values stay on show.

### New from Dayfolio (Mac)

**File › New from Dayfolio…** draws a diagram from that same summary: a **Project map** of your projects and the people on them, a **Week flow** of your latest week’s entries, or a **Timeline**. Until Dayfolio shares its summary, the sheet says Dayfolio isn’t sharing with Diagrove yet, and **Try with sample data** shows each diagram with made-up projects and entries, so you can see what it would draw. It’s on the Mac only.

The sheet also says what the summary holds: your projects, people, tags, places, the running timer and the titles of recent entries. Locked journals and what you write in entries are never part of it.

### Diagrams inside entries

A diagram shown live inside a Dayfolio entry, which you could tap through, isn’t in Dayfolio yet either. A picture of the canvas, through Send to Dayfolio, is what an entry shows today.

You can already see how a diagram would look and behave there: **View › Preview as embed**, with **Width** set to **Dayfolio entry**. A graphic with an **Ask the host app** action is how a diagram would ask Dayfolio to do something, such as start a timer for a project. Today, in Diagrove’s Play mode, it shows a note with what Dayfolio would get.

[shot: preview-embed-mac] The Mac, light appearance, the App screen template: the Preview as embed sheet with Width set to Dayfolio entry and Show set to Just the drawing, and one row under The app receives.

> **Tip:** What Dayfolio gets is a copy. Your document stays where you saved it, and later changes in Diagrove reach an entry only when you send the diagram again.

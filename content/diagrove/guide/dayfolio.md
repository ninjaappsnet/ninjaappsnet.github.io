---
title: Diagrove and Dayfolio
description: What works between Diagrove and Dayfolio today: Send to Dayfolio, Shortcuts and links.
slug: dayfolio
date: 2026-10-29
order: 12
---
Diagrove and [Dayfolio](../../../dayfolio/) are made by the same small team, and they’re built to work together. This page says what works between them today.

## What works today

| From | To | How |
|---|---|---|
| A diagram | A Dayfolio entry | **Send to Dayfolio** (from the iPad) |
| A diagram | A Dayfolio entry | The **Export Canvas as Image** shortcut action |
| A Dayfolio entry’s text | A new diagram | The **Create Diagram from Text** shortcut action |
| A click in a diagram | Dayfolio | A **Run shortcut** action that runs one of Dayfolio’s shortcuts |
| Anywhere a link works | A new diagram | A `diagrove://new?text=…` link |

### Send to Dayfolio

On the Mac, choose **File › Send to Dayfolio…**, which shows when Dayfolio is installed; **View › Customize Toolbar…** can add it to the toolbar too. On iPad it’s in the toolbar’s Export menu.

Diagrove opens the share menu (the share sheet on iPad) with two files: a picture of the current canvas, as a PNG, and the whole document, zipped. On iPad, choose Dayfolio, and Dayfolio’s share extension takes them into an entry: the picture to look at, and the document kept with it. Dayfolio for Mac doesn’t take shared files yet, so on the Mac it isn’t in the share menu: send the diagram from your iPad, or save the picture and add it to an entry yourself. Any other app in the share menu can take the files too.

![The Roadmap template on iPad with the share sheet open from Send to Dayfolio, Dayfolio first among the apps, then Preview and More, and Copy, Assign to Contact, Print and Save to Files.](send-to-dayfolio-ipad.webp "Send to Dayfolio opens the share sheet, with Dayfolio in it.")

> **Tip:** What Dayfolio gets is a copy. Your document stays where you saved it, and later changes in Diagrove reach an entry only when you send the diagram again.

### Shortcuts both ways

Diagrove’s two shortcut actions work with Dayfolio’s own:

- **Create Diagram from Text** turns words into a diagram: make a shortcut that takes an entry’s text and passes it on, and an arrow chain such as `Idea -> Plan -> Ship` or an indented list becomes a new diagram. With Apple Intelligence, a description works too.
- **Export Canvas as Image** turns a Diagrove document’s first canvas into a PNG, PDF or SVG file, which the next step of a shortcut can give to Dayfolio.
- In the other direction, a graphic’s **Run shortcut** action can run one of Dayfolio’s shortcuts, such as New entry or Quick note. Click it in Play mode, and the diagram becomes a panel of buttons for your day. See [Play mode and actions](../play-mode-and-actions/).

### A link

`diagrove://new?text=…` opens a new diagram drawn from the text, from any app or note that can open a link. See [Import and export](../import-and-export/).

## What comes later

More connections between Diagrove and Dayfolio come in later versions, once Dayfolio has its side of them. There’s no date for them, so plan on what works today.

### Diagrams inside entries

A diagram shown live inside a Dayfolio entry, which you could tap through, is one of them. A picture of the canvas, through Send to Dayfolio, is what an entry shows today.

You can already see how a diagram would look and behave there: **View › Preview as embed**, with **Width** set to **In Dayfolio**. A graphic with a **Send to the app it’s embedded in** action is how a diagram would ask Dayfolio to do something, such as start a timer for a project. Today, in Diagrove’s Play mode, it shows a note with what Dayfolio would get.

![The Preview as embed sheet over the App screen template: Show set to Just the drawing, Width set to Dayfolio entry, the top of the two phone screens in the preview, whose stage scrolls to show the rest, and under The app receives one row: a click on the background, where the app could open the diagram in Diagrove.](preview-embed-mac.webp "Preview as embed at the width of a Dayfolio entry.")

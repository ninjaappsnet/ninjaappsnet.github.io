---
title: Import and export
description: Export PNG, PDF, SVG or a web player, automate with Shortcuts and links, and bring in SVG drawings, OmniGraffle files, sketches, Diagrove text and Mermaid.
slug: import-and-export
date: 2026-10-29
order: 10
---
Diagrove documents are `.diagrove` files you keep wherever you like. This page covers the ways a diagram leaves Diagrove, as a picture, a PDF, a drawing or a web page, and the ways other work comes in.

## Export a picture, a PDF or an SVG

Choose **File › Export…** (Shift-Command-E), or click **Export** in the toolbar. The sheet shows a preview and says what it will save.

- **Format**: **PNG image**, **PDF document**, **SVG drawing**, and on the Mac **Web player**.
- **Area**: **Whole canvas**, paper and all, or **Just the drawing** with a small margin.
- For PNG, **Scale** is 1×, 2× or 3×, and **Transparent background** leaves out the paper.
- For PDF in a document with two or more canvases, **Every canvas, one page each** puts the whole document in one file.

On the Mac you choose where to save. On iPad, choose **Save to Files…** or **Share**.

Copy works too: a selection you copy carries a PDF and a PNG of itself, so you can paste it straight into a document, a slide or a message.

![The export sheet over the Flowchart template: a preview of the bike repair flowchart, Format set to PNG image, Area set to Just the drawing, Scale 2×, Transparent background off, and the subtitle giving the picture’s size in pixels.](export-sheet-mac.webp "File › Export… set to a PNG image.")

## The Web player (Mac)

Choose **Web player** as the format and Diagrove saves a folder that plays the document in any browser: open its `index.html`. Every canvas is drawn as it is in the app, actions work, **Back** and a canvas menu move between canvases, and variables and [bindings](../bindings/) that read JSON work as they do in Play mode. It needs no server; it works opened from your disk.

- Under **More options**, **Include a desktop app project** adds a Tauri project beside the player, to build into a desktop app. Building it needs Tauri and Rust.
- To put the player on a web page of your own, show `index.html` in an `iframe`. Adding `?chrome=0` to its address leaves out the player’s own controls.
- A graphic with an **Ask the host app** action hands it to the page around the player. See [Play mode and actions](../play-mode-and-actions/).

The Web player is on the Mac only in Diagrove 1.0. The iPad exports PNG, PDF and SVG.

## Shortcuts and diagrove links

Diagrove gives the Shortcuts app two actions, on the Mac and on iPad:

- **Create Diagram from Text** takes text and opens a new diagram drawn from it: an arrow chain such as `Idea -> Plan -> Ship`, an indented list, or, with Apple Intelligence, a description in your own words.
- **Export Canvas as Image** takes a Diagrove document and gives back its first canvas as a PNG, PDF or SVG file, for the next step of your shortcut.

A `diagrove://` link does the same from anywhere a link works:

```text
diagrove://new?text=Idea%20-%3E%20Plan%20-%3E%20Ship
```

The text after `text=` is written as a web address writes it, with spaces and symbols encoded. `diagrove://new` alone opens an empty document on the Mac, and the start screen on iPad. On iPad, the link draws the diagram and the start screen says it’s ready: tap **New diagram** to open it.

## Bring in SVG drawings

An SVG drawing comes in as graphics you can edit, not as a flat picture:

- On the Mac, choose **Insert › Drawing…** (Option-Shift-Command-I). **Insert › Picture…** takes an SVG too and brings it in the same way.
- On iPad, choose **Insert › Drawing from Files…**.
- Drop SVG files on the canvas.
- Paste an SVG you copied, such as an SVG file copied in the Finder, or SVG markup copied as text, like a design app’s “Copy as SVG”.

A drawing arrives as one group, centred where you dropped it or in the middle of what you see, and selected. Undo takes it all back in one step. If something couldn’t come across, such as a filter or a linked picture, a notice under the tool palette says what was skipped.

> **Tip:** Dragging an SVG out of a web page in Safari brings nothing in. Save it from Safari first, or copy its markup.

## Open OmniGraffle documents (Mac)

Choose **File › Import…** and pick a `.graffle` file, or open one from the Finder. Diagrove opens a copy as a new document and leaves your original file as it is; saving asks for a new `.diagrove` file.

Canvases, layers, shapes, lines and their connections, groups, tables, pictures and link actions come across. A report card over the canvas lists what didn’t map exactly.

OmniGraffle stencils (`.gstencil`) come in as a library of your own, on iPad too: open **Your libraries** on the sidebar’s Stencils tab and choose **Import…** at the top of its page. See [Stencils and tints](../stencils-and-tints/).

## Turn a sketch or photo into a diagram (Mac)

A photo of a whiteboard, a paper sketch or a screenshot of a drawn diagram can become shapes and connected lines.

1. Choose **File › New diagram from sketch or photo…** for a new document, or **Insert › Diagram from sketch or photo…** to add to this one. A picture already on the canvas has **Turn into diagram…** in its context menu and in the inspector’s Picture section.
2. Choose the picture, or drop it on the sheet. To take one with your iPhone, choose **File › Import from iPhone or iPad** while the sheet is open.
3. The sheet, **Turn your sketch into a diagram**, shows your picture beside the diagram Diagrove read from it. Under **Layout**, choose **Keep my layout** to keep things where you drew them, or **Tidy** to have them arranged for you.
4. Click **Insert**.

Diagrove reads the picture on your Mac; nothing is sent anywhere. It looks for closed outlines and lines between them, so a photo taken straight on, with dark lines on a light background, reads best. Shapes it was unsure of are dashed on your picture.

On iPad you draw the sketch over the canvas instead, in Sketch mode. See [Diagrove on iPad](../ipad/).

![The Turn your sketch into a diagram sheet over a new document: a picture of a drawn flowchart, four shapes and arrows, on the left with the shapes it found outlined, the diagram it made on the right, Layout set to Keep my layout, and Insert.](sketch-sheet-mac.webp "Turn your sketch into a diagram, with Keep my layout.")

## Diagrove text

Diagrove text is a plain-text way to write a diagram: `cart -> pay` is two shapes and a line between them.

- **Edit › Copy as Diagrove text** (Option-Shift-Command-C) copies the selection, or the whole canvas when nothing is selected, as text you can keep, send or edit.
- Paste text that reads as a diagram and it pastes as words first. A notice then says “This text reads as a diagram of 5 graphics.” Choose **Insert as diagram** to swap the words for the diagram, as one undo step.
- On the Mac, `.gtext` files open with **File › Open…** or **File › Import…** as a new document.

The [command-line tool](../command-line-tool/) writes and reads Diagrove text too, and its guide describes the language.

## Mermaid flowcharts

The command-line tool brings in a Mermaid flowchart, with its nodes, edges, subgraphs and colours, as a Diagrove document:

```sh
diagrove import mermaid chart.mmd -o Chart.diagrove
```

The command-line tool is for the Mac. See [The command-line tool](../command-line-tool/).

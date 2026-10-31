---
title: Open an OmniGraffle file
description: Bring an OmniGraffle document into Diagrove on the Mac as a new Document, see what came across differently, and save it as a .diagrove file.
slug: open-an-omnigraffle-file
date: 2026-10-29
order: 6
---
Diagrove on the Mac reads OmniGraffle documents (`.graffle`, flat files and packages) and turns each into a new Diagrove Document. Your original file is only read, never changed.

## Import the document

1. Choose **File › Import…**. You can also open a `.graffle` file from the Finder with Diagrove.
2. Choose the OmniGraffle document. Diagrove opens a copy as a new, untitled Document.
3. A card below the tool palette shows the file’s name and what came across, such as “Imported a copy · 3 canvases, 142 graphics”. A green check means everything came across as it was, and the card goes away on its own. Otherwise, open the list of differences to see what was simplified or left out.
4. Choose **File › Save** and give it a name. It’s saved as a `.diagrove` Document; the `.graffle` stays as it was.

[shot: import-report] Mac, light. A newly imported OmniGraffle document with the import card below the tool palette, its list of differences open. Point to the differences.

## What comes across

- Canvases, in order, with their names, sizes and layers. Master canvases from older OmniGraffle documents become shared layers when every canvas uses the same one, and ordinary layers otherwise.
- Shapes, including custom outlines, with their fills and gradients, strokes, shadows, words and text styles.
- Lines with their arrowheads and labels, connected to the shapes and magnets they were connected to.
- Groups, tables and pictures.
- Links, as Open link Actions, and jumps to another canvas, as Go to canvas Actions.

Some things come across differently, and the card names each one: shapes Diagrove has no outline for, arrowheads it doesn’t draw, curved and elbow lines whose bends Diagrove routes itself, mixed text styles in one shape, and Actions that can’t run, such as scripts. Notes aren’t imported. Shared layers from newer OmniGraffle versions import as ordinary layers.

## OmniGraffle stencils

To bring in an OmniGraffle stencil file (`.gstencil`), open **Your libraries** on the sidebar’s **Stencils** tab and choose **Import…** at the top of its page. Its stencils appear in a library of your own. See [Make a stencil library](../make-a-stencil-library/).

Opening OmniGraffle documents is on the Mac only in Diagrove 1.0; **Import…** in **Your libraries** takes `.gstencil` files on iPad too. Documents you save open on iPad as usual.

More in [Import and export](../../guide/import-and-export/).

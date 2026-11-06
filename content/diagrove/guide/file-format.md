---
title: The Diagrove file format
description: What is inside a .diagrove document and a .gtext file: the package, its versioned JSON, pictures and stencils, and the plain-text form of a diagram.
slug: file-format
date: 2026-11-06
order: 15
---
Your diagrams are files, and both of their formats are open. A Diagrove document is a `.diagrove` package of JSON, a preview and pictures, readable without Diagrove. Diagrove text, a `.gtext` file, writes the same diagram as a few lines of plain text that a person, a script or an AI assistant can write. This page describes both, for anyone who wants to read, write, keep or check them outside the app.

## The .diagrove document

A `.diagrove` document is a folder that the Finder and Files show as one file: a package. Its type is `net.ninjaapps.apps.diagrove.document`, and it conforms to `com.apple.package`. Inside it:

| Item | What it holds |
|---|---|
| `document.json` | The whole diagram: every canvas, layer and graphic, the document’s variables, and its copy of each stencil it uses. |
| `preview.png` | A picture of the first canvas, for Quick Look, the Finder and Dayfolio. |
| `assets/` | The pictures the diagram uses, one file each. |

Diagrove writes `document.json` as UTF-8 JSON, indented, with its keys in alphabetical order, so two versions of a document compare line by line in a diff. To look inside a package on the Mac, Control-click it in the Finder and choose Show Package Contents.

## document.json

The top level of `document.json` has these keys:

| Key | What it is |
|---|---|
| `schemaVersion` | The lowest version of the format that can read this document: 1, 2 or 3. |
| `canvases` | The canvases, in order. Each has an ID, a name, a size, a background, a grid and its layers, and an isometric one says so. |
| `stencils` | The document’s own copy of each stencil its instances use, by stencil ID. |
| `variables` | The document’s variables and their starting values, when it has any. |

Each layer has an ID, a name, whether it is visible, locked, printable or shared, and its graphics, back to front. A graphic is a shape, a line, a group or a table, with its ID. A shape has its frame, its kind and its style; a line its two ends, each attached to a shape’s magnet or free at a point; a group its children.

A **stencil instance** is a group with an `instance` key: the stencil’s ID and version, its frame, its tint and the parts you changed. Its children are written out in full as well. A reader that doesn’t know instances draws the group, and the diagram looks the same. Because the document keeps its own copy of every stencil, it opens the same on any Mac or iPad, without your libraries.

## Versions

The format has three versions, and a document says the lowest one that can read it, not the newest one that wrote it:

- **Version 1** holds shapes, lines, groups, tables, shared layers, bindings and variables.
- **Version 2** adds what a version 1 reader couldn’t decode: new kinds of action (set or toggle a variable, go back, and one for an app that hosts the diagram), picture fills, and custom shapes.
- **Version 3** adds radial gradients, custom dashes, inner shadows, blend modes, masks, the notation line ends (UML, entity–relationship, BPMN), and isometric canvases.

A document that uses nothing from version 2 or 3 says `1`, so an older reader keeps opening it. Diagrove 1.0 reads every version up to 3. A document that says a newer version opens with the message “This document was made with a newer version of Diagrove. Update Diagrove to open it.”

Within a version, readers are lenient: a key they don’t know is ignored, and an action or a binding they can’t decode is left out rather than failing the whole document.

## Pictures in assets/

A picture is stored once, in `assets/`, however many graphics use it. Its file name comes from its content: the first eight bytes of its SHA-256 hash in hexadecimal, then its extension, such as `3f9a1c0e7b2d4a65.png`. Graphics refer to it by that name. Only the pictures some graphic still uses are written when the document is saved.

## Diagrove text: the .gtext file

Diagrove text writes a whole document as plain text, close to D2, extended for what Diagrove has: canvases, layers, stencils, tables, actions, variables and bindings. Files end in `.gtext` and are UTF-8. This one is a complete document:

```
# A checkout flow. Lines starting with # are comments.
start: "Cart" { shape: rounded }
pay: "Paid?" { shape: diamond; fill: light-orange }
done: "Receipt"
retry: "Try again"
start -> pay
pay -> done: "Yes"
pay -> retry: "No" { dash: dashed }
retry -> pay
```

Nothing in it says where anything goes: auto-layout places graphics written without `at`, top to bottom, or left to right with `direction: right` on the canvas. Graphics with `at` stay where they are written.

The statements:

- **Shapes.** A key, its words and a block of attributes: `api: "Orders API" { at: 40, 40; size: 160, 60 }`. The key is the graphic’s ID, and it stays its ID through every command.
- **Lines.** `a -> b` (an arrow at b), `a <- b`, `a <-> b` or `a -- b` (no arrows), with a label after a colon. `a.right -> b.left` attaches to named magnets, and `a -> (400, 80)` leaves an end free.
- **Groups, tables and charts,** as blocks of their own.
- **Canvases and layers:** `canvas "Home" { … }` and `layer "Header" { … }`. A shared layer is written once, then named on the other canvases with `shared: true`.
- **Isometric canvases:** `projection: isometric`, then iso shapes with `iso-height`, `elevation` and `plane`.
- **Stencils:** `rack { stencil: iso.servers.rack; tint: teal }`, with `override:` lines for the parts you change.
- **Styles:** `style warn { fill: light-orange }`, and the styles `shapes`, `lines`, `groups` and `cells` for every graphic of a kind.
- **Actions, variables and bindings:** `on-click: go "Settings"`, `vars { count: 3 }` and `bind text: var count | format "{value} open"`.

Colours are names from Diagrove’s palette, such as `teal` or `light-orange`, or hex values such as `#ff8800`.

## Text and documents, both ways

A document written as text and read back keeps everything Diagrove text can say. What it can’t say is listed by name, never dropped silently: a picture, for one, stays a reference to its asset. On the Mac, **File › Open…** and **File › Import…** open a `.gtext` file as a new document; the app never writes one. **Edit › Copy as Diagrove text** (Option-Shift-Command-C) copies the selection, or the canvas when nothing is selected, as text.

The [command-line tool](../command-line-tool/) does the rest:

```
diagrove validate plan.gtext                  # every mistake, with its line, column and a hint
diagrove new --text plan.gtext -o Plan.diagrove
diagrove text Plan.diagrove -o plan.gtext     # a document as Diagrove text
diagrove schema text                          # the grammar, every attribute, the colours and magnets
```

A mistake is reported with its place and the fix, such as `broken.gtext:3:8: expected a Graphic's key or a point after ‘->’ (write the other end, such as a -> b)`.

## Stencil libraries

Your own stencil libraries are `.diagrovestencils` files. Export one from the Stencils tab to share it, and bring one in with **Import…** in Your libraries. See [Stencils and tints](../stencils-and-tints/).

## Related

- [The command-line tool](../command-line-tool/): make, check, render and change documents from Terminal.
- [Import and export](../import-and-export/): PNG, PDF, SVG, the web player, and OmniGraffle files.

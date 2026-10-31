---
title: Export for the web
description: Save a Document as a web player on the Mac: a folder that plays every canvas, Action and JSON binding in any browser, ready to put on a website.
slug: export-for-the-web
date: 2026-10-29
order: 9
---
A web player is a folder that plays your Document in a browser, just as Play mode does: clicks go to other canvases and back, links open, and bindings to variables and JSON files show their values. Nobody needs Diagrove to open it. The web player is on the Mac in Diagrove 1.0.

## Export it

1. Open the Document and choose **File › Export…** (Shift-Command-E), or click **Export** in the toolbar.
2. Set **Format** to **Web player**. The subtitle says what the folder plays, such as “Saves a folder that plays both canvases in any browser.”
3. Click **Export…**, give the folder a name and choose where to put it.
4. Open the folder’s `index.html` in a browser to try it.

[shot: web-player-format] Mac, light. The export sheet with Format set to Web player for the App screen template, the subtitle saying it plays both canvases. Point to the Format menu.

## What’s in the folder

- `index.html`, the page. It carries the Document inside it, so it works opened straight from your disk.
- `player.js` and `player.css`, which draw each canvas and run its Actions.
- `diagram.json`, the Document’s data, `pictures.json`, where each picture is and its size, and `assets`, its pictures and JSON files.

To put it online, upload the whole folder to any web host and link to its `index.html`.

## In the browser

The player starts on the first canvas and fits it to the window. After a jump it shows **Back**, and with more than one canvas it has a menu to choose one. A few additions to the address change it:

- `index.html#Website` starts on the canvas named Website.
- `?chrome=0` hides the player’s controls, for showing the diagram inside another page.
- `?zoom=1` keeps it at its own size instead of fitting the window.

[shot: player-in-browser] Mac, light. The exported App screen web player in Safari on the Website canvas after a click, with the player’s Back button and canvas menu. Point to the Back button.

## A desktop app too

Under **More options** in the export sheet, **Include a desktop app project** adds a Tauri project next to the player, so you can build the diagram into an app of its own. Building it needs Tauri and Rust. With it, the player moves into the project’s `web` folder: open `web/index.html` to try it.

To share a single picture instead, export a PNG, PDF or SVG from the same sheet. More in [Import and export](../../guide/import-and-export/) and [Play mode and Actions](../../guide/play-mode-and-actions/).

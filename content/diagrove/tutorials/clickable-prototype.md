---
title: A clickable prototype from the App screen template
description: Start from the App screen template, see how its Actions work, give another row a screen of its own with a back button, play it, then export a web player.
slug: clickable-prototype
date: 2026-10-29
order: 2
---
The App screen template is already a small working prototype: a projects list on one phone and the Website project on another, where a click on the Website row opens that project’s screen. In this tutorial you see how it works, make the Logo row open a screen of its own, add a back button and click through it in Play mode. On the Mac you then export it as a folder anyone can open in a browser.

## 1. Open the App screen template

On the Mac, choose **File › New from template…** (Shift-Command-N). In the gallery, choose **Product**, then **App screen**, pick White or Ink paper and click **Create**. You can also type “prototype” in **Search templates**. On iPad, tap **Choose a template** on the start screen.

The Document has two canvases, listed in the sidebar’s **Canvases** list:

- **Projects**: both phones side by side, the list on the left and the Website screen it opens on the right, with an arrow marked “Tap” between them.
- **Website**: the Website screen on its own, which a click on the row opens.

The phone frames lie on locked layers under the screens, so a click selects what’s on a screen rather than the phone around it.

![The App screen template on White paper: the Projects canvas with the projects list on the left phone and the Website screen on the right, joined by an arrow marked Tap, and the Canvases list showing Projects and Website.](app-screen-template.webp "The App screen template’s Projects canvas.")

## 2. See how its Actions work

Click the Website row on the left phone, then open **Action** in the inspector. **On click** is set to **Go to canvas**, and **Canvas** to **Website**. The caption underneath says it in words: “In Play mode, a click on this instance goes to Website.” The globe symbol on the row has the same Action, so a click anywhere on the row works.

Now open the Website canvas from the Canvases list and select the large “Website” title at the top of its screen. Its Action is **Go back**, which “Goes back to the canvas you came from.”

An Action does nothing while you edit. It runs in Play mode, or in the web player you export.

![The Website row selected on the Projects canvas, with the inspector’s Action section open: On click set to Go to canvas, Canvas set to Website, and the caption In Play mode, a click on this instance goes to Website.](action-section.webp "The Website row goes to the Website canvas.")

## 3. Give the Logo row a screen of its own

1. With the Website canvas open, choose **Canvas › Duplicate canvas**. A copy called “Website copy” appears in the Canvases list.
2. Right-click the copy in the list (touch and hold on iPad), choose **Rename** and call it “Logo”.
3. On the Logo canvas, double-click the “Website” title and type “Logo”. Change “Due 23 Oct” to “Due 28 Oct”, the date the list shows for Logo, and rename the tasks as you like.
4. Open the Projects canvas and click the Logo row on the left phone.
5. In the inspector’s **Action** section, set **On click** to **Go to canvas**, then set **Canvas** to **Logo**.
6. Click the sparkles symbol on the Logo row and give it the same Action, as the template does for Website’s globe.

![The Projects canvas with the Logo row selected and the inspector’s Action section set to Go to canvas, Canvas Logo; the Canvases list shows Projects, Website and the new Logo canvas.](logo-action.webp "The Logo row now goes to the Logo canvas.")

## 4. Add a back button

The Logo screen’s title came with the copy, so it already goes back. Any graphic can be a back button. Give the tab bar at the bottom of the Logo screen one too:

1. On the Logo canvas, click the tab bar.
2. In **Action**, set **On click** to **Go back**.

Go back returns to wherever you came from. If a graphic should always lead to one place, use **Go to canvas** instead. The same menu has **Open link**, **Run shortcut**, **Set variable**, **Toggle variable** and **Ask the host app**.

![The Logo canvas with its tab bar selected and the inspector’s Action section set to Go back, with the caption Goes back to the canvas you came from.](back-button.webp "The tab bar as a back button.")

## 5. Play it

Open the Projects canvas and click **Play** in the toolbar, or choose **View › Play** (Option-Command-P). The **Try it in Play mode** button in the Action section’s header does the same.

Click the Logo row: the Logo screen opens. Click its title or its tab bar to come back, then try the Website row. While you play, nothing can be moved or changed. Press Esc, or click **Stop**, to go back to editing.

On iPad, tap **Play**, tap through the screens, and tap **Stop** when you’re done.

![Play mode on the Logo canvas after a click on the Logo row: the Logo screen, due 28 Oct, and the play bar with the back arrow, Playing, Logo and Stop.](playing.webp "Playing: the Logo row opened the Logo screen.")

## 6. Export a web player (Mac)

A web player is a folder that plays your Document in any browser, Actions and all.

1. Choose **File › Export…** (Shift-Command-E).
2. Set **Format** to **Web player**. The subtitle says “Saves a folder that plays all three canvases in any browser.”
3. Click **Export…**, give the folder a name and choose where to put it.
4. Open the folder’s `index.html` in a browser and click the rows.

The player shows a **Back** button after a jump and a menu of canvases. Under **More options**, **Include a desktop app project** adds a Tauri project next to the player; building it needs Tauri and Rust. The web player is on the Mac only in Diagrove 1.0.

![The exported web player open in Safari, showing the Logo screen after a click on the Logo row, with the player’s Back button and canvas menu at the top.](web-player.webp "The web player in Safari, after a click on Logo.")

## Where to go next

- [Play mode and Actions](../../guide/play-mode-and-actions/): every kind of Action, and variables.
- [Export for the web](../../how-to/export-for-the-web/): the web player folder and its page options.
- [Run a shortcut from a diagram](../../how-to/run-a-shortcut-from-a-diagram/): a click that runs a shortcut.
- [Share a layer across canvases](../../how-to/share-a-layer-across-canvases/): one header or tab bar on every screen.

---
title: Share a layer across canvases
description: Show one layer, such as a header, a frame or a tab bar, on every canvas of a Document, and edit it once for all of them.
slug: share-a-layer-across-canvases
date: 2026-10-29
order: 4
---
A shared layer appears on every canvas of the Document. Use it for what repeats: a title block, a page frame, a logo, or the tab bar of every screen in a prototype. Change it on any canvas and every canvas changes with it.

## Share a layer

1. Put what should repeat on a layer of its own. To make one, choose **Canvas › New layer** (Option-Command-L), then move graphics onto it: select them, right-click the layer in the sidebar’s **Layers** list and choose **Move selection here**.
2. Right-click the layer in the **Layers** list (on iPad, touch and hold it) and choose **Share with all canvases**.

The layer now shows a small badge in the list. Its tooltip says how many canvases show it, such as “Shared layer, shown on all 3 canvases”. Canvases you add later get it too.

[shot: share-menu] Mac, light. The Layers list with a layer’s context menu open and Share with all canvases highlighted. Point to the menu item.

## Work with it

- **Edit anywhere.** Move, restyle or retype anything on the shared layer, on any canvas: the change reaches every canvas, as one step you can undo. Hiding, locking or renaming the layer is shared too.
- **Draw on it on purpose.** New graphics go on the canvas’s own top layer, even when the shared layer is above it, so drawing on one canvas never draws on all of them. To add to the shared layer, click it in the Layers list first.
- **Order per canvas.** Moving the shared layer up or down changes only the canvas you’re on.
- **Lines.** A line on an ordinary layer can connect to a graphic on a shared layer. A line on a shared layer connects only to graphics on shared layers, because the others aren’t on every canvas. If sharing a layer would disconnect some line ends, Diagrove asks first and says how many; the lines stay where they are drawn.

[shot: shared-badge] Mac, light. The Layers list on the second canvas of a Document, the shared “Header” layer at the top with its badge and tooltip. Point to the badge.

## Stop sharing or delete it

- **Stop sharing**, in the same menu, turns every copy back into an ordinary layer that you can change on its own.
- **Delete from all canvases** removes it everywhere.

More in [Drawing](../../guide/drawing/) and [A clickable prototype](../../tutorials/clickable-prototype/).

---
title: Your first flowchart
description: Draw a checkout flowchart from one line of text, add the “No” path by hand, change it in plain words, tidy it and export it as a PNG.
slug: first-flowchart
date: 2026-10-29
order: 1
---
In this tutorial you draw a small checkout flowchart: a cart, a payment, a check that the payment went through and a receipt. You type the steps in one line, draw one line by hand, change the diagram in plain words and save a picture of it. Everything here works with or without Apple Intelligence, and it takes about ten minutes.

## 1. Start a new diagram

On the Mac, choose **File › New diagram** (Command-N). On iPad, tap **New diagram** on the start screen.

A blank canvas opens. The tool palette floats at the top of the canvas, and the prompt bar floats at the bottom of the canvas. Save it now (Command-S) and call it Checkout.

![A new blank diagram called Checkout on White paper with its grid: the Start your diagram card in the middle of the canvas, the tool palette at the top of the canvas and the prompt bar at the bottom.](blank-canvas.webp "A new diagram, with the prompt bar at the bottom of the canvas.")

## 2. Type the steps

Click the prompt bar and type:

```text
Cart -> Pay -> Paid? -> Send receipt
```

Press Return. On iPad, tap the arrow at the end of the bar. Diagrove draws four shapes joined by arrows, laid out from top to bottom, and a notice says “Drawn from your text”. Because “Paid?” ends with a question mark, it becomes a decision. If it isn’t what you wanted, the notice’s **Undo** takes it away.

> **Tip:** You can label an arrow as you type it. `Paid? -[Yes]-> Send receipt` puts “Yes” on that line, and so does `Paid? -> Send receipt: Yes`.

![The checkout flow just drawn from the prompt bar, from top to bottom: Cart, Pay, the Paid? decision and Send receipt, joined by arrows, with the notice Drawn from your text and Undo.](drawn-from-text.webp "Four steps drawn from one line, with Paid? as a decision.")

## 3. Add the “No” path by hand

A payment that fails should go back to Pay. Draw that line yourself:

1. Choose **Line** in the tool palette, or press L.
2. Control-click the Line button and choose **Elbow** from its menu, so the line bends at right angles instead of running straight.
3. Point at Paid? and its magnets show as dots. Drag from the dot on Paid?’s right point to the dot on the right side of Pay, and let go there. Diagrove goes back to the Select tool with the new line selected.
4. Press Return (or double-click the line) and type “No”. Click an empty part of the canvas to finish.

Both ends of the line are connected, so if you move Paid? or Pay, the line follows. Label the other way out of the decision too: double-click the line from Paid? to Send receipt and type “Yes”.

On iPad, touch and hold **Line** in the palette and choose **Elbow**, drag from dot to dot with your finger or Apple Pencil, then double-tap the new line to type its label.

![The checkout flow with a line from the Paid? decision back to Pay labelled No, and Yes on the line from Paid? down to Send receipt.](no-path.webp "The No line loops back to Pay.")

## 4. Change it in words

Changes go through the same prompt bar. Type this and press Return:

```text
make all decisions orange
```

The change shows on the canvas first. Click **Apply** (or press Return again) to keep it as one step you can undo, or **Discard** to put things back as they were.

Try a few more, applying each one:

- “rename Cart to Basket”
- “add a step after Pay called Fraud check”
- select Pay, then “make it bold”

The sparkle at the start of the prompt bar opens the guide to what you can ask, with examples you can click to put in the bar. It’s also in **Help › What you can ask the prompt bar**, on the Mac and the iPad.

![The checkout flow with make all decisions orange in the prompt bar, the Paid? decision shown orange, and the card above the bar with Change the fill of “Paid?”, Read from your text, Discard and Apply.](change-on-show.webp "The change on show, with Discard and Apply.")

## 5. Tidy the layout

Adding Fraud check laid the flow out again around the new step. Whenever shapes you’ve moved by hand need putting back in order, type “tidy up the whole diagram” in the prompt bar, or choose **Arrange › Auto-arrange › Flow, top to bottom** (Shift-Command-L). The connected shapes are laid out again, neatly spaced, with your hand-drawn “No” line still joining Paid? to Pay.

![The finished checkout flow: Basket, Pay, Fraud check, an orange Paid? decision and Send receipt in bold, with the No line looping back to Pay and Yes on the line to Send receipt.](tidied.webp "The finished flow, laid out again.")

## 6. Export a PNG

1. Choose **File › Export…** (Shift-Command-E), or click **Export** in the toolbar. On iPad, tap **Export**, then **Export…**.
2. Set **Format** to **PNG image**.
3. Choose the **Area**: **Whole canvas**, or **Just the drawing** for a picture cropped to your shapes with a small margin.
4. Choose a **Scale** of 1×, 2× or 3×, and turn on **Transparent background** if the picture will sit on a coloured page.
5. Click **Export…** and choose where to save it. On iPad, tap **Save to Files…**, or **Share** to send it straight on.

The sheet’s subtitle says what you’ll get, including the PNG’s size in pixels.

![The export sheet for Checkout: a preview of the checkout flow, Format set to PNG image, Area set to Just the drawing and Scale 2×, under the subtitle Saves “Diagram” as a PNG picture, 510 × 1,160 px.](export-png.webp "The subtitle gives the PNG’s size in pixels.")

## Where to go next

- [The prompt bar](../../guide/prompt-bar/): everything it reads, with and without Apple Intelligence.
- [Drawing](../../guide/drawing/): shapes, lines, magnets and the tool palette.
- [Outline and auto-layout](../../guide/outline-and-auto-layout/): the other ways to arrange a diagram.
- [Import and export](../../guide/import-and-export/): PDF, SVG and the other formats.
- [Make it clickable](../clickable-prototype/): the next tutorial.

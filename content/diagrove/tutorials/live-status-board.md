---
title: A live status board from a JSON file
description: Build a status board whose colours and words follow a JSON file, kept in the Document or read from a web address, with Match values and Steps rules.
slug: live-status-board
date: 2026-10-29
order: 4
---
A Binding lets a graphic take its words, colours, visibility or progress from data. In this tutorial you build a small status board for three services and a support queue. Each box turns green, amber or red from a JSON file, and says what the file says. You start with a file kept inside the Document, then switch to a web address so the board keeps itself up to date.

## 1. Write the data

Save this as `status.json`, in TextEdit set to plain text or in any code editor:

```json
{
  "services": [
    {"name": "Website", "status": "up"},
    {"name": "Shop", "status": "slow"},
    {"name": "Email", "status": "down"}
  ],
  "queue": {"waiting": 14}
}
```

## 2. Draw the board

1. Choose **File › New diagram** (Command-N). On iPad, tap **New diagram**.
2. Choose **Rounded rectangle** in the tool palette and drag out a box. Type “Website”.
3. Draw a second, wider box below it and type “Support queue”.

Leave Shop and Email for later: you’ll copy the Website box once its Bindings are set.

[shot: board-drawn] Mac, light. A new diagram with two rounded rectangles, Website and Support queue, on White paper. Point to the Website box.

## 3. Colour Website from the file

1. Select the Website box. In the inspector, open **Data** and choose **Add binding › Fill**.
2. Set **From** to **JSON**.
3. Open the **Source** menu and choose **Use a file…**, then choose `status.json`. Diagrove keeps a copy of it inside the Document.
4. In **Path**, type `services[name=Website].status`. This finds the item in `services` whose `name` is Website, and reads its `status`.
5. Set **Rule** to **Match values**. Add three matches with **Add match**: `up` gives light green, `slow` gives light amber, and `down` gives light red. **Otherwise** can leave the box as drawn.

Text matches exactly, so “Up” and “up” are different values. Numbers and true or false match however they’re written.

[shot: match-values] Mac, light. The Website box selected, with the inspector’s Data section showing a Fill binding: From JSON, Source In this document, the path, and Match values with up, slow and down. Point to the Rule menu.

## 4. Put the status in its words

1. With Website still selected, click **+** (Add a binding) in the Data section and choose **Text**.
2. Set **From** to **JSON**, choose **Use a file…** and `status.json` again, and type the same path.
3. Set **Rule** to **Format text** and type `Website: {value}`. The value goes where `{value}` is.

## 5. See it live

Bindings don’t change the drawing you edit. To see what the data does, click **Show live data** in the canvas’s bottom-left corner, above the zoom control. The Website box turns light green and reads “Website: up”. Click it again to see the canvas as drawn. Edits you make while it’s on still change the drawing.

[shot: show-live-data] Mac, light. Show live data turned on: the Website box light green reading “Website: up”. Point to the Show live data button.

## 6. Copy it for Shop and Email

1. Select Website and press Command-D twice. Copies keep their Bindings.
2. Move the copies beside it and type “Shop” and “Email” as their words.
3. For each copy, change the **Path** of both Bindings to `services[name=Shop].status` or `services[name=Email].status`, and change the Format text to `Shop: {value}` or `Email: {value}`.

With live data showing, Shop turns amber and Email red.

## 7. Colour the queue by steps

Match values suits words. For a number, use **Steps**:

1. Select Support queue and add a **Fill** binding from JSON, with the same file and the path `queue.waiting`.
2. Set **Rule** to **Steps**. Set the steps to **at** 0, light green; **at** 10, light amber; **at** 25, light red. **Add step** adds another.
3. Add a **Text** binding with the same path, the rule **Format text** and `{value} waiting`.

The last step the value reaches wins, so 14 waiting is amber. Below the first step, the graphic stays as drawn.

[shot: steps] Mac, light. Support queue selected, light amber and reading “14 waiting”, with the Data section showing Steps at 0, 10 and 25. Point to the steps.

## 8. Read it from a web address

A file kept in the Document stays as it was when the original changes; to update it, choose **Choose another file…** in the Source menu. To have the board follow the data by itself, put `status.json` on a web server and:

1. In each binding, open **Source** and choose **Use a link instead**.
2. Type the address in **Link**. It must start with `https://`.
3. Click **Load now** to read it straight away.

Diagrove reads a link only while you play or show live data, and again every 30 seconds while it does. Opening the Document never reaches the network by itself, and if a read fails, the board keeps the last values it read. This is the only time Diagrove uses the network for your diagrams.

## 9. Play it

Click **Play** (Option-Command-P on the Mac). The canvas’s bottom-left corner shows how the live data stands, with **Refresh live data** to read it again now. Change `status.json` on the server, wait half a minute or refresh, and watch the board follow.

[shot: playing-live] Mac, dark appearance, White paper. The finished board in Play mode: Website green, Shop amber, Email red, Support queue amber, with the live data status and Refresh in the corner. Point to Refresh.

> **Tip:** A colour can come straight from the data, too. With the rule **As it is**, a Fill binding uses the value as a colour: a swatch name such as `teal` or `light amber`, or a hex code.

## Where to go next

- [Bindings](../../guide/bindings/): every property, source and rule, variables and shortcuts included.
- [Play mode and Actions](../../guide/play-mode-and-actions/): buttons that set variables your Bindings follow.
- [Export for the web](../../how-to/export-for-the-web/): the web player reads JSON Bindings too.

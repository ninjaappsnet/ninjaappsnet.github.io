---
title: Reports and Pages
description: A Report is a set of Pages, and a Page is a grid of Visuals. Learn to add, move, resize and undo Visuals, and how a Visual gets its data.
slug: reports-and-pages
date: 2026-10-26
order: 10
---
A Flow shapes your data. A Report shows it. Reports are where you turn the Datasets you have prepared into charts, tables and numbers that other people can read at a glance.

This page explains how a Report is built: Reports, Pages, the grid, and the Visuals that sit on it. If you have not built a Flow yet, start there. A Report only reads the output of a Step, so it needs at least one Input.

## How a Report is organised

A Workbook can hold any number of Reports. Each Report holds Pages, and each Page holds Visuals.

- A **Report** is one collection of Pages, such as “Sales Dashboard”.
- A **Page** is one screen of the Report. Pages appear as tabs along the top.
- A **Visual** is one chart, table, card or Slicer on a Page.

A new Workbook starts with an empty Flow and one empty Report named “Report 1”, with one Page named “Page 1”.

![The Overview Page of the Sales Dashboard in FlectoBI: three cards across the top, a Region Slicer, a line chart, a column chart and a donut chart, with the inspector open on the right.](report-overview.webp "The Overview Page of the Sales Sample, with nothing selected.")

### Work with Reports

Reports are listed in the sidebar under **Reports**.

1. Click **New Report**, or press Option-Command-N, to add a Report.
2. Control-click a Report and choose **Rename…** to change its name. You can also rename it inline and press Return.
3. Choose **Add Page** from the same menu to add a Page.
4. Choose **Delete Report** to remove it. Undo brings it back.

### Work with Pages

1. Click the plus in the tab bar (**Add Page**) to add a Page.
2. Double-click a tab to rename it, or drag a tab to reorder.
3. Control-click a tab for **Rename…**, **Duplicate**, **Move Left**, **Move Right** and **Delete Page**.

A duplicate is named the way Finder names copies: “Page 2 copy”, then “Page 2 copy 2”.

## The grid

Every Page is a grid of 12 columns. Rows are a fixed 60 points high, with a 12 point gap. A Page can be as tall as you need.

Visuals sit on whole cells. When you move or resize one, it snaps to the grid, so a Page stays tidy without any effort. You can place Visuals so they overlap. The drop target turns orange to tell you so.

If the window is too narrow for the Page, FlectoBI scales the Page down to fit. Past the smallest scale, the Page scrolls sideways.

## Add a Visual

1. Select a Page.
2. Choose **Add Visual** in the toolbar, or open **Report** > **Add Visual**.
3. Pick a kind, such as **Column Chart** or **Table**.

On an empty Page you can also click one of the buttons in the middle of the Page: Column, Line, Card, Table or Slicer. **More Visuals** lists the other kinds.

The new Visual lands in the first free spot, scanning from the top left. FlectoBI picks a Dataset for it and fills its Field Wells from your data, so it usually draws at once. The next section shows how to change what it shows.

![Clip of a new empty Page: the Column button adds a chart of Revenue by region, then its X-axis is set to Category and its Legend to Region, and the Visual is made wider.](clip-add-visual.mp4 "Adding a Column Chart and changing its Field Wells.")

## Give a Visual its data

Every Visual reads from exactly one Dataset: the output of one Step. Select the Visual and look at the inspector.

1. Under **Data**, use the Dataset picker to choose a Step. If it says **Choose…**, no Step is chosen yet.
2. Under **Fields**, fill the Field Wells. Each kind has its own wells, such as **X-axis** and **Values**. The [Visuals guide](../visuals/) lists them all.
3. For each Value, choose a Column and an Aggregation such as **Sum** or **Count**.

The Visual draws as soon as it has what it needs. If a Step has not run yet, the Visual says the Step “is not ready yet.” If a Step has a problem, it says so and names the Step. If you delete a Step that a Visual used, the Visual says “The dataset of this visual was deleted.” Pick another Dataset to bring it back.

> **Tip:** A Report only reads Step outputs. To show a different shape of data, add a Transform to your Flow, then pick that Step as the Dataset.

## Move, resize and tidy

Drag a Visual by its title bar to move it. Drag the bottom-right corner to resize it. Both snap to the grid, and each gesture is one undo step.

Each Visual has a minimum size in columns by rows:

| Visual | Smallest size |
|---|---|
| Card | 2 x 2 |
| Slicer | 2 x 3 |
| Heatmap, Filled Map, Bubble Map | 4 x 3 |
| 3D Scatter, Surface Plot | 4 x 4 |
| All others | 3 x 3 |

The inspector’s **Layout** section shows the **Position** and **Size**, and has **Duplicate** and **Delete Visual** buttons. You can also use the keyboard: arrow keys move the selected Visual one cell, and Shift-arrow keys resize it. See [Keyboard and accessibility](../keyboard-and-accessibility/).

Each Visual also has a **Visual options** menu in its title bar. It offers **Edit Fields…**, **Change Type**, **Filter By**, **Clear Selection**, **Duplicate** and **Delete**.

To give a Visual a clearer name, edit its **Title** in the inspector.

## Undo and Redo

Every edit to a Report can be undone, and the Edit menu names what it will undo, for example “Undo Rename Visual” or “Undo Add Value”. A move or a resize counts as one step, however long you drag.

> **Tip:** Try things freely. Delete a Visual, change a chart’s type, or reorder Pages. Undo restores the whole Workbook as it was.

Turning a 3D Visual and choosing values in a Slicer or on a chart are about viewing the data, so they are not edits. A Slicer’s choices are saved with the Workbook. Clicks on a chart are not. [Selections and Slicers](../selections-and-slicers/) explains the difference.

## Show or hide the inspector

Choose **Inspector** in the toolbar, or press Option-Command-I, to show or hide the inspector. When no Visual is selected, it says “No Visual Selected”. Select a Visual on the Page, or add one from the toolbar.

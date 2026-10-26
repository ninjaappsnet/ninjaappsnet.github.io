---
title: Build a monthly sales dashboard
description: Turn a sales CSV into monthly revenue totals and a Report with cards, a line chart and a slicer, then refresh it next month by replacing the file.
slug: monthly-sales-dashboard
date: 2026-10-26
order: 2
---
Many people rebuild the same monthly chart in a spreadsheet every few weeks. In FlectoBI you build it once. Next month you replace the file and the Report updates.

**Goal:** a Report with total revenue, a line chart of revenue by month and a Region slicer, built from your own sales CSV.

**What you need:** a CSV file with one row per sale. This tutorial assumes these Columns: OrderDate, Region, Units and UnitPrice. Yours may be named differently. Use your own names wherever you see these ones.

## Add the file as an Input

1. Choose **File**, then **New**, to open an empty Workbook. It starts with an empty Flow and a Report called Report 1.
2. Drag your CSV file from Finder onto the canvas. Or click **Add Input** in the toolbar, choose your file and click **Add**.
3. Select the new Input. The preview grid shows your rows. Check the Column names in the header row.

![A new Workbook with an empty Flow and the options to add an Input or open the sample.](workbook-empty.webp "A new Workbook starts empty.")

FlectoBI guesses the delimiter, the encoding and the header row. If the Columns look wrong, open the **Format** section of the inspector. Set **Delimiter**, **Header row** or **Skip rows**. If your dates read the wrong way round, set **Date order** to Month first or Day first.

![The Input inspector for a CSV file, with the source file, its delimiter and its encoding.](inspector-input-csv.webp "The options of a CSV Input.")

## Calculate Revenue

1. Select the Input. Click **Add Transform** and choose **Calculate**, in the Columns group. You can also double-click the canvas and type calculate in the search field.
2. Under **New column**, type Revenue.
3. In the Formula field, type `round([Units] * [UnitPrice], 2)`. Use **Insert Column** to pick names instead of typing them.
4. Press **Command-Return** to apply.

The preview now ends with a Revenue Column. If the Formula has a mistake, a plain sentence under the field says what is wrong. A typo in a Column name reads “Unknown column [UnitPrise]. Did you mean [UnitPrice]?”

![A Formula with its plain-English error under the field.](formula-error.webp "Errors say what happened.")

## Add a Month Column

Add another Calculate Step after Revenue. Name the Column Month. Use this Formula:

`date_trunc('month', [OrderDate])`

Every date becomes the first day of its month. Orders from 3 March and 28 March now share one Value.

## Total by month and region

1. Add a **Summary** Step after Month. It is in the **Reshape** group.
2. In **Group by**, choose Month and Region.
3. Click **Add Value**. Choose the Column Revenue and the calculation Sum.

The result has one row for each month and region, with the sum of Revenue.

![The inspector of a Summary Step, grouped by Month and Region with a Sum of Revenue.](inspector-summary.webp "A Summary groups rows and totals them.")

> **Tip:** Group by both Month and Region now. The Region slicer in your Report needs a Region Column in the same Dataset as the chart.

## Build the Report

1. Click **Report 1** in the sidebar. The first Page is called Page 1.
2. Click **Add Visual** in the toolbar and choose **Card**. In the inspector, set **Dataset** to your Summary Step. Put Revenue in **Values** with the Aggregation Sum. Set the title to Total revenue.
3. Add a **Line Chart**. Use the same Dataset. Put Month in **X-axis** and Revenue in **Values**, again with Sum.
4. Add a **Slicer** and set its **Field** to Region.

Drag a Visual by its title bar to move it. Drag the corner to resize it. Both snap to the grid.

![Adding a column chart to an empty Page: it draws at once with suggested Field Wells, then its X-axis and Legend are changed and it is made wider.](clip-add-visual.mp4 "The same steps work for every chart.")

Now tick one region in the slicer. The card and the line follow. Press **Esc** to clear it.

![The Overview Page of the Sales Dashboard sample, with cards, a slicer and charts.](report-overview.webp "A finished Page in the Sales Sample, for comparison.")

## Refresh next month

The Workbook stores the recipe, not the data. The data stays in your CSV file.

1. Replace the CSV file with the new export. Keep the same name and the same folder.
2. Return to FlectoBI. When it becomes the active app again, it notices that the file changed and reads it again.
3. Or press **Command-R** to refresh all Inputs at once.

The Steps recompute in order and the Report redraws. If the file has a new name, select the Input and click **Change File…**.

> **Tip:** Save the Workbook next to your CSV file. Paths are stored relative to the Workbook, so you can move the pair together.

## What you learned

- An Input reads a file as a snapshot, and Refresh reads it again. See [Inputs](../../guide/inputs/).
- Calculate adds a Column from a Formula. See [Formulas](../../guide/formulas/).
- A Summary turns rows into totals. See [Transforms](../../guide/transforms/).
- Every Visual in a Report is bound to one Dataset, and its Field Wells decide what it shows. See [Visuals](../../guide/visuals/).

Next: [Clean and combine Excel exports](../clean-and-combine-excel-exports/).

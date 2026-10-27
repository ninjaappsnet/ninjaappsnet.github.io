---
title: Explore the Sales Sample
description: Follow the data in FlectoBI’s sample Workbook from four CSV Inputs through a Join and Formulas to the Sales Dashboard Report, then cross-filter it.
slug: explore-the-sales-sample
date: 2026-10-26
order: 1
---
The Sales Sample is a Workbook that comes with FlectoBI. It holds a small shop chain’s orders, products and stores, shaped into a Flow and shown in a Report. In about ten minutes you can see how a file becomes a chart, and how a click in one chart changes the others.

**Goal:** understand how a Flow feeds a Report, and use a Selection to filter a Page.

**What you need:** FlectoBI on a Mac with macOS 26 or later. No files of your own. The sample reads without any permission prompt.

## Open the sample

1. Choose **Help**, then **Open Sample Workbook**. On a new, empty Flow you can also click **or open the Sample Workbook**.
2. A window called Sales Sample opens. FlectoBI copies the sample files into its own Documents folder first, so you cannot damage anything.

The window has three areas. The sidebar on the left lists the **Data Flow** and the Reports. The workspace is in the middle. The inspector on the right shows the options of whatever is selected. If the inspector is hidden, press **Option-Command-I**.

## Follow the data through the Flow

Click **Data Flow** in the sidebar. The Flow is a canvas of Steps joined by lines called Connections. Data moves from left to right.

1. Click **Zoom to Fit** if the whole Flow is not in view.
2. Click the Input called **Sales**. Below the canvas, the preview grid shows its Dataset: 3,000 orders with Columns such as OrderID, OrderDate, Region and Units. The header bar above the grid shows the row and Column counts and the status, Ready.
3. In the inspector, look at the **Source** section. It names the CSV file and offers **Change File…** and **Show in Finder**. FlectoBI only reads this file. It never writes over it.
4. Click **Products**, **Stores** and **Footfall** in turn. Each is another CSV file.

![The Data Flow of the Sales Sample, fitted in the window, with the Join Step “Add product details” selected, its rows in the preview grid and its options in the inspector.](flow-overview.webp "The Flow of the Sales Sample. The preview and the inspector follow the selected Step.")

Now click along the Flow from the Inputs to the right. The clip shows the idea: the preview and the inspector change with each Step.

![Selecting the Steps of the Flow one after another, from Sales to the Join, Revenue and Month, then a Summary and an Output.](clip-steps.mp4 "Select a Step to see the data it produces.")

### The Join

Select **Add product details**. This is a Join Step. It matches each order to a product by the ProductID Column, so every row gains a product name, a category and a price. The Join type is Left, which keeps every order even when no product matches.

![The options of the Join Step: the Join type, the key Columns and the suffix for repeated Column names.](inspector-join.webp "A Join matches rows on key Columns.")

### The Formulas

Select **Revenue**. It is a Calculate Step, which adds a Column worked out with a Formula. The Formula is:

`round([Units] * [UnitPrice] * (1 - [Discount]), 2)`

Square brackets name a Column. Units times price, less the discount, rounded to two decimals. Look at the preview: the new Revenue Column is the last one.

![A Calculate Step showing the Revenue Formula, marked valid, with its preview below.](inspector-calculate.webp "Formulas read like a spreadsheet.")

Then select **Month**. It uses `date_trunc('month', [OrderDate])` to turn each date into the first day of its month.

> **Tip:** Click a Column header and press **Option-Command-P** to open its profile. It shows the rows, the empty Values, the distinct Values and the most frequent ones.

### Summary and Output

Select **Monthly by region**. A Summary Step groups rows and totals them. Here it groups by month and region and adds up Revenue and Units. The last Step, **Monthly revenue CSV**, is an Output. It can write the result to a file, but only when you ask it to.

## Open the Report

Reports read only the output of Steps. Click **Sales Dashboard** under Reports in the sidebar. Its Pages are tabs along the top. Open **Overview**.

![The Overview Page of the Sales Dashboard: three cards, a Region slicer, a line chart of revenue by month, a column chart by category and a donut chart of units by region.](report-overview.webp "The Overview Page with nothing selected.")

Each Visual is bound to one Dataset, a Step’s output. Click the line chart. The inspector shows its **Field Wells**: the X-axis holds the month, the Values hold the sum of Revenue.

![The inspector of a selected chart, with its Field Wells and options.](report-visual-inspector.webp "Field Wells decide what a chart shows.")

## Cross-filter the Page

A Selection is a set of Values you choose. It filters every other Visual on the Page that has a Column of the same name.

1. In the **Region** slicer, tick **North**. The cards, the line, the columns and the donut all change to show North only. A chip at the top of the Page reads “Region: North”.
2. Click one column in the column chart, such as Electronics. The cards, the slicer counts and the donut filter to that category too, and the other columns dim. The line chart does not change, because its Dataset has no Category Column.
3. Press **Esc**, or click the chip, to clear the Selection.

![The Overview Page with North ticked in the Region slicer and the other Visuals filtered.](report-overview-north.webp "North only.")

![Ticking North in the slicer, clicking a column in a chart and then clearing the Selection.](clip-cross-filter.mp4 "A Selection filters the other Visuals on the Page.")

Command-click adds a second Value to a Selection. Clicking a single selected mark again clears it.

## What you learned

- A Flow is a chain of Steps: Inputs, Transforms and Outputs. You can see the data at every Step. See [The Flow canvas](../../guide/the-flow-canvas/).
- A Formula is written like a spreadsheet formula, with Columns in square brackets. See [Formulas](../../guide/formulas/).
- A Report shows Step outputs on Pages, and a Selection cross-filters the Visuals of a Page. See [Reports and Pages](../../guide/reports-and-pages/).

Next, build your own: [Build a monthly sales dashboard](../monthly-sales-dashboard/).

---
title: Getting started with FlectoBI
description: What you need to run FlectoBI, how to open the Sales Sample, the parts of the window, and how to build your first Flow and Report.
slug: getting-started
date: 2026-10-26
order: 1
---
FlectoBI is a Mac app for shaping data and showing it. You build a recipe once, as a Flow of Steps, and then draw Reports from the result. When your files change, you refresh and everything follows. This page takes you from a first launch to a first Flow and a first Report.

## What you need

- A Mac with Apple silicon.
- macOS 26 or later.
- FlectoBI is coming to the Mac App Store.

There is no account and no sign-in. Your data stays on your Mac.

## Open the Sales Sample

The quickest way to see what FlectoBI does is to open the sample.

1. Choose **Help › Open Sample Workbook**. On an empty Flow you can also click **or open the Sample Workbook**, under the two buttons.
2. FlectoBI copies the sample files into its own folder and opens **Sales Sample.flectobi**.
3. Click **Data Flow** in the sidebar to see the Flow. Click **Sales Dashboard** under Reports to see the Report.

The sample needs no permissions and no internet connection. It holds 3,000 orders, 12 products and 40 stores. If you change the sample Workbook, FlectoBI keeps your changes the next time you open it.

## The parts of the window

Each Workbook opens in its own window with three areas.

- **Sidebar, on the left.** The **Flow** section has one row, **Data Flow**. The **Reports** section lists your Reports, with a **New Report** button.
- **Workspace, in the middle.** With the Flow selected, the Flow canvas sits above a preview grid. With a Report selected, you see its Pages as tabs, and the Page below.
- **Inspector, on the right.** It shows the options of the Step or Visual you have selected. Show or hide it with **Option-Command-I**, or the **Inspector** button in the toolbar.

A new Workbook starts with an empty Flow and one empty Report named Report 1.

![A new Workbook: an empty Flow with the message Start with Your Data, the Add Files and Connect to Database buttons, and a link to the Sample Workbook.](workbook-empty.webp "A new Workbook opens with an empty Flow.")

## Your first Flow from a CSV

A Flow is a row of Steps. Each Step takes a Dataset, does one job and passes it on. The three kinds are Inputs (read a file or database), Transforms (change the data) and Outputs (write a file).

1. Drag a CSV file from Finder onto the canvas. Or click **Add Input** in the toolbar and choose the file.
2. A Step appears, named after the file. Click it. The preview grid below shows your rows, and the inspector shows how the file is read.
3. Check that the columns look right. If they do not, change the **Delimiter** or **Encoding** in the inspector. See [Inputs](../inputs/).
4. With the Input still selected, choose **Add Transform** in the toolbar and pick a Transform, for example **Filter** or **Sort**. The new Step is connected after the one you selected.
5. Set its options in the inspector. The preview updates as you go.

Every Step shows its own result, so you can see where a number changed. You never have to guess what the recipe did.

![The Sales Sample Flow with the Join Step called Add product details selected, its preview grid below and its inspector on the right.](flow-overview.webp "A Flow on the canvas, with the preview and inspector for the selected Step.")

> **Tip:** Press **Command-Z** to undo any change. Every edit is one undo step, with a name such as Undo Change Delimiter.

## Your first Report

Reports read the output of a Step. They never read your files directly.

1. Click **New Report** in the sidebar, or press **Option-Command-N**.
2. Click **Add Visual** in the toolbar and choose, for example, **Column Chart**.
3. FlectoBI picks a Dataset, the output of one of your Steps, and fills the Field Wells from your data. To change the Dataset, use **Data** in the inspector.
4. In **Fields**, change the Field Wells. For a Column Chart, put a Column in **X-axis** and a Column in **Values**. Pick an Aggregation such as Sum.
5. The Visual draws as soon as it has what it needs. Drag its title bar to move it, and its bottom-right corner to resize it.

Add a **Slicer** to let people choose a Value, such as one Region. Click a bar in a chart and the other Visuals on the Page filter to match.

![The Overview Page of the Sales Dashboard with cards, a Region slicer, a line chart, a column chart and a donut chart.](report-overview.webp "The Sales Dashboard Report in the Sales Sample.")

## Save your work

Choose **File › Save**. FlectoBI saves a **.flectobi** Workbook that holds your recipe, not your data. Read [Workbooks and file access](../workbooks-and-file-access/) to see what that means when you move or share it.

## Where to go next

- [Inputs](../inputs/) for every file type and its options.
- [The Flow canvas](../the-flow-canvas/) for adding, connecting and moving Steps.
- [Preview and Column profile](../preview-and-column-profile/) for checking your data.

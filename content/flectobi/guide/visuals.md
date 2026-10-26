---
title: The Visuals
description: Every Visual in FlectoBI, from column charts to funnels, with what each is for, its Field Wells and its options, including category labels and Top N.
slug: visuals
date: 2026-10-26
order: 11
---
A Visual is one chart, table, card or Slicer on a Page. FlectoBI has the common kinds, plus a few for maps and 3D. This page tells you when to use each one, what goes in its Field Wells, and which options change how it looks.

If you are new to Reports, read [Reports and Pages](../reports-and-pages/) first.

## Field Wells

A Field Well is a slot in the inspector where you drop a Column. Most Visuals have three kinds of well:

- **Category** wells (named **X-axis**, **Y-axis**, **Slices** and so on) decide what the Visual groups by.
- **Legend** splits the marks into series by a second Column.
- **Values** holds the numbers. Each Value has a Column and an **Aggregation**.

The Aggregations a Visual offers are **Sum**, **Average**, **Median**, **Min**, **Max**, **Count** and **Distinct count**. Choose **Add Value** to add another Value, and **Remove this value** to take one away. Labels read like “Sum of Revenue” or “Count of OrderID”.

If a Visual uses fewer Values than you add, the inspector says so, for example that a kind shows only the first value.

![A chart selected on the Overview Page, with the inspector showing its Field Wells and options.](report-visual-inspector.webp "The inspector shows a selected chart’s Field Wells and options.")

## Which Visual to use

| Visual | Use it to | Field Wells |
|---|---|---|
| Column Chart | Compare values across categories, such as revenue by category | X-axis, Legend, Values |
| Bar Chart | Compare categories with long names | Y-axis, Legend, Values |
| Line Chart | Follow a value over time | X-axis, Legend, Values |
| Area Chart | Show a total over time, or stacked series | X-axis, Legend, Values |
| Pie Chart, Donut Chart | Show parts of one whole | Slices, Legend, Values (one) |
| Scatter Chart | See how two numbers relate | Details, Legend, Values (X, then Y) |
| Heatmap | Spot patterns in two categories at once | Rows, Columns, Colour (one) |
| Funnel | Show stages that shrink one by one | Stages, Value (one), Order by |
| Table | Read the exact rows or totals | Group by, Then by, Values |
| Card | Show one big number | Category, Values (up to two) |
| Slicer | Let readers choose values | Field |

The map and 3D kinds have their own pages: [Maps](../maps/) and [3D Visuals](../3d-visuals/).

Some limits are worth knowing. A Scatter Chart draws up to 20,000 points and samples evenly beyond that. A Heatmap shows at most 60 rows and 60 columns. A Funnel shows at most 12 stages. A Table shows up to 1,000 rows. A chart shows up to 1,000 categories. A card tells you when it cut the data.

### Table and Card

A Table has two modes. Fill **Group by**, **Then by** and **Values** to get totals. Leave all three empty and use **Columns** to list raw rows. Numbers are right-aligned.

A Card shows one number. Its help text shows the full value, because a Card can shorten large numbers. A second Value appears as **Second**.

### Funnel

A Funnel orders stages by **Sort**, or by the smallest value of the Column you choose in **Order by**. This helps when the stages are numbered or dated, so the first stage stays on top.

## Options

The **Options** section changes with the kind. These are the ones you will use most.

- **Show legend** appears when a chart has series. Pie and Donut Charts always have it.
- **Show data labels** writes the value on each mark. New column and bar charts turn it on while there are 12 categories or fewer. Labels show only where the text fits.
- **Stack series** stacks columns, bars or areas that have a Legend.
- **Colour scale** for heatmaps, filled maps and surfaces: **Automatic**, **Sequential** or **Diverging**. Automatic uses a diverging scale when values cross zero.
- **Sort by**: **Category, A to Z**, **Category, Z to A**, **Value, low to high** or **Value, high to low**. Dates always run in time order.

### Top N and Other

Choose **Show only the top** and enter N to keep the first N categories after sorting. Sort decides which ones stay.

New Pie and Donut Charts start with a Top N of 8. Everything past eight slices folds into one slice called “Other”, so the pie stays readable. Raise the number if you want to see more.

## Category labels

When a chart has many categories, long names can crowd the axis. Column, Line and Area Charts have a **Category labels** option with four choices:

1. **Auto**: one line if every name fits. If not, FlectoBI slants the names about 40 degrees and keeps whole names where it can, shortening them only when it must. It never hides a name.
2. **Horizontal**: one line each, cut with an ellipsis where a name does not fit.
3. **Slanted**: about 40 degrees, with whole names.
4. **Every other**: shows every other label, on one line. FlectoBI only does this when you choose it.

Line and Area Charts over dates thin the dates by themselves, so they do not offer this option.

### The crowding warning

If your choice cannot work at the chart’s width, the chart keeps your choice and a warning appears in the inspector, under **Category labels**. It says, for example, that slanted names overlap, or that there are too many categories to show even every other name.

![A narrow column chart of 12 teams with slanted names running into each other, and in the inspector the warning that slanted names overlap, with three buttons to fix it.](report-category-labels-warning.webp "The warning under Category labels, with its fixes.")

The warning has buttons to fix it: **Use Auto**, **Use One Line**, and **Show Every Other** when every other name would fit. One Undo returns your earlier choice.

> **Tip:** The simplest fix is often a bar chart. Its names run along the side, where there is room.

## Colour

A chart with one series uses the teal accent. A chart with several series uses a 12-colour palette tuned so that people with colour-blindness can tell colours apart. Colours inside one chart are always clearly different, and the palette has high-contrast variants. Selection never relies on colour alone.

---
title: Transforms: every Step you can add
description: A reference of all 26 FlectoBI Transforms, grouped as the palette groups them: what each does, when to use it and its main options.
slug: transforms
date: 2026-10-26
order: 7
---
A Transform is a Step that takes a Dataset, changes it and passes the result on. You add one after the selected Step, and the preview shows the result at once. This page lists all 26, in the groups the palette uses: Rows, Columns, Text, Combine and Reshape.

## Add a Transform

1. Select the Step the new one should follow.
2. Choose **Add Transform** in the toolbar and pick a name. The menu lists them in groups. Or double-click empty canvas and type a few letters.
3. In the palette, press Return to add it. The new Step is connected to the one you selected.
4. Set its options in the inspector. A one-line explanation at the top says what it does.

![The palette open after the Month Step with col typed, listing Keep/Remove Columns, Rename Columns, Reorder Columns, Conditional Column, Split Column, Combine Columns and Calculate](flow-palette.webp "Typing col lists every Transform that works on Columns.")

The search knows other names too. Try *vlookup*, *group by*, *union*, *trim* or *melt*. A Step with incomplete options shows a hint, such as **Enter a formula.**, not a red error.

> **Tip:** To put a Transform in the middle of a Flow, right-click a Step and choose **Insert Transform Between**, or right-click a wire.

## Rows

These Transforms choose which rows stay. They never change the Columns.

### Filter
Keeps or removes rows that meet your conditions. Use it to drop test orders or to keep one region. Choose **Keep matching** or **Remove matching**. Define a match with **Conditions** (a Column, an operator and a Value, joined by **all** or **any**) or with a true or false Formula. Operators include equals, is at least, contains, starts with, is empty and matches regex. With no conditions, every row passes.

![The Filter inspector with one condition: Revenue is at least 300](inspector-filter.webp "A Filter that keeps large orders.")

### Sort
Puts the rows in order by one or more Columns. Use it before a report table or an Output. **Add Column**, then choose Ascending or Descending. The first Column leads and the next breaks ties. Empty Values come last.

### Remove Duplicates
Removes rows that repeat the same Values. Tick the Columns that define a duplicate. None ticked means all Columns. The first row of each group is kept. **Match case** is optional.

### Slice Rows
Keeps or removes a range of rows by position. Use it to cut a title block or take the first 100 rows. Set the first row and the last row, or **Through the last row**.

### Sample
Keeps a random selection of rows, by **Percentage** or **Number of rows**. The **Random seed** (42 by default) makes the same rows come back each run. **Pick Another Sample** changes it.

## Columns

These Transforms add, remove or change Columns.

### Keep/Remove Columns
Chooses which Columns stay. Choose **Keep columns** or **Remove columns**, then tick Columns. At least one must remain.

### Rename Columns
Gives Columns new names. Type the new name beside the old one. **Reset All** undoes your renames. Two Columns cannot share a name.

### Reorder Columns
Changes the order. Sort **A to Z**, **Z to A**, return to **Original Order**, or drag. **Keep columns that are not listed** decides what happens to the rest.

### Calculate
Adds a Column worked out with a Formula. Use it for revenue, a month or a margin. Give the new Column a name. An existing name is replaced in place. See [Formulas](../formulas/).

### Conditional Column
Adds a Column whose Value depends on rules. **Add Rule** for each case, then set **Otherwise**. Rules are checked from the top, and the first match wins. Use it when a Formula would be a long chain of if tests.

### Split Column
Splits one Column at a delimiter, such as a comma, dash or space. Choose **Into columns** or **Into rows**. Into rows repeats the other Columns for each part. Tick **Keep the original column** if you want it.

### Combine Columns
Joins several Columns into one, in the order you pick. Choose a separator and a name. **Skip empty values** avoids doubled separators.

### Change Type
Converts Columns to text, whole number, decimal, true / false, date or date and time. Pick the **Date format** that matches your data. Under **Values that cannot be converted**, choose **Become empty** or **Stop with an error**. Use it to fix a date that was read as text.

### Row Number
Adds a Column that numbers the rows, starting at 1 by default. It is placed first and follows the current order, so sort before it.

## Text

These work on text Values, in the Columns you choose.

### Find & Replace
Finds text and replaces it. Options: **Match case**, **Whole value only** and **Regular expression**. It applies to chosen Columns or **All text columns**.

### Change Case
Changes text to UPPER, lower or Title case.

### Whitespace
Trims spaces at the start and end, collapses repeated spaces, or removes all whitespace. Use it before a Join, since a stray space stops two Values from matching.

### Replace Empty
Puts a Value into empty cells. **Treat whitespace-only text as empty** catches cells that look blank. Columns that cannot hold the Value are left alone.

### Fill
Fills empty cells from the nearest Value above (**Down**) or below (**Up**). Use it for exports that show a group name once and leave the rows below blank.

## Combine

These bring two or more Datasets together. They take several Connections.

### Join
Combines two Datasets by matching rows on key Columns. Use it to add product details to orders. It needs exactly two Connections, and the first is the first Dataset. Choose a join type: Inner, Left, Right, Full, Subtract or Intersect. **Add Key** for each Column pair. All keys must match. Repeated names from the second Dataset get a suffix, ` (2)` by default. Without keys you see **Choose the columns to match on.**

![The Join inspector: a Left join of Sales and Products on ProductID](inspector-join.webp "Left keeps every order, even one with no product.")

### Stack
Puts Datasets on top of each other, such as one file per month. It needs at least two Connections. Match Columns by **Name** or by **Position**. Missing Columns stay empty.

## Reshape

These change the shape of the Dataset.

### Summary
Groups rows and works out totals. Choose **Group by** Columns, then **Add Value** for each calculation: Sum, Average, Median, Min, Max, Count, Distinct count, First, Last, Std. deviation, Variance or Concatenate. Each result can have its own name.

![The Summary inspector grouping by Month and Region](inspector-summary.webp "Group by two Columns and total Revenue.")

### Pivot
Turns the Values of one Column into new Columns. Choose that Column, the Column that fills them and how repeats are combined. It allows at most 500 distinct Values.

### Unpivot
Turns several Columns into rows of names and Values. The new Columns are called Attribute and Value. Use it when months sit in separate Columns.

### Transpose
Flips rows and Columns. It has no options and allows at most 1,000 rows. Every Value becomes text.

### Header Row
Uses the first row as Column names, or turns the names back into a row. Use it when a file has a title line above the real header.

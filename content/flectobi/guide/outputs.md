---
title: Outputs: write your data to a file
description: How FlectoBI Outputs work: the file types, their options, when a file is written, auto-write, and why a source file is never overwritten.
slug: outputs
date: 2026-10-26
order: 9
---
An Output is the Step that writes a Dataset to a file. Use it to hand shaped data to a colleague, to feed another tool or to keep a snapshot. Reports do not need Outputs. They read the Steps directly.

## Add an Output

1. Select the Step whose data you want to write.
2. Choose **Flow**, then **Add Output…**. Or use **Add Transform** and choose **Output…**.
3. In the save panel, type a name and choose a place. The default name is Output.csv.
4. Check the options in the inspector.
5. Click **Write Now**.

![The Output inspector for a CSV file, with its options and the Write Now button](inspector-output.webp "The sample’s Monthly revenue CSV Output.")

The name decides the type. FlectoBI creates an empty file first, so it can ask macOS for permission to write there.

## File types

| Type | Name ends in | Good for |
|---|---|---|
| CSV / TSV | .csv, .tsv | Any other tool |
| JSON | .json | Apps and scripts |
| Parquet | .parquet | Large Datasets |
| Excel | .xlsx | People who open it in Excel |

FlectoBI cannot write SQLite files, and an Output cannot replace a Workbook. It tells you so and asks for another file. If the name and the format disagree, you see **The file name ends in .X but the format is Y.**

### CSV and TSV

- **Delimiter**: comma, semicolon, tab, pipe or your own.
- **Decimals**: automatic, dot or comma. Automatic uses a comma when Values are separated by semicolons.
- The first row always holds the column names.

A comma cannot separate both Values and decimals. Choose another delimiter or decimal separator.

### JSON

By default the file is one array of objects. Tick **One object per line (JSON Lines)** for one object on each line. Infinity and not-a-number are written as null.

### Parquet

Parquet keeps Column types and compresses well. It suits large Datasets.

### Excel

The file is always **.xlsx**, never the older .xls. It has one sheet, named after the Step, with a bold header row. A sheet holds at most 1,048,575 rows and 16,384 Columns. For more rows, you see a message that suggests CSV or Parquet. The sheet name must be one Excel allows.

## When a file is written

Nothing is written by surprise. Opening a Workbook never writes a file.

- **Write Now** writes this Output. The result line says how many rows were written and when.
- **Write All Outputs** (Shift-Command-R in the **Flow** menu) writes every Output.
- **Write automatically when the data changes** rewrites the file whenever the data changes. It starts only after you have used **Write Now** or **Write All Outputs** once in this session.

> **Tip:** Switch on auto-write for a file someone else reads. Refresh the Inputs, and the file follows.

## Your sources stay safe

FlectoBI never writes over a file it reads. If an Output points at one of your Input files, you see **This output would overwrite “sales.csv”, which this flow reads. Choose another file.** **Write Now** stays off until you do.

Writes are also staged. FlectoBI writes a temporary file and copies it over the destination only when it is complete. If something fails, **The file was left as it was.** That covers a full disk, a file being written somewhere else at the same moment and a missing permission.

## If a write fails

- **FlectoBI can’t write to this file.** Click **Grant Access…** in the banner, or **Change…** to choose the file again. See [Workbooks and file access](../workbooks-and-file-access/).
- **There is not enough disk space.** Free some space, or write to another disk.
- **Some outputs could not be written.** After **Write All Outputs**, the alert lists each Step and its reason.

Use **Show in Finder** to find the file once it is written.

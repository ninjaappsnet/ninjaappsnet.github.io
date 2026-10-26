---
title: Inputs and their options
description: Every file type FlectoBI reads as an Input, the options for CSV, JSON, Excel and SQLite files, and how and when your data is read again.
slug: inputs
date: 2026-10-26
order: 3
---
An Input is a Step that reads data. It is where every Flow starts. This page lists the file types FlectoBI reads and what you can set for each. For databases, see [Databases](../databases/).

## Adding an Input

Choose one of these:

- Drag files from Finder onto the Flow canvas.
- Click **Add Input** in the toolbar. It opens a file panel.
- Choose **Flow › Add Input Files…**, or press **Shift-Command-I**.

You can choose several files at once. Each one becomes its own Step. If FlectoBI cannot read a file, it names it in a message and adds the others.

## File types

| Type | File endings |
| --- | --- |
| CSV and text | .csv, .txt |
| Tab-separated | .tsv, .tab |
| JSON | .json |
| JSON Lines | .ndjson, .jsonl |
| Parquet | .parquet |
| Excel and similar | .xlsx, .xlsm, .xlsb, .xls, .ods |
| SQLite | .sqlite, .sqlite3, .db |

FlectoBI also reads from PostgreSQL, MySQL and MariaDB servers.

Select an Input and the inspector shows a **Source** section with the file name, where it is, **Change File…**, **Show in Finder**, and the size of the Dataset. The **Format** picker offers **CSV / TSV**, **JSON**, **Parquet**, **Excel** and **SQLite**. FlectoBI guesses from the ending, and you can change it.

![The inspector of a CSV Input, showing the Source and Format sections with delimiter, encoding and header options.](inspector-input-csv.webp "The Input inspector for the Sales file.")

## CSV and TSV options

Most problems with CSV files are about how the file is read. Change these in the inspector and watch the preview.

- **Delimiter:** Auto-detect, Comma, Semicolon, Tab, Pipe, or Custom with your own character.
- **Encoding:** Automatic, UTF-8, UTF-16, Latin-1, Windows-1252 or Mac Roman. Automatic reads UTF-8 and UTF-16, and Windows-1252 when the file is not UTF-8.
- **Header row:** Auto, Yes or No. This says whether the first row holds Column names.
- **Skip rows:** the number of rows before the header, such as a title.
- **Read every column as text:** keeps leading zeros, such as 00123, and stops FlectoBI guessing types. Use the **Change Type** Transform afterwards.
- **Date order:** Automatic, Month first, Day first or Year first. A date like 03/04/2025 can mean two things. Choose the order your file uses.
- **Decimals:** Automatic, Dot or Comma. Choose Comma for numbers written as 1.234,56.

The last two are off while **Read every column as text** is on.

## JSON and Parquet

For JSON, the **Layout** is Auto, Array or Lines. Array means one list of objects. Lines means one object per line. Auto works it out, and also opens API responses that wrap their records in an object.

Parquet files carry their own Column names and types, so there is nothing to set.

## Excel files

FlectoBI reads Excel files in a separate, sandboxed helper. A damaged file cannot take the app down with it.

- **Sheet:** choose which sheet to read. FlectoBI starts with the first visible sheet.
- **First row has column names:** tick it when the first row is a header.
- **Skip rows** and **Range:** read only some cells, for example A1:F200.
- **Read every column as text:** as for CSV.

If a workbook is protected by a password, remove the password in Excel first. If a sheet is very large, save it as CSV or Parquet.

## SQLite files

Choose the **Table** to read. Tables and views are both listed. FlectoBI opens the database read-only. If it asks for access to the folder, click **Grant Access…**. See [Workbooks and file access](../workbooks-and-file-access/).

## Reading the data again

An Input is a snapshot. FlectoBI reads it when the Workbook opens and when you refresh.

- Click **Refresh** in the toolbar, or press **Command-R**, to read every Input again.
- Use **Refresh** in one Input’s inspector to read only that file.
- When you switch back to FlectoBI, it reads again any file that changed while you were away.

Steps and Reports that depend on the Input update by themselves. To stop a long run, press **Command-.**.

> **Tip:** Large files are fine. FlectoBI works on the data in a fast engine and shows pages of rows as you scroll. If a Step runs out of memory, filter or summarize earlier in the Flow.

## Common messages

- “could not be found”: the file moved. Choose it again with **Change File…**.
- “needs permission to read”: choose the file again, or use **Grant Access…** in the banner.
- “is not UTF-8 text”: pick the right **Encoding**.

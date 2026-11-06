---
title: Large database tables
description: How FlectoBI shows a big table at once, loads the rest in the background, lets you stop it, and runs Filters, Joins and more on the server so fewer rows travel.
slug: large-tables
date: 2026-10-31
order: 5
---
A table with millions of rows should not make you wait. A database Input shows its first 1,000 rows at once and loads the rest in the background. Steps right after it can run on the server, so fewer rows travel. This page explains the sample, the **Import** and **Order** settings, **Stop**, and the shaded “On the server” region on the canvas. To connect to a database first, see [Connecting to databases](../databases/).

## The sample comes first

When you add a database Input, its preview shows the first 1,000 rows at once. The Steps after it run on those rows straight away. Everything that rests on the sample says so.

- A small grey **Sample** tag sits beside the row count in the preview bar, and on the cards of the Steps after the Input. Its tooltip says, for example, “Based on a sample of 1,000 rows. Updates when all rows are loaded.”
- A Visual built on a sample carries the same tag. Its tooltip says “Based on the first 1,000 rows. Updates when all rows are loaded.”
- In the Input’s inspector, the size line starts with “Sample:”.

The rest of the table loads in the background. When it lands, the tags go and every Step after the Input runs again on all the rows.

## Choose the rows: Import and Order

A table Input has two rows in the **Data** section of its inspector.

**Import** chooses how much to read.

- **All rows** reads the whole table.
- **First…** reads only the first rows. Type a number, such as 5,000,000, and press Return. The number must be a whole number above 0. “First” means first in the **Order** below.

Changing **Import** while a load runs stops that load and starts a new one. **Undo** brings the old setting back.

**Order** decides which rows come first. They are the sample, the first rows of the import, and the rows a Slice Rows Step keeps.

- **Newest first by** the table’s key, such as “Newest first by id”. FlectoBI uses it when the table has a single primary key that holds whole numbers.
- **Newest first by** another column. The pop-up lists the columns the server has an index on that hold numbers or dates. An unindexed column would make the server sort the whole table every time.
- **Server order (no key found)** when there is nothing to order by. FlectoBI takes the rows in the order the server gives them.

A Custom Query has no **Order** row. It reads in the order the server gives.

## Progress, Stop and Load All Rows

While the rest loads:

- The Input’s card shows a thin bar, and “1.2M of ~10M” in place of its row count. Before the load starts it says “Waiting” or “Reading”, and while the server sorts the table, “Sorting”.
- The preview bar says “Loading all rows” with a percentage, and has a **Stop** button.
- The inspector shows “Loading all rows: 1,234,567 of about 10,000,000 (12%)” under a bar, with **Stop**.
- Only one Input loads at a time. A waiting one says “Another input is loading first; this one loads the rest after it.”

You can keep working. Edit a Step after the Input and it runs again on the sample, and the load goes on.

**Stop** is also **Command-.** (**Flow › Stop**). A stopped Input keeps its sample. It says, for example, “Stopped after 1,234,567 of about 10,000,000 rows. Showing the first 1,000.” The Steps after it keep their results and their **Sample** tag. Click **Load All Rows** to start again from the beginning.

If the connection fails during the load, the Input also keeps its sample. It shows the server’s sentence and **Try Again**. **Refresh** reads the table again from the start.

An Output never writes a sample. While the rows load it says “Waits for all rows to load.”, and **Write Now** writes nothing until they are in.

A Join of a table that is still loading looks up the matching rows on the server for the keys of its first input. The preview then shows real matches. If it cannot, the Step says “Only a sample of the second input’s rows is matched here, so some matching rows may be missing until all rows load.”

## Steps that run on the server

Filtering a table on your Mac means downloading it first. When the Steps right after a database Input would give the same result on the server, FlectoBI sends them with the import. Only the rows and columns they keep are downloaded.

On the canvas, a shaded region labelled **On the server · name of the source** surrounds the Input and these Steps. The connection that leaves the region says how much comes down: “⇣ 100 rows”. While the load runs it says “⇣ ~10M rows”, or “⇣ 123K rows so far” when the server gave no estimate. A Step in the region wears a small server symbol.

These Steps can run on the server:

- **Filter**, with conditions. A Filter written as a Formula stays on your Mac.
- **Keep/Remove Columns**.
- **Slice Rows**, when it keeps the first rows.
- **Sort**, only when a Slice Rows that keeps the first rows comes right after it. Sorting a whole table alone would download the same rows.
- **Join**, an inner or a left Join whose Inputs come from the same data source.
- **Summary**, with Count, Sum, Min or Max.

FlectoBI does this only for forms it has tested to give the same rows as on your Mac. A Step stays on your Mac when, for example, it sorts text, ignores case, matches a pattern, uses a Formula, or compares with a value the server might read differently. The same is true when the Step before it is used by more than one Step, is shown in a Report, or writes a file. The first Step that cannot run on the server, and everything after it, runs on your Mac.

Select the Input and look at **On the server** in its inspector.

- It lists the Steps that run on the server: “Filter “Region is West” and Keep/Remove Columns run on the server, so only the rows and columns they keep are downloaded.”
- It names the first Step that stays on your Mac, and why: “Sort runs on this Mac: it sorts text.”
- **Show Query** opens the SQL that is sent to the server. You can select and copy it. It holds no password and no user name.

The inspector of a Step in the region says “Runs on the server as part of the import from “orders”.”

If the server refuses the combined query, the Steps run on your Mac instead, without a message. If the server or the connection fails while they run, the Step keeps its sample and says so, for example “FlectoBI tries again in 5 seconds.” It tries again twice, after 5 and after 30 seconds. Then it says “Refresh tries again.”

To edit the query that runs on the server, choose **Convert to Custom Query**. See [The SQL editor and relationships](../sql-editor/).

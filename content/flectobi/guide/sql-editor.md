---
title: The SQL editor and relationships
description: Write one query for a database Input with colours, name completion and error marks. Turn server Steps into a query, and tell FlectoBI how tables relate.
slug: sql-editor
date: 2026-10-31
order: 6
---
A **Custom Query** reads the result of one query instead of a whole table. The server runs it in a read-only session, and FlectoBI imports the result as a snapshot. This page covers the editor you write it in, **Convert to Custom Query**, and relationships, which fill in joins for you. To save a server first, see [Connecting to databases](../databases/).

## Where to write a query

- In the table picker, click **Custom Query…**. The page is one big editor. Press **Command-Return** or click **Add Input**. **Back** returns to the tables.
- On an Input that is already there, choose **Custom Query** in the **Data** section of the inspector. The editor sits in the inspector. FlectoBI applies your text when you click away or press **Command-Return**. **Apply** shows while the text differs from the Input’s.
- Click the **Open Larger Editor** button under the editor for a bigger window called Custom Query. **Apply** (**Command-Return**) writes the text to the Input. **Cancel** gives it back as it was.

## What a query may be

A query must read data. Start it with **SELECT**, **WITH**, **TABLE** or **VALUES**. Enter one query only, with at most one semicolon at the end. Remove **INTO**, because the rows come into FlectoBI, not into a table or a file. For PostgreSQL, remove **FOR UPDATE** and **FOR SHARE** too. A CALL is refused.

FlectoBI checks this as you type. A red dotted line marks the problem. The sentence under the editor says what to change, and **Show** selects the place.

> **Tip:** A query that already filters and summarizes on the server keeps the Dataset small. Use it when a table is very large.

## Colours, names and joins

The editor colours keywords, strings, numbers and comments, in Light and Dark.

A list of suggestions opens by itself as you type, after a dot, and after **FROM** or **JOIN**. Press **Esc** or **Control-Space** to open it yourself.

- **Up** and **Down** move through the list. **Tab** or **Return** takes the highlighted row. **Esc** closes it.
- Rows are tables, views, columns, functions and keywords. A column shows its type and its table. A line under the list says more, such as “bigint, not empty, primary key of orders”.
- Type **sel** and pick the first row for a template, `SELECT ‹columns› FROM ‹table›`. **Tab** moves between the two placeholders. A query with a placeholder left in is not run: the editor says “Fill in or remove ‹table›.”
- Pick a column of a table the query does not use yet, and the row says “adds a join”. Accepting it writes the column, adds the table with a join and fills in the **ON** condition from a key the database declares or a relationship you confirmed. If several relationships fit, FlectoBI asks which one. If none is known, the row says “adds a join (no key known)”, the query gets a **LEFT JOIN** with a placeholder for the condition, and **Define Relationship…** is offered.
- Each completion is one **Undo** step, even when it changes two places.
- A column the query names that none of its tables has gets a red dotted line, and its tooltip says “not in “orders””.

The names come from the copy of the source’s tables that FlectoBI keeps (see [Connecting to databases](../databases/)). Without one, the editor still colours and completes keywords and says “Connect to complete table and column names.” with a **Connect…** button. While the tables are still being read it says “Reading the tables… Their names complete once they’re read.”

If the server refuses the query, the Input shows the server’s sentence, and underlines the place when it can find it.

## Convert to Custom Query

Steps that run on the server (see [Large tables](../large-tables/)) are one query behind the scenes. **Convert to Custom Query** turns them into a Custom Query you can read and edit.

1. Right-click the shaded region, or any card in it, and choose **Convert to Custom Query**. The button is in the **On the server** section of the Input’s inspector too.
2. The cards of the region are replaced by one Input that holds the query. It keeps the name and place of the region’s last Step, so the Connections, Visuals and Outputs that used it are unchanged.
3. The canvas says “Converted 3 steps into one Custom Query.” The new Input is selected, with its query in the editor.

**Undo** brings all the cards back in one step. The command is greyed out when the query cannot be written, and its tooltip says why. While FlectoBI is still writing the query, the tooltip says “FlectoBI is still writing these steps’ query.” The rows to import and the order of the old Inputs become the query’s own LIMIT and ORDER BY. A Sum of whole numbers comes back as a decimal with no places. The values are the same.

## Relationships

A relationship says that a column in one table holds the key of another table, such as orders.customer_id and customers.id. FlectoBI uses relationships to write joins. Foreign keys that the database declares count already. Relationships add the ones it does not.

Open them in one of three places: **Relationships…** in the table picker, **Relationships…** beside a source in **Settings › Data Sources**, or **Define Relationship…** in the editor’s suggestions. The sheet has four groups.

- **From the Database:** the foreign keys the database declares. You cannot change them.
- **Yours:** the relationships you confirmed. Each shows its check result and has **Delete**.
- **Suggested:** guesses from column names, such as customer_id and the table customers. Each says why FlectoBI thinks so, and has **Check**, **Confirm** and **Dismiss**. **Dismiss** means “don’t suggest it again”.
- **From This Workbook:** relationships a colleague’s Workbook carries. They help in that Workbook only. **Save to My Relationships** keeps one for every Workbook.

Nothing is used until you confirm it. **Check** looks up the first 1,000 values of the column on the server and reports, for example, “98% of 1,000 values found”. Confirming an unchecked one runs the check first. When a check looks doubtful the button reads **Confirm Anyway**.

Click **Add Relationship…** to make one yourself. Choose a table and a column, then the table and column they refer to. Its pop-up lists keys first. If you choose a column that is not a key, the sheet warns that a join on it can repeat rows.

Where relationships are used:

- **The editor** writes the **ON** condition of a join, as above.
- **The Join Step.** When both of its Inputs are tables from one source and exactly one relationship links them, the keys are filled in. If several fit, the key row’s pop-up lists them under **From relationships**. Keys you set yourself are never changed.
- **The table picker.** With tables ticked, **Add Related Tables** ticks every table one relationship away. Its title says how many, such as “Add 3 Related Tables”.

A Workbook keeps the relationships it uses, so a colleague gets them as hints. It holds no login and no values. A relationship whose table or column is gone from the database is marked “Missing in the database” and is not used.

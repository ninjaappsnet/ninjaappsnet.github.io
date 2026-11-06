---
title: Build a Report from a database
description: Save a PostgreSQL or MySQL server as a data source, pick a table or write one SELECT, shape the result, build a Report and refresh it later.
slug: report-from-a-database
date: 2026-10-31
order: 5
---
Business data often lives in a database. FlectoBI can read from PostgreSQL and from MySQL, including MariaDB. It only reads. It never writes to your database, and your login stays in your Mac’s Keychain.

**Goal:** a Report built on a table or a query from a database.

**What you need:** the host name, the port, the database name, a user name and a password. Ask your administrator for an account that can read the tables you need. An account with read rights only is the safest choice, and the sheet reminds you: “Use a read-only database user.”

## Connect

1. Choose **Flow › Connect to Database › New Data Source**, then **PostgreSQL…** or **MySQL or MariaDB…**. On an empty Flow, click **Connect to Database** and choose from the same menu.
2. Fill in the sheet: **Name**, if you want one. **Host**, such as db.example.com. **Port**, which starts at 5432 for PostgreSQL and 3306 for MySQL. **Database**. **User**. **SSL**, explained below. **Password**.
3. Click **Test Connection**. On success the sheet says “Connected. N tables and views found.” You can click **Cancel** while it is connecting.
4. Click **Continue**. FlectoBI saves the data source on this Mac and shows its tables.

![The connection sheet for a PostgreSQL source, with the host, port, database, user, SSL and password.](sheet-postgres.webp "The PostgreSQL sheet.")

![The connection sheet for a MySQL source.](sheet-mysql.webp "The MySQL sheet.")

If something is wrong, the sheet says what, in a sentence. Examples are “Authentication failed. Check the user name and password.”, “The host name could not be found.” and “The server did not respond in time.” A server older than FlectoBI supports says so too. See [Databases](../../guide/databases/) for the list.

## Choose the SSL mode

SSL decides whether the connection is encrypted and whether the server’s identity is checked. The picker offers **Off**, **Prefer**, **Require** and **Verify certificate**.

- For a server on another machine, use **Verify certificate** when you can. FlectoBI checks the certificate against the trusted certificates of macOS. A new connection to another machine starts at **Require** for PostgreSQL and at **Verify certificate** for MySQL.
- **Require** encrypts, but does not check who is on the other end. For MySQL, a note under the picker says so.
- **Off** to another machine lets others read the password and the data on the network. For MySQL, FlectoBI warns you. Choose it only when the server offers nothing else.
- A server on your own Mac is fine on its defaults, because the traffic stays on the Mac.

> **Tip:** If the server offers only outdated encryption, FlectoBI says so and asks you to have TLS 1.2 or later turned on.

## Where your login goes

Your user name and password are saved in the macOS Keychain, one item for each data source. Under **Keep the User Name and Password** you choose whether the item stays on this Mac or syncs with iCloud Keychain. They are never saved in the Workbook, so you can send the Workbook to a colleague without sharing them. A colleague connects the source once with their own login, using **Connect…** in the Input’s inspector.

## Read a table, or write one SELECT

The table picker lists the source’s tables and views, with a row estimate for each. Choose how to read.

- **Tables:** tick one or several, then click **Add Table** (or **Add 3 Tables**, and so on). Each becomes an Input named after the table.
- **Custom Query…:** write a single query in the editor. It runs on the server in a read-only session. Click **Add Input** or press **Command-Return**.

A custom query must start with SELECT, WITH, TABLE or VALUES. Use one query only. Remove INTO. One semicolon at the end is allowed. The editor marks a problem before you add the Input. A CALL is refused. The editor colours the words and suggests table and column names as you type. See [The SQL editor and relationships](../../guide/sql-editor/).

For example, to read only this year’s orders you might write a query that selects the order id, date, region and total from the orders table, with a condition on the date. A query that reads less comes back faster, and needs less memory, than a whole table that you then filter.

FlectoBI copies the result into the engine as a snapshot.

## Watch a big table load

Click the new Input. Its first 1,000 rows appear at once, tagged **Sample**, and the Steps you add after it work on those rows straight away. The rest of the table loads in the background, and the Input’s card shows the progress. Click **Stop** if you have seen enough. When all rows are in, the tag goes and the Steps run again on everything. For the details, and for Steps that run on the server, see [Large tables](../../guide/large-tables/).

## Shape the data

Select the new Input and look at the preview. Then use Transforms as in the other tutorials:

1. **Change Type**, if a Column came in as text but holds dates or numbers.
2. **Filter**, to keep the rows you need.
3. **Summary**, to group by month or region and total the numbers. See [Build a monthly sales dashboard](../monthly-sales-dashboard/).

Doing the heavy filtering in the query is kinder to the server. Doing it in the Flow lets you change your mind without writing SQL.

## Build the Report

1. Click **New Report** in the sidebar.
2. Click **Add Visual** and choose **Column Chart**. Set **Dataset** to your last Step.
3. Put a category in **X-axis** and a number in **Values**, such as the Sum of total.
4. Add a **Card** and a **Slicer** in the same way.

![The Overview Page of the Sales Sample with a slicer, cards and charts.](report-overview.webp "A finished Page, from the Sales Sample.")

A column chart with many long names can crowd. FlectoBI never hides a name by itself. If the **Category labels** option you chose cannot fit, a warning under it in the inspector offers **Use Auto** and **Use One Line**, and **Show Every Other** when every other name would fit.

![A narrow column chart with slanted names running into each other, and in the inspector the warning that slanted names overlap, with its three fixes.](report-category-labels-warning.webp "The crowding warning and its fixes.")

## Refresh

A database Input is a snapshot. It does not stay connected.

1. Click **Refresh** in the toolbar, or press **Command-R**. FlectoBI connects, reads the table or query again and recomputes the Steps. The Report redraws.
2. A Workbook from someone else does not connect on its own. It asks once before it uses a login saved on this Mac, and otherwise waits for you to click **Connect…**.
3. To change the server or the user, select the Input and click **Edit Source…** in its inspector. Saving changes the source for every Input that reads it.

## What you learned

- A database is saved once as a data source. An Input from it is read-only and a snapshot. See [Databases](../../guide/databases/).
- The login lives in the Keychain, not the Workbook. See [Databases](../../guide/databases/).
- A big table shows a sample first and loads the rest in the background. See [Large tables](../../guide/large-tables/).
- You can shape the result and build a Report as with any Input. See [Reports and Pages](../../guide/reports-and-pages/).

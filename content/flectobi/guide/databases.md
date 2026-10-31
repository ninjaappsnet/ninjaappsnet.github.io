---
title: Connecting to databases
description: Save a PostgreSQL, MySQL or MariaDB server as a data source and pick its tables. SSL modes, where your login is kept, supported servers and common errors.
slug: databases
date: 2026-10-31
order: 4
---
FlectoBI can read from PostgreSQL, MySQL and MariaDB. It only reads. It never writes to a database, and it never changes one. This page shows how to save a server as a data source, pick its tables, and what to do when a connection fails. For tables with millions of rows, see [Large tables](../large-tables/). To write your own query, see [The SQL editor and relationships](../sql-editor/).

> **Tip:** Use a read-only database user. The sheet says “Use a read-only database user.” under the **User** field. Ask your administrator for an account that can read the tables you need and nothing else.

## Save a data source

A data source is a server you save once. Every Workbook on this Mac can then pick tables from it.

1. Choose **Flow › Connect to Database › New Data Source**, then **PostgreSQL…** or **MySQL or MariaDB…**. Use the MySQL one for MariaDB too. The same menu is under **Add Input** in the toolbar, in the right-click menu of the canvas, and on the **Connect to Database** button of an empty Flow.
2. Type a **Name** if you like. Without one, FlectoBI shows the database and host, such as “shop on db.example.com”.
3. Fill in **Host**, **Port**, **Database** and **User**. The port starts as 5432 for PostgreSQL and 3306 for MySQL.
4. Choose the **SSL** mode. See below.
5. Type the **Password**.
6. Click **Test Connection**. FlectoBI tells you how many tables and views it found.
7. Under **Keep the User Name and Password**, choose where your login is kept. See below.
8. Click **Continue**. FlectoBI saves the source and opens the table picker.

![The sheet for a new PostgreSQL data source with host, port, database, user, SSL and password fields and the Test Connection button.](sheet-postgres.webp)
![The sheet for a new MySQL data source with the same fields, the port set to 3306.](sheet-mysql.webp)

If you already saved a source for the same server, database and user, the sheet says “You already have this source” and offers **Use It**.

## Pick tables

The table picker shows the source’s name and address above a list of its tables.

- Type in **Search tables** to narrow the list.
- Each row shows the table’s name, its kind (Table, View or Materialized view) and a row estimate, such as “about 1.2M rows”. A table already in this Workbook says “Already added”. You can add it again.
- Tick one table or several. The button reads **Add Table**, or **Add 3 Tables**, and so on.
- Each table becomes its own Input, named after the table. The new Steps are stacked at the left of the canvas. One **Undo** takes them all away.

FlectoBI keeps a copy of the table and column names on this Mac, so the picker opens at once. The copy holds names and keys, never rows. FlectoBI reads it again when it is more than a day old. Click the **Refresh Schema** button beside the search box to read it now. On a big database a line under the list says “Reading columns…”. You can pick tables meanwhile.

If this Mac has no password for the source, the picker asks for it first. If the connection fails, the picker says why, with **Try Again** and **Edit Source…**.

The picker also has **Custom Query…** for your own query and **Relationships…**. See [The SQL editor and relationships](../sql-editor/).

## Change a table or a source

Select a database Input. Its inspector has a **Source** section and a **Data** section.

- **Source** names the data source and its address. **Edit Source…** opens the sheet again. Saving it changes the source for every Input that reads it, in every Workbook. **Change** reads this Input’s table from another source of the same kind. A **Password** field shows when this Mac has none for the source. **Test Connection** is here too.
- **Data** has **Table** and **Custom Query**. Choose another table from the **Table** pop-up. Views are marked “(view)”. For the rest of the section, see [Large tables](../large-tables/).

To rename or delete saved sources, open **Settings** with **Command-,** and choose **Data Sources**. Each row shows a name you can change, the address, **Relationships…** and **Delete…**. Deleting a source removes its password from the Keychain. Workbooks that read it ask you to connect again.

## What the SSL modes mean

SSL decides whether the conversation between your Mac and the server is encrypted, and whether FlectoBI checks who it is talking to.

| Mode | In plain words |
| --- | --- |
| **Off** | Nothing is encrypted. Anyone on the network could read the password and the data. |
| **Prefer** | Encrypted when the server offers it. FlectoBI does not check the server’s identity. |
| **Require** | Always encrypted. The server’s identity is not checked. |
| **Verify certificate** | Always encrypted, and FlectoBI checks the server’s certificate against the certificates your Mac trusts. |

For a server on another machine, choose **Verify certificate** whenever you can. A new connection to another machine starts at **Require** for PostgreSQL and **Verify certificate** for MySQL. A connection to your own Mac starts at **Prefer**, because the traffic never leaves it.

If your MySQL server uses its own certificate, **Verify certificate** may fail. FlectoBI then suggests **Require**. For MySQL, the sheet shows a warning under the SSL choice when the mode is weaker than it should be for the server you named.

## Where your login goes

Your user name and password are saved together in your Mac’s Keychain, one item for each data source. They are never saved in a Workbook or in FlectoBI’s own files. Under **Keep the User Name and Password** you choose where the item may go.

- **This Mac.** The default. The item stays in this Mac’s Keychain.
- **This Mac and iCloud Keychain.** The item can sync to your other Macs with the same Apple Account, when Passwords sync is on in System Settings. The choice is greyed out when this Mac is not signed in to iCloud, with an **Open System Settings…** button under it. The first time you pick it, FlectoBI asks you to check that Passwords sync is on. Click **Passwords Sync Is On** to go on.
- **This Mac only, never in backups.** A new Mac asks again.

A Workbook keeps only the source’s name, kind, host, port, database and SSL mode. It never holds a user name or a password. That makes it safe to send to a colleague.

### A Workbook from someone else

A Workbook you did not make never connects by itself.

- If it reads from a server you have not saved, the source is listed under **In This Workbook** in the Connect to Database menu. Its Inputs and the Visuals they feed say “Connect to load the data.” Click **Connect…** in the Input’s inspector and type your own user name and password. **Save to My Data Sources** is ticked. FlectoBI saves the source only once the connection works. Untick it and FlectoBI forgets the login when you quit.
- If it reads from a source you have saved, a bar asks once: “This workbook wants to read from “name” with your saved login.” Click **Allow** or **Don’t Allow**. Until you allow it, the Inputs say “Allow to load the data.”, FlectoBI makes no connection, and each waiting Input offers **Allow**. FlectoBI remembers your answer on this Mac for that file. If the file is changed somewhere else, it asks again. A Workbook you made on this Mac does not ask.

## Snapshots and refresh

A database Input copies the table or the query result into FlectoBI. It does not stay connected. Your Flow and Reports work on that copy. Click **Refresh** to read a fresh copy. FlectoBI connects only to the hosts and ports of your data sources, and only when it needs to: when you test a connection, open the picker, refresh, or open a Workbook that reads from the source.

## Servers FlectoBI works with

FlectoBI is tested with these servers:

- PostgreSQL 14, 15, 16, 17 and 18.
- MySQL 8.0, 8.4, 9.7 and 26.x.
- MariaDB 10.11, 11.4 and 11.8.

A server older than that is refused at once, with a sentence such as “This server runs MySQL 5.7. FlectoBI needs MySQL 8.0 or later.”

## Common errors

| What you see | What to do |
| --- | --- |
| Authentication failed. Check the user name and password. | Retype them. |
| The server refused the connection. Check the host and port. | Check the address, the port and any firewall. |
| The host name could not be found. | Check the spelling, and your network. |
| The server did not respond in time. | Try again, or ask whether the server is up. |
| The server requires SSL. Choose Require or Verify certificate. | Change the **SSL** mode. |
| The server’s certificate could not be verified. | If the server uses its own certificate, choose **Require**. |
| The server does not allow connections from this Mac. | Ask the administrator to allow your Mac’s address. |
| That database does not exist on this server. | Check the database name. |
| This user may not read that database or table. | Ask for read permission. |
| That table does not exist. | Check the table name. |
| The sign-in for this connection could not be prepared. Check the host, database, user name and password. | Check those four fields in **Edit Source…**. |
| This server runs MySQL 5.7. FlectoBI needs MySQL 8.0 or later. | The server is older than FlectoBI supports. The sentence names the server and the version it needs. |
| Connect to load the data. | This Mac has no login for the source. Click **Connect…**. |
| Allow to load the data. | Click **Allow** in the bar or in the Input’s inspector. |

## What is not supported

- Accounts on MySQL or MariaDB that sign in with ed25519, PARSEC or sha256_password. Ask for an account that uses caching_sha2_password or mysql_native_password.
- Servers that offer only TLS 1.0 or 1.1. MySQL needs TLS 1.2 or later.
- Stored procedures on MySQL and MariaDB (CALL). Only queries that read data are accepted.
- Servers older than the list above.
- Other databases. SQL Server, Oracle and cloud warehouses are not available.

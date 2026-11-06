---
title: Workbooks and file access
description: What a FlectoBI Workbook stores, how to save and share it, and how Grant Access and the Access settings work with the Mac sandbox.
slug: workbooks-and-file-access
date: 2026-10-31
order: 2
---
A FlectoBI Workbook is one file with the ending **.flectobi**. It holds your Flow and your Reports. It does not hold your data. This page explains what that means, how to share a Workbook, and why FlectoBI sometimes asks for permission to read a file.

## What a Workbook stores

A Workbook is a single text file. Inside it are:

- Your Steps, where you placed them, their options and their Connections.
- Your Reports, Pages and Visuals, with their Field Wells and options.
- The choices you made in a Slicer.
- The paths of your files, and the name, host, port, database and SSL setting of any database source. Relationships you defined between its tables are kept too, if the Workbook uses them.

It never contains your rows. It never contains a database user name or password. It never contains a file permission.

Because the data is not inside, the file stays small. When you open a Workbook, FlectoBI reads each Input again from the file or database it points to. Your numbers are always as new as your files.

Opening a Workbook never writes a file. A Workbook from someone else never connects to a database on its own. If it reads from a data source you saved on this Mac, FlectoBI asks once before it uses your saved login. See [Databases](../databases/).

> **Tip:** FlectoBI never changes the files it reads. An Output cannot write to a file that your Flow reads. FlectoBI refuses it and tells you why.

## Saving

Use **File › Save**, or let autosave do it. Every edit can be undone with **Edit › Undo**. A Workbook made by a newer FlectoBI cannot be opened by an older one. FlectoBI says so and asks you to update.

## Why the sandbox asks

Apps from the Mac App Store run in a sandbox. A sandboxed app can open only the files you choose. This protects you: an app cannot quietly read your Documents folder.

When you pick a file, or drop it onto the canvas, FlectoBI remembers your choice. macOS calls this a security-scoped bookmark. It lets FlectoBI open that file again next time without asking. An Input gets permission to read. An Output gets permission to read and write. A permission for a folder covers everything inside it.

These permissions belong to this Mac and this copy of FlectoBI. They are not stored in the Workbook.

## Sharing a Workbook

To share a Workbook, send the **.flectobi** file together with the data files it reads. Keep the same folder layout. The Workbook stores each path relative to itself, so it finds the files when the folder moves as a whole.

On the other Mac, FlectoBI does not yet have permission to read those files. This is expected.

1. Open the Workbook. An orange banner appears at the top, for example “FlectoBI needs permission to read 4 input files.”
2. Click **Grant Access…**.
3. FlectoBI opens a panel at the common parent folder. Choose that folder, or the files themselves.
4. The Steps read their files again by themselves.

One grant of the parent folder usually fixes every Step. If the Workbook has Outputs, the banner says “read and write”, because they need to write.

Logins do not travel. The person who opens the Workbook gives their own user name and password for each database source, and they are saved in their own Keychain. See [Databases](../databases/).

![The Settings window on its Access pane, Files and folders FlectoBI can open, still empty with the words None yet.](settings.webp "Settings › Access lists every file and folder FlectoBI can open.")

## Settings › Access

Open **Settings** with **Command-,**. The **Access** pane is titled “Files and folders FlectoBI can open”. Each row shows a name, where it is, and whether FlectoBI can only **Read** or can **Read & write**.

- Click **Remove** to take back a permission. It takes effect at once.
- Data FlectoBI has already read stays in open Workbooks until you refresh them.
- The list starts empty. A permission appears when you add an Input or an Output.

The **About** pane shows the version and the data engine. It states that all processing happens on this Mac and that FlectoBI never uploads your data.

## When a file is missing or moved

If a file cannot be found, FlectoBI says it may have been moved, renamed or deleted, or be on a drive that is not connected. A permission cannot bring a missing file back. Put the file back, or choose it again with **Change File…** in the Input’s inspector.

SQLite databases need one more permission. They keep small working files next to the database, so FlectoBI asks for the folder that contains it.

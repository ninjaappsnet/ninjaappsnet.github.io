---
title: Import, export and backups
description: Export journals as Markdown or a Dayfolio archive, restore a backup, import a Markdown folder, and keep a live Markdown copy in a folder on your Mac.
slug: import-and-export
date: 2026-10-16
order: 10
---
What you write in Dayfolio stays yours, in formats you can read anywhere. You can export a journal or everything as Markdown files, keep a complete backup you can restore on any device, bring in Markdown notes from elsewhere, and, on a Mac, keep a live Markdown copy of chosen journals in a folder of your own. Exporting and importing are free.

## Export

Start an export from:

- **On a Mac:** File › Export…, a journal’s settings › Export, or *Export…* in a journal’s menu in the sidebar.
- **On iPhone and iPad:** More › Export…, a journal’s settings › Export, or *Export…* in the journal menu at the top.

Choose what to export, one journal or all journals, and a format:

- **Markdown folder:** one text file per entry, with its pictures and files, readable in any notes or text app. It can’t be restored into Dayfolio as it is.
- **Dayfolio archive:** a complete backup you can restore into Dayfolio on any device: every journal with its files and templates, Recently deleted and your settings.

Then choose where to save it. On iPhone and iPad, you pick a folder in Files and the export is written straight into it.

Exports aren’t encrypted, and the sheet says so. If the export includes a journal you lock, Dayfolio asks for Face ID or Touch ID first.

![The Export sheet on a Mac, exporting Engineering Log as a Markdown folder, with the entry count and the note that the files aren’t encrypted.](export-sheet-mac.webp)

### What a Markdown export looks like

Each entry is a file named by its date, time and title, such as `2026-09-24 0912 Payments retry design.md`, in a folder per journal. The file starts with front matter holding the date, journal, template, tags, location and each field’s value, followed by the text fields as sections. Pictures and files are copied next to it and linked, so the folder opens well in Markdown editors and notes apps.

### The Dayfolio archive

A `.dayfolio` file is a single ZIP holding everything as JSON plus your original files. Its format is public, so your data never depends on Dayfolio to be read: see the [archive format](../../archive-format.html).

## Share or export one entry

The entry’s Share button has one list on every device:

- **Share as PDF…** and **Print…** (⌘P),
- **Copy as Markdown** (⌥⇧⌘C on a Mac), ready to paste without front matter,
- *Export as Markdown…*, *Export as PDF…* and *Export as Word…*.

PDFs and Word files are laid out for A4 or US Letter, whichever your region uses. Reports have their own ways to send them; see [Reports](../reports/).

## Restore a backup or import

- **On a Mac:** File › Import….
- **On iPhone and iPad:** More › Import…, or open a `.dayfolio` file from Files, Mail or AirDrop.
- **On first launch:** *Already have journals? Import…* under the first page.

**A Dayfolio archive** restores by adding only what’s missing. Nothing already on the device is changed or removed. Before anything happens, the sheet names the archive, its journals and the dates of its entries, so you can check it’s the backup you meant. When it’s done, *Import complete* lists anything it skipped and offers to open the first journal it added.

**A Markdown folder** becomes a new journal named after the folder, with each file as a Note. Subfolders become journals of their own. Dates come from the front matter, the file name or the file itself; titles and tags are kept, and linked local files become attachments.

![The import confirmation on iPhone for a Dayfolio archive, listing its journals, the date range of its entries and what it adds to this iPhone.](import-archive-iphone.webp)

## Mirror to a folder on a Mac

The mirror folder keeps a Markdown copy of the journals you choose up to date in a folder you choose, such as a notes vault or a Git repository.

1. Open Settings › **Export** › Mirror to a folder.
2. Choose **Choose folder…** and pick the folder.
3. Tick the journals to mirror.

Dayfolio writes each entry as a Markdown file, in the same layout as a Markdown export, and keeps the files current while it runs: a changed entry is rewritten, a renamed one moved, and a deleted one removed. The status line under the folder says how it stands, such as “Up to date · 3 entries”.

- It’s one way. Changes you make to the files don’t come back into Dayfolio, and are replaced the next time the entry changes.
- Dayfolio touches only the files it wrote. Anything else in the folder is left alone.
- A journal you lock is never mirrored. Locking a mirrored journal removes its files from the folder.
- **Stop mirroring**, or unticking a journal, leaves the files where they are. They’re yours.

The mirrored files aren’t encrypted, like any export.

![Settings › Export on a Mac, mirroring Engineering Log and Northwind Client to a folder named Vault, up to date, with Career & Growth dimmed because it’s locked.](export-mirror-folder-mac.webp)

## What’s free

Exporting entries and journals, restoring an archive, importing Markdown and mirroring to a folder are all free, including for anything over the free version’s limits.

## Related

- [Sync and iCloud](../sync-and-icloud/)
- [Locked journals and privacy](../locked-journals/)
- [Getting started](../getting-started/)
- [The Dayfolio archive format](../../archive-format.html)

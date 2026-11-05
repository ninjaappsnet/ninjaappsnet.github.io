---
title: Import, export and backups
description: Export journals as Markdown or a Dayfolio archive, restore a backup, import a Markdown folder, and keep a live Markdown copy in a folder on your Mac.
slug: import-and-export
date: 2026-10-16
updated: 2026-11-05
order: 11
---
What you write in Dayfolio stays yours, in formats you can read anywhere. You can export a journal or everything as Markdown files, keep a complete backup you can restore on any device, bring in Markdown notes from elsewhere, and, on a Mac, keep a live Markdown copy of chosen journals in a folder of your own.

## Export

Start an export from:

- **On a Mac:** File › Export…, a journal’s settings › Export, or *Export…* in a journal’s menu in the sidebar.
- **On iPhone and iPad:** More › Export…, a journal’s settings › Export, or *Export…* in the journal menu at the top.

Start from what you want to do. The sheet offers three purposes:

- **Back up everything** makes a Dayfolio archive: a complete backup you can restore into Dayfolio on any device, with every journal and folder, its form and files, Recently deleted and your settings. From a journal, it reads *Back up this journal*.
- **Read or edit elsewhere** makes a Markdown folder: one text file per entry, with its pictures and files, readable in any notes or text app. It can’t be restored into Dayfolio as it is.
- **Share or print one entry** makes a PDF of the entry that’s open, to share or print. With none open, the sheet says how to open one.

File › Export… starts on *Back up everything*, and a journal’s own *Export…* starts on *Read or edit elsewhere*. **More options** holds what to export, one journal or all of them, and the format; choosing a format there changes the purpose to match.

Then choose where to save it. On iPhone and iPad, you pick a folder in Files and the export is written straight into it.

Exports aren’t encrypted, and the sheet says so under the purpose you chose, never tucked away under More options. If the export includes a journal you lock, Dayfolio asks for Face ID or Touch ID first.

### When it finishes

While it works, the sheet says what it’s doing, from the real work: “Reading your journals”, “Copying files 3 of 12”, “Checking the archive”. A bar appears only where it counts something, such as files, and nothing shows at all when the export is quick. When it’s done, the sheet stays open on what it made and where: “Exported 58 entries to Downloads › Dayfolio export 2026-11-04 0930”, or “Backed up 3 journals, 212 entries and 14 files to Documents › Dayfolio.dayfolio”. **Show in Finder** opens it on a Mac, and **Share…** sends it from an iPhone or iPad. If attachments were left out, they’re listed under the result. Choose **Done** to close the sheet.

If something fails, the sheet says “Couldn’t finish the export”, and why where it can, and “Nothing was left half-written, and your journals are unchanged.” Your choices are kept, and **Try again** asks where to save again. A single PDF, Markdown or Word file from an entry or a report ends in a message too, such as “Saved “Standup.pdf” in Downloads”, with *Show in Finder* or *Share…*, and a retry if it fails.

### What a Markdown export looks like

Each entry is a file named by its date, time and title, such as `2026-09-24 0912 Payments retry design.md`, in a folder per journal. The file starts with front matter holding the date, journal, the form’s name, tags, location and each field’s value, followed by the text fields as sections. Pictures and files are copied next to it and linked, so the folder opens well in Markdown editors and notes apps.

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



## Related

- [Sync and iCloud](../sync-and-icloud/)
- [Locked journals and privacy](../locked-journals/)
- [Getting started](../getting-started/)
- [The Dayfolio archive format](../../archive-format.html)

---
title: Quick capture
description: Write into Dayfolio without opening it: Mac quick entry with ⌥⌘J, notes from a terminal, drag and drop, answering a reminder, and the Share sheet.
slug: quick-capture
date: 2026-10-16
updated: 2026-11-05
order: 8
---
The best moment to write something down is the moment it happens, usually while you’re in another app. Dayfolio has several ways to capture a note without stopping what you’re doing. Each one makes an ordinary entry, and what you typed is never thrown away, even when it can’t be saved yet.

## Quick entry on a Mac

Press **⌥⌘J** anywhere, or click Dayfolio’s icon in the menu bar. A small window opens with the cursor already in the note.

1. Type your note. Add tags with **+ Tag**.
2. Quick entry opens on **Notes**, the journal that is always there. Choose another journal at the top if you want one, for that note only.
3. Press **⌘↩** to save. The window closes and the menu-bar icon shows a tick.

When you choose a journal other than Notes, the note is written with that journal’s form, the text going in its first long text field. A Fill line appears under the note: press Tab and type values, such as `energy 4, focus 2h, status on track`, and they’re saved with the note. If the journal’s form has nowhere for the note, it’s saved in Notes and quick entry says “Saved in Notes”. See [Journals, forms and fields](../templates-and-fields/).

Under the note, **Today so far** lists what you’ve written today, and a *What’s next* row suggests the entry you’re most likely to want, such as the journal a reminder just asked for. **Open Dayfolio** brings the main window forward.

![Quick entry on a Mac, opened from the menu bar with Daily Standup picked, a note typed and the Fill line reading “energy 4, focus time 1h30”, above Today so far.](capture-quick-entry-mac.webp)

A draft you close without saving is kept until you come back. You can change the shortcut, hide the menu-bar icon or open Dayfolio at login in Settings › General › Quick entry.


## Notes from a terminal or a script

On a Mac, a link can write a note without opening a window, so a terminal command or a git hook can log your work. Turn it on in Settings › General › Quick entry › **Write notes from links**. Dayfolio makes a key for your Mac and shows a line to add to your shell profile, with the key already in it. After that,

```sh
note Fixed the flaky CI job
```

writes the note into Notes while Dayfolio stays in the background. A link without your key writes nothing, and a link never writes into a journal you lock, Notes included. The full setup, including a git hook, is on the support page: [Writing notes from links](../../support.html#quick-note-link). In the app, it’s Help › *Writing notes from links*.

## Drop onto a journal

Drag text, a link, a picture or a file from another app onto a journal in the sidebar, on a Mac or on an iPad with the sidebar showing. Dayfolio adds it to that journal as a note dated now, and a message says “Added to Fernhill Client” with *Open* and *Undo*. Hold ⌥ as you drop on a Mac to open the New entry sheet with it waiting instead. Up to ten files go at once, each up to 50 MB.

## Reminders that take an answer

A reminder nudges you to write in a journal at the days and time you choose. To add one, open the journal’s settings, go to Reminders and choose **Add reminder**: pick the days, the time and, if you like, a message. Templates such as Daily standup and Billable day suggest a reminder, offered once, as a switch, when you make a journal from them in New journal. A reminder is skipped on a day you’ve already written in that journal.

When a reminder arrives, you can answer it without opening Dayfolio:

- **Write now** opens a new entry in the journal.
- **Reply** writes your answer as an entry.
- **Quick fields:** touch and hold the notification on iPhone and iPad, or use its arrow on a Mac, and fields from the journal’s form appear above Reply: its project as chips, a rating or mood as five dots, a choice such as a status as coloured chips, and a duration with −15m and +15m. Tap what applies and choose **Save**. The notification confirms where it went, such as “Saved to Engineering Log”.


Reply and quick fields ask for Face ID, Touch ID, your passcode or your Mac’s password first, and they’re offered only for journals you don’t lock; a locked journal’s reminder has *Write now* only. Settings › Reminders shows every reminder and has one switch to pause them all. To quiet some journals’ reminders during a Focus, see [Siri, Shortcuts, widgets, Control Center and Focus](../siri-shortcuts-and-widgets/).

## The Share sheet on iPhone and iPad

In any app’s share sheet, choose **Dayfolio**. The *Save to Dayfolio* sheet shows what you’re sharing, such as the text and the page’s link, and any files by name and size.

1. The sheet opens on Notes. Pick another journal if you like. Its form is used, the text going in its first long text field; if the form has nowhere for the text or the files, the entry is saved in Notes and the sheet says so.
2. Choose **Save**.

The entry is written without opening Dayfolio. A journal you lock is listed with a lock and is written to without being opened.


## Camera and scanner

On iPhone and iPad, an entry’s *Add attachment* menu can take a photo or a video with the camera, or scan a document into a PDF, straight into the entry. Nothing is saved to your Photos library. A photo records where it was taken only when its journal captures location.

## Siri, Shortcuts and widgets

You can also capture by voice with **Log in Dayfolio**, from a Home Screen widget or from Control Center. See [Siri, Shortcuts, widgets, Control Center and Focus](../siri-shortcuts-and-widgets/).


## Related

- [Journals, forms and fields](../templates-and-fields/)
- [Locked journals and privacy](../locked-journals/)
- [Getting started](../getting-started/)
- Templates with a suggested reminder: [Daily standup](../../templates/software-engineering/daily-standup/), [Billable day](../../templates/consulting-freelance/billable-day/), [Weekly review](../../templates/general/weekly-review/)

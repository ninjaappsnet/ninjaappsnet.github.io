---
title: Run a shortcut from a diagram
description: Make a click on a shape run one of your shortcuts in Play mode, such as starting a new Dayfolio entry or sending a message, and bring a shortcut’s answer back.
slug: run-a-shortcut-from-a-diagram
date: 2026-10-29
order: 7
---
Any graphic can run a shortcut from the Shortcuts app when you click it in Play mode. A diagram becomes a control panel: a box per journal that opens a new entry in it, or a button that sends today’s plan.

## Give a graphic the Action

1. Make the shortcut in the Shortcuts app first, and note its exact name.
2. In Diagrove, select the graphic that should run it.
3. In the inspector, open **Action** and set **On click** (on iPad, **On tap**) to **Run shortcut**.
4. Type the shortcut’s name in **Shortcut**, exactly as the Shortcuts app shows it.

The caption under it says “Runs the shortcut in the Shortcuts app.”

![A rounded rectangle labelled New entry selected, with the inspector’s Action section set to Run shortcut, the shortcut Larkspur entry typed in, and the caption Runs the shortcut in the Shortcuts app.](run-shortcut-action.webp "A Run shortcut Action with the shortcut’s name.")

## Run it

1. Click **Play** in the toolbar, or choose **View › Play** (Option-Command-P). On iPad, tap **Play**.
2. Click the graphic. The Shortcuts app runs the shortcut.
3. Press Esc, or click **Stop**, to go back to editing.

A Run shortcut Action runs only in Play mode, never while you edit.

## Use it with Dayfolio

Dayfolio offers its own actions in the Shortcuts app, such as New entry, Quick note and Log in Dayfolio. Make a shortcut that uses one, say New entry with the Larkspur journal chosen, name it “Larkspur entry”, and give a graphic a Run shortcut Action with that name. A click on the box then opens a new entry in that journal in Dayfolio. New entry and Quick note are Dayfolio’s actions on iPad and iPhone; on the Mac, Dayfolio offers Log in Dayfolio.

## Bring an answer back

A shortcut can also feed a diagram. Add a binding in the inspector’s **Data** section, set **From** to **Shortcut** and type the shortcut’s name. The shortcut runs each time Play mode starts and when you refresh live data, and what it stops with shows in the graphic: its words, a colour, whether it shows, or a progress bar. **Run now** in the binding runs it straight away.

![A note shape, Today’s focus, selected, with the inspector’s Data section showing a Text binding from the shortcut Today’s focus, Rule As it is, and Run now.](shortcut-binding.webp "A Text binding from a shortcut, with Run now.")

More in [Play mode and Actions](../../guide/play-mode-and-actions/) and [Bindings](../../guide/bindings/).

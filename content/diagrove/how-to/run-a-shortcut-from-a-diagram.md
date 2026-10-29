---
title: Run a shortcut from a diagram
description: Make a click on a shape run one of your shortcuts in Play mode, such as starting a timer in Dayfolio or sending a message, and bring a shortcut’s answer back.
slug: run-a-shortcut-from-a-diagram
date: 2026-10-29
order: 7
---
Any graphic can run a shortcut from the Shortcuts app when you click it in Play mode. A diagram becomes a control panel: a box per project that starts its timer, or a button that sends today’s plan.

## Give a graphic the Action

1. Make the shortcut in the Shortcuts app first, and note its exact name.
2. In Diagrove, select the graphic that should run it.
3. In the inspector, open **Action** and set **On click** (on iPad, **On tap**) to **Run shortcut**.
4. Type the shortcut’s name in **Shortcut**, exactly as the Shortcuts app shows it.

The caption under it says “Runs the shortcut in the Shortcuts app.”

[shot: run-shortcut-action] Mac, light. A rounded rectangle labelled “Start timer” selected, with the Action section set to Run shortcut and the shortcut’s name typed in. Point to the Shortcut field.

## Run it

1. Click **Play** in the toolbar, or choose **View › Play** (Option-Command-P). On iPad, tap **Play**.
2. Click the graphic. The Shortcuts app runs the shortcut.
3. Press Esc, or click **Stop**, to go back to editing.

Shortcuts only run in Play mode, never while you edit.

## Use it with Dayfolio

Dayfolio offers its own actions in the Shortcuts app, such as New entry and Start timer. Make a shortcut that uses one, name it, say “Start Larkspur timer”, and give a graphic a Run shortcut Action with that name. A click on the box then starts the timer in Dayfolio.

## Bring an answer back

A shortcut can also feed a diagram. Add a binding in the inspector’s **Data** section, set **From** to **Shortcut** and type the shortcut’s name. The shortcut runs each time Play mode starts and when you refresh live data, and what it stops with shows in the graphic: its words, a colour, whether it shows, or a progress bar. **Run now** in the binding runs it straight away.

[shot: shortcut-binding] Mac, light. A note shape selected with a Text binding from a Shortcut, and its Run now button. Point to Run now.

More in [Play mode and Actions](../../guide/play-mode-and-actions/) and [Bindings](../../guide/bindings/).

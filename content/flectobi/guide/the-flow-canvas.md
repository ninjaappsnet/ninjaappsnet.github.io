---
title: The Flow canvas
description: Add Steps, connect them, move and rename them, zoom and select several at once. The palette, the context menus and the keyboard shortcuts.
slug: the-flow-canvas
date: 2026-10-26
order: 5
---
The Flow canvas is where you build your recipe. Each box is a Step. Lines between them are Connections that carry a Dataset from one Step to the next. This page covers everything you can do on the canvas, with the mouse and the keyboard.

## Three kinds of Step

- An **Input** reads data. It has an output port and no input port.
- A **Transform** changes data. There are 26, in five groups: Rows, Columns, Text, Combine and Reshape.
- An **Output** writes a file. It takes one Connection.

A Step shows its state: Ready, Failed, Waiting, Queued or Running. A Step with a problem tells you what to fix in the preview and inspector.

## Add a Step

There are several ways. Use the one that suits you.

- Click **Add Transform** in the toolbar and choose from the five groups. The new Step is connected after the Step you selected.
- Double-click empty canvas to open the palette, a search box titled “Search transforms”.
- Select a Step and start typing a letter. The palette opens with that letter already typed.
- Right-click a Step and choose **Add Transform After**. Choose **Insert Transform Between** to put one in the middle of a Connection.
- Right-click a wire and choose **Insert Transform on Connection**.

![The Transform palette open on the Flow canvas with a search typed and matching Transforms listed.](flow-palette.webp "The palette finds a Transform by name, by its first letters or by a common word.")

## Use the palette

Type part of a name, or a word you know from elsewhere. “where” finds **Filter**. “vlookup” finds **Join**. “group by” finds **Summary**. Letters in order work too: “rmdup” finds **Remove Duplicates**.

Press **Up** and **Down** to choose, **Return** to add, and **Esc** to close.

## Connect Steps

- Drag from a Step’s output port to another Step’s input port, or drop on the Step itself.
- With a Step selected, press **Control-Return** to open the **Connect Output To** menu. This works without a mouse.
- Click a wire to select it. Press **Delete** to remove it, or right-click and choose **Delete Connection**.

A **Join** takes exactly two Connections. A **Stack** takes at least two. Every other Transform takes one.

## Select, move and rename

- Click a Step to select it. **Command-click** or **Shift-click** adds to the selection.
- Drag across empty space to select everything inside the box.
- Press **Command-A** to select all, and **Esc** to clear the selection.
- Drag a Step to move it. It snaps to a 10 point grid. The arrow keys nudge a selected Step, and **Shift** moves it further.
- Press **Return** on a selected Step to rename it, as in Finder.
- Press **Command-D** to duplicate the selected Steps. Copies get numbered names, such as Sales 2.
- Press **Delete** to remove them. **Undo** brings them back.

Right-click empty canvas and choose **Auto Layout** to tidy the whole Flow.

Every Step has a **Note** field in the inspector, with the prompt “Describe what this step is for”. A line of explanation helps the next person, and helps you in three months.

## Zoom

Use the zoom control, or pinch on a trackpad. The range is 25% to 200%.

- **Command-=** zooms in. **Command--** zooms out.
- **Command-0** returns to actual size.
- **Zoom to Fit** shows the whole Flow.

Below 60%, Steps shrink to an icon and a name, so a long Flow stays readable. A long Flow opens zoomed out.

## Step through a Flow

Click a Step to see its result in the preview below and its options in the inspector. Select each Step from left to right and you see the data change.

![The Flow canvas as each Step is selected in turn, with the preview grid and inspector changing.](clip-steps.mp4 "Select one Step after another to watch the data change.")

**Tab** selects the next Step from left to right. **Shift-Tab** selects the previous one. To drag the divider between the canvas and the preview, use the mouse, or the up and down arrows when it has focus.

## Context menus

Right-click a Step for **Add Transform After**, **Find Transform…**, **Insert Transform Between**, **Add Output…**, **Connect Output To**, **Refresh**, **Write Now**, **Show in Inspector**, **Rename**, **Duplicate** and **Delete**. Refresh applies to Inputs and Write Now to Outputs.

Right-click empty canvas for **Add Input Files…**, **New PostgreSQL Input…**, **New MySQL Input…**, **Add Transform**, **Find Transform…**, **Auto Layout**, **Zoom to Fit** and **Select All**.

## Stop and refresh

Press **Command-R** to read every Input again. Press **Command-.** to stop a running Step. A stopped Step stays stopped until you change or refresh it.

> **Tip:** If a Step fails, click it. The preview says which Step has the problem and why. Fix that Step and the ones after it run again.

## VoiceOver

Steps support VoiceOver actions: **Show Inspector**, **Rename**, **Connect Output To…** and **Delete**.

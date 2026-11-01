---
title: The command-line tool
description: Install the diagrove command-line tool, make, check, render and change documents from Terminal, and connect its MCP server to an AI assistant.
slug: command-line-tool
date: 2026-10-29
order: 11
---
`diagrove` is a command-line tool for the Mac that makes, reads, checks, changes and draws Diagrove documents without opening the app. It’s built for scripts and for AI assistants: every command answers in JSON, and `diagrove mcp` serves the same commands to any assistant that speaks the Model Context Protocol. This page covers installing it, its commands, and working with a document open in the app.

## Install it

The tool is free, notarized by Apple and separate from the app. In the app, **Help › Command-line tool…** shows the same steps, with a link to the download. Install it with Homebrew:

```sh
brew install ninjaappsnet/diagrove/diagrove
```

Or download the latest release from [github.com/ninjaappsnet/homebrew-diagrove](https://github.com/ninjaappsnet/homebrew-diagrove/releases/latest) (for 1.0.0, `diagrove-1.0.0-macos.zip`). The zip holds `diagrove`, the `.bundle` folders it reads from beside itself, and `LICENSES.txt`. Keep them together in one folder and link `diagrove` onto your `PATH`, rather than copying the tool alone, which breaks it. For example, with the files unzipped into `~/.local/lib/diagrove`:

```sh
sudo ln -sf ~/.local/lib/diagrove/diagrove /usr/local/bin/diagrove
```

Check that it works:

```sh
diagrove --version
diagrove --help
```

`diagrove --version` answers `1.0.0`. The tool needs macOS 26 or later and runs on Apple silicon and Intel Macs; it doesn’t run on iPad. The app works fully without it. `diagrove --licenses` prints the notices of the open-source software in it.

## How it answers

Every command writes one JSON object on standard output: `{"ok": true, …}`, or `{"ok": false, "errors": […]}` with a `code`, a `message`, where the problem is and a `hint` that names the fix. A sentence for people goes to standard error, and a failure exits with a non-zero status. Add `--pretty` to indent the JSON, or `--quiet` to leave out the sentence. `diagrove --help`, and `--help` after any command, says what it takes.

## The commands

| Command | What it does |
|---|---|
| `diagrove new -o Plan.diagrove` | Makes a document: empty, from Diagrove text with `--text plan.gtext`, or from a template with `--template kanban` (add `--paper dark` for Ink paper). |
| `diagrove text Plan.diagrove` | Writes a document as Diagrove text, and lists anything that couldn’t come across. |
| `diagrove validate plan.gtext` | Checks a `.diagrove` or `.gtext` file and reports each problem and where it is: in Diagrove text, its line and column. |
| `diagrove check Plan.diagrove` | Finds what makes a diagram hard to read: overlaps, words that don’t fit, weak contrast, lines through shapes. `--fix` applies the safe fixes. |
| `diagrove render Plan.diagrove -o plan.png` | Draws a canvas as PNG, PDF or SVG, exactly as the app exports it. `--live-data` draws bindings with the document’s variables and JSON files. |
| `diagrove apply Plan.diagrove edits.json` | Applies a list of changes (Ops), all at once or not at all. `--dry-run` shows what would change. |
| `diagrove inspect Plan.diagrove` | Describes the structure: canvases, layers, and each graphic’s ID, kind, words and position. |
| `diagrove layout Plan.diagrove` | Arranges connected graphics as the app’s Tidy does, with `--style layered` or `tree` and `--direction down` or `right`. |
| `diagrove templates list` | Lists the app’s 63 templates and its two blank documents. `diagrove templates show flowchart` answers one as Diagrove text to adapt. |
| `diagrove stencils search database` | Finds built-in stencils by name or keyword, with the IDs Diagrove text uses. |
| `diagrove import mermaid chart.mmd -o Chart.diagrove` | Makes a document from a Mermaid flowchart. |
| `diagrove schema ops` | Describes the Ops, Diagrove text (`schema text`) or any command’s input and output. |

`apply`, `layout` and `check --fix` write back to the file you give them unless you add `-o` with another file.

## Diagrove text in brief

Diagrove text writes a whole document in a few lines. Files end in `.gtext`.

```text
cart: "Cart" { shape: rounded; fill: light-teal }
pay: "Paid?" { shape: diamond; fill: light-amber }
receipt: "Send receipt"
retry: "Try again" { fill: light-orange }
cart -> pay
pay -> receipt: "Yes"
pay -> retry: "No" { dash: dashed }
```

- `key: "Label" { … }` is a shape. The key is its ID.
- `a -> b` is a line with an arrow at `b`, and `: "Yes"` labels it.
- Shapes without a position are laid out for you, top to bottom, or left to right with `direction: right` at the top.
- For more than one canvas, put each canvas’s lines in a `canvas "Home" { … }` block; then every shape goes in one. `on-click: go "Home"` gives a shape an action.

Build it with `diagrove new --text checkout.gtext -o Checkout.diagrove`, then `check` it and `render` it to look at the result. `diagrove schema text` lists every attribute.

## Ops

Ops change a document you already have, by graphic ID, so everything else stays exactly as it was. They’re JSON:

```json
{"ops": [
  {"op": "add-shape", "id": "refund", "text": "Refund", "at": [40, 480]},
  {"op": "add-line", "from": "pay", "to": "refund", "label": "Disputed"},
  {"op": "update", "id": "receipt", "set": {"text": "Email receipt"}}
]}
```

`diagrove inspect` lists the IDs. If one Op fails, nothing changes and the answer names the Op that failed.

## Work on a document open in the app

Add `--live` to `text`, `inspect`, `apply` or `render`, and the command acts on a document open in Diagrove instead of a file: the front one, or the one you name with `--document`.

```sh
diagrove apply --live edits.json --document "Checkout"
```

Changes made with `apply --live` land in the window as one undo step, so **Edit › Undo** takes them back. They’re refused while the document is playing.

The first time, macOS asks whether your terminal app may control Diagrove. If you said no, turn it on in **System Settings › Privacy & Security › Automation**. Diagrove has to be running; the tool says so when it isn’t.

[shot: live-apply-mac] The Mac, light appearance: Terminal beside a Diagrove window with the Flowchart template, after `diagrove apply --live` added a shape; the new shape selected on the canvas and the JSON answer in Terminal.

## Connect an AI assistant

`diagrove mcp` is an MCP server over standard input and output. An assistant starts the command `diagrove` with the argument `mcp`. In a client that takes a JSON configuration, add:

```json
{"mcpServers": {"diagrove": {"command": "diagrove", "args": ["mcp"]}}}
```

In Claude Code:

```sh
claude mcp add diagrove -- diagrove mcp
```

The assistant then has the commands as tools, such as `create`, `apply`, `check`, `render` (which hands back the picture so it can look), `templates` and `search_stencils`, and a `read_me` tool with the guide to Diagrove text that it reads first.

For Claude Code there’s also a skill that teaches it the whole loop of writing, checking, rendering and fixing a diagram:

```sh
diagrove skill install
```

It goes in `~/.claude/skills/diagrove`, or in the folder you give with `--path`.

[shot: render-result-mac] The Mac, dark appearance: Terminal after `diagrove render Checkout.diagrove -o look.png`, with the JSON answer, beside the PNG open in Preview showing the checkout flow on White paper.

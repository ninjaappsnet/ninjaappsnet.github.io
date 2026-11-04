---
title: Diagrams with an AI assistant
description: Install the diagrove tool, connect it to an AI assistant over MCP, have it draw a diagram, check and render it, then edit it live in the app.
slug: diagrams-with-an-ai-assistant
date: 2026-10-29
order: 5
---
The `diagrove` command-line tool makes, checks, renders and changes Diagrove Documents without the app, and `diagrove mcp` offers the same commands to an AI assistant. In this tutorial you install it, connect it to an assistant, ask for a diagram, check what came back, open it in Diagrove and change it while it’s open. The tool is for the Mac, and the app works fully without it.

## 1. Install the tool

The tool is a free, notarized download, outside the App Store. With Homebrew, run this in Terminal:

```sh
brew install ninjaappsnet/diagrove/diagrove
```

Without Homebrew, download the zip from [the latest release](https://github.com/ninjaappsnet/homebrew-diagrove/releases/latest), keep its files together in one folder, and link `diagrove` onto your `PATH`, as the [command-line tool’s page](../../guide/command-line-tool/) shows. It needs macOS 26 or later. Then check that it runs:

```sh
diagrove templates list
```

It answers in JSON, listing the same templates the app’s gallery has.

[shot: install] Mac, dark appearance. Terminal after `brew install ninjaappsnet/diagrove/diagrove` and `diagrove templates list`, showing the start of the JSON answer.

## 2. Connect it to your assistant

`diagrove mcp` is an MCP server that talks over standard input and output. An assistant that supports MCP starts it as the command `diagrove` with the argument `mcp`. Many read a settings file in this shape:

```json
{"mcpServers": {"diagrove": {"command": "diagrove", "args": ["mcp"]}}}
```

Add it where your assistant keeps its MCP servers, then restart the assistant. Its tools include `read_me`, `create`, `check`, `render`, `inspect`, `apply`, `layout`, `templates` and `search_stencils`.

If your assistant is Claude Code, also run:

```sh
diagrove skill install
```

This puts Diagrove’s skill in `~/.claude/skills/diagrove`, where Claude Code finds it (use `--path` for another folder): how to write Diagrove text, the Ops that change a Document, and the habit of rendering and looking before calling a diagram done.

## 3. Ask for a diagram

Ask in plain words, and say where to save it. For example:

> Draw a checkout flowchart as Checkout.diagrove in my Documents folder: Cart, Pay, a Paid? decision, Send receipt on Yes, and a No path back to Pay.

The assistant reads Diagrove’s guide, writes the diagram as Diagrove text, creates the Document, checks it, and renders a picture to look at. If the check finds words that don’t fit or shapes that overlap, it fixes them and looks again.

[shot: assistant-answer] Mac, light. An AI assistant’s window after the request, showing the rendered checkout flowchart the `render` tool returned. Point to the picture.

## 4. Check and render it yourself

You can run the same checks in Terminal:

```sh
cd ~/Documents
diagrove check Checkout.diagrove
diagrove render Checkout.diagrove -o Checkout.png
```

`check` answers in JSON with a list of issues, each naming its graphics and often a fix; `diagrove check Checkout.diagrove --fix` applies the safe ones (alignment, gaps and contrast). `render` draws the first canvas as a PNG, or as a PDF or SVG when the `-o` name ends in `.pdf` or `.svg`.

## 5. Open it in the app

The Document is an ordinary `.diagrove` file. Double-click it in the Finder, or run:

```sh
open Checkout.diagrove
```

Everything in it can be edited by hand, played and exported like any Diagrove Document.

![Checkout open in Diagrove: the flowchart the assistant drew, Cart, Pay, a Paid? decision with Yes to Send receipt and No back to Pay, with Paid? selected and the inspector showing its fill.](open-in-app.webp "The assistant’s Checkout, open in Diagrove.")

## 6. Edit it live

With the Document open in Diagrove, add `--live` and the tool works on the open window instead of the file:

```sh
diagrove inspect --live
```

The answer lists every graphic with its ID. Write the change as Ops in a file, `edits.json`, naming graphics by those IDs. Here `pay` stands for the ID `inspect` gave the Pay box:

```json
{"ops": [
  {"op": "update", "id": "pay", "set": {"fill": "light-amber"}}
]}
```

Try it first, then apply it:

```sh
diagrove apply --live --dry-run edits.json
diagrove apply --live edits.json
```

The first time, macOS asks whether Terminal may control Diagrove; you can change the answer later in **System Settings › Privacy & Security › Automation**. The change appears in the window at once, as one step: Command-Z undoes it. `--live` works with `apply`, `inspect`, `text` and `render`, and acts on the front Document unless `--document` names another. A live `apply` is refused while the Document is playing.

The MCP tools work on files. An assistant that can run commands in Terminal, with the skill installed, can use `--live` the same way to change what you have open.

![Checkout open in Diagrove just after diagrove apply --live edits.json, with the Pay box now light amber and the title bar saying Edited.](live-edit.webp "After diagrove apply --live, Pay is light amber in the open window.")

## Where to go next

- [The command-line tool](../../guide/command-line-tool/): every command and what it answers.
- [Templates](../../guide/templates/): `diagrove new --template` starts from the same templates as the app.
- [Your first flowchart](../first-flowchart/): the same flowchart drawn by hand.

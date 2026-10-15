#!/usr/bin/env python3
"""Regenerate apps/dayfolio/archive-format.html from the Dayfolio repo's
docs/dayfolio-archive-format.md.

    python3 tools/archive-page.py /path/to/dayfolio/docs/dayfolio-archive-format.md

The Markdown file is the source of truth: the Dayfolio repo checks it against
the code (ArchiveFormatDocTests), so edit it there and run this, never the
generated page. Standard library only, like the rest of this site. The page's
header, footer and head are taken from apps/dayfolio/index.html, so a change to
the site's chrome carries over the next time this runs.

It handles exactly what that document uses: headings, paragraphs, bullet and
numbered lists (one nested level), pipe tables, fenced code, `code`, **bold**,
*italic*, [links](url) and <autolinks>. A link to a file that only exists in the
Dayfolio repo (a relative path) is kept as plain text, since it would be dead
here. Anything else it meets makes it stop rather than guess.
"""

from __future__ import annotations

import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "apps" / "dayfolio" / "archive-format.html"
SOURCE_PAGE = ROOT / "apps" / "dayfolio" / "index.html"
URL = "https://ninjaapps.net/apps/dayfolio/archive-format.html"
TITLE = "The Dayfolio archive format — Dayfolio — NinjaApps"
DESCRIPTION = ("The .dayfolio file format, in full: the container, every record type and key, "
               "the versions, and what a restore does, precisely enough to write a reader.")


def slug(text: str, seen: dict[str, int]) -> str:
    base = re.sub(r"[^a-z0-9]+", "-", re.sub(r"`", "", text).lower()).strip("-") or "section"
    seen[base] = seen.get(base, 0) + 1
    return base if seen[base] == 1 else f"{base}-{seen[base]}"


def inline(text: str) -> str:
    """Markdown inline spans to HTML. Code spans are lifted out first so nothing inside them is touched."""
    codes: list[str] = []

    def lift(m: re.Match) -> str:
        codes.append(f"<code>{html.escape(m.group(1), quote=False)}</code>")
        return f"\x00{len(codes) - 1}\x00"

    text = re.sub(r"`([^`]+)`", lift, text)
    text = html.escape(text, quote=False)
    text = re.sub(r"&lt;(https?://[^\s&]+)&gt;", r'<a href="\1">\1</a>', text)

    def link(m: re.Match) -> str:
        label, url = m.group(1), m.group(2)
        if re.match(r"https?://", url):
            return f'<a href="{url}">{label}</a>'
        return label  # a path inside the Dayfolio repo: dead here, so plain text

    text = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", link, text)
    text = re.sub(r"\*\*(?=\S)(.+?)(?<=\S)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<![\*\w])\*(?=\S)([^*]+?)(?<=\S)\*(?![\*\w])", r"<em>\1</em>", text)
    return re.sub(r"\x00(\d+)\x00", lambda m: codes[int(m.group(1))], text)


def split_row(line: str) -> list[str]:
    cells = re.split(r"(?<!\\)\|", line.strip())[1:-1]
    return [c.strip().replace("\\|", "|") for c in cells]


def convert(md: str) -> str:
    lines = md.splitlines()
    out: list[str] = []
    seen: dict[str, int] = {}
    i, first_h1 = 0, True
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
        elif line.startswith("```"):
            j = i + 1
            while not lines[j].startswith("```"):
                j += 1
            out.append("<pre><code>" + html.escape("\n".join(lines[i + 1:j]), quote=False) + "</code></pre>")
            i = j + 1
        elif re.match(r"#{1,6} ", line):
            level = len(line) - len(line.lstrip("#"))
            text = line[level:].strip()
            if level == 1 and first_h1:
                first_h1 = False  # the page's own heading stands in for it
            else:
                out.append(f'<h{level} id="{slug(text, seen)}">{inline(text)}</h{level}>')
            i += 1
        elif line.startswith("|"):
            j = i
            while j < len(lines) and lines[j].startswith("|"):
                j += 1
            head, sep, body = lines[i], lines[i + 1], lines[i + 2:j]
            assert re.fullmatch(r"\|(?:\s*:?-+:?\s*\|)+", sep.strip()), f"not a table separator: {sep}"
            rows = "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in split_row(r)) + "</tr>" for r in body)
            heads = "".join(f"<th>{inline(c)}</th>" for c in split_row(head))
            out.append(f'<div class="table-wrap"><table><thead><tr>{heads}</tr></thead><tbody>{rows}</tbody></table></div>')
            i = j
        elif re.match(r"\s*(?:[-*] |\d+\. )", line):
            items: list[tuple[int, str, str]] = []
            while i < len(lines) and lines[i].strip():
                m = re.match(r"(\s*)([-*]|\d+\.) (.*)", lines[i])
                if m:
                    items.append((len(m.group(1)), "ol" if m.group(2)[0].isdigit() else "ul", m.group(3)))
                elif lines[i].startswith("  ") and items:  # a continuation line of the last item
                    depth, kind, text = items[-1]
                    items[-1] = (depth, kind, text + " " + lines[i].strip())
                else:
                    break
                i += 1
            out.append(render_list(items))
        else:
            para = [line.strip()]
            i += 1
            while i < len(lines) and lines[i].strip() and not re.match(r"(```|#{1,6} |\||\s*(?:[-*] |\d+\. ))", lines[i]):
                para.append(lines[i].strip())
                i += 1
            out.append(f"<p>{inline(' '.join(para))}</p>")
    return "\n\n".join(out)


def render_list(items: list[tuple[int, str, str]]) -> str:
    base = min(d for d, _, _ in items)
    html_out, stack = "", []  # stack of (depth, kind)
    for depth, kind, text in items:
        while stack and depth < stack[-1][0]:
            html_out += f"</li></{stack.pop()[1]}>"
        if stack and depth == stack[-1][0]:
            html_out += "</li>"
        elif not stack or depth > stack[-1][0]:
            assert depth == base or stack, "list nesting this tool does not read"
            html_out += f"<{kind}>"
            stack.append((depth, kind))
        html_out += f"<li>{inline(text)}"
    while stack:
        html_out += f"</li></{stack.pop()[1]}>"
    return html_out


def build(md: str) -> str:
    src = SOURCE_PAGE.read_text(encoding="utf-8")
    header = re.search(r"<header>.*?</header>", src, re.S).group(0)
    footer = re.search(r"<footer>.*?</footer>", src, re.S).group(0)
    tail = re.search(r'(<link rel="icon".*?)</head>', src, re.S).group(1)
    title, desc = html.escape(TITLE, quote=True), html.escape(DESCRIPTION, quote=True)
    return f"""<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{URL}">
<meta property="og:site_name" content="NinjaApps">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{URL}">
{tail}</head>
<body>

{header}

<main>

<section class="page">
  <div class="kicker">式 FORMAT — DAYFOLIO</div>
  <h1 class="page-title">The Dayfolio archive format</h1>
  <div class="prose">

{convert(md)}

  </div>
  <a class="backlink" href="support.html#archive">← BACK TO SUPPORT</a>
</section>

</main>

{footer}

</body>
</html>
"""


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    PAGE.write_text(build(Path(sys.argv[1]).read_text(encoding="utf-8")), encoding="utf-8")
    print(f"wrote {PAGE.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

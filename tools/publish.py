#!/usr/bin/env python3
"""The files the deploy publishes, and nothing else. Standard library only:

    python3 tools/publish.py _site

Every page goes live (every .html outside the templates and the brand sources), and
so does every file a page uses: what its href, src, srcset, poster or meta content
names, what the stylesheet's url() names, and so on, followed through the
stylesheet and the scripts. Some addresses are fetched from outside the site, so
they go live though no page names them (ALWAYS, ALWAYS_UNDER, and the files among
check-site.py's BAKED_IN_URLS). Anything else, the repo's notes, the Markdown
sources, the templates and files nothing uses any more, stays off the site.

The deploy (.github/workflows/pages.yml) runs this after the build and the
checks, into an empty folder, and publishes that folder.
"""

from __future__ import annotations

import importlib.util
import posixpath
import re
import shutil
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse


def load(name: str, file: str):
    """Another tool in this folder, as a module."""
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(file))
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
    return sys.modules[name]


check = load("check_site", "check-site.py")

# Never published, whatever names them.
NEVER = {".git", ".github", "tools", "_site", "__pycache__"}
# Fetched by crawlers and by iOS, not linked from a page.
ALWAYS = ["robots.txt", "sitemap.xml", ".well-known/apple-app-site-association"]
# Fetched by link from outside the site: the files social media posts point at, and
# the brand images (logos, avatars, banners) kept reachable for press and profiles.
ALWAYS_UNDER = [("games/smalti/social/", ""), ("assets/brand/", ".png"), ("assets/brand/", ".svg")]
# Files whose text can name other files.
FOLLOWED = (".html", ".css", ".js", ".xml")

REFERENCE = re.compile(
    r'(?:href|src|poster|content)\s*=\s*"([^"]+)"'   # a page's links, pictures, films and meta
    r'|srcset\s*=\s*"([^"]+)"'                        # a picture's candidates
    r"""|url\(\s*['"]?([^'")]+)['"]?\s*\)"""         # the stylesheet's
    r"|<loc>([^<]+)</loc>")                           # the sitemap's


def site_files(root: Path) -> set:
    return {path.relative_to(root).as_posix() for path in root.rglob("*")
            if path.is_file() and not NEVER.intersection(path.relative_to(root).parts)}


def is_page(rel: str) -> bool:
    return rel.endswith(".html") and not any(rel.startswith(d + "/") for d in check.EXEMPT_DIRS)


def resolve(base: str, ref: str, files: set):
    """The file `ref`, as written in `base`, names on this site, or None."""
    url = urlparse(ref.strip())
    if url.scheme in ("http", "https"):
        if url.netloc != urlparse(check.ORIGIN).netloc:
            return None
    elif url.scheme or url.netloc:
        return None  # mailto:, data:, tel:, another site
    path = unquote(url.path)
    if not path:
        return None  # a same-page anchor
    if url.netloc or path.startswith("/"):
        target = path.lstrip("/")
    else:
        target = posixpath.normpath(posixpath.join(posixpath.dirname(base), path))
    if target in ("", "."):
        return "index.html"
    if target.rstrip("/") + "/index.html" in files:
        return target.rstrip("/") + "/index.html"
    return target if target in files else None


def references(rel: str, text: str) -> list:
    found = []
    for match in REFERENCE.finditer(text):
        if match.group(2):
            found += [candidate.split()[0] for candidate in match.group(2).split(",") if candidate.strip()]
        else:
            found.append(next(group for group in match.groups() if group))
    return found


def published_files(root: Path) -> set:
    files = site_files(root)
    baked = [urlparse(url).path.lstrip("/") for url in check.BAKED_IN_URLS]
    queue = [rel for rel in files if is_page(rel)]
    queue += [rel for rel in ALWAYS + baked if rel in files]
    queue += [rel for rel in files for prefix, suffix in ALWAYS_UNDER
              if rel.startswith(prefix) and rel.endswith(suffix)]
    published = set()
    while queue:
        rel = queue.pop()
        if rel in published:
            continue
        published.add(rel)
        if rel.endswith(FOLLOWED):
            text = (root / rel).read_text(encoding="utf-8", errors="replace")
            for ref in references(rel, text):
                target = resolve(rel, ref, files)
                if target and target not in published:
                    queue.append(target)
    return published


def copy(root: Path, dest: Path) -> list:
    published = sorted(published_files(root))
    for rel in published:
        (dest / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(root / rel, dest / rel)
    return published


def main(argv=None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1:
        print(__doc__)
        return 2
    dest = Path(args[0])
    if dest.exists() and any(dest.iterdir()):
        print(f"FAIL — {dest} is not empty")
        return 1
    root = check.ROOT
    published = copy(root, dest)
    print(f"OK — {len(published)} of {len(site_files(root))} files published to {dest}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

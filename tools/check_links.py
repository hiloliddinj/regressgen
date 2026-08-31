"""Verify every internal markdown link and anchor resolves.

Run before submitting. A dead link in a judged repository reads as carelessness,
and section anchors drift whenever a heading is renumbered.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LINK = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")
# Trajectories embed generated test source, and a regex like
# `[a-z0-9]([a-z0-9-](?!--)` parses as a markdown link. Strip fenced blocks
# and inline code before looking for links.
FENCE = re.compile(r"```.*?```", re.DOTALL)
INLINE_CODE = re.compile(r"`[^`\n]*`")
SKIP_DIRS = {".venv", ".work", "cases", "cases_excluded", "node_modules", ".git"}


def anchors(md: Path) -> set[str]:
    out = set()
    for line in md.read_text().splitlines():
        if line.startswith("#"):
            t = re.sub(r"[^\w\s-]", "", line.lstrip("#").strip().lower())
            out.add(re.sub(r"\s+", "-", t))
    return out


def main() -> int:
    bad = 0
    for md in sorted(ROOT.rglob("*.md")):
        if SKIP_DIRS & set(md.parts):
            continue
        body = INLINE_CODE.sub(" ", FENCE.sub(" ", md.read_text()))
        for text, href in LINK.findall(body):
            if href.startswith(("http://", "https://", "mailto:")):
                continue
            path_part, _, frag = href.partition("#")
            target = (md.parent / path_part).resolve() if path_part else md.resolve()
            rel = md.relative_to(ROOT)
            if not target.exists():
                print(f"MISSING FILE    {rel}: [{text[:34]}]({href})")
                bad += 1
            elif frag and target.suffix == ".md" and frag not in anchors(target):
                print(f"MISSING ANCHOR  {rel}: [{text[:34]}]({href})")
                bad += 1
    print(f"\n{bad} broken link(s)" if bad else "\nall internal links resolve")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())

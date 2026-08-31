"""Inject generated result tables into README.md and docs/CORPUS.md.

Numbers in the documentation are never typed by hand: they are regenerated from
`results/` and `cases/`, so a claim in the prose cannot drift from its evidence.

    uv run python tools/update_readme.py
"""

from __future__ import annotations

import re
import sys
from collections import Counter
from itertools import pairwise
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from regressgen.corpus import load_cases  # noqa: E402
from regressgen.report import (  # noqa: E402
    SYSTEMS,
    _agg,
    load,
    mcnemar,
    per_case,
    scoreboard,
    stability,
    verdict_breakdown,
)

# The system we ship: matches v5 and v6 on score at a fraction of the cost.
SHIPPED = "v4-discipline"


def headline() -> str:
    """The three numbers a skimming reader should leave with.

    Means over all stored runs, matching the scoreboard — not the latest run.
    """
    b, f = _agg("baseline"), _agg(SHIPPED)
    if not b or not f:
        return "_no results yet — run `make headline`_"
    pairs = min(b["runs"], f["runs"])
    runs = f"mean of {pairs} runs each" if pairs > 1 else "single run each"
    verdict = mcnemar("baseline", SHIPPED)
    p = verdict.split("p = ")[-1].split(" ")[0] if "p = " in verdict else "?"
    return (
        "| | baseline | shipped agent |\n|---|---|---|\n"
        f"| regression tests that actually reproduce the bug "
        f"| {b['rate'] * 100:.0f}% | **{f['rate'] * 100:.0f}%** |\n"
        f"| tests that silently pass on broken code "
        f"| {b['silent']:.1f} | **{f['silent']:.1f}** |\n"
        f"| cost per test | ${b['usd']:.2f} | ${f['usd']:.2f} |\n"
        f"\n{b['n']} real bugs from 7 upstream libraries, {runs}. "
        f"Paired exact McNemar: p = {p}."
    )


def significance() -> str:
    have = [s for s in SYSTEMS if load(s)]
    if len(have) < 2:
        return "_not enough systems run yet_"
    lines = [f"- **Headline** — {mcnemar('baseline', SHIPPED)}", ""]
    lines += [f"- {mcnemar(a, b)}" for a, b in pairwise(have)]
    return "\n".join(lines)


def corpus_summary() -> str:
    cases = load_cases()
    by = Counter(c.meta["repo"] for c in cases)
    libs = ", ".join(r for r, _ in by.most_common())
    return (f"**{len(cases)} cases**, each a real bug fixed by a real maintainer "
            f"in a real library, drawn from {len(by)} upstream projects "
            f"({libs}).")


def corpus_repos() -> str:
    cases = load_cases()
    by = Counter(c.meta["repo"] for c in cases)
    lic = {c.meta["repo"]: c.meta.get("license", "?") for c in cases}
    url = {c.meta["repo"]: c.meta.get("upstream", "") for c in cases}
    rows = ["| Library | Cases | Upstream | Licence |", "|---|---:|---|---|"]
    for r, n in sorted(by.items()):
        u = url[r].removeprefix("https://").removesuffix(".git")
        rows.append(f"| {r} | {n} | {u} | {lic[r]} |")
    rows.append(f"| **total** | **{len(cases)}** | | |")
    return "\n".join(rows)


def corpus_cases() -> str:
    rows = ["| Case | Fix commit subject | Src churn |", "|---|---|---:|"]
    for c in load_cases():
        subj = c.meta["subject"].replace("|", "\\|")[:74]
        rows.append(f"| `{c.id}` | {subj} | {c.meta.get('src_churn', '?')} |")
    return "\n".join(rows)


README_BLOCKS = {
    "headline": headline,
    "scoreboard": scoreboard,
    "verdicts": verdict_breakdown,
    "stability": stability,
    "percase": per_case,
    "significance": significance,
    "corpussummary": corpus_summary,
}
CORPUS_BLOCKS = {"repos": corpus_repos, "cases": corpus_cases}


def inject(path: Path, blocks: dict) -> None:
    s = path.read_text()
    for name, fn in blocks.items():
        pat = re.compile(rf"(<!-- BEGIN:{name} -->\n).*?(\n<!-- END:{name} -->)",
                         re.DOTALL)
        if not pat.search(s):
            print(f"  ! no marker for {name} in {path.name}")
            continue
        # Slice rather than sub: a lambda here would close over the loop
        # variable, and a generated table can contain backslash sequences that
        # re.sub would try to interpret as replacement escapes.
        m = pat.search(s)
        s = s[:m.end(1)] + fn() + s[m.start(2):]
        print(f"  + {path.name}:{name}")
    path.write_text(s)


def main() -> int:
    inject(ROOT / "README.md", README_BLOCKS)
    inject(ROOT / "docs" / "CORPUS.md", CORPUS_BLOCKS)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

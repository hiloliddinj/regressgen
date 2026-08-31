"""Draft a user-voice bug report for each mined case.

The report is derived from the upstream regression test (which encodes the
*correct* behaviour) and the commit subject — never from the fix diff itself.
That keeps the report honest about the symptom without handing over the
location or shape of the fix.

Drafts are written to cases/<id>/report.md and are reviewed by a human before
the corpus is frozen; see docs/CORPUS.md.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from regressgen.corpus import load_cases
from regressgen.model import complete

REPOS = Path(__file__).resolve().parent.parent / ".work" / "repos"

SYSTEM = """\
You are a user of a Python library, filing an issue on its GitHub tracker.

You will be shown the regression test a maintainer later added when they fixed
the bug. Use it only to learn what actually goes wrong. Then write the issue as
the user would have written it BEFORE any of that was known.

You do not have the source open. You do not know why it happens. You know only
what you observed from the outside.

Hard rules — a report that breaks any of these is unusable:
  * Never explain the cause. No "because ...", no "it fails when the internal
    ... is None", no description of control flow inside the library.
  * Never name anything private or internal: no dunder methods, no leading-
    underscore names, no module or file names, no class internals. Public API
    you actually called is fine.
  * Never state the exact expected return value, exact error message text, or
    exact assertion. Say what you wanted in ordinary words: "I expected a clear
    error", "I expected these two to compare equal", "I expected it to finish".
  * Never mention tests, maintainers, commits, versions of the fix, or the fix.
  * Everything you write must be true. Vague is fine; wrong is not.

Include a short reproduction using only public API, and say plainly what
happened and what you expected instead. Slightly imprecise, mildly annoyed,
concrete. 90-150 words. Prose plus one code block. No headings, no title."""


PRIVATE_RE = re.compile(r"\b_[A-Za-z]\w*")
CAUSE_RE = re.compile(
    r"\b(because|caused by|due to|root cause|internally|under the hood|"
    r"the bug is|should check|missing check|fails to check)\b", re.I)


FENCE_RE = re.compile(r"```.*?```", re.S)

# Protocol dunders are public API, not internals. A user of a dataclass library
# says "__eq__" the way a user of a dict says "keys()". Banning them outright
# made the attrs cases unwritable.
PUBLIC_DUNDERS = {
    "__init__", "__new__", "__eq__", "__ne__", "__lt__", "__le__", "__gt__",
    "__ge__", "__hash__", "__repr__", "__str__", "__call__", "__len__",
    "__iter__", "__next__", "__contains__", "__getitem__", "__setitem__",
    "__delitem__", "__reversed__", "__enter__", "__exit__", "__copy__",
    "__deepcopy__", "__reduce__", "__getstate__", "__setstate__",
    "__traceback__", "__slots__", "__dict__", "__class__", "__name__",
    "__doc__", "__module__", "__annotations__", "__post_init__",
    "__pre_init__", "__attrs_post_init__", "__attrs_pre_init__",
}
DUNDER_RE = re.compile(r"__\w+__")


def leaks(report: str, src_diff: str, src_files: list[str]) -> list[str]:
    """Mechanical gate: does the report give away internals or the fix?

    Only prose is scanned. A dunder or private name pasted inside a fenced
    block is an observed traceback — that is exactly what a real reporter
    includes, and it reveals nothing the user did not already see.
    """
    prose = FENCE_RE.sub(" ", report)
    bad = []
    private = {m for m in PRIVATE_RE.findall(src_diff) if len(m) > 2}
    for name in sorted(private):
        # Word-boundary, not substring: `_cache` must not match inside
        # `mru_cache`, which is a perfectly public decorator name.
        if re.search(rf"(?<![\w]){re.escape(name)}\b", prose):
            bad.append(f"private identifier {name!r}")
    for f in src_files:
        stem = f.rsplit("/", 1)[-1]
        if stem in report:                       # literal "version.py"
            bad.append(f"source file {stem!r}")
    for d in set(DUNDER_RE.findall(prose)) - PUBLIC_DUNDERS:
        bad.append(f"internal dunder {d!r} in prose")
    m = CAUSE_RE.search(prose)
    if m:
        bad.append(f"causal explanation ({m.group(0)!r})")
    return bad


def diff_for(repo: str, parent: str, sha: str, files: list[str],
             additions_only: bool = True) -> str:
    path = REPOS / repo
    if not path.exists():
        return ""
    out = subprocess.run(
        ["git", "-C", str(path), "diff", f"{parent}..{sha}", "--", *files],
        capture_output=True, text=True,
    ).stdout
    if additions_only:
        out = "\n".join(x for x in out.splitlines() if not x.startswith("-"))
    return out[:12_000]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true", help="overwrite existing reports")
    ap.add_argument("--case", action="append")
    args = ap.parse_args()

    total = 0.0
    for case in load_cases(args.case):
        dest = case.root / "report.md"
        if dest.exists() and not args.force:
            print(f"  = {case.id} (exists)")
            continue
        m = case.meta
        diff = diff_for(m["repo"], m["buggy_commit"], m["fix_commit"],
                        m["oracle_test_files"])
        src_diff = diff_for(m["repo"], m["buggy_commit"], m["fix_commit"],
                            m["src_files"], additions_only=False)
        if not diff.strip():
            print(f"  ! {case.id}: no test diff, skipped")
            continue
        prompt = (
            f"Library: {m['repo']}\n"
            f"Maintainer's one-line summary of the fix: {m['subject']}\n\n"
            f"The regression test they added (diff, additions only):\n"
            f"```diff\n{diff}\n```\n\n"
            f"For reference, this is how the test fails on the unfixed code:\n"
            f"```\n{m.get('oracle_failure_excerpt', '')[:1800]}\n```\n"
        )
        text, bad, attempts = "", ["unstarted"], 0
        while bad and attempts < 3:
            attempts += 1
            extra = ""
            if bad:
                extra = ("\n\nA previous draft was rejected for: "
                         + "; ".join(bad) + ". Avoid all of that.")
            c = complete(prompt + extra, system=SYSTEM)
            total += c.usd
            if c.error or not c.text.strip():
                bad = [str(c.error)]
                continue
            text = c.text.strip()
            bad = leaks(text, src_diff, m["src_files"])
        if bad:
            print(f"  ! {case.id}: still leaking after {attempts}: {bad}")
            continue
        dest.write_text(text + "\n")
        print(f"  + {case.id}  ({len(text.split())}w, {attempts} draft(s))")

    print(f"\nreport drafting cost: ${total:.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

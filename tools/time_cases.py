"""Time each case's existing test suite.

`try_fix` runs the full suite on every probe, so a case with a slow suite costs
far more than its share of an evaluation run. This reports the cost of each case
so slow ones can be excluded deliberately rather than discovered mid-sweep.
"""

from __future__ import annotations

import argparse
import shutil
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from regressgen.corpus import load_cases  # noqa: E402
from regressgen.sandbox import run_suite  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--threshold", type=float, default=25.0,
                    help="seconds; cases slower than this are flagged")
    ap.add_argument("--drop", action="store_true",
                    help="actually move flagged cases to cases_excluded/")
    args = ap.parse_args()

    slow = []
    for case in load_cases():
        t0 = time.monotonic()
        r = run_suite(case.buggy, case.tests_dir, timeout=180)
        dt = time.monotonic() - t0
        flag = ""
        if dt > args.threshold or not r.passed:
            flag = "  <-- SLOW" if dt > args.threshold else "  <-- SUITE RED"
            slow.append(case)
        print(f"{case.id:34s} {dt:7.1f}s  suite={'green' if r.passed else 'RED'}{flag}")

    print(f"\n{len(slow)} case(s) flagged (threshold {args.threshold}s)")
    if slow and args.drop:
        dest = ROOT / "cases_excluded"
        dest.mkdir(exist_ok=True)
        for c in slow:
            shutil.move(str(c.root), str(dest / c.id))
            print(f"  moved {c.id} -> cases_excluded/")
        print("\nExclusions are deliberate and recorded here; see docs/CORPUS.md.")
    elif slow:
        print("Re-run with --drop to move them out of the corpus.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

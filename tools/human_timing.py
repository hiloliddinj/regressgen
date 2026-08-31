"""Time a human on the same task, scored by the same gate.

Not run for the submitted numbers — there were not enough hours. It exists so
the human-time column can be filled with a measurement rather than a guess, by
whoever has twenty minutes.

    uv run python tools/human_timing.py --n 3
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from regressgen.corpus import load_cases  # noqa: E402
from regressgen.verify import verify  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=3)
    ap.add_argument("--editor", default="${EDITOR:-vi}")
    ap.add_argument("--out", default="results/human_timing.json")
    args = ap.parse_args()

    cases = load_cases()[: args.n]
    rows = []
    for i, case in enumerate(cases, 1):
        print("\n" + "=" * 72)
        print(f"CASE {i}/{len(cases)}: {case.id}")
        print(f"Repository to read: {case.buggy}")
        print("=" * 72)
        print(case.report)
        print("=" * 72)
        print("Write a pytest test that fails on this code and would pass once "
              "the bug is fixed.\nSave and close your editor when done.")
        input("Press Enter to start the clock... ")

        with tempfile.NamedTemporaryFile("w+", suffix=".py", delete=False) as f:
            f.write("# Write your regression test here.\n")
            path = f.name
        t0 = time.monotonic()
        subprocess.run(f'{args.editor} {path}', shell=True)
        elapsed = time.monotonic() - t0

        result = verify(case, Path(path).read_text())
        print(f"\n  {elapsed/60:.1f} min   verdict: {result.verdict}")
        rows.append({"case_id": case.id, "minutes": round(elapsed / 60, 2),
                     "verdict": str(result.verdict)})

    ok = sum(r["verdict"] == "REPRO" for r in rows)
    total = sum(r["minutes"] for r in rows)
    payload = {"cases": rows, "repro": ok, "n": len(rows),
               "total_minutes": round(total, 1),
               "minutes_per_case": round(total / len(rows), 1) if rows else 0}
    Path(args.out).write_text(json.dumps(payload, indent=2))
    print(f"\n{ok}/{len(rows)} reproduced · {payload['minutes_per_case']} min/case"
          f"\nwritten to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Derive changelog evidence from results/.

Which cases flipped at each rung, which regressed, and which nobody solved.
Everything the Improvement Changelog claims should be visible in this output.
"""

from __future__ import annotations

import json
import sys
from itertools import pairwise
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from regressgen.runner import RESULTS, SYSTEMS  # noqa: E402

REPRO = "REPRO"


def load() -> dict[str, dict[str, str]]:
    out = {}
    for s in SYSTEMS:
        f = RESULTS / f"{s}.json"
        if f.exists():
            d = json.loads(f.read_text())
            out[s] = {c["case_id"]: c["verdict"] for c in d["cases"]}
    return out


def stability() -> None:
    """Run-to-run agreement on the cases both runs share.

    The exploratory 17 are a subset of the full corpus, so re-running every
    system gives a free reliability estimate: same system, same cases, two
    independent runs. This is the honest measure of how much a one-case delta
    is worth.
    """
    import json as _json

    old_dir = RESULTS / "_exploratory-17case"
    if not old_dir.exists():
        print("no exploratory run to compare against")
        return

    print("\n" + "=" * 78)
    print("RUN-TO-RUN STABILITY — same system, same cases, two independent runs")
    print("=" * 78)
    print(f"{'system':18s} {'shared':>7s} {'agree':>7s} {'flip→pass':>10s} "
          f"{'flip→fail':>10s}  agreement")
    tot_shared = tot_agree = 0
    for f in sorted(old_dir.glob("*.json")):
        new_f = RESULTS / f.name
        if not new_f.exists():
            continue
        old_d, new_d = _json.loads(f.read_text()), _json.loads(new_f.read_text())
        if old_d.get("started") == new_d.get("started"):
            print(f"{f.stem:18s}   (archived copy of the same run — not a re-run; "
                  f"no stability signal yet)")
            continue
        old = {c["case_id"]: c["verdict"] for c in old_d["cases"]}
        new = {c["case_id"]: c["verdict"] for c in new_d["cases"]}
        shared = sorted(set(old) & set(new))
        if not shared:
            continue
        if f.stem == "v6-critic":
            print(f"{f.stem:18s}   (skipped — the critic's output contract changed "
                  f"between runs, so this pair is not a like-for-like re-run)")
            continue
        agree = sum(old[c] == new[c] for c in shared)
        up = sum(old[c] != REPRO and new[c] == REPRO for c in shared)
        down = sum(old[c] == REPRO and new[c] != REPRO for c in shared)
        tot_shared += len(shared)
        tot_agree += agree
        print(f"{f.stem:18s} {len(shared):7d} {agree:7d} {up:10d} {down:10d}"
              f"  {agree / len(shared) * 100:5.0f}%")
    if tot_shared:
        print(f"\noverall verdict agreement across re-runs: "
              f"{tot_agree}/{tot_shared} = {tot_agree / tot_shared * 100:.0f}%")
        print("A single-case delta smaller than this noise floor is not evidence.")


def main() -> int:
    data = load()
    systems = list(data)
    if len(systems) < 2:
        print("need at least two systems")
        return 1
    cases = sorted(next(iter(data.values())))

    print("=" * 78)
    print("RUNG-BY-RUNG DELTAS")
    print("=" * 78)
    for a, b in pairwise(systems):
        va, vb = data[a], data[b]
        won = [c for c in cases if va.get(c) != REPRO and vb.get(c) == REPRO]
        lost = [c for c in cases if va.get(c) == REPRO and vb.get(c) != REPRO]
        na = sum(v == REPRO for v in va.values())
        nb = sum(v == REPRO for v in vb.values())
        print(f"\n{a}  ->  {b}     {na} -> {nb}  ({nb - na:+d})")
        for c in won:
            print(f"   WON  {c:32s} {va.get(c)} -> REPRO")
        for c in lost:
            print(f"   LOST {c:32s} REPRO -> {vb.get(c)}")
        if not won and not lost:
            print("   (no case changed verdict)")

    print("\n" + "=" * 78)
    print("HARDEST CASES — never solved by any system")
    print("=" * 78)
    never = [c for c in cases if all(data[s].get(c) != REPRO for s in systems)]
    for c in never:
        print(f"   {c:32s} " + "  ".join(f"{s}={data[s].get(c)}" for s in systems))
    if not never:
        print("   (every case solved by at least one system)")

    print("\n" + "=" * 78)
    print("BASELINE-ONLY WINS — solved by the baseline, lost by the final system")
    print("=" * 78)
    final = systems[-1]
    only = [c for c in cases
            if data[systems[0]].get(c) == REPRO and data[final].get(c) != REPRO]
    for c in only:
        print(f"   {c:32s} final={data[final].get(c)}")
    if not only:
        print("   (none — the final system is a strict superset of the baseline)")

    stability()

    print("\n" + "=" * 78)
    print("PER-CASE GRID")
    print("=" * 78)
    w = max(len(c) for c in cases)
    print(" " * (w + 2) + "  ".join(f"{s[:9]:>9s}" for s in systems))
    for c in cases:
        marks = "  ".join(
            f"{('PASS' if data[s].get(c) == REPRO else (data[s].get(c) or '-')[:9]):>9s}"
            for s in systems)
        print(f"{c:{w}s}  {marks}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

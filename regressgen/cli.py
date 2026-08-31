"""regressgen command line."""

from __future__ import annotations

import argparse
import json
import sys
from itertools import pairwise
from pathlib import Path

from .agent.loop import Variant
from .agent.loop import solve as agent_solve
from .corpus import Case, load_cases
from .report import mcnemar, per_case, scoreboard, stability, verdict_breakdown
from .runner import SYSTEMS, run_system
from .sandbox import detect_python, run_at_paths, run_candidate, run_suite


def cmd_list(a) -> int:
    for c in load_cases():
        words = len(c.report.split())
        print(f"{c.id:34s} {c.meta['repo']:15s} report:{words:4d}w  {c.meta['subject'][:52]}")
    return 0


def cmd_show(a) -> int:
    """Everything about one case, including the held-out answer."""
    cases = load_cases([a.case_id])
    if not cases:
        print(f"no such case: {a.case_id}", file=sys.stderr)
        return 1
    c = cases[0]
    m = c.meta
    print(f"case      {c.id}")
    print(f"library   {m['repo']}  ({m.get('license','?')})")
    print(f"upstream  {m.get('upstream','?')}")
    print(f"fix       {m['fix_commit']}")
    print(f"parent    {m['buggy_commit']}")
    print(f"subject   {m['subject']}")
    print(f"touched   {', '.join(m['src_files'])}  ({m.get('src_churn','?')} lines)")
    if m.get("fix_commit_url"):
        print(f"commit    {m['fix_commit_url']}")
    for ref in m.get("upstream_refs", []):
        print(f"issue     {ref}")
    print(f"\n{'-' * 72}\nBUG REPORT (this is all the agent gets)\n{'-' * 72}")
    print(c.report.strip())
    if a.spoil:
        print(f"\n{'-' * 72}\nHELD-OUT ORACLE — the maintainer's own regression test\n{'-' * 72}")
        for f in c.oracle_tests:
            print(f"\n### {f.name}\n")
            print(f.read_text()[:4000])
    else:
        print("\n(the held-out fix and oracle test are hidden; pass --spoil to see them)")
    return 0


def cmd_validate(a) -> int:
    """Re-prove I1-I4 for every case, so judges can trust the ground truth."""
    bad = 0
    cases = load_cases(a.case)
    print(f"re-proving I1-I4 on {len(cases)} cases "
          f"(4 pytest runs each, no model calls, no cost)\n", flush=True)
    for i, c in enumerate(cases, 1):
        oracle = c.oracle_at_original_paths
        i1 = run_suite(c.buggy, c.tests_dir).passed
        i2 = run_suite(c.fixed, c.tests_dir).passed
        i3 = not run_at_paths(c.buggy, oracle).passed
        i4 = run_at_paths(c.fixed, oracle).passed
        ok = i1 and i2 and i3 and i4
        bad += not ok
        flag = "OK  " if ok else "FAIL"
        print(f"[{i:2d}/{len(cases)}] {flag} {c.id:34s} "
              f"I1={i1!s:5s} I2={i2!s:5s} I3={i3!s:5s} I4={i4!s:5s}", flush=True)
    print(f"\n{'all cases valid' if not bad else f'{bad} INVALID CASE(S)'}")
    return 1 if bad else 0


def cmd_run(a) -> int:
    cases = load_cases(a.case)
    if a.limit:
        cases = cases[: a.limit]
    if not cases:
        print("no cases found", file=sys.stderr)
        return 1
    # A case with no report is a freshly mined one that has not been written up.
    # Running it would quietly score the agent on an empty prompt.
    missing = [c.id for c in cases if not c.report.strip()]
    if missing:
        print(f"{len(missing)} case(s) have no bug report yet:", file=sys.stderr)
        for m in missing:
            print(f"  {m}", file=sys.stderr)
        print("\nRun:  uv run python tools/write_reports.py", file=sys.stderr)
        return 1
    for rep in range(1, a.repeat + 1):
        for system in a.system:
            label = f" (repeat {rep}/{a.repeat})" if a.repeat > 1 else ""
            print(f"\n=== {system} over {len(cases)} cases "
                  f"(workers={a.workers}){label} ===", flush=True)
            d = run_system(system, cases, workers=a.workers)
            su = d["summary"]
            print(f"repro {su['repro']}/{su['n']} ({su['repro_rate'] * 100:.0f}%)  "
                  f"${su['usd_total']:.3f}  {d['wall_seconds']:.0f}s wall  "
                  f"run #{d['run_index']}")
            print("verdicts:", json.dumps(su["verdicts"]))
            if su.get("errors"):
                print(f"  !! {su['errors']} case(s) hit a harness/API error and were "
                      f"excluded. Re-run before quoting this.")
    return 0


def cmd_solve(a) -> int:
    """Run the agent against a repository you own, from a bug report you wrote."""
    repo = Path(a.repo).resolve()
    if not repo.is_dir():
        print(f"no such directory: {repo}", file=sys.stderr)
        return 1
    report = Path(a.report).read_text()
    case = Case.from_repo(repo, report, a.tests_dir, a.pkg_dir)
    python = a.python or detect_python(repo)

    print(f"repo      {repo}")
    print(f"package   {case.pkg_dir}")
    print(f"tests     {case.tests_dir}")
    print(f"agent     {a.variant}")
    print(f"python    {python}"
          f"{'  (your project venv)' if python != sys.executable else '  (harness venv — your project deps may be missing)'}\n")

    sol = agent_solve(case, Variant(a.variant), python=python)
    if not sol.test_source.strip():
        print(f"agent produced no test ({sol.error})", file=sys.stderr)
        return 1

    # One-sided check: with no fixed tree we can only prove the failing half here.
    # The other half is what the agent's try_fix probe is for; its result is shown
    # below so a human can judge whether the expected behaviour is right.
    r = run_candidate(case.buggy, sol.test_source, case.tests_dir, python=python)
    proven = not r.passed and r.collected

    probes = [c for c in sol.calls if c["tool"] == "try_fix"]
    print("=" * 72)
    print(sol.test_source)
    print("=" * 72)
    print(f"\nFails on your code as it stands : {'YES' if proven else 'NO'}"
          f"  (exit {r.rc})")
    if not r.collected:
        print("  WARNING: the test did not import cleanly — treat it as a draft.")
    if probes:
        print(f"Hypothetical-fix probes run     : {len(probes)}")
        print(f"  last probe: {probes[-1]['result'][:100]}")
    else:
        print("Hypothetical-fix probes run     : 0")
    if sol.rationale:
        print(f"\nAgent's rationale:\n  {sol.rationale.strip()[:600]}")
    print(f"\ncost ${sol.usd:.3f} · {len(sol.calls)} tool calls")

    print("\n" + "-" * 72)
    print("REVIEW BEFORE USE. This test asserts what the agent believes the correct")
    print("behaviour to be. That judgement is the part a human still owns — read the")
    print("assertion and confirm it is what you actually want the code to do.")
    if a.out:
        Path(a.out).write_text(sol.test_source)
        print(f"\nwritten to {a.out}")
    else:
        print("\nNot written to disk. Pass --out PATH to save it.")
    return 0 if proven else 2


def cmd_report(a) -> int:
    print(scoreboard())
    print()
    print("### Failure modes (most recent run of each system)\n")
    print(verdict_breakdown())
    print()
    print("### How much is one run worth?\n")
    print(stability())
    print()
    print(per_case())
    print()
    print("### Paired significance (exact McNemar)\n")
    from .report import SYSTEMS as _S
    from .report import load
    have = [s for s in _S if load(s)]
    if len(have) >= 2:
        print(f"Headline — {have[0]} vs {have[-1]}:\n")
        print(f"- {mcnemar(have[0], have[-1])}\n")
        print("Rung by rung:\n")
        for x, y in pairwise(have):
            print(f"- {mcnemar(x, y)}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(prog="regressgen")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list", help="list mined cases").set_defaults(fn=cmd_list)

    v = sub.add_parser("validate", help="re-prove the four corpus invariants")
    v.add_argument("--case", action="append")
    v.set_defaults(fn=cmd_validate)

    sh = sub.add_parser("show", help="inspect one case")
    sh.add_argument("case_id")
    sh.add_argument("--spoil", action="store_true",
                    help="also print the held-out oracle test")
    sh.set_defaults(fn=cmd_show)

    r = sub.add_parser("run", help="run a system over the corpus")
    r.add_argument("--system", action="append", required=True, choices=SYSTEMS)
    r.add_argument("--case", action="append")
    r.add_argument("--workers", type=int, default=4)
    r.add_argument("--repeat", type=int, default=1,
                   help="run the system N times; results are averaged and each "
                        "run is kept in results/runs/")
    r.add_argument("--limit", type=int, default=None,
                   help="only the first N cases — for a cheap partial reproduction")
    r.set_defaults(fn=cmd_run)

    so = sub.add_parser("solve", help="generate a regression test for your own repo")
    so.add_argument("--repo", required=True, help="path to the repository under test")
    so.add_argument("--report", required=True, help="file containing the bug report")
    so.add_argument("--tests-dir", default="tests")
    so.add_argument("--pkg-dir", default=None, help="override package dir autodetect")
    so.add_argument("--variant", default=Variant.V4_DISCIPLINE.value,
                choices=[v.value for v in Variant],
                help="v4-discipline is the default: same score as v5/v6 at a "
                     "fifth of the cost. Use v5-fixprobe to also get a stated "
                     "fix hypothesis you can check.")
    so.add_argument("--python", default=None,
                    help="interpreter to run tests under (default: the repo's "
                         ".venv if present, else the harness venv)")
    so.add_argument("--out", default=None, help="write the test here (default: print only)")
    so.set_defaults(fn=cmd_solve)

    sub.add_parser("report", help="print the comparison table").set_defaults(fn=cmd_report)

    a = ap.parse_args()
    return a.fn(a)


if __name__ == "__main__":
    raise SystemExit(main())

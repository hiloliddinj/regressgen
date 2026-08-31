"""Render stored runs into readable agent trajectories.

One markdown file per (system, case): the exact instructions the agent was
given, every tool call and what the tool answered, the retries those answers
caused, the submitted test, and the two-sided gate's verdict.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from regressgen.agent import prompts  # noqa: E402
from regressgen.agent.loop import CONFIG, Variant  # noqa: E402
from regressgen.corpus import load_cases  # noqa: E402
from regressgen.runner import RESULTS  # noqa: E402

OUT = ROOT / "trajectories"
CLIP = 2200


def fence(text: str, lang: str = "") -> str:
    body = (text or "").rstrip()
    if len(body) > CLIP:
        body = body[:CLIP] + f"\n... [{len(text) - CLIP} more chars]"
    return f"```{lang}\n{body}\n```"


def system_for(system: str) -> str:
    if system == "baseline":
        return prompts.build_system(navigate=False, execute=False, discipline=False,
                                    fix_probe=False, tool_output=False)
    cfg = CONFIG[Variant(system)]
    return prompts.build_system(navigate=True, execute=cfg["execute"],
                                discipline=cfg["discipline"],
                                fix_probe=cfg["fix_probe"], tool_output=True)


def render(system: str, rec: dict, report: str) -> str:
    L = [f"# Trajectory — `{system}` on `{rec['case_id']}`", "",
         f"**Verdict: {rec['verdict']}**"
         + ("  (fails on buggy, passes on fixed — reproduces the bug)"
            if rec["verdict"] == "REPRO" else ""),
         "",
         f"- cost `${rec['usd']}` · wall `{rec['seconds']}s` · "
         f"tool calls `{len(rec.get('trajectory', []))}`", "",
         "## 1. Agent instructions (system prompt)", "", fence(system_for(system)), "",
         "## 2. Task (user prompt)", "",
         "The agent receives the bug report and the repository layout. It never "
         "sees the fixed tree, the upstream fix, or the maintainer's test.", "",
         fence(report), "", "## 3. Tool calls", ""]

    calls = rec.get("trajectory", [])
    if not calls:
        L += ["_No tools — this system answers in a single prompt._", ""]
    for i, c in enumerate(calls, 1):
        args = dict(c.get("args") or {})
        pretty = ", ".join(f"{k}={json.dumps(v)[:110]}" for k, v in args.items())
        L += [f"### {i}. `{c['tool']}`({pretty})", "", "Tool responded:", "",
              fence(str(c.get("result", ""))), ""]

    L += ["## 4. Submitted test", "", fence(rec.get("test_source", ""), "python"), ""]
    if rec.get("rationale"):
        L += ["**Agent's stated rationale:**", "", f"> {rec['rationale']}", ""]
    L += ["## 5. Two-sided gate", "",
          f"### Against `buggy/` — exit {rec['buggy_rc']} "
          f"(must be non-zero)", "", fence(rec.get("buggy_output", "")), "",
          f"### Against `fixed/` — exit {rec['fixed_rc']} "
          f"(must be zero)", "", fence(rec.get("fixed_output", "")), ""]
    return "\n".join(L)


def write_index(seen: dict[str, dict[str, str]], out_root: Path,
                src: Path, note: str = "") -> None:
    """A map of the trajectories, so a reader knows where to start."""
    systems = list(seen)
    cases = sorted({c for v in seen.values() for c in v})
    L = ["# Agent trajectories", "",
         f"Generated from `{src.relative_to(ROOT) if src.is_relative_to(ROOT) else src}/` by "
         f"`tools/export_trajectories.py`.", ""]
    if note:
        L += [note, ""]
    L += [
         "One file per system per case. Each shows the exact instructions the "
         "agent was given, every tool call and what the tool answered, the "
         "retries those answers caused, the test it submitted, and both halves "
         "of the two-sided gate.", "",
         "**PASS** means the test failed on the buggy tree and passed on the "
         "held-out fixed tree.", "",
         "Tool responses are the real output, truncated to 2,200 characters where "
         "long; the untruncated record is in `results/<system>.json` under each "
         "case's `trajectory`.", "",
         "## Where to start", ""]

    confirmatory = [
        ("baseline/more-itertools-0e6acdf9.md",
         "What one prompt with no tools produces, given the whole source file."),
        ("v4-discipline/more-itertools-0e6acdf9.md",
         "The shipped agent on the same case: search, targeted reads, run the "
         "test, check the failure is the right failure."),
        ("v4-discipline/semver-bc41390f.md",
         "The case no system solves. The agent's reasoning is sound and its "
         "answer is defensible — the report simply does not contain the "
         "maintainer's design decision."),
    ]

    exploratory = [
        ("v2-tools/boltons-eb659013.md",
         "The same case *without* execution feedback — the agent has to reason "
         "about what correct behaviour is, and gets it right."),
        ("v3-exec/boltons-eb659013.md",
         "The same case *with* execution feedback. It calls `run_test`, sees "
         "`FAILED`, and stops — with an invented expectation. The clearest "
         "illustration of a half-observable verifier."),
        ("v4-discipline/boltons-eb659013.md",
         "The recovery: same tools as v3, plus the instruction to check *why* "
         "it failed."),
        ("v5-fixprobe/semver-bc41390f.md",
         "The agent invents a patch that makes its own wrong expectation true, "
         "and `try_fix` answers \"your test PASSES with this fix\". "
         "Self-verification confirming an error."),
        ("v6-critic/semver-bc41390f.md",
         "A fresh-context reviewer reads the same wrong test and approves it."),
        ("baseline/more-itertools-0e6acdf9.md",
         "What one prompt with no tools produces."),
    ]

    curated = exploratory if any(
        (out_root / p).exists() for p, _ in exploratory[:1]) else confirmatory
    rows = [(path, why) for path, why in curated if (out_root / path).exists()]
    if rows:
        L += ["| Read this | Why |", "|---|---|"]
        L += [f"| [`{path}`]({path}) | {why} |" for path, why in rows]

    L += ["", "## Full index", "",
          "| Case | " + " | ".join(systems) + " |",
          "|---|" + "---|" * len(systems)]
    for c in cases:
        row = []
        for sysname in systems:
            v = seen[sysname].get(c)
            row.append(f"[{'**PASS**' if v == 'REPRO' else (v or '-').lower()}]"
                       f"({sysname}/{c}.md)" if v else "-")
        L.append(f"| `{c}` | " + " | ".join(row) + " |")
    (out_root / "README.md").write_text("\n".join(L) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--system", action="append")
    ap.add_argument("--case", action="append")
    ap.add_argument("--results-dir", default=None,
                    help="read from this results directory "
                         "(default: results/; use results/_exploratory-17case "
                         "for the exploratory ladder)")
    ap.add_argument("--label", default=None,
                    help="subdirectory of trajectories/ to write into")
    args = ap.parse_args()

    src = (Path(args.results_dir).resolve() if args.results_dir else RESULTS)
    out_root = OUT / args.label if args.label else OUT

    reports = {c.id: c.report for c in load_cases()}
    out_root.mkdir(parents=True, exist_ok=True)
    n = 0
    seen: dict[str, dict[str, str]] = {}
    for f in sorted(src.glob("*.json")):
        system = f.stem
        if args.system and system not in args.system:
            continue
        data = json.loads(f.read_text())
        for rec in data["cases"]:
            if args.case and rec["case_id"] not in args.case:
                continue
            d = out_root / system
            d.mkdir(parents=True, exist_ok=True)
            (d / f"{rec['case_id']}.md").write_text(
                render(system, rec, reports.get(rec["case_id"], "")))
            n += 1
            seen.setdefault(system, {})[rec["case_id"]] = rec["verdict"]
    note = ""
    if "_exploratory" in str(src):
        note = ("> **Note on these files.** The exploratory ladder was run "
                "before the trajectory recorder was fixed to store full tool "
                "output, so tool responses here are summarised (`\"1472 "
                "chars\"`, `\"2 hits\"`) rather than verbatim. The tool calls, "
                "their arguments, the retries and the submitted test are all "
                "complete. Confirmatory trajectories carry the real tool output.")
    write_index(seen, out_root, src, note)
    print(f"wrote {n} trajectories + index to {out_root}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

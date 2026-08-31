"""Render comparison tables from stored results.

Agent evaluations are noisy: two runs of the same system on the same cases
disagree on a substantial fraction of them. So a single run is not a
measurement. Everything here works over *all* stored runs of a system, reports
a mean with its observed range, and says how many runs it is averaging.
"""

from __future__ import annotations

import json
from itertools import pairwise
from math import comb
from statistics import mean

from .runner import RESULTS, RUNS, SYSTEMS
from .verify import Verdict

ORDER = [Verdict.REPRO, Verdict.VACUOUS, Verdict.WRONG_EXPECTATION,
         Verdict.INVALID, Verdict.INVERTED, Verdict.LEAKED, Verdict.ERROR]

SILENT = {Verdict.VACUOUS, Verdict.INVERTED}

LABEL = {
    "baseline": "Baseline (one prompt, no tools)",
    "v2-tools": "v2  + repo navigation",
    "v3-exec": "v3  + run the test",
    "v4-discipline": "v4  + right-reason check",
    "v5-fixprobe": "v5  + hypothetical-fix probe",
    "v6-critic": "v6  + adversarial critic",
}


def load_runs(system: str) -> list[dict]:
    """Every stored run of a system, oldest first."""
    if not RUNS.exists():
        p = RESULTS / f"{system}.json"
        return [json.loads(p.read_text())] if p.exists() else []
    files = sorted(RUNS.glob(f"{system}.*.json"),
                   key=lambda f: int(f.stem.rsplit(".", 1)[-1]))
    runs = [json.loads(f.read_text()) for f in files]
    if runs:
        return runs
    p = RESULTS / f"{system}.json"
    return [json.loads(p.read_text())] if p.exists() else []


def load(system: str) -> dict | None:
    runs = load_runs(system)
    return runs[-1] if runs else None


def silent_failures(d: dict) -> int:
    return sum(d["summary"]["verdicts"].get(k, 0) for k in SILENT)


def _agg(system: str) -> dict | None:
    runs = load_runs(system)
    if not runs:
        return None
    rates = [r["summary"]["repro_rate"] for r in runs]
    repros = [r["summary"]["repro"] for r in runs]
    return {
        "runs": len(runs),
        "n": runs[-1]["summary"]["n"],
        "rate": mean(rates),
        "lo": min(rates), "hi": max(rates),
        "repro": mean(repros),
        "silent": mean(silent_failures(r) for r in runs),
        "errors": sum(r["summary"].get("errors", 0) for r in runs),
        "usd": mean(r["summary"]["usd_per_case"] for r in runs),
        "secs": mean(r["summary"]["seconds_per_case"] for r in runs),
        "verdicts": runs[-1]["summary"]["verdicts"],
    }


def scoreboard() -> str:
    rows = [(s, _agg(s)) for s in SYSTEMS]
    rows = [(s, a) for s, a in rows if a]
    if not rows:
        return "No results yet. Run `regressgen run --system baseline` first."

    multi = any(a["runs"] > 1 for _, a in rows)
    out = ["| System | Repro rate | " + ("Range | " if multi else "")
           + "Runs | Silent failures | $/case | s/case |",
           "|---|---:|" + ("---:|" if multi else "") + "---:|---:|---:|---:|"]
    for s, a in rows:
        rng = (f" {a['lo'] * 100:.0f}–{a['hi'] * 100:.0f}% |"
               if multi else "")
        out.append(
            f"| {LABEL.get(s, s)} | **{a['repro']:.1f}/{a['n']}"
            f"  ({a['rate'] * 100:.0f}%)** |{rng} {a['runs']} | "
            f"{a['silent']:.1f} | ${a['usd']:.3f} | {a['secs']:.0f} |"
        )
    caption = ("Repro rate is the mean over all stored runs of that system; "
               "*Range* is the lowest and highest single run. "
               if multi else
               "Repro rate is from a single run of each system. ")
    out += ["",
            caption
            + "*Silent failures* are tests that pass when run against the buggy "
            "code (VACUOUS + INVERTED) — a developer runs pytest, sees green, "
            "and commits believing they have coverage they do not have. Every "
            "other failure mode is loud."]
    return "\n".join(out)


def verdict_breakdown() -> str:
    rows = [(s, load(s)) for s in SYSTEMS]
    rows = [(s, d) for s, d in rows if d]
    if not rows:
        return ""
    out = ["| System (most recent run) | "
           + " | ".join(v.value.title().replace("_", " ") for v in ORDER) + " |",
           "|---|" + "---:|" * len(ORDER)]
    for s, d in rows:
        v = d["summary"]["verdicts"]
        out.append(f"| {LABEL.get(s, s)} | "
                   + " | ".join(str(v.get(k, 0)) for k in ORDER) + " |")
    return "\n".join(out)


def per_case() -> str:
    rows = [(s, load(s)) for s in SYSTEMS]
    rows = [(s, d) for s, d in rows if d]
    if not rows:
        return ""
    ids = sorted({c["case_id"] for _, d in rows for c in d["cases"]})
    lines = ["| Case | " + " | ".join(s for s, _ in rows) + " |",
             "|---|" + "---|" * len(rows)]
    for cid in ids:
        cells = []
        for _, d in rows:
            m = {c["case_id"]: c["verdict"] for c in d["cases"]}
            v = m.get(cid, "-")
            cells.append("**PASS**" if v == Verdict.REPRO else v.lower())
        lines.append(f"| `{cid}` | " + " | ".join(cells) + " |")
    return "\n".join(lines)


def _exact_p(b: int, c: int) -> float:
    n = b + c
    if n == 0:
        return 1.0
    hi = max(b, c)
    return min(1.0, 2 * sum(comb(n, k) for k in range(hi, n + 1)) / 2 ** n)


def mcnemar(system_a: str, system_b: str) -> str:
    """Exact McNemar over paired per-case outcomes, pooled across repeats.

    Systems run on the same cases, so only cases where they disagree carry
    information. When both systems have several runs, runs are paired in order
    and the discordant counts summed — a stratified McNemar. Pooling assumes
    the runs are independent, which they are: each is a fresh set of model
    calls.
    """
    ra, rb = load_runs(system_a), load_runs(system_b)
    if not ra or not rb:
        return f"(missing results for {system_a} or {system_b})"

    b = c_ = shared_n = 0
    pairs = min(len(ra), len(rb))
    for i in range(pairs):
        va = {x["case_id"]: x["verdict"] for x in ra[i]["cases"]}
        vb = {x["case_id"]: x["verdict"] for x in rb[i]["cases"]}
        shared = [k for k in set(va) & set(vb)
                  if va[k] != Verdict.ERROR and vb[k] != Verdict.ERROR]
        shared_n += len(shared)
        b += sum(va[k] != Verdict.REPRO and vb[k] == Verdict.REPRO for k in shared)
        c_ += sum(va[k] == Verdict.REPRO and vb[k] != Verdict.REPRO for k in shared)

    n = b + c_
    if n == 0:
        return (f"{system_a} vs {system_b}: identical on all {shared_n} paired "
                f"observations (no discordant pairs; p = 1.0)")
    p = _exact_p(b, c_)
    verdict = ("significant at p<0.05" if p < 0.05
               else "NOT significant at p<0.05 — treat as noise")
    over = f" over {pairs} paired run(s)" if pairs > 1 else ""
    return (f"{system_a} vs {system_b}: {b} fixed, {c_} broken, {n} discordant "
            f"of {shared_n} paired observations{over}. Exact McNemar "
            f"p = {p:.5f} ({verdict}).")


def stability() -> str:
    """How much does a single run tell you? Compare repeats of the same system."""
    lines = []
    for s in SYSTEMS:
        runs = load_runs(s)
        if len(runs) < 2:
            continue
        agree = total = 0
        for x, y in pairwise(runs):
            vx = {c["case_id"]: c["verdict"] for c in x["cases"]}
            vy = {c["case_id"]: c["verdict"] for c in y["cases"]}
            shared = [k for k in set(vx) & set(vy)
                      if vx[k] != Verdict.ERROR and vy[k] != Verdict.ERROR]
            agree += sum(vx[k] == vy[k] for k in shared)
            total += len(shared)
        if total:
            lines.append(f"| {LABEL.get(s, s)} | {len(runs)} | "
                         f"{agree}/{total} | {agree / total * 100:.0f}% |")
    if not lines:
        return ("_Only one run per system so far — re-run with `--repeat` to "
                "measure how much a single run is worth._")
    return "\n".join(
        ["| System | Runs | Verdicts agreeing between consecutive runs | Agreement |",
         "|---|---:|---:|---:|", *lines, "",
         "Same system, same cases, independent runs. A rung-to-rung delta "
         "smaller than this disagreement rate is not evidence."])

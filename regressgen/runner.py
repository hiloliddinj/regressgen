"""Run one system over the corpus and score it with the two-sided gate."""

from __future__ import annotations

import json
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path

from . import baseline
from .agent.loop import Variant
from .agent.loop import solve as agent_solve
from .corpus import Case
from .model import MODEL
from .verify import CaseResult, Verdict, verify

RESULTS = Path(__file__).resolve().parent.parent / "results"
RUNS = RESULTS / "runs"
BASELINE = "baseline"
SYSTEMS = [BASELINE] + [v.value for v in Variant]


def _solve(system: str, case: Case) -> tuple[str, float, str | None, list[dict], str]:
    if system == BASELINE:
        src, usd, err = baseline.solve(case)
        return src, usd, err, [], ""
    sol = agent_solve(case, Variant(system))
    return sol.test_source, sol.usd, sol.error, sol.calls, sol.rationale


def run_case(system: str, case: Case) -> CaseResult:
    t0 = time.monotonic()
    try:
        src, usd, err, calls, rationale = _solve(system, case)
    except Exception as e:
        # A transport/API failure is not an agent failure. Scoring it as one
        # would quietly attribute a rate limit to the model's competence.
        return CaseResult(case.id, Verdict.ERROR, -1, -1,
                          f"{type(e).__name__}: {e}", "", "",
                          seconds=time.monotonic() - t0)

    if not src.strip():
        transport = err and err != "no test submitted"
        r = CaseResult(case.id, Verdict.ERROR if transport else Verdict.INVALID,
                       -1, -1, f"no test produced ({err})", "", "")
    else:
        r = verify(case, src)
    r.seconds = round(time.monotonic() - t0, 1)
    r.usd = round(usd, 5)
    r.trajectory = calls          # type: ignore[attr-defined]
    r.rationale = rationale       # type: ignore[attr-defined]
    return r


def next_run_index(system: str) -> int:
    RUNS.mkdir(parents=True, exist_ok=True)
    return 1 + max((int(f.stem.rsplit(".", 1)[-1])
                    for f in RUNS.glob(f"{system}.*.json")), default=0)


def run_system(system: str, cases: list[Case], workers: int = 4) -> dict:
    started = datetime.now(UTC).isoformat(timespec="seconds")
    t0 = time.monotonic()
    with ThreadPoolExecutor(max_workers=workers) as ex:
        results = list(ex.map(lambda c: run_case(system, c), cases))

    counts = Counter(r.verdict for r in results)
    n = len(results)
    errors = counts.get(Verdict.ERROR, 0)
    if errors:
        print(f"  !! {errors} case(s) failed with a harness/API error and are "
              f"EXCLUDED from the rate. Re-run them before quoting this number.",
              flush=True)
    scored = n - errors
    payload = {
        "system": system,
        "model": MODEL,
        "started": started,
        "wall_seconds": round(time.monotonic() - t0, 1),
        "summary": {
            "n": scored,
            "n_attempted": n,
            "errors": errors,
            "repro": counts.get(Verdict.REPRO, 0),
            "repro_rate": round(counts.get(Verdict.REPRO, 0) / scored, 4) if scored else 0.0,
            "verdicts": dict(sorted(counts.items())),
            "usd_total": round(sum(r.usd for r in results), 4),
            "usd_per_case": round(sum(r.usd for r in results) / n, 5) if n else 0.0,
            "seconds_per_case": round(sum(r.seconds for r in results) / n, 1) if n else 0.0,
        },
        "cases": [
            {**asdict(r),
             "trajectory": getattr(r, "trajectory", []),
             "rationale": getattr(r, "rationale", "")}
            for r in results
        ],
    }
    RESULTS.mkdir(exist_ok=True)
    RUNS.mkdir(parents=True, exist_ok=True)
    # Every run is kept. Agent evaluations are noisy enough that a single run is
    # not a measurement — see docs/FINDINGS.md — so the reported figures are
    # means over repeats, and each repeat stays on disk as its own evidence.
    idx = next_run_index(system)
    payload["run_index"] = idx
    (RUNS / f"{system}.{idx}.json").write_text(json.dumps(payload, indent=2))
    (RESULTS / f"{system}.json").write_text(json.dumps(payload, indent=2))
    return payload

"""Did the adversarial critic (v6) catch anything?

Splits the critic's behaviour by whether the test it reviewed was actually
correct. This is the evidence behind FINDINGS §3: a reviewer built from the same
model has the same blind spots, so its objections are uncorrelated with real
errors — it churns correct work and endorses the mistakes.

    uv run python tools/critic_analysis.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from regressgen.agent.loop import _objects  # noqa: E402
from regressgen.runner import RESULTS  # noqa: E402

REPRO = "REPRO"


def main() -> int:
    f = RESULTS / "v6-critic.json"
    if not f.exists():
        print("no v6-critic results; run: uv run regressgen run --system v6-critic")
        return 1
    data = json.loads(f.read_text())

    rows = []
    for c in data["cases"]:
        crit = [t for t in c["trajectory"] if t["tool"] == "critic"]
        text = crit[0]["result"].strip() if crit else ""
        rows.append({
            "id": c["case_id"],
            "correct": c["verdict"] == REPRO,
            "objected": bool(crit) and _objects(text),
            "revised": any(t["tool"] == "revision" for t in c["trajectory"]),
            "text": text,
        })

    if rows and not any("VERDICT:" in r["text"].upper() for r in rows):
        print("WARNING: no case carries a `VERDICT:` line, so this run predates the\n"
              "         critic's output contract. Under the earlier parser anything\n"
              "         that did not literally start with APPROVE counted as an\n"
              "         objection, which inflated the revision count. Re-run v6 for\n"
              "         accurate objection numbers.\n")

    ok = [r for r in rows if r["correct"]]
    bad = [r for r in rows if not r["correct"]]

    print(f"v6 critic behaviour over {len(rows)} cases\n")
    print(f"{'':34s} {'correct tests':>14s} {'incorrect tests':>16s}")
    print(f"{'cases':34s} {len(ok):>14d} {len(bad):>16d}")
    print(f"{'critic objected':34s} {sum(r['objected'] for r in ok):>14d} "
          f"{sum(r['objected'] for r in bad):>16d}")
    print(f"{'critic endorsed':34s} {sum(not r['objected'] for r in ok):>14d} "
          f"{sum(not r['objected'] for r in bad):>16d}")
    print(f"{'revision round triggered':34s} {sum(r['revised'] for r in ok):>14d} "
          f"{sum(r['revised'] for r in bad):>16d}")

    caught = sum(r["objected"] for r in bad)
    print(f"\nreal errors caught      : {caught}/{len(bad)}")
    print(f"correct work sent back  : {sum(r['objected'] for r in ok)}/{len(ok)}")
    if bad:
        print("\n--- what the critic said about each test that was actually wrong ---")
        for r in bad:
            print(f"\n{r['id']}  (critic "
                  f"{'OBJECTED' if r['objected'] else 'ENDORSED'})")
            print("  " + (r["text"][:420].replace("\n", "\n  ") or "(no reply)"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

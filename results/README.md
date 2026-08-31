# Results

Raw output from every evaluation run. These files are the evidence behind every
number in the README, which is regenerated from them by
`tools/update_readme.py` rather than typed by hand.

## What is here

| Path | What it is |
|---|---|
| `<system>.json` | the current run of that system on the full corpus — these are the reported numbers |
| `_exploratory-17case/` | the earlier ladder, run on the 17-case corpus, before it was expanded for statistical power |
| `_archive/` | superseded runs kept as evidence for specific changelog entries |

## Why `_archive/` exists

Two entries in the Improvement Changelog are about bugs found in the evaluation
itself, and each needs its "before" number to be checkable:

- `baseline_truncated-24k.json` — the baseline when its inlined source was
  capped at 24,000 characters, so on 11 of 17 cases it was reading the first
  11% of the file and never reaching the function under discussion.
- `v2-tools_run1.json` — kept alongside the current v2 run.

## Reading a result file

```jsonc
{
  "system": "v4-discipline",
  "model": "claude-sonnet-5",
  "summary": {
    "n": 44,               // cases scored
    "errors": 0,           // harness/API failures, excluded from the rate
    "repro": 38,           // reached REPRO: failed on buggy, passed on fixed
    "repro_rate": 0.8636,
    "verdicts": { },       // full breakdown
    "usd_per_case": 0.23
  },
  "cases": [
    {
      "case_id": "...",
      "verdict": "REPRO",
      "test_source": "...",   // exactly what the agent submitted
      "buggy_output": "...",  // pytest output from the buggy tree
      "fixed_output": "...",  // pytest output from the held-out fixed tree
      "trajectory": [ ]       // every tool call and what it returned
    }
  ]
}
```

Machine-specific paths are redacted to `~` and `<sandbox>` so these files are
portable and diffable across machines.

Render them with:

```bash
uv run regressgen report
uv run python tools/analyze.py
```

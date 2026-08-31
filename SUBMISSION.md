# Submission map

micro1 Frontier Engineering Challenge 2026 — deadline **Mon 31 Aug, 18:00 UTC**.

## The result, in one table

| per run of 44 real bugs | baseline | shipped agent |
|---|---:|---:|
| regression tests that reproduce the bug | 35.3 (80%) | **40.0 (91%)** |
| tests that silently pass on broken code | 1.7 | **0.0** |
| tests that will not import | 1.0 | **0.0** |
| run-to-run verdict agreement | 88% | **95%** |
| cost per test | $0.08 | $0.22 |

Three runs of each, paired exact McNemar: 19 fixed, 5 broken, **p = 0.0066**.
The same comparison from a single run gives p = 0.23.

Total model spend for the whole project, every run included: **$78**.

## The four required deliverables

| # | Required | Where it is |
|---|---|---|
| 1 | Complete solution code + Improvement Changelog | this repo; changelog in [README.md](README.md#improvement-changelog) |
| 2 | Reproduction guide | [REPRODUCTION.md](REPRODUCTION.md) |
| 3 | Solution video (≤ 5 min) | **to record** — shot list in [docs/VIDEO_SCRIPT.md](docs/VIDEO_SCRIPT.md) |
| 4 | Agent trajectories | [`trajectories/confirmatory/`](trajectories/confirmatory/) (89 files) and [`trajectories/exploratory/`](trajectories/exploratory/) (103 files) — one per system × case, each with instructions, every tool call and its real output, retries, the submitted test, and both halves of the gate |

## Rule-book compliance

| Rule | How it is met |
|---|---|
| 02 — what existed before vs. what was added | README, "What existed before, and what is new" |
| 03 — licences respected | [NOTICE.md](NOTICE.md); every vendored tree keeps its upstream licence |
| 04 — consequential actions sandboxed, human approval first | every test runs in a throwaway copy; `regressgen solve` never writes to your repo unless you pass `--out`, and prints a review banner first |
| 05 — qualified human reviewer in the loop | the agent asserts what it *believes* correct behaviour to be; `solve` stops for review. [docs/FINDINGS.md](docs/FINDINGS.md#5-the-challenging-case-when-the-report-cannot-determine-the-answer) shows a real case where that review is the only thing that catches the error |
| 06 — legal and ethical use case | analysing public OSS libraries; no personal data anywhere |
| 07 — data you may share | six permissively-licensed public repos, listed in NOTICE.md |
| 08 — no credentials in the submission | none; auth is the reader's own Claude Code login |
| 09 — every claim tied to evidence | README numbers are generated from `results/` by `tools/update_readme.py`, never typed by hand |
| 10 — judges can run it and reproduce the main result | `uv sync && uv run regressgen validate` needs no API key and no model calls |

## Disclosure of coding-agent use (required)

**Building it.** Written with **Claude Code** (CLI 2.1.227, Opus 5) as the coding
agent, in a single session. Every file in `regressgen/`, `tools/`, `tests/` and
`docs/` was produced that way, under human direction and review.

**The shipped system.** Calls **Claude Sonnet 5** via `claude-agent-sdk` 0.2.148,
authenticating through the local Claude Code login rather than an API key, so a
judge needs no credentials of their own beyond their own login.

**Trajectories.** `trajectories/` contains, for every system and case, the exact
instructions the agent received, every tool call, the real tool output that came
back, the retries that output caused, and both halves of the grading gate.
Untruncated records are in `results/*.json`.

**Where the human decisions were.** Choosing the problem; deciding the two-sided
gate was the right metric; catching that the first corpus was a test
specification rather than a set of bug reports; catching that the baseline was
being fed 11% of the file; deciding that a rung which *lowered* the headline
score was worth keeping because of what it did to silent failures; and deciding
that three verification mechanisms which each felt like progress had to be
removed because the measurements said they did nothing.

## Before submitting

```bash
make check          # lint + 16 tests + link check, no cost
make validate       # re-prove the corpus invariants, no cost, ~15 min
make report         # scoreboard, significance, stability
uv run python tools/update_readme.py   # tables must match results/
uv run python tools/export_trajectories.py
```

- [ ] Record the video — [docs/VIDEO_SCRIPT.md](docs/VIDEO_SCRIPT.md)
- [ ] `make check` clean
- [ ] `make validate` prints `all cases valid`
- [ ] README tables regenerated from `results/` (never hand-edited)
- [ ] Trajectories regenerated after the final run
- [ ] Push to a public repo and confirm a stranger can clone it
      (the clone is ~90 MB; most of it is the vendored corpus)
- [ ] No absolute paths from this machine in committed files
      (`grep -rn "/Users/" --include='*.md' --include='*.py' .`)
- [ ] Submit on HackerEarth before 18:00 UTC Monday

## Note on IP

Per the Hackathon Participation Agreement accepted at registration, micro1 owns
submissions and may use them for AI model training and evaluation. Nothing in
this repository is confidential or employer-owned: every input is public
open-source code or text written for this submission.

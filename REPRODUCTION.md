# Reproduction guide

Written for someone starting from a clean machine with nothing installed but
`git` and a shell.

## 1. Prerequisites

| Thing | Version used | Notes |
|---|---|---|
| `uv` | 0.11.8 | the only thing you must install by hand |
| Python | 3.12.13 | **fetched automatically by `uv`** — do not install it yourself |
| Claude Code CLI | 2.1.227 | provides model access; `claude-agent-sdk` drives it |
| macOS / Linux | macOS 15 (arm64) tested | no Docker required |

Install `uv`:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Install the Claude Code CLI and log in once:

```bash
npm install -g @anthropic-ai/claude-code && claude login
```

Confirm the login works headlessly — this must print `AUTH_OK`:

```bash
claude -p "Reply with exactly: AUTH_OK" --max-turns 1
```

No `ANTHROPIC_API_KEY` is needed. The harness authenticates through the Claude
Code login. If you would rather use an API key, export `ANTHROPIC_API_KEY` and
everything below works unchanged.

## 2. Set up

```bash
git clone <this-repo> && cd micro1
uv sync
```

The clone is about 90 MB. Most of that is `cases/`, which vendors two copies of
each upstream tree (buggy and fixed) so the evaluation runs offline with no
network and no per-case dependency resolution. The trees are committed exactly
as `git archive` produced them, unmodified, so you can diff any case against its
upstream commit.

`uv sync` pins Python 3.12.13 from `.python-version`, installs from `uv.lock`,
and takes about 30 seconds on a warm cache.

There is a `Makefile` with one-line entry points for everything below:

```bash
make help
```

Check the install:

```bash
uv run regressgen list
```

Expect 17 lines, one per case.

## 3. Verify the ground truth before trusting any number

The corpus carries its own proof. This re-runs pytest four times per case and
re-establishes invariants I1–I4 from scratch:

```bash
uv run regressgen validate
```

Expect `all cases valid` after roughly 15 minutes — it runs pytest four times
per case. No model calls, no network, no cost. **If this fails, stop** — every result below is meaningless without it.

## 4. Run the baseline

```bash
uv run regressgen run --system baseline --repeat 3 --workers 4
```

- runtime ≈ 3.5–5 minutes per run, ~13 minutes for three
- cost ≈ $10 for all three (the first run is ~$6, repeats are cheaper because
  the prompts cache)
- expected: **34–36 of 44** per run; our three were 34, 36, 36

## 5. Run the shipped agent

```bash
uv run regressgen run --system v4-discipline --repeat 3 --workers 4
```

- runtime ≈ 10 minutes per run, ~30 minutes for three
- cost ≈ $28 for all three
- expected: **39–41 of 44** per run; our three were 39, 40, 41

Both together are `make headline`.

### Cheaper: a partial run

Every `run` accepts `--limit N` to use only the first N cases. A four-case
baseline-vs-final comparison costs well under a dollar and takes a couple of
minutes:

```bash
uv run regressgen run --system baseline --system v4-discipline --limit 4 --workers 4
uv run regressgen report
```

The headline numbers in the README come from the full corpus; a partial run will
differ, and the significance test will say so.

### What you should see

```
| Baseline (one prompt, no tools) | 35.3/44  (80%) | 77–82% | 3 | 1.7 | $0.078 |
| v4  + right-reason check        | 40.0/44  (91%) | 89–93% | 3 | 0.0 | $0.215 |

baseline vs v4-discipline: 19 fixed, 5 broken, 24 discordant of 132 paired
observations over 3 paired run(s). Exact McNemar p = 0.00661 (significant).
```

Your numbers will differ by a case or two per run — see the stability table,
which reports how much two runs of the same system disagree. The direction and
rough size of the gap should reproduce; an exact match would be suspicious.

## 6. Print the comparison

```bash
uv run regressgen report
```

Renders the scoreboard and the per-case grid from whatever is in `results/`.

## 7. Reproduce the whole changelog

Every intermediate rung, in order:

```bash
uv run regressgen run \
  --system baseline --system v2-tools --system v3-exec \
  --system v4-discipline --system v5-fixprobe --system v6-critic --workers 5
uv run regressgen report
uv run python tools/update_readme.py     # regenerate the README tables
```

### Why `--repeat`

Model calls are not deterministic, and this task is noisy enough that two runs
of the same system on the same cases disagree on a real fraction of individual
verdicts. A single run is therefore not a measurement.

Every `run` accepts `--repeat N`. Each run is stored separately under
`results/runs/<system>.<n>.json`, and `regressgen report` averages over all of
them and shows the observed range:

```bash
uv run regressgen run --system baseline --repeat 3 --workers 4
```

The reported headline figures are means over repeats. Rungs measured only once
are labelled as such in the changelog.

## 8. Check statistical significance

`regressgen report` prints an exact McNemar test for the headline comparison and
for each adjacent rung. Systems run on the same cases, so the comparison is
paired and only the cases where two systems disagree carry information. When
both systems have several runs, runs are paired in order and the discordant
counts pooled — a stratified McNemar.

It also prints a stability table: how often two runs of the *same* system agree.
Read any rung-to-rung delta against that number.

## 9. Regenerate the agent trajectories

```bash
uv run python tools/export_trajectories.py
```

Writes `trajectories/<system>/<case>.md`, one per run, plus an index at
`trajectories/README.md`.

## 10. Run the human-baseline timing exercise (optional)

```bash
uv run python tools/human_timing.py --n 3
```

Presents cases one at a time, times you writing a test for each, and scores your
tests through the same gate the agents face. Not run for the submitted numbers.

## Rebuilding the corpus from scratch (optional)

The mined cases are committed, so this is not needed to reproduce any result.
It is here so you can confirm the corpus was not hand-picked.

```bash
uv run python tools/mine_cases.py --scan 2500 --max-per-repo 9 --since 2020-01-01
uv run python tools/write_reports.py --force
uv run regressgen validate
```

This clones ~150 MB of upstream history and takes 20–30 minutes. Report drafting
costs about $0.40 in model calls. Because it mines by date window, re-running it
later against newer upstream history can yield a *different* set of cases — the
committed corpus is the frozen one all reported numbers refer to.

### What the dollar figures mean

Every cost in this repository is `total_cost_usd` as reported by
`claude-agent-sdk` — the value of the tokens consumed, priced at Anthropic API
list rates. It is a usage measurement, chosen because it is comparable between
systems and reproducible by anyone.

It is not necessarily what you will be charged. Running this through a Claude
Code login draws on that plan's quota; the dollar figure is what the same tokens
would cost through the API. With `ANTHROPIC_API_KEY` set, it is a real bill.

Total for every run behind the reported numbers, including the ones that were
superseded: about $78.

## Determinism, and what it costs

Model calls are not deterministic, so repeated runs vary. Everything around them
is pinned: `uv.lock`, `.python-version`, `PYTHONHASHSEED=0`, `TZ=UTC`, a scrubbed
environment, and `-o addopts=` so no upstream pytest config leaks into the
sandbox.

Expect the headline numbers to move by roughly ±1 case between runs. The
baseline-to-final gap is far larger than that, but a single rung's delta of one
case should not be read as significant. Where the changelog rests on a small
delta, it says so.

## Troubleshooting

**`validate` fails on every case.** Your interpreter is probably not 3.12.
`uv run python -V` should say 3.12.13.

**Runs hang or time out.** Lower `--workers`. Each worker spawns a Claude Code
subprocess and pytest subprocesses; 5 is comfortable on 8 cores.

**`no test submitted` errors.** Usually rate limiting. Re-run — results are
written per system, so completed systems are not lost.

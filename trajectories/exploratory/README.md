# Agent trajectories

Generated from `results/_exploratory-17case/` by `tools/export_trajectories.py`.

> **Note on these files.** The exploratory ladder was run before the trajectory recorder was fixed to store full tool output, so tool responses here are summarised (`"1472 chars"`, `"2 hits"`) rather than verbatim. The tool calls, their arguments, the retries and the submitted test are all complete. Confirmatory trajectories carry the real tool output.

One file per system per case. Each shows the exact instructions the agent was given, every tool call and what the tool answered, the retries those answers caused, the test it submitted, and both halves of the two-sided gate.

**PASS** means the test failed on the buggy tree and passed on the held-out fixed tree.

Tool responses are the real output, truncated to 2,200 characters where long; the untruncated record is in `results/<system>.json` under each case's `trajectory`.

## Where to start

| Read this | Why |
|---|---|
| [`v2-tools/boltons-eb659013.md`](v2-tools/boltons-eb659013.md) | The same case *without* execution feedback — the agent has to reason about what correct behaviour is, and gets it right. |
| [`v3-exec/boltons-eb659013.md`](v3-exec/boltons-eb659013.md) | The same case *with* execution feedback. It calls `run_test`, sees `FAILED`, and stops — with an invented expectation. The clearest illustration of a half-observable verifier. |
| [`v4-discipline/boltons-eb659013.md`](v4-discipline/boltons-eb659013.md) | The recovery: same tools as v3, plus the instruction to check *why* it failed. |
| [`v5-fixprobe/semver-bc41390f.md`](v5-fixprobe/semver-bc41390f.md) | The agent invents a patch that makes its own wrong expectation true, and `try_fix` answers "your test PASSES with this fix". Self-verification confirming an error. |
| [`v6-critic/semver-bc41390f.md`](v6-critic/semver-bc41390f.md) | A fresh-context reviewer reads the same wrong test and approves it. |
| [`baseline/more-itertools-0e6acdf9.md`](baseline/more-itertools-0e6acdf9.md) | What one prompt with no tools produces. |

## Full index

| Case | baseline | v2-tools | v3-exec | v4-discipline | v5-fixprobe | v6-critic |
|---|---|---|---|---|---|---|
| `boltons-c1c25da3` | [wrong_expectation](baseline/boltons-c1c25da3.md) | [**PASS**](v2-tools/boltons-c1c25da3.md) | [**PASS**](v3-exec/boltons-c1c25da3.md) | [**PASS**](v4-discipline/boltons-c1c25da3.md) | [**PASS**](v5-fixprobe/boltons-c1c25da3.md) | [**PASS**](v6-critic/boltons-c1c25da3.md) |
| `boltons-eb659013` | [wrong_expectation](baseline/boltons-eb659013.md) | [**PASS**](v2-tools/boltons-eb659013.md) | [wrong_expectation](v3-exec/boltons-eb659013.md) | [**PASS**](v4-discipline/boltons-eb659013.md) | [**PASS**](v5-fixprobe/boltons-eb659013.md) | [**PASS**](v6-critic/boltons-eb659013.md) |
| `boltons-f1034b07` | [**PASS**](baseline/boltons-f1034b07.md) | [**PASS**](v2-tools/boltons-f1034b07.md) | [**PASS**](v3-exec/boltons-f1034b07.md) | [**PASS**](v4-discipline/boltons-f1034b07.md) | [**PASS**](v5-fixprobe/boltons-f1034b07.md) | [**PASS**](v6-critic/boltons-f1034b07.md) |
| `cachetools-57d2e481` | [vacuous](baseline/cachetools-57d2e481.md) | [vacuous](v2-tools/cachetools-57d2e481.md) | [**PASS**](v3-exec/cachetools-57d2e481.md) | [**PASS**](v4-discipline/cachetools-57d2e481.md) | [**PASS**](v5-fixprobe/cachetools-57d2e481.md) | [**PASS**](v6-critic/cachetools-57d2e481.md) |
| `cachetools-bb4b37cf` | [wrong_expectation](baseline/cachetools-bb4b37cf.md) | [**PASS**](v2-tools/cachetools-bb4b37cf.md) | [**PASS**](v3-exec/cachetools-bb4b37cf.md) | [**PASS**](v4-discipline/cachetools-bb4b37cf.md) | [**PASS**](v5-fixprobe/cachetools-bb4b37cf.md) | [**PASS**](v6-critic/cachetools-bb4b37cf.md) |
| `cachetools-c0fdf6ab` | [**PASS**](baseline/cachetools-c0fdf6ab.md) | [**PASS**](v2-tools/cachetools-c0fdf6ab.md) | [**PASS**](v3-exec/cachetools-c0fdf6ab.md) | [**PASS**](v4-discipline/cachetools-c0fdf6ab.md) | [**PASS**](v5-fixprobe/cachetools-c0fdf6ab.md) | [**PASS**](v6-critic/cachetools-c0fdf6ab.md) |
| `more-itertools-0e6acdf9` | [vacuous](baseline/more-itertools-0e6acdf9.md) | [**PASS**](v2-tools/more-itertools-0e6acdf9.md) | [**PASS**](v3-exec/more-itertools-0e6acdf9.md) | [**PASS**](v4-discipline/more-itertools-0e6acdf9.md) | [**PASS**](v5-fixprobe/more-itertools-0e6acdf9.md) | [**PASS**](v6-critic/more-itertools-0e6acdf9.md) |
| `more-itertools-958990e2` | [**PASS**](baseline/more-itertools-958990e2.md) | [**PASS**](v2-tools/more-itertools-958990e2.md) | [**PASS**](v3-exec/more-itertools-958990e2.md) | [**PASS**](v4-discipline/more-itertools-958990e2.md) | [**PASS**](v5-fixprobe/more-itertools-958990e2.md) | [**PASS**](v6-critic/more-itertools-958990e2.md) |
| `more-itertools-d992be0d` | [**PASS**](baseline/more-itertools-d992be0d.md) | [**PASS**](v2-tools/more-itertools-d992be0d.md) | [**PASS**](v3-exec/more-itertools-d992be0d.md) | [**PASS**](v4-discipline/more-itertools-d992be0d.md) | [**PASS**](v5-fixprobe/more-itertools-d992be0d.md) | [**PASS**](v6-critic/more-itertools-d992be0d.md) |
| `packaging-524b701c` | [**PASS**](baseline/packaging-524b701c.md) | [**PASS**](v2-tools/packaging-524b701c.md) | [**PASS**](v3-exec/packaging-524b701c.md) | [**PASS**](v4-discipline/packaging-524b701c.md) | [**PASS**](v5-fixprobe/packaging-524b701c.md) | [**PASS**](v6-critic/packaging-524b701c.md) |
| `packaging-a716c52b` | [wrong_expectation](baseline/packaging-a716c52b.md) | [**PASS**](v2-tools/packaging-a716c52b.md) | [**PASS**](v3-exec/packaging-a716c52b.md) | [**PASS**](v4-discipline/packaging-a716c52b.md) | [**PASS**](v5-fixprobe/packaging-a716c52b.md) | [**PASS**](v6-critic/packaging-a716c52b.md) |
| `packaging-c52d2b30` | [**PASS**](baseline/packaging-c52d2b30.md) | [**PASS**](v2-tools/packaging-c52d2b30.md) | [**PASS**](v3-exec/packaging-c52d2b30.md) | [**PASS**](v4-discipline/packaging-c52d2b30.md) | [**PASS**](v5-fixprobe/packaging-c52d2b30.md) | [**PASS**](v6-critic/packaging-c52d2b30.md) |
| `semver-4b03f867` | [invalid](baseline/semver-4b03f867.md) | [**PASS**](v2-tools/semver-4b03f867.md) | [**PASS**](v3-exec/semver-4b03f867.md) | [**PASS**](v4-discipline/semver-4b03f867.md) | [**PASS**](v5-fixprobe/semver-4b03f867.md) | [**PASS**](v6-critic/semver-4b03f867.md) |
| `semver-bc41390f` | [wrong_expectation](baseline/semver-bc41390f.md) | [wrong_expectation](v2-tools/semver-bc41390f.md) | [wrong_expectation](v3-exec/semver-bc41390f.md) | [wrong_expectation](v4-discipline/semver-bc41390f.md) | [wrong_expectation](v5-fixprobe/semver-bc41390f.md) | [wrong_expectation](v6-critic/semver-bc41390f.md) |
| `tabulate-5373ebfa` | [**PASS**](baseline/tabulate-5373ebfa.md) | [**PASS**](v2-tools/tabulate-5373ebfa.md) | [**PASS**](v3-exec/tabulate-5373ebfa.md) | [**PASS**](v4-discipline/tabulate-5373ebfa.md) | [**PASS**](v5-fixprobe/tabulate-5373ebfa.md) | [**PASS**](v6-critic/tabulate-5373ebfa.md) |
| `tabulate-87a9a4e0` | [**PASS**](baseline/tabulate-87a9a4e0.md) | [**PASS**](v2-tools/tabulate-87a9a4e0.md) | [wrong_expectation](v3-exec/tabulate-87a9a4e0.md) | [**PASS**](v4-discipline/tabulate-87a9a4e0.md) | [**PASS**](v5-fixprobe/tabulate-87a9a4e0.md) | [**PASS**](v6-critic/tabulate-87a9a4e0.md) |
| `tabulate-d29909b4` | [**PASS**](baseline/tabulate-d29909b4.md) | [wrong_expectation](v2-tools/tabulate-d29909b4.md) | [wrong_expectation](v3-exec/tabulate-d29909b4.md) | [wrong_expectation](v4-discipline/tabulate-d29909b4.md) | [wrong_expectation](v5-fixprobe/tabulate-d29909b4.md) | [wrong_expectation](v6-critic/tabulate-d29909b4.md) |

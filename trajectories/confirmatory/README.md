# Agent trajectories

Generated from `results/` by `tools/export_trajectories.py`.

One file per system per case. Each shows the exact instructions the agent was given, every tool call and what the tool answered, the retries those answers caused, the test it submitted, and both halves of the two-sided gate.

**PASS** means the test failed on the buggy tree and passed on the held-out fixed tree.

Tool responses are the real output, truncated to 2,200 characters where long; the untruncated record is in `results/<system>.json` under each case's `trajectory`.

## Where to start

| Read this | Why |
|---|---|
| [`baseline/more-itertools-0e6acdf9.md`](baseline/more-itertools-0e6acdf9.md) | What one prompt with no tools produces, given the whole source file. |
| [`v4-discipline/more-itertools-0e6acdf9.md`](v4-discipline/more-itertools-0e6acdf9.md) | The shipped agent on the same case: search, targeted reads, run the test, check the failure is the right failure. |
| [`v4-discipline/semver-bc41390f.md`](v4-discipline/semver-bc41390f.md) | The case no system solves. The agent's reasoning is sound and its answer is defensible — the report simply does not contain the maintainer's design decision. |

## Full index

| Case | baseline | v4-discipline |
|---|---|---|
| `attrs-09161fc9` | [**PASS**](baseline/attrs-09161fc9.md) | [**PASS**](v4-discipline/attrs-09161fc9.md) |
| `attrs-6fda0a4e` | [**PASS**](baseline/attrs-6fda0a4e.md) | [**PASS**](v4-discipline/attrs-6fda0a4e.md) |
| `attrs-937b1e23` | [**PASS**](baseline/attrs-937b1e23.md) | [**PASS**](v4-discipline/attrs-937b1e23.md) |
| `attrs-97f8d175` | [**PASS**](baseline/attrs-97f8d175.md) | [**PASS**](v4-discipline/attrs-97f8d175.md) |
| `attrs-a71fbbad` | [wrong_expectation](baseline/attrs-a71fbbad.md) | [**PASS**](v4-discipline/attrs-a71fbbad.md) |
| `attrs-af9c5109` | [**PASS**](baseline/attrs-af9c5109.md) | [**PASS**](v4-discipline/attrs-af9c5109.md) |
| `attrs-c9150d27` | [wrong_expectation](baseline/attrs-c9150d27.md) | [**PASS**](v4-discipline/attrs-c9150d27.md) |
| `attrs-ce89f5d1` | [**PASS**](baseline/attrs-ce89f5d1.md) | [**PASS**](v4-discipline/attrs-ce89f5d1.md) |
| `attrs-f9ff9135` | [vacuous](baseline/attrs-f9ff9135.md) | [wrong_expectation](v4-discipline/attrs-f9ff9135.md) |
| `boltons-1e61524a` | [**PASS**](baseline/boltons-1e61524a.md) | [**PASS**](v4-discipline/boltons-1e61524a.md) |
| `boltons-55dfe507` | [**PASS**](baseline/boltons-55dfe507.md) | [**PASS**](v4-discipline/boltons-55dfe507.md) |
| `boltons-609cabe9` | [**PASS**](baseline/boltons-609cabe9.md) | [**PASS**](v4-discipline/boltons-609cabe9.md) |
| `boltons-c1c25da3` | [invalid](baseline/boltons-c1c25da3.md) | [**PASS**](v4-discipline/boltons-c1c25da3.md) |
| `boltons-d0a284fc` | [**PASS**](baseline/boltons-d0a284fc.md) | [**PASS**](v4-discipline/boltons-d0a284fc.md) |
| `boltons-ead236e2` | [**PASS**](baseline/boltons-ead236e2.md) | [**PASS**](v4-discipline/boltons-ead236e2.md) |
| `boltons-eb659013` | [**PASS**](baseline/boltons-eb659013.md) | [**PASS**](v4-discipline/boltons-eb659013.md) |
| `boltons-ebc7a8f7` | [**PASS**](baseline/boltons-ebc7a8f7.md) | [**PASS**](v4-discipline/boltons-ebc7a8f7.md) |
| `boltons-f1034b07` | [**PASS**](baseline/boltons-f1034b07.md) | [**PASS**](v4-discipline/boltons-f1034b07.md) |
| `cachetools-57d2e481` | [invalid](baseline/cachetools-57d2e481.md) | [**PASS**](v4-discipline/cachetools-57d2e481.md) |
| `cachetools-bb4b37cf` | [**PASS**](baseline/cachetools-bb4b37cf.md) | [**PASS**](v4-discipline/cachetools-bb4b37cf.md) |
| `cachetools-c0fdf6ab` | [**PASS**](baseline/cachetools-c0fdf6ab.md) | [**PASS**](v4-discipline/cachetools-c0fdf6ab.md) |
| `cachetools-d3598664` | [**PASS**](baseline/cachetools-d3598664.md) | [**PASS**](v4-discipline/cachetools-d3598664.md) |
| `more-itertools-073d2342` | [**PASS**](baseline/more-itertools-073d2342.md) | [**PASS**](v4-discipline/more-itertools-073d2342.md) |
| `more-itertools-0e6acdf9` | [**PASS**](baseline/more-itertools-0e6acdf9.md) | [**PASS**](v4-discipline/more-itertools-0e6acdf9.md) |
| `more-itertools-428a0a2c` | [**PASS**](baseline/more-itertools-428a0a2c.md) | [**PASS**](v4-discipline/more-itertools-428a0a2c.md) |
| `more-itertools-958990e2` | [**PASS**](baseline/more-itertools-958990e2.md) | [**PASS**](v4-discipline/more-itertools-958990e2.md) |
| `more-itertools-b0aa91ef` | [**PASS**](baseline/more-itertools-b0aa91ef.md) | [**PASS**](v4-discipline/more-itertools-b0aa91ef.md) |
| `more-itertools-d64a7d69` | [**PASS**](baseline/more-itertools-d64a7d69.md) | [**PASS**](v4-discipline/more-itertools-d64a7d69.md) |
| `more-itertools-d992be0d` | [**PASS**](baseline/more-itertools-d992be0d.md) | [**PASS**](v4-discipline/more-itertools-d992be0d.md) |
| `more-itertools-edb3346f` | [**PASS**](baseline/more-itertools-edb3346f.md) | [**PASS**](v4-discipline/more-itertools-edb3346f.md) |
| `more-itertools-f51a53bf` | [**PASS**](baseline/more-itertools-f51a53bf.md) | [**PASS**](v4-discipline/more-itertools-f51a53bf.md) |
| `packaging-524b701c` | [**PASS**](baseline/packaging-524b701c.md) | [**PASS**](v4-discipline/packaging-524b701c.md) |
| `packaging-a716c52b` | [**PASS**](baseline/packaging-a716c52b.md) | [**PASS**](v4-discipline/packaging-a716c52b.md) |
| `packaging-c52d2b30` | [**PASS**](baseline/packaging-c52d2b30.md) | [**PASS**](v4-discipline/packaging-c52d2b30.md) |
| `semver-4b03f867` | [**PASS**](baseline/semver-4b03f867.md) | [**PASS**](v4-discipline/semver-4b03f867.md) |
| `semver-bc41390f` | [wrong_expectation](baseline/semver-bc41390f.md) | [wrong_expectation](v4-discipline/semver-bc41390f.md) |
| `tabulate-0655054b` | [**PASS**](baseline/tabulate-0655054b.md) | [**PASS**](v4-discipline/tabulate-0655054b.md) |
| `tabulate-0978de5b` | [wrong_expectation](baseline/tabulate-0978de5b.md) | [**PASS**](v4-discipline/tabulate-0978de5b.md) |
| `tabulate-20c6370d` | [wrong_expectation](baseline/tabulate-20c6370d.md) | [**PASS**](v4-discipline/tabulate-20c6370d.md) |
| `tabulate-5373ebfa` | [**PASS**](baseline/tabulate-5373ebfa.md) | [**PASS**](v4-discipline/tabulate-5373ebfa.md) |
| `tabulate-6c48142c` | [**PASS**](baseline/tabulate-6c48142c.md) | [**PASS**](v4-discipline/tabulate-6c48142c.md) |
| `tabulate-87a9a4e0` | [**PASS**](baseline/tabulate-87a9a4e0.md) | [**PASS**](v4-discipline/tabulate-87a9a4e0.md) |
| `tabulate-b1ed1fda` | [**PASS**](baseline/tabulate-b1ed1fda.md) | [**PASS**](v4-discipline/tabulate-b1ed1fda.md) |
| `tabulate-d29909b4` | [**PASS**](baseline/tabulate-d29909b4.md) | [wrong_expectation](v4-discipline/tabulate-d29909b4.md) |

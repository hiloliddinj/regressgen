# The corpus

Every case is a real bug that a real maintainer really fixed in a real
open-source Python library. Nothing here is invented, and no case was hand-picked
for how well the agent does on it — the mining script keeps whatever survives its
checks, and the checks were written before any agent was run. The exact roster is
generated from the committed cases:

## Where the cases come from

`tools/mine_cases.py` clones permissively-licensed, pure-Python,
dependency-light libraries and walks their commit history looking for fix-shaped
commits that change both source and tests. Sixteen libraries are attempted; the
ones that contribute cases are those whose suites run clean on the pinned
interpreter:

<!-- BEGIN:repos -->
| Library | Cases | Upstream | Licence |
|---|---:|---|---|
| attrs | 9 | github.com/python-attrs/attrs | MIT |
| boltons | 9 | github.com/mahmoud/boltons | BSD-3-Clause |
| cachetools | 4 | github.com/tkem/cachetools | MIT |
| more-itertools | 9 | github.com/more-itertools/more-itertools | MIT |
| packaging | 3 | github.com/pypa/packaging | Apache-2.0 OR BSD-2-Clause |
| semver | 2 | github.com/python-semver/python-semver | BSD-3-Clause |
| tabulate | 8 | github.com/astanin/python-tabulate | MIT |
| **total** | **44** | | |
<!-- END:repos -->

Commits are filtered to a focused source change (≤ 60 changed lines, ≤ 3 files)
that arrives with a new test, and only commits since the cutoff are considered so
the code runs on a modern interpreter. The committed corpus was produced by:

```bash
uv run python tools/mine_cases.py --scan 2500 --max-per-repo 9 --since 2020-01-01
```

Re-running against newer upstream history can yield a different set — the
committed cases are the frozen ones every reported number refers to.

For a commit `C` with parent `P`, the case is assembled as:

- `buggy/` — the whole tree at `P`
- `fixed/` — the source at `C`, with the tests from `P`
- `oracle/` — the test files as they exist at `C`

Swapping the parent's tests into `fixed/` is the important step: it means the
regression test the maintainer wrote lives **only** in `oracle/`, and `oracle/`
is never placed anywhere the agent can reach.

## What makes a case valid

A candidate is discarded unless all four invariants hold:

| | existing suite | oracle test |
|---|---|---|
| `buggy/` | **I1** green | **I3** fails |
| `fixed/` | **I2** green | **I4** passes |

I1 and I2 say the bug ships undetected and the fix breaks nothing. This is the
property that makes the task hard and honest: the existing suite is green on both
sides, so an agent cannot find the bug by running the tests that are already
there. It has to construct a new input that exposes it.

I3 and I4 say a regression test for this bug is actually possible, and that the
real fix satisfies it. Without I4 a case could be unsatisfiable; without I3 there
would be nothing to catch.

### One thing this got wrong, and what it cost

The oracle must run at the path it occupied upstream. Some maintainer tests
assert on their own module name — attrs has
`repr(C(1)).startswith("<tests.test_make.C object at 0x")` — and others pickle a
class defined in the test module. An early version of `validate` copied the
oracle to a synthetic filename, which broke both and reported three perfectly
good attrs cases as invalid.

The miner had always run the oracle at its real path, so the two disagreed. The
lesson generalises past this project: when a checker and the thing it checks are
built separately, they will drift, and the drift shows up as *false alarms about
your data* rather than as an obvious bug. `tests/test_corpus.py` now pins the
behaviour.

Re-prove all four at any time:

```bash
uv run regressgen validate
```

That command is the corpus's own test suite. It should print `all cases valid`.

## What gets excluded, and why

A library contributes nothing if its test suite does not run green on the pinned
interpreter. Several were attempted and dropped for exactly that reason:

| Attempted | Why it contributes nothing |
|---|---|
| `humanize` | needs a build-time generated `humanize._version` |
| `jmespath` | its era predates Python 3.12; uses `assertRaisesRegexp`, removed in 3.12 |
| `click` | suite hangs without a tty — the pager and prompt tests wait on stdin, so every candidate hits the timeout |

This is recorded rather than hidden. The miner prints a reject reason for every
candidate it discards, and the roster above is the residue of those logs. The
miner also carries a circuit breaker: four consecutive `I1` failures and it
abandons the library, because a suite that cannot run here will not start
running at an older commit — `click` alone would otherwise have cost an hour of
timeouts to learn nothing.

Cases whose existing suite is slow are also excluded, because `try_fix` re-runs
that suite on every probe and a slow case would dominate an evaluation run.
`tools/time_cases.py` measures this; anything excluded is moved to
`cases_excluded/` rather than deleted, so the decision is inspectable.

## The bug reports

Each case has a `report.md` written in the voice of a user filing an issue. The
reports are drafted by a model from the *oracle test* — never from the fix diff —
and then passed through a mechanical leak gate (`leaks()` in
`tools/write_reports.py`) that rejects any draft which:

- names a private identifier that appears in the fix diff,
- names a source file touched by the fix,
- uses a dunder in prose (as opposed to inside a pasted traceback),
- or explains the cause ("because...", "fails to check...").

A rejected draft is regenerated with the specific violation fed back, up to three
times. Every report in the corpus passed this gate, and each was read by a human
before the corpus was frozen.

This gate exists because the first version of the corpus did not have one, and it
mattered enormously — see the Improvement Changelog in the README, iteration 0.

`report_v1_precise.md` is kept alongside each case: the original, over-specified
draft, preserved as evidence for that changelog entry.

### Why generated reports rather than the real GitHub threads

Scraping the original issue would be more authentic, and it was considered. It
was not done, for two reasons. Real threads are wildly uneven — some are a single
sentence, some are forty comments of diagnosis that hand over the fix — so the
task difficulty would vary for reasons unrelated to the bug. And many of these
commits cite no issue at all.

The trade-off is real and you should be able to check it. Where a commit names an
issue, `meta.json` carries `upstream_refs`, and every case carries
`fix_commit_url`:

```bash
uv run python -c "import json; m=json.load(open('cases/cachetools-d3598664/meta.json')); print(m['upstream_refs'], m['fix_commit_url'])"
```

21 of the 44 cases link to an upstream thread. Open one and compare it against
our `report.md`.

## Every case

<!-- BEGIN:cases -->
| Case | Fix commit subject | Src churn |
|---|---|---:|
| `attrs-09161fc9` | Fix crash when __pre_init__, kw_only, and defaults come together (#1319) | 12 |
| `attrs-6fda0a4e` | Make Converter a kind of adapter, fix converters.pipe (#1328) | 43 |
| `attrs-937b1e23` | Fixes issue #1427 (#1428) | 12 |
| `attrs-97f8d175` | Fix ClassVar forward reference detection (#1593) | 1 |
| `attrs-a71fbbad` | Fix @frozen exceptions to allow __traceback__ to be set. (#1081) | 35 |
| `attrs-af9c5109` | Fix validators.disabled() to save/restore state on nesting (#1513) | 4 |
| `attrs-c9150d27` | Fix backward compatibility with pickles before v22.2.0 (#1085) | 12 |
| `attrs-ce89f5d1` | Fix message passing in frozen errors | 8 |
| `attrs-f9ff9135` | Fix test_ne in test_cmp.py for Python 3.13 (#1255) | 1 |
| `boltons-1e61524a` | fix(strutils): stop singularize() mangling words ending in 'ss' | 7 |
| `boltons-55dfe507` | fix(fileutils): accept os.PathLike in AtomicSaver | 5 |
| `boltons-609cabe9` | fix IndexedSet slicing after removals: keep iter_slice bounds in apparent  | 14 |
| `boltons-c1c25da3` | Fix off-by-one in Bits length check | 2 |
| `boltons-d0a284fc` | fix IndexedSet out-of-range negative indexing wrapping around (x[-n-k], po | 10 |
| `boltons-ead236e2` | fix: backoff_iter with factor=1.0 and no count raised ZeroDivisionError | 10 |
| `boltons-eb659013` | tableutils: fix Table.to_text crashes on degenerate tables and headers | 17 |
| `boltons-ebc7a8f7` | Fix copy.copy/copy.deepcopy collapsing OrderedMultiDict values | 8 |
| `boltons-f1034b07` | jsonutils: fix JSONLIterator nontermination at EOF and negative rel_seek | 12 |
| `cachetools-57d2e481` | Fix #387: Handle obj=None case for inspection in _DescriptorBase. | 7 |
| `cachetools-bb4b37cf` | Fix #292, fix #205, fix #103: TTLCache.expire() returns iterable of expire | 12 |
| `cachetools-c0fdf6ab` | Fix TLRUCache silently keeping stale value on expired overwrite | 18 |
| `cachetools-d3598664` | Fix #256: Deprecate @mru_cache decorator. | 4 |
| `more-itertools-073d2342` | Fix support for iterators using "repeat" | 4 |
| `more-itertools-0e6acdf9` | Raise a clear ValueError for negative n in chunked() | 3 |
| `more-itertools-428a0a2c` | Issue 1098: Add synchronized decorator | 30 |
| `more-itertools-958990e2` | Raise for negative slice sizes in sliced() | 3 |
| `more-itertools-b0aa91ef` | Fix random_product() as well | 2 |
| `more-itertools-d64a7d69` | Raise for negative tail sizes on sized iterables | 3 |
| `more-itertools-d992be0d` | Fix stability in running_min and running_max | 50 |
| `more-itertools-edb3346f` | Fix empty ranges in numeric_range.__reversed__ | 10 |
| `more-itertools-f51a53bf` | fix: handle empty interleave_evenly input | 3 |
| `packaging-524b701c` | parse_{sdist,wheel}_filename: don't raise InvalidVersion (#721) | 18 |
| `packaging-a716c52b` | Fix uninformative error message (#830) | 6 |
| `packaging-c52d2b30` | Fix specifier matching when it is long and has an epoch (#712) | 31 |
| `semver-4b03f867` | Fix #426: call subclass when deriving from Version | 6 |
| `semver-bc41390f` | Fix comparison with subclasses | 2 |
| `tabulate-0655054b` | Fix support for separating lines | 9 |
| `tabulate-0978de5b` | Fix separating line with dataclasses | 7 |
| `tabulate-20c6370d` | fix #180 - exception on empty data with maxcolwidths option | 11 |
| `tabulate-5373ebfa` | fix #176 - implement Decimal fixed-point support | 3 |
| `tabulate-6c48142c` | fix #190 - preserve line breaks when using maxcolwidths | 6 |
| `tabulate-87a9a4e0` | fix #365 - added a regression test and a fix based on pull request #393 | 2 |
| `tabulate-b1ed1fda` | Fix support for separating lines | 13 |
| `tabulate-d29909b4` | Fix handling "True"/"False" bool str and None | 8 |
<!-- END:cases -->

## Provenance

Every case carries `meta.json` with the upstream URL, the fix commit SHA, the
parent SHA, the maintainer's subject line, and the files touched. Any claim in
this project can be traced back to a specific upstream commit:

```bash
cat cases/more-itertools-0e6acdf9/meta.json
```

## Licensing

Case directories vendor source from the libraries above under their original
licences, unmodified except for the tree surgery described here. Each case's
licence is recorded in `meta.json`, and each upstream `LICENSE` file travels with
the vendored tree. The libraries are used here as test subjects for research
evaluation; no library is redistributed as a package.

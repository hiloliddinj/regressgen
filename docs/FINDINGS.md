# Findings

Detail behind the Improvement Changelog. Every claim here points at a file in
`results/` or `cases/` you can open yourself.

**Which numbers come from where.** Findings §1–§3 are from the *exploratory*
stage: the full six-rung ladder, run once each on a 17-case corpus, stored in
`results/_exploratory-17case/`. They are the hypotheses this project generated,
and each is supported by a specific mechanism visible in a trajectory, not by a
score alone — which matters, because §4 shows how little a single run's score is
worth. The *confirmatory* stage re-ran only the headline pair, three times each,
on the full 44-case corpus; that is the number in the README's headline table.

---

## 1. A verifier that checks half your goal points the agent somewhere else

**The rung that went backwards.** Adding `run_test` — letting the agent run its
candidate against the buggy code and read real pytest output — *lowered* the
score, 14/17 to 13/17. One case won, two lost.

That is not the expected direction. Execution feedback is supposed to be the
most valuable thing you can hand a coding agent.

**What actually happened.** The success criterion has two halves: fail on buggy,
pass on fixed. The agent can only observe the first. `run_test` therefore
certifies exactly half the goal, and the agent optimises against the half it can
see — it stops as soon as the bar goes red.

`boltons-eb659013` shows the mechanism cleanly:

- **v2 (no execution) — REPRO.** With no way to check, the agent had to reason
  about what `Table.to_text()` *should* produce, and asserted only what the
  report justified.
- **v3 (execution) — WRONG_EXPECTATION.** It wrote a test, called `run_test`,
  saw `FAILED (exit 1)`, called it once more, and submitted. The test asserts
  `'None' in text`, an invented detail about how missing cells render. The real
  fix renders `'1'` and no `None`, so it fails on the fixed tree too.

```
assert 'None' in text
E   AssertionError: assert 'None' in '1'
```

The tool said FAILED. The agent read that as *done*. A red bar looks identical
whether you found the bug or misspelled an attribute.

**But the headline number hides something better.** Look at the silent-failure
column, not the repro rate:

| | repro | silent failures (green on buggy code) |
|---|---:|---:|
| v2 + navigation | 14/17 | 1 |
| v3 + execution | 13/17 | **0** |

Execution did not create errors. It *converted* them — from silent to loud.
A VACUOUS test passes, so a developer commits it believing they have coverage
they do not have. A WRONG_EXPECTATION test fails in front of them. Execution
traded one point of repro rate for the elimination of the only failure mode that
ships undetected, and no later rung ever reintroduced a silent failure.

If we had scored only the headline metric we would have reverted v3 as a
regression, and lost the thing it was actually good at.

**What we did about it.** Two rungs, in order:

- *v4* tells the agent that a failure caused by a wrong name, a wrong signature
  or an invented detail is worth nothing, and to read the failure before
  believing it. This recovered **exactly the two cases v3 broke** (15/17).
- *v5* gives it `try_fix`: patch the bug yourself in a scratch copy, run your
  own test against the patched code, and see whether it goes green — a proxy for
  the hidden half of the gate, reconstructed from the half the agent may see.
  This is the obvious repair, and it did not work. §2 explains why.

**The generalisable lesson.** Before wiring a verifier into an agent loop, ask
what fraction of your success criterion it certifies. A partial verifier is not
a weak verifier; it is an optimisation target aimed slightly away from your goal,
and it can be worse than none, because the agent stops reasoning the moment the
signal turns green. The repair is not to remove it — it is to either complete
the signal (`try_fix`) or tell the agent explicitly what the signal cannot see
(v4). And measure the failure *modes*, not just the score, or you will throw away
a change that helped.

## 2. Self-verification is a mirror, not an oracle

**The experiment.** v3 taught us the agent could only observe half the gate. The
obvious repair: let it reconstruct the other half. `try_fix` lets the agent patch
the bug itself in a scratch copy and run its own test against the patched code.
If the test goes green, both halves are satisfied — apparently.

It was the most involved tool in the project and the one we had most confidence
in.

**The result.** 15/17 — *identical to v4*. Not one case changed verdict. Cost per
case rose 59% ($0.230 → $0.366) and wall time 43%.

**And it was genuinely used**, so this is not a story about an ignored tool:

| | |
|---|---|
| cases where `try_fix` was called | 17 / 17 |
| total probes | 30 |
| probes reporting "your test STILL FAILS" | 10 |

The agent probed, was told it was wrong a third of the time, and iterated. The
machinery worked exactly as designed. It just did not help.

**Why it did not help — and this is the part worth keeping.** Look at the two
cases v5 still got wrong. In both, the agent invented a patch, and the probe
answered:

```
your test PASSES with this fix
```

Both tests fail against the *real* fix.

The agent wrote a patch that made its own expectation true, then read the green
bar as confirmation. On `semver-bc41390f` it patched out the `TypeError` its test
demanded; the maintainer deliberately kept that `TypeError`. On
`tabulate-d29909b4` it rewrote the cell-casting branch to match its guess.

`try_fix` does not verify correctness. It verifies that the agent's test and the
agent's patch agree with each other — and they were written by the same
reasoning, from the same misunderstanding, minutes apart. When the underlying
model of correct behaviour is wrong, the probe does not catch it. It *confirms*
it, and hands back a stronger signal than the agent had before.

**The generalisable lesson**, which subsumes §1: an agent's self-verification can
only ever check consistency with its own model of correctness. When that model is
right, verification is redundant — v4 already had those cases. When it is wrong,
verification is actively harmful, because it converts a guess into a
justified-feeling conclusion without touching accuracy. Adding verification steps
raises confidence monotonically; it does not raise correctness monotonically. The
only thing that breaks the loop is a signal from outside the agent's own
reasoning — held-out ground truth, a genuinely independent reviewer, or a human.

**Decision: removed from the default path.** `try_fix` is retained as an opt-in
tool, because in `regressgen solve` — where there is no held-out tree and a human
is reading the output — a stated fix hypothesis the reviewer can check is worth
something even when it does not improve the test. It is not worth 59% of the
budget in batch evaluation.

**This is what motivated v6**: if self-verification cannot escape the agent's own
frame, does a reviewer with a fresh context escape it?

---

## 3. An independent reviewer that shares your priors is not independent

**The experiment.** §2 ended with a question: if the agent cannot escape its own
frame by self-verifying, does a reviewer with a *fresh context* escape it? v6
adds one — a separate agent, its own context, read-only access to the buggy tree,
asked exactly one question: *once this bug is fixed, will this test pass?* If it
objects, the original agent gets one revision round.

This is the orchestration answer, and the one we expected to work.

**The result.** 15/17 — and not merely the same total as v4, the same verdict on
**every single case**. Zero differences. For:

| | repro | $/case | s/case |
|---|---:|---:|---:|
| v4 (instruction only) | 15/17 | $0.230 | 53 |
| v5 (+ self-fix probe) | 15/17 | $0.366 | 76 |
| v6 (+ independent critic) | 15/17 | **$0.534** | **142** |

2.3× the cost and 2.7× the wall time of v4, for an identical answer on all 17
cases.

**It was not idle.** The critic ran on 17 of 17 cases and produced substantive
analysis on every one — reading source, tracing control flow, citing line
numbers.

**Where it actually landed.** Split by whether the test was right:

| | correct tests (15) | incorrect tests (2) |
|---|---:|---:|
| critic endorsed the test | 14 | **2** |
| critic objected | 1 | **0** |
| real errors caught | — | **0 / 2** |

It endorsed both wrong tests and caught neither.

`semver-bc41390f` is the one to read. The critic did not skim it. It went and
traced the comparison logic, found the actual mechanism, and wrote it down
correctly:

> "I traced `Version.compare()` [...] the bug is that it does `cls = type(self)`
> and then checks `elif not isinstance(other, cls)`, so
> `MyVersion(...).compare(Version(...))` fails because a `Version` instance isn't
> an instance of the subclass"

That analysis is right. Its verdict was `APPROVE`, on a test that fails against
the real fix. Understanding the bug correctly did not stop it from endorsing the
wrong expectation about what the fix *should* do, because that expectation is a
design decision and the critic makes the same guess the first agent made.

On `tabulate-d29909b4` it cross-referenced an analogous already-passing test to
confirm the expected table layout, and concluded the wrong output was right —
with a citation.

**An engineering flaw, fixed, that changed nothing.** The first version of this
experiment asked the critic to reply with a bare `APPROVE` token and treated
anything else as an objection. The critic frequently wrote its analysis without
emitting the token, so approvals were misread as objections and triggered
pointless revision rounds — 8 of them. Replacing that with an explicit
`VERDICT: APPROVE` / `VERDICT: OBJECT` line collapsed spurious objections from 8
to 1.

It also changed the error-catching rate from 0/2 to 0/2. The contract bug was
making the critic *noisier*, not blinder. Worth fixing — "the model will follow
the output format" is exactly the assumption this project exists to distrust —
but it was never what was wrong.

**Why it fails.** The critic has a fresh *context*. It does not have fresh
*priors*. Same model, same training, same reading of the same ambiguous report,
same blind spots. Where the first agent's reasoning was sound the critic agreed;
where it was subtly wrong the critic made the identical error, because that is
the error the model makes on that input — and then wrote a justification for it.

Independence of context is not independence of judgement. A second opinion is
only worth having if it can be *differently* wrong.

**Decision: removed.** Three verification mechanisms — execution, self-patching,
independent review — and the score is the same 15/17 that roughly 150 words of
instruction reached at a fifth of the cost.

---

## 4. A single run is not a measurement

Everything in §1–§3 rests on comparing one run of one system against one run of
another. Partway through, an accident showed how shaky that is.

**How it surfaced.** A rate-limit interruption forced the baseline to be re-run
on a corpus that contained the original 17 cases as a subset. That produced two
independent runs of the *same system* on the *same cases*, and they disagreed on
6 of the 14 scored in both — `boltons-eb659013`, `cachetools-bb4b37cf`,
`more-itertools-0e6acdf9`, `packaging-a716c52b` and `semver-4b03f867` all moved
from a failure verdict to REPRO, while `boltons-f1034b07` moved the other way.
Nothing in the harness had changed.

**How much of that was real.** That second run happened *during* the rate-limit
event, so some of it ran under degraded conditions and 43% is not a trustworthy
disagreement rate. The confirmatory stage therefore ran the baseline three times
cleanly on all 44 cases. The measured figures:

| | run 1 | run 2 | run 3 |
|---|---:|---:|---:|
| repro | 34/44 | 36/44 | 36/44 |
| rate | 77% | 82% | 82% |

**88% verdict agreement between consecutive runs** — 11 individual cases out of
88 paired observations changed verdict, with nothing changing but the sampling.
The aggregate rate is steadier than the per-case verdicts: a 5-point band across
three runs, while roughly one case in eight flips.

**What it changes.** Every rung delta in §1–§3 is one or two cases wide. One case
in eight flipping on its own means those deltas sit inside the noise. That does
not make the findings worthless, but it changes what they rest on: not the score,
but the *mechanism* visible in the trajectory — the agent stopping the moment
`run_test` said FAILED, the probe replying "your test PASSES with this fix" to a
patch the agent had just invented, the critic writing a paragraph of citations
endorsing a wrong expectation. Those are reproducible observations about
behaviour. The scores around them wobble.

It also explains why the confirmatory stage repeats the headline pair rather than
re-running the whole ladder. Three runs of two systems buys more certainty about
the claim that matters than one run of six systems buys about all of them.

**The lesson.** If you are comparing agent configurations on a benchmark, run each
configuration more than once before believing a difference, and report the
within-system variance next to the between-system one. Most agent evaluations —
including the first version of this one — quietly report a single run as though
it were a measurement. `regressgen report` now prints the agreement rate directly
underneath the scoreboard, so the noise floor is impossible to miss.

---

## 5. The challenging case: when the report cannot determine the answer

`semver-bc41390f` is solved by no system, at any rung, in any run. Across
**12 stored runs spanning all six systems** it returns the identical verdict —
WRONG_EXPECTATION — every time. In a corpus where roughly one case in eight
flips between runs, that consistency is itself the finding: this is not a case
the agent sometimes gets. It is a case the agent cannot get.

**The bug.** Comparing a `Version` with an instance of a subclass is asymmetric:
one direction works, the other raises `TypeError`.

**What every system asserted.** That both directions should succeed and agree:

```python
assert a.compare(b) == 0
assert b.compare(a) == 0
assert a == b and b == a
```

Reasonable. Also wrong.

**What the maintainer actually did.** The fix is one token — `Version` becomes
`type(self)` in the comparable-types tuple — and the regression test they wrote
alongside it asserts something no one guessed:

```python
with pytest.raises(TypeError):
    SemVerSubclass.parse("1.0.0").compare(Version.parse("1.0.0"))   # still raises
assert Version.parse("1.0.0").compare(SemVerSubclass.parse("1.0.0")) == 0

assert SemVerSubclass.parse("1.0.0").__eq__(Version.parse("1.0.0")) is NotImplemented
assert SemVerSubclass.parse("1.0.0") == Version.parse("1.0.0")      # ...yet True
```

`compare()` stays asymmetric. `==` becomes symmetric — but not because both
sides succeed. One side returns `NotImplemented` and Python falls back to the
reflected operation. The maintainer fixed the equality protocol and deliberately
left `compare()` alone.

**What it reveals.** The report asked for symmetry and offered two ways to get
there: make both work, or make both fail. The maintainer picked a third path
that the report does not contain and could not have contained, because it is a
design decision about which protocol should carry the semantics.

This is a ceiling, not a bug in the agent, and the run data says so plainly.
Every other case in the corpus moves around: systems disagree, runs disagree
with themselves. This one never does. Better tools, more turns and stronger
verification all move an agent toward *the correct behaviour as the report
describes it*. None of them recover intent that was never written down, and no
amount of sampling stumbles onto it.

It is also the clearest argument for the human checkpoint in `regressgen solve`.
The agent's failure here is not sloppiness — its answer is defensible, and a
reviewer who knows the library would catch it in seconds. That is exactly the
division of labour the tool is built around.

---

## 6. Four bugs found in our own evaluation

Every one of these was caught by auditing the harness rather than the agent, and
each had been quietly distorting a result. They are recorded because in a project
whose entire claim is "the measurement is trustworthy", the measurement's own bug
history is part of the evidence.

**The corpus was a test specification.** The first generated bug reports stated
the exact expected value and, in several cases, explained the root cause. One
cachetools report ended with a paragraph naming the internal method and the
missing check. The baseline scored **14/17** against those reports — not because
it was good at the task, but because the task had become transcription.

Reports were rewritten in a user's voice: symptom-level, no exact expected
values, no causal explanation. A mechanical leak gate (`leaks()` in
`tools/write_reports.py`) now rejects any draft naming a private identifier from
the fix diff, a touched source file, a dunder in prose, or a causal phrase, and
regenerates it with the violation fed back.

Baseline against the rewritten corpus: **9/17**. The original drafts are kept as
`cases/*/report_v1_precise.md`.

**The baseline was reading 11% of the file.** Source inlined for the baseline was
truncated at 24,000 characters. For 11 of 17 cases the real file is larger —
`more_itertools/more.py` is 172,000 characters — so the baseline was shown the
first 11% of the file and never reached the function under discussion.

Raised to 250,000 characters, so every file in the corpus fits whole. The
baseline score did not move (9/17), but the failure mix did: INVALID fell 3→1
and WRONG_EXPECTATION rose 3→5. Truncation had been converting "wrong idea about
correct behaviour" into "could not import", which would have made the agent's
elimination of INVALID look like a larger win than it is.

Both numbers are in `results/_archive/` alongside the current ones.

**Third: the leak gate itself had false positives.** Expanding the corpus
surfaced two:

- Private identifiers were matched by substring, so `_cache` — lifted from a
  cachetools fix diff — matched inside `mru_cache`, a perfectly public decorator
  name. Now matched on a word boundary.
- Dunders in prose were banned outright, which is right for `__get__` inside a
  descriptor and wrong for `__eq__` in a dataclass library. For attrs, protocol
  dunders *are* the public API — a user says `__attrs_pre_init__` the way a dict
  user says `keys()`. Now only non-protocol dunders are flagged, against an
  explicit whitelist.

Both failed *closed* — they rejected good reports rather than admitting leaky
ones — so no leaked report ever reached the corpus. That is the direction you
want a gate like this to fail: the cost of a false positive is one more draft;
the cost of a false negative is a corpus that silently measures the wrong thing.

**Fourth: the validator disagreed with the miner.** `validate` copied the
maintainer's oracle test to a synthetic filename before running it. Three attrs
cases assert on their own module path — `repr(C(1)).startswith("<tests.test_make.C
object at 0x")` — or pickle a class defined in the test module, and both break
when the file is renamed. The miner had always run the oracle at its real path,
so the two components disagreed and three perfectly good cases were reported as
invalid.

The general shape is worth keeping: when a checker and the thing it checks are
built separately, they drift, and the drift surfaces as *false alarms about your
data* rather than as an obvious bug. The instinct on seeing three invalid cases
is to drop them. `tests/test_corpus.py` now pins the behaviour instead.

**What these four have in common.** Not one was found by looking at the agent.
Three were found by asking "is this number too good?" and one by asking "is this
failure really the data's fault?". An evaluation harness is code, it has bugs at
the same rate as any other code, and its bugs are unusually dangerous because
they present as *results*.

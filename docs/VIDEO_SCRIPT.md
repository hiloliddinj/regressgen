# Video script — 6 commands, ~4:30

Terse by design. Say the bold lines, let the terminal do the rest.
Long pauses while output scrolls are fine — better than talking over it.

**Two bugs carry the whole video:**

| | `boltons-c1c25da3` | `semver-bc41390f` |
|---|---|---|
| bug | `Bits(4, 2)` should raise; doesn't | subclass comparison is asymmetric |
| real fix | `>` → `>=` | `Version` → `type(self)` |
| agent | solves it | **cannot** solve it, ever |
| used in | steps 1, 2, 4 | steps 2, 5 |

## Before recording

```bash
cd ~/Desktop/micro1 && uv sync && uv run regressgen report >/dev/null
```

```bash
claude -p "Reply with exactly: AUTH_OK" --max-turns 1
```

---

# 1 · 0:00 — The problem

```bash
uv run regressgen show boltons-c1c25da3
```

> **"A real bug in a real library. `Bits(4, 2)` should raise an error — four
> doesn't fit in two bits. It doesn't raise."**

*Point at line 8 of the output — the one starting `commit`:*

```
commit    https://github.com/mahmoud/boltons/commit/c1c25da365cf...
```

> **"That's the actual upstream commit. The fix is one character: greater-than
> becomes greater-or-equal."**

> **"Before fixing it I'm supposed to write a test that fails because of it.
> Nobody does. The reason isn't laziness — a test that fails because I mistyped
> a method name looks exactly like a test that found the bug. Same red bar."**

---

# 2 · 0:45 — How it's graded

```bash
uv run regressgen validate --case boltons-c1c25da3 --case semver-bc41390f
```

> **"So I built the grader first. Every test runs twice — against the broken
> code, where it must fail, and the fixed code, where it must pass. The agent
> only ever sees the broken half."**

> **"That pair can't be gamed. `assert False` fails both. A test of code that
> already works passes both. Only a test that pins down correct behaviour
> survives."**

*Point at `I1=True  I2=True` on either verdict line:*

```
[ 1/2] OK   boltons-c1c25da3    I1=True  I2=True  I3=True  I4=True
                                ^^^^^^^^^^^^^^^^
```

> **"Forty-four real bugs. I1 and I2 say the library's own test suite is green
> on both sides — the bug shipped, undetected. You can't find it by running the
> tests that already exist."**

---

# 3 · 1:20 — The baseline

```bash
uv run regressgen report
```

Prints an aligned table in a terminal (markdown only when piped), and the
44-row per-case grid is hidden unless you pass `--per-case` — so nothing
scrolls off screen.

> **"The baseline is what you'd do today: one prompt, the report, the whole
> source file — more than the agent gets. It's already good. Eighty percent."**

*Point at the fifth column, `Silent failures` — the `1.7` and the `0.0`:*

```
  System                           Repro rate      Range   Runs  Silent failures
  Baseline (one prompt, no tools)  35.3/44  (80%)  77–82%  3     1.7
  v4  + right-reason check         40.0/44  (91%)  89–93%  3     0.0
                                                                 ^^^
```

> **"This column is the one I care about. One point seven per run. Tests that
> pass on the broken code. You run pytest, see green, commit — and you have no
> coverage. Reading the test, you can't tell."**

> **"The agent's number there is zero. Every run."**

---

# 4 · 1:55 — The agent, live

```bash
uv run regressgen solve --repo cases/boltons-c1c25da3/buggy --report cases/boltons-c1c25da3/report.md --tests-dir tests
```

*(let it run — 4 tool calls, about a minute; narrate lightly)*

> **"Searches. Reads the real implementation instead of guessing. Writes a test.
> Runs it."**

> **"Then the part that matters — it reads *why* it failed. Not that it failed.
> Why."**

*Point at the `Agent's rationale:` block near the bottom — the phrase
"off-by-one in Bits.__init__'s bounds check":*

> **"Off-by-one in the bounds check. That's exactly the one-character fix from
> step one."**

*Point at the last box — `REVIEW BEFORE USE`:*

> **"And it stops. Won't touch your repo unless you pass `--out`. The agent
> asserts what it *believes* correct behaviour is — that judgement stays mine.
> Here's why that matters."**

---

# 5 · 3:00 — The one it can't solve

```bash
uv run regressgen show semver-bc41390f --spoil
```

*The output has two halves. Stay on the top half — `BUG REPORT` — first:*

> **"Subclass a Version, compare both directions, get different answers. Every
> system I built asserts the obvious thing: both directions should work and
> agree."**

*Now scroll to the second half — `HELD-OUT ORACLE`. Point at the
`with pytest.raises(TypeError):` line:*

```
    with pytest.raises(TypeError):
        SemVerSubclass.parse("1.0.0").compare(Version.parse("1.0.0"))
    ^^^^ still raises, even after the fix
```

> **"The maintainer did something else. `compare()` still raises — look, they
> assert the TypeError. Only equality became symmetric, through Python's
> NotImplemented fallback."**

> **"That's a design decision. It's not in the report and couldn't be. Twelve
> runs, six configurations, every one fails this case. That's not a case the
> agent sometimes misses — it's one it can't get. That's why a human reviews."**

---

# 6 · 3:45 — What I learned

*(show the Improvement changelog table in README.md)*

> **"Six versions. Three of them taught me I was wrong."**

> **"Biggest jump: letting it read the repository."**

> **"Then I added execution — let it run its own test. It got *worse*. The agent
> only sees half the goal: it can check the test fails, not that it fails for
> the right reason. It saw FAILED and stopped."**

> **"Then I let it patch the bug itself and check its test goes green. Changed
> nothing, sixty percent more cost. It wrote patches that made its own wrong
> answers true."**

> **"Then a separate reviewer agent, fresh context. Identical verdict on all
> seventeen cases, twice the cost. On the semver bug it traced the code
> correctly — and approved a test that fails against the real fix."**

# 4:25 — Close

> **"Three verification mechanisms. All three removed. What worked was a hundred
> and fifty words telling the agent what its verifier couldn't see."**

> **"Verification inside the agent's own reasoning raises its confidence, not
> its accuracy. A fresh context is not fresh priors."**

*(leave the scoreboard on screen)*

---

## Numbers, if you need them

| | baseline | agent |
|---|---|---|
| repro rate | 80% (77–82%) | **91%** (89–93%) |
| silent failures | 1.7 | **0.0** |
| run-to-run agreement | 88% | 95% |
| cost per test | $0.08 | $0.22 |

McNemar over 3 paired runs: 19 fixed, 5 broken, **p = 0.0066**. Single run: p = 0.23.

## Don't

- Don't run the baseline or full `validate` live — minutes long.
- Don't add a third bug.
- Don't talk over scrolling output. Pause, then speak.
- Hard limit 5:00. Cut step 6 before you cut step 4.

# Video script

Read the **SAY** lines out loud, word for word. Type the **TYPE** lines.
No mouse, no pointing — just talk while the output sits on screen.

**Timing.** Steps 1–5 are about **3 minutes 30**. Step 6 adds about **1 minute**.
Total ~4:30, under the 5:00 limit.

If you fluff lines or talk slower than planned, **stop after step 5 and skip
step 6.** Steps 1–5 tell the whole story. Going over 5:00 is the only thing that
can disqualify the video.

---

## BEFORE RECORDING

Big font (16pt). Window as large as it goes. Run these once — the second must
print `AUTH_OK`:

```bash
cd ~/Desktop/micro1 && uv sync && uv run regressgen report > /dev/null
```

```bash
claude -p "Reply with exactly: AUTH_OK" --max-turns 1
```

Type `clear`. Start recording.

---

## STEP 1

**TYPE:**

```bash
uv run regressgen show boltons-c1c25da3
```

**WAIT** for the output.

**SAY:**

> "A real bug in a real Python library. There's the link to the actual commit
> that fixed it — one character.
>
> `Bits(4, 2)` should raise an error, because four doesn't fit in two bits. It
> doesn't. It quietly returns the wrong thing.
>
> Before fixing a bug you should write a test that fails because of it. Almost
> nobody does — and not from laziness. A test that fails because I mistyped a
> function name looks exactly like one that found the bug. Both are just red."

**TYPE:** `clear`

---

## STEP 2

**TYPE:**

```bash
uv run regressgen validate --case boltons-c1c25da3 --case semver-bc41390f
```

**WAIT** — 8 seconds.

**SAY:**

> "So I built the grader first.
>
> Every test runs twice. Against the broken code, where it must fail. Against the
> fixed code, where it must pass. The agent only ever sees the broken version.
>
> That can't be cheated. `assert False` fails both — scores nothing. A test of
> something that already works passes both — also nothing. Only a test that says
> what the code *should* do survives.
>
> Those first two checks mean the library's own test suite is green on both
> versions. This bug shipped undetected. You can't find it with the tests that
> already exist. Forty-four bugs like this, from seven real libraries."

**TYPE:** `clear`

---

## STEP 3

**TYPE:**

```bash
uv run regressgen report
```

**SAY:**

> "Top row is the baseline — one prompt, with the whole source file. More than my
> agent gets, deliberately. It's already good: eighty percent. Mine is
> ninety-one.
>
> But look at silent failures. The baseline makes one point seven per run — tests
> that *pass* on the broken code. You run pytest, see green, commit, and you have
> no coverage. Reading it, you can't tell.
>
> Mine is zero. Every run."

**TYPE:** `clear`

---

## STEP 4

**TYPE** (one long line — copy it whole):

```bash
uv run regressgen solve --repo cases/boltons-c1c25da3/buggy --report cases/boltons-c1c25da3/report.md --tests-dir tests
```

**WAIT** about a minute. Talk while it runs:

> "The real tool. It gets the broken library and the bug report, nothing else.
>
> It searches, reads the actual code instead of guessing, writes a test, runs it.
>
> Then the part that matters — it reads *why* it failed. Not that it failed. Why."

**WAIT** for it to finish, then **SAY:**

> "There's the test. The rationale says off-by-one in the bounds check — exactly
> the one-character fix from the start.
>
> Then it stops for review. It won't touch my repo unless I say so, because it's
> asserting what it *believes* is correct. That judgement is still mine. Here's
> why that matters."

**TYPE:** `clear`

---

## STEP 5

**TYPE:**

```bash
uv run regressgen show semver-bc41390f --spoil
```

**WAIT.** Scroll slowly down while you talk.

**SAY:**

> "Different bug. Subclass a Version, compare two of them, and the answer depends
> on which one is on the left.
>
> Every version of my agent says both directions should work and agree. The
> obvious reading.
>
> Here's what the maintainer actually did. They left it raising — their test
> expects a TypeError. They only fixed equality, through a Python fallback.
>
> That's a design decision. It isn't in the report and never could be. Twelve
> runs, six configurations, all wrong. Not a case it sometimes misses — one it
> cannot get. That's why a human reviews."

**TYPE:** `clear`

---

## STEP 6 — OPTIONAL, skip if you are near 4 minutes

**TYPE:**

```bash
uv run regressgen report
```

**SAY:**

> "Six versions. Three taught me I was wrong.
>
> Biggest win: letting it read the repository.
>
> Then I let it run its own tests — that made it *worse*. It only sees half the
> goal. It can check its test fails, not that it fails for the right reason. It
> saw FAILED and stopped.
>
> Then I let it patch the bug itself to confirm its test went green. Changed
> nothing, cost sixty percent more. It wrote patches that made its own wrong
> answers true.
>
> Then a separate reviewer agent. Identical answer on all seventeen cases, twice
> the cost. On that semver bug it traced the code correctly, then approved a test
> that fails against the real fix.
>
> Three verification mechanisms, all removed. What worked was a hundred and fifty
> words telling the agent what its verifier couldn't see.
>
> Verification inside the agent's own reasoning makes it more confident, not more
> correct. Thanks for watching."

**STOP RECORDING.**

---

## If something goes wrong

- **`solve` hangs or errors** → Claude login expired. Re-run the `AUTH_OK` check,
  then re-record step 4 only.
- **The table wraps onto two lines** → terminal too narrow. Widen it, or drop the
  font one point.
- **Over 5 minutes** → cut step 6. Steps 1–5 tell the whole story.
- **You fluff a line** → `clear`, redo that step. It's only 4 minutes; re-recording
  from the top is fine.

## Numbers, if anyone asks

| | baseline | my agent |
|---|---|---|
| tests that reproduce the bug | 80% | **91%** |
| tests that silently pass on broken code | 1.7 per run | **0.0** |
| cost per test | $0.08 | $0.22 |

44 real bugs, 3 runs each. Significance: p = 0.0066.

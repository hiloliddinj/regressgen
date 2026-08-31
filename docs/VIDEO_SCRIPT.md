# Solution video — shot list (target 4:50, hard limit 5:00)

Record with QuickTime (File → New Screen Recording) or `Cmd+Shift+5`.
Terminal at ~16pt, dark theme, ~110 columns.

**The whole video follows two bugs.** One the agent gets right, one it provably
cannot. Everything else hangs off those two.

| | Bug A — `boltons-c1c25da3` | Bug B — `semver-bc41390f` |
|---|---|---|
| what | `Bits(4, 2)` should raise — 4 doesn't fit in 2 bits | subclass comparison is asymmetric |
| real fix | one character: `>` becomes `>=` | one token: `Version` becomes `type(self)` |
| agent | **solves it**, every run | **fails**, in all 12 runs of all 6 systems |
| why it's in the video | shows the machine working | shows the ceiling, and why a human stays in the loop |

---

## Before you hit record

```bash
cd ~/Desktop/micro1 && uv sync && uv run regressgen report >/dev/null
```

Confirm the live demo will work — this must print `AUTH_OK`:

```bash
claude -p "Reply with exactly: AUTH_OK" --max-turns 1
```

Have two terminal tabs ready. Do one silent practice run of the five commands.

---

## 0:00–0:40 — The problem

Show Bug A's report:

```bash
cat cases/boltons-c1c25da3/report.md
```

> "This is a real bug report, filed against a real Python library. `Bits(4, 2)` —
> four doesn't fit in two bits — should raise an error and doesn't.
>
> Before I fix that, I'm supposed to write a test that fails because of it.
> Everybody knows that. Almost nobody does it, and not out of laziness: the
> failing test is the expensive part. I have to find the code in a library I
> didn't write, work out what the *correct* behaviour is — the report tells me
> what broke, not precisely what right looks like — and get a test to fail for
> the right reason.
>
> And that last part is the trap. A test that fails because I mistyped a method
> name looks exactly like a test that found the bug. Same red bar."

## 0:40–1:20 — How it's graded

Show the verdict table in the README, then:

> "So I built the grader first. Every generated test is run twice: against the
> buggy code, where it must fail, and against the fixed code, where it must
> pass. The agent only ever sees the buggy half.
>
> That pair is what makes this measurable rather than a matter of taste.
> `assert False` fails on the buggy code — and on the fixed code, so it scores
> zero. A test of behaviour that already works passes both, so it scores zero
> too. The only way through is to pin down what the code *should* do."

Run it on both bugs — 8 seconds:

```bash
uv run regressgen validate --case boltons-c1c25da3 --case semver-bc41390f
```

> "Forty-four cases, each a real bug a real maintainer really fixed, mined by
> script from seven open-source libraries. This re-proves the ground truth from
> scratch — four pytest runs per case, no model calls, no cost. Two here; all
> forty-four takes fifteen minutes and prints the same thing.
>
> Watch I1 and I2. The project's *existing* test suite is green on both sides of
> every case. The bug ships undetected. You cannot find it by running the tests
> that are already there."

## 1:20–1:55 — The baseline

Don't run it live — three and a half minutes. Show the stored result:

```bash
uv run regressgen report
```

> "The baseline is what you'd do today: one prompt, the bug report, and the whole
> source file the real fix touched — which is more than the agent gets, on
> purpose. A fair baseline that still loses is worth more than a weak one.
>
> It's already good. Eighty percent."

Point at the silent-failures column.

> "But look at this column. One point seven per run. These are tests that *pass*
> on the broken code. Real tests, real assertions, completely useless — you run
> pytest, see green, commit, and you believe you have regression coverage you do
> not have. Reading the test, you cannot tell.
>
> The agent's number there is zero. In every run. That's the row I care about."

## 1:55–3:05 — Bug A, live

```bash
uv run regressgen solve \
  --repo cases/boltons-c1c25da3/buggy \
  --report cases/boltons-c1c25da3/report.md \
  --tests-dir tests
```

Narrate the tool calls as they scroll:

> "It searches for the class, reads the actual implementation instead of guessing
> the signature, writes a test, and runs it against the buggy code.
>
> Then the part that matters: it reads *why* it failed. Not that it failed —
> why. Was this an assertion about behaviour, or did I typo a method name?"

Point at the rationale.

> "And there's the bug. The check is `val > 2 ** len_` where it needed
> `>=`. Off by one. The real fix upstream is exactly that one character."

Point at the review banner.

> "Then it stops. It won't write to your repo unless you pass `--out`. The agent
> is asserting what it *believes* correct behaviour to be, and that judgement is
> still mine. Which brings me to the second bug."

## 3:05–3:50 — Bug B, the one it cannot solve

```bash
uv run regressgen show semver-bc41390f
```

> "Subclass a `Version`, compare it both ways round, and you get different
> answers — one direction raises, the other works. Every system I built asserts
> the same thing here: that both directions should succeed and agree. It's the
> obvious reading. It's also wrong."

Now reveal the held-out answer:

```bash
uv run regressgen show semver-bc41390f --spoil
```

> "The maintainer kept `compare()` asymmetric — it still raises — and fixed only
> the equality protocol, so `==` becomes symmetric through Python's
> `NotImplemented` fallback. A third path the report doesn't contain and could
> not have contained, because it's a design decision.
>
> No system solves this. Twelve runs, six configurations, identical verdict every
> time. In a corpus where one case in eight flips between runs, that consistency
> *is* the finding. This isn't a case the agent sometimes misses. It's one it
> cannot get — and it's exactly why a human reviews the output."

## 3:50–4:30 — The changelog

Show the changelog table in the README.

> "Getting to ninety-one percent took six versions, and I want the ladder — not
> for the final number, but because three of the six taught me I was wrong.
> These rungs are a smaller corpus, one run each; the comparison I showed you is
> the bigger one, repeated.
>
> The biggest jump was just letting the agent read the repository.
>
> Then I added execution feedback — let it run its own test. It made things
> *worse*. The agent can only see half the goal: it can check the test fails, not
> that it fails for the right reason. So it wrote a test, saw FAILED, and stopped.
>
> So I let it patch the bug itself and check its test goes green. Used in every
> case, pushed back a third of the time, changed nothing — for sixty percent more
> money. On the cases it got wrong it wrote a patch that made its own wrong answer
> true, and the probe said 'your test passes'.
>
> Last try: a separate reviewer agent, fresh context. It returned the *identical
> verdict on all seventeen cases*, at more than twice the cost. On this semver
> bug it went and traced the comparison logic, found the real mechanism, wrote it
> down correctly — and approved a test that fails against the actual fix."

## 4:30–4:50 — The finding

> "Three verification mechanisms. All three removed. What worked was about a
> hundred and fifty words of instruction telling the agent what its verifier
> couldn't see.
>
> Verification that lives inside the agent's own reasoning raises its confidence
> without raising its accuracy. A fresh context is not fresh priors — a second
> opinion is only worth having if it can be *differently* wrong.
>
> And run it more than once. Three runs of the same system agree on eighty-eight
> percent of verdicts. Every rung on my ladder is one or two cases wide, so none
> of them clear that bar on score alone. They hold because you can watch the
> mechanism in the trajectories."

Close on the scoreboard and let it sit.

---

## Numbers, for reference

Re-check against `make report` on the day — re-running shifts them by a case or two.

| | baseline | shipped agent |
|---|---|---|
| repro rate | 35.3/44 = 80% (77–82%) | 40.0/44 = 91% (89–93%) |
| silent failures | 1.7 | 0.0 |
| uncollectable tests | 1.0 | 0.0 |
| run-to-run agreement | 88% | 95% |
| cost per test | $0.08 | $0.22 |

Paired exact McNemar over 3 run-pairs: 19 fixed, 5 broken, **p = 0.0066**.
On a single run: p = 0.23 — worth saying out loud.

## Do not

- Don't read the README aloud. Show the terminal.
- Don't run the baseline or the full validate live. Both are minutes long.
- Don't introduce a third bug. Two is the whole story.
- Don't exceed 5:00. Cut the changelog walk before you cut the live execution.

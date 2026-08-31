# Solution video — shot list (target 4:30, hard limit 5:00)

Record with QuickTime (File → New Screen Recording) or `Cmd+Shift+5`.
Terminal at ~16pt, dark theme, window ~120 cols. Have two tabs ready.

Run every command live. Judges have seen a lot of slideware; a real terminal
that actually prints the number is worth more than any animation.

**Before recording**, warm the caches so nothing stalls on camera:

```bash
uv sync && uv run regressgen list >/dev/null
```

---

## 0:00–0:35 — The problem

On camera: `cases/more-itertools-0e6acdf9/report.md` open in the terminal
(`cat` it, don't scroll a browser).

> "This is a real bug report from a real Python library. My job is the thing
> every developer is supposed to do first and almost nobody does: write a test
> that fails because of this bug, before fixing it.
>
> That's harder than it sounds. I have to find the code, work out what the
> *correct* behaviour is — the report says what broke, not what right looks
> like — and get a test to fail for the right reason. A test that fails because
> I guessed a function name wrong looks exactly the same in the terminal."

## 0:35–1:15 — How it's graded, and why that's the whole trick

Show the verdict table in the README.

> "Every generated test is run twice: against the buggy code, where it must
> fail, and against the fixed code, where it must pass. The agent only ever
> sees the buggy tree.
>
> That pair is what makes this measurable. `assert False` fails on the buggy
> code — and also on the fixed code, so it scores zero. A test of behaviour
> that already works passes both, so it scores zero too. The only way through
> is to pin down what the code *should* do."

Run the corpus's own proof:

Run two cases, not all 44 — the full run is 15 minutes and you do not have them:

```bash
uv run regressgen validate --case boltons-c1c25da3 --case semver-bc41390f
```

> "Forty-four cases, each a real bug a real maintainer really fixed. This
> re-proves the ground truth from scratch — four pytest runs per case, no model
> calls, no cost. I'm running two here; the full set takes fifteen minutes and
> prints the same thing.
>
> The important line is I1 and I2: the project's *existing* test suite is green
> on both sides of every case. The bug ships undetected. You cannot find it by
> running the tests that are already there — the agent has to construct a new
> input that exposes it."

## 1:15–1:55 — The baseline

Do **not** run this live — it takes three and a half minutes. Show the stored
result instead:

```bash
uv run regressgen report
```

> "The baseline is what you do today: one prompt, the bug report, and the whole
> source file the real fix touched — which is more than the agent gets, on
> purpose. A fair baseline that still loses is worth more than a weak one.
>
> It's already good — eighty percent. These are real libraries and a lot of
> these bugs are straightforward once you can see the code. A weak baseline
> would have made my numbers look better and meant nothing."

Point at the silent-failures column.

> "But look at this column. These are tests that *pass* on the broken code. Real
> tests, real assertions, and completely useless — you'd run pytest, see green,
> and commit believing you have regression coverage you don't have. Reading the
> test, you cannot tell. That's the failure this whole project is about."

Open one and show it.

## 1:55–3:10 — One full agent execution

Run the shipped default against a real repository:

```bash
uv run regressgen solve \
  --repo cases/boltons-c1c25da3/buggy \
  --report cases/boltons-c1c25da3/report.md \
  --tests-dir tests
```

Narrate the tool calls as they scroll:

> "It searches for the class, reads the actual implementation rather than
> guessing the signature, writes a test, and runs it against the buggy code.
>
> Then it does the thing the baseline can't: it reads *why* the test failed. A
> test that fails because I typo'd a method name looks exactly like a test that
> found the bug — same red bar. It checks the failure is an assertion about
> behaviour, and that the value it called 'expected' is the correct one, not the
> broken one it just observed."

Point at the rationale, then the review banner.

> "It found the off-by-one — `greater than` where the code needed `greater than
> or equal`. And it stops here for a human. The agent is asserting what it
> believes correct behaviour to be, and that judgement is still mine. I'll show
> you in a moment exactly why that matters."

## 3:10–4:10 — The changelog, and the thing I did not expect

Show the changelog table in the README (not the scoreboard — these rungs are the
smaller exploratory corpus, and conflating the two on camera is the easiest way
to look sloppy).

> "Getting there took six versions, and I want to walk the ladder — not for the
> final number, but because three of the six taught me I was wrong.
>
> These are on a smaller seventeen-case corpus, one run each. The headline
> comparison I just showed you is the bigger one, repeated."

Point at the v2 row.

> "The biggest single jump was just letting the agent read the repository.
> Everything after that is verification — and this is where I was wrong three
> times in a row."

Point at v3.

> "Adding execution feedback made it *worse*. The agent can only see half the
> goal — it can check that its test fails, not that it fails for the right
> reason. So it wrote a test, saw FAILED, and stopped. Except look at the
> silent-failure column: execution drove that to zero. It didn't create errors,
> it converted them from silent to loud. If I'd scored only the headline number
> I'd have reverted the change that fixed the most dangerous failure mode."

Point at v5.

> "So I let the agent patch the bug itself and check its test goes green.
> Used in every single case, pushed back a third of the time, and changed
> nothing — for 60% more money. On the cases it got wrong, it wrote a patch that
> made its own wrong answer true, and the probe said 'your test passes'."

Point at v6. **This is the beat to land.**

> "Last try: a completely separate reviewer agent, fresh context, one question —
> will this test pass once the bug is fixed? It analysed every case, sent nine
> back for revision, cost three times as much, and changed nothing.
>
> It endorsed both of the wrong tests and caught neither. On this one" —
> `tabulate-d29909b4` — "it read the alignment code, cited the line number,
> cross-checked a similar test, and concluded 'this all checks out'. It was
> wrong. It's just wrong with a citation now."

## 4:10–4:45 — The finding

> "Three verification mechanisms, all removed. The one that worked was about a
> hundred and fifty words of instruction telling the agent what its verifier
> couldn't see.
>
> And one more thing I only found because a rate limit killed a run and forced
> me to repeat it. Three clean runs of the *same* system on the *same* cases
> agree on only 88% of individual verdicts. Every step on my ladder is one or
> two cases wide — all of them inside that noise.
>
> So these findings don't rest on the scores. They rest on what the trajectories
> show the agent actually doing: stopping the instant the tool said FAILED,
> patching the code to make its own wrong answer true, writing a paragraph of
> citations to endorse a mistake.
>
> The lesson I'd take anywhere: verification that lives inside the agent's own
> reasoning raises its confidence without raising its accuracy. A fresh context
> is not fresh priors — a second opinion is only worth having if it can be
> *differently* wrong. And run it more than once before you believe it."

Close on:

```bash
uv run regressgen report
```

Let the scoreboard and the stability table sit on screen together for a beat.

---

## Fill these in from `results/` before recording

Run `uv run regressgen report`. Two sets of numbers exist and they are not
interchangeable:

- **Exploratory** (17 cases, one run each) — the ladder rungs: v2's +5, v3's
  regression, v4's recovery, v5 and v6 changing nothing. Say "on a smaller
  corpus" when you quote these.
- **Confirmatory** (44 cases, three runs each) — baseline versus the shipped
  agent. This is the headline. Quote the mean and the range.

Current numbers, for reference — re-check them against `make report` on the day,
since re-running shifts them by a case or two:

| | baseline | shipped agent |
|---|---|---|
| repro rate | 35.3/44 = 80% (range 77–82%) | 40.0/44 = 91% (range 89–93%) |
| silent failures | 1.7 | 0.0 |
| uncollectable tests | 1.0 | 0.0 |
| run-to-run agreement | 88% | 95% |
| cost per test | $0.08 | $0.22 |

Paired exact McNemar over 3 run-pairs: 19 fixed, 5 broken, **p = 0.0066**.
The same comparison on a *single* run gives p = 0.23 — worth saying out loud.

## Do not

- Do not read the README aloud. Show the terminal.
- Do not skip `validate` — it is the reason anyone should believe the rest.
- Do not exceed 5:00. Cut the changelog walk before you cut the live execution.

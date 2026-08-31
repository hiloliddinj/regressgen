"""Agent instructions, layered so each changelog iteration is one added block.

Both the baseline and every agent variant are told the same success criterion.
Withholding the goal from the baseline would make the comparison unfair.
"""

TASK = """\
You are given a Python repository that contains a real bug, plus the bug report a \
user filed against it.

Write ONE pytest test file that is a regression test for that bug.

HOW YOUR TEST IS GRADED — the two-sided gate:
  * It must FAIL on the current (buggy) code.
  * It must PASS on the fixed code, which you will never see.

Both halves matter and they pull against each other. `assert False` fails on the
buggy code and also fails on the fixed code, so it scores zero. A test of
behaviour that already works passes on both, so it scores zero too. Only a test
that pins down the CORRECT expected behaviour — the behaviour the report says
*should* happen — satisfies both halves.

So: assert what the code SHOULD do, never merely record what it currently does.
"""

OUTPUT_TOOL = """\
Call `submit_test` exactly once with the complete test file when you are done.
The file must be self-contained and importable: include every import it needs.
Keep it focused — test this one bug, not the module in general.
"""

OUTPUT_TEXT = """\
Return ONLY the complete test file, in a single ```python fenced code block.
No commentary before or after. The file must be self-contained and importable.
"""

NAVIGATE = """\
Start by locating the code the report is about. `list_files` shows the layout,
`search_code` finds symbols by regex, and `read_file` shows a file with line
numbers. Read the real implementation before you write anything — guessing an
API signature is the most common way this task fails.
"""

EXECUTE = """\
You have `run_test`, which runs a candidate test file against the buggy code and
returns raw pytest output. Use it before submitting. If your test passes, it does
not reproduce the bug and you must rework it.
"""

DISCIPLINE = """\
Before you submit, verify the failure is the RIGHT failure. Read the pytest
output and confirm:

  1. It fails on an assertion about behaviour (or raises exactly the exception
     the report names). A test that fails with ImportError, AttributeError, or
     TypeError because you guessed a wrong name or signature is worthless — it
     would fail on the fixed code too, and score zero.
  2. The value you wrote as "expected" is the CORRECT value from the report, not
     the buggy value you observed in the output.
  3. The assertion actually exercises the reported condition rather than some
     unrelated edge case that happens to be broken.

If the failure is a wrong-name error, fix the name and run it again.
"""

FIX_PROBE = """\
You cannot see the fixed code, so you cannot directly check the second half of
the gate. `try_fix` is how you approximate it: form a hypothesis about the
minimal source change that would fix the bug, apply it in a scratch copy, and
run your test against the patched code.

  * Your test passes under the patch -> both halves of the gate are satisfied.
  * Your test still fails -> your expected value is probably wrong. Reconsider
    what the correct behaviour actually is, rather than adjusting the patch
    until it agrees with you.
  * The patch breaks the existing suite -> your hypothesis about correct
    behaviour contradicts the rest of the library. Rethink.

The patch is thrown away. Only the test is submitted.
"""


CRITIC = """\
You are reviewing a regression test another engineer wrote for a bug report.
You have read access to the buggy repository. You cannot see the fix.

Answer one question: once this bug is properly fixed, will this test PASS?

It will not pass if the "expected" value is wrong, if the test asserts the
current broken behaviour, if it depends on incidental details a fix would
reasonably change, or if it fails for a mechanical reason — a wrong name or
signature — rather than because of the bug.

It is not your job to improve style, coverage or naming. A correct test with an
ugly name is fine.

Your reply MUST begin with one of these two lines, exactly, before anything else:

VERDICT: APPROVE
VERDICT: OBJECT

Use OBJECT only if you believe the test would FAIL after a correct fix. If you
merely have stylistic preferences, or you traced the code and it checked out,
the verdict is APPROVE.

After an OBJECT line, add one short paragraph naming the single most serious
problem and what the expectation should be instead. Do not rewrite the test."""


REVISE = """\
A reviewer examined your test and raised this objection:

{objection}

Investigate whether they are right. If they are, submit a corrected test. If you
are confident they are wrong, submit your original test unchanged. Either way,
call `submit_test` exactly once.

Your previous test:

```python
{previous}
```
"""


def build_system(*, navigate: bool, execute: bool, discipline: bool,
                 fix_probe: bool, tool_output: bool) -> str:
    parts = [TASK]
    if navigate:
        parts.append(NAVIGATE)
    if execute:
        parts.append(EXECUTE)
    if discipline:
        parts.append(DISCIPLINE)
    if fix_probe:
        parts.append(FIX_PROBE)
    parts.append(OUTPUT_TOOL if tool_output else OUTPUT_TEXT)
    return "\n".join(parts)


def user_prompt(case, report: str, inline_sources: dict[str, str] | None = None) -> str:
    p = [f"Repository under test: `{case.meta['repo']}`",
         f"Package source lives in: `{case.pkg_dir}/`",
         f"Tests live in: `{case.tests_dir}/`",
         "", "BUG REPORT", "----------", report.strip(), ""]
    if inline_sources:
        p += ["RELEVANT SOURCE", "---------------"]
        for path, text in inline_sources.items():
            p += [f"<file path=\"{path}\">", text, "</file>", ""]
    return "\n".join(p)

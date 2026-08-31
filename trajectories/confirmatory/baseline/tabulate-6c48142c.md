# Trajectory — `baseline` on `tabulate-6c48142c`

**Verdict: REPRO**  (fails on buggy, passes on fixed — reproduces the bug)

- cost `$0.044` · wall `7.6s` · tool calls `0`

## 1. Agent instructions (system prompt)

```
You are given a Python repository that contains a real bug, plus the bug report a user filed against it.

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

Return ONLY the complete test file, in a single ```python fenced code block.
No commentary before or after. The file must be self-contained and importable.
```

## 2. Task (user prompt)

The agent receives the bug report and the repository layout. It never sees the fixed tree, the upstream fix, or the maintainer's test.

```
When using `maxcolwidths` on a cell that already contains a manual line break (`\n`), the existing line break gets collapsed/merged with the wrapped text instead of being preserved.

```python
from tabulate import tabulate

table = [["123456789 bbb\nccc"]]
print(tabulate(table, tablefmt="grid", maxcolwidths=10))
```

Got:
```
+-----------+
| 123456789 |
| bbb ccc   |
+-----------+
```

The `\n` between "bbb" and "ccc" got turned into a space and joined onto the same line, even though it fits fine on its own line width-wise.

I expected the original line break to be kept as a separate line, something like:

```
+-----------+
| 123456789 |
| bbb       |
| ccc       |
+-----------+
```

Seems like the wrapping logic used for `maxcolwidths` doesn't respect existing newlines in the cell content and just re-flows everything as one paragraph.
```

## 3. Tool calls

_No tools — this system answers in a single prompt._

## 4. Submitted test

```python
"""Regression test for maxcolwidths collapsing existing newlines.

Bug: when a cell already contains a manual line break (\n), wrapping it
with `maxcolwidths` should preserve that line break as a separate line,
not merge it with the wrapped text into a single re-flowed paragraph.
"""
from tabulate import tabulate


def test_maxcolwidths_preserves_existing_newline():
    table = [["123456789 bbb\nccc"]]
    result = tabulate(table, tablefmt="grid", maxcolwidths=10)

    # The original newline between "bbb" and "ccc" must be preserved,
    # i.e. "bbb" and "ccc" must appear on separate lines, not merged
    # into "bbb ccc" on the same line.
    assert "bbb ccc" not in result

    lines = result.splitlines()
    bbb_line = [line for line in lines if "bbb" in line]
    ccc_line = [line for line in lines if "ccc" in line]

    assert len(bbb_line) == 1
    assert len(ccc_line) == 1
    assert bbb_line[0] != ccc_line[0]

    # "ccc" should not be on the same line as "bbb"
    assert "ccc" not in bbb_line[0]
    assert "bbb" not in ccc_line[0]

    expected = (
        "+-----------+\n"
        "| 123456789 |\n"
        "| bbb       |\n"
        "| ccc       |\n"
        "+-----------+"
    )
    assert result == expected
```

## 5. Two-sided gate

### Against `buggy/` — exit 1 (must be non-zero)

```
F                                                                        [100%]
=================================== FAILURES ===================================
_________________ test_maxcolwidths_preserves_existing_newline _________________

    def test_maxcolwidths_preserves_existing_newline():
        table = [["123456789 bbb\nccc"]]
        result = tabulate(table, tablefmt="grid", maxcolwidths=10)
    
        # The original newline between "bbb" and "ccc" must be preserved,
        # i.e. "bbb" and "ccc" must appear on separate lines, not merged
        # into "bbb ccc" on the same line.
>       assert "bbb ccc" not in result
E       AssertionError: assert 'bbb ccc' not in '+----------...-----------+'
E         
E         'bbb ccc' is contained here:
E           +-----------+
E           | 123456789 |
E           | bbb ccc   |
E           +-----------+

test/test_regressgen_candidate.py:17: AssertionError
=========================== short test summary info ============================
FAILED test/test_regressgen_candidate.py::test_maxcolwidths_preserves_existing_newline
1 failed in 0.09s
```

### Against `fixed/` — exit 0 (must be zero)

```
.                                                                        [100%]
1 passed in 0.08s
```

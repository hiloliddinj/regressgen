# Trajectory — `baseline` on `tabulate-b1ed1fda`

**Verdict: REPRO**  (fails on buggy, passes on fixed — reproduces the bug)

- cost `$0.12074` · wall `78.8s` · tool calls `0`

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
SEPARATING_LINE renders garbage in orgtbl format

When using SEPARATING_LINE in a table with tablefmt="orgtbl", the separator row doesn't come out as a proper line — instead of a real dashed separator row like `|-----------+-----------|` I get a broken/garbled row with what looks like a stray control character in it.

Repro:

```python
from tabulate import tabulate, SEPARATING_LINE

table = [
    ["spam", 41.9999],
    SEPARATING_LINE,
    ["eggs", 451],
]
headers = ["strings", "numbers"]

print(tabulate(table, headers, tablefmt="orgtbl"))
```

Expected output should have a proper separator line matching the column widths, similar to how this works fine with tablefmt="simple" or "grid". Instead the orgtbl output has some garbage in place of the separator row, which breaks the table formatting badly. Seems specific to orgtbl - other formats handle SEPARATING_LINE correctly.
```

## 3. Tool calls

_No tools — this system answers in a single prompt._

## 4. Submitted test

```python
import pytest

from tabulate import tabulate, SEPARATING_LINE


def test_orgtbl_separating_line_renders_proper_separator():
    """Regression test: SEPARATING_LINE must render as a proper dashed
    separator row (like the one under the header) in the 'orgtbl' format,
    not as a garbled row containing the raw SEPARATING_LINE control
    character.
    """
    headers = ["strings", "numbers"]
    table_no_sep = [["spam", 41.9999], ["eggs", 451]]
    table_with_sep = [["spam", 41.9999], SEPARATING_LINE, ["eggs", 451]]

    baseline = tabulate(table_no_sep, headers, tablefmt="orgtbl")
    baseline_lines = baseline.split("\n")

    # Sanity check on the baseline (no separating line) rendering:
    # header, linebelowheader ("|---+---|"), row(spam), row(eggs)
    assert len(baseline_lines) == 4
    separator_line = baseline_lines[1]
    assert separator_line.startswith("|")
    assert separator_line.endswith("|")
    assert "-" in separator_line
    assert "+" in separator_line

    result = tabulate(table_with_sep, headers, tablefmt="orgtbl")
    result_lines = result.split("\n")

    # Expected structure with the separating line inserted between the two
    # data rows:
    #   header
    #   linebelowheader
    #   row(spam)
    #   separator line (same shape as linebelowheader)
    #   row(eggs)
    assert len(result_lines) == 5

    assert result_lines[0] == baseline_lines[0]
    assert result_lines[1] == baseline_lines[1]
    assert result_lines[2] == baseline_lines[2]
    assert result_lines[4] == baseline_lines[3]

    # The inserted separating line must look like a real separator line
    # (matching the same dashed pattern as linebelowheader), not garbage.
    assert result_lines[3] == separator_line

    # No stray control characters should leak into the rendered output.
    assert SEPARATING_LINE not in result
    assert "\x01" not in result
```

## 5. Two-sided gate

### Against `buggy/` — exit 1 (must be non-zero)

```
F                                                                        [100%]
=================================== FAILURES ===================================
_____________ test_orgtbl_separating_line_renders_proper_separator _____________

    def test_orgtbl_separating_line_renders_proper_separator():
        """Regression test: SEPARATING_LINE must render as a proper dashed
        separator row (like the one under the header) in the 'orgtbl' format,
        not as a garbled row containing the raw SEPARATING_LINE control
        character.
        """
        headers = ["strings", "numbers"]
        table_no_sep = [["spam", 41.9999], ["eggs", 451]]
        table_with_sep = [["spam", 41.9999], SEPARATING_LINE, ["eggs", 451]]
    
        baseline = tabulate(table_no_sep, headers, tablefmt="orgtbl")
        baseline_lines = baseline.split("\n")
    
        # Sanity check on the baseline (no separating line) rendering:
        # header, linebelowheader ("|---+---|"), row(spam), row(eggs)
        assert len(baseline_lines) == 4
        separator_line = baseline_lines[1]
        assert separator_line.startswith("|")
        assert separator_line.endswith("|")
        assert "-" in separator_line
        assert "+" in separator_line
    
        result = tabulate(table_with_sep, headers, tablefmt="orgtbl")
        result_lines = result.split("\n")
    
        # Expected structure with the separating line inserted between the two
        # data rows:
        #   header
        #   linebelowheader
        #   row(spam)
        #   separator line (same shape as linebelowheader)
        #   row(eggs)
        assert len(result_lines) == 5
    
        assert result_lines[0] == baseline_lines[0]
        assert result_lines[1] == baseline_lines[1]
        assert result_lines[2] == baseline_lines[2]
        assert result_lines[4] == baseline_lines[3]
    
        # The inserted separating line must look like a real separator line
        # (matching the same dashed pattern as linebelowheader), not garbage.
>       assert result_lines[3] == separator_line
E       AssertionError: assert '| \x01 |' == '|-----------+-----------|'
E         
E         - |-----------+-------
... [272 more chars]
```

### Against `fixed/` — exit 0 (must be zero)

```
.                                                                        [100%]
1 passed in 0.08s
```

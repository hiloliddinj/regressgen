# Trajectory — `baseline` on `tabulate-d29909b4`

**Verdict: REPRO**  (fails on buggy, passes on fixed — reproduces the bug)

- cost `$0.04764` · wall `7.7s` · tool calls `0`

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
Using `maxcolwidths` on a table that has a "True"/"False" string cell or a None cell raises an exception instead of producing wrapped output. Here's a minimal repro:

```python
from tabulate import tabulate

data = [
    ["First Entry", "True"],
    ["Second Entry", None],
]
headers = ["Title", "When"]
print(tabulate(data, headers=headers, tablefmt="grid", maxcolwidths=[7, 5]))
```

This blows up somewhere in the internal text-wrapping step when it tries to convert the cell value before wrapping it. Without `maxcolwidths` it works fine, so it's specific to the wrapping code path.

I expected `tabulate` to just wrap these cells like normal strings ("True"/"False" as text, None as empty/blank), not crash. Seems like the type-detection logic used for deciding how to cast a cell before wrapping doesn't handle these values properly.
```

## 3. Tool calls

_No tools — this system answers in a single prompt._

## 4. Submitted test

```python
"""Regression test for tabulate maxcolwidths crash on bool-like strings and None cells.

Bug: Using `maxcolwidths` on a table that has a "True"/"False" string cell or a
None cell raises an exception instead of producing wrapped output, because the
type-detection logic (`_type`) used to cast the cell before wrapping resolves to
`bool` or `NoneType`, which are not callable in the way the code expects
(`_type(cell, numparse)(cell)`).
"""

import pytest

from tabulate import tabulate


def test_maxcolwidths_with_bool_like_string_does_not_raise():
    data = [
        ["First Entry", "True"],
        ["Second Entry", "False"],
    ]
    headers = ["Title", "When"]

    result = tabulate(data, headers=headers, tablefmt="grid", maxcolwidths=[7, 5])

    assert "True" in result
    assert "False" in result


def test_maxcolwidths_with_none_cell_does_not_raise():
    data = [
        ["First Entry", "True"],
        ["Second Entry", None],
    ]
    headers = ["Title", "When"]

    # Should not raise an exception
    result = tabulate(data, headers=headers, tablefmt="grid", maxcolwidths=[7, 5])

    assert isinstance(result, str)
    assert "First Entry" not in result.split("\n")[0]  # sanity: it's wrapped/table text
    assert "True" in result
```

## 5. Two-sided gate

### Against `buggy/` — exit 1 (must be non-zero)

```
)
>                       for line in casted_cell.splitlines()
                                    ^^^^^^^^^^^^^^^^^^^^^^
                        if line.strip() != ""
                    ]
E                   AttributeError: 'bool' object has no attribute 'splitlines'

tabulate/__init__.py:1653: AttributeError
_______________ test_maxcolwidths_with_none_cell_does_not_raise ________________

    def test_maxcolwidths_with_none_cell_does_not_raise():
        data = [
            ["First Entry", "True"],
            ["Second Entry", None],
        ]
        headers = ["Title", "When"]
    
        # Should not raise an exception
>       result = tabulate(data, headers=headers, tablefmt="grid", maxcolwidths=[7, 5])
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

test/test_regressgen_candidate.py:36: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
tabulate/__init__.py:2249: in tabulate
    list_of_lists = _wrap_text_to_colwidths(
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

list_of_lists = [['First Entry', 'True'], ['Second Entry', None]]
colwidths = [7, 5], numparses = [True, True]

    def _wrap_text_to_colwidths(list_of_lists, colwidths, numparses=True):
        if len(list_of_lists):
            num_cols = len(list_of_lists[0])
        else:
            num_cols = 0
        numparses = _expand_iterable(numparses, num_cols, True)
    
        result = []
    
        for row in list_of_lists:
            new_row = []
            for cell, width, numparse in zip(row, colwidths, numparses):
                if _isnumber(cell) and numparse:
                    new_row.append(cell)
                    continue
    
                if width is not None:
                    wrapper = _CustomTextWrap(width=width)
                    # Cast based on our internal type handling. Any future custom
                    # formatting of types (such as datetimes) may need to be more
                    # explicit than just `str` of the object. Also doesn't work for
                    # custom floatfmt/intfmt, nor with any missing/blank cells.
                    casted_
... [800 more chars]
```

### Against `fixed/` — exit 0 (must be zero)

```
..                                                                       [100%]
2 passed in 0.07s
```

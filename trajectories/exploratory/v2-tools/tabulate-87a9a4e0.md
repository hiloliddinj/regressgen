# Trajectory — `v2-tools` on `tabulate-87a9a4e0`

**Verdict: REPRO**  (fails on buggy, passes on fixed — reproduces the bug)

- cost `$0.08144` · wall `20.3s` · tool calls `3`

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

Start by locating the code the report is about. `list_files` shows the layout,
`search_code` finds symbols by regex, and `read_file` shows a file with line
numbers. Read the real implementation before you write anything — guessing an
API signature is the most common way this task fails.

Call `submit_test` exactly once with the complete test file when you are done.
The file must be self-contained and importable: include every import it needs.
Keep it focused — test this one bug, not the module in general.
```

## 2. Task (user prompt)

The agent receives the bug report and the repository layout. It never sees the fixed tree, the upstream fix, or the maintainer's test.

```
Calling `tabulate` with an empty data list but with `maxheadercolwidths` set raises an error instead of just printing the headers. Since there are no rows, I'd expect it to behave the same as if `maxheadercolwidths` wasn't passed at all (just format the header row), but instead it blows up.

Repro:

```python
from tabulate import tabulate

print(tabulate([], headers=["one", "two", "three"], maxheadercolwidths=5))
```

Expected: just the header row rendered normally, something like:

```
one    two    three
-----  -----  -------
```

Actual: it throws an exception instead of returning the table. Works fine if I pass at least one row of data, so it seems specific to the empty-table case combined with `maxheadercolwidths`. Would expect empty tables to be handled consistently regardless of which column-width kwargs are set, same as `maxcolwidths` already works fine with empty data.
```

## 3. Tool calls

### 1. `search_code`(pattern="maxheadercolwidths")

Tool responded:

```
11 hits
```

### 2. `read_file`(path="tabulate/__init__.py", start=2230, end=2320)

Tool responded:

```
4607 chars
```

### 3. `submit_test`(rationale="Regression test for the bug where tabulate() raises an IndexError when called with an empty data list ([]) to)

Tool responded:

```
submitted
```

## 4. Submitted test

```python
import pytest

from tabulate import tabulate


def test_tabulate_empty_data_with_maxheadercolwidths_does_not_raise():
    """
    Bug: calling tabulate([], headers=[...], maxheadercolwidths=N) raises an
    exception (IndexError) instead of just rendering the header row, as it
    does when maxheadercolwidths is omitted or when maxcolwidths is used
    instead with empty data.
    """
    headers = ["one", "two", "three"]

    # This should not raise - previously raised IndexError: list index out of range
    result = tabulate([], headers=headers, maxheadercolwidths=5)

    assert isinstance(result, str)

    # The header row should still be rendered normally.
    for h in headers:
        assert h in result

    # It should behave the same as when maxheadercolwidths is not passed at all.
    expected = tabulate([], headers=headers)
    assert result == expected


def test_tabulate_empty_data_with_maxheadercolwidths_matches_maxcolwidths_behavior():
    """
    maxcolwidths already handles empty data gracefully; maxheadercolwidths
    should behave consistently with it for empty tables.
    """
    headers = ["one", "two", "three"]

    result_maxcolwidths = tabulate([], headers=headers, maxcolwidths=5)
    result_maxheadercolwidths = tabulate([], headers=headers, maxheadercolwidths=5)

    assert result_maxheadercolwidths == result_maxcolwidths
```

**Agent's stated rationale:**

> Regression test for the bug where tabulate() raises an IndexError when called with an empty data list ([]) together with maxheadercolwidths set. In tabulate/__init__.py, the maxcolwidths branch correctly guards against an empty list_of_lists (num_cols = 0 if empty), but the maxheadercolwidths branch unconditionally does `num_cols = len(list_of_lists[0])`, which raises IndexError('list index out of range') when list_of_lists is empty. The test asserts that calling tabulate with empty data and maxheadercolwidths does not raise, and that it renders just the header row (mirroring the behavior when maxheadercolwidths is not passed).

## 5. Two-sided gate

### Against `buggy/` — exit 1 (must be non-zero)

```
where fields are expected
        to reasonably be too long to look good as a single line, tabulate can help automate
        word wrapping long fields for you. Use the parameter `maxcolwidth` to provide a
        list of maximal column widths
    
        >>> print(tabulate( \
              [('1', 'John Smith', \
                'This is a rather long description that might look better if it is wrapped a bit')], \
              headers=("Issue Id", "Author", "Description"), \
              maxcolwidths=[None, None, 30], \
              tablefmt="grid"  \
            ))
        +------------+------------+-------------------------------+
        |   Issue Id | Author     | Description                   |
        +============+============+===============================+
        |          1 | John Smith | This is a rather long         |
        |            |            | description that might look   |
        |            |            | better if it is wrapped a bit |
        +------------+------------+-------------------------------+
    
        Header column width can be specified in a similar way using `maxheadercolwidth`
    
        """
    
        if tabular_data is None:
            tabular_data = []
    
        list_of_lists, headers, headers_pad = _normalize_tabular_data(
            tabular_data, headers, showindex=showindex
        )
        list_of_lists, separating_lines = _remove_separating_lines(list_of_lists)
    
        if maxcolwidths is not None:
            if type(maxcolwidths) is tuple:  # Check if tuple, convert to list if so
                maxcolwidths = list(maxcolwidths)
            if len(list_of_lists):
                num_cols = len(list_of_lists[0])
            else:
                num_cols = 0
            if isinstance(maxcolwidths, int):  # Expand scalar for all columns
                maxcolwidths = _expand_iterable(maxcolwidths, num_cols, maxcolwidths)
            else:  # Ignore col width for any 'trailing' columns
                maxcolwidths = _expand_iterable(maxcolwidths, num_cols, None)
    
            numparses = _expand_numparse(disable_numparse, num_cols)
            list_of_lists = _wrap_text_to_colwidths(
   
... [800 more chars]
```

### Against `fixed/` — exit 0 (must be zero)

```
..                                                                       [100%]
2 passed in 0.49s
```

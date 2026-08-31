# Trajectory — `baseline` on `tabulate-87a9a4e0`

**Verdict: REPRO**  (fails on buggy, passes on fixed — reproduces the bug)

- cost `$0.20648` · wall `6.4s` · tool calls `0`

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

_No tools — this system answers in a single prompt._

## 4. Submitted test

```python
"""Regression test for tabulate bug: maxheadercolwidths with empty data raises."""
from tabulate import tabulate


def test_maxheadercolwidths_with_empty_data():
    """Calling tabulate with empty data and maxheadercolwidths set should not
    raise, and should behave like the header-only table (same as when
    maxheadercolwidths is not passed)."""
    result = tabulate([], headers=["one", "two", "three"], maxheadercolwidths=5)
    expected = tabulate([], headers=["one", "two", "three"])
    assert result == expected

    # sanity check that headers actually appear in the output
    assert "one" in result
    assert "two" in result
    assert "three" in result
```

## 5. Two-sided gate

### Against `buggy/` — exit 1 (must be non-zero)

```
     Tabulate will, by default, set the width of each column to the length of the
        longest element in that column. However, in situations where fields are expected
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
                maxcolwidths = _expand_iterable(maxcolwidths, n
... [800 more chars]
```

### Against `fixed/` — exit 0 (must be zero)

```
.                                                                        [100%]
1 passed in 0.39s
```

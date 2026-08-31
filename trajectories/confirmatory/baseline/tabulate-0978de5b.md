# Trajectory — `baseline` on `tabulate-0978de5b`

**Verdict: WRONG_EXPECTATION**

- cost `$0.05065` · wall `11.7s` · tool calls `0`

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
Using `tabulate` with a list of dataclass instances and a `SEPARATING_LINE` mixed in raises an error instead of producing a table. If I just use plain dicts with the same separating line, it works fine, so it seems specific to dataclass rows.

```python
from dataclasses import make_dataclass
from tabulate import tabulate, SEPARATING_LINE

Person = make_dataclass("Person", ["name", "age", "height"])
data = [Person("Alice", 23, 169.5), SEPARATING_LINE, Person("Bob", 27, 175.0)]

print(tabulate(data, headers="keys"))
```

Expected: a table with headers derived from the dataclass fields, with a separating line drawn between the two rows, similar to how it works with lists-of-dicts input.

Instead it blows up with a traceback that looks like it's trying to treat the separating line marker itself as a dataclass row and failing when checking its fields. Would expect SEPARATING_LINE to just be skipped/handled the same way regardless of the row type used elsewhere in the list.
```

## 3. Tool calls

_No tools — this system answers in a single prompt._

## 4. Submitted test

```python
"""
Regression test for: tabulate() raising an error when a list of dataclass
instances is mixed with SEPARATING_LINE.

See bug report: using SEPARATING_LINE with dataclass rows should behave the
same way it does with dict rows -- i.e. it should be skipped when detecting
the dataclass fields, and rendered as a separating line in the output.
"""
from dataclasses import make_dataclass

import pytest

from tabulate import tabulate, SEPARATING_LINE

Person = make_dataclass("Person", ["name", "age", "height"])


def test_dataclass_rows_with_separating_line_does_not_raise():
    data = [Person("Alice", 23, 169.5), SEPARATING_LINE, Person("Bob", 27, 175.0)]

    # Should not raise any exception
    result = tabulate(data, headers="keys")

    assert isinstance(result, str)


def test_dataclass_rows_with_separating_line_produces_expected_table():
    data = [Person("Alice", 23, 169.5), SEPARATING_LINE, Person("Bob", 27, 175.0)]

    result = tabulate(data, headers="keys", tablefmt="simple")

    # headers should be derived from dataclass fields
    assert "name" in result
    assert "age" in result
    assert "height" in result

    # both rows' data should be present
    assert "Alice" in result
    assert "Bob" in result

    lines = result.splitlines()

    # There should be a separating line (a line made solely of '-' and spaces,
    # distinct from the header/table border lines) appearing between the two
    # data rows.
    alice_idx = next(i for i, l in enumerate(lines) if "Alice" in l)
    bob_idx = next(i for i, l in enumerate(lines) if "Bob" in l)
    assert bob_idx > alice_idx

    between_lines = lines[alice_idx + 1 : bob_idx]
    assert len(between_lines) >= 1
    # at least one of the lines between Alice and Bob should be a dashed
    # separator line (only dashes/spaces, no alphanumeric content)
    assert any(
        set(line.strip()) <= set("-") and line.strip() != ""
        for line in between_lines
    )


def test_dataclass_matches_dict_behavior_with_separating_line():
    # Using plain dicts with SEPARATING_LINE works; dataclasses should behave
    # the same way, producing structurally equivalent output.
    dict_data = [
        {"name": "Alice"
... [440 more chars]
```

## 5. Two-sided gate

### Against `buggy/` — exit 1 (must be non-zero)

```
       )  # columns have to be transposed
            elif hasattr(tabular_data, "index"):
                # values is a property, has .index => it's likely a pandas.DataFrame (pandas 0.11.0)
                keys = list(tabular_data)
                if (
                    showindex in ["default", "always", True]
                    and tabular_data.index.name is not None
                ):
                    if isinstance(tabular_data.index.name, list):
                        keys[:0] = tabular_data.index.name
                    else:
                        keys[:0] = [tabular_data.index.name]
                vals = tabular_data.values  # values matrix doesn't need to be transposed
                # for DataFrames add an index per default
                index = list(tabular_data.index)
                rows = [list(row) for row in vals]
            else:
                raise ValueError("tabular data doesn't appear to be a dict or a DataFrame")
    
            if headers == "keys":
                headers = list(map(str, keys))  # headers should be strings
    
        else:  # it's a usual iterable of iterables, or a NumPy array, or an iterable of dataclasses
            rows = list(tabular_data)
    
            if headers == "keys" and not rows:
                # an empty table (issue #81)
                headers = []
            elif (
                headers == "keys"
                and hasattr(tabular_data, "dtype")
                and getattr(tabular_data.dtype, "names")
            ):
                # numpy record array
                headers = tabular_data.dtype.names
            elif (
                headers == "keys"
                and len(rows) > 0
                and isinstance(rows[0], tuple)
                and hasattr(rows[0], "_fields")
            ):
                # namedtuple
                headers = list(map(str, rows[0]._fields))
            elif len(rows) > 0 and hasattr(rows[0], "keys") and hasattr(rows[0], "values"):
                # dict-like object
                uniq_keys = set()  # implements hashed lookup
                keys = []  # storage for set
                if headers == "firstrow":
                    firstd
... [800 more chars]
```

### Against `fixed/` — exit 1 (must be zero)

```
         rows = list(
                    izip_longest(*tabular_data.values())
                )  # columns have to be transposed
            elif hasattr(tabular_data, "index"):
                # values is a property, has .index => it's likely a pandas.DataFrame (pandas 0.11.0)
                keys = list(tabular_data)
                if (
                    showindex in ["default", "always", True]
                    and tabular_data.index.name is not None
                ):
                    if isinstance(tabular_data.index.name, list):
                        keys[:0] = tabular_data.index.name
                    else:
                        keys[:0] = [tabular_data.index.name]
                vals = tabular_data.values  # values matrix doesn't need to be transposed
                # for DataFrames add an index per default
                index = list(tabular_data.index)
                rows = [list(row) for row in vals]
            else:
                raise ValueError("tabular data doesn't appear to be a dict or a DataFrame")
    
            if headers == "keys":
                headers = list(map(str, keys))  # headers should be strings
    
        else:  # it's a usual iterable of iterables, or a NumPy array, or an iterable of dataclasses
            rows = list(tabular_data)
    
            if headers == "keys" and not rows:
                # an empty table (issue #81)
                headers = []
            elif (
                headers == "keys"
                and hasattr(tabular_data, "dtype")
                and getattr(tabular_data.dtype, "names")
            ):
                # numpy record array
                headers = tabular_data.dtype.names
            elif (
                headers == "keys"
                and len(rows) > 0
                and isinstance(rows[0], tuple)
                and hasattr(rows[0], "_fields")
            ):
                # namedtuple
                headers = list(map(str, rows[0]._fields))
            elif len(rows) > 0 and hasattr(rows[0], "keys") and hasattr(rows[0], "values"):
                # dict-like object
                uniq_keys = set()  # implements hashed lookup
                keys = []
... [800 more chars]
```

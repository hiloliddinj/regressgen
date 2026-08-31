# Trajectory — `v6-critic` on `tabulate-d29909b4`

**Verdict: WRONG_EXPECTATION**

- cost `$0.71126` · wall `220.7s` · tool calls `24`

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

You have `run_test`, which runs a candidate test file against the buggy code and
returns raw pytest output. Use it before submitting. If your test passes, it does
not reproduce the bug and you must rework it.

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

You cannot see the fixed code, so you cannot directly check the second half of
the gate. `try_fix` is how you approximate it: form a hypothesis about the
minimal source change that would fix the bug, apply it in a sc
... [732 more chars]
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

### 1. `search_code`(pattern="maxcolwidths|_wrap_text_to_colwidths|def _type")

Tool responded:

```
tabulate/__init__.py:963: def _type(string, has_invisible=True, numparse=True):
tabulate/__init__.py:1626: def _wrap_text_to_colwidths(list_of_lists, colwidths, numparses=True):
tabulate/__init__.py:1703: maxcolwidths=None,
tabulate/__init__.py:2213: maxcolwidths=[None, None, 30], \
tabulate/__init__.py:2236: if maxcolwidths is not None:
tabulate/__init__.py:2237: if type(maxcolwidths) is tuple:  # Check if tuple, convert to list if so
tabulate/__init__.py:2238: maxcolwidths = list(maxcolwidths)
tabulate/__init__.py:2243: if isinstance(maxcolwidths, int):  # Expand scalar for all columns
tabulate/__init__.py:2244: maxcolwidths = _expand_iterable(maxcolwidths, num_cols, maxcolwidths)
tabulate/__init__.py:2246: maxcolwidths = _expand_iterable(maxcolwidths, num_cols, None)
tabulate/__init__.py:2249: list_of_lists = _wrap_text_to_colwidths(
tabulate/__init__.py:2250: list_of_lists, maxcolwidths, numparses=numparses
tabulate/__init__.py:2263: headers = _wrap_text_to_colwidths(
test/test_api.py:54: ("maxcolwidths", None),
test/test_internal.py:150: def test_wrap_text_to_colwidths():
test/test_internal.py:151: "Internal: Test _wrap_text_to_colwidths to show it will wrap text based on colwidths"
test/test_internal.py:171: result = T._wrap_text_to_colwidths(rows, widths)
test/test_internal.py:191: result = T._wrap_text_to_colwidths(rows, widths)
test/test_internal.py:197: """Internal: Test _wrap_text_to_colwidths force ignores numbers by
test/test_internal.py:209: result = T._wrap_text_to_colwidths(rows, widths, numparses=[True, True, False])
test/test_internal.py:213: def test_wrap_text_to_colwidths_single_ansi_colors_full_cell():
test/test_internal.py:224: result = T._wrap_text_to_colwidths(data, [30])
test/test_internal.py:240: def test_wrap_text_to_colwidths_colors_wide_char():
test/test_internal.py:245: skip("test_wrap_text_to_colwidths_colors_wide_char is skipped")
test/test_internal.py:248: result = T._wrap_text_to_colwidths(data, [30])
test/test_internal.py:264: def test_wrap_text_to_colwidths_multi_ansi_colors_full_cell():
test/test_internal.py:276: result = T._wrap_text_to_colwidths(data, [30])
test/test_internal.py:292: def test_wrap_text_to_colwidths_multi_an
... [300 more chars]
```

### 2. `read_file`(path="tabulate/__init__.py", start=955, end=1000)

Tool responded:

```
tabulate/__init__.py lines 955-1000 of 3000

  955|     >>> _isbool(1)
  956|     False
  957|     """
  958|     return type(string) is bool or (
  959|         isinstance(string, (bytes, str)) and string in ("True", "False")
  960|     )
  961| 
  962| 
  963| def _type(string, has_invisible=True, numparse=True):
  964|     """The least generic type (type(None), int, float, str, unicode).
  965| 
  966|     Treats empty string as missing for the purposes of type deduction, so as to not influence
  967|     the type of an otherwise complete column; does *not* result in missingval replacement!
  968| 
  969|     >>> _type(None) is type(None)
  970|     True
  971|     >>> _type("") is type(None)
  972|     True
  973|     >>> _type("foo") is type("")
  974|     True
  975|     >>> _type("1") is type(1)
  976|     True
  977|     >>> _type('\x1b[31m42\x1b[0m') is type(42)
  978|     True
  979|     >>> _type('\x1b[31m42\x1b[0m') is type(42)
  980|     True
  981| 
  982|     """
  983| 
  984|     if has_invisible and isinstance(string, (str, bytes)):
  985|         string = _strip_ansi(string)
  986| 
  987|     if string is None or (isinstance(string, (bytes, str)) and not string):
  988|         return type(None)
  989|     elif hasattr(string, "isoformat"):  # datetime.datetime, date, and time
  990|         return str
  991|     elif _isbool(string):
  992|         return bool
  993|     elif numparse and (
  994|         _isint(string)
  995|         or (
  996|             isinstance(string, str)
  997|             and _isnumber_with_thousands_separator(string)
  998|             and "." not in string
  999|         )
 1000|     ):
```

### 3. `read_file`(path="tabulate/__init__.py", start=1620, end=1670)

Tool responded:

```
tabulate/__init__.py lines 1620-1670 of 3000

 1620|         headers_pad = max(0, len(rows[0]) - len(headers))
 1621|         headers = [""] * headers_pad + headers
 1622| 
 1623|     return rows, headers, headers_pad
 1624| 
 1625| 
 1626| def _wrap_text_to_colwidths(list_of_lists, colwidths, numparses=True):
 1627|     if len(list_of_lists):
 1628|         num_cols = len(list_of_lists[0])
 1629|     else:
 1630|         num_cols = 0
 1631|     numparses = _expand_iterable(numparses, num_cols, True)
 1632| 
 1633|     result = []
 1634| 
 1635|     for row in list_of_lists:
 1636|         new_row = []
 1637|         for cell, width, numparse in zip(row, colwidths, numparses):
 1638|             if _isnumber(cell) and numparse:
 1639|                 new_row.append(cell)
 1640|                 continue
 1641| 
 1642|             if width is not None:
 1643|                 wrapper = _CustomTextWrap(width=width)
 1644|                 # Cast based on our internal type handling. Any future custom
 1645|                 # formatting of types (such as datetimes) may need to be more
 1646|                 # explicit than just `str` of the object. Also doesn't work for
 1647|                 # custom floatfmt/intfmt, nor with any missing/blank cells.
 1648|                 casted_cell = (
 1649|                     str(cell) if _isnumber(cell) else _type(cell, numparse)(cell)
 1650|                 )
 1651|                 wrapped = [
 1652|                     "\n".join(wrapper.wrap(line))
 1653|                     for line in casted_cell.splitlines()
 1654|                     if line.strip() != ""
 1655|                 ]
 1656|                 new_row.append("\n".join(wrapped))
 1657|             else:
 1658|                 new_row.append(cell)
 1659|         result.append(new_row)
 1660| 
 1661|     return result
 1662| 
 1663| 
 1664| def _to_str(s, encoding="utf8", errors="ignore"):
 1665|     """
 1666|     A type safe wrapper for converting a bytestring to str. This is essentially just
 1667|     a wrapper around .decode() intended for use with things like map(), but with some
 1668|     specific behavior:
 1669| 
 1670|     1. if the given parameter is not
... [40 more chars]
```

### 4. `read_file`(path="test/test_textwrapper.py", start=185, end=225)

Tool responded:

```
test/test_textwrapper.py lines 185-222 of 222

  185|     wrapper = CTW(width=10)
  186|     result = wrapper.wrap(data)
  187|     assert_equal(expected, result)
  188| 
  189|     clean_data = _strip_ansi(data)
  190|     for width in range(2, len(clean_data)):
  191|         wrapper = CTW(width=width)
  192|         result = wrapper.wrap(data)
  193|         # Comparing after stripping ANSI should be enough to catch broken escape codes
  194|         assert_equal(clean_data, _strip_ansi("".join(result)))
  195| 
  196| 
  197| def test_wrap_datetime():
  198|     """TextWrapper: Show that datetimes can be wrapped without crashing"""
  199|     data = [
  200|         ["First Entry", datetime.datetime(2020, 1, 1, 5, 6, 7)],
  201|         ["Second Entry", datetime.datetime(2021, 2, 2, 0, 0, 0)],
  202|     ]
  203|     headers = ["Title", "When"]
  204|     result = tabulate(data, headers=headers, tablefmt="grid", maxcolwidths=[7, 5])
  205| 
  206|     expected = [
  207|         "+---------+--------+",
  208|         "| Title   | When   |",
  209|         "+=========+========+",
  210|         "| First   | 2020-  |",
  211|         "| Entry   | 01-01  |",
  212|         "|         | 05:06  |",
  213|         "|         | :07    |",
  214|         "+---------+--------+",
  215|         "| Second  | 2021-  |",
  216|         "| Entry   | 02-02  |",
  217|         "|         | 00:00  |",
  218|         "|         | :00    |",
  219|         "+---------+--------+",
  220|     ]
  221|     expected = "\n".join(expected)
  222|     assert_equal(expected, result)
```

### 5. `run_test`(test_source="from tabulate import tabulate\n\n\ndef test_maxcolwidths_with_bool_and_none_cells():\n    data = [\n        [)

Tool responded:

```
FAILED (exit 1)

F                                                                        [100%]
=================================== FAILURES ===================================
__________________ test_maxcolwidths_with_bool_and_none_cells __________________

    def test_maxcolwidths_with_bool_and_none_cells():
        data = [
            ["First Entry", "True"],
            ["Second Entry", None],
        ]
        headers = ["Title", "When"]
>       result = tabulate(data, headers=headers, tablefmt="grid", maxcolwidths=[7, 5])
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

test/test_regressgen_candidate.py:10: 
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
                    casted_cell = (
                        str(cell) if _isnumber(cell) else _type(cell, numparse)(cell)
                    )
                    wrapped = [
                        "\n".join(wr
... [300 more chars]
```

### 6. `try_fix`(path="tabulate/__init__.py", find="                casted_cell = (\n                    str(cell) if _isnumber(cell) else _type(cell, numparse)()

Tool responded:

```
your test STILL FAILS with this fix
existing suite still green

============ FAILURES ===================================
__________________ test_maxcolwidths_with_bool_and_none_cells __________________

    def test_maxcolwidths_with_bool_and_none_cells():
        data = [
            ["First Entry", "True"],
            ["Second Entry", None],
        ]
        headers = ["Title", "When"]
        result = tabulate(data, headers=headers, tablefmt="grid", maxcolwidths=[7, 5])
    
        expected = "\n".join(
            [
                "+---------+-------+",
                "| Title   | When  |",
                "+=========+=======+",
                "| First   | True  |",
                "| Entry   |       |",
                "+---------+-------+",
                "| Second  |       |",
                "| Entry   |       |",
                "+---------+-------+",
            ]
        )
>       assert result == expected
E       AssertionError: assert '+---------+-...---+--------+' == '+---------+-...----+-------+'
E         
E         - +---------+-------+
E         + +---------+--------+
E         ?                   +
E         - | Title   | When  |
E         + | Title   | When   |
E         ?                   +...
E         
E         ...Full output truncated (21 lines hidden), use '-vv' to show

test/test_regressgen_candidate.py:25: AssertionError
=========================== short test summary info ============================
FAILED test/test_regressgen_candidate.py::test_maxcolwidths_with_bool_and_none_cells
1 failed in 0.10s
```

### 7. `try_fix`(path="tabulate/__init__.py", find="                casted_cell = (\n                    str(cell) if _isnumber(cell) else _type(cell, numparse)()

Tool responded:

```
your test STILL FAILS with this fix
existing suite still green

F                                                                        [100%]
=================================== FAILURES ===================================
__________________ test_maxcolwidths_with_bool_and_none_cells __________________

    def test_maxcolwidths_with_bool_and_none_cells():
        data = [
            ["First Entry", "True"],
            ["Second Entry", None],
        ]
        headers = ["Title", "When"]
        result = tabulate(data, headers=headers, tablefmt="grid", maxcolwidths=[7, 5])
>       raise AssertionError(repr(result))
E       AssertionError: '+---------+--------+\n| Title   | When   |\n+=========+========+\n| First   | True   |\n| Entry   |        |\n+---------+--------+\n| Second  |        |\n| Entry   |        |\n+---------+--------+'

test/test_regressgen_candidate.py:11: AssertionError
=========================== short test summary info ============================
FAILED test/test_regressgen_candidate.py::test_maxcolwidths_with_bool_and_none_cells
1 failed in 0.09s
```

### 8. `try_fix`(path="tabulate/__init__.py", find="                casted_cell = (\n                    str(cell) if _isnumber(cell) else _type(cell, numparse)()

Tool responded:

```
your test PASSES with this fix
existing suite still green

.                                                                        [100%]
1 passed in 0.08s
```

### 9. `run_test`(test_source="from tabulate import tabulate\n\n\ndef test_maxcolwidths_with_bool_and_none_cells():\n    \"\"\"Regression: m)

Tool responded:

```
FAILED (exit 1)

F                                                                        [100%]
=================================== FAILURES ===================================
__________________ test_maxcolwidths_with_bool_and_none_cells __________________

    def test_maxcolwidths_with_bool_and_none_cells():
        """Regression: maxcolwidths should wrap 'True'/'False' strings and None
        cells instead of raising AttributeError during text wrapping."""
        data = [
            ["First Entry", "True"],
            ["Second Entry", None],
        ]
        headers = ["Title", "When"]
>       result = tabulate(data, headers=headers, tablefmt="grid", maxcolwidths=[7, 5])
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

test/test_regressgen_candidate.py:12: 
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
                    casted_cell = (
                       
... [300 more chars]
```

### 10. `submit_test`(rationale="The bug report says tabulate() raises an exception when maxcolwidths is combined with a \"True\"/\"False\" st)

Tool responded:

```
Submitted.

from tabulate import tabulate


def test_maxcolwidths_with_bool_and_none_cells():
    """Regression: maxcolwidths should wrap 'True'/'False' strings and None
    cells instead of raising AttributeError during text wrapping.

    See bug report: using maxcolwidths on a table containing a "True"/"False"
    string cell or a None cell raised an exception (AttributeError) inside
    _wrap_text_to_colwidths because the type-detection logic (_type) casts
    "True"/"False" strings to an actual bool, and None to None, neither of
    which support .splitlines(). Expected behavior: these should be wrapped
    like normal strings ("True"/"False" as text, None as blank).
    """
    data = [
        ["First Entry", "True"],
        ["Second Entry", None],
    ]
    headers = ["Title", "When"]
    result = tabulate(data, headers=headers, tablefmt="grid", maxcolwidths=[7, 5])

    expected = "\n".join(
        [
            "+---------+--------+",
            "| Title   | When   |",
            "+=========+========+",
            "| First   | True   |",
            "| Entry   |        |",
            "+---------+--------+",
            "| Second  |        |",
            "| Entry   |        |",
            "+---------+--------+",
        ]
    )
    assert result == expected
```

### 11. `critic`()

Tool responded:

```
VERDICT: APPROVE

The test's expected table layout (borders, column widths, and cell wrapping) matches exactly what an already-passing analogous test (`test_wrap_datetime` in `test/test_textwrapper.py`, which uses the identical `data`/`headers` structure and `maxcolwidths=[7, 5]`) produces for column 0, confirming the width/padding math (`+---------+--------+`, `Title`/`When` header row, `Second`/`Entry` wrapping) is correct. Tracing `_wrap_text_to_colwidths` and `_type`/`_format` confirms that once the type-detection bug is fixed so that string "True" and `None` are cast via `str`/empty-string logic instead of `bool`/`NoneType`, "True" wraps unchanged and `None` becomes an empty cell — exactly matching the bug report's stated expectation and the test's expected output. No incidental or currently-broken behavior is being asserted.
```

### 12. `search_code`(pattern="_wrap_text_to_colwidths")

Tool responded:

```
tabulate/__init__.py:1626: def _wrap_text_to_colwidths(list_of_lists, colwidths, numparses=True):
tabulate/__init__.py:2249: list_of_lists = _wrap_text_to_colwidths(
tabulate/__init__.py:2263: headers = _wrap_text_to_colwidths(
test/test_internal.py:150: def test_wrap_text_to_colwidths():
test/test_internal.py:151: "Internal: Test _wrap_text_to_colwidths to show it will wrap text based on colwidths"
test/test_internal.py:171: result = T._wrap_text_to_colwidths(rows, widths)
test/test_internal.py:191: result = T._wrap_text_to_colwidths(rows, widths)
test/test_internal.py:197: """Internal: Test _wrap_text_to_colwidths force ignores numbers by
test/test_internal.py:209: result = T._wrap_text_to_colwidths(rows, widths, numparses=[True, True, False])
test/test_internal.py:213: def test_wrap_text_to_colwidths_single_ansi_colors_full_cell():
test/test_internal.py:224: result = T._wrap_text_to_colwidths(data, [30])
test/test_internal.py:240: def test_wrap_text_to_colwidths_colors_wide_char():
test/test_internal.py:245: skip("test_wrap_text_to_colwidths_colors_wide_char is skipped")
test/test_internal.py:248: result = T._wrap_text_to_colwidths(data, [30])
test/test_internal.py:264: def test_wrap_text_to_colwidths_multi_ansi_colors_full_cell():
test/test_internal.py:276: result = T._wrap_text_to_colwidths(data, [30])
test/test_internal.py:292: def test_wrap_text_to_colwidths_multi_ansi_colors_in_subset():
test/test_internal.py:303: result = T._wrap_text_to_colwidths(data, [30])
```

### 13. `search_code`(pattern="def _type")

Tool responded:

```
tabulate/__init__.py:963: def _type(string, has_invisible=True, numparse=True):
```

### 14. `read_file`(path="tabulate/__init__.py", start=1626, end=1680)

Tool responded:

```
tabulate/__init__.py lines 1626-1680 of 3000

 1626| def _wrap_text_to_colwidths(list_of_lists, colwidths, numparses=True):
 1627|     if len(list_of_lists):
 1628|         num_cols = len(list_of_lists[0])
 1629|     else:
 1630|         num_cols = 0
 1631|     numparses = _expand_iterable(numparses, num_cols, True)
 1632| 
 1633|     result = []
 1634| 
 1635|     for row in list_of_lists:
 1636|         new_row = []
 1637|         for cell, width, numparse in zip(row, colwidths, numparses):
 1638|             if _isnumber(cell) and numparse:
 1639|                 new_row.append(cell)
 1640|                 continue
 1641| 
 1642|             if width is not None:
 1643|                 wrapper = _CustomTextWrap(width=width)
 1644|                 # Cast based on our internal type handling. Any future custom
 1645|                 # formatting of types (such as datetimes) may need to be more
 1646|                 # explicit than just `str` of the object. Also doesn't work for
 1647|                 # custom floatfmt/intfmt, nor with any missing/blank cells.
 1648|                 casted_cell = (
 1649|                     str(cell) if _isnumber(cell) else _type(cell, numparse)(cell)
 1650|                 )
 1651|                 wrapped = [
 1652|                     "\n".join(wrapper.wrap(line))
 1653|                     for line in casted_cell.splitlines()
 1654|                     if line.strip() != ""
 1655|                 ]
 1656|                 new_row.append("\n".join(wrapped))
 1657|             else:
 1658|                 new_row.append(cell)
 1659|         result.append(new_row)
 1660| 
 1661|     return result
 1662| 
 1663| 
 1664| def _to_str(s, encoding="utf8", errors="ignore"):
 1665|     """
 1666|     A type safe wrapper for converting a bytestring to str. This is essentially just
 1667|     a wrapper around .decode() intended for use with things like map(), but with some
 1668|     specific behavior:
 1669| 
 1670|     1. if the given parameter is not a bytestring, it is returned unmodified
 1671|     2. decode() is called for the given parameter and assumes utf8 encoding, but the
 1672|        default error behavior is changed from 's
... [186 more chars]
```

### 15. `read_file`(path="tabulate/__init__.py", start=963, end=1000)

Tool responded:

```
tabulate/__init__.py lines 963-1000 of 3000

  963| def _type(string, has_invisible=True, numparse=True):
  964|     """The least generic type (type(None), int, float, str, unicode).
  965| 
  966|     Treats empty string as missing for the purposes of type deduction, so as to not influence
  967|     the type of an otherwise complete column; does *not* result in missingval replacement!
  968| 
  969|     >>> _type(None) is type(None)
  970|     True
  971|     >>> _type("") is type(None)
  972|     True
  973|     >>> _type("foo") is type("")
  974|     True
  975|     >>> _type("1") is type(1)
  976|     True
  977|     >>> _type('\x1b[31m42\x1b[0m') is type(42)
  978|     True
  979|     >>> _type('\x1b[31m42\x1b[0m') is type(42)
  980|     True
  981| 
  982|     """
  983| 
  984|     if has_invisible and isinstance(string, (str, bytes)):
  985|         string = _strip_ansi(string)
  986| 
  987|     if string is None or (isinstance(string, (bytes, str)) and not string):
  988|         return type(None)
  989|     elif hasattr(string, "isoformat"):  # datetime.datetime, date, and time
  990|         return str
  991|     elif _isbool(string):
  992|         return bool
  993|     elif numparse and (
  994|         _isint(string)
  995|         or (
  996|             isinstance(string, str)
  997|             and _isnumber_with_thousands_separator(string)
  998|             and "." not in string
  999|         )
 1000|     ):
```

### 16. `read_file`(path="tabulate/__init__.py", start=2230, end=2270)

Tool responded:

```
tabulate/__init__.py lines 2230-2270 of 3000

 2230| 
 2231|     list_of_lists, headers, headers_pad = _normalize_tabular_data(
 2232|         tabular_data, headers, showindex=showindex
 2233|     )
 2234|     list_of_lists, separating_lines = _remove_separating_lines(list_of_lists)
 2235| 
 2236|     if maxcolwidths is not None:
 2237|         if type(maxcolwidths) is tuple:  # Check if tuple, convert to list if so
 2238|             maxcolwidths = list(maxcolwidths)
 2239|         if len(list_of_lists):
 2240|             num_cols = len(list_of_lists[0])
 2241|         else:
 2242|             num_cols = 0
 2243|         if isinstance(maxcolwidths, int):  # Expand scalar for all columns
 2244|             maxcolwidths = _expand_iterable(maxcolwidths, num_cols, maxcolwidths)
 2245|         else:  # Ignore col width for any 'trailing' columns
 2246|             maxcolwidths = _expand_iterable(maxcolwidths, num_cols, None)
 2247| 
 2248|         numparses = _expand_numparse(disable_numparse, num_cols)
 2249|         list_of_lists = _wrap_text_to_colwidths(
 2250|             list_of_lists, maxcolwidths, numparses=numparses
 2251|         )
 2252| 
 2253|     if maxheadercolwidths is not None:
 2254|         num_cols = len(list_of_lists[0])
 2255|         if isinstance(maxheadercolwidths, int):  # Expand scalar for all columns
 2256|             maxheadercolwidths = _expand_iterable(
 2257|                 maxheadercolwidths, num_cols, maxheadercolwidths
 2258|             )
 2259|         else:  # Ignore col width for any 'trailing' columns
 2260|             maxheadercolwidths = _expand_iterable(maxheadercolwidths, num_cols, None)
 2261| 
 2262|         numparses = _expand_numparse(disable_numparse, num_cols)
 2263|         headers = _wrap_text_to_colwidths(
 2264|             [headers], maxheadercolwidths, numparses=numparses
 2265|         )[0]
 2266| 
 2267|     # empty values in the first column of RST tables should be escaped (issue #82)
 2268|     # "" should be escaped as "\\ " or ".."
 2269|     if tablefmt == "rst":
 2270|         list_of_lists, headers = _rst_escape_first_column(list_of_lists, headers)
```

### 17. `read_file`(path="tabulate/__init__.py", start=1580, end=1626)

Tool responded:

```
tabulate/__init__.py lines 1580-1626 of 3000

 1580|             rows = [[getattr(row, f) for f in field_names] for row in rows]
 1581| 
 1582|         elif headers == "keys" and len(rows) > 0:
 1583|             # keys are column indices
 1584|             headers = list(map(str, range(len(rows[0]))))
 1585| 
 1586|     # take headers from the first row if necessary
 1587|     if headers == "firstrow" and len(rows) > 0:
 1588|         if index is not None:
 1589|             headers = [index[0]] + list(rows[0])
 1590|             index = index[1:]
 1591|         else:
 1592|             headers = rows[0]
 1593|         headers = list(map(str, headers))  # headers should be strings
 1594|         rows = rows[1:]
 1595|     elif headers == "firstrow":
 1596|         headers = []
 1597| 
 1598|     headers = list(map(str, headers))
 1599|     #    rows = list(map(list, rows))
 1600|     rows = list(map(lambda r: r if _is_separating_line(r) else list(r), rows))
 1601| 
 1602|     # add or remove an index column
 1603|     showindex_is_a_str = type(showindex) in [str, bytes]
 1604|     if showindex == "default" and index is not None:
 1605|         rows = _prepend_row_index(rows, index)
 1606|     elif isinstance(showindex, Sized) and not showindex_is_a_str:
 1607|         rows = _prepend_row_index(rows, list(showindex))
 1608|     elif isinstance(showindex, Iterable) and not showindex_is_a_str:
 1609|         rows = _prepend_row_index(rows, showindex)
 1610|     elif showindex == "always" or (_bool(showindex) and not showindex_is_a_str):
 1611|         if index is None:
 1612|             index = list(range(len(rows)))
 1613|         rows = _prepend_row_index(rows, index)
 1614|     elif showindex == "never" or (not _bool(showindex) and not showindex_is_a_str):
 1615|         pass
 1616| 
 1617|     # pad with empty headers for initial columns if necessary
 1618|     headers_pad = 0
 1619|     if headers and len(rows) > 0:
 1620|         headers_pad = max(0, len(rows[0]) - len(headers))
 1621|         headers = [""] * headers_pad + headers
 1622| 
 1623|     return rows, headers, headers_pad
 1624| 
 1625| 
 1626| def _wrap_text_to_colwidths(list_of_lists, colwidth
... [19 more chars]
```

### 18. `search_code`(pattern="maxcolwidths")

Tool responded:

```
tabulate/__init__.py:1703: maxcolwidths=None,
tabulate/__init__.py:2213: maxcolwidths=[None, None, 30], \
tabulate/__init__.py:2236: if maxcolwidths is not None:
tabulate/__init__.py:2237: if type(maxcolwidths) is tuple:  # Check if tuple, convert to list if so
tabulate/__init__.py:2238: maxcolwidths = list(maxcolwidths)
tabulate/__init__.py:2243: if isinstance(maxcolwidths, int):  # Expand scalar for all columns
tabulate/__init__.py:2244: maxcolwidths = _expand_iterable(maxcolwidths, num_cols, maxcolwidths)
tabulate/__init__.py:2246: maxcolwidths = _expand_iterable(maxcolwidths, num_cols, None)
tabulate/__init__.py:2250: list_of_lists, maxcolwidths, numparses=numparses
test/test_api.py:54: ("maxcolwidths", None),
test/test_output.py:109: table, headers="firstrow", tablefmt="plain", maxcolwidths=[10, 10]
test/test_output.py:126: table, headers="firstrow", tablefmt="plain", maxcolwidths=[10, 10]
test/test_output.py:154: table, headers="firstrow", tablefmt="plain", maxcolwidths=[10, 30]
test/test_output.py:174: result = tabulate(table, headers="firstrow", tablefmt="plain", maxcolwidths=6)
test/test_output.py:193: table, headers="firstrow", tablefmt="plain", maxcolwidths=[None, 6]
test/test_output.py:217: result = tabulate(table, tablefmt="grid", maxcolwidths=6, disable_numparse=[2])
test/test_output.py:229: maxcolwidths=[10, 10],
test/test_regression.py:475: def test_preserve_line_breaks_with_maxcolwidths():
test/test_regression.py:476: "Regression: preserve line breaks when using maxcolwidths (github issue #190)"
test/test_regression.py:487: result = tabulate(table, tablefmt="grid", maxcolwidths=10)
test/test_regression.py:491: def test_maxcolwidths_accepts_list_or_tuple():
test/test_regression.py:492: "Regression: maxcolwidths can accept a list or a tuple (github issue #214)"
test/test_regression.py:504: # test with maxcolwidths as a list
test/test_regression.py:505: result = tabulate(table, tablefmt="grid", maxcolwidths=[12, 8])
test/test_regression.py:507: # test with maxcolwidths as a tuple
test/test_regression.py:508: result = tabulate(table, tablefmt="grid", maxcolwidths=(12, 8))
test/test_regression.py:512: def test_exception_on_empty_data_with_maxcolwidth
... [291 more chars]
```

### 19. `read_file`(path="test/test_textwrapper.py", start=180, end=230)

Tool responded:

```
test/test_textwrapper.py lines 180-222 of 222

  180|     data = "012345(\x1b[32ma\x1b[0mbc\x1b[32mdefghij\x1b[0m)"
  181|     expected = [
  182|         "012345(\x1b[32ma\x1b[0mbc\x1b[32m\x1b[0m",
  183|         "\x1b[32mdefghij\x1b[0m)",
  184|     ]
  185|     wrapper = CTW(width=10)
  186|     result = wrapper.wrap(data)
  187|     assert_equal(expected, result)
  188| 
  189|     clean_data = _strip_ansi(data)
  190|     for width in range(2, len(clean_data)):
  191|         wrapper = CTW(width=width)
  192|         result = wrapper.wrap(data)
  193|         # Comparing after stripping ANSI should be enough to catch broken escape codes
  194|         assert_equal(clean_data, _strip_ansi("".join(result)))
  195| 
  196| 
  197| def test_wrap_datetime():
  198|     """TextWrapper: Show that datetimes can be wrapped without crashing"""
  199|     data = [
  200|         ["First Entry", datetime.datetime(2020, 1, 1, 5, 6, 7)],
  201|         ["Second Entry", datetime.datetime(2021, 2, 2, 0, 0, 0)],
  202|     ]
  203|     headers = ["Title", "When"]
  204|     result = tabulate(data, headers=headers, tablefmt="grid", maxcolwidths=[7, 5])
  205| 
  206|     expected = [
  207|         "+---------+--------+",
  208|         "| Title   | When   |",
  209|         "+=========+========+",
  210|         "| First   | 2020-  |",
  211|         "| Entry   | 01-01  |",
  212|         "|         | 05:06  |",
  213|         "|         | :07    |",
  214|         "+---------+--------+",
  215|         "| Second  | 2021-  |",
  216|         "| Entry   | 02-02  |",
  217|         "|         | 00:00  |",
  218|         "|         | :00    |",
  219|         "+---------+--------+",
  220|     ]
  221|     expected = "\n".join(expected)
  222|     assert_equal(expected, result)
```

### 20. `read_file`(path="test/test_regression.py", start=470, end=516)

Tool responded:

```
test/test_regression.py lines 470-516 of 547

  470|     expected = "1  a\n2  b\n3  c"
  471|     result = tabulate(table, showindex=count(1), tablefmt="plain")
  472|     assert_equal(expected, result)
  473| 
  474| 
  475| def test_preserve_line_breaks_with_maxcolwidths():
  476|     "Regression: preserve line breaks when using maxcolwidths (github issue #190)"
  477|     table = [["123456789 bbb\nccc"]]
  478|     expected = "\n".join(
  479|         [
  480|             "+-----------+",
  481|             "| 123456789 |",
  482|             "| bbb       |",
  483|             "| ccc       |",
  484|             "+-----------+",
  485|         ]
  486|     )
  487|     result = tabulate(table, tablefmt="grid", maxcolwidths=10)
  488|     assert_equal(expected, result)
  489| 
  490| 
  491| def test_maxcolwidths_accepts_list_or_tuple():
  492|     "Regression: maxcolwidths can accept a list or a tuple (github issue #214)"
  493|     table = [["lorem ipsum dolor sit amet"] * 3]
  494|     expected = "\n".join(
  495|         [
  496|             "+-------------+----------+----------------------------+",
  497|             "| lorem ipsum | lorem    | lorem ipsum dolor sit amet |",
  498|             "| dolor sit   | ipsum    |                            |",
  499|             "| amet        | dolor    |                            |",
  500|             "|             | sit amet |                            |",
  501|             "+-------------+----------+----------------------------+",
  502|         ]
  503|     )
  504|     # test with maxcolwidths as a list
  505|     result = tabulate(table, tablefmt="grid", maxcolwidths=[12, 8])
  506|     assert_equal(expected, result)
  507|     # test with maxcolwidths as a tuple
  508|     result = tabulate(table, tablefmt="grid", maxcolwidths=(12, 8))
  509|     assert_equal(expected, result)
  510| 
  511| 
  512| def test_exception_on_empty_data_with_maxcolwidths():
  513|     "Regression: exception on empty data when using maxcolwidths (github issue #180)"
  514|     result = tabulate([], maxcolwidths=5)
  515|     assert_equal(result, "")
  516|
```

### 21. `search_code`(pattern="MIN_PADDING")

Tool responded:

```
tabulate/__init__.py:34: MIN_PADDING = 2
tabulate/__init__.py:2276: min_padding = MIN_PADDING
```

### 22. `read_file`(path="tabulate/__init__.py", start=2271, end=2310)

Tool responded:

```
tabulate/__init__.py lines 2271-2310 of 3000

 2271| 
 2272|     # PrettyTable formatting does not use any extra padding.
 2273|     # Numbers are not parsed and are treated the same as strings for alignment.
 2274|     # Check if pretty is the format being used and override the defaults so it
 2275|     # does not impact other formats.
 2276|     min_padding = MIN_PADDING
 2277|     if tablefmt == "pretty":
 2278|         min_padding = 0
 2279|         disable_numparse = True
 2280|         numalign = "center" if numalign == _DEFAULT_ALIGN else numalign
 2281|         stralign = "center" if stralign == _DEFAULT_ALIGN else stralign
 2282|     else:
 2283|         numalign = "decimal" if numalign == _DEFAULT_ALIGN else numalign
 2284|         stralign = "left" if stralign == _DEFAULT_ALIGN else stralign
 2285| 
 2286|     # 'colon_grid' uses colons in the line beneath the header to represent a column's
 2287|     # alignment instead of literally aligning the text differently. Hence,
 2288|     # left alignment of the data in the text output is enforced.
 2289|     if tablefmt == "colon_grid":
 2290|         colglobalalign = "left"
 2291|         headersglobalalign = "left"
 2292| 
 2293|     # optimization: look for ANSI control codes once,
 2294|     # enable smart width functions only if a control code is found
 2295|     #
 2296|     # convert the headers and rows into a single, tab-delimited string ensuring
 2297|     # that any bytestrings are decoded safely (i.e. errors ignored)
 2298|     plain_text = "\t".join(
 2299|         chain(
 2300|             # headers
 2301|             map(_to_str, headers),
 2302|             # rows: chain the rows together into a single iterable after mapping
 2303|             # the bytestring conversino to each cell value
 2304|             chain.from_iterable(map(_to_str, row) for row in list_of_lists),
 2305|         )
 2306|     )
 2307| 
 2308|     has_invisible = _ansi_codes.search(plain_text) is not None
 2309| 
 2310|     enable_widechars = wcwidth is not None and WIDE_CHARS_MODE
```

### 23. `search_code`(pattern="missingval")

Tool responded:

```
tabulate/__init__.py:967: the type of an otherwise complete column; does *not* result in missingval replacement!
tabulate/__init__.py:1298: def _format(val, valtype, floatfmt, intfmt, missingval="", has_invisible=True):
tabulate/__init__.py:1311: return missingval
tabulate/__init__.py:1697: missingval=_DEFAULT_MISSINGVAL,
tabulate/__init__.py:1799: `None` values are replaced with a `missingval` string (like
tabulate/__init__.py:1805: ...                 ["other", None, 2.7]], missingval="?"))
tabulate/__init__.py:2342: if isinstance(missingval, str):
tabulate/__init__.py:2343: missing_vals = len(cols) * [missingval]
tabulate/__init__.py:2345: missing_vals = list(missingval)
test/test_api.py:48: ("missingval", ""),
test/test_output.py:2993: def test_missingval():
test/test_output.py:2996: [["Alice", 10], ["Bob", None]], missingval="n/a", tablefmt="plain"
test/test_output.py:3002: def test_missingval_multi():
test/test_output.py:3006: missingval=("n/a", "?"),
test/test_output.py:3026: missingval="?",
```

### 24. `read_file`(path="tabulate/__init__.py", start=1298, end=1340)

Tool responded:

```
tabulate/__init__.py lines 1298-1340 of 3000

 1298| def _format(val, valtype, floatfmt, intfmt, missingval="", has_invisible=True):
 1299|     """Format a value according to its deduced type.  Empty values are deemed valid for any type.
 1300| 
 1301|     Unicode is supported:
 1302| 
 1303|     >>> hrow = ['\u0431\u0443\u043a\u0432\u0430', '\u0446\u0438\u0444\u0440\u0430'] ; \
 1304|         tbl = [['\u0430\u0437', 2], ['\u0431\u0443\u043a\u0438', 4]] ; \
 1305|         good_result = '\\u0431\\u0443\\u043a\\u0432\\u0430      \\u0446\\u0438\\u0444\\u0440\\u0430\\n-------  -------\\n\\u0430\\u0437             2\\n\\u0431\\u0443\\u043a\\u0438           4' ; \
 1306|         tabulate(tbl, headers=hrow) == good_result
 1307|     True
 1308| 
 1309|     """  # noqa
 1310|     if val is None:
 1311|         return missingval
 1312|     if isinstance(val, (bytes, str)) and not val:
 1313|         return ""
 1314| 
 1315|     if valtype is str:
 1316|         return f"{val}"
 1317|     elif valtype is int:
 1318|         if isinstance(val, str):
 1319|             val_striped = val.encode("unicode_escape").decode("utf-8")
 1320|             colored = re.search(
 1321|                 r"(\\[xX]+[0-9a-fA-F]+\[\d+[mM]+)([0-9.]+)(\\.*)$", val_striped
 1322|             )
 1323|             if colored:
 1324|                 total_groups = len(colored.groups())
 1325|                 if total_groups == 3:
 1326|                     digits = colored.group(2)
 1327|                     if digits.isdigit():
 1328|                         val_new = (
 1329|                             colored.group(1)
 1330|                             + format(int(digits), intfmt)
 1331|                             + colored.group(3)
 1332|                         )
 1333|                         val = val_new.encode("utf-8").decode("unicode_escape")
 1334|             intfmt = ""
 1335|         return format(val, intfmt)
 1336|     elif valtype is bytes:
 1337|         try:
 1338|             return str(val, "ascii")
 1339|         except (TypeError, UnicodeDecodeError):
 1340|             return str(val)
```

## 4. Submitted test

```python
from tabulate import tabulate


def test_maxcolwidths_with_bool_and_none_cells():
    """Regression: maxcolwidths should wrap 'True'/'False' strings and None
    cells instead of raising AttributeError during text wrapping.

    See bug report: using maxcolwidths on a table containing a "True"/"False"
    string cell or a None cell raised an exception (AttributeError) inside
    _wrap_text_to_colwidths because the type-detection logic (_type) casts
    "True"/"False" strings to an actual bool, and None to None, neither of
    which support .splitlines(). Expected behavior: these should be wrapped
    like normal strings ("True"/"False" as text, None as blank).
    """
    data = [
        ["First Entry", "True"],
        ["Second Entry", None],
    ]
    headers = ["Title", "When"]
    result = tabulate(data, headers=headers, tablefmt="grid", maxcolwidths=[7, 5])

    expected = "\n".join(
        [
            "+---------+--------+",
            "| Title   | When   |",
            "+=========+========+",
            "| First   | True   |",
            "| Entry   |        |",
            "+---------+--------+",
            "| Second  |        |",
            "| Entry   |        |",
            "+---------+--------+",
        ]
    )
    assert result == expected
```

**Agent's stated rationale:**

> The bug report says tabulate() raises an exception when maxcolwidths is combined with a "True"/"False" string cell or a None cell, because the internal _wrap_text_to_colwidths casts cells via _type(cell, numparse)(cell) before calling .splitlines() on the result. For a "True"/"False" string, _type detects bool and casts it to an actual Python bool (e.g. bool("True") -> True), which has no .splitlines(); for None, _type(None) is NoneType, casting None to None, which also lacks .splitlines(). This reproduces the exact minimal repro from the report and asserts the CORRECT expected behavior: no exception, "True" wrapped as plain text, and the None cell rendered as blank. Verified: (1) it fails on the current buggy code with the exact reported AttributeError ('bool' object has no attribute 'splitlines'), and (2) it passes once _wrap_text_to_colwidths is fixed to treat bool-like strings and None specially before casting, without breaking the rest of the existing test suite.

## 5. Two-sided gate

### Against `buggy/` — exit 1 (must be non-zero)

```
s should wrap 'True'/'False' strings and None
        cells instead of raising AttributeError during text wrapping.
    
        See bug report: using maxcolwidths on a table containing a "True"/"False"
        string cell or a None cell raised an exception (AttributeError) inside
        _wrap_text_to_colwidths because the type-detection logic (_type) casts
        "True"/"False" strings to an actual bool, and None to None, neither of
        which support .splitlines(). Expected behavior: these should be wrapped
        like normal strings ("True"/"False" as text, None as blank).
        """
        data = [
            ["First Entry", "True"],
            ["Second Entry", None],
        ]
        headers = ["Title", "When"]
>       result = tabulate(data, headers=headers, tablefmt="grid", maxcolwidths=[7, 5])
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

test/test_regressgen_candidate.py:20: 
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
     
... [800 more chars]
```

### Against `fixed/` — exit 1 (must be zero)

```
F                                                                        [100%]
=================================== FAILURES ===================================
__________________ test_maxcolwidths_with_bool_and_none_cells __________________

    def test_maxcolwidths_with_bool_and_none_cells():
        """Regression: maxcolwidths should wrap 'True'/'False' strings and None
        cells instead of raising AttributeError during text wrapping.
    
        See bug report: using maxcolwidths on a table containing a "True"/"False"
        string cell or a None cell raised an exception (AttributeError) inside
        _wrap_text_to_colwidths because the type-detection logic (_type) casts
        "True"/"False" strings to an actual bool, and None to None, neither of
        which support .splitlines(). Expected behavior: these should be wrapped
        like normal strings ("True"/"False" as text, None as blank).
        """
        data = [
            ["First Entry", "True"],
            ["Second Entry", None],
        ]
        headers = ["Title", "When"]
        result = tabulate(data, headers=headers, tablefmt="grid", maxcolwidths=[7, 5])
    
        expected = "\n".join(
            [
                "+---------+--------+",
                "| Title   | When   |",
                "+=========+========+",
                "| First   | True   |",
                "| Entry   |        |",
                "+---------+--------+",
                "| Second  |        |",
                "| Entry   |        |",
                "+---------+--------+",
            ]
        )
>       assert result == expected
E       AssertionError: assert '+---------+-...---+--------+' == '+---------+-...---+--------+'
E         
E         Skipping 128 identical leading characters in diff, use -v to show
E         Skipping 37 identical trailing characters in diff, use -v to show
E         - Second  |        |
E         ?           ^^^^
E         + Second  | None   |
E         ?           ^^^^
E           | En

test/test_regressgen_candidate.py:35: AssertionError
=========================== short test summary info ============================
FAILED test/test_regressgen_candidate.py::test_maxc
... [52 more chars]
```

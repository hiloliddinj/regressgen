# Trajectory — `v4-discipline` on `tabulate-0978de5b`

**Verdict: REPRO**  (fails on buggy, passes on fixed — reproduces the bug)

- cost `$0.42284` · wall `74.4s` · tool calls `14`

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

Call `submit_test` exactly once with the complete test file when you are done.
The file must be self-contained and importable: include every import it needs.
Keep it focused — test this one bug, not the module in gen
... [6 more chars]
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

### 1. `search_code`(pattern="dataclass")

Tool responded:

```
tabulate/__init__.py:13: import dataclasses
tabulate/__init__.py:1334: * list of dataclasses (Python 3.7+ only, usually used with headers="keys")
tabulate/__init__.py:1391: else:  # it's a usual iterable of iterables, or a NumPy array, or an iterable of dataclasses
tabulate/__init__.py:1456: dataclasses is not None
tabulate/__init__.py:1458: and dataclasses.is_dataclass(rows[0])
tabulate/__init__.py:1460: # Python 3.7+'s dataclass
tabulate/__init__.py:1461: field_names = [field.name for field in dataclasses.fields(rows[0])]
tabulate/__init__.py:1603: an iterable of dataclasses (Python 3.7+), a two-dimensional NumPy array,
test/test_input.py:481: def test_py37orlater_list_of_dataclasses_keys():
test/test_input.py:482: "Input: a list of dataclasses with first item's fields as keys and headers"
test/test_input.py:484: from dataclasses import make_dataclass
test/test_input.py:486: Person = make_dataclass("Person", ["name", "age", "height"])
test/test_input.py:499: skip("test_py37orlater_list_of_dataclasses_keys is skipped")
test/test_input.py:502: def test_py37orlater_list_of_dataclasses_headers():
test/test_input.py:503: "Input: a list of dataclasses with user-supplied headers"
test/test_input.py:505: from dataclasses import make_dataclass
test/test_input.py:507: Person = make_dataclass("Person", ["name", "age", "height"])
test/test_input.py:520: skip("test_py37orlater_list_of_dataclasses_headers is skipped")
```

### 2. `read_file`(path="tabulate/__init__.py", start=1440, end=1480)

Tool responded:

```
tabulate/__init__.py lines 1440-1480 of 2787

 1440|                 raise ValueError(
 1441|                     "headers for a list of dicts is not a dict or a keyword"
 1442|                 )
 1443|             rows = [[row.get(k) for k in keys] for row in rows]
 1444| 
 1445|         elif (
 1446|             headers == "keys"
 1447|             and hasattr(tabular_data, "description")
 1448|             and hasattr(tabular_data, "fetchone")
 1449|             and hasattr(tabular_data, "rowcount")
 1450|         ):
 1451|             # Python Database API cursor object (PEP 0249)
 1452|             # print tabulate(cursor, headers='keys')
 1453|             headers = [column[0] for column in tabular_data.description]
 1454| 
 1455|         elif (
 1456|             dataclasses is not None
 1457|             and len(rows) > 0
 1458|             and dataclasses.is_dataclass(rows[0])
 1459|         ):
 1460|             # Python 3.7+'s dataclass
 1461|             field_names = [field.name for field in dataclasses.fields(rows[0])]
 1462|             if headers == "keys":
 1463|                 headers = field_names
 1464|             rows = [[getattr(row, f) for f in field_names] for row in rows]
 1465| 
 1466|         elif headers == "keys" and len(rows) > 0:
 1467|             # keys are column indices
 1468|             headers = list(map(str, range(len(rows[0]))))
 1469| 
 1470|     # take headers from the first row if necessary
 1471|     if headers == "firstrow" and len(rows) > 0:
 1472|         if index is not None:
 1473|             headers = [index[0]] + list(rows[0])
 1474|             index = index[1:]
 1475|         else:
 1476|             headers = rows[0]
 1477|         headers = list(map(str, headers))  # headers should be strings
 1478|         rows = rows[1:]
 1479|     elif headers == "firstrow":
 1480|         headers = []
```

### 3. `read_file`(path="tabulate/__init__.py", start=1395, end=1445)

Tool responded:

```
tabulate/__init__.py lines 1395-1445 of 2787

 1395|             # an empty table (issue #81)
 1396|             headers = []
 1397|         elif (
 1398|             headers == "keys"
 1399|             and hasattr(tabular_data, "dtype")
 1400|             and getattr(tabular_data.dtype, "names")
 1401|         ):
 1402|             # numpy record array
 1403|             headers = tabular_data.dtype.names
 1404|         elif (
 1405|             headers == "keys"
 1406|             and len(rows) > 0
 1407|             and isinstance(rows[0], tuple)
 1408|             and hasattr(rows[0], "_fields")
 1409|         ):
 1410|             # namedtuple
 1411|             headers = list(map(str, rows[0]._fields))
 1412|         elif len(rows) > 0 and hasattr(rows[0], "keys") and hasattr(rows[0], "values"):
 1413|             # dict-like object
 1414|             uniq_keys = set()  # implements hashed lookup
 1415|             keys = []  # storage for set
 1416|             if headers == "firstrow":
 1417|                 firstdict = rows[0] if len(rows) > 0 else {}
 1418|                 keys.extend(firstdict.keys())
 1419|                 uniq_keys.update(keys)
 1420|                 rows = rows[1:]
 1421|             for row in rows:
 1422|                 for k in row.keys():
 1423|                     # Save unique items in input order
 1424|                     if k not in uniq_keys:
 1425|                         keys.append(k)
 1426|                         uniq_keys.add(k)
 1427|             if headers == "keys":
 1428|                 headers = keys
 1429|             elif isinstance(headers, dict):
 1430|                 # a dict of headers for a list of dicts
 1431|                 headers = [headers.get(k, k) for k in keys]
 1432|                 headers = list(map(str, headers))
 1433|             elif headers == "firstrow":
 1434|                 if len(rows) > 0:
 1435|                     headers = [firstdict.get(k, k) for k in keys]
 1436|                     headers = list(map(str, headers))
 1437|                 else:
 1438|                     headers = []
 1439|             elif headers:
 1440|                 raise ValueError(
 1441|          
... [193 more chars]
```

### 4. `search_code`(pattern="SEPARATING_LINE\\s*=")

Tool responded:

```
tabulate/__init__.py:51: SEPARATING_LINE = "\001"
```

### 5. `search_code`(pattern="SEPARATING_LINE")

Tool responded:

```
tabulate/__init__.py:51: SEPARATING_LINE = "\001"
tabulate/__init__.py:108: (len(row) >= 1 and row[0] == SEPARATING_LINE)
tabulate/__init__.py:109: or (len(row) >= 2 and row[1] == SEPARATING_LINE)
tabulate/__init__.py:1290: rows.insert(index, SEPARATING_LINE)
tabulate/__init__.py:2453: # the SEPARATING_LINE flag
test/test_internal.py:318: T.SEPARATING_LINE,
test/test_internal.py:320: T.SEPARATING_LINE,
test/test_internal.py:322: T.SEPARATING_LINE,
test/test_internal.py:335: T.SEPARATING_LINE,
test/test_internal.py:337: T.SEPARATING_LINE,
test/test_internal.py:339: T.SEPARATING_LINE,
test/test_output.py:5: from tabulate import tabulate, simple_separated_format, SEPARATING_LINE
test/test_output.py:12: _test_table_with_sep_line = [["spam", 41.9999], SEPARATING_LINE, ["eggs", "451.0"]]
test/test_output.py:118: SEPARATING_LINE,
test/test_output.py:261: table = [["Earth", 6371], ["Mars", 3390], SEPARATING_LINE, ["Moon", 1737]]
test/test_output.py:307: SEPARATING_LINE,
test/test_output.py:2676: [["one", "two"], SEPARATING_LINE, ["three", "four"]],
test/test_output.py:2921: dd = [(0, 101), SEPARATING_LINE, (1, 102), (2, 103)]
```

### 6. `read_file`(path="tabulate/__init__.py", start=1320, end=1400)

Tool responded:

```
tabulate/__init__.py lines 1320-1400 of 2787

 1320| 
 1321| def _normalize_tabular_data(tabular_data, headers, showindex="default"):
 1322|     """Transform a supported data type to a list of lists, and a list of headers, with headers padding.
 1323| 
 1324|     Supported tabular data types:
 1325| 
 1326|     * list-of-lists or another iterable of iterables
 1327| 
 1328|     * list of named tuples (usually used with headers="keys")
 1329| 
 1330|     * list of dicts (usually used with headers="keys")
 1331| 
 1332|     * list of OrderedDicts (usually used with headers="keys")
 1333| 
 1334|     * list of dataclasses (Python 3.7+ only, usually used with headers="keys")
 1335| 
 1336|     * 2D NumPy arrays
 1337| 
 1338|     * NumPy record arrays (usually used with headers="keys")
 1339| 
 1340|     * dict of iterables (usually used with headers="keys")
 1341| 
 1342|     * pandas.DataFrame (usually used with headers="keys")
 1343| 
 1344|     The first row can be used as headers if headers="firstrow",
 1345|     column indices can be used as headers if headers="keys".
 1346| 
 1347|     If showindex="default", show row indices of the pandas.DataFrame.
 1348|     If showindex="always", show row indices for all types of data.
 1349|     If showindex="never", don't show row indices for all types of data.
 1350|     If showindex is an iterable, show its values as row indices.
 1351| 
 1352|     """
 1353| 
 1354|     try:
 1355|         bool(headers)
 1356|         is_headers2bool_broken = False  # noqa
 1357|     except ValueError:  # numpy.ndarray, pandas.core.index.Index, ...
 1358|         is_headers2bool_broken = True  # noqa
 1359|         headers = list(headers)
 1360| 
 1361|     index = None
 1362|     if hasattr(tabular_data, "keys") and hasattr(tabular_data, "values"):
 1363|         # dict-like and pandas.DataFrame?
 1364|         if hasattr(tabular_data.values, "__call__"):
 1365|             # likely a conventional dict
 1366|             keys = tabular_data.keys()
 1367|             rows = list(
 1368|                 izip_longest(*tabular_data.values())
 1369|             )  # columns have to be transposed
 1370|         elif hasattr(tabular_data, 
... [300 more chars]
```

### 7. `run_test`(test_source="\nfrom dataclasses import make_dataclass\nfrom tabulate import tabulate, SEPARATING_LINE\n\ndef test_dataclas)

Tool responded:

```
FAILED (exit 1)

ython 3.7+'s dataclass
                field_names = [field.name for field in dataclasses.fields(rows[0])]
                if headers == "keys":
                    headers = field_names
>               rows = [[getattr(row, f) for f in field_names] for row in rows]
                         ^^^^^^^^^^^^^^^
E               AttributeError: 'str' object has no attribute 'name'

tabulate/__init__.py:1464: AttributeError
________________________ test_dict_with_separating_line ________________________

    def test_dict_with_separating_line():
        data = [{"name": "Alice", "age": 23, "height": 169.5}, SEPARATING_LINE, {"name": "Bob", "age": 27, "height": 175.0}]
>       result = tabulate(data, headers="keys")
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

test/test_regressgen_candidate.py:15: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
tabulate/__init__.py:2088: in tabulate
    list_of_lists, headers, headers_pad = _normalize_tabular_data(
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

tabular_data = [{'age': 23, 'height': 169.5, 'name': 'Alice'}, '\x01', {'age': 27, 'height': 175.0, 'name': 'Bob'}]
headers = 'keys', showindex = 'default'

    def _normalize_tabular_data(tabular_data, headers, showindex="default"):
        """Transform a supported data type to a list of lists, and a list of headers, with headers padding.
    
        Supported tabular data types:
    
        * list-of-lists or another iterable of iterables
    
        * list of named tuples (usually used with headers="keys")
    
        * list of dicts (usually used with headers="keys")
    
        * list of OrderedDicts (usually used with headers="keys")
    
        * list of dataclasses (Python 3.7+ only, usually used with headers="keys")
    
        * 2D NumPy arrays
    
        * NumPy record arrays (usually used with headers="keys")
    
        * dict of iterables (usually used with headers="keys")
    
        * pandas.DataFrame (usually used with headers="keys")
    
        The first row can be used as headers if headers="firstrow",
        column indices can be used as headers if headers="k
... [300 more chars]
```

### 8. `read_file`(path="tabulate/__init__.py", start=95, end=120)

Tool responded:

```
tabulate/__init__.py lines 95-120 of 2787

   95|         "linebetweenrows",
   96|         "linebelow",
   97|         "headerrow",
   98|         "datarow",
   99|         "padding",
  100|         "with_header_hide",
  101|     ],
  102| )
  103| 
  104| 
  105| def _is_separating_line(row):
  106|     row_type = type(row)
  107|     is_sl = (row_type == list or row_type == str) and (
  108|         (len(row) >= 1 and row[0] == SEPARATING_LINE)
  109|         or (len(row) >= 2 and row[1] == SEPARATING_LINE)
  110|     )
  111|     return is_sl
  112| 
  113| 
  114| def _pipe_segment_with_colons(align, colwidth):
  115|     """Return a segment of a horizontal line with optional colons which
  116|     indicate column's alignment (as in `pipe` output format)."""
  117|     w = colwidth
  118|     if align in ["right", "decimal"]:
  119|         return ("-" * (w - 1)) + ":"
  120|     elif align == "center":
```

### 9. `read_file`(path="test/test_output.py", start=1, end=40)

Tool responded:

```
test/test_output.py lines 1-40 of 3029

    1| """Test output of the various forms of tabular data."""
    2| 
    3| import tabulate as tabulate_module
    4| from common import assert_equal, raises, skip, check_warnings
    5| from tabulate import tabulate, simple_separated_format, SEPARATING_LINE
    6| 
    7| # _test_table shows
    8| #  - coercion of a string to a number,
    9| #  - left alignment of text,
   10| #  - decimal point alignment of numbers
   11| _test_table = [["spam", 41.9999], ["eggs", "451.0"]]
   12| _test_table_with_sep_line = [["spam", 41.9999], SEPARATING_LINE, ["eggs", "451.0"]]
   13| _test_table_headers = ["strings", "numbers"]
   14| 
   15| 
   16| def test_plain():
   17|     "Output: plain with headers"
   18|     expected = "\n".join(
   19|         ["strings      numbers", "spam         41.9999", "eggs        451"]
   20|     )
   21|     result = tabulate(_test_table, _test_table_headers, tablefmt="plain")
   22|     assert_equal(expected, result)
   23| 
   24| 
   25| def test_plain_headerless():
   26|     "Output: plain without headers"
   27|     expected = "\n".join(["spam   41.9999", "eggs  451"])
   28|     result = tabulate(_test_table, tablefmt="plain")
   29|     assert_equal(expected, result)
   30| 
   31| 
   32| def test_plain_multiline_headerless():
   33|     "Output: plain with multiline cells without headers"
   34|     table = [["foo bar\nbaz\nbau", "hello"], ["", "multiline\nworld"]]
   35|     expected = "\n".join(
   36|         ["foo bar    hello", "  baz", "  bau", "         multiline", "           world"]
   37|     )
   38|     result = tabulate(table, stralign="center", tablefmt="plain")
   39|     assert_equal(expected, result)
   40|
```

### 10. `search_code`(pattern="_test_table_with_sep_line")

Tool responded:

```
test/test_output.py:12: _test_table_with_sep_line = [["spam", 41.9999], SEPARATING_LINE, ["eggs", "451.0"]]
test/test_output.py:256: result = tabulate(_test_table_with_sep_line, _test_table_headers, tablefmt="simple")
test/test_output.py:334: result = tabulate(_test_table_with_sep_line, tablefmt="simple")
```

### 11. `read_file`(path="test/test_output.py", start=240, end=345)

Tool responded:

```
test/test_output.py lines 240-345 of 3029

  240|     )
  241|     result = tabulate(_test_table, _test_table_headers, tablefmt="simple")
  242|     assert_equal(expected, result)
  243| 
  244| 
  245| def test_simple_with_sep_line():
  246|     "Output: simple with headers and separating line"
  247|     expected = "\n".join(
  248|         [
  249|             "strings      numbers",
  250|             "---------  ---------",
  251|             "spam         41.9999",
  252|             "---------  ---------",
  253|             "eggs        451",
  254|         ]
  255|     )
  256|     result = tabulate(_test_table_with_sep_line, _test_table_headers, tablefmt="simple")
  257|     assert_equal(expected, result)
  258| 
  259| 
  260| def test_readme_example_with_sep():
  261|     table = [["Earth", 6371], ["Mars", 3390], SEPARATING_LINE, ["Moon", 1737]]
  262|     expected = "\n".join(
  263|         [
  264|             "-----  ----",
  265|             "Earth  6371",
  266|             "Mars   3390",
  267|             "-----  ----",
  268|             "Moon   1737",
  269|             "-----  ----",
  270|         ]
  271|     )
  272|     result = tabulate(table, tablefmt="simple")
  273|     assert_equal(expected, result)
  274| 
  275| 
  276| def test_simple_multiline_2():
  277|     "Output: simple with multiline cells"
  278|     expected = "\n".join(
  279|         [
  280|             " key     value",
  281|             "-----  ---------",
  282|             " foo      bar",
  283|             "spam   multiline",
  284|             "         world",
  285|         ]
  286|     )
  287|     table = [["key", "value"], ["foo", "bar"], ["spam", "multiline\nworld"]]
  288|     result = tabulate(table, headers="firstrow", stralign="center", tablefmt="simple")
  289|     assert_equal(expected, result)
  290| 
  291| 
  292| def test_simple_multiline_2_with_sep_line():
  293|     "Output: simple with multiline cells"
  294|     expected = "\n".join(
  295|         [
  296|             " key     value",
  297|             "-----  ---------",
  298|             " foo      bar",
  299|             "-----  ---------",
  300|             "spam   multiline",
 
... [300 more chars]
```

### 12. `run_test`(test_source="\nfrom tabulate import tabulate, SEPARATING_LINE\n\ndef test_expected_output():\n    data = [[\"Alice\", 23, )

Tool responded:

```
FAILED (exit 1)

F                                                                        [100%]
=================================== FAILURES ===================================
_____________________________ test_expected_output _____________________________

    def test_expected_output():
        data = [["Alice", 23, 169.5], SEPARATING_LINE, ["Bob", 27, 175.0]]
        result = tabulate(data, headers=["name", "age", "height"], tablefmt="simple")
        print(repr(result))
        print(result)
>       assert False
E       assert False

test/test_regressgen_candidate.py:9: AssertionError
----------------------------- Captured stdout call -----------------------------
'name      age    height\n------  -----  --------\nAlice      23     169.5\n------  -----  --------\nBob        27     175'
name      age    height
------  -----  --------
Alice      23     169.5
------  -----  --------
Bob        27     175
=========================== short test summary info ============================
FAILED test/test_regressgen_candidate.py::test_expected_output - assert False
1 failed in 0.09s
```

### 13. `run_test`(test_source="\nfrom dataclasses import make_dataclass\nfrom tabulate import tabulate, SEPARATING_LINE\n\n\ndef test_datacl)

Tool responded:

```
FAILED (exit 1)

   
        * 2D NumPy arrays
    
        * NumPy record arrays (usually used with headers="keys")
    
        * dict of iterables (usually used with headers="keys")
    
        * pandas.DataFrame (usually used with headers="keys")
    
        The first row can be used as headers if headers="firstrow",
        column indices can be used as headers if headers="keys".
    
        If showindex="default", show row indices of the pandas.DataFrame.
        If showindex="always", show row indices for all types of data.
        If showindex="never", don't show row indices for all types of data.
        If showindex is an iterable, show its values as row indices.
    
        """
    
        try:
            bool(headers)
            is_headers2bool_broken = False  # noqa
        except ValueError:  # numpy.ndarray, pandas.core.index.Index, ...
            is_headers2bool_broken = True  # noqa
            headers = list(headers)
    
        index = None
        if hasattr(tabular_data, "keys") and hasattr(tabular_data, "values"):
            # dict-like and pandas.DataFrame?
            if hasattr(tabular_data.values, "__call__"):
                # likely a conventional dict
                keys = tabular_data.keys()
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
                rows = [list(row) for row in vals
... [300 more chars]
```

### 14. `submit_test`(rationale="The bug report describes tabulate() raising an error when a list of dataclass instances contains a SEPARATING)

Tool responded:

```
Submitted.

"""Regression test for: list of dataclass instances mixed with SEPARATING_LINE
raises an AttributeError instead of producing a table with a separating line.

See bug report: using tabulate() on a list containing dataclass rows and a
SEPARATING_LINE marker blows up because the dataclass-handling code path
tries to call getattr() on the SEPARATING_LINE sentinel itself (treating it
like a dataclass row), instead of skipping/passing it through the way the
list-of-dicts code path is expected to.
"""

from dataclasses import make_dataclass

from tabulate import SEPARATING_LINE, tabulate


def test_dataclass_rows_with_separating_line():
    """A list of dataclass instances mixed with SEPARATING_LINE should render
    a table with headers derived from the dataclass fields and a separating
    line drawn between the rows -- the same result you get from the
    equivalent plain list-of-lists input -- rather than raising an error.
    """
    Person = make_dataclass("Person", ["name", "age", "height"])
    data = [
        Person("Alice", 23, 169.5),
        SEPARATING_LINE,
        Person("Bob", 27, 175.0),
    ]

    result = tabulate(data, headers="keys", tablefmt="simple")

    expected = "\n".join(
        [
            "name      age    height",
            "------  -----  --------",
            "Alice      23     169.5",
            "------  -----  --------",
            "Bob        27     175",
        ]
    )

    assert result == expected
```

## 4. Submitted test

```python
"""Regression test for: list of dataclass instances mixed with SEPARATING_LINE
raises an AttributeError instead of producing a table with a separating line.

See bug report: using tabulate() on a list containing dataclass rows and a
SEPARATING_LINE marker blows up because the dataclass-handling code path
tries to call getattr() on the SEPARATING_LINE sentinel itself (treating it
like a dataclass row), instead of skipping/passing it through the way the
list-of-dicts code path is expected to.
"""

from dataclasses import make_dataclass

from tabulate import SEPARATING_LINE, tabulate


def test_dataclass_rows_with_separating_line():
    """A list of dataclass instances mixed with SEPARATING_LINE should render
    a table with headers derived from the dataclass fields and a separating
    line drawn between the rows -- the same result you get from the
    equivalent plain list-of-lists input -- rather than raising an error.
    """
    Person = make_dataclass("Person", ["name", "age", "height"])
    data = [
        Person("Alice", 23, 169.5),
        SEPARATING_LINE,
        Person("Bob", 27, 175.0),
    ]

    result = tabulate(data, headers="keys", tablefmt="simple")

    expected = "\n".join(
        [
            "name      age    height",
            "------  -----  --------",
            "Alice      23     169.5",
            "------  -----  --------",
            "Bob        27     175",
        ]
    )

    assert result == expected
```

**Agent's stated rationale:**

> The bug report describes tabulate() raising an error when a list of dataclass instances contains a SEPARATING_LINE marker, because the dataclass-detection branch in _normalize_tabular_data unconditionally does `getattr(row, f)` for every row (including the SEPARATING_LINE sentinel string), rather than skipping/passing through the separator like other code paths do. I confirmed via run_test that this exact scenario currently raises `AttributeError: 'str' object has no attribute 'name'` at tabulate/__init__.py:1464. I derived the expected correct output independently by running the equivalent plain list-of-lists input (which is unaffected by this bug) through tabulate with the same headers and tablefmt="simple", confirming the separating line is rendered between the two data rows. The submitted test asserts this correct expected string against the dataclass-based input, so it fails on the current buggy code (AttributeError) and will pass once the fix makes dataclass rows behave the same as list/dict rows with respect to SEPARATING_LINE.

## 5. Two-sided gate

### Against `buggy/` — exit 1 (must be non-zero)

```
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
                    firstdict = rows[0] if len(rows) > 0 else {}
                    keys.extend(firstdict.keys())
                    uniq_keys.update(keys)
                    rows = rows[1:]
                for row in rows:
                    for k in row.keys():
                        # Save unique items in input order
                        if k not in uniq_keys:
                            keys.append(k)
                            uniq_keys.add(k)
                if headers == "keys":
                    headers = keys
                elif isinstance(headers, dict):
                    # a dict of headers for a list of dicts
                    headers = [headers.get(k, k) for k in keys]
                    headers = list(map(str, headers))
                elif headers == "firstrow":
                    if len(rows) > 0:
                        headers = [firstdict.get(k, k) for k in keys]
                        headers = list(map(str, headers))
                    else:
                        headers = []
                elif headers:
                    raise ValueError(
                        "headers for a list of dicts is not a dict or a keyword"
                    )
                rows = [[row.get(k) for k in keys] for row in rows]
    
            elif (
                headers == "keys"
                and hasattr(tabular_data, "description")
                and hasattr(tabular_data, "fetchone")
                and hasattr(tabular_data, "rowcount")
            ):
                # Python Database API cursor object (PEP 0249)
                # print tabulate(cursor, headers='keys')
                headers = [column[0] for column in tabular_data.d
... [800 more chars]
```

### Against `fixed/` — exit 0 (must be zero)

```
.                                                                        [100%]
1 passed in 0.08s
```

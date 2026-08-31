# Trajectory — `v4-discipline` on `boltons-eb659013`

**Verdict: REPRO**  (fails on buggy, passes on fixed — reproduces the bug)

- cost `$0.3377` · wall `91.6s` · tool calls `9`

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
`Table.to_text()` blows up on a few edge cases instead of just producing reasonable output. Ran into this while building tables dynamically where row length/headers aren't always known upfront.

Examples:

```python
from boltons.tableutils import Table

Table([[]]).to_text()
# ValueError: max() iterable argument is empty

Table([[], [1]]).to_text()
# IndexError

t = Table([[1, 2]], headers=[])
t.headers = ['a']
t.to_text()
# IndexError

Table([[None, 'b'], [1, 2]]).to_text()
# AttributeError: 'NoneType' object has no attribute 'center'
```

I expected `to_text()` to just render something sensible in all these cases (empty string for an empty table, no header row when there are no headers, headers padded out if shorter than the row width, and `None` header cells rendered like `None` data cells) rather than throwing. `to_html()` seems to cope with similar inputs fine, so I'd expect `to_text()` to be at least as forgiving.
```

## 3. Tool calls

### 1. `search_code`(pattern="def to_text")

Tool responded:

```
boltons/tableutils.py:84: def to_text(obj, maxlen=None):
boltons/tableutils.py:558: def to_text(self, with_headers=True, maxlen=None):
boltons/urlutils.py:745: def to_text(self, full_quote=False):
boltons/urlutils.py:1589: def to_text(self, full_quote=False):
```

### 2. `read_file`(path="boltons/tableutils.py", start=540, end=600)

Tool responded:

```
boltons/tableutils.py lines 540-583 of 583

  540|         for i in range(self._width):
  541|             line_parts = [tr]
  542|             if headers:
  543|                 line_parts.extend([th, esc(headers[i]), _th])
  544|             if max_depth > 1:
  545|                 new_depth = max_depth - 1
  546|                 _fill_parts = []
  547|                 for row in self._data:
  548|                     cell = row[i]
  549|                     if isinstance(cell, Table):
  550|                         _fill_parts.append(cell.to_html(max_depth=new_depth))
  551|                     else:
  552|                         _fill_parts.append(esc(row[i]))
  553|             else:
  554|                 _fill_parts = [esc(row[i]) for row in self._data]
  555|             line_parts.extend([td, _tdtd.join(_fill_parts), _td_tr])
  556|             lines.append(''.join(line_parts))
  557| 
  558|     def to_text(self, with_headers=True, maxlen=None):
  559|         """Get the Table's textual representation. Only works well
  560|         for Tables with non-recursive data.
  561| 
  562|         Args:
  563|             with_headers (bool): Whether to include a header row at the top.
  564|             maxlen (int): Max length of data in each cell.
  565|         """
  566|         lines = []
  567|         widths = []
  568|         headers = list(self.headers)
  569|         text_data = [[to_text(cell, maxlen=maxlen) for cell in row]
  570|                      for row in self._data]
  571|         for idx in range(self._width):
  572|             cur_widths = [len(row[idx]) for row in text_data]
  573|             if with_headers:
  574|                 cur_widths.append(len(to_text(headers[idx], maxlen=maxlen)))
  575|             widths.append(max(cur_widths))
  576|         if with_headers:
  577|             lines.append(' | '.join([h.center(widths[i])
  578|                                      for i, h in enumerate(headers)]))
  579|             lines.append('-|-'.join(['-' * w for w in widths]))
  580|         for row in text_data:
  581|             lines.append(' | '.join([cell.center(widths[j])
  582|                                      for j
... [66 more chars]
```

### 3. `read_file`(path="boltons/tableutils.py", start=70, end=110)

Tool responded:

```
boltons/tableutils.py lines 70-110 of 583

   70|   starting from empty?
   71| * is it possible to effectively tell the difference between when a
   72|   Table is from_data()'d with a single row (list) or with a list of lists?
   73| * CSS: white-space pre-line or pre-wrap maybe?
   74| * Would be nice to support different backends (currently uses lists
   75|   exclusively). Sometimes large datasets come in list-of-dicts and
   76|   list-of-tuples format and it's desirable to cut down processing overhead.
   77| 
   78| TODO: make iterable on rows?
   79| """
   80| 
   81| __all__ = ['Table']
   82| 
   83| 
   84| def to_text(obj, maxlen=None):
   85|     try:
   86|         text = str(obj)
   87|     except Exception:
   88|         try:
   89|             text = str(repr(obj))
   90|         except Exception:
   91|             text = str(object.__repr__(obj))
   92|     if maxlen and len(text) > maxlen:
   93|         text = text[:maxlen - 3] + '...'
   94|         # TODO: inverse of ljust/rjust/center
   95|     return text
   96| 
   97| 
   98| def escape_html(obj, maxlen=None):
   99|     text = to_text(obj, maxlen=maxlen)
  100|     return html_escape(text, quote=True)
  101| 
  102| 
  103| _DNR = {type(None), bool, complex, float, type(NotImplemented), slice,
  104|         str, bytes, int,
  105|         types.FunctionType, types.MethodType,
  106|         types.BuiltinFunctionType, types.GeneratorType}
  107| 
  108| 
  109| class UnsupportedData(TypeError):
  110|     pass
```

### 4. `read_file`(path="boltons/tableutils.py", start=110, end=260)

Tool responded:

```
boltons/tableutils.py lines 110-260 of 583

  110|     pass
  111| 
  112| 
  113| class InputType:
  114|     def __init__(self, *a, **kw):
  115|         pass
  116| 
  117|     def get_entry_seq(self, data_seq, headers):
  118|         return [self.get_entry(entry, headers) for entry in data_seq]
  119| 
  120| 
  121| class DictInputType(InputType):
  122|     def check_type(self, obj):
  123|         return isinstance(obj, Mapping)
  124| 
  125|     def guess_headers(self, obj):
  126|         return sorted(obj.keys())
  127| 
  128|     def get_entry(self, obj, headers):
  129|         return [obj.get(h) for h in headers]
  130| 
  131|     def get_entry_seq(self, obj, headers):
  132|         return [[ci.get(h) for h in headers] for ci in obj]
  133| 
  134| 
  135| class ObjectInputType(InputType):
  136|     def check_type(self, obj):
  137|         return type(obj) not in _DNR and hasattr(obj, '__class__')
  138| 
  139|     def guess_headers(self, obj):
  140|         headers = []
  141|         for attr in dir(obj):
  142|             # an object's __dict__ could technically have non-string keys
  143|             try:
  144|                 val = getattr(obj, attr)
  145|             except Exception:
  146|                 # seen on greenlet: `run` shows in dir() but raises
  147|                 # AttributeError. Also properties misbehave.
  148|                 continue
  149|             if callable(val):
  150|                 continue
  151|             headers.append(attr)
  152|         return headers
  153| 
  154|     def get_entry(self, obj, headers):
  155|         values = []
  156|         for h in headers:
  157|             try:
  158|                 values.append(getattr(obj, h))
  159|             except Exception:
  160|                 values.append(None)
  161|         return values
  162| 
  163| 
  164| # might be better to hardcode list support since it's so close to the
  165| # core or might be better to make this the copy-style from_* importer
  166| # and have the non-copy style be hardcoded in __init__
  167| class ListInputType(InputType):
  168|     def check_type(self, obj):
  169|         return isinstance(obj, Mut
... [300 more chars]
```

### 5. `read_file`(path="boltons/tableutils.py", start=260, end=340)

Tool responded:

```
boltons/tableutils.py lines 260-340 of 583

  260|     # _html_tfoot, _html_tfoot_close = '<tfoot>', '</tfoot>'
  261|     _html_table_tag, _html_table_tag_close = '<table>', '</table>'
  262| 
  263|     def __init__(self, data=None, headers=_MISSING, metadata=None):
  264|         if headers is _MISSING:
  265|             headers = []
  266|             if data:
  267|                 headers, data = list(data[0]), islice(data, 1, None)
  268|         self.headers = headers or []
  269|         self.metadata = metadata or {}
  270|         self._data = []
  271|         self._width = 0
  272| 
  273|         self.extend(data)
  274| 
  275|     def extend(self, data):
  276|         """
  277|         Append the given data to the end of the Table.
  278|         """
  279|         if not data:
  280|             return
  281|         self._data.extend(data)
  282|         self._set_width()
  283|         self._fill()
  284| 
  285|     def _set_width(self, reset=False):
  286|         if reset:
  287|             self._width = 0
  288|         if self._width:
  289|             return
  290|         if self.headers:
  291|             self._width = len(self.headers)
  292|             return
  293|         self._width = max([len(d) for d in self._data])
  294| 
  295|     def _fill(self):
  296|         width, filler = self._width, [None]
  297|         if not width:
  298|             return
  299|         for d in self._data:
  300|             rem = width - len(d)
  301|             if rem > 0:
  302|                 d.extend(filler * rem)
  303|         return
  304| 
  305|     @classmethod
  306|     def from_dict(cls, data, headers=_MISSING, max_depth=1, metadata=None):
  307|         """Create a Table from a :class:`dict`. Operates the same as
  308|         :meth:`from_data`, but forces interpretation of the data as a
  309|         Mapping.
  310|         """
  311|         return cls.from_data(data=data, headers=headers,
  312|                              max_depth=max_depth, _data_type=DictInputType(),
  313|                              metadata=metadata)
  314| 
  315|     @classmethod
  316|     def from_list(cls, data, headers=_MISSING, max_d
... [300 more chars]
```

### 6. `run_test`(test_source="\nfrom boltons.tableutils import Table\n\ndef test_case1():\n    t = Table([[]])\n    print(\"constructed ok\)

Tool responded:

```
FAILED (exit 1)

FFFF                                                                     [100%]
=================================== FAILURES ===================================
__________________________________ test_case1 __________________________________

    def test_case1():
>       t = Table([[]])
            ^^^^^^^^^^^

tests/test_regressgen_candidate.py:5: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
boltons/tableutils.py:273: in __init__
    self.extend(data)
boltons/tableutils.py:282: in extend
    self._set_width()
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = Table([]), reset = False

    def _set_width(self, reset=False):
        if reset:
            self._width = 0
        if self._width:
            return
        if self.headers:
            self._width = len(self.headers)
            return
>       self._width = max([len(d) for d in self._data])
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       ValueError: max() iterable argument is empty

boltons/tableutils.py:293: ValueError
__________________________________ test_case2 __________________________________

    def test_case2():
        t = Table([[], [1]])
        print("constructed ok")
>       print(t.to_text())
              ^^^^^^^^^^^

tests/test_regressgen_candidate.py:12: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = Table([[1]]), with_headers = True, maxlen = None

    def to_text(self, with_headers=True, maxlen=None):
        """Get the Table's textual representation. Only works well
        for Tables with non-recursive data.
    
        Args:
            with_headers (bool): Whether to include a header row at the top.
            maxlen (int): Max length of data in each cell.
        """
        lines = []
        widths = []
        headers = list(self.headers)
        text_data = [[to_text(cell, maxlen=maxlen) for cell in row]
                     for row in self._data]
        for idx in range(self._width):
            cur_widths = [len(row[idx]) for row in text_data]
            if with_headers:
>               cur_widths.append(len(to_text
... [300 more chars]
```

### 7. `search_code`(pattern="to_text")

Tool responded:

```
boltons/tableutils.py:84: def to_text(obj, maxlen=None):
boltons/tableutils.py:99: text = to_text(obj, maxlen=maxlen)
boltons/tableutils.py:558: def to_text(self, with_headers=True, maxlen=None):
boltons/tableutils.py:569: text_data = [[to_text(cell, maxlen=maxlen) for cell in row]
boltons/tableutils.py:574: cur_widths.append(len(to_text(headers[idx], maxlen=maxlen)))
boltons/urlutils.py:456: using the :meth:`~URL.to_text()` method. In this way, it's similar
boltons/urlutils.py:462: :meth:`~URL.to_text()` may be used. For an immutable, but
boltons/urlutils.py:481: url = url.to_text()  # better way to copy URLs?
boltons/urlutils.py:541: validation. :meth:`URL.to_text()` should be used to check if
boltons/urlutils.py:603: >>> print(URL('fakescheme://test.com').to_text())
boltons/urlutils.py:605: >>> print(URL('mockscheme:hello:world').to_text())
boltons/urlutils.py:624: :meth:`~URL.to_text()`.
boltons/urlutils.py:705: Used internally by :meth:`~URL.to_text()` and can be useful
boltons/urlutils.py:745: def to_text(self, full_quote=False):
boltons/urlutils.py:751: >>> print(url.to_text())
boltons/urlutils.py:766: query_string = self.query_params.to_text(full_quote=full_quote)
boltons/urlutils.py:795: return f'{cn}({self.to_text()!r})'
boltons/urlutils.py:798: return self.to_text()
boltons/urlutils.py:801: return self.to_text()
boltons/urlutils.py:1575: >>> qp.to_text()
boltons/urlutils.py:1589: def to_text(self, full_quote=False):
tests/test_tableutils.py:44: assert t3.to_text()
tests/test_urlutils.py:59: result = URL(test_url).to_text(full_quote=True)
tests/test_urlutils.py:65: assert isinstance(u1.to_text(), str)
tests/test_urlutils.py:81: assert u1.to_text(full_quote=True) == 'http://xn--bcher-kva.ch'
tests/test_urlutils.py:82: assert u1.to_text(full_quote=False) == 'http://bücher.ch'
tests/test_urlutils.py:86: assert u2.to_text(full_quote=True) == 'https://xn--bcher-kva.ch'
tests/test_urlutils.py:87: assert u2.to_text(full_quote=False) == 'https://bücher.ch'
tests/test_urlutils.py:94: qp_text = url_obj.query_params.to_text(full_quote=True)
tests/test_urlutils.py:108: assert url.query_params.to_text(full_quote=True).endswith('%E2%98%98')
tests/test_urlutils.py:11
... [300 more chars]
```

### 8. `run_test`(test_source="\nfrom boltons.tableutils import Table\n\n\ndef test_to_text_empty_table():\n    # Table([[]]) should not blo)

Tool responded:

```
FAILED (exit 1)

FFFF                                                                     [100%]
=================================== FAILURES ===================================
___________________________ test_to_text_empty_table ___________________________

    def test_to_text_empty_table():
        # Table([[]]) should not blow up, and should render as an empty string
        # since there is no header and no data.
>       t = Table([[]])
            ^^^^^^^^^^^

tests/test_regressgen_candidate.py:8: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
boltons/tableutils.py:273: in __init__
    self.extend(data)
boltons/tableutils.py:282: in extend
    self._set_width()
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = Table([]), reset = False

    def _set_width(self, reset=False):
        if reset:
            self._width = 0
        if self._width:
            return
        if self.headers:
            self._width = len(self.headers)
            return
>       self._width = max([len(d) for d in self._data])
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       ValueError: max() iterable argument is empty

boltons/tableutils.py:293: ValueError
_____________________ test_to_text_ragged_rows_no_headers ______________________

    def test_to_text_ragged_rows_no_headers():
        # First row is empty (used to guess headers -> no headers), second row
        # has one cell. Should not raise and should render without a header row.
        t = Table([[], [1]])
>       result = t.to_text()
                 ^^^^^^^^^^^

tests/test_regressgen_candidate.py:16: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = Table([[1]]), with_headers = True, maxlen = None

    def to_text(self, with_headers=True, maxlen=None):
        """Get the Table's textual representation. Only works well
        for Tables with non-recursive data.
    
        Args:
            with_headers (bool): Whether to include a header row at the top.
            maxlen (int): Max length of data in each cell.
        """
        lines = []
        widths = []
        headers = list(se
... [300 more chars]
```

### 9. `submit_test`(rationale="The report describes four edge cases where Table.to_text() raises instead of producing sensible output: (1) a)

Tool responded:

```
Submitted.


from boltons.tableutils import Table


def test_to_text_empty_table():
    # Table([[]]) should not blow up (previously: ValueError: max() iterable
    # argument is empty), and should render as an empty string since there
    # is no header and no data.
    t = Table([[]])
    assert t.to_text() == ''


def test_to_text_ragged_rows_no_headers():
    # First row is empty (used to guess headers -> no headers), second row
    # has one cell. Should not raise (previously: IndexError) and should
    # render without a header row since there are no headers.
    t = Table([[], [1]])
    result = t.to_text()
    assert isinstance(result, str)
    assert '1' in result
    # since headers are empty/falsy, no header row (and thus no stray
    # 'None' text) should appear
    assert 'None' not in result


def test_to_text_headers_shorter_than_row_width():
    # Headers set after construction can be shorter than the row width;
    # to_text() should pad them out rather than raising (previously:
    # IndexError).
    t = Table([[1, 2]], headers=[])
    t.headers = ['a']
    result = t.to_text()
    assert isinstance(result, str)
    assert 'a' in result
    assert '1' in result
    assert '2' in result


def test_to_text_none_header_rendered_like_none_data():
    # A None header cell should be rendered the same way a None data cell
    # is (i.e. as the text 'None'), not raise an AttributeError since None
    # has no .center() method.
    t = Table([[None, 'b'], [1, 2]])
    result = t.to_text()
    assert isinstance(result, str)
    assert 'None' in result
    assert 'b' in result
```

## 4. Submitted test

```python

from boltons.tableutils import Table


def test_to_text_empty_table():
    # Table([[]]) should not blow up (previously: ValueError: max() iterable
    # argument is empty), and should render as an empty string since there
    # is no header and no data.
    t = Table([[]])
    assert t.to_text() == ''


def test_to_text_ragged_rows_no_headers():
    # First row is empty (used to guess headers -> no headers), second row
    # has one cell. Should not raise (previously: IndexError) and should
    # render without a header row since there are no headers.
    t = Table([[], [1]])
    result = t.to_text()
    assert isinstance(result, str)
    assert '1' in result
    # since headers are empty/falsy, no header row (and thus no stray
    # 'None' text) should appear
    assert 'None' not in result


def test_to_text_headers_shorter_than_row_width():
    # Headers set after construction can be shorter than the row width;
    # to_text() should pad them out rather than raising (previously:
    # IndexError).
    t = Table([[1, 2]], headers=[])
    t.headers = ['a']
    result = t.to_text()
    assert isinstance(result, str)
    assert 'a' in result
    assert '1' in result
    assert '2' in result


def test_to_text_none_header_rendered_like_none_data():
    # A None header cell should be rendered the same way a None data cell
    # is (i.e. as the text 'None'), not raise an AttributeError since None
    # has no .center() method.
    t = Table([[None, 'b'], [1, 2]])
    result = t.to_text()
    assert isinstance(result, str)
    assert 'None' in result
    assert 'b' in result
```

**Agent's stated rationale:**

> The report describes four edge cases where Table.to_text() raises instead of producing sensible output: (1) a table built from [[]] should render as an empty string rather than raising ValueError from max() on an empty sequence; (2) a table with ragged/empty first row (which becomes empty guessed headers) should render the data without a header row instead of raising IndexError when headers are shorter than the data width; (3) headers manually set to be shorter than the row width should be padded rather than raising IndexError; (4) a None header cell should be converted to text like a None data cell (i.e. rendered as 'None') rather than raising AttributeError from calling .center() on None. I verified each of these four tests fails on the current buggy code with exactly the exception described in the report (ValueError, IndexError, IndexError, AttributeError respectively), and each assertion encodes the correct/expected behavior from the report rather than the buggy behavior, so the tests should pass once the reported bug is fixed.

## 5. Two-sided gate

### Against `buggy/` — exit 1 (must be non-zero)

```
axlen=None):
        """Get the Table's textual representation. Only works well
        for Tables with non-recursive data.
    
        Args:
            with_headers (bool): Whether to include a header row at the top.
            maxlen (int): Max length of data in each cell.
        """
        lines = []
        widths = []
        headers = list(self.headers)
        text_data = [[to_text(cell, maxlen=maxlen) for cell in row]
                     for row in self._data]
        for idx in range(self._width):
            cur_widths = [len(row[idx]) for row in text_data]
            if with_headers:
>               cur_widths.append(len(to_text(headers[idx], maxlen=maxlen)))
                                              ^^^^^^^^^^^^
E               IndexError: list index out of range

boltons/tableutils.py:574: IndexError
_______________ test_to_text_none_header_rendered_like_none_data _______________

    def test_to_text_none_header_rendered_like_none_data():
        # A None header cell should be rendered the same way a None data cell
        # is (i.e. as the text 'None'), not raise an AttributeError since None
        # has no .center() method.
        t = Table([[None, 'b'], [1, 2]])
>       result = t.to_text()
                 ^^^^^^^^^^^

tests/test_regressgen_candidate.py:44: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = Table(headers=[None, 'b'], data=[[1, 2]]), with_headers = True
maxlen = None

    def to_text(self, with_headers=True, maxlen=None):
        """Get the Table's textual representation. Only works well
        for Tables with non-recursive data.
    
        Args:
            with_headers (bool): Whether to include a header row at the top.
            maxlen (int): Max length of data in each cell.
        """
        lines = []
        widths = []
        headers = list(self.headers)
        text_data = [[to_text(cell, maxlen=maxlen) for cell in row]
                     for row in self._data]
        for idx in range(self._width):
            cur_widths = [len(row[idx]) for row in text_data]
            if with_headers:
                cur_widths.append(len(to_text(headers[idx], maxlen=maxle
... [800 more chars]
```

### Against `fixed/` — exit 0 (must be zero)

```
....                                                                     [100%]
4 passed in 0.08s
```

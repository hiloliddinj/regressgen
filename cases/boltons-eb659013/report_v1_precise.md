`Table.to_text()` raises exceptions instead of rendering for a few edge cases that `to_html()` handles fine.

The simplest case is an empty table:

```python
from boltons.tableutils import Table

Table([[]]).to_text()
```

This raises:

```
ValueError: max() iterable argument is empty
```

I'd expect this to just return `''`, same as `to_html()` returns an (mostly) empty string for the equivalent input, instead of blowing up in `_set_width`.

There are related problems too:

- `Table([[None, 'b'], [1, 2]])` raises `AttributeError` because `.center()` gets called on a `None` header instead of treating it like a `None` data cell.
- `Table([[], [1]])` (no headers) raises `IndexError` instead of just omitting the header row/separator, which is what `to_html()` does.
- `Table([[1, 2]], headers=[])` with headers later set shorter than the row width (e.g. `t.headers = ['a']`) also raises `IndexError` instead of padding the missing header cells with `None`, again matching `to_html()` behavior.

Expected: `to_text()` should handle these degenerate cases gracefully and consistently with `to_html()`, not raise.

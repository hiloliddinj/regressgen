Using SEPARATING_LINE inside a data row to force a divider line produces garbage output when the tablefmt has padding or its own linebetweenrows characters, like "github" or "grid".

```python
from tabulate import tabulate, SEPARATING_LINE

table = [["spam", 41.9999], SEPARATING_LINE, ["eggs", 451]]

print(tabulate(table, tablefmt="github"))
```

Expected something like:
```
|------|----------|
| spam |  41.9999 |
|------|----------|
| eggs | 451      |
```

Instead I get a broken row where the separator is replaced by a stray control character and the column widths are lost, e.g. a line like `|  |` with an unprintable char in it instead of a proper dashed separator. It only happens with formats that have extra padding or repeat the row line (github, grid); plain formats like "simple" render the separating line fine. Would expect the separator row to always come out as a normal divider regardless of tablefmt.

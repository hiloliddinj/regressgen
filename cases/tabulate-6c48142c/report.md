When using `maxcolwidths` on a cell that already contains a manual line break (`\n`), the existing line break gets collapsed/merged with the wrapped text instead of being preserved.

```python
from tabulate import tabulate

table = [["123456789 bbb\nccc"]]
print(tabulate(table, tablefmt="grid", maxcolwidths=10))
```

Got:
```
+-----------+
| 123456789 |
| bbb ccc   |
+-----------+
```

The `\n` between "bbb" and "ccc" got turned into a space and joined onto the same line, even though it fits fine on its own line width-wise.

I expected the original line break to be kept as a separate line, something like:

```
+-----------+
| 123456789 |
| bbb       |
| ccc       |
+-----------+
```

Seems like the wrapping logic used for `maxcolwidths` doesn't respect existing newlines in the cell content and just re-flows everything as one paragraph.

When using `maxcolwidths` together with data that contains the string `"True"`/`"False"` or `None` values, `tabulate` crashes instead of wrapping the text.

```python
from tabulate import tabulate

data = [
    ["First Entry", "True"],
    ["Second Entry", None],
]
headers = ["Title", "When"]
print(tabulate(data, headers=headers, tablefmt="grid", maxcolwidths=[7, 5]))
```

This raises a `TypeError` deep inside the text-wrapping logic (it ends up trying to call `bool("True")` or `bool(None)` and then treat the result as something wrappable, which fails).

Without `maxcolwidths`, the same data tabulates fine and `"True"`/`None` are rendered as plain text. I expected `maxcolwidths` to behave the same way — wrapping the string representation of the cell (`"True"`, `""` for `None`, etc.) rather than raising an exception. This seems to be a side effect of how cell types are detected/cast when a column width is set, since numeric cells work fine but bool-like strings and `None` don't.

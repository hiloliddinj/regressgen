Calling `tabulate` with an empty data list, headers, and the `maxheadercolwidths` kwarg raises an `IndexError` instead of just printing the headers.

```python
from tabulate import tabulate

print(tabulate([], headers=["one", "two", "three"], maxheadercolwidths=5))
```

Expected output:

```
one    two    three
-----  -----  -------
```

Instead I get:

```
Traceback (most recent call last):
  ...
IndexError: list index out of range
```

This is basically the same issue as #365 for `maxcolwidths`/`colalign` with empty tables, but it shows up again for `maxheadercolwidths` — passing an empty `tabular_data` combined with header column width limits blows up instead of degrading gracefully to just rendering the header row. Since headers should always be printable even when there are zero data rows, I'd expect `tabulate` to compute the header widths (capped by `maxheadercolwidths`) without needing to look at any data rows, and just return the two-line header/separator output shown above, same as it does when `maxheadercolwidths` isn't passed at all.

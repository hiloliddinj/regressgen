Calling `tabulate([], maxcolwidths=5)` throws an exception instead of just giving back an empty table. Looks like when there's no rows at all, whatever handles the maxcolwidths option chokes on the empty data before it can bail out and just return an empty string like tabulate normally does for empty input.

Repro:

```python
from tabulate import tabulate

print(tabulate([], maxcolwidths=5))
```

Without `maxcolwidths` set, `tabulate([])` returns `""` just fine, so this only shows up when that option is passed alongside empty data.

Expected: same empty-string result as calling `tabulate([])` without the option, since there's no data to wrap column widths for anyway.

Got: a traceback instead, so any code path that conditionally adds `maxcolwidths` but might receive empty data now needs a special-case guard just to avoid crashing.

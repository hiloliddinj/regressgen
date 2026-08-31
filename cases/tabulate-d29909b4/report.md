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

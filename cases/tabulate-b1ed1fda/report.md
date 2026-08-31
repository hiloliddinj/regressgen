SEPARATING_LINE renders garbage in orgtbl format

When using SEPARATING_LINE in a table with tablefmt="orgtbl", the separator row doesn't come out as a proper line — instead of a real dashed separator row like `|-----------+-----------|` I get a broken/garbled row with what looks like a stray control character in it.

Repro:

```python
from tabulate import tabulate, SEPARATING_LINE

table = [
    ["spam", 41.9999],
    SEPARATING_LINE,
    ["eggs", 451],
]
headers = ["strings", "numbers"]

print(tabulate(table, headers, tablefmt="orgtbl"))
```

Expected output should have a proper separator line matching the column widths, similar to how this works fine with tablefmt="simple" or "grid". Instead the orgtbl output has some garbage in place of the separator row, which breaks the table formatting badly. Seems specific to orgtbl - other formats handle SEPARATING_LINE correctly.

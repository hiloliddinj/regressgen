Calling `tabulate` with an empty data list but with `maxheadercolwidths` set raises an error instead of just printing the headers. Since there are no rows, I'd expect it to behave the same as if `maxheadercolwidths` wasn't passed at all (just format the header row), but instead it blows up.

Repro:

```python
from tabulate import tabulate

print(tabulate([], headers=["one", "two", "three"], maxheadercolwidths=5))
```

Expected: just the header row rendered normally, something like:

```
one    two    three
-----  -----  -------
```

Actual: it throws an exception instead of returning the table. Works fine if I pass at least one row of data, so it seems specific to the empty-table case combined with `maxheadercolwidths`. Would expect empty tables to be handled consistently regardless of which column-width kwargs are set, same as `maxcolwidths` already works fine with empty data.

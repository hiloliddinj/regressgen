tabulate mangles Decimal values when applying floatfmt, giving a result that isn't even a correctly-rounded version of the input.

```python
from decimal import Decimal
from tabulate import tabulate

print(tabulate(
    [[Decimal("99999998999.999980"), 1234.5, 1.2345678, "inf"]],
    floatfmt=".6f",
    tablefmt="plain",
))
```

Expected the Decimal to be formatted to 6 decimal places while preserving its exact value, something like:

```
99999998999.999980  1234.500000  1.234568  inf
```

Instead I get:

```
99999998999.999985  1234.500000  1.234568  inf
```

Notice the last two digits changed from `80` to `85` — that's not a rounding artifact of just cutting to 6 decimals, it's actually a different number than what I put in. The whole point of using Decimal instead of float is to avoid this kind of precision drift, so this defeats the purpose. Floats in the same row format fine. Would expect Decimal to be handled with its own precision rather than going through whatever path floats take.

When formatting a table containing `decimal.Decimal` values with `floatfmt`, tabulate silently corrupts the value because it converts it to a regular `float` before formatting, introducing binary floating-point rounding error even though `Decimal` is specifically meant to preserve exact fixed-point precision.

```python
from decimal import Decimal
from tabulate import tabulate

result = tabulate(
    [[Decimal("99999998999.999980"), 1234.5, 1.2345678, "inf"]],
    floatfmt=".6f",
    tablefmt="plain",
)
print(result)
```

Got:
```
99999998999.999985  1234.500000  1.234568  inf
```

Expected:
```
99999998999.999980  1234.500000  1.234568  inf
```

Since `Decimal("99999998999.999980")` is an exact value, formatting it with `.6f` should never change its digits beyond what the format precision dictates — it should print `99999998999.999980`, not silently drift to `...985` due to a float conversion. I'd expect `Decimal` inputs to be formatted using their own fixed-point arithmetic rather than being coerced through `float()`, so precision-critical values (e.g. currency, measurements) stay exact.

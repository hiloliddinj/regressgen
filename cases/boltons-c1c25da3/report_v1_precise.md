`Bits(val, len_)` is supposed to validate that `val` actually fits in `len_` bits, but it accepts values that are one bit too large without complaining. For example:

```python
from boltons.mathutils import Bits

b = Bits(4, 2)
print(b.as_bin())  # prints '100', 3 characters for a length-2 Bits!
```

`2 ** len_` (here, `4`) does not fit in `len_` bits — the largest value representable in 2 bits is `3` (`0b11`). Constructing `Bits(4, 2)` should raise `ValueError` since the value is out of range for the requested length, but instead it silently creates a `Bits` object whose binary representation is longer than the length I asked for.

Similarly, `Bits(1, 0)` should raise `ValueError` (no bits available to hold the value `1`) but doesn't.

Expected: constructing a `Bits` with a value that doesn't fit in the given bit length should raise `ValueError`, and `as_bin()`/`as_int()` should always round-trip consistently with the declared length. Only values up to `2 ** len_ - 1` should be accepted.

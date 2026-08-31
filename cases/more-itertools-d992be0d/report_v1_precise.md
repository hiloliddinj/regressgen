`running_min` and `running_max` don't behave like Python's built-in `min`/`max` when values compare equal but have different types. Built-in `min(x, y)` returns `x` when `x == y`, but `running_min`/`running_max` seem to return the *later* value instead of the earlier one in that case.

```python
from fractions import Fraction
from more_itertools import running_min, running_max

data = [0, 0.0, Fraction(0)]
print(list(map(type, running_min(data, maxlen=2))))
# got:      [int, float, Fraction]
# expected: [int, int, float]

print(list(map(type, running_max(data, maxlen=2))))
# same mismatch
```

Since all values in `data` are numerically equal, I'd expect the result types to match what plain `min`/`max` would pick when comparing pairs — i.e. the earlier operand should win on ties, consistent with `min(a, b)` returning `a` when `a == b`. Instead the returned type corresponds to the newer element in the window, which breaks stability guarantees when tracking running min/max over a sliding window of equal-but-differently-typed values.

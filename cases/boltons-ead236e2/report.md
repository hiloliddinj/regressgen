Calling `backoff()` with `factor=1.0` and no explicit `count` blows up with a `ZeroDivisionError` instead of a normal exception or a result.

```python
from boltons.iterutils import backoff

backoff(1, 10, factor=1.0)
```

This raises `ZeroDivisionError` from inside the function. I get that a constant factor of 1.0 means there's no growth, so you can't infer how many steps it'd take to go from start to stop — but that should be reported as a `ValueError` like the other invalid-argument cases, not crash with an unrelated arithmetic error.

Also, passing an explicit `count` alongside `factor=1.0` should just work and return that many identical values, e.g. `backoff(2, 10, count=3, factor=1.0)` — currently that also fails the same way even though count is given, which I really didn't expect.

Expected: either a clear `ValueError` explaining count can't be inferred when factor is 1.0, or if count is provided, a normal list of constant values.

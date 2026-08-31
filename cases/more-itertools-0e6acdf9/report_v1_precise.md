Passing a negative value for `n` to `chunked()` doesn't fail with a helpful error. Instead it raises a confusing `ValueError` from deep inside `itertools.islice`, which is not something a caller would expect to see or be able to make sense of without digging into the implementation.

```python
import more_itertools as mi

list(mi.chunked('ABCDE', -1))
```

This raises:

```
ValueError: Stop argument for islice() must be None or an integer: 0 <= x <= sys.maxsize.
```

I'd expect `chunked()` to validate its `n` argument up front and raise a `ValueError` with a clear message like "n must be at least 0", the same way `sliced()` already does when given a negative size. Right now the two functions behave inconsistently for the same kind of invalid input, and the error message from `chunked()` gives no indication that the problem is the `n` argument at all.

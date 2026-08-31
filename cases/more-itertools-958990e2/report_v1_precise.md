`sliced()` doesn't validate the `n` argument, so calling it with a negative size doesn't raise an error but instead silently produces incorrect/unexpected results (or an infinite-looking sequence of empty slices, depending on the input).

```python
import more_itertools as mi

seq = 'ABCDEFG'
print(list(mi.sliced(seq, -1)))
```

I expected this to raise a `ValueError`, since a negative slice size doesn't make sense semantically — you can't split a sequence into chunks of negative length. Instead it just runs and returns something like `['']` or similar garbage without any indication that the input was invalid.

This also affects `strict=True` mode — I'd expect the same `ValueError` there too, not a silent pass-through.

Since there's no validation, it's easy to accidentally pass a negative number (e.g. from a miscalculated offset) and get a confusing result instead of an immediate, obvious error pointing at the bad input.

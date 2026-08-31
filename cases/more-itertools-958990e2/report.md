`sliced()` doesn't complain if you pass a negative size, it just quietly does something weird instead of telling you the input is invalid.

```python
import more_itertools as mi

seq = 'ABCDEFG'
print(list(mi.sliced(seq, -1)))
print(list(mi.sliced(seq, -1, strict=True)))
```

I expected this to raise a `ValueError` since a negative slice size doesn't make sense, similar to how other bad inputs are rejected elsewhere in the library. Instead it runs without error and gives back a result that isn't the sliced sequence I'd expect (definitely not chunks of `seq`). This is easy to hit by accident, e.g. if a size is computed from some other value and ends up negative — no exception, just silently wrong output that could go unnoticed downstream.

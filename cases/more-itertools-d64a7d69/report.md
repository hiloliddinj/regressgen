`tail(-1, iterable)` doesn't raise or return anything sensible when the iterable is sized (has a length, like a string or list). Instead of an error it just silently returns something wrong.

Repro:

```python
import more_itertools as mi

list(mi.tail(-1, 'ABCDEFG'))
```

I expected this to raise a ValueError (or similar) since a negative count doesn't make sense for "last n items". Passing a negative n to a generic iterable (like a generator without a length) does seem to behave differently, so the sized case seems to be handled separately and skips the validation. Would be nice if both code paths agreed and negative sizes were rejected consistently regardless of whether the input has a known length.

Reversing an empty `numeric_range` throws an `IndexError` instead of just giving me an empty sequence. Regular `range` handles this fine, so I expected `numeric_range` to behave the same way.

```python
import more_itertools as mi

list(reversed(mi.numeric_range(0)))
```

This raises:

```
IndexError: numeric range object index out of range
```

but for comparison:

```python
list(reversed(range(0)))  # -> []
```

works with no problem. I'd expect `reversed()` on an empty `numeric_range` to just return an empty iterator/list like it does for the built-in `range`, not blow up. Ran into this while writing some generic code that iterates over ranges in reverse order and happened to hit a zero-length range as an edge case — had to add a special-case check just to avoid the crash, which seems unnecessary.

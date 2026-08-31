random_product() with repeat > 1 raises IndexError when passed iterators instead of lists/sequences.

```python
import more_itertools as mi

nums = [1, 2, 3]
lets = ['a', 'b', 'c']

# works fine
r = list(mi.random_product(nums, lets, repeat=100))

# fails
r = list(mi.random_product(iter(nums), iter(lets), repeat=100))
```

The second call blows up with:

```
IndexError: Cannot choose from an empty sequence
```

Passing plain lists works fine with repeat, and passing iterators works fine when repeat=1 (default), so it seems specific to combining iterators with repeat > 1. I'd expect random_product to accept iterables the same way other itertools-style functions in this library do, and either consume them once and reuse the resulting pools for each repeat, or just document clearly that iterators aren't supported here. Right now it silently works for one case and throws for a very similar one, which was confusing to debug since the traceback doesn't hint at the iterable-vs-iterator issue at all.

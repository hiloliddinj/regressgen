IndexedSet slicing returns wrong results after any item has been removed with `pop`/`discard`.

```python
from boltons.setutils import IndexedSet

x = IndexedSet(range(10))
x.pop(2)  # remove one element

print(list(x))     # [0, 1, 3, 4, 5, 6, 7, 8, 9]
print(list(x[1:4]))  # I expected [1, 3, 4]
```

Instead I get `[1, 3, 4, 5]` — one extra element. It looks like the slice is being computed against the underlying storage rather than the set's current visible contents, so once anything has been removed, indices past the removal point get thrown off by however many items were removed. This happens with plain slices, negative indices, and negative stops too, not just this one case. Since IndexedSet is supposed to behave like a list for indexing/slicing purposes once you've removed anything from it, this makes slicing pretty unreliable — you can't trust `x[a:b]` to correspond to the actual sequence of items you'd get from iterating or indexing individually.

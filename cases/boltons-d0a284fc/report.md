IndexedSet doesn't raise IndexError for negative indices that are way out of range - instead it silently wraps around and returns some other element. Same problem happens with pop().

Example:

```python
from boltons.setutils import IndexedSet

x = IndexedSet(range(10))
x.pop(2)  # len is now 9

print(x[-1])   # 9, fine
print(x[-10])  # expected IndexError, got 9 back instead

x.pop(-15)  # expected IndexError, instead silently removes some unrelated element
print(4 in x)  # False - 4 got popped even though -15 is nowhere close to valid range
```

For a set of length 9, I'd expect indices from -9 to 8 to be valid and anything outside that to raise IndexError, same as it would for a list. Instead negative indices seem to get normalized twice somehow, so something like -10 or -15 just quietly maps to a valid-looking slot instead of raising. This is pretty dangerous with pop() since it can delete the wrong item without any warning that the index was invalid.

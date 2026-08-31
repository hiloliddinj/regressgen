TLRUCache: overwriting an existing key with a value that is already expired at insertion time keeps the old value instead of dropping the key.

Repro:

```python
from cachetools import TLRUCache

def ttu(_k, value, t):
    return t + value

cache = TLRUCache(maxsize=2, ttu=ttu, timer=lambda: 0)
cache[1] = 5
print(cache[1])  # 5, fine

cache[1] = 0  # ttu(1, 0, t) == t, so it's expired the instant it's set
print(1 in cache)   # True <- unexpected
print(cache[1])      # 5 <- old stale value still there
```

I expected setting `cache[1] = 0` to either evict key 1 (since the new value has no valid lifetime) or raise, but instead the cache just keeps serving the previous value as if nothing happened. `len(cache)` and `currsize` also stay as if the old entry is still valid. This is confusing since the value you just assigned is simply gone but the key doesn't reflect that at all - a lookup after this assignment should not silently keep returning old data.

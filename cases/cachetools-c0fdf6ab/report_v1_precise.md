When I assign a new value to an existing key in a `TLRUCache`, and the new value's TTU makes it already expired at insertion time, the cache keeps the *old* value instead of evicting the key. I expected the key to end up expired/removed, not silently retain stale data.

Repro:

```python
from cachetools import TLRUCache

def ttu(_k, value, t):
    return t + value

cache = TLRUCache(maxsize=2, ttu=ttu, timer=lambda: 0)
cache[1] = 5
print(cache[1])  # 5

cache[1] = 0  # ttu(_, 0, t) == t -> immediately expired
print(1 in cache)   # prints True, but should be False
print(cache.get(1))  # returns 5, but should be None
```

Since the new value is dead-on-arrival according to its own TTU, assigning it can't actually store a live value under that key. I'd expect `cache[1] = 0` in this case to behave as if the key were evicted/expired, so `1 in cache` is `False` and `cache.get(1)` returns `None`, rather than leaving the previous value (`5`) accessible.

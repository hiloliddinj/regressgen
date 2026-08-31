`TTLCache.expire()` returns `None` instead of the expired items. I was trying to use it to get a list of the (key, value) pairs that were removed due to TTL expiry, but calling it just gives `None`, so anything trying to iterate over the result blows up with `TypeError: 'NoneType' object is not iterable`.

Repro:

```python
from cachetools import TTLCache
from datetime import datetime, timedelta

cache = TTLCache(maxsize=1, ttl=timedelta(days=1), timer=datetime.now)
cache[1] = 1

items = cache.expire(datetime.now() + timedelta(days=1))
print(list(items))  # TypeError: 'NoneType' object is not iterable
```

I expected `expire()` to return an iterable of the `(key, value)` pairs that were expired and removed from the cache (empty if nothing expired), similar to how you'd want to inspect/log evicted entries. Instead it silently discards that information and returns `None`, making it impossible to know what was expired without re-implementing the expiry logic yourself.

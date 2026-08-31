Using `unittest.mock.create_autospec` on a class that has a `@cachedmethod`-decorated method fails with an `AttributeError` instead of working normally.

```python
import unittest.mock
from cachetools import LRUCache, cachedmethod


class Cached:
    def __init__(self):
        self.cache = LRUCache(maxsize=10)

    @cachedmethod(lambda self: self.cache)
    def get(self, key):
        return key


unittest.mock.create_autospec(Cached, instance=True)
```

This raises:

```
AttributeError: 'NoneType' object has no attribute '__dict__'
```

coming from inside the descriptor's `__get__`, when `obj` is `None` and `self.__attrname` is not `None` — it tries `obj.__dict__.setdefault(...)` without checking that `obj` is actually an instance.

`create_autospec` calls `getattr(spec, attr, None)` on the class itself (not an instance) while introspecting attributes, so `obj` ends up being `None`. This is a normal and expected way to introspect a class, so it shouldn't raise at all — `create_autospec` should succeed and produce a mock, exactly like it does for classes without `cachedmethod`.

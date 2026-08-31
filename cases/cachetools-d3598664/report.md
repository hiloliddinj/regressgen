`cachetools.func.mru_cache` doesn't warn that it's deprecated, unlike some of the other decorators in that module which do print a `DeprecationWarning` when used. Since MRU caching seems like it's on its way out (or at least discouraged), I'd expect using it to at least give a heads up so people can migrate away from it, similar to how other soon-to-be-removed things behave.

Repro:

```python
import warnings
import cachetools.func

with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    cached = cachetools.func.mru_cache(maxsize=2)(lambda n: n)

print(w)  # expected at least one DeprecationWarning, got an empty list
```

Nothing is printed/captured, `w` stays empty. I expected calling `mru_cache` to raise a `DeprecationWarning` so tooling and users get notified before it's eventually removed, but instead it silently behaves like a normal supported decorator with no indication anything is off.

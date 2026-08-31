Feature request: a `synchronized` decorator/helper to make generators (or generator-based iterators) safe to call from multiple threads concurrently.

I have generator objects that get shared across worker threads, and calling `next()` on the same generator instance from different threads at the same time causes interleaved/corrupted state (or outright errors), since generators aren't thread-safe on their own. Right now I have to hand-roll a lock wrapper around every generator I want to share, which is tedious and easy to get wrong.

I expected `more_itertools` to have something like a `synchronized` wrapper, similar in spirit to `serialize`, that I could apply to a generator function so that each call to it is serialized with a lock, guaranteeing only one thread advances the generator at a time.

```python
import more_itertools as mi

@mi.synchronized
def counter():
    i = 0
    while True:
        yield i
        i += 1
```

This raises `AttributeError: module 'more_itertools' has no attribute 'synchronized'` — there's currently no equivalent in the library that I could find.

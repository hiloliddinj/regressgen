Passing a negative `n` to `chunked()` doesn't give a helpful error. Instead of telling me the argument is invalid, it blows up with a confusing internal error about `islice()` arguments, which makes it look like something is broken inside the library rather than me just passing a bad value.

```python
import more_itertools as mi

list(mi.chunked('ABCDE', -1))
```

This raises:

```
ValueError: Stop argument for islice() must be None or an integer: 0 <= x <= sys.maxsize.
```

I'd expect a straightforward `ValueError` telling me that `n` needs to be non-negative, similar to how `sliced()` handles this case. Right now the error message doesn't mention `chunked` or `n` at all, so it's not obvious what I did wrong unless you already know how the function is implemented.

`validators.disabled()` context manager doesn't handle nesting correctly - exiting the inner context re-enables validators even though the outer context is still active.

Repro:

```python
import attr
from attr import validators

with validators.disabled():
    with validators.disabled():
        pass
    # validators are re-enabled here, even though we're still
    # inside the outer `disabled()` block
    @attr.s
    class C:
        x = attr.ib(validator=attr.validators.instance_of(int))

    C(x="not an int")  # this raises, but I expected it not to
```

I expected validators to stay disabled for the whole duration of the outer context manager, regardless of how many times `disabled()` is nested inside it. Instead, the inner context manager's exit turns validation back on immediately, so any code between the inner and outer `with` blocks runs with validators active again. This makes `disabled()` unsafe to use in helper functions that might themselves be called from within an already-disabled block, since it silently changes behavior depending on nesting.

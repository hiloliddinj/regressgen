Frozen exception classes made with attrs blow up as soon as Python tries to attach a traceback to them. This happens even without doing anything unusual - just raising the exception inside a context manager (e.g. contextlib.contextmanager based ones) triggers it, and even manually re-assigning the traceback attribute to itself fails.

```python
import attrs
from contextlib import contextmanager

@attrs.frozen
class MyException(Exception):
    pass

@contextmanager
def do_nothing():
    yield

try:
    with do_nothing():
        raise MyException()
except MyException as e:
    e.__traceback__ = e.__traceback__  # raises FrozenInstanceError
```

I expected exception instances to still allow their traceback to be set/updated, since that's normal exception machinery, not user code touching frozen fields. Instead it raises FrozenInstanceError, which makes frozen exceptions basically unusable in combination with context managers or manual re-raising.

FrozenInstanceError raised on frozen attrs classes doesn't carry a message. If I try to set or delete an attribute on a frozen instance, I get an empty exception - no "can't set attribute" text or anything, just the bare exception class with no args.

```python
import attr
from attr.exceptions import FrozenInstanceError

@attr.s(frozen=True)
class Frozen:
    x = attr.ib()

f = Frozen(1)
try:
    f.x = 2
except FrozenInstanceError as e:
    print(repr(e.args))
    print(repr(getattr(e, "msg", None)))
```

This prints empty args and `msg` is missing/None. Same thing happens on `del f.x`.

I'd expect the exception to actually explain what went wrong, e.g. something like "can't set attribute", available both as the exception message and via `.msg`, similar to how a normal frozen dataclass/object raises. Right now it's silent, which makes debugging or matching on the error message impossible.

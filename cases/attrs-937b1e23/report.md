`__attrs_pre_init__` is receiving the wrong values for some attributes when the class has a mix of positional, defaulted, and keyword-only fields.

```python
import attr

@attr.define
class MixtureClass:
    val1: int
    val2: int = 100
    val3: int = attr.field(factory=int)
    val4: int = attr.field(kw_only=True)
    val5: int = attr.field(default=100, kw_only=True)
    val6: int = attr.field(factory=int, kw_only=True)

    def __attrs_pre_init__(self, val1, val2, val3, val4, val5, val6):
        print(val1, val2, val3, val4, val5, val6)

MixtureClass(val1=200, val2=200, val3=200, val4=200, val5=200, val6=200)
```

I expected `__attrs_pre_init__` to be called with all values equal to 200, matching what's passed to the constructor and what ends up on the instance. Instead `val2` (and possibly others) shows up as `100`, i.e. the default value, even though I explicitly passed `200`. The final instance attribute is correct, it's just the pre_init call that gets stale/default values instead of the actual arguments.

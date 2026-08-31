I'm using a list of converters with `attr.define` (so `on_setattr` is implied), and after construction, setting the attribute again doesn't seem to re-run the converter pipeline correctly.

```python
import attr

@attr.define
class C:
    x = attr.field(converter=[int])

c = C("1")
print(c.x)   # 1, fine

c.x = "2"
print(c.x)   # I expected this to be 2 (int), but it's not converted properly
```

The initial construction converts fine, but assigning afterwards doesn't behave like it went through the same converter chain. I also noticed something odd when combining `attr.Converter(...)` (with `takes_self`/`takes_field`) inside a converter list together with `setters.pipe` — the value/instance/field passed through don't line up with what I'd expect, and separately a `Converter` instance doesn't survive a pickle round trip as a normal callable. Feels like list-converters and `on_setattr` pipes aren't interacting the way single-callable converters do.

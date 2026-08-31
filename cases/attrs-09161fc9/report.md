Using a pre-init hook together with a keyword-only field that has a default value causes class creation to blow up with a syntax error in the generated init code, not even a normal Python exception you'd expect from bad user code.

Repro:

```python
import attr

@attr.define
class Foo:
    kw_and_default: int = attr.field(kw_only=True, default=3)

    def __attrs_pre_init__(self, *, kw_and_default):
        print(kw_and_default)

Foo()
```

This raises a SyntaxError coming from compiling the generated init source, with the traceback showing the generated code has a malformed parameter default assignment (something like `default=kw_and_default=attr_dict[...].default` duplicated oddly). It only shows up when all three things are combined: a pre-init hook that takes the field, kw_only=True, and a default value. Removing any one of those makes it work fine.

I expected the class to just be created normally and the pre-init hook to receive the default value like it does without kw_only. Instead the class definition itself fails before I even get to instantiate anything.

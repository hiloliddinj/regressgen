Comparing a `Version` subclass instance against a plain `Version` instance behaves inconsistently depending on which side calls the comparison.

```python
from semver import Version

class SemVerSubclass(Version):
    pass

a = SemVerSubclass.parse("1.0.0")
b = Version.parse("1.0.0")

a.compare(b)   # raises TypeError instead of comparing
b.compare(a)   # returns 0, fine

a == b   # ?
b == a   # True
```

`SemVerSubclass.parse("1.0.0").compare(Version.parse("1.0.0"))` should either compare successfully (since the subclass instance carries the same major/minor/patch/prerelease/build data) or, if it's meant to reject unrelated types, that decision should be symmetric.

More importantly, `__eq__` should follow normal Python semantics: when comparing a subclass instance against a base-class instance in a context where `compare()` can't reconcile the types, `__eq__` should return `NotImplemented` rather than raising, so Python falls back to the reflected `__eq__` on the other object. Right now calling `SemVerSubclass.parse("1.0.0") == Version.parse("1.0.0")` (or `.__eq__` directly) raises a `TypeError` propagated from `compare` instead of returning `NotImplemented`, while `Version.parse("1.0.0") == SemVerSubclass.parse("1.0.0")` works and returns `True`. This asymmetry breaks equality invariants for subclasses.

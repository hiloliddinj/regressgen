`Version.replace()` doesn't respect subclassing — it returns a plain `Version` instance instead of an instance of the subclass it was called on, which means any overridden `__str__` (or other subclass behavior) is lost.

Following the "Creating Subclasses from Version" example in the docs:

```python
from semver import Version

class SemVerWithVPrefix(Version):
    @classmethod
    def parse(cls, version):
        if version[0] not in ("v", "V"):
            raise ValueError(f"{version!r} must start with 'v' or 'V'")
        return super().parse(version[1:], optional_minor_and_patch=True)

    def __str__(self):
        return "v" + super().__str__()

version = SemVerWithVPrefix.parse("v1.1.0")
dev_version = version.replace(prerelease="dev.0")
print(str(dev_version))
```

I expected this to print `v1.1.0-dev.0`, since `dev_version` should be a `SemVerWithVPrefix` instance and use its overridden `__str__`. Instead it prints `1.1.0-dev.0`, showing that `replace()` silently produced a base `Version` object rather than calling the subclass's constructor/parse logic.

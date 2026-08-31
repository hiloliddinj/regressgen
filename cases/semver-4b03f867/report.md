`replace()` doesn't return an instance of the subclass when called on a subclassed Version

I have a subclass of `Version` that adds a "v" prefix (basically the pattern from the docs' "Creating Subclasses from Version" example, overriding `parse` and the string conversion). Parsing works fine and printing gives back the "v" prefix. But calling `.replace()` on an instance of the subclass seems to fall back to plain `Version` behavior — the prefix is lost in the output.

```python
class SemVerWithVPrefix(Version):
    @classmethod
    def parse(cls, version):
        if version[0] not in ("v", "V"):
            raise ValueError("must start with v or V")
        return super().parse(version[1:], optional_minor_and_patch=True)

    def __str__(self):
        return "v" + super().__str__()

version = SemVerWithVPrefix.parse("v1.1.0")
dev_version = version.replace(prerelease="dev.0")
print(str(dev_version))
```

I expected `v1.1.0-dev.0`, but got `1.1.0-dev.0` — as if `replace` built a base `Version` instead of a `SemVerWithVPrefix`. Parsing alone works correctly, it's specifically `replace` that seems to lose the subclass behavior.

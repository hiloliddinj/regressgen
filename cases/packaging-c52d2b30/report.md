Version matching with `==` and a wildcard seems to be broken when the version string has more "parts" than usual, combined with an epoch being present (or absent) mismatched between the version and the specifier.

For example, I expected `2!1.0` to NOT match `==1.0.0.*` (different epoch, so this should be excluded), but it seems to match. Similarly `1.0` should not match `==2!1.0.0.*`, and `2!1.0.0` should match `==2!1.0.0.0.*`, but the results I'm getting are inconsistent/wrong.

```python
from packaging.specifiers import SpecifierSet

print(SpecifierSet("==1.0.0.*").contains("2!1.0"))      # I expected False
print(SpecifierSet("==2!1.0.0.*").contains("1.0"))       # I expected False
print(SpecifierSet("==2!1.0.0.0.*").contains("2!1.0.0")) # I expected True
```

It looks like once the specifier has more trailing zero segments than the normal `X.Y` shape, the epoch check for wildcard `==` matching stops working correctly. Would expect epoch mismatches to always be excluded regardless of how many segments are in the wildcard specifier.

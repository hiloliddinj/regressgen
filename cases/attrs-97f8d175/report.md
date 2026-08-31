On Python 3.14, `attr.s(auto_attribs=True)` no longer strips out `ClassVar` attributes if the annotation ends up being a forward reference (which seems to happen more with newer annotation evaluation behavior). Instead of skipping the ClassVar, attrs treats it as a normal attribute.

```python
import attr
from typing import ClassVar

@attr.s(auto_attribs=True)
class C:
    cls_var: ClassVar[str]
    value: int = 1

print(attr.fields_dict(C))
```

I expected `cls_var` to not show up in `attr.fields_dict(C)` at all, same as it doesn't when running on older Python versions. Instead it gets picked up as a real attribute, which then messes with init generation and the general fields list. This only shows up when the ClassVar annotation is represented as a forward reference rather than the resolved `typing.ClassVar` object — plain string annotations like `"ClassVar[str]"` seem to work fine already.

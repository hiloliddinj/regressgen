# Trajectory — `baseline` on `attrs-97f8d175`

**Verdict: REPRO**  (fails on buggy, passes on fixed — reproduces the bug)

- cost `$0.06839` · wall `29.6s` · tool calls `0`

## 1. Agent instructions (system prompt)

```
You are given a Python repository that contains a real bug, plus the bug report a user filed against it.

Write ONE pytest test file that is a regression test for that bug.

HOW YOUR TEST IS GRADED — the two-sided gate:
  * It must FAIL on the current (buggy) code.
  * It must PASS on the fixed code, which you will never see.

Both halves matter and they pull against each other. `assert False` fails on the
buggy code and also fails on the fixed code, so it scores zero. A test of
behaviour that already works passes on both, so it scores zero too. Only a test
that pins down the CORRECT expected behaviour — the behaviour the report says
*should* happen — satisfies both halves.

So: assert what the code SHOULD do, never merely record what it currently does.

Return ONLY the complete test file, in a single ```python fenced code block.
No commentary before or after. The file must be self-contained and importable.
```

## 2. Task (user prompt)

The agent receives the bug report and the repository layout. It never sees the fixed tree, the upstream fix, or the maintainer's test.

```
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
```

## 3. Tool calls

_No tools — this system answers in a single prompt._

## 4. Submitted test

```python
"""
Regression test for the bug where `attr.s(auto_attribs=True)` fails to
strip out `typing.ClassVar` annotations when the annotation value is a
forward reference (e.g. `typing.ForwardRef("ClassVar[str]")`) instead of
a resolved `typing.ClassVar[...]` object or a plain string.

See: attrs GitHub issue about ClassVar handling regressing on Python 3.14
where annotations can be represented as ForwardRef objects.
"""

import typing

import attr


def test_classvar_forward_ref_is_stripped():
    """
    A ClassVar annotation represented as a `typing.ForwardRef` object
    (rather than a resolved `typing.ClassVar` or plain string) must still
    be recognized and excluded from the generated attrs fields.
    """

    class C:
        value: int = 1

    # Simulate the "forward reference" annotation scenario: the annotation
    # for `cls_var` is a ForwardRef object wrapping the ClassVar string,
    # instead of a plain string or a resolved typing.ClassVar object.
    C.__annotations__ = {
        "cls_var": typing.ForwardRef("ClassVar[str]"),
        "value": int,
    }

    C = attr.s(auto_attribs=True)(C)

    fields = attr.fields_dict(C)

    assert "cls_var" not in fields, (
        "ClassVar annotation represented as a forward reference was not "
        "stripped and leaked into the attrs fields."
    )
    assert "value" in fields

    # Since cls_var should not be a real attrs field, it must not show up
    # as a required __init__ parameter either.
    inst = C()
    assert inst.value == 1
```

## 5. Two-sided gate

### Against `buggy/` — exit 1 (must be non-zero)

```
F                                                                        [100%]
=================================== FAILURES ===================================
____________________ test_classvar_forward_ref_is_stripped _____________________

    def test_classvar_forward_ref_is_stripped():
        """
        A ClassVar annotation represented as a `typing.ForwardRef` object
        (rather than a resolved `typing.ClassVar` or plain string) must still
        be recognized and excluded from the generated attrs fields.
        """
    
        class C:
            value: int = 1
    
        # Simulate the "forward reference" annotation scenario: the annotation
        # for `cls_var` is a ForwardRef object wrapping the ClassVar string,
        # instead of a plain string or a resolved typing.ClassVar object.
        C.__annotations__ = {
            "cls_var": typing.ForwardRef("ClassVar[str]"),
            "value": int,
        }
    
        C = attr.s(auto_attribs=True)(C)
    
        fields = attr.fields_dict(C)
    
>       assert "cls_var" not in fields, (
            "ClassVar annotation represented as a forward reference was not "
            "stripped and leaked into the attrs fields."
        )
E       AssertionError: ClassVar annotation represented as a forward reference was not stripped and leaked into the attrs fields.
E       assert 'cls_var' not in {'cls_var': Attribute(name='cls_var', default=NOTHING, validator=None, repr=True, eq=True, eq_key=None, order=True, or...=mappingproxy({}), type=<class 'int'>, converter=None, kw_only=False, inherited=False, on_setattr=None, alias='value')}

tests/test_regressgen_candidate.py:38: AssertionError
=========================== short test summary info ============================
FAILED tests/test_regressgen_candidate.py::test_classvar_forward_ref_is_stripped
1 failed in 0.02s
```

### Against `fixed/` — exit 0 (must be zero)

```
.                                                                        [100%]
1 passed in 0.01s
```

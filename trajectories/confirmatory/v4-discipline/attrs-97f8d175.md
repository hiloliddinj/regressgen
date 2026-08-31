# Trajectory — `v4-discipline` on `attrs-97f8d175`

**Verdict: REPRO**  (fails on buggy, passes on fixed — reproduces the bug)

- cost `$0.29164` · wall `66.1s` · tool calls `9`

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

Start by locating the code the report is about. `list_files` shows the layout,
`search_code` finds symbols by regex, and `read_file` shows a file with line
numbers. Read the real implementation before you write anything — guessing an
API signature is the most common way this task fails.

You have `run_test`, which runs a candidate test file against the buggy code and
returns raw pytest output. Use it before submitting. If your test passes, it does
not reproduce the bug and you must rework it.

Before you submit, verify the failure is the RIGHT failure. Read the pytest
output and confirm:

  1. It fails on an assertion about behaviour (or raises exactly the exception
     the report names). A test that fails with ImportError, AttributeError, or
     TypeError because you guessed a wrong name or signature is worthless — it
     would fail on the fixed code too, and score zero.
  2. The value you wrote as "expected" is the CORRECT value from the report, not
     the buggy value you observed in the output.
  3. The assertion actually exercises the reported condition rather than some
     unrelated edge case that happens to be broken.

If the failure is a wrong-name error, fix the name and run it again.

Call `submit_test` exactly once with the complete test file when you are done.
The file must be self-contained and importable: include every import it needs.
Keep it focused — test this one bug, not the module in gen
... [6 more chars]
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

### 1. `search_code`(pattern="ClassVar")

Tool responded:

```
src/attr/_make.py:42: "typing.ClassVar",
src/attr/_make.py:43: "t.ClassVar",
src/attr/_make.py:44: "ClassVar",
src/attr/_make.py:45: "typing_extensions.ClassVar",
src/attr/_make.py:294: Check whether *annot* is a typing.ClassVar.
src/attr/_next_gen.py:295: Attributes annotated as `typing.ClassVar`, and attributes that are
tests/test_annotations.py:108: cls_var: typing.ClassVar[int] = 23
tests/test_annotations.py:402: from typing import ClassVar
tests/test_annotations.py:406: cls_var1: "typing.ClassVar[int]" = 23
tests/test_annotations.py:407: cls_var2: "ClassVar[int]" = 23
tests/test_annotations.py:408: cls_var3: "t.ClassVar[int]" = 23
tests/test_annotations.py:428: If ClassVar is coming from typing_extensions, it is recognized too.
tests/test_annotations.py:433: cls_var: "typing_extensions.ClassVar" = 23  # noqa: F821
tests/test_annotations.py:690: typing.ClassVar,
tests/test_annotations.py:691: "typing.ClassVar",
tests/test_annotations.py:692: "'typing.ClassVar[dict]'",
tests/test_annotations.py:693: "t.ClassVar[int]",
tests/test_annotations.py:698: ClassVars are detected, even if they're a string or quoted.
```

### 2. `read_file`(path="src/attr/_make.py", start=1, end=60)

Tool responded:

```
src/attr/_make.py lines 1-60 of 3439

    1| # SPDX-License-Identifier: MIT
    2| 
    3| from __future__ import annotations
    4| 
    5| import abc
    6| import contextlib
    7| import enum
    8| import itertools
    9| import linecache
   10| import sys
   11| import types
   12| import unicodedata
   13| import weakref
   14| 
   15| from collections.abc import Callable, Mapping
   16| from functools import cached_property
   17| from typing import Any, NamedTuple, TypeVar
   18| 
   19| # We need to import _compat itself in addition to the _compat members to avoid
   20| # having the thread-local in the globals here.
   21| from . import _compat, _config, setters
   22| from ._compat import (
   23|     PY_3_10_PLUS,
   24|     PY_3_11_PLUS,
   25|     PY_3_13_PLUS,
   26|     _AnnotationExtractor,
   27|     _get_annotations,
   28|     get_generic_base,
   29| )
   30| from .exceptions import (
   31|     DefaultAlreadySetError,
   32|     FrozenInstanceError,
   33|     NotAnAttrsClassError,
   34|     UnannotatedAttributeError,
   35| )
   36| 
   37| 
   38| # This is used at least twice, so cache it here.
   39| _OBJ_SETATTR = object.__setattr__
   40| _INIT_FACTORY_PAT = "__attr_factory_%s"
   41| _CLASSVAR_PREFIXES = (
   42|     "typing.ClassVar",
   43|     "t.ClassVar",
   44|     "ClassVar",
   45|     "typing_extensions.ClassVar",
   46| )
   47| # we don't use a double-underscore prefix because that triggers
   48| # name mangling when trying to create a slot for the field
   49| # (when slots=True)
   50| _HASH_CACHE_FIELD = "_attrs_cached_hash"
   51| 
   52| _EMPTY_METADATA_SINGLETON = types.MappingProxyType({})
   53| 
   54| # Unique object for unequivocal getattr() defaults.
   55| _SENTINEL = object()
   56| 
   57| _DEFAULT_ON_SETATTR = setters.pipe(setters.convert, setters.validate)
   58| 
   59| 
   60| class _Nothing(enum.Enum):
```

### 3. `read_file`(path="src/attr/_make.py", start=270, end=340)

Tool responded:

```
src/attr/_make.py lines 270-340 of 3439

  270|         __slots__ = ()
  271|         x = property(itemgetter(0))
  272|     """
  273|     attr_class_name = f"{cls_name}Attributes"
  274|     body = {}
  275|     for i, attr_name in enumerate(attr_names):
  276| 
  277|         def getter(self, i=i):
  278|             return self[i]
  279| 
  280|         body[attr_name] = property(getter)
  281|     return type(attr_class_name, (tuple,), body)
  282| 
  283| 
  284| # Tuple class for extracted attributes from a class definition.
  285| # `base_attrs` is a subset of `attrs`.
  286| class _Attributes(NamedTuple):
  287|     attrs: type
  288|     base_attrs: list[Attribute]
  289|     base_attrs_map: dict[str, type]
  290| 
  291| 
  292| def _is_class_var(annot):
  293|     """
  294|     Check whether *annot* is a typing.ClassVar.
  295| 
  296|     The string comparison hack is used to avoid evaluating all string
  297|     annotations which would put attrs-based classes at a performance
  298|     disadvantage compared to plain old classes.
  299|     """
  300|     annot = str(annot)
  301| 
  302|     # Annotation can be quoted.
  303|     if annot.startswith(("'", '"')) and annot.endswith(("'", '"')):
  304|         annot = annot[1:-1]
  305| 
  306|     return annot.startswith(_CLASSVAR_PREFIXES)
  307| 
  308| 
  309| def _has_own_attribute(cls, attrib_name):
  310|     """
  311|     Check whether *cls* defines *attrib_name* (and doesn't just inherit it).
  312|     """
  313|     return attrib_name in cls.__dict__
  314| 
  315| 
  316| def _collect_base_attrs(
  317|     cls, taken_attr_names
  318| ) -> tuple[list[Attribute], dict[str, type]]:
  319|     """
  320|     Collect attr.ibs from base classes of *cls*, except *taken_attr_names*.
  321|     """
  322|     base_attrs = []
  323|     base_attr_map = {}  # A dictionary of base attrs to their classes.
  324| 
  325|     # Traverse the MRO and collect attributes.
  326|     for base_cls in reversed(cls.__mro__[1:-1]):
  327|         for a in getattr(base_cls, "__attrs_attrs__", []):
  328|             if a.inherited or a.name in taken_attr_names:
  329|                 continue
  330| 
  331| 
... [300 more chars]
```

### 4. `search_code`(pattern="_get_annotations|_AnnotationExtractor|ForwardRef|PY_3_14")

Tool responded:

```
src/attr/_compat.py:15: PY_3_14_PLUS = sys.version_info[:2] >= (3, 14)
src/attr/_compat.py:18: if PY_3_14_PLUS:
src/attr/_compat.py:22: def _get_annotations(cls):
src/attr/_compat.py:31: def _get_annotations(cls):
src/attr/_compat.py:38: class _AnnotationExtractor:
src/attr/_make.py:26: _AnnotationExtractor,
src/attr/_make.py:27: _get_annotations,
src/attr/_make.py:396: anns = _get_annotations(cls)
src/attr/_make.py:925: class_annotations = _get_annotations(self._cls)
src/attr/_make.py:3155: ex = _AnnotationExtractor(converter)
src/attr/_make.py:3424: t = _AnnotationExtractor(converters[0]).get_first_param_type()
src/attr/_make.py:3433: rt = _AnnotationExtractor(last).get_return_type()
src/attr/converters.py:9: from ._compat import _AnnotationExtractor
src/attr/converters.py:50: xtr = _AnnotationExtractor(converter)
tests/conftest.py:9: from attr._compat import PY_3_10_PLUS, PY_3_14_PLUS
tests/conftest.py:37: if not PY_3_14_PLUS:
tests/test_converters.py:14: from attr._compat import _AnnotationExtractor
tests/test_converters.py:296: is _AnnotationExtractor(
tests/test_slots.py:18: from attr._compat import PY_3_14_PLUS, PYPY
tests/test_slots.py:789: PY_3_14_PLUS, reason="3.14 does not infer the type anymore."
```

### 5. `read_file`(path="src/attr/_compat.py", start=1, end=60)

Tool responded:

```
src/attr/_compat.py lines 1-60 of 103

    1| # SPDX-License-Identifier: MIT
    2| 
    3| import sys
    4| import threading
    5| 
    6| from collections.abc import Mapping, Sequence  # noqa: F401
    7| from typing import _GenericAlias
    8| 
    9| 
   10| PYPY = sys.implementation.name == "pypy"
   11| PY_3_10_PLUS = sys.version_info[:2] >= (3, 10)
   12| PY_3_11_PLUS = sys.version_info[:2] >= (3, 11)
   13| PY_3_12_PLUS = sys.version_info[:2] >= (3, 12)
   14| PY_3_13_PLUS = sys.version_info[:2] >= (3, 13)
   15| PY_3_14_PLUS = sys.version_info[:2] >= (3, 14)
   16| 
   17| 
   18| if PY_3_14_PLUS:
   19|     # We request forward-ref annotations to not break in the presence of
   20|     # forward references.
   21| 
   22|     def _get_annotations(cls):
   23|         import annotationlib
   24| 
   25|         return annotationlib.get_annotations(
   26|             cls, format=annotationlib.Format.FORWARDREF
   27|         )
   28| 
   29| else:
   30| 
   31|     def _get_annotations(cls):
   32|         """
   33|         Get annotations for *cls*.
   34|         """
   35|         return cls.__dict__.get("__annotations__", {})
   36| 
   37| 
   38| class _AnnotationExtractor:
   39|     """
   40|     Extract type annotations from a callable, returning None whenever there
   41|     is none.
   42|     """
   43| 
   44|     __slots__ = ["sig"]
   45| 
   46|     def __init__(self, callable):
   47|         import inspect
   48| 
   49|         try:
   50|             self.sig = inspect.signature(callable)
   51|         except (ValueError, TypeError):  # inspect failed
   52|             self.sig = None
   53| 
   54|     def get_first_param_type(self):
   55|         """
   56|         Return the type annotation of the first argument if it's not empty.
   57|         """
   58|         import inspect
   59| 
   60|         if not self.sig:
```

### 6. `read_file`(path="src/attr/_make.py", start=370, end=470)

Tool responded:

```
src/attr/_make.py lines 370-470 of 3439

  370|             taken_attr_names.add(a.name)
  371|             base_attrs.append(a)
  372|             base_attr_map[a.name] = base_cls
  373| 
  374|     return base_attrs, base_attr_map
  375| 
  376| 
  377| def _transform_attrs(
  378|     cls,
  379|     these,
  380|     auto_attribs,
  381|     kw_only,
  382|     collect_by_mro,
  383|     field_transformer,
  384| ) -> _Attributes:
  385|     """
  386|     Transform all `_CountingAttr`s on a class into `Attribute`s.
  387| 
  388|     If *these* is passed, use that and don't look for them on the class.
  389| 
  390|     If *collect_by_mro* is True, collect them in the correct MRO order,
  391|     otherwise use the old -- incorrect -- order.  See #428.
  392| 
  393|     Return an `_Attributes`.
  394|     """
  395|     cd = cls.__dict__
  396|     anns = _get_annotations(cls)
  397| 
  398|     if these is not None:
  399|         ca_list = list(these.items())
  400|     elif auto_attribs is True:
  401|         ca_names = {
  402|             name
  403|             for name, attr in cd.items()
  404|             if attr.__class__ is _CountingAttr
  405|         }
  406|         ca_list = []
  407|         annot_names = set()
  408|         for attr_name, type in anns.items():
  409|             if _is_class_var(type):
  410|                 continue
  411|             annot_names.add(attr_name)
  412|             a = cd.get(attr_name, NOTHING)
  413| 
  414|             if a.__class__ is not _CountingAttr:
  415|                 a = attrib(a)
  416|             ca_list.append((attr_name, a))
  417| 
  418|         unannotated = ca_names - annot_names
  419|         if unannotated:
  420|             raise UnannotatedAttributeError(
  421|                 "The following `attr.ib`s lack a type annotation: "
  422|                 + ", ".join(
  423|                     sorted(unannotated, key=lambda n: cd.get(n).counter)
  424|                 )
  425|                 + "."
  426|             )
  427|     else:
  428|         ca_list = sorted(
  429|             (
  430|                 (name, attr)
  431|                 for name, attr in cd.items()
  43
... [300 more chars]
```

### 7. `run_test`(test_source="import typing\nimport attr\n\n\ndef test_forward_ref_classvar_excluded_from_fields():\n    class C:\n        )

Tool responded:

```
FAILED (exit 1)

F                                                                        [100%]
=================================== FAILURES ===================================
________________ test_forward_ref_classvar_excluded_from_fields ________________

    def test_forward_ref_classvar_excluded_from_fields():
        class C:
            pass
    
        # Simulate what Python 3.14's `annotationlib.get_annotations(...,
        # format=FORWARDREF)` produces when a ClassVar annotation cannot be
        # resolved eagerly: a `typing.ForwardRef` wrapping the original
        # annotation string, instead of the resolved `typing.ClassVar[str]`
        # object or a plain string.
        C.__annotations__ = {
            "cls_var": typing.ForwardRef("ClassVar[str]"),
            "value": int,
        }
        C.value = 1
    
        C = attr.s(auto_attribs=True)(C)
    
        fields = attr.fields_dict(C)
    
>       assert "cls_var" not in fields
E       AssertionError: assert 'cls_var' not in {'cls_var': Attribute(name='cls_var', default=NOTHING, validator=None, repr=True, eq=True, eq_key=None, order=True, or...=mappingproxy({}), type=<class 'int'>, converter=None, kw_only=False, inherited=False, on_setattr=None, alias='value')}

tests/test_regressgen_candidate.py:24: AssertionError
=========================== short test summary info ============================
FAILED tests/test_regressgen_candidate.py::test_forward_ref_classvar_excluded_from_fields
1 failed in 0.02s
```

### 8. `run_test`(test_source="import typing\nimport attr\nfrom attr._make import _is_class_var\n\n\ndef test_is_class_var_recognizes_forwar)

Tool responded:

```
FAILED (exit 1)

FF                                                                       [100%]
=================================== FAILURES ===================================
___________________ test_is_class_var_recognizes_forward_ref ___________________

    def test_is_class_var_recognizes_forward_ref():
        """
        `_is_class_var` should recognize a `typing.ForwardRef` wrapping a
        ClassVar annotation string, just like it recognizes the resolved
        `typing.ClassVar` object or a plain string annotation.
        """
>       assert _is_class_var(typing.ForwardRef("ClassVar[str]")) is True
E       AssertionError: assert False is True
E        +  where False = _is_class_var(ForwardRef('ClassVar[str]'))
E        +    where ForwardRef('ClassVar[str]') = <class 'typing.ForwardRef'>('ClassVar[str]')
E        +      where <class 'typing.ForwardRef'> = typing.ForwardRef

tests/test_regressgen_candidate.py:12: AssertionError
________________ test_forward_ref_classvar_excluded_from_fields ________________

    def test_forward_ref_classvar_excluded_from_fields():
        class C:
            pass
    
        # Simulate what Python 3.14's `annotationlib.get_annotations(...,
        # format=FORWARDREF)` produces when a ClassVar annotation cannot be
        # resolved eagerly: a `typing.ForwardRef` wrapping the original
        # annotation string, instead of the resolved `typing.ClassVar[str]`
        # object or a plain string.
        C.__annotations__ = {
            "cls_var": typing.ForwardRef("ClassVar[str]"),
            "value": int,
        }
        C.value = 1
    
        C = attr.s(auto_attribs=True)(C)
    
        fields = attr.fields_dict(C)
    
>       assert "cls_var" not in fields
E       AssertionError: assert 'cls_var' not in {'cls_var': Attribute(name='cls_var', default=NOTHING, validator=None, repr=True, eq=True, eq_key=None, order=True, or...=mappingproxy({}), type=<class 'int'>, converter=None, kw_only=False, inherited=False, on_setattr=None, alias='value')}

tests/test_regressgen_candidate.py:34: AssertionError
=========================== short test summary info ============================
FAILED tests/test_regressgen_can
... [160 more chars]
```

### 9. `submit_test`(rationale="The bug is in attr._make._is_class_var, which detects ClassVar-annotated attributes by stringifying the annot)

Tool responded:

```
Submitted.

import typing

import attr
from attr._make import _is_class_var


def test_is_class_var_recognizes_forward_ref():
    """
    `_is_class_var` should recognize a `typing.ForwardRef` wrapping a
    ClassVar annotation string, just like it already recognizes the
    resolved `typing.ClassVar` object or a plain/quoted string annotation.

    On Python 3.14+, `annotationlib.get_annotations(cls,
    format=Format.FORWARDREF)` returns a `typing.ForwardRef` instead of a
    resolved type whenever the annotation can't be eagerly evaluated (e.g.
    it references names not yet defined). `_is_class_var` must unwrap that
    ForwardRef to inspect the underlying annotation string rather than just
    stringifying the ForwardRef object itself (which produces something like
    "ForwardRef('ClassVar[str]')" and therefore never matches the expected
    ClassVar prefixes).
    """
    assert _is_class_var(typing.ForwardRef("ClassVar[str]")) is True


def test_forward_ref_classvar_excluded_from_fields():
    """
    Regression test for: on Python 3.14, `attr.s(auto_attribs=True)` no
    longer strips out `ClassVar` attributes if the annotation ends up being
    a forward reference. Instead of being skipped, it was treated as a
    normal attribute, which then leaked into `attr.fields_dict()` and messed
    with `__init__` generation.

    We simulate the Python 3.14 `annotationlib` behavior directly by
    injecting a `typing.ForwardRef` into `__annotations__` (this is exactly
    what `annotationlib.get_annotations(cls, format=Format.FORWARDREF)`
    would produce for an unresolved ClassVar annotation), so the regression
    is exercised independent of the Python version running the test suite.
    """

    class C:
        pass

    C.__annotations__ = {
        "cls_var": typing.ForwardRef("ClassVar[str]"),
        "value": int,
    }
    C.value = 1

    C = attr.s(auto_attribs=True)(C)

    fields = attr.fields_dict(C)

    # The ClassVar-annotated attribute must be skipped entirely, just like
    # it is skipped when the annotation is the resolved `typing.ClassVar`
    # object or a plain string on older Python versions.
    assert "cls_var" not in fields
    # 
... [126 more chars]
```

## 4. Submitted test

```python
import typing

import attr
from attr._make import _is_class_var


def test_is_class_var_recognizes_forward_ref():
    """
    `_is_class_var` should recognize a `typing.ForwardRef` wrapping a
    ClassVar annotation string, just like it already recognizes the
    resolved `typing.ClassVar` object or a plain/quoted string annotation.

    On Python 3.14+, `annotationlib.get_annotations(cls,
    format=Format.FORWARDREF)` returns a `typing.ForwardRef` instead of a
    resolved type whenever the annotation can't be eagerly evaluated (e.g.
    it references names not yet defined). `_is_class_var` must unwrap that
    ForwardRef to inspect the underlying annotation string rather than just
    stringifying the ForwardRef object itself (which produces something like
    "ForwardRef('ClassVar[str]')" and therefore never matches the expected
    ClassVar prefixes).
    """
    assert _is_class_var(typing.ForwardRef("ClassVar[str]")) is True


def test_forward_ref_classvar_excluded_from_fields():
    """
    Regression test for: on Python 3.14, `attr.s(auto_attribs=True)` no
    longer strips out `ClassVar` attributes if the annotation ends up being
    a forward reference. Instead of being skipped, it was treated as a
    normal attribute, which then leaked into `attr.fields_dict()` and messed
    with `__init__` generation.

    We simulate the Python 3.14 `annotationlib` behavior directly by
    injecting a `typing.ForwardRef` into `__annotations__` (this is exactly
    what `annotationlib.get_annotations(cls, format=Format.FORWARDREF)`
    would produce for an unresolved ClassVar annotation), so the regression
    is exercised independent of the Python version running the test suite.
    """

    class C:
        pass

    C.__annotations__ = {
        "cls_var": typing.ForwardRef("ClassVar[str]"),
        "value": int,
    }
    C.value = 1

    C = attr.s(auto_attribs=True)(C)

    fields = attr.fields_dict(C)

    # The ClassVar-annotated attribute must be skipped entirely, just like
    # it is skipped when the annotation is the resolved `typing.ClassVar`
    # object or a plain string on older Python versions.
    assert "cls_var" not in fields
    # The regular 
... [114 more chars]
```

**Agent's stated rationale:**

> The bug is in attr._make._is_class_var, which detects ClassVar-annotated attributes by stringifying the annotation and checking known prefixes ("typing.ClassVar", "ClassVar", etc.). On Python 3.14, annotations are fetched via annotationlib.get_annotations(cls, format=Format.FORWARDREF) (see attr._compat._get_annotations), which returns a typing.ForwardRef object instead of a resolved type whenever the annotation can't be eagerly evaluated. str(ForwardRef("ClassVar[str]")) renders as "ForwardRef('ClassVar[str]')", which does not start with any of the recognized ClassVar prefixes, so _is_class_var wrongly returns False and the ClassVar attribute leaks into the class's attrs fields instead of being skipped.

The test file has two parts:
1. A direct unit test of _is_class_var with a typing.ForwardRef wrapping a ClassVar annotation string, asserting it should be recognized as a ClassVar (True) per the bug report's expected behavior.
2. An integration-level test that reproduces the full user-facing symptom by injecting a typing.ForwardRef into a class's __annotations__ (exactly what annotationlib would produce in the reported scenario on Python 3.14) and then applying attr.s(auto_attribs=True), asserting that the ClassVar-annotated name is excluded from attr.fields_dict() while the normal attribute is still present and correctly initialized.

Both tests were verified to fail against the current buggy code with clear, on-topic assertion failures (not import/attribute errors), and they assert the behavior explicitly described as correct in the bug report (ClassVar attributes should not appear in fields_dict at all), so they will pass once _is_class_var is fixed to unwrap ForwardRef annotations before the prefix check.

## 5. Two-sided gate

### Against `buggy/` — exit 1 (must be non-zero)

```
nnotations(cls,
        format=Format.FORWARDREF)` returns a `typing.ForwardRef` instead of a
        resolved type whenever the annotation can't be eagerly evaluated (e.g.
        it references names not yet defined). `_is_class_var` must unwrap that
        ForwardRef to inspect the underlying annotation string rather than just
        stringifying the ForwardRef object itself (which produces something like
        "ForwardRef('ClassVar[str]')" and therefore never matches the expected
        ClassVar prefixes).
        """
>       assert _is_class_var(typing.ForwardRef("ClassVar[str]")) is True
E       AssertionError: assert False is True
E        +  where False = _is_class_var(ForwardRef('ClassVar[str]'))
E        +    where ForwardRef('ClassVar[str]') = <class 'typing.ForwardRef'>('ClassVar[str]')
E        +      where <class 'typing.ForwardRef'> = typing.ForwardRef

tests/test_regressgen_candidate.py:22: AssertionError
________________ test_forward_ref_classvar_excluded_from_fields ________________

    def test_forward_ref_classvar_excluded_from_fields():
        """
        Regression test for: on Python 3.14, `attr.s(auto_attribs=True)` no
        longer strips out `ClassVar` attributes if the annotation ends up being
        a forward reference. Instead of being skipped, it was treated as a
        normal attribute, which then leaked into `attr.fields_dict()` and messed
        with `__init__` generation.
    
        We simulate the Python 3.14 `annotationlib` behavior directly by
        injecting a `typing.ForwardRef` into `__annotations__` (this is exactly
        what `annotationlib.get_annotations(cls, format=Format.FORWARDREF)`
        would produce for an unresolved ClassVar annotation), so the regression
        is exercised independent of the Python version running the test suite.
        """
    
        class C:
            pass
    
        C.__annotations__ = {
            "cls_var": typing.ForwardRef("ClassVar[str]"),
            "value": int,
        }
        C.value = 1
    
        C = attr.s(auto_attribs=True)(C)
    
        fields = attr.fields_dict(C)
    
        # The ClassVar-annotated attribute must be skipped entirely, just 
... [800 more chars]
```

### Against `fixed/` — exit 0 (must be zero)

```
..                                                                       [100%]
2 passed in 0.01s
```

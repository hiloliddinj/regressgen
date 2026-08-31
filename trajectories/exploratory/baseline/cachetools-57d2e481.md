# Trajectory — `baseline` on `cachetools-57d2e481`

**Verdict: VACUOUS**

- cost `$0.01171` · wall `9.5s` · tool calls `0`

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
Using `unittest.mock.create_autospec` on a class that has a `cachedmethod`-decorated method blows up with an AttributeError instead of just producing a mock.

Repro:

```python
import unittest.mock
from cachetools import cachedmethod, LRUCache

class Cached:
    def __init__(self):
        self.cache = LRUCache(maxsize=10)

    @cachedmethod(lambda self: self.cache)
    def get(self, key):
        return key

unittest.mock.create_autospec(Cached, instance=True)
```

This raises an AttributeError coming from deep inside the descriptor logic while `unittest.mock` is introspecting the class attributes (it appears mock passes an instance of `None` when checking things like `iscoroutinefunction` on class-level attributes). Any class with a cached method fails autospeccing this way, which makes it awkward to write mocks/tests for classes that use `cachedmethod`.

Expected: `create_autospec` should work normally (or at least not throw) on classes using `cachedmethod`, same as it does for plain methods.
```

## 3. Tool calls

_No tools — this system answers in a single prompt._

## 4. Submitted test

```python
"""Regression test for AttributeError when using create_autospec on a
class that has a @cachedmethod-decorated method.

See bug report: create_autospec(Cached, instance=True) raises
AttributeError because unittest.mock accesses the descriptor with
obj=None (i.e. via the class, not an instance) when introspecting
class attributes, and the descriptor's __get__ blows up trying to
build a Wrapper around None.
"""
import unittest.mock

import pytest

from cachetools import LRUCache, cachedmethod


class Cached:
    def __init__(self):
        self.cache = LRUCache(maxsize=10)

    @cachedmethod(lambda self: self.cache)
    def get(self, key):
        return key


def test_create_autospec_does_not_raise():
    # Should not raise AttributeError (or any other exception).
    mock_instance = unittest.mock.create_autospec(Cached, instance=True)
    assert mock_instance is not None


def test_create_autospec_get_is_callable_mock():
    mock_instance = unittest.mock.create_autospec(Cached, instance=True)
    # The mocked 'get' method should behave like a normal mock method.
    mock_instance.get("foo")
    mock_instance.get.assert_called_once_with("foo")


def test_descriptor_get_on_class_does_not_raise():
    # Directly mimic what unittest.mock does: access the descriptor
    # via the class (obj=None) rather than through an instance.
    descriptor = Cached.__dict__["get"]
    # Should not raise AttributeError when obj is None.
    result = descriptor.__get__(None, Cached)
    assert result is not None
```

## 5. Two-sided gate

### Against `buggy/` — exit 0 (must be non-zero)

```
...                                                                      [100%]
=============================== warnings summary ===============================
tests/test_regressgen_candidate.py::test_create_autospec_does_not_raise
tests/test_regressgen_candidate.py::test_create_autospec_get_is_callable_mock
  ~/.local/share/uv/python/cpython-3.12.13-macos-aarch64-none/lib/python3.12/unittest/mock.py:529: DeprecationWarning: No '__dict__' attribute on 'NoneType' instance to cache 'get' property.
    if iscoroutinefunction(getattr(spec, attr, None)):

tests/test_regressgen_candidate.py::test_create_autospec_does_not_raise
tests/test_regressgen_candidate.py::test_create_autospec_get_is_callable_mock
  ~/.local/share/uv/python/cpython-3.12.13-macos-aarch64-none/lib/python3.12/unittest/mock.py:2810: DeprecationWarning: No '__dict__' attribute on 'NoneType' instance to cache 'get' property.
    original = getattr(spec, entry)

tests/test_regressgen_candidate.py::test_descriptor_get_on_class_does_not_raise
  <sandbox>:44: DeprecationWarning: No '__dict__' attribute on 'NoneType' instance to cache 'get' property.
    result = descriptor.__get__(None, Cached)

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
3 passed, 5 warnings in 0.42s
```

### Against `fixed/` — exit 0 (must be zero)

```
...                                                                      [100%]
3 passed in 0.40s
```

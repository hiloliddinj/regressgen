# Trajectory — `v6-critic` on `cachetools-57d2e481`

**Verdict: REPRO**  (fails on buggy, passes on fixed — reproduces the bug)

- cost `$0.55323` · wall `138.3s` · tool calls `17`

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

You cannot see the fixed code, so you cannot directly check the second half of
the gate. `try_fix` is how you approximate it: form a hypothesis about the
minimal source change that would fix the bug, apply it in a sc
... [732 more chars]
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

### 1. `search_code`(pattern="def cachedmethod")

Tool responded:

```
src/cachetools/__init__.py:750: def cachedmethod(cache, key=keys.methodkey, lock=None, condition=None, info=False):
```

### 2. `read_file`(path="src/cachetools/__init__.py", start=700, end=830)

Tool responded:

```
src/cachetools/__init__.py lines 700-772 of 772

  700|             else:
  701|                 return (key, self.pop(key))
  702| 
  703|     def clear(self):
  704|         _TimedCache.clear(self)
  705|         self.__items.clear()
  706|         del self.__order[:]
  707| 
  708|     def __getitem(self, key):
  709|         value = self.__items[key]
  710|         self.__items.move_to_end(key)
  711|         return value
  712| 
  713| 
  714| _CacheInfo = collections.namedtuple(
  715|     "CacheInfo", ["hits", "misses", "maxsize", "currsize"]
  716| )
  717| 
  718| 
  719| def cached(cache, key=keys.hashkey, lock=None, condition=None, info=False):
  720|     """Decorator to wrap a function with a memoizing callable that saves
  721|     results in a cache.
  722| 
  723|     """
  724|     from ._cached import _wrapper
  725| 
  726|     def decorator(func):
  727|         if info:
  728|             if isinstance(cache, Cache):
  729| 
  730|                 def make_info(hits, misses):
  731|                     return _CacheInfo(hits, misses, cache.maxsize, cache.currsize)
  732| 
  733|             elif isinstance(cache, collections.abc.Mapping):
  734| 
  735|                 def make_info(hits, misses):
  736|                     return _CacheInfo(hits, misses, None, len(cache))
  737| 
  738|             else:
  739| 
  740|                 def make_info(hits, misses):
  741|                     return _CacheInfo(hits, misses, 0, 0)
  742| 
  743|             return _wrapper(func, cache, key, lock, condition, info=make_info)
  744|         else:
  745|             return _wrapper(func, cache, key, lock, condition)
  746| 
  747|     return decorator
  748| 
  749| 
  750| def cachedmethod(cache, key=keys.methodkey, lock=None, condition=None, info=False):
  751|     """Decorator to wrap a class or instance method with a memoizing
  752|     callable that saves results in a cache.
  753| 
  754|     """
  755|     from ._cachedmethod import _wrapper
  756| 
  757|     def decorator(method):
  758|         if info:
  759| 
  760|             def make_info(cache, hits, misses):
  761|                 if isinstance(cache, Cache):
  762|                
... [300 more chars]
```

### 3. `read_file`(path="src/cachetools/_cachedmethod.py", start=0, end=400)

Tool responded:

```
src/cachetools/_cachedmethod.py lines 1-400 of 410

    1| """Method decorator helpers."""
    2| 
    3| __all__ = ()
    4| 
    5| import functools
    6| import warnings
    7| import weakref
    8| 
    9| 
   10| def _warn_classmethod(stacklevel):
   11|     warnings.warn(
   12|         "decorating class methods with @cachedmethod is deprecated",
   13|         DeprecationWarning,
   14|         stacklevel=stacklevel,
   15|     )
   16| 
   17| 
   18| def _warn_instance_dict(msg, stacklevel):
   19|     warnings.warn(
   20|         msg,
   21|         DeprecationWarning,
   22|         stacklevel=stacklevel,
   23|     )
   24| 
   25| 
   26| class _WrapperBase:
   27|     """Wrapper base class providing default implementations for properties."""
   28| 
   29|     def __init__(self, obj, method, cache, key, lock=None, cond=None):
   30|         if isinstance(obj, type):
   31|             _warn_classmethod(stacklevel=5)
   32|         functools.update_wrapper(self, method)
   33|         self._obj = obj  # protected
   34|         self.__cache = cache
   35|         self.__key = key
   36|         self.__lock = lock
   37|         self.__cond = cond
   38| 
   39|     def __call__(self, *args, **kwargs):
   40|         raise NotImplementedError()  # pragma: no cover
   41| 
   42|     def cache_clear(self):
   43|         raise NotImplementedError()  # pragma: no cover
   44| 
   45|     @property
   46|     def cache(self):
   47|         return self.__cache(self._obj)
   48| 
   49|     @property
   50|     def cache_key(self):
   51|         return self.__key
   52| 
   53|     @property
   54|     def cache_lock(self):
   55|         return None if self.__lock is None else self.__lock(self._obj)
   56| 
   57|     @property
   58|     def cache_condition(self):
   59|         return None if self.__cond is None else self.__cond(self._obj)
   60| 
   61| 
   62| class _DescriptorBase:
   63|     """Descriptor base class implementing the basic descriptor protocol."""
   64| 
   65|     def __init__(self, deprecated=False):
   66|         self.__attrname = None
   67|         self.__deprecated = deprecated
   68| 
   69|     def __set_name__(self, ow
... [300 more chars]
```

### 4. `run_test`(test_source="\nimport unittest.mock\nfrom cachetools import cachedmethod, LRUCache\n\n\ndef test_autospec_on_cachedmethod_)

Tool responded:

```
PASSED (exit 0) — this test does NOT reproduce the bug

.                                                                        [100%]
=============================== warnings summary ===============================
tests/test_regressgen_candidate.py::test_autospec_on_cachedmethod_class
  ~/.local/share/uv/python/cpython-3.12.13-macos-aarch64-none/lib/python3.12/unittest/mock.py:529: DeprecationWarning: No '__dict__' attribute on 'NoneType' instance to cache 'get' property.
    if iscoroutinefunction(getattr(spec, attr, None)):

tests/test_regressgen_candidate.py::test_autospec_on_cachedmethod_class
  ~/.local/share/uv/python/cpython-3.12.13-macos-aarch64-none/lib/python3.12/unittest/mock.py:2810: DeprecationWarning: No '__dict__' attribute on 'NoneType' instance to cache 'get' property.
    original = getattr(spec, entry)

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
1 passed, 2 warnings in 0.08s
```

### 5. `run_test`(test_source="\nimport unittest.mock\nfrom cachetools import cachedmethod, LRUCache\n\n\ndef test_autospec_on_cachedmethod_)

Tool responded:

```
FAILED (exit 1)

F                                                                        [100%]
=================================== FAILURES ===================================
___________________ test_autospec_on_cachedmethod_info_class ___________________

    def test_autospec_on_cachedmethod_info_class():
        class Cached:
            def __init__(self):
                self.cache = LRUCache(maxsize=10)
    
            @cachedmethod(lambda self: self.cache, info=True)
            def get(self, key):
                return key
    
        # Should not raise
>       mock_obj = unittest.mock.create_autospec(Cached, instance=True)
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_regressgen_candidate.py:16: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
~/.local/share/uv/python/cpython-3.12.13-macos-aarch64-none/lib/python3.12/unittest/mock.py:2773: in create_autospec
    mock = Klass(parent=_parent, _new_parent=_parent, _new_name=_new_name,
~/.local/share/uv/python/cpython-3.12.13-macos-aarch64-none/lib/python3.12/unittest/mock.py:2139: in __init__
    _safe_super(MagicMixin, self).__init__(*args, **kw)
~/.local/share/uv/python/cpython-3.12.13-macos-aarch64-none/lib/python3.12/unittest/mock.py:460: in __init__
    self._mock_add_spec(spec, spec_set, _spec_as_instance, _eat_self)
~/.local/share/uv/python/cpython-3.12.13-macos-aarch64-none/lib/python3.12/unittest/mock.py:529: in _mock_add_spec
    if iscoroutinefunction(getattr(spec, attr, None)):
                           ^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <cachetools._cachedmethod._unlocked_info.<locals>.Descriptor object at 0x10b5bea80>
obj = None
objtype = <class 'tests.test_regressgen_candidate.test_autospec_on_cachedmethod_info_class.<locals>.Cached'>

    def __get__(self, obj, objtype=None):
        wrapper = self.Wrapper(obj)
        if self.__attrname is not None:
            # replace descriptor instance with wrapper in instance dict
            try:
                # In case of a race condition where another thread already replaced
               
... [300 more chars]
```

### 6. `search_code`(pattern="create_autospec|__get__|obj is None")

Tool responded:

```
src/cachetools/_cachedmethod.py:78: def __get__(self, obj, objtype=None):
```

### 7. `try_fix`(path="src/cachetools/_cachedmethod.py", find="    def __get__(self, obj, objtype=None):\n        wrapper = self.Wrapper(obj)")

Tool responded:

```
your test PASSES with this fix
existing suite still green

.                                                                        [100%]
1 passed in 0.08s
```

### 8. `run_test`(test_source="\nimport unittest.mock\n\nimport pytest\n\nfrom cachetools import cachedmethod, LRUCache\n\n\ndef test_create)

Tool responded:

```
FAILED (exit 1)

F                                                                        [100%]
=================================== FAILURES ===================================
__________ test_create_autospec_on_cachedmethod_class_does_not_raise ___________

    def test_create_autospec_on_cachedmethod_class_does_not_raise():
        """Regression test: unittest.mock.create_autospec() must work on classes
        that use @cachedmethod, instead of blowing up while mock introspects
        class-level attributes (see GH bug report).
        """
    
        class Cached:
            def __init__(self):
                self.cache = LRUCache(maxsize=10)
    
            @cachedmethod(lambda self: self.cache, info=True)
            def get(self, key):
                return key
    
        # This must succeed and simply produce a mock, not raise.
>       mock_obj = unittest.mock.create_autospec(Cached, instance=True)
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_regressgen_candidate.py:24: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
~/.local/share/uv/python/cpython-3.12.13-macos-aarch64-none/lib/python3.12/unittest/mock.py:2773: in create_autospec
    mock = Klass(parent=_parent, _new_parent=_parent, _new_name=_new_name,
~/.local/share/uv/python/cpython-3.12.13-macos-aarch64-none/lib/python3.12/unittest/mock.py:2139: in __init__
    _safe_super(MagicMixin, self).__init__(*args, **kw)
~/.local/share/uv/python/cpython-3.12.13-macos-aarch64-none/lib/python3.12/unittest/mock.py:460: in __init__
    self._mock_add_spec(spec, spec_set, _spec_as_instance, _eat_self)
~/.local/share/uv/python/cpython-3.12.13-macos-aarch64-none/lib/python3.12/unittest/mock.py:529: in _mock_add_spec
    if iscoroutinefunction(getattr(spec, attr, None)):
                           ^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <cachetools._cachedmethod._unlocked_info.<locals>.Descriptor object at 0x10ac12720>
obj = None
objtype = <class 'tests.test_regressgen_candidate.test_create_autospec_on_cachedmethod_class_does_not_raise.<locals>.Cached'>

    de
... [300 more chars]
```

### 9. `try_fix`(path="src/cachetools/_cachedmethod.py", find="    def __get__(self, obj, objtype=None):\n        wrapper = self.Wrapper(obj)")

Tool responded:

```
your test STILL FAILS with this fix
existing suite still green

F                                                                        [100%]
=================================== FAILURES ===================================
__________ test_create_autospec_on_cachedmethod_class_does_not_raise ___________

    def test_create_autospec_on_cachedmethod_class_does_not_raise():
        """Regression test: unittest.mock.create_autospec() must work on classes
        that use @cachedmethod, instead of blowing up while mock introspects
        class-level attributes (see GH bug report).
        """
    
        class Cached:
            def __init__(self):
                self.cache = LRUCache(maxsize=10)
    
            @cachedmethod(lambda self: self.cache, info=True)
            def get(self, key):
                return key
    
        # This must succeed and simply produce a mock, not raise.
        mock_obj = unittest.mock.create_autospec(Cached, instance=True)
        assert mock_obj is not None
    
        # The autospecced mock should behave like a normal callable method.
>       mock_obj.get("k")
E       TypeError: 'NonCallableMagicMock' object is not callable

tests/test_regressgen_candidate.py:28: TypeError
=========================== short test summary info ============================
FAILED tests/test_regressgen_candidate.py::test_create_autospec_on_cachedmethod_class_does_not_raise
1 failed in 0.09s
```

### 10. `try_fix`(path="src/cachetools/_cachedmethod.py", find="    def __get__(self, obj, objtype=None):\n        wrapper = self.Wrapper(obj)")

Tool responded:

```
your test PASSES with this fix
existing suite still green

.                                                                        [100%]
1 passed in 0.08s
```

### 11. `submit_test`(rationale="The bug report states that unittest.mock.create_autospec() raises an AttributeError (from descriptor logic be)

Tool responded:

```
Submitted.

import unittest.mock

from cachetools import cachedmethod, LRUCache


def test_create_autospec_on_cachedmethod_class_does_not_raise():
    """Regression test for: using unittest.mock.create_autospec() on a class
    that has a @cachedmethod-decorated method blows up instead of just
    producing a mock.

    unittest.mock introspects class-level attributes (e.g. via
    getattr(spec, attr, None) to check iscoroutinefunction), which triggers
    the descriptor's __get__ with obj=None (class-level access, not through
    an instance). The descriptor must handle this gracefully instead of
    raising, exactly as it does for plain methods.
    """

    class Cached:
        def __init__(self):
            self.cache = LRUCache(maxsize=10)

        @cachedmethod(lambda self: self.cache, info=True)
        def get(self, key):
            return key

    # This must succeed and simply produce a mock, not raise an
    # AttributeError/TypeError from inside the cachedmethod descriptor logic.
    mock_obj = unittest.mock.create_autospec(Cached, instance=True)
    assert mock_obj is not None
```

### 12. `critic`()

Tool responded:

```
VERDICT: APPROVE

The test faithfully reproduces the bug report's scenario (a class with a `cachedmethod`-decorated method passed to `unittest.mock.create_autospec(..., instance=True)`) and asserts only that this doesn't raise and produces a mock — which matches the bug report's stated expectation ("create_autospec should work normally (or at least not throw)"). Tracing `_DescriptorBase.__get__` in `src/cachetools/_cachedmethod.py`, the failure path when `obj=None` (class-level access) is common to all decorator variants (plain, locked, condition, info), so a fix addressing this shared `__get__` logic (e.g., short-circuiting when `obj is None`) would equally cover the `info=True` variant used in the test. The added `info=True` kwarg doesn't introduce an incidental dependency that a reasonable fix would break, since it routes through the same base descriptor class. The decorator signature and imports used are correct, so there's no mechanical issue either.
```

### 13. `search_code`(pattern="class cachedmethod")

Tool responded:

```
(no matches)
```

### 14. `search_code`(pattern="def cachedmethod")

Tool responded:

```
src/cachetools/__init__.py:750: def cachedmethod(cache, key=keys.methodkey, lock=None, condition=None, info=False):
```

### 15. `read_file`(path="src/cachetools/__init__.py", start=700, end=800)

Tool responded:

```
src/cachetools/__init__.py lines 700-772 of 772

  700|             else:
  701|                 return (key, self.pop(key))
  702| 
  703|     def clear(self):
  704|         _TimedCache.clear(self)
  705|         self.__items.clear()
  706|         del self.__order[:]
  707| 
  708|     def __getitem(self, key):
  709|         value = self.__items[key]
  710|         self.__items.move_to_end(key)
  711|         return value
  712| 
  713| 
  714| _CacheInfo = collections.namedtuple(
  715|     "CacheInfo", ["hits", "misses", "maxsize", "currsize"]
  716| )
  717| 
  718| 
  719| def cached(cache, key=keys.hashkey, lock=None, condition=None, info=False):
  720|     """Decorator to wrap a function with a memoizing callable that saves
  721|     results in a cache.
  722| 
  723|     """
  724|     from ._cached import _wrapper
  725| 
  726|     def decorator(func):
  727|         if info:
  728|             if isinstance(cache, Cache):
  729| 
  730|                 def make_info(hits, misses):
  731|                     return _CacheInfo(hits, misses, cache.maxsize, cache.currsize)
  732| 
  733|             elif isinstance(cache, collections.abc.Mapping):
  734| 
  735|                 def make_info(hits, misses):
  736|                     return _CacheInfo(hits, misses, None, len(cache))
  737| 
  738|             else:
  739| 
  740|                 def make_info(hits, misses):
  741|                     return _CacheInfo(hits, misses, 0, 0)
  742| 
  743|             return _wrapper(func, cache, key, lock, condition, info=make_info)
  744|         else:
  745|             return _wrapper(func, cache, key, lock, condition)
  746| 
  747|     return decorator
  748| 
  749| 
  750| def cachedmethod(cache, key=keys.methodkey, lock=None, condition=None, info=False):
  751|     """Decorator to wrap a class or instance method with a memoizing
  752|     callable that saves results in a cache.
  753| 
  754|     """
  755|     from ._cachedmethod import _wrapper
  756| 
  757|     def decorator(method):
  758|         if info:
  759| 
  760|             def make_info(cache, hits, misses):
  761|                 if isinstance(cache, Cache):
  762|                
... [300 more chars]
```

### 16. `read_file`(path="src/cachetools/_cachedmethod.py", start=0, end=400)

Tool responded:

```
src/cachetools/_cachedmethod.py lines 1-400 of 410

    1| """Method decorator helpers."""
    2| 
    3| __all__ = ()
    4| 
    5| import functools
    6| import warnings
    7| import weakref
    8| 
    9| 
   10| def _warn_classmethod(stacklevel):
   11|     warnings.warn(
   12|         "decorating class methods with @cachedmethod is deprecated",
   13|         DeprecationWarning,
   14|         stacklevel=stacklevel,
   15|     )
   16| 
   17| 
   18| def _warn_instance_dict(msg, stacklevel):
   19|     warnings.warn(
   20|         msg,
   21|         DeprecationWarning,
   22|         stacklevel=stacklevel,
   23|     )
   24| 
   25| 
   26| class _WrapperBase:
   27|     """Wrapper base class providing default implementations for properties."""
   28| 
   29|     def __init__(self, obj, method, cache, key, lock=None, cond=None):
   30|         if isinstance(obj, type):
   31|             _warn_classmethod(stacklevel=5)
   32|         functools.update_wrapper(self, method)
   33|         self._obj = obj  # protected
   34|         self.__cache = cache
   35|         self.__key = key
   36|         self.__lock = lock
   37|         self.__cond = cond
   38| 
   39|     def __call__(self, *args, **kwargs):
   40|         raise NotImplementedError()  # pragma: no cover
   41| 
   42|     def cache_clear(self):
   43|         raise NotImplementedError()  # pragma: no cover
   44| 
   45|     @property
   46|     def cache(self):
   47|         return self.__cache(self._obj)
   48| 
   49|     @property
   50|     def cache_key(self):
   51|         return self.__key
   52| 
   53|     @property
   54|     def cache_lock(self):
   55|         return None if self.__lock is None else self.__lock(self._obj)
   56| 
   57|     @property
   58|     def cache_condition(self):
   59|         return None if self.__cond is None else self.__cond(self._obj)
   60| 
   61| 
   62| class _DescriptorBase:
   63|     """Descriptor base class implementing the basic descriptor protocol."""
   64| 
   65|     def __init__(self, deprecated=False):
   66|         self.__attrname = None
   67|         self.__deprecated = deprecated
   68| 
   69|     def __set_name__(self, ow
... [300 more chars]
```

### 17. `search_code`(pattern="create_autospec")

Tool responded:

```
(no matches)
```

## 4. Submitted test

```python
import unittest.mock

from cachetools import cachedmethod, LRUCache


def test_create_autospec_on_cachedmethod_class_does_not_raise():
    """Regression test for: using unittest.mock.create_autospec() on a class
    that has a @cachedmethod-decorated method blows up instead of just
    producing a mock.

    unittest.mock introspects class-level attributes (e.g. via
    getattr(spec, attr, None) to check iscoroutinefunction), which triggers
    the descriptor's __get__ with obj=None (class-level access, not through
    an instance). The descriptor must handle this gracefully instead of
    raising, exactly as it does for plain methods.
    """

    class Cached:
        def __init__(self):
            self.cache = LRUCache(maxsize=10)

        @cachedmethod(lambda self: self.cache, info=True)
        def get(self, key):
            return key

    # This must succeed and simply produce a mock, not raise an
    # AttributeError/TypeError from inside the cachedmethod descriptor logic.
    mock_obj = unittest.mock.create_autospec(Cached, instance=True)
    assert mock_obj is not None
```

**Agent's stated rationale:**

> The bug report states that unittest.mock.create_autospec() raises an AttributeError (from descriptor logic being invoked with obj=None during class-attribute introspection) on classes using @cachedmethod, and that this should instead work without raising.

Investigation of src/cachetools/_cachedmethod.py shows _DescriptorBase.__get__ unconditionally does `wrapper = self.Wrapper(obj)` and then, when an attrname is set, tries `obj.__dict__.setdefault(...)`. When mock introspects the class itself (not an instance), Python calls `__get__(None, cls)`, so obj is None and `None.__dict__` raises AttributeError, which for non-deprecated cachedmethod descriptors (e.g. the ones created when info=True) is re-raised as a TypeError instead of being swallowed - i.e. create_autospec blows up instead of producing a mock.

The test reproduces the exact repro pattern from the bug report (a class with an __init__ setting an LRUCache and a @cachedmethod-decorated method), using info=True to hit the code path in the current codebase that actually raises today, and asserts that create_autospec(Cached, instance=True) succeeds and returns a mock object (the "should just work" behavior described in the report).

Verified: the test fails on the current buggy code with a TypeError raised from inside _DescriptorBase.__get__ (the same descriptor logic named in the report). Using try_fix with a minimal hypothesized fix - returning the descriptor itself early when __get__ is called with obj=None (i.e. class-level attribute access, as opposed to instance access) - the test passes, and the existing test suite remains green, confirming both halves of the grading gate.

## 5. Two-sided gate

### Against `buggy/` — exit 1 (must be non-zero)

```
 raising, exactly as it does for plain methods.
        """
    
        class Cached:
            def __init__(self):
                self.cache = LRUCache(maxsize=10)
    
            @cachedmethod(lambda self: self.cache, info=True)
            def get(self, key):
                return key
    
        # This must succeed and simply produce a mock, not raise an
        # AttributeError/TypeError from inside the cachedmethod descriptor logic.
>       mock_obj = unittest.mock.create_autospec(Cached, instance=True)
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_regressgen_candidate.py:28: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
~/.local/share/uv/python/cpython-3.12.13-macos-aarch64-none/lib/python3.12/unittest/mock.py:2773: in create_autospec
    mock = Klass(parent=_parent, _new_parent=_parent, _new_name=_new_name,
~/.local/share/uv/python/cpython-3.12.13-macos-aarch64-none/lib/python3.12/unittest/mock.py:2139: in __init__
    _safe_super(MagicMixin, self).__init__(*args, **kw)
~/.local/share/uv/python/cpython-3.12.13-macos-aarch64-none/lib/python3.12/unittest/mock.py:460: in __init__
    self._mock_add_spec(spec, spec_set, _spec_as_instance, _eat_self)
~/.local/share/uv/python/cpython-3.12.13-macos-aarch64-none/lib/python3.12/unittest/mock.py:529: in _mock_add_spec
    if iscoroutinefunction(getattr(spec, attr, None)):
                           ^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <cachetools._cachedmethod._unlocked_info.<locals>.Descriptor object at 0x107078830>
obj = None
objtype = <class 'tests.test_regressgen_candidate.test_create_autospec_on_cachedmethod_class_does_not_raise.<locals>.Cached'>

    def __get__(self, obj, objtype=None):
        wrapper = self.Wrapper(obj)
        if self.__attrname is not None:
            # replace descriptor instance with wrapper in instance dict
            try:
                # In case of a race condition where another thread already replaced
                # the descriptor, prefer the initial wrapper.
                wrapper = obj.__dict__.setdefault(self.__att
... [800 more chars]
```

### Against `fixed/` — exit 0 (must be zero)

```
.                                                                        [100%]
1 passed in 0.08s
```

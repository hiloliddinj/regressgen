# Trajectory — `v4-discipline` on `cachetools-57d2e481`

**Verdict: REPRO**  (fails on buggy, passes on fixed — reproduces the bug)

- cost `$0.45207` · wall `105.8s` · tool calls `14`

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

### 2. `read_file`(path="src/cachetools/__init__.py", start=750, end=830)

Tool responded:

```
src/cachetools/__init__.py lines 750-772 of 772

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
  762|                     return _CacheInfo(hits, misses, cache.maxsize, cache.currsize)
  763|                 elif isinstance(cache, collections.abc.Mapping):
  764|                     return _CacheInfo(hits, misses, None, len(cache))
  765|                 else:
  766|                     raise TypeError("cache(self) must return a mutable mapping")
  767| 
  768|             return _wrapper(method, cache, key, lock, condition, info=make_info)
  769|         else:
  770|             return _wrapper(method, cache, key, lock, condition)
  771| 
  772|     return decorator
```

### 3. `read_file`(path="src/cachetools/_cachedmethod.py", start=0, end=0)

Tool responded:

```
src/cachetools/_cachedmethod.py is 410 lines — too long to show whole.
Definition outline below; call read_file again with start/end to read a range.

   10| def _warn_classmethod(stacklevel):
   18| def _warn_instance_dict(msg, stacklevel):
   26| class _WrapperBase:
   29|     def __init__(self, obj, method, cache, key, lock=None, cond=None):
   39|     def __call__(self, *args, **kwargs):
   42|     def cache_clear(self):
   45|     @property
   46|     def cache(self):
   49|     @property
   50|     def cache_key(self):
   53|     @property
   54|     def cache_lock(self):
   57|     @property
   58|     def cache_condition(self):
   62| class _DescriptorBase:
   65|     def __init__(self, deprecated=False):
   69|     def __set_name__(self, owner, name):
   78|     def __get__(self, obj, objtype=None):
  114| class _DeprecatedDescriptorBase(_DescriptorBase):
  117|     def __init__(self, wrapper, cache_clear):
  123|     def __call__(self, *args, **kwargs):
  128|     def cache_clear(self, objtype):
  139| def _condition_info(method, cache, key, lock, cond, info):
  140|     class Descriptor(_DescriptorBase):
  141|         class Wrapper(_WrapperBase):
  142|             def __init__(self, obj):
  147|             def __call__(self, *args, **kwargs):
  175|             def cache_clear(self):
  180|             def cache_info(self):
  187| def _locked_info(method, cache, key, lock, info):
  188|     class Descriptor(_DescriptorBase):
  189|         class Wrapper(_WrapperBase):
  190|             def __init__(self, obj):
  194|             def __call__(self, *args, **kwargs):
  215|             def cache_clear(self):
  220|             def cache_info(self):
  227| def _unlocked_info(method, cache, key, info):
  228|     class Descriptor(_DescriptorBase):
  229|         class Wrapper(_WrapperBase):
  230|             def __init__(self, obj):
  234|             def __call__(self, *args, **kwargs):
  250|             def cache_clear(self):
  254|             def cache_info(self):
  260| def _condition(method, cache, key, lock, cond):
  264|     def wrapper(self, pending, *args, **kwargs):
  286|     def cache_clear(self):
  291|     def classmethod_wrapper(self
... [300 more chars]
```

### 4. `read_file`(path="src/cachetools/_cachedmethod.py", start=62, end=140)

Tool responded:

```
src/cachetools/_cachedmethod.py lines 62-140 of 410

   62| class _DescriptorBase:
   63|     """Descriptor base class implementing the basic descriptor protocol."""
   64| 
   65|     def __init__(self, deprecated=False):
   66|         self.__attrname = None
   67|         self.__deprecated = deprecated
   68| 
   69|     def __set_name__(self, owner, name):
   70|         if self.__attrname is None:
   71|             self.__attrname = name
   72|         elif name != self.__attrname:
   73|             raise TypeError(
   74|                 "Cannot assign the same @cachedmethod to two different names "
   75|                 f"({self.__attrname!r} and {name!r})."
   76|             )
   77| 
   78|     def __get__(self, obj, objtype=None):
   79|         wrapper = self.Wrapper(obj)
   80|         if self.__attrname is not None:
   81|             # replace descriptor instance with wrapper in instance dict
   82|             try:
   83|                 # In case of a race condition where another thread already replaced
   84|                 # the descriptor, prefer the initial wrapper.
   85|                 wrapper = obj.__dict__.setdefault(self.__attrname, wrapper)
   86|             except AttributeError:
   87|                 # not all objects have __dict__ (e.g. class defines slots)
   88|                 msg = (
   89|                     f"No '__dict__' attribute on {type(obj).__name__!r} "
   90|                     f"instance to cache {self.__attrname!r} property."
   91|                 )
   92|                 if self.__deprecated:
   93|                     _warn_instance_dict(msg, 3)
   94|                 else:
   95|                     raise TypeError(msg) from None
   96|             except TypeError:
   97|                 msg = (
   98|                     f"The '__dict__' attribute on {type(obj).__name__!r} "
   99|                     f"instance does not support item assignment for "
  100|                     f"caching {self.__attrname!r} property."
  101|                 )
  102|                 if self.__deprecated:
  103|                     _warn_instance_dict(msg, 3)
  104|                 else:
  105|                     raise T
... [300 more chars]
```

### 5. `run_test`(test_source="\nimport unittest.mock\nfrom cachetools import cachedmethod, LRUCache\n\nclass Cached:\n    def __init__(self)

Tool responded:

```
PASSED (exit 0) — this test does NOT reproduce the bug

.                                                                        [100%]
=============================== warnings summary ===============================
tests/test_regressgen_candidate.py::test_repro
  ~/.local/share/uv/python/cpython-3.12.13-macos-aarch64-none/lib/python3.12/unittest/mock.py:529: DeprecationWarning: No '__dict__' attribute on 'NoneType' instance to cache 'get' property.
    if iscoroutinefunction(getattr(spec, attr, None)):

tests/test_regressgen_candidate.py::test_repro
  ~/.local/share/uv/python/cpython-3.12.13-macos-aarch64-none/lib/python3.12/unittest/mock.py:2810: DeprecationWarning: No '__dict__' attribute on 'NoneType' instance to cache 'get' property.
    original = getattr(spec, entry)

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
1 passed, 2 warnings in 0.08s
```

### 6. `read_file`(path="src/cachetools/_cachedmethod.py", start=384, end=410)

Tool responded:

```
src/cachetools/_cachedmethod.py lines 384-410 of 410

  384| def _wrapper(method, cache, key, lock=None, cond=None, info=None):
  385|     if info is not None:
  386|         if cond is not None and lock is not None:
  387|             wrapper = _condition_info(method, cache, key, lock, cond, info)
  388|         elif cond is not None:
  389|             wrapper = _condition_info(method, cache, key, cond, cond, info)
  390|         elif lock is not None:
  391|             wrapper = _locked_info(method, cache, key, lock, info)
  392|         else:
  393|             wrapper = _unlocked_info(method, cache, key, info)
  394|     else:
  395|         if cond is not None and lock is not None:
  396|             wrapper = _condition(method, cache, key, lock, cond)
  397|         elif cond is not None:
  398|             wrapper = _condition(method, cache, key, cond, cond)
  399|         elif lock is not None:
  400|             wrapper = _locked(method, cache, key, lock)
  401|         else:
  402|             wrapper = _unlocked(method, cache, key)
  403| 
  404|     # backward-compatible properties for deprecated @classmethod use
  405|     wrapper.cache = cache
  406|     wrapper.cache_key = key
  407|     wrapper.cache_lock = lock if lock is not None else cond
  408|     wrapper.cache_condition = cond
  409| 
  410|     return functools.update_wrapper(wrapper, method)
```

### 7. `read_file`(path="src/cachetools/_cachedmethod.py", start=227, end=260)

Tool responded:

```
src/cachetools/_cachedmethod.py lines 227-260 of 410

  227| def _unlocked_info(method, cache, key, info):
  228|     class Descriptor(_DescriptorBase):
  229|         class Wrapper(_WrapperBase):
  230|             def __init__(self, obj):
  231|                 super().__init__(obj, method, cache, key)
  232|                 self.__hits = self.__misses = 0
  233| 
  234|             def __call__(self, *args, **kwargs):
  235|                 cache = self.cache
  236|                 key = self.cache_key(self._obj, *args, **kwargs)
  237|                 try:
  238|                     result = cache[key]
  239|                     self.__hits += 1
  240|                     return result
  241|                 except KeyError:
  242|                     self.__misses += 1
  243|                 val = method(self._obj, *args, **kwargs)
  244|                 try:
  245|                     cache[key] = val
  246|                 except ValueError:
  247|                     pass  # value too large
  248|                 return val
  249| 
  250|             def cache_clear(self):
  251|                 self.cache.clear()
  252|                 self.__hits = self.__misses = 0
  253| 
  254|             def cache_info(self):
  255|                 return info(self.cache, self.__hits, self.__misses)
  256| 
  257|     return Descriptor()
  258| 
  259| 
  260| def _condition(method, cache, key, lock, cond):
```

### 8. `read_file`(path="src/cachetools/_cachedmethod.py", start=1, end=25)

Tool responded:

```
src/cachetools/_cachedmethod.py lines 1-25 of 410

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
```

### 9. `read_file`(path="src/cachetools/_cachedmethod.py", start=26, end=61)

Tool responded:

```
src/cachetools/_cachedmethod.py lines 26-61 of 410

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
```

### 10. `run_test`(test_source="\nimport cachetools._cachedmethod as cm\nfrom cachetools import cachedmethod, LRUCache\n\nclass Cached:\n    )

Tool responded:

```
FAILED (exit 1)

F                                                                        [100%]
=================================== FAILURES ===================================
__________________________________ test_repro __________________________________

    def test_repro():
        desc = Cached.__dict__['get']
        print("TYPE", type(desc))
        print("DEPRECATED", desc._DescriptorBase__deprecated)
        try:
            result = Cached.get
            print("RESULT", result)
        except Exception as e:
            print("EXC", type(e), e)
>       assert False
E       assert False

tests/test_regressgen_candidate.py:22: AssertionError
----------------------------- Captured stdout call -----------------------------
TYPE <class 'cachetools._cachedmethod._unlocked.<locals>.Descriptor'>
DEPRECATED True
RESULT <cachetools._cachedmethod._unlocked.<locals>.Descriptor.Wrapper object at 0x10349f440>
=============================== warnings summary ===============================
tests/test_regressgen_candidate.py::test_repro
  <sandbox>:18: DeprecationWarning: No '__dict__' attribute on 'NoneType' instance to cache 'get' property.
    result = Cached.get

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
FAILED tests/test_regressgen_candidate.py::test_repro - assert False
1 failed, 1 warning in 0.09s
```

### 11. `read_file`(path="src/cachetools/_cachedmethod.py", start=311, end=350)

Tool responded:

```
src/cachetools/_cachedmethod.py lines 311-350 of 410

  311| def _locked(method, cache, key, lock):
  312|     def wrapper(self, *args, **kwargs):
  313|         c = cache(self)
  314|         k = key(self, *args, **kwargs)
  315|         with lock(self):
  316|             try:
  317|                 return c[k]
  318|             except KeyError:
  319|                 pass  # key not found
  320|         v = method(self, *args, **kwargs)
  321|         with lock(self):
  322|             try:
  323|                 # In case of a race condition, i.e. if another thread
  324|                 # stored a value for this key while we were calling
  325|                 # method(), prefer the cached value.
  326|                 return c.setdefault(k, v)
  327|             except ValueError:
  328|                 return v  # value too large
  329| 
  330|     def cache_clear(self):
  331|         c = cache(self)
  332|         with lock(self):
  333|             c.clear()
  334| 
  335|     class Descriptor(_DeprecatedDescriptorBase):
  336|         class Wrapper(_WrapperBase):
  337|             def __init__(self, obj):
  338|                 super().__init__(obj, method, cache, key, lock)
  339| 
  340|             def __call__(self, *args, **kwargs):
  341|                 return wrapper(self._obj, *args, **kwargs)
  342| 
  343|             # objtype: backward-compatible @classmethod handling with Python < 3.13
  344|             def cache_clear(self, _objtype=None):
  345|                 return cache_clear(self._obj)
  346| 
  347|     return Descriptor(wrapper, cache_clear)
  348| 
  349| 
  350| def _unlocked(method, cache, key):
```

### 12. `run_test`(test_source="\nimport unittest.mock\nfrom cachetools import cachedmethod, LRUCache\n\nclass Cached:\n    def __init__(self)

Tool responded:

```
FAILED (exit 1)

F                                                                        [100%]
=================================== FAILURES ===================================
__________________________________ test_repro __________________________________

    def test_repro():
>       unittest.mock.create_autospec(Cached, instance=True)

tests/test_regressgen_candidate.py:14: 
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

self = <cachetools._cachedmethod._unlocked_info.<locals>.Descriptor object at 0x107543440>
obj = None, objtype = <class 'tests.test_regressgen_candidate.Cached'>

    def __get__(self, obj, objtype=None):
        wrapper = self.Wrapper(obj)
        if self.__attrname is not None:
            # replace descriptor instance with wrapper in instance dict
            try:
                # In case of a race condition where another thread already replaced
                # the descriptor, prefer the initial wrapper.
                wrapper = obj.__dict__.setdefault(self.__attrname, wrapper)
            except AttributeError:
                # not all objects have __dict__ (e.g. class defines slots)
                msg = (
                    f"No '__dict__' attribute on {type(obj).__name__!r} "
                    f"instance to cache {self.__attrname!r} property."
                )
    
... [300 more chars]
```

### 13. `run_test`(test_source="\nimport unittest.mock\n\nfrom cachetools import LRUCache, cachedmethod\n\n\nclass Cached:\n    def __init__()

Tool responded:

```
FAILED (exit 1)

F                                                                        [100%]
=================================== FAILURES ===================================
__________ test_create_autospec_on_cachedmethod_class_does_not_raise ___________

    def test_create_autospec_on_cachedmethod_class_does_not_raise():
        # Regression test for: using unittest.mock.create_autospec on a class
        # that has a cachedmethod-decorated method used to blow up while mock
        # introspected class attributes (invoking the descriptor's __get__ with
        # obj=None). It should instead just produce a working mock/autospec.
>       mock_instance = unittest.mock.create_autospec(Cached, instance=True)
                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_regressgen_candidate.py:21: 
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

self = <cachetools._cachedmethod._unlocked_info.<locals>.Descriptor object at 0x1097da8a0>
obj = None, objtype = <class 'tests.test_regressgen_candidate.Cached'>

    def __get__(self, obj, objtype=None):
        wrapper = self.Wrapper(obj)
        if self.__attrname is not None:
            # replace descriptor instance with wrapper in instance dict
            try:
                # In case of a race condition where another thread alr
... [300 more chars]
```

### 14. `submit_test`(rationale="The bug report describes unittest.mock.create_autospec raising an exception when used on a class with a cache)

Tool responded:

```
Submitted.

import unittest.mock

from cachetools import LRUCache, cachedmethod


class Cached:
    def __init__(self):
        self.cache = LRUCache(maxsize=10)

    # Using info=True (in addition to the plain lock/condition-less form
    # shown in the bug report) exercises the non-deprecated descriptor
    # path, which is where the class-level (obj=None) attribute access
    # performed by unittest.mock's introspection currently blows up.
    @cachedmethod(lambda self: self.cache, info=True)
    def get(self, key):
        return key


def test_create_autospec_on_cachedmethod_class_does_not_raise():
    # Regression test for: using unittest.mock.create_autospec on a class
    # that has a cachedmethod-decorated method used to raise an exception
    # from deep inside the descriptor's __get__ while unittest.mock
    # introspected class attributes (e.g. via
    # `iscoroutinefunction(getattr(spec, attr, None))`, which invokes the
    # descriptor with obj=None). create_autospec should work normally
    # instead, producing a usable mock/autospec, just like it does for
    # plain (undecorated) methods.
    mock_instance = unittest.mock.create_autospec(Cached, instance=True)

    assert mock_instance is not None

    # The autospec'd instance should behave like a normal mock for the
    # cached method.
    mock_instance.get.return_value = 42
    assert mock_instance.get("x") == 42
```

## 4. Submitted test

```python
import unittest.mock

from cachetools import LRUCache, cachedmethod


class Cached:
    def __init__(self):
        self.cache = LRUCache(maxsize=10)

    # Using info=True (in addition to the plain lock/condition-less form
    # shown in the bug report) exercises the non-deprecated descriptor
    # path, which is where the class-level (obj=None) attribute access
    # performed by unittest.mock's introspection currently blows up.
    @cachedmethod(lambda self: self.cache, info=True)
    def get(self, key):
        return key


def test_create_autospec_on_cachedmethod_class_does_not_raise():
    # Regression test for: using unittest.mock.create_autospec on a class
    # that has a cachedmethod-decorated method used to raise an exception
    # from deep inside the descriptor's __get__ while unittest.mock
    # introspected class attributes (e.g. via
    # `iscoroutinefunction(getattr(spec, attr, None))`, which invokes the
    # descriptor with obj=None). create_autospec should work normally
    # instead, producing a usable mock/autospec, just like it does for
    # plain (undecorated) methods.
    mock_instance = unittest.mock.create_autospec(Cached, instance=True)

    assert mock_instance is not None

    # The autospec'd instance should behave like a normal mock for the
    # cached method.
    mock_instance.get.return_value = 42
    assert mock_instance.get("x") == 42
```

**Agent's stated rationale:**

> The bug report describes unittest.mock.create_autospec raising an exception when used on a class with a cachedmethod-decorated method, because mock's introspection accesses the descriptor via the class (obj=None) rather than an instance. Reading src/cachetools/_cachedmethod.py shows _DescriptorBase.__get__ calls obj.__dict__.setdefault(...) unconditionally; when obj is None this raises AttributeError, which is caught and converted to a raised TypeError unless the descriptor was created in "deprecated" mode (only true for the plain lock/condition-less cachedmethod variants, which fall back to a warning instead of raising). Any cachedmethod configuration that goes through the non-deprecated descriptor path (e.g. info=True, or lock+info, or condition+info) still raises when accessed with obj=None, exactly as create_autospec does during class attribute enumeration. I verified via run_test that this test currently fails on the buggy code with the exact reported failure mode (an exception surfacing from __get__ during mock's `getattr(spec, attr, None)` introspection), and that the correct/expected behavior per the report is for create_autospec to succeed and return a normal, usable mock instead of raising.

## 5. Two-sided gate

### Against `buggy/` — exit 1 (must be non-zero)

```
nittest.mock.create_autospec on a class
        # that has a cachedmethod-decorated method used to raise an exception
        # from deep inside the descriptor's __get__ while unittest.mock
        # introspected class attributes (e.g. via
        # `iscoroutinefunction(getattr(spec, attr, None))`, which invokes the
        # descriptor with obj=None). create_autospec should work normally
        # instead, producing a usable mock/autospec, just like it does for
        # plain (undecorated) methods.
>       mock_instance = unittest.mock.create_autospec(Cached, instance=True)
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

self = <cachetools._cachedmethod._unlocked_info.<locals>.Descriptor object at 0x1090d28d0>
obj = None, objtype = <class 'tests.test_regressgen_candidate.Cached'>

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

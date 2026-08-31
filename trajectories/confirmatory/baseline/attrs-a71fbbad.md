# Trajectory — `baseline` on `attrs-a71fbbad`

**Verdict: WRONG_EXPECTATION**

- cost `$0.04211` · wall `9.8s` · tool calls `0`

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
Frozen exception classes made with attrs blow up as soon as Python tries to attach a traceback to them. This happens even without doing anything unusual - just raising the exception inside a context manager (e.g. contextlib.contextmanager based ones) triggers it, and even manually re-assigning the traceback attribute to itself fails.

```python
import attrs
from contextlib import contextmanager

@attrs.frozen
class MyException(Exception):
    pass

@contextmanager
def do_nothing():
    yield

try:
    with do_nothing():
        raise MyException()
except MyException as e:
    e.__traceback__ = e.__traceback__  # raises FrozenInstanceError
```

I expected exception instances to still allow their traceback to be set/updated, since that's normal exception machinery, not user code touching frozen fields. Instead it raises FrozenInstanceError, which makes frozen exceptions basically unusable in combination with context managers or manual re-raising.
```

## 3. Tool calls

_No tools — this system answers in a single prompt._

## 4. Submitted test

```python
import traceback

import pytest

import attrs


def test_frozen_exception_allows_traceback_reassignment():
    """
    Regression test: setting __traceback__ on a frozen exception instance
    (as Python's exception machinery does automatically, e.g. when raised
    inside a context manager, or when manually re-raising) must not raise
    FrozenInstanceError.
    """

    @attrs.frozen
    class MyException(Exception):
        pass

    try:
        raise MyException()
    except MyException as e:
        # This mimics what Python's exception machinery does internally
        # (and what users do when manually re-raising exceptions).
        e.__traceback__ = e.__traceback__


def test_frozen_exception_traceback_survives_context_manager():
    from contextlib import contextmanager

    @attrs.frozen
    class MyException(Exception):
        pass

    @contextmanager
    def do_nothing():
        yield

    caught = None
    try:
        with do_nothing():
            raise MyException("boom")
    except MyException as e:
        caught = e

    assert caught is not None
    # Should be able to format the traceback without errors.
    traceback.format_exception(type(caught), caught, caught.__traceback__)
```

## 5. Two-sided gate

### Against `buggy/` — exit 1 (must be non-zero)

```
==
_____________ test_frozen_exception_allows_traceback_reassignment ______________

    def test_frozen_exception_allows_traceback_reassignment():
        """
        Regression test: setting __traceback__ on a frozen exception instance
        (as Python's exception machinery does automatically, e.g. when raised
        inside a context manager, or when manually re-raising) must not raise
        FrozenInstanceError.
        """
    
        @attrs.frozen
        class MyException(Exception):
            pass
    
        try:
>           raise MyException()
E           tests.test_regressgen_candidate.test_frozen_exception_allows_traceback_reassignment.<locals>.MyException

tests/test_regressgen_candidate.py:21: MyException

During handling of the above exception, another exception occurred:

    def test_frozen_exception_allows_traceback_reassignment():
        """
        Regression test: setting __traceback__ on a frozen exception instance
        (as Python's exception machinery does automatically, e.g. when raised
        inside a context manager, or when manually re-raising) must not raise
        FrozenInstanceError.
        """
    
        @attrs.frozen
        class MyException(Exception):
            pass
    
        try:
            raise MyException()
        except MyException as e:
            # This mimics what Python's exception machinery does internally
            # (and what users do when manually re-raising exceptions).
>           e.__traceback__ = e.__traceback__
            ^^^^^^^^^^^^^^^

tests/test_regressgen_candidate.py:25: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = MyException(), name = '__traceback__'
value = <traceback object at 0x109c85400>

    def _frozen_setattrs(self, name, value):
        """
        Attached to frozen classes as __setattr__.
        """
>       raise FrozenInstanceError()
E       attr.exceptions.FrozenInstanceError

<sandbox>:606: FrozenInstanceError
___________ test_frozen_exception_traceback_survives_context_manager ___________

    def test_frozen_exception_traceback_survives_context_manager():
        from contextlib import contextmanager
    
        @a
... [800 more chars]
```

### Against `fixed/` — exit 1 (must be zero)

```
.F                                                                       [100%]
=================================== FAILURES ===================================
___________ test_frozen_exception_traceback_survives_context_manager ___________

    def test_frozen_exception_traceback_survives_context_manager():
        from contextlib import contextmanager
    
        @attrs.frozen
        class MyException(Exception):
            pass
    
        @contextmanager
        def do_nothing():
            yield
    
        caught = None
        try:
            with do_nothing():
>               raise MyException("boom")
                      ^^^^^^^^^^^^^^^^^^^
E               TypeError: test_frozen_exception_traceback_survives_context_manager.<locals>.MyException.__init__() takes 1 positional argument but 2 were given

tests/test_regressgen_candidate.py:42: TypeError
=========================== short test summary info ============================
FAILED tests/test_regressgen_candidate.py::test_frozen_exception_traceback_survives_context_manager
1 failed, 1 passed in 0.02s
```

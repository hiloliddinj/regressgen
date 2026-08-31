# Trajectory — `baseline` on `attrs-c9150d27`

**Verdict: WRONG_EXPECTATION**

- cost `$0.058` · wall `26.6s` · tool calls `0`

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
Unpickling old pickle data of a slotted attrs class fails to properly restore the object's attributes on current attrs.

I have a bunch of pickled objects created a while ago (slotted, frozen attrs class with attributes x, b, c). Loading them with `pickle.loads` on a newer attrs version gives back an object that looks fine in isolation but is actually missing an attribute — accessing it raises AttributeError, and comparing it to a freshly-constructed equal instance blows up instead of returning True/False.

```python
import pickle
import attr

@attr.s(slots=True, frozen=True)
class A:
    x = attr.ib()
    b = attr.ib()
    c = attr.ib()

a = A(1, 2, 3)

# pickle produced by an older attrs version, loaded now:
old_pickled = b"\x80\x04\x95&\x00\x00\x00\x00\x00\x00\x00\x8c\x10__main__\x94\x8c\x01A\x94\x93\x94)\x81\x94K\x01K\x02K\x03\x87\x94b."

restored = pickle.loads(old_pickled)
restored == a  # raises AttributeError instead of comparing
```

I expected old pickles to still unpickle into fully-populated, usable objects, not ones missing one of their attributes. This only shows up with frozen slotted classes for me.
```

## 3. Tool calls

_No tools — this system answers in a single prompt._

## 4. Submitted test

```python
import pickle
import sys

import pytest

import attr


# Bytes produced by pickling an *old* (pre-22.2) attrs version of:
#
#     @attr.s(slots=True, frozen=True)
#     class A:
#         x = attr.ib()
#         b = attr.ib()
#         c = attr.ib()
#
#     a = A(1, 2, 3)
#     pickle.dumps(a)
#
# The old-style getstate/setstate stored the state as a plain tuple of
# values (in attribute order), not as a dict of name -> value.
OLD_PICKLE = (
    b"\x80\x04\x95&\x00\x00\x00\x00\x00\x00\x00\x8c\x10__main__\x94\x8c"
    b"\x01A\x94\x93\x94)\x81\x94K\x01K\x02K\x03\x87\x94b."
)


@attr.s(slots=True, frozen=True)
class A:
    x = attr.ib()
    b = attr.ib()
    c = attr.ib()


@pytest.fixture(autouse=True)
def _install_class_in_main():
    """
    The pickle blob references `__main__.A`, so make sure that name
    resolves to our test class for the duration of the test.
    """
    main_module = sys.modules["__main__"]
    had_attr = hasattr(main_module, "A")
    previous = getattr(main_module, "A", None)

    A.__module__ = "__main__"
    main_module.A = A

    yield

    if had_attr:
        main_module.A = previous
    else:
        delattr(main_module, "A")


def test_unpickling_old_tuple_state_restores_all_attributes():
    """
    Old pickles that stored the instance's state as a plain tuple (instead
    of the current dict-based __getstate__ format) must still unpickle into
    fully-populated instances -- every attribute must be present and have
    its correct value.
    """
    restored = pickle.loads(OLD_PICKLE)

    # All attributes must actually be set on the restored instance.
    assert restored.x == 1
    assert restored.b == 2
    assert restored.c == 3

    # Comparing to a freshly constructed, equal instance must not raise
    # and must correctly report equality.
    fresh = A(1, 2, 3)
    assert restored == fresh
```

## 5. Two-sided gate

### Against `buggy/` — exit 1 (must be non-zero)

```
F                                                                        [100%]
=================================== FAILURES ===================================
___________ test_unpickling_old_tuple_state_restores_all_attributes ____________

    def test_unpickling_old_tuple_state_restores_all_attributes():
        """
        Old pickles that stored the instance's state as a plain tuple (instead
        of the current dict-based __getstate__ format) must still unpickle into
        fully-populated instances -- every attribute must be present and have
        its correct value.
        """
>       restored = pickle.loads(OLD_PICKLE)
                   ^^^^^^^^^^^^^^^^^^^^^^^^
E       _pickle.UnpicklingError: pickle data was truncated

tests/test_regressgen_candidate.py:63: UnpicklingError
=========================== short test summary info ============================
FAILED tests/test_regressgen_candidate.py::test_unpickling_old_tuple_state_restores_all_attributes
1 failed in 0.02s
```

### Against `fixed/` — exit 1 (must be zero)

```
F                                                                        [100%]
=================================== FAILURES ===================================
___________ test_unpickling_old_tuple_state_restores_all_attributes ____________

    def test_unpickling_old_tuple_state_restores_all_attributes():
        """
        Old pickles that stored the instance's state as a plain tuple (instead
        of the current dict-based __getstate__ format) must still unpickle into
        fully-populated instances -- every attribute must be present and have
        its correct value.
        """
>       restored = pickle.loads(OLD_PICKLE)
                   ^^^^^^^^^^^^^^^^^^^^^^^^
E       _pickle.UnpicklingError: pickle data was truncated

tests/test_regressgen_candidate.py:63: UnpicklingError
=========================== short test summary info ============================
FAILED tests/test_regressgen_candidate.py::test_unpickling_old_tuple_state_restores_all_attributes
1 failed in 0.02s
```

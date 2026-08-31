# Trajectory — `baseline` on `attrs-ce89f5d1`

**Verdict: REPRO**  (fails on buggy, passes on fixed — reproduces the bug)

- cost `$0.00735` · wall `7.1s` · tool calls `0`

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
FrozenInstanceError raised on frozen attrs classes doesn't carry a message. If I try to set or delete an attribute on a frozen instance, I get an empty exception - no "can't set attribute" text or anything, just the bare exception class with no args.

```python
import attr
from attr.exceptions import FrozenInstanceError

@attr.s(frozen=True)
class Frozen:
    x = attr.ib()

f = Frozen(1)
try:
    f.x = 2
except FrozenInstanceError as e:
    print(repr(e.args))
    print(repr(getattr(e, "msg", None)))
```

This prints empty args and `msg` is missing/None. Same thing happens on `del f.x`.

I'd expect the exception to actually explain what went wrong, e.g. something like "can't set attribute", available both as the exception message and via `.msg`, similar to how a normal frozen dataclass/object raises. Right now it's silent, which makes debugging or matching on the error message impossible.
```

## 3. Tool calls

_No tools — this system answers in a single prompt._

## 4. Submitted test

```python
"""
Regression test for: FrozenInstanceError raised on frozen attrs classes
doesn't carry a message.

The exception should behave like a namedtuple's frozen error: it should
have non-empty `args` containing the message "can't set attribute", and
a `.msg` attribute with the same text.
"""
import pytest

import attr
from attr.exceptions import FrozenInstanceError, FrozenError


@attr.s(frozen=True)
class Frozen:
    x = attr.ib()


def test_frozen_instance_error_has_message_on_setattr():
    f = Frozen(1)
    with pytest.raises(FrozenInstanceError) as ei:
        f.x = 2

    exc = ei.value
    assert exc.args == ("can't set attribute",)
    assert getattr(exc, "msg", None) == "can't set attribute"
    assert str(exc) == "can't set attribute"


def test_frozen_instance_error_has_message_on_delattr():
    f = Frozen(1)
    with pytest.raises(FrozenInstanceError) as ei:
        del f.x

    exc = ei.value
    assert exc.args == ("can't set attribute",)
    assert getattr(exc, "msg", None) == "can't set attribute"
    assert str(exc) == "can't set attribute"


def test_frozen_error_class_itself_has_message():
    exc = FrozenError()
    assert exc.args == ("can't set attribute",)
    assert exc.msg == "can't set attribute"
```

## 5. Two-sided gate

### Against `buggy/` — exit 1 (must be non-zero)

```
FFF                                                                      [100%]
=================================== FAILURES ===================================
______________ test_frozen_instance_error_has_message_on_setattr _______________

    def test_frozen_instance_error_has_message_on_setattr():
        f = Frozen(1)
        with pytest.raises(FrozenInstanceError) as ei:
            f.x = 2
    
        exc = ei.value
>       assert exc.args == ("can't set attribute",)
E       assert ["can't set attribute"] == ("can't set attribute",)
E         
E         Use -v to get more diff

tests/test_regressgen_candidate.py:26: AssertionError
______________ test_frozen_instance_error_has_message_on_delattr _______________

    def test_frozen_instance_error_has_message_on_delattr():
        f = Frozen(1)
        with pytest.raises(FrozenInstanceError) as ei:
            del f.x
    
        exc = ei.value
>       assert exc.args == ("can't set attribute",)
E       assert ["can't set attribute"] == ("can't set attribute",)
E         
E         Use -v to get more diff

tests/test_regressgen_candidate.py:37: AssertionError
__________________ test_frozen_error_class_itself_has_message __________________

    def test_frozen_error_class_itself_has_message():
        exc = FrozenError()
>       assert exc.args == ("can't set attribute",)
E       assert ["can't set attribute"] == ("can't set attribute",)
E         
E         Use -v to get more diff

tests/test_regressgen_candidate.py:44: AssertionError
=========================== short test summary info ============================
FAILED tests/test_regressgen_candidate.py::test_frozen_instance_error_has_message_on_setattr
FAILED tests/test_regressgen_candidate.py::test_frozen_instance_error_has_message_on_delattr
FAILED tests/test_regressgen_candidate.py::test_frozen_error_class_itself_has_message
3 failed in 0.02s
```

### Against `fixed/` — exit 0 (must be zero)

```
...                                                                      [100%]
3 passed in 0.01s
```

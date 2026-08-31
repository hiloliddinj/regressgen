# Trajectory — `baseline` on `attrs-937b1e23`

**Verdict: REPRO**  (fails on buggy, passes on fixed — reproduces the bug)

- cost `$0.04446` · wall `10.0s` · tool calls `0`

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
`__attrs_pre_init__` is receiving the wrong values for some attributes when the class has a mix of positional, defaulted, and keyword-only fields.

```python
import attr

@attr.define
class MixtureClass:
    val1: int
    val2: int = 100
    val3: int = attr.field(factory=int)
    val4: int = attr.field(kw_only=True)
    val5: int = attr.field(default=100, kw_only=True)
    val6: int = attr.field(factory=int, kw_only=True)

    def __attrs_pre_init__(self, val1, val2, val3, val4, val5, val6):
        print(val1, val2, val3, val4, val5, val6)

MixtureClass(val1=200, val2=200, val3=200, val4=200, val5=200, val6=200)
```

I expected `__attrs_pre_init__` to be called with all values equal to 200, matching what's passed to the constructor and what ends up on the instance. Instead `val2` (and possibly others) shows up as `100`, i.e. the default value, even though I explicitly passed `200`. The final instance attribute is correct, it's just the pre_init call that gets stale/default values instead of the actual arguments.
```

## 3. Tool calls

_No tools — this system answers in a single prompt._

## 4. Submitted test

```python
"""
Regression test for the bug where ``__attrs_pre_init__`` receives stale
default values instead of the actual arguments passed to ``__init__`` when
the class has a mix of positional (with and without defaults) and keyword
-only fields.

See: https://github.com/python-attrs/attrs/issues (pre_init args bug)
"""

import attr


def test_pre_init_receives_actual_values_not_defaults():
    calls = []

    @attr.s(init=True)
    class MixtureClass:
        val1 = attr.ib()
        val2 = attr.ib(default=100)
        val3 = attr.ib(factory=int)
        val4 = attr.ib(kw_only=True)
        val5 = attr.ib(default=100, kw_only=True)
        val6 = attr.ib(factory=int, kw_only=True)

        def __attrs_pre_init__(self, val1, val2, val3, val4, val5, val6):
            calls.append((val1, val2, val3, val4, val5, val6))

    inst = MixtureClass(val1=200, val2=200, val3=200, val4=200, val5=200, val6=200)

    # The final instance attributes should be correct.
    assert inst.val1 == 200
    assert inst.val2 == 200
    assert inst.val3 == 200
    assert inst.val4 == 200
    assert inst.val5 == 200
    assert inst.val6 == 200

    # __attrs_pre_init__ must have been called exactly once...
    assert len(calls) == 1

    # ...with the actual values passed to the constructor, not the stale
    # default values baked into the generated __init__.
    assert calls[0] == (200, 200, 200, 200, 200, 200)
```

## 5. Two-sided gate

### Against `buggy/` — exit 1 (must be non-zero)

```
F                                                                        [100%]
=================================== FAILURES ===================================
______________ test_pre_init_receives_actual_values_not_defaults _______________

    def test_pre_init_receives_actual_values_not_defaults():
        calls = []
    
        @attr.s(init=True)
        class MixtureClass:
            val1 = attr.ib()
            val2 = attr.ib(default=100)
            val3 = attr.ib(factory=int)
            val4 = attr.ib(kw_only=True)
            val5 = attr.ib(default=100, kw_only=True)
            val6 = attr.ib(factory=int, kw_only=True)
    
            def __attrs_pre_init__(self, val1, val2, val3, val4, val5, val6):
                calls.append((val1, val2, val3, val4, val5, val6))
    
        inst = MixtureClass(val1=200, val2=200, val3=200, val4=200, val5=200, val6=200)
    
        # The final instance attributes should be correct.
        assert inst.val1 == 200
        assert inst.val2 == 200
        assert inst.val3 == 200
        assert inst.val4 == 200
        assert inst.val5 == 200
        assert inst.val6 == 200
    
        # __attrs_pre_init__ must have been called exactly once...
        assert len(calls) == 1
    
        # ...with the actual values passed to the constructor, not the stale
        # default values baked into the generated __init__.
>       assert calls[0] == (200, 200, 200, 200, 200, 200)
E       assert (200, 100, NO...200, 200, 200) == (200, 200, 200, 200, 200, 200)
E         
E         At index 1 diff: 100 != 200
E         Use -v to get more diff

tests/test_regressgen_candidate.py:43: AssertionError
=========================== short test summary info ============================
FAILED tests/test_regressgen_candidate.py::test_pre_init_receives_actual_values_not_defaults
1 failed in 0.02s
```

### Against `fixed/` — exit 0 (must be zero)

```
.                                                                        [100%]
1 passed in 0.01s
```

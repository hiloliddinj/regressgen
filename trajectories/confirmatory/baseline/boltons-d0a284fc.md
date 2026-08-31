# Trajectory — `baseline` on `boltons-d0a284fc`

**Verdict: REPRO**  (fails on buggy, passes on fixed — reproduces the bug)

- cost `$0.01733` · wall `7.0s` · tool calls `0`

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
IndexedSet doesn't raise IndexError for negative indices that are way out of range - instead it silently wraps around and returns some other element. Same problem happens with pop().

Example:

```python
from boltons.setutils import IndexedSet

x = IndexedSet(range(10))
x.pop(2)  # len is now 9

print(x[-1])   # 9, fine
print(x[-10])  # expected IndexError, got 9 back instead

x.pop(-15)  # expected IndexError, instead silently removes some unrelated element
print(4 in x)  # False - 4 got popped even though -15 is nowhere close to valid range
```

For a set of length 9, I'd expect indices from -9 to 8 to be valid and anything outside that to raise IndexError, same as it would for a list. Instead negative indices seem to get normalized twice somehow, so something like -10 or -15 just quietly maps to a valid-looking slot instead of raising. This is pretty dangerous with pop() since it can delete the wrong item without any warning that the index was invalid.
```

## 3. Tool calls

_No tools — this system answers in a single prompt._

## 4. Submitted test

```python
"""Regression test for IndexedSet negative-index out-of-range bug.

See bug report: IndexedSet doesn't raise IndexError for negative indices
that are way out of range - instead it silently wraps around and returns
(or pops) some other element.
"""

import pytest

from boltons.setutils import IndexedSet


def test_getitem_negative_index_out_of_range():
    x = IndexedSet(range(10))
    x.pop(2)  # len is now 9, valid indices: -9..8

    # sanity check: -1 should still work
    assert x[-1] == 9

    # -9 is the smallest valid negative index for a set of length 9
    assert x[-9] == 0

    # -10 is out of range and must raise IndexError, not wrap around
    with pytest.raises(IndexError):
        x[-10]

    # even more out of range
    with pytest.raises(IndexError):
        x[-15]


def test_pop_negative_index_out_of_range():
    x = IndexedSet(range(10))
    x.pop(2)  # len is now 9

    with pytest.raises(IndexError):
        x.pop(-15)

    # ensure nothing was actually removed as a side effect of the failed pop
    assert 4 in x
    assert len(x) == 9
```

## 5. Two-sided gate

### Against `buggy/` — exit 1 (must be non-zero)

```
FF                                                                       [100%]
=================================== FAILURES ===================================
___________________ test_getitem_negative_index_out_of_range ___________________

    def test_getitem_negative_index_out_of_range():
        x = IndexedSet(range(10))
        x.pop(2)  # len is now 9, valid indices: -9..8
    
        # sanity check: -1 should still work
        assert x[-1] == 9
    
        # -9 is the smallest valid negative index for a set of length 9
        assert x[-9] == 0
    
        # -10 is out of range and must raise IndexError, not wrap around
>       with pytest.raises(IndexError):
             ^^^^^^^^^^^^^^^^^^^^^^^^^
E       Failed: DID NOT RAISE <class 'IndexError'>

tests/test_regressgen_candidate.py:24: Failed
_____________________ test_pop_negative_index_out_of_range _____________________

    def test_pop_negative_index_out_of_range():
        x = IndexedSet(range(10))
        x.pop(2)  # len is now 9
    
>       with pytest.raises(IndexError):
             ^^^^^^^^^^^^^^^^^^^^^^^^^
E       Failed: DID NOT RAISE <class 'IndexError'>

tests/test_regressgen_candidate.py:36: Failed
=========================== short test summary info ============================
FAILED tests/test_regressgen_candidate.py::test_getitem_negative_index_out_of_range
FAILED tests/test_regressgen_candidate.py::test_pop_negative_index_out_of_range
2 failed in 0.09s
```

### Against `fixed/` — exit 0 (must be zero)

```
..                                                                       [100%]
2 passed in 0.08s
```

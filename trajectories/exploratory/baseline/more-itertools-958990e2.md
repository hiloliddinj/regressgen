# Trajectory — `baseline` on `more-itertools-958990e2`

**Verdict: REPRO**  (fails on buggy, passes on fixed — reproduces the bug)

- cost `$0.3239` · wall `5.7s` · tool calls `0`

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
`sliced()` doesn't complain if you pass a negative size, it just quietly does something weird instead of telling you the input is invalid.

```python
import more_itertools as mi

seq = 'ABCDEFG'
print(list(mi.sliced(seq, -1)))
print(list(mi.sliced(seq, -1, strict=True)))
```

I expected this to raise a `ValueError` since a negative slice size doesn't make sense, similar to how other bad inputs are rejected elsewhere in the library. Instead it runs without error and gives back a result that isn't the sliced sequence I'd expect (definitely not chunks of `seq`). This is easy to hit by accident, e.g. if a size is computed from some other value and ends up negative — no exception, just silently wrong output that could go unnoticed downstream.
```

## 3. Tool calls

_No tools — this system answers in a single prompt._

## 4. Submitted test

```python
import pytest
import more_itertools as mi


def test_sliced_negative_size_raises():
    seq = 'ABCDEFG'
    with pytest.raises(ValueError):
        list(mi.sliced(seq, -1))


def test_sliced_negative_size_raises_strict():
    seq = 'ABCDEFG'
    with pytest.raises(ValueError):
        list(mi.sliced(seq, -1, strict=True))
```

## 5. Two-sided gate

### Against `buggy/` — exit 1 (must be non-zero)

```
F.                                                                       [100%]
=================================== FAILURES ===================================
_______________________ test_sliced_negative_size_raises _______________________

    def test_sliced_negative_size_raises():
        seq = 'ABCDEFG'
>       with pytest.raises(ValueError):
             ^^^^^^^^^^^^^^^^^^^^^^^^^
E       Failed: DID NOT RAISE <class 'ValueError'>

tests/test_regressgen_candidate.py:7: Failed
=========================== short test summary info ============================
FAILED tests/test_regressgen_candidate.py::test_sliced_negative_size_raises
1 failed, 1 passed in 0.41s
```

### Against `fixed/` — exit 0 (must be zero)

```
..                                                                       [100%]
2 passed in 0.39s
```

# Trajectory — `baseline` on `boltons-ebc7a8f7`

**Verdict: REPRO**  (fails on buggy, passes on fixed — reproduces the bug)

- cost `$0.01912` · wall `6.0s` · tool calls `0`

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
copy.copy() and copy.deepcopy() on an OrderedMultiDict silently lose duplicate values for a key. Only the last value inserted per key survives the copy.

```python
import copy
from boltons.dictutils import OrderedMultiDict as OMD

omd = OMD([('a', 1), ('a', 2), ('b', 3)])

shallow = copy.copy(omd)
print(shallow == omd)          # False, expected True
print(shallow.getlist('a'))    # [2], expected [1, 2]

deep = copy.deepcopy(omd)
print(deep.getlist('a'))       # also [2], expected [1, 2]
```

I expected copying an OMD to produce an equal OMD that preserves every value for every key, same as pickling round-trips it correctly. Instead both copy.copy and copy.deepcopy end up keeping just one value per key, as if the earlier values were overwritten. This makes copy.copy/deepcopy unsafe to use on OMD instances that have any keys with more than one value, which is kind of the whole point of using OMD in the first place.
```

## 3. Tool calls

_No tools — this system answers in a single prompt._

## 4. Submitted test

```python
import copy

from boltons.dictutils import OrderedMultiDict as OMD


def test_omd_copy_preserves_duplicate_values():
    omd = OMD([('a', 1), ('a', 2), ('b', 3)])

    shallow = copy.copy(omd)
    assert shallow == omd
    assert shallow.getlist('a') == [1, 2]
    assert shallow.getlist('b') == [3]
    assert list(shallow.iteritems(multi=True)) == [('a', 1), ('a', 2), ('b', 3)]


def test_omd_deepcopy_preserves_duplicate_values():
    omd = OMD([('a', 1), ('a', 2), ('b', 3)])

    deep = copy.deepcopy(omd)
    assert deep == omd
    assert deep.getlist('a') == [1, 2]
    assert deep.getlist('b') == [3]
    assert list(deep.iteritems(multi=True)) == [('a', 1), ('a', 2), ('b', 3)]
```

## 5. Two-sided gate

### Against `buggy/` — exit 1 (must be non-zero)

```
FF                                                                       [100%]
=================================== FAILURES ===================================
___________________ test_omd_copy_preserves_duplicate_values ___________________

    def test_omd_copy_preserves_duplicate_values():
        omd = OMD([('a', 1), ('a', 2), ('b', 3)])
    
        shallow = copy.copy(omd)
>       assert shallow == omd
E       AssertionError: assert OrderedMultiD...2), ('b', 3)]) == OrderedMultiD...2), ('b', 3)])
E         
E         Omitting 2 identical items, use -vv to show
E         Use -v to get more diff

tests/test_regressgen_candidate.py:10: AssertionError
_________________ test_omd_deepcopy_preserves_duplicate_values _________________

    def test_omd_deepcopy_preserves_duplicate_values():
        omd = OMD([('a', 1), ('a', 2), ('b', 3)])
    
        deep = copy.deepcopy(omd)
>       assert deep == omd
E       AssertionError: assert OrderedMultiD...2), ('b', 3)]) == OrderedMultiD...2), ('b', 3)])
E         
E         Omitting 2 identical items, use -vv to show
E         Use -v to get more diff

tests/test_regressgen_candidate.py:20: AssertionError
=========================== short test summary info ============================
FAILED tests/test_regressgen_candidate.py::test_omd_copy_preserves_duplicate_values
FAILED tests/test_regressgen_candidate.py::test_omd_deepcopy_preserves_duplicate_values
2 failed in 0.08s
```

### Against `fixed/` — exit 0 (must be zero)

```
..                                                                       [100%]
2 passed in 0.07s
```

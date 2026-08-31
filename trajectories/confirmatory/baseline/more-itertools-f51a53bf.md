# Trajectory — `baseline` on `more-itertools-f51a53bf`

**Verdict: REPRO**  (fails on buggy, passes on fixed — reproduces the bug)

- cost `$0.07026` · wall `5.5s` · tool calls `0`

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
`interleave_evenly` blows up when given an empty list of iterables, instead of just returning an empty result.

```python
import more_itertools as mi

list(mi.interleave_evenly([]))
# also:
list(mi.interleave_evenly([], lengths=[]))
```

Both raise an exception (IndexError-ish, coming from somewhere inside the length/permutation handling) instead of returning `[]`. I'd expect calling this with an empty input to just produce an empty iterator, same as most other itertools-style functions handle degenerate/empty inputs gracefully. Since `lengths` also defaults sensibly to matching the number of iterables, I'd think zero iterables should be a trivial, valid case rather than an error condition. Ran into this while looping over a dynamically built list of sources that happened to be empty in one branch.
```

## 3. Tool calls

_No tools — this system answers in a single prompt._

## 4. Submitted test

```python
"""Regression test for interleave_evenly with empty input.

Bug: `interleave_evenly([])` (and with `lengths=[]`) raises an exception
instead of returning an empty iterator, as expected for a trivial/degenerate
case of zero iterables.
"""

import more_itertools as mi


def test_interleave_evenly_empty_no_lengths():
    result = list(mi.interleave_evenly([]))
    assert result == []


def test_interleave_evenly_empty_with_lengths():
    result = list(mi.interleave_evenly([], lengths=[]))
    assert result == []
```

## 5. Two-sided gate

### Against `buggy/` — exit 1 (must be non-zero)

```
long an axis)
>       delta_primary, deltas_secondary = lengths_desc[0], lengths_desc[1:]
                                          ^^^^^^^^^^^^^^^
E       IndexError: list index out of range

more_itertools/more.py:1350: IndexError
__________________ test_interleave_evenly_empty_with_lengths ___________________

    def test_interleave_evenly_empty_with_lengths():
>       result = list(mi.interleave_evenly([], lengths=[]))
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_regressgen_candidate.py:17: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

iterables = [], lengths = []

    def interleave_evenly(iterables, lengths=None):
        """
        Interleave multiple iterables so that their elements are evenly distributed
        throughout the output sequence.
    
        >>> iterables = [1, 2, 3, 4, 5], ['a', 'b']
        >>> list(interleave_evenly(iterables))
        [1, 2, 'a', 3, 4, 'b', 5]
    
        >>> iterables = [[1, 2, 3], [4, 5], [6, 7, 8]]
        >>> list(interleave_evenly(iterables))
        [1, 6, 4, 2, 7, 3, 8, 5]
    
        This function requires iterables of known length. Iterables without
        ``__len__()`` can be used by manually specifying lengths with *lengths*:
    
        >>> from itertools import combinations, repeat
        >>> iterables = [combinations(range(4), 2), ['a', 'b', 'c']]
        >>> lengths = [4 * (4 - 1) // 2, 3]
        >>> list(interleave_evenly(iterables, lengths=lengths))
        [(0, 1), (0, 2), 'a', (0, 3), (1, 2), 'b', (1, 3), (2, 3), 'c']
    
        Based on Bresenham's algorithm.
        """
        if lengths is None:
            try:
                lengths = [len(it) for it in iterables]
            except TypeError:
                raise ValueError(
                    'Iterable lengths could not be determined automatically. '
                    'Specify them with the lengths keyword.'
                )
        elif len(iterables) != len(lengths):
            raise ValueError('Mismatching number of iterables and lengths.')
    
        dims = len(lengths)
    
        # sort iterables by length, descending
        lengths_permute = sorted(
 
... [800 more chars]
```

### Against `fixed/` — exit 0 (must be zero)

```
..                                                                       [100%]
2 passed in 0.08s
```

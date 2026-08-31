# Trajectory — `baseline` on `more-itertools-0e6acdf9`

**Verdict: VACUOUS**

- cost `$0.32462` · wall `6.1s` · tool calls `0`

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
Passing a negative `n` to `chunked()` doesn't give a helpful error. Instead of telling me the argument is invalid, it blows up with a confusing internal error about `islice()` arguments, which makes it look like something is broken inside the library rather than me just passing a bad value.

```python
import more_itertools as mi

list(mi.chunked('ABCDE', -1))
```

This raises:

```
ValueError: Stop argument for islice() must be None or an integer: 0 <= x <= sys.maxsize.
```

I'd expect a straightforward `ValueError` telling me that `n` needs to be non-negative, similar to how `sliced()` handles this case. Right now the error message doesn't mention `chunked` or `n` at all, so it's not obvious what I did wrong unless you already know how the function is implemented.
```

## 3. Tool calls

_No tools — this system answers in a single prompt._

## 4. Submitted test

```python
import pytest

import more_itertools as mi


def test_chunked_negative_n_raises_value_error():
    """Passing a negative n to chunked() should raise a clear ValueError,
    similar to how sliced() handles this case, instead of an obscure
    internal error from islice()."""
    with pytest.raises(ValueError):
        list(mi.chunked('ABCDE', -1))
```

## 5. Two-sided gate

### Against `buggy/` — exit 0 (must be non-zero)

```
.                                                                        [100%]
1 passed in 0.40s
```

### Against `fixed/` — exit 0 (must be zero)

```
.                                                                        [100%]
1 passed in 0.40s
```

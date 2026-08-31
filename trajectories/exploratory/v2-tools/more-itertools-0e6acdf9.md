# Trajectory — `v2-tools` on `more-itertools-0e6acdf9`

**Verdict: REPRO**  (fails on buggy, passes on fixed — reproduces the bug)

- cost `$0.10117` · wall `25.7s` · tool calls `5`

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

Call `submit_test` exactly once with the complete test file when you are done.
The file must be self-contained and importable: include every import it needs.
Keep it focused — test this one bug, not the module in general.
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

### 1. `search_code`(pattern="def chunked")

Tool responded:

```
2 hits
```

### 2. `search_code`(pattern="def sliced")

Tool responded:

```
1 hits
```

### 3. `read_file`(path="more_itertools/more.py", start=200, end=260)

Tool responded:

```
2217 chars
```

### 4. `read_file`(path="more_itertools/more.py", start=1517, end=1550)

Tool responded:

```
1323 chars
```

### 5. `submit_test`(rationale="The bug report states that chunked() with a negative n should raise a clear ValueError about the invalid n ar)

Tool responded:

```
submitted
```

## 4. Submitted test

```python
import pytest

import more_itertools as mi


def test_chunked_negative_n_raises_value_error():
    """chunked() should reject a negative n with a clear ValueError,
    the same way sliced() does, instead of letting islice() raise a
    confusing internal error.
    """
    with pytest.raises(ValueError):
        list(mi.chunked('ABCDE', -1))


def test_chunked_negative_n_error_message_is_informative():
    """The ValueError message should actually mention that n is invalid,
    not leak an internal islice() error about stop arguments.
    """
    with pytest.raises(ValueError) as exc_info:
        list(mi.chunked('ABCDE', -1))

    message = str(exc_info.value)
    # The buggy behavior raises a message like:
    #   "Stop argument for islice() must be None or an integer: ..."
    # which never mentions islice, and instead should be about n being
    # invalid (mirroring sliced()'s "n must be at least 0").
    assert 'islice' not in message.lower()
    assert 'n' in message.lower()
```

**Agent's stated rationale:**

> The bug report states that chunked() with a negative n should raise a clear ValueError about the invalid n argument (similar to sliced(), which explicitly checks `if n < 0: raise ValueError('n must be at least 0')`), rather than letting the underlying islice() call fail with an unrelated, confusing error message about islice's stop argument.

Currently, chunked() has no upfront validation of n, so `list(mi.chunked('ABCDE', -1))` raises `ValueError: Stop argument for islice() must be None or an integer: 0 <= x <= sys.maxsize.` from deep inside itertools.islice via the `take` helper. This error message does not mention 'n' or 'chunked' and instead mentions 'islice', which is the exact confusing behavior the user is reporting.

The test has two parts:
1. Confirms a ValueError is still raised (this already happens on buggy code, but is necessary context).
2. Confirms the error message is a helpful, chunked-specific message that does not reference the internal islice implementation detail and does mention 'n' (the invalid argument) — mirroring the fix that should validate n upfront like sliced() does with 'n must be at least 0'.

On the current buggy code, the second test fails because the raised message contains "islice" and does not read as an n-specific validation message. On the fixed code (which is expected to add an explicit `if n < 0: raise ValueError(...)` check mentioning n), both assertions will pass because the message will be clear, chunked-specific, and free of internal implementation details.

## 5. Two-sided gate

### Against `buggy/` — exit 1 (must be non-zero)

```
.F                                                                       [100%]
=================================== FAILURES ===================================
_____________ test_chunked_negative_n_error_message_is_informative _____________

    def test_chunked_negative_n_error_message_is_informative():
        """The ValueError message should actually mention that n is invalid,
        not leak an internal islice() error about stop arguments.
        """
        with pytest.raises(ValueError) as exc_info:
            list(mi.chunked('ABCDE', -1))
    
        message = str(exc_info.value)
        # The buggy behavior raises a message like:
        #   "Stop argument for islice() must be None or an integer: ..."
        # which never mentions islice, and instead should be about n being
        # invalid (mirroring sliced()'s "n must be at least 0").
>       assert 'islice' not in message.lower()
E       AssertionError: assert 'islice' not in 'stop argume...sys.maxsize.'
E         
E         'islice' is contained here:
E           stop argument for islice() must be none or an integer: 0 <= x <= sys.maxsize.
E         ?                   ++++++

tests/test_regressgen_candidate.py:27: AssertionError
=========================== short test summary info ============================
FAILED tests/test_regressgen_candidate.py::test_chunked_negative_n_error_message_is_informative
1 failed, 1 passed in 0.51s
```

### Against `fixed/` — exit 0 (must be zero)

```
..                                                                       [100%]
2 passed in 0.42s
```

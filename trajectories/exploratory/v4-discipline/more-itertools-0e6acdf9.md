# Trajectory — `v4-discipline` on `more-itertools-0e6acdf9`

**Verdict: REPRO**  (fails on buggy, passes on fixed — reproduces the bug)

- cost `$0.3567` · wall `54.0s` · tool calls `11`

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

You have `run_test`, which runs a candidate test file against the buggy code and
returns raw pytest output. Use it before submitting. If your test passes, it does
not reproduce the bug and you must rework it.

Before you submit, verify the failure is the RIGHT failure. Read the pytest
output and confirm:

  1. It fails on an assertion about behaviour (or raises exactly the exception
     the report names). A test that fails with ImportError, AttributeError, or
     TypeError because you guessed a wrong name or signature is worthless — it
     would fail on the fixed code too, and score zero.
  2. The value you wrote as "expected" is the CORRECT value from the report, not
     the buggy value you observed in the output.
  3. The assertion actually exercises the reported condition rather than some
     unrelated edge case that happens to be broken.

If the failure is a wrong-name error, fix the name and run it again.

Call `submit_test` exactly once with the complete test file when you are done.
The file must be self-contained and importable: include every import it needs.
Keep it focused — test this one bug, not the module in gen
... [6 more chars]
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

### 3. `read_file`(path="more_itertools/more.py", start=214, end=250)

Tool responded:

```
1472 chars
```

### 4. `read_file`(path="more_itertools/more.py", start=1517, end=1545)

Tool responded:

```
1160 chars
```

### 5. `search_code`(pattern="^def take")

Tool responded:

```
2 hits
```

### 6. `read_file`(path="more_itertools/recipes.py", start=113, end=125)

Tool responded:

```
416 chars
```

### 7. `search_code`(pattern="chunked.*-1|n must be at least 0|negative")

Tool responded:

```
52 hits
```

### 8. `read_file`(path="more_itertools/recipes.py", start=113, end=160)

Tool responded:

```
1499 chars
```

### 9. `search_code`(pattern="n must not be negative|n must be non-negative|n must be at least 0|n must be positive")

Tool responded:

```
2 hits
```

### 10. `run_test`(test_source="\nimport pytest\nimport more_itertools as mi\n\n\ndef test_chunked_negative_n_raises_clear_value_error():\n  )

Tool responded:

```
FAILED (exit 1)
```

### 11. `submit_test`(rationale="The bug report states that chunked() with a negative n leaks an internal ValueError from itertools.islice() ()

Tool responded:

```
submitted
```

## 4. Submitted test

```python
import pytest
import more_itertools as mi


def test_chunked_negative_n_raises_clear_value_error():
    """
    Regression test for: passing a negative n to chunked() should raise a
    clear ValueError about the bad argument (similar to sliced()), not an
    internal error leaking from itertools.islice().
    """
    with pytest.raises(ValueError) as exc_info:
        list(mi.chunked('ABCDE', -1))

    message = str(exc_info.value)

    # The error should be a clear, user-facing message about the invalid
    # argument, not an internal implementation detail leaking from
    # itertools.islice() (e.g. "Stop argument for islice() must be None or
    # an integer: 0 <= x <= sys.maxsize.").
    assert 'islice' not in message
    # The message should actually mention the offending argument.
    assert 'n' in message
```

**Agent's stated rationale:**

> The bug report states that chunked() with a negative n leaks an internal ValueError from itertools.islice() ("Stop argument for islice() must be None or an integer: 0 <= x <= sys.maxsize.") instead of raising a clear, user-facing ValueError about the invalid n argument, as sliced() does (which raises ValueError('n must be at least 0')). 

The test calls list(mi.chunked('ABCDE', -1)) and asserts that a ValueError is raised whose message does not reference the internal 'islice' implementation detail and does mention 'n' (the offending parameter). On the current buggy code, the raised message is the raw islice error containing 'islice', so the 'islice' not in message assertion fails, correctly reproducing the bug. Once fixed to validate n explicitly (mirroring sliced()'s explicit check and message), the raised ValueError will be a clean, descriptive message that does not mention 'islice' and does mention 'n', so the test will pass.

## 5. Two-sided gate

### Against `buggy/` — exit 1 (must be non-zero)

```
F                                                                        [100%]
=================================== FAILURES ===================================
_______________ test_chunked_negative_n_raises_clear_value_error _______________

    def test_chunked_negative_n_raises_clear_value_error():
        """
        Regression test for: passing a negative n to chunked() should raise a
        clear ValueError about the bad argument (similar to sliced()), not an
        internal error leaking from itertools.islice().
        """
        with pytest.raises(ValueError) as exc_info:
            list(mi.chunked('ABCDE', -1))
    
        message = str(exc_info.value)
    
        # The error should be a clear, user-facing message about the invalid
        # argument, not an internal implementation detail leaking from
        # itertools.islice() (e.g. "Stop argument for islice() must be None or
        # an integer: 0 <= x <= sys.maxsize.").
>       assert 'islice' not in message
E       AssertionError: assert 'islice' not in 'Stop argume...sys.maxsize.'
E         
E         'islice' is contained here:
E           Stop argument for islice() must be None or an integer: 0 <= x <= sys.maxsize.
E         ?                   ++++++

tests/test_regressgen_candidate.py:20: AssertionError
=========================== short test summary info ============================
FAILED tests/test_regressgen_candidate.py::test_chunked_negative_n_raises_clear_value_error
1 failed in 0.39s
```

### Against `fixed/` — exit 0 (must be zero)

```
.                                                                        [100%]
1 passed in 0.37s
```

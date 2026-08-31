# Trajectory — `baseline` on `cachetools-d3598664`

**Verdict: REPRO**  (fails on buggy, passes on fixed — reproduces the bug)

- cost `$0.00693` · wall `6.6s` · tool calls `0`

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
`cachetools.func.mru_cache` doesn't warn that it's deprecated, unlike some of the other decorators in that module which do print a `DeprecationWarning` when used. Since MRU caching seems like it's on its way out (or at least discouraged), I'd expect using it to at least give a heads up so people can migrate away from it, similar to how other soon-to-be-removed things behave.

Repro:

```python
import warnings
import cachetools.func

with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    cached = cachetools.func.mru_cache(maxsize=2)(lambda n: n)

print(w)  # expected at least one DeprecationWarning, got an empty list
```

Nothing is printed/captured, `w` stays empty. I expected calling `mru_cache` to raise a `DeprecationWarning` so tooling and users get notified before it's eventually removed, but instead it silently behaves like a normal supported decorator with no indication anything is off.
```

## 3. Tool calls

_No tools — this system answers in a single prompt._

## 4. Submitted test

```python
"""Regression test for cachetools.func.mru_cache deprecation warning."""

import warnings

import cachetools.func


def test_mru_cache_emits_deprecation_warning():
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        cachetools.func.mru_cache(maxsize=2)(lambda n: n)

    assert len(w) >= 1, "expected at least one warning to be raised"
    assert any(issubclass(warning.category, DeprecationWarning) for warning in w), (
        "expected a DeprecationWarning to be raised when using mru_cache"
    )


def test_mru_cache_deprecation_warning_when_used_as_direct_decorator():
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")

        @cachetools.func.mru_cache
        def func(n):
            return n

    assert len(w) >= 1, "expected at least one warning to be raised"
    assert any(issubclass(warning.category, DeprecationWarning) for warning in w), (
        "expected a DeprecationWarning to be raised when using mru_cache"
    )
```

## 5. Two-sided gate

### Against `buggy/` — exit 1 (must be non-zero)

```
FF                                                                       [100%]
=================================== FAILURES ===================================
___________________ test_mru_cache_emits_deprecation_warning ___________________

    def test_mru_cache_emits_deprecation_warning():
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            cachetools.func.mru_cache(maxsize=2)(lambda n: n)
    
>       assert len(w) >= 1, "expected at least one warning to be raised"
E       AssertionError: expected at least one warning to be raised
E       assert 0 >= 1
E        +  where 0 = len([])

tests/test_regressgen_candidate.py:13: AssertionError
_______ test_mru_cache_deprecation_warning_when_used_as_direct_decorator _______

    def test_mru_cache_deprecation_warning_when_used_as_direct_decorator():
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
    
            @cachetools.func.mru_cache
            def func(n):
                return n
    
>       assert len(w) >= 1, "expected at least one warning to be raised"
E       AssertionError: expected at least one warning to be raised
E       assert 0 >= 1
E        +  where 0 = len([])

tests/test_regressgen_candidate.py:27: AssertionError
=========================== short test summary info ============================
FAILED tests/test_regressgen_candidate.py::test_mru_cache_emits_deprecation_warning
FAILED tests/test_regressgen_candidate.py::test_mru_cache_deprecation_warning_when_used_as_direct_decorator
2 failed in 0.08s
```

### Against `fixed/` — exit 0 (must be zero)

```
..                                                                       [100%]
2 passed in 0.07s
```

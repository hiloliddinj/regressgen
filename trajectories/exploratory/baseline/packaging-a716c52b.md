# Trajectory — `baseline` on `packaging-a716c52b`

**Verdict: WRONG_EXPECTATION**

- cost `$0.06282` · wall `7.4s` · tool calls `0`

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
When `dynamic` in metadata includes a disallowed field like `name`, `version`, or `metadata-version`, accessing `.dynamic` raises `InvalidMetadata`, but the error message prints the whole list instead of telling me which field was actually the problem.

```python
from packaging import metadata

meta = metadata.Metadata.from_raw({"dynamic": ["name"]}, validate=False)
meta.dynamic
```

This raises something like:

```
packaging.metadata.InvalidMetadata: ['name'] is not allowed as a dynamic field
```

If `dynamic` has more than one entry, it's not obvious which one triggered the error just from reading the message - I have to go figure it out myself. I'd expect the error to name the specific offending field (e.g. `'name' is not allowed as a dynamic field`), not dump the whole list back at me. Minor, but it makes debugging metadata files with several dynamic fields more annoying than it needs to be.
```

## 3. Tool calls

_No tools — this system answers in a single prompt._

## 4. Submitted test

```python
"""Regression test for InvalidMetadata error message on disallowed dynamic fields.

The error message should name the specific offending field (e.g. 'name'),
not dump the entire dynamic list back at the user.
"""
import pytest

from packaging import metadata


def test_dynamic_error_names_offending_field_only():
    meta = metadata.Metadata.from_raw(
        {"dynamic": ["classifiers", "name", "keywords"]}, validate=False
    )
    with pytest.raises(metadata.InvalidMetadata) as exc_info:
        meta.dynamic

    message = str(exc_info.value)
    # The message should reference the single offending field, not the whole list.
    assert "'name'" in message
    assert "['classifiers', 'name', 'keywords']" not in message


def test_dynamic_error_single_field_message():
    meta = metadata.Metadata.from_raw({"dynamic": ["version"]}, validate=False)
    with pytest.raises(metadata.InvalidMetadata) as exc_info:
        meta.dynamic

    message = str(exc_info.value)
    assert message == "'version' is not allowed as a dynamic field"
```

## 5. Two-sided gate

### Against `buggy/` — exit 1 (must be non-zero)

```
FF                                                                       [100%]
=================================== FAILURES ===================================
________________ test_dynamic_error_names_offending_field_only _________________

    def test_dynamic_error_names_offending_field_only():
        meta = metadata.Metadata.from_raw(
            {"dynamic": ["classifiers", "name", "keywords"]}, validate=False
        )
        with pytest.raises(metadata.InvalidMetadata) as exc_info:
            meta.dynamic
    
        message = str(exc_info.value)
        # The message should reference the single offending field, not the whole list.
        assert "'name'" in message
>       assert "['classifiers', 'name', 'keywords']" not in message
E       assert "['classifie... 'keywords']" not in "['classifie...ynamic field"
E         
E         "['classifiers', 'name', 'keywords']" is contained here:
E           ['classifiers', 'name', 'keywords'] is not a valid dynamic field

tests/test_regressgen_candidate.py:21: AssertionError
___________________ test_dynamic_error_single_field_message ____________________

    def test_dynamic_error_single_field_message():
        meta = metadata.Metadata.from_raw({"dynamic": ["version"]}, validate=False)
        with pytest.raises(metadata.InvalidMetadata) as exc_info:
            meta.dynamic
    
        message = str(exc_info.value)
>       assert message == "'version' is not allowed as a dynamic field"
E       assert "['version'] ...dynamic field" == "'version' is...dynamic field"
E         
E         - 'version' is not allowed as a dynamic field
E         + ['version'] is not allowed as a dynamic field
E         ? +         +

tests/test_regressgen_candidate.py:30: AssertionError
=========================== short test summary info ============================
FAILED tests/test_regressgen_candidate.py::test_dynamic_error_names_offending_field_only
FAILED tests/test_regressgen_candidate.py::test_dynamic_error_single_field_message
2 failed in 0.42s
```

### Against `fixed/` — exit 1 (must be zero)

```
F.                                                                       [100%]
=================================== FAILURES ===================================
________________ test_dynamic_error_names_offending_field_only _________________

    def test_dynamic_error_names_offending_field_only():
        meta = metadata.Metadata.from_raw(
            {"dynamic": ["classifiers", "name", "keywords"]}, validate=False
        )
        with pytest.raises(metadata.InvalidMetadata) as exc_info:
            meta.dynamic
    
        message = str(exc_info.value)
        # The message should reference the single offending field, not the whole list.
>       assert "'name'" in message
E       assert "'name'" in "'classifiers' is not a valid dynamic field"

tests/test_regressgen_candidate.py:20: AssertionError
=========================== short test summary info ============================
FAILED tests/test_regressgen_candidate.py::test_dynamic_error_names_offending_field_only
1 failed, 1 passed in 0.42s
```

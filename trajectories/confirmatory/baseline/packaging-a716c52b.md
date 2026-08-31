# Trajectory — `baseline` on `packaging-a716c52b`

**Verdict: REPRO**  (fails on buggy, passes on fixed — reproduces the bug)

- cost `$0.01785` · wall `7.1s` · tool calls `0`

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
"""Regression test for InvalidMetadata error message on invalid dynamic field.

The bug: when `dynamic` contains a disallowed field (e.g. "name", "version",
"metadata-version"), the raised InvalidMetadata error message dumps the whole
list of dynamic fields instead of naming just the offending field.
"""

import pytest

from packaging import metadata


def test_dynamic_disallowed_field_names_offender_not_whole_list():
    meta = metadata.Metadata.from_raw({"dynamic": ["name"]}, validate=False)

    with pytest.raises(metadata.InvalidMetadata) as exc_info:
        meta.dynamic

    message = str(exc_info.value)

    # The message should identify the specific offending field.
    assert "'name'" in message
    assert "is not allowed as a dynamic field" in message

    # The message should NOT dump the whole list representation.
    assert "['name']" not in message


def test_dynamic_disallowed_field_among_multiple_names_offender():
    meta = metadata.Metadata.from_raw(
        {"dynamic": ["keywords", "version", "summary"]}, validate=False
    )

    with pytest.raises(metadata.InvalidMetadata) as exc_info:
        meta.dynamic

    message = str(exc_info.value)

    # Should call out the specific offending entry, "version".
    assert "'version'" in message
    assert "is not allowed as a dynamic field" in message

    # Should not include the whole list in the error message.
    assert "['keywords', 'version', 'summary']" not in message
```

## 5. Two-sided gate

### Against `buggy/` — exit 1 (must be non-zero)

```
FF                                                                       [100%]
=================================== FAILURES ===================================
_________ test_dynamic_disallowed_field_names_offender_not_whole_list __________

    def test_dynamic_disallowed_field_names_offender_not_whole_list():
        meta = metadata.Metadata.from_raw({"dynamic": ["name"]}, validate=False)
    
        with pytest.raises(metadata.InvalidMetadata) as exc_info:
            meta.dynamic
    
        message = str(exc_info.value)
    
        # The message should identify the specific offending field.
        assert "'name'" in message
        assert "is not allowed as a dynamic field" in message
    
        # The message should NOT dump the whole list representation.
>       assert "['name']" not in message
E       assert "['name']" not in "['name'] is...ynamic field"
E         
E         "['name']" is contained here:
E           ['name'] is not allowed as a dynamic field
E         ? ++++++++

tests/test_regressgen_candidate.py:26: AssertionError
_________ test_dynamic_disallowed_field_among_multiple_names_offender __________

    def test_dynamic_disallowed_field_among_multiple_names_offender():
        meta = metadata.Metadata.from_raw(
            {"dynamic": ["keywords", "version", "summary"]}, validate=False
        )
    
        with pytest.raises(metadata.InvalidMetadata) as exc_info:
            meta.dynamic
    
        message = str(exc_info.value)
    
        # Should call out the specific offending entry, "version".
        assert "'version'" in message
        assert "is not allowed as a dynamic field" in message
    
        # Should not include the whole list in the error message.
>       assert "['keywords', 'version', 'summary']" not in message
E       assert "['keywords'..., 'summary']" not in "['keywords'...ynamic field"
E         
E         "['keywords', 'version', 'summary']" is contained here:
E           ['keywords', 'version', 'summary'] is not allowed as a dynamic field

tests/test_regressgen_candidate.py:44: AssertionError
=========================== short test summary info ============================
FAILED tests/test_regressgen_can
... [192 more chars]
```

### Against `fixed/` — exit 0 (must be zero)

```
..                                                                       [100%]
2 passed in 0.10s
```

# Trajectory — `v2-tools` on `packaging-a716c52b`

**Verdict: REPRO**  (fails on buggy, passes on fixed — reproduces the bug)

- cost `$0.12289` · wall `25.1s` · tool calls `5`

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

### 1. `search_code`(pattern="is not allowed as a dynamic field")

Tool responded:

```
1 hits
```

### 2. `read_file`(path="src/packaging/metadata.py", start=570, end=600)

Tool responded:

```
1586 chars
```

### 3. `search_code`(pattern="_invalid_metadata|class InvalidMetadata")

Tool responded:

```
17 hits
```

### 4. `read_file`(path="src/packaging/metadata.py", start=505, end=525)

Tool responded:

```
926 chars
```

### 5. `submit_test`(rationale="The bug is in Metadata._process_dynamic (src/packaging/metadata.py), which raises InvalidMetadata using f\"{v)

Tool responded:

```
submitted
```

## 4. Submitted test

```python
"""
Regression test for: InvalidMetadata error message for a disallowed
``dynamic`` field should name the specific offending field, not the
entire list of dynamic fields.

Bug report summary:
    metadata.Metadata.from_raw({"dynamic": ["name"]}, validate=False).dynamic
raises InvalidMetadata with a message like:
    "['name'] is not allowed as a dynamic field"
instead of:
    "'name' is not allowed as a dynamic field"

This is especially confusing when there are multiple dynamic fields,
since the whole list is printed regardless of which entry actually
triggered the error.
"""
import pytest

from packaging import metadata


def test_dynamic_error_names_offending_field_not_whole_list():
    # Only "version" is disallowed here; "keywords" is a perfectly valid
    # dynamic field. The error message must call out "version"
    # specifically, not print the entire ["keywords", "version"] list.
    meta = metadata.Metadata.from_raw(
        {"dynamic": ["keywords", "version"]}, validate=False
    )

    with pytest.raises(metadata.InvalidMetadata) as exc_info:
        meta.dynamic

    message = str(exc_info.value)

    # The message should mention the specific bad field ...
    assert "'version'" in message
    # ... and should NOT dump the whole raw list into the message.
    assert "['keywords', 'version']" not in message
    assert "keywords" not in message


def test_dynamic_error_single_field_matches_expected_format():
    # Sanity check on the exact wording the report expects for a
    # single-entry case: the field name alone, not a list repr.
    meta = metadata.Metadata.from_raw({"dynamic": ["name"]}, validate=False)

    with pytest.raises(metadata.InvalidMetadata) as exc_info:
        meta.dynamic

    message = str(exc_info.value)

    assert "'name' is not allowed as a dynamic field" in message
    assert "['name']" not in message
```

**Agent's stated rationale:**

> The bug is in Metadata._process_dynamic (src/packaging/metadata.py), which raises InvalidMetadata using f"{value!r} is not allowed as a dynamic field" -- `value` is the *entire* raw list passed for the `dynamic` field, not the individual offending entry (`dynamic_field`) that failed the `in {"name", "version", "metadata-version"}` check. This makes the error message ambiguous when there are multiple dynamic fields, as described in the bug report.

The test exercises two cases:
1. A multi-entry case where a valid field ("keywords") is mixed with an invalid one ("version"). On the buggy code the message contains the whole list repr (`['keywords', 'version']`) including the unrelated valid field name "keywords", which the fix should eliminate -- the message should mention only the true offending field ("version").
2. A single-entry case that pins down the exact expected message format from the report: `'name' is not allowed as a dynamic field`, asserting it is not the list repr `['name']`.

On the current buggy implementation, both assertions about not containing the list repr / containing only the specific field name fail, since the code interpolates `value` (the whole list) rather than `dynamic_field` (the specific entry). Once fixed to reference the individual field, both tests will pass.

## 5. Two-sided gate

### Against `buggy/` — exit 1 (must be non-zero)

```
FF                                                                       [100%]
=================================== FAILURES ===================================
___________ test_dynamic_error_names_offending_field_not_whole_list ____________

    def test_dynamic_error_names_offending_field_not_whole_list():
        # Only "version" is disallowed here; "keywords" is a perfectly valid
        # dynamic field. The error message must call out "version"
        # specifically, not print the entire ["keywords", "version"] list.
        meta = metadata.Metadata.from_raw(
            {"dynamic": ["keywords", "version"]}, validate=False
        )
    
        with pytest.raises(metadata.InvalidMetadata) as exc_info:
            meta.dynamic
    
        message = str(exc_info.value)
    
        # The message should mention the specific bad field ...
        assert "'version'" in message
        # ... and should NOT dump the whole raw list into the message.
>       assert "['keywords', 'version']" not in message
E       assert "['keywords', 'version']" not in "['keywords'...ynamic field"
E         
E         "['keywords', 'version']" is contained here:
E           ['keywords', 'version'] is not allowed as a dynamic field

tests/test_regressgen_candidate.py:38: AssertionError
___________ test_dynamic_error_single_field_matches_expected_format ____________

    def test_dynamic_error_single_field_matches_expected_format():
        # Sanity check on the exact wording the report expects for a
        # single-entry case: the field name alone, not a list repr.
        meta = metadata.Metadata.from_raw({"dynamic": ["name"]}, validate=False)
    
        with pytest.raises(metadata.InvalidMetadata) as exc_info:
            meta.dynamic
    
        message = str(exc_info.value)
    
>       assert "'name' is not allowed as a dynamic field" in message
E       assert "'name' is not allowed as a dynamic field" in "['name'] is not allowed as a dynamic field"

tests/test_regressgen_candidate.py:52: AssertionError
=========================== short test summary info ============================
FAILED tests/test_regressgen_candidate.py::test_dynamic_error_names_offending_field_not_wh
... [126 more chars]
```

### Against `fixed/` — exit 0 (must be zero)

```
..                                                                       [100%]
2 passed in 0.41s
```

# Trajectory — `v4-discipline` on `packaging-a716c52b`

**Verdict: REPRO**  (fails on buggy, passes on fixed — reproduces the bug)

- cost `$0.09746` · wall `21.7s` · tool calls `4`

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

### 1. `search_code`(pattern="dynamic field")

Tool responded:

```
2 hits
```

### 2. `read_file`(path="src/packaging/metadata.py", start=570, end=600)

Tool responded:

```
1586 chars
```

### 3. `run_test`(test_source="\nimport pytest\nfrom packaging import metadata\n\n\ndef test_dynamic_error_names_specific_field():\n    meta)

Tool responded:

```
FAILED (exit 1)
```

### 4. `submit_test`(rationale="The bug report states that when `dynamic` includes a disallowed field (e.g. \"name\"), the InvalidMetadata er)

Tool responded:

```
submitted
```

## 4. Submitted test

```python
import pytest

from packaging import metadata


def test_dynamic_error_names_specific_field():
    """
    When `dynamic` contains a disallowed field (name/version/metadata-version)
    alongside other valid dynamic fields, the raised InvalidMetadata message
    should name the specific offending field, not dump the entire list.
    """
    meta = metadata.Metadata.from_raw(
        {
            "metadata_version": "2.1",
            "name": "foo",
            "version": "1.0",
            "dynamic": ["summary", "name"],
        },
        validate=False,
    )

    with pytest.raises(metadata.InvalidMetadata) as exc_info:
        meta.dynamic

    message = str(exc_info.value)

    # The message should identify the specific bad field...
    assert "'name'" in message
    # ...and not just dump the whole raw list back at the user.
    assert "['summary', 'name']" not in message
```

**Agent's stated rationale:**

> The bug report states that when `dynamic` includes a disallowed field (e.g. "name"), the InvalidMetadata error message dumps the entire raw list instead of naming the specific offending field. In src/packaging/metadata.py, `_process_dynamic` uses `f"{value!r} is not allowed as a dynamic field"` (the whole input list) instead of `f"{dynamic_field!r} is not allowed as a dynamic field"` (the single bad entry). This test constructs a `dynamic` list with a valid field ("summary") plus the disallowed field ("name"), triggers the error via `.dynamic`, and asserts the message contains the specific field name 'name' and does NOT contain the full list representation. On the current buggy code this fails because the message is "['summary', 'name'] is not allowed as a dynamic field" (contains the full list, satisfying the negative assertion's failure). On fixed code, the message would be "'name' is not allowed as a dynamic field", satisfying both assertions.

## 5. Two-sided gate

### Against `buggy/` — exit 1 (must be non-zero)

```
F                                                                        [100%]
=================================== FAILURES ===================================
___________________ test_dynamic_error_names_specific_field ____________________

    def test_dynamic_error_names_specific_field():
        """
        When `dynamic` contains a disallowed field (name/version/metadata-version)
        alongside other valid dynamic fields, the raised InvalidMetadata message
        should name the specific offending field, not dump the entire list.
        """
        meta = metadata.Metadata.from_raw(
            {
                "metadata_version": "2.1",
                "name": "foo",
                "version": "1.0",
                "dynamic": ["summary", "name"],
            },
            validate=False,
        )
    
        with pytest.raises(metadata.InvalidMetadata) as exc_info:
            meta.dynamic
    
        message = str(exc_info.value)
    
        # The message should identify the specific bad field...
        assert "'name'" in message
        # ...and not just dump the whole raw list back at the user.
>       assert "['summary', 'name']" not in message
E       assert "['summary', 'name']" not in "['summary',...ynamic field"
E         
E         "['summary', 'name']" is contained here:
E           ['summary', 'name'] is not allowed as a dynamic field
E         ? +++++++++++++++++++

tests/test_regressgen_candidate.py:30: AssertionError
=========================== short test summary info ============================
FAILED tests/test_regressgen_candidate.py::test_dynamic_error_names_specific_field
1 failed in 0.41s
```

### Against `fixed/` — exit 0 (must be zero)

```
.                                                                        [100%]
1 passed in 0.39s
```

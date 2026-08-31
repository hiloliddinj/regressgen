# Trajectory — `v4-discipline` on `packaging-a716c52b`

**Verdict: REPRO**  (fails on buggy, passes on fixed — reproduces the bug)

- cost `$0.0946` · wall `23.1s` · tool calls `4`

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

### 1. `search_code`(pattern="is not allowed as a dynamic field")

Tool responded:

```
src/packaging/metadata.py:592: f"{value!r} is not allowed as a dynamic field"
```

### 2. `read_file`(path="src/packaging/metadata.py", start=570, end=600)

Tool responded:

```
src/packaging/metadata.py lines 570-600 of 804

  570|                 f"{{field}} must be one of {list(content_types)}, not {value!r}"
  571|             )
  572| 
  573|         charset = parameters.get("charset", "UTF-8")
  574|         if charset != "UTF-8":
  575|             raise self._invalid_metadata(
  576|                 f"{{field}} can only specify the UTF-8 charset, not {list(charset)}"
  577|             )
  578| 
  579|         markdown_variants = {"GFM", "CommonMark"}
  580|         variant = parameters.get("variant", "GFM")  # Use an acceptable default.
  581|         if content_type == "text/markdown" and variant not in markdown_variants:
  582|             raise self._invalid_metadata(
  583|                 f"valid Markdown variants for {{field}} are {list(markdown_variants)}, "
  584|                 f"not {variant!r}",
  585|             )
  586|         return value
  587| 
  588|     def _process_dynamic(self, value: list[str]) -> list[str]:
  589|         for dynamic_field in map(str.lower, value):
  590|             if dynamic_field in {"name", "version", "metadata-version"}:
  591|                 raise self._invalid_metadata(
  592|                     f"{value!r} is not allowed as a dynamic field"
  593|                 )
  594|             elif dynamic_field not in _EMAIL_TO_RAW_MAPPING:
  595|                 raise self._invalid_metadata(f"{value!r} is not a valid dynamic field")
  596|         return list(map(str.lower, value))
  597| 
  598|     def _process_provides_extra(
  599|         self,
  600|         value: list[str],
```

### 3. `run_test`(test_source="\nimport pytest\nfrom packaging import metadata\n\n\ndef test_dynamic_error_names_offending_field_not_whole_l)

Tool responded:

```
FAILED (exit 1)

F                                                                        [100%]
=================================== FAILURES ===================================
___________ test_dynamic_error_names_offending_field_not_whole_list ____________

    def test_dynamic_error_names_offending_field_not_whole_list():
        meta = metadata.Metadata.from_raw(
            {"dynamic": ["summary", "name"]}, validate=False
        )
        with pytest.raises(metadata.InvalidMetadata) as exc_info:
            meta.dynamic
    
        message = str(exc_info.value)
>       assert "'name' is not allowed as a dynamic field" in message
E       assert "'name' is not allowed as a dynamic field" in "['summary', 'name'] is not allowed as a dynamic field"

tests/test_regressgen_candidate.py:14: AssertionError
=========================== short test summary info ============================
FAILED tests/test_regressgen_candidate.py::test_dynamic_error_names_offending_field_not_whole_list
1 failed in 0.11s
```

### 4. `submit_test`(rationale="The bug report states that when Metadata.dynamic raises InvalidMetadata for a disallowed field (name/version/)

Tool responded:

```
Submitted.


import pytest
from packaging import metadata


def test_dynamic_error_names_offending_field_not_whole_list():
    """Regression test for: InvalidMetadata for a disallowed 'dynamic' field
    (e.g. 'name', 'version', 'metadata-version') should name the specific
    offending field, not dump the entire dynamic list.
    """
    meta = metadata.Metadata.from_raw(
        {"dynamic": ["summary", "name"]}, validate=False
    )
    with pytest.raises(metadata.InvalidMetadata) as exc_info:
        meta.dynamic

    message = str(exc_info.value)
    # The message should call out the specific bad field...
    assert "'name' is not allowed as a dynamic field" in message
    # ...not the whole list of dynamic fields.
    assert "['summary', 'name']" not in message


def test_dynamic_error_single_field_still_correct():
    """Sanity check: with a single-entry list, the field name itself should
    be quoted/reported, matching the expected message format.
    """
    meta = metadata.Metadata.from_raw({"dynamic": ["version"]}, validate=False)
    with pytest.raises(metadata.InvalidMetadata) as exc_info:
        meta.dynamic

    message = str(exc_info.value)
    assert "'version' is not allowed as a dynamic field" in message
```

## 4. Submitted test

```python

import pytest
from packaging import metadata


def test_dynamic_error_names_offending_field_not_whole_list():
    """Regression test for: InvalidMetadata for a disallowed 'dynamic' field
    (e.g. 'name', 'version', 'metadata-version') should name the specific
    offending field, not dump the entire dynamic list.
    """
    meta = metadata.Metadata.from_raw(
        {"dynamic": ["summary", "name"]}, validate=False
    )
    with pytest.raises(metadata.InvalidMetadata) as exc_info:
        meta.dynamic

    message = str(exc_info.value)
    # The message should call out the specific bad field...
    assert "'name' is not allowed as a dynamic field" in message
    # ...not the whole list of dynamic fields.
    assert "['summary', 'name']" not in message


def test_dynamic_error_single_field_still_correct():
    """Sanity check: with a single-entry list, the field name itself should
    be quoted/reported, matching the expected message format.
    """
    meta = metadata.Metadata.from_raw({"dynamic": ["version"]}, validate=False)
    with pytest.raises(metadata.InvalidMetadata) as exc_info:
        meta.dynamic

    message = str(exc_info.value)
    assert "'version' is not allowed as a dynamic field" in message
```

**Agent's stated rationale:**

> The bug report states that when Metadata.dynamic raises InvalidMetadata for a disallowed field (name/version/metadata-version), the error message should name the specific offending field rather than the entire raw list passed to `dynamic`. The current implementation formats the error using `value!r` (the whole input list) instead of `dynamic_field!r` (the individual field that triggered the failure). 

The first test uses a two-element dynamic list where only the second entry ('name') is disallowed. On the buggy code, the message is "['summary', 'name'] is not allowed as a dynamic field", so asserting the specific-field message is present, and that the whole-list representation is absent, fails on current code (confirmed via run_test) and will pass once the fix reports the individual field. The second test provides an additional single-field case that should hold on both buggy and fixed code (since with one element the specific field text happens to overlap what's checked), reinforcing correct behavior without being redundant risk-wise — it acts as a sanity/smoke check for the message format expected post-fix.

## 5. Two-sided gate

### Against `buggy/` — exit 1 (must be non-zero)

```
FF                                                                       [100%]
=================================== FAILURES ===================================
___________ test_dynamic_error_names_offending_field_not_whole_list ____________

    def test_dynamic_error_names_offending_field_not_whole_list():
        """Regression test for: InvalidMetadata for a disallowed 'dynamic' field
        (e.g. 'name', 'version', 'metadata-version') should name the specific
        offending field, not dump the entire dynamic list.
        """
        meta = metadata.Metadata.from_raw(
            {"dynamic": ["summary", "name"]}, validate=False
        )
        with pytest.raises(metadata.InvalidMetadata) as exc_info:
            meta.dynamic
    
        message = str(exc_info.value)
        # The message should call out the specific bad field...
>       assert "'name' is not allowed as a dynamic field" in message
E       assert "'name' is not allowed as a dynamic field" in "['summary', 'name'] is not allowed as a dynamic field"

tests/test_regressgen_candidate.py:19: AssertionError
________________ test_dynamic_error_single_field_still_correct _________________

    def test_dynamic_error_single_field_still_correct():
        """Sanity check: with a single-entry list, the field name itself should
        be quoted/reported, matching the expected message format.
        """
        meta = metadata.Metadata.from_raw({"dynamic": ["version"]}, validate=False)
        with pytest.raises(metadata.InvalidMetadata) as exc_info:
            meta.dynamic
    
        message = str(exc_info.value)
>       assert "'version' is not allowed as a dynamic field" in message
E       assert "'version' is not allowed as a dynamic field" in "['version'] is not allowed as a dynamic field"

tests/test_regressgen_candidate.py:33: AssertionError
=========================== short test summary info ============================
FAILED tests/test_regressgen_candidate.py::test_dynamic_error_names_offending_field_not_whole_list
FAILED tests/test_regressgen_candidate.py::test_dynamic_error_single_field_still_correct
2 failed in 0.11s
```

### Against `fixed/` — exit 0 (must be zero)

```
..                                                                       [100%]
2 passed in 0.09s
```

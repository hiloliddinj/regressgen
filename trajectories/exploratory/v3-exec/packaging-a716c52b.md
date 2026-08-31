# Trajectory — `v3-exec` on `packaging-a716c52b`

**Verdict: REPRO**  (fails on buggy, passes on fixed — reproduces the bug)

- cost `$0.171` · wall `29.6s` · tool calls `6`

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

### 3. `search_code`(pattern="def dynamic|_invalid_metadata|class Metadata")

Tool responded:

```
17 hits
```

### 4. `read_file`(path="src/packaging/metadata.py", start=505, end=525)

Tool responded:

```
926 chars
```

### 5. `run_test`(test_source="\nfrom packaging import metadata\n\n\ndef test_dynamic_invalid_field_names_specific_field_not_whole_list():\n)

Tool responded:

```
FAILED (exit 1)
```

### 6. `submit_test`(rationale="The bug: Metadata._process_dynamic() raises InvalidMetadata using f\"{value!r} is not allowed as a dynamic fi)

Tool responded:

```
submitted
```

## 4. Submitted test

```python

from packaging import metadata


def test_dynamic_invalid_field_names_specific_field_not_whole_list():
    """
    Regression test for: when `dynamic` contains a disallowed field (name,
    version, or metadata-version) among other entries, the raised
    InvalidMetadata message should name the specific offending field, not
    dump the entire `dynamic` list.
    """
    meta = metadata.Metadata.from_raw(
        {"metadata_version": "2.1", "name": "foo", "dynamic": ["license", "name"]},
        validate=False,
    )

    try:
        meta.dynamic
    except metadata.InvalidMetadata as exc:
        message = str(exc)
    else:
        raise AssertionError("expected InvalidMetadata to be raised")

    # The message should call out the specific bad field...
    assert "'name' is not allowed as a dynamic field" in message
    # ...not the whole list of dynamic fields.
    assert "['license', 'name']" not in message


def test_dynamic_invalid_metadata_version_field_reported_specifically():
    """
    Same bug, but for the `metadata-version` disallowed value, combined with
    other (valid) dynamic entries so the whole-list bug would be visible.
    """
    meta = metadata.Metadata.from_raw(
        {
            "metadata_version": "2.1",
            "name": "foo",
            "dynamic": ["keywords", "metadata-version"],
        },
        validate=False,
    )

    try:
        meta.dynamic
    except metadata.InvalidMetadata as exc:
        message = str(exc)
    else:
        raise AssertionError("expected InvalidMetadata to be raised")

    assert "'metadata-version' is not allowed as a dynamic field" in message
    assert "['keywords', 'metadata-version']" not in message
```

**Agent's stated rationale:**

> The bug: Metadata._process_dynamic() raises InvalidMetadata using f"{value!r} is not allowed as a dynamic field" where `value` is the *entire* raw `dynamic` list, instead of the single offending field name. So when `dynamic` has multiple entries and one of them is disallowed (name/version/metadata-version), the error message dumps the whole list (e.g. "['license', 'name'] is not allowed as a dynamic field") instead of pinpointing which entry was invalid (expected: "'name' is not allowed as a dynamic field").

This test constructs metadata with a multi-entry `dynamic` list containing one disallowed field, triggers the validation via the `.dynamic` property getter, and asserts that the resulting error message names the specific bad field and does not contain the full list representation. On the current buggy code this fails because the message contains the whole list rather than the single field. After the fix (using the specific `dynamic_field` in the message instead of `value`), the message will correctly single out the offending field and the test will pass.

## 5. Two-sided gate

### Against `buggy/` — exit 1 (must be non-zero)

```
FF                                                                       [100%]
=================================== FAILURES ===================================
________ test_dynamic_invalid_field_names_specific_field_not_whole_list ________

    def test_dynamic_invalid_field_names_specific_field_not_whole_list():
        """
        Regression test for: when `dynamic` contains a disallowed field (name,
        version, or metadata-version) among other entries, the raised
        InvalidMetadata message should name the specific offending field, not
        dump the entire `dynamic` list.
        """
        meta = metadata.Metadata.from_raw(
            {"metadata_version": "2.1", "name": "foo", "dynamic": ["license", "name"]},
            validate=False,
        )
    
        try:
            meta.dynamic
        except metadata.InvalidMetadata as exc:
            message = str(exc)
        else:
            raise AssertionError("expected InvalidMetadata to be raised")
    
        # The message should call out the specific bad field...
>       assert "'name' is not allowed as a dynamic field" in message
E       assert "'name' is not allowed as a dynamic field" in "['license', 'name'] is not allowed as a dynamic field"

tests/test_regressgen_candidate.py:25: AssertionError
______ test_dynamic_invalid_metadata_version_field_reported_specifically _______

    def test_dynamic_invalid_metadata_version_field_reported_specifically():
        """
        Same bug, but for the `metadata-version` disallowed value, combined with
        other (valid) dynamic entries so the whole-list bug would be visible.
        """
        meta = metadata.Metadata.from_raw(
            {
                "metadata_version": "2.1",
                "name": "foo",
                "dynamic": ["keywords", "metadata-version"],
            },
            validate=False,
        )
    
        try:
            meta.dynamic
        except metadata.InvalidMetadata as exc:
            message = str(exc)
        else:
            raise AssertionError("expected InvalidMetadata to be raised")
    
>       assert "'metadata-version' is not allowed as a dynamic field" in message
E       assert "'met
... [491 more chars]
```

### Against `fixed/` — exit 0 (must be zero)

```
..                                                                       [100%]
2 passed in 0.40s
```

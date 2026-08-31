# Trajectory — `v3-exec` on `packaging-524b701c`

**Verdict: REPRO**  (fails on buggy, passes on fixed — reproduces the bug)

- cost `$0.14206` · wall `28.2s` · tool calls `4`

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
parse_wheel_filename and parse_sdist_filename don't raise the documented exception when the filename has a bogus version string. Instead they let InvalidVersion escape from inside packaging.version, which callers aren't expecting since the docs say these functions raise InvalidWheelFilename / InvalidSdistFilename.

Repro:

```python
from packaging.utils import parse_wheel_filename, parse_sdist_filename

parse_wheel_filename("foobar-1.x-py3-none-any.whl")
# raises InvalidVersion, not InvalidWheelFilename

parse_sdist_filename("foo-1.x.tar.gz")
# raises InvalidVersion, not InvalidSdistFilename
```

I expected both calls to raise InvalidWheelFilename/InvalidSdistFilename respectively, same as other malformed-filename cases (bad extension, bad name characters, etc.), since that's what I have to catch to handle bad input gracefully. Instead I get an unrelated exception type from a different module, which means code that only catches the documented filename exceptions will crash unexpectedly on this particular kind of bad input.
```

## 3. Tool calls

### 1. `read_file`(path="src/packaging/utils.py", start=1, end=120)

Tool responded:

```
4371 chars
```

### 2. `read_file`(path="src/packaging/utils.py", start=120, end=158)

Tool responded:

```
1822 chars
```

### 3. `run_test`(test_source="\nimport pytest\n\nfrom packaging.utils import (\n    InvalidSdistFilename,\n    InvalidWheelFilename,\n    p)

Tool responded:

```
FAILED (exit 1)
```

### 4. `submit_test`(rationale="The bug report states that parse_wheel_filename and parse_sdist_filename should raise their documented except)

Tool responded:

```
submitted
```

## 4. Submitted test

```python
"""
Regression test for: parse_wheel_filename / parse_sdist_filename must raise
their documented exceptions (InvalidWheelFilename / InvalidSdistFilename)
when the filename contains a bogus PEP 440 version string, instead of letting
packaging.version.InvalidVersion escape uncaught.
"""

import pytest

from packaging.utils import (
    InvalidSdistFilename,
    InvalidWheelFilename,
    parse_sdist_filename,
    parse_wheel_filename,
)
from packaging.version import InvalidVersion


def test_parse_wheel_filename_bogus_version_raises_invalid_wheel_filename():
    # "1.x" is not a valid PEP 440 version, so this should be treated the
    # same as any other malformed wheel filename and raise
    # InvalidWheelFilename -- not the unrelated InvalidVersion.
    with pytest.raises(InvalidWheelFilename):
        parse_wheel_filename("foobar-1.x-py3-none-any.whl")


def test_parse_wheel_filename_bogus_version_does_not_leak_invalid_version():
    try:
        parse_wheel_filename("foobar-1.x-py3-none-any.whl")
    except InvalidWheelFilename:
        pass
    except InvalidVersion:
        pytest.fail(
            "parse_wheel_filename leaked InvalidVersion instead of raising "
            "InvalidWheelFilename"
        )


def test_parse_sdist_filename_bogus_version_raises_invalid_sdist_filename():
    with pytest.raises(InvalidSdistFilename):
        parse_sdist_filename("foo-1.x.tar.gz")


def test_parse_sdist_filename_bogus_version_does_not_leak_invalid_version():
    try:
        parse_sdist_filename("foo-1.x.tar.gz")
    except InvalidSdistFilename:
        pass
    except InvalidVersion:
        pytest.fail(
            "parse_sdist_filename leaked InvalidVersion instead of raising "
            "InvalidSdistFilename"
        )
```

**Agent's stated rationale:**

> The bug report states that parse_wheel_filename and parse_sdist_filename should raise their documented exceptions (InvalidWheelFilename / InvalidSdistFilename respectively) for any malformed filename, including one with a bogus PEP 440 version segment, but instead let packaging.version.InvalidVersion escape uncaught. I verified via read_file that both functions call Version(...) directly without catching InvalidVersion. The test exercises the exact repro from the report for both functions, asserting the documented exception type is raised (pytest.raises), and additionally guards against InvalidVersion leaking through un-caught. I confirmed with run_test that both assertions fail against the current buggy code (they raise packaging.version.InvalidVersion instead of the expected filename-specific exceptions), and they will pass once the fix wraps the Version(...) calls to translate InvalidVersion into the appropriate InvalidWheelFilename/InvalidSdistFilename.

## 5. Two-sided gate

### Against `buggy/` — exit 1 (must be non-zero)

```
it into pieces
        match = self._regex.search(version)
        if not match:
>           raise InvalidVersion(f"Invalid version: '{version}'")
E           packaging.version.InvalidVersion: Invalid version: '1.x'

<sandbox>:200: InvalidVersion
____ test_parse_sdist_filename_bogus_version_does_not_leak_invalid_version _____

    def test_parse_sdist_filename_bogus_version_does_not_leak_invalid_version():
        try:
>           parse_sdist_filename("foo-1.x.tar.gz")

tests/test_regressgen_candidate.py:46: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
<sandbox>:157: in parse_sdist_filename
    version = Version(version_part)
              ^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <[AttributeError("'Version' object has no attribute '_version'") raised in repr()] Version object at 0x10ab53da0>
version = '1.x'

    def __init__(self, version: str) -> None:
        """Initialize a Version object.
    
        :param version:
            The string representation of a version which will be parsed and normalized
            before use.
        :raises InvalidVersion:
            If the ``version`` does not conform to PEP 440 in any way then this
            exception will be raised.
        """
    
        # Validate the version and parse it into pieces
        match = self._regex.search(version)
        if not match:
>           raise InvalidVersion(f"Invalid version: '{version}'")
E           packaging.version.InvalidVersion: Invalid version: '1.x'

<sandbox>:200: InvalidVersion

During handling of the above exception, another exception occurred:

    def test_parse_sdist_filename_bogus_version_does_not_leak_invalid_version():
        try:
            parse_sdist_filename("foo-1.x.tar.gz")
        except InvalidSdistFilename:
            pass
        except InvalidVersion:
>           pytest.fail(
                "parse_sdist_filename leaked InvalidVersion instead of raising "
                "InvalidSdistFilename"
            )
E           Failed: parse_sdist_filename leaked InvalidVersion instead of raising InvalidSdistFilename

tests/test_regressgen_candida
... [568 more chars]
```

### Against `fixed/` — exit 0 (must be zero)

```
....                                                                     [100%]
4 passed in 0.38s
```

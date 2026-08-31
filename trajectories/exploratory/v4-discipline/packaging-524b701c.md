# Trajectory — `v4-discipline` on `packaging-524b701c`

**Verdict: REPRO**  (fails on buggy, passes on fixed — reproduces the bug)

- cost `$0.09855` · wall `19.0s` · tool calls `3`

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

### 1. `read_file`(path="src/packaging/utils.py", start=0, end=0)

Tool responded:

```
6037 chars
```

### 2. `run_test`(test_source="\nimport pytest\nfrom packaging.utils import (\n    parse_wheel_filename,\n    parse_sdist_filename,\n    Inv)

Tool responded:

```
FAILED (exit 1)
```

### 3. `submit_test`(rationale="The bug report states that parse_wheel_filename and parse_sdist_filename should raise their documented except)

Tool responded:

```
submitted
```

## 4. Submitted test

```python
import pytest
from packaging.utils import (
    parse_wheel_filename,
    parse_sdist_filename,
    InvalidWheelFilename,
    InvalidSdistFilename,
)


def test_parse_wheel_filename_bogus_version_raises_invalid_wheel_filename():
    # A wheel filename with a bogus (non-PEP-440) version string should
    # raise the documented InvalidWheelFilename exception, not let
    # packaging.version.InvalidVersion escape.
    with pytest.raises(InvalidWheelFilename):
        parse_wheel_filename("foobar-1.x-py3-none-any.whl")


def test_parse_sdist_filename_bogus_version_raises_invalid_sdist_filename():
    # An sdist filename with a bogus (non-PEP-440) version string should
    # raise the documented InvalidSdistFilename exception, not let
    # packaging.version.InvalidVersion escape.
    with pytest.raises(InvalidSdistFilename):
        parse_sdist_filename("foo-1.x.tar.gz")
```

**Agent's stated rationale:**

> The bug report states that parse_wheel_filename and parse_sdist_filename should raise their documented exceptions (InvalidWheelFilename / InvalidSdistFilename) when given a filename containing a malformed version string, but instead the current implementation lets packaging.version.InvalidVersion escape unhandled since it calls Version(...) directly without catching InvalidVersion. This test calls both functions with filenames that have valid structure/extension but an invalid PEP 440 version segment ("1.x"), and asserts the documented exception type is raised. On the buggy code, this fails because InvalidVersion (not InvalidWheelFilename/InvalidSdistFilename) propagates out, confirmed by running the test. On a fixed implementation that wraps the Version(...) call and re-raises the appropriate documented exception, the test will pass.

## 5. Two-sided gate

### Against `buggy/` — exit 1 (must be non-zero)

```
 _ _ _ _ _ _ _ _ _ _ _ _ 

self = <[AttributeError("'Version' object has no attribute '_version'") raised in repr()] Version object at 0x10b42f560>
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
____ test_parse_sdist_filename_bogus_version_raises_invalid_sdist_filename _____

    def test_parse_sdist_filename_bogus_version_raises_invalid_sdist_filename():
        # An sdist filename with a bogus (non-PEP-440) version string should
        # raise the documented InvalidSdistFilename exception, not let
        # packaging.version.InvalidVersion escape.
        with pytest.raises(InvalidSdistFilename):
>           parse_sdist_filename("foo-1.x.tar.gz")

tests/test_regressgen_candidate.py:23: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
<sandbox>:157: in parse_sdist_filename
    version = Version(version_part)
              ^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <[AttributeError("'Version' object has no attribute '_version'") raised in repr()] Version object at 0x10b440a10>
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
    
        # Validate the version and parse it i
... [568 more chars]
```

### Against `fixed/` — exit 0 (must be zero)

```
..                                                                       [100%]
2 passed in 0.38s
```

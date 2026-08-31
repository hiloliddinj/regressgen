# Trajectory — `v2-tools` on `packaging-524b701c`

**Verdict: REPRO**  (fails on buggy, passes on fixed — reproduces the bug)

- cost `$0.08595` · wall `17.9s` · tool calls `2`

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

### 1. `read_file`(path="src/packaging/utils.py", start=0, end=200)

Tool responded:

```
6080 chars
```

### 2. `submit_test`(rationale="The bug report states that parse_wheel_filename and parse_sdist_filename let InvalidVersion escape instead of)

Tool responded:

```
submitted
```

## 4. Submitted test

```python
import pytest

from packaging.utils import (
    InvalidSdistFilename,
    InvalidWheelFilename,
    parse_sdist_filename,
    parse_wheel_filename,
)


def test_parse_wheel_filename_bogus_version_raises_invalid_wheel_filename():
    # "1.x" is not a valid PEP 440 version, so Version() would raise
    # InvalidVersion internally. The documented behavior is that
    # parse_wheel_filename should raise InvalidWheelFilename for any
    # malformed wheel filename, including one with a bogus version string.
    with pytest.raises(InvalidWheelFilename):
        parse_wheel_filename("foobar-1.x-py3-none-any.whl")


def test_parse_sdist_filename_bogus_version_raises_invalid_sdist_filename():
    # Likewise, parse_sdist_filename should raise InvalidSdistFilename,
    # not let InvalidVersion escape from packaging.version.
    with pytest.raises(InvalidSdistFilename):
        parse_sdist_filename("foo-1.x.tar.gz")
```

**Agent's stated rationale:**

> The bug report states that parse_wheel_filename and parse_sdist_filename let InvalidVersion escape instead of raising the documented InvalidWheelFilename/InvalidSdistFilename exceptions when given a filename with a malformed PEP 440 version string. In the current buggy code (src/packaging/utils.py), Version(parts[1]) and Version(version_part) are called unguarded, so InvalidVersion propagates instead of being wrapped/translated. This test calls both functions with filenames containing a bogus version ("1.x") and asserts that the documented exception types are raised. On the buggy code, pytest.raises(InvalidWheelFilename) / pytest.raises(InvalidSdistFilename) will fail because an InvalidVersion (unrelated exception type) is raised instead, causing the test to fail as required. On a fixed implementation that catches InvalidVersion and re-raises as InvalidWheelFilename/InvalidSdistFilename, the test will pass.

## 5. Two-sided gate

### Against `buggy/` — exit 1 (must be non-zero)

```
^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <[AttributeError("'Version' object has no attribute '_version'") raised in repr()] Version object at 0x1074d0290>
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
        # Likewise, parse_sdist_filename should raise InvalidSdistFilename,
        # not let InvalidVersion escape from packaging.version.
        with pytest.raises(InvalidSdistFilename):
>           parse_sdist_filename("foo-1.x.tar.gz")

tests/test_regressgen_candidate.py:24: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
<sandbox>:157: in parse_sdist_filename
    version = Version(version_part)
              ^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <[AttributeError("'Version' object has no attribute '_version'") raised in repr()] Version object at 0x1074e4830>
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
2 passed in 0.39s
```

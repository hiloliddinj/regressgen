# Trajectory — `baseline` on `packaging-524b701c`

**Verdict: REPRO**  (fails on buggy, passes on fixed — reproduces the bug)

- cost `$0.00969` · wall `7.2s` · tool calls `0`

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

_No tools — this system answers in a single prompt._

## 4. Submitted test

```python
"""
Regression test for: parse_wheel_filename / parse_sdist_filename should
raise InvalidWheelFilename / InvalidSdistFilename (not InvalidVersion) when
the filename contains a bogus version string.
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
    with pytest.raises(InvalidWheelFilename):
        parse_wheel_filename("foobar-1.x-py3-none-any.whl")


def test_parse_wheel_filename_bogus_version_does_not_raise_invalid_version():
    try:
        parse_wheel_filename("foobar-1.x-py3-none-any.whl")
    except InvalidVersion:
        pytest.fail(
            "parse_wheel_filename raised InvalidVersion instead of "
            "InvalidWheelFilename"
        )
    except InvalidWheelFilename:
        pass


def test_parse_sdist_filename_bogus_version_raises_invalid_sdist_filename():
    with pytest.raises(InvalidSdistFilename):
        parse_sdist_filename("foo-1.x.tar.gz")


def test_parse_sdist_filename_bogus_version_does_not_raise_invalid_version():
    try:
        parse_sdist_filename("foo-1.x.tar.gz")
    except InvalidVersion:
        pytest.fail(
            "parse_sdist_filename raised InvalidVersion instead of "
            "InvalidSdistFilename"
        )
    except InvalidSdistFilename:
        pass
```

## 5. Two-sided gate

### Against `buggy/` — exit 1 (must be non-zero)

```
g representation of a version which will be parsed and normalized
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
____ test_parse_sdist_filename_bogus_version_does_not_raise_invalid_version ____

    def test_parse_sdist_filename_bogus_version_does_not_raise_invalid_version():
        try:
>           parse_sdist_filename("foo-1.x.tar.gz")

tests/test_regressgen_candidate.py:41: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
<sandbox>:157: in parse_sdist_filename
    version = Version(version_part)
              ^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <[AttributeError("'Version' object has no attribute '_version'") raised in repr()] Version object at 0x109729220>
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

    def test_parse_sdist_filename_bogus_version_does_not_raise_invalid_version():
        try:
            parse_sdist_filename("foo-1.x.tar.gz")
        except InvalidVersion:
>           pytest.fail(
                "pars
... [800 more chars]
```

### Against `fixed/` — exit 0 (must be zero)

```
....                                                                     [100%]
4 passed in 0.07s
```

When calling `parse_wheel_filename()` or `parse_sdist_filename()` on a filename that has an invalid (non-PEP 440) version segment, I get an `InvalidVersion` exception instead of `InvalidWheelFilename` / `InvalidSdistFilename`.

```python
from packaging.utils import parse_wheel_filename, parse_sdist_filename

parse_wheel_filename("foobar-1.x-py3-none-any.whl")
# InvalidVersion: Invalid version: '1.x'

parse_sdist_filename("foo-1.x.tar.gz")
# InvalidVersion: Invalid version: '1.x'
```

Since both functions document that they raise `InvalidWheelFilename`/`InvalidSdistFilename` for malformed filenames, I expected the same to happen here — the version part being unparseable is just another way the filename is malformed, and callers who only catch the documented exception types get an unhandled `InvalidVersion` instead. I'd expect the fix to wrap the version parsing so any failure there is reported consistently as the filename-specific exception, matching how other malformed segments (bad extension, missing separators, invalid name) are already handled.

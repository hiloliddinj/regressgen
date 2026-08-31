AtomicSaver blows up if I pass a pathlib.Path instead of a plain string for the destination. Everywhere else in boltons (and in the stdlib generally) path-like objects are accepted interchangeably with strings, so I expected this to just work too.

```python
from pathlib import Path
from boltons import fileutils

dest = Path('/tmp/output.bin')
with fileutils.AtomicSaver(dest) as f:
    f.write(b'hello')
```

This raises:

```
TypeError: unsupported operand type(s) for +: 'PosixPath' and 'str'
```

Passing `str(dest)` instead works fine, so it's specifically the Path object that trips it up. I'd expect AtomicSaver to accept anything satisfying os.PathLike, same as `open()` and the rest of the os/pathlib ecosystem, instead of erroring out. Wrapping every path in `str()` before calling it feels like an unnecessary workaround for something that should just be handled.

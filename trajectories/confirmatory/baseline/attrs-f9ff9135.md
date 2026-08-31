# Trajectory — `baseline` on `attrs-f9ff9135`

**Verdict: VACUOUS**

- cost `$0.10956` · wall `112.3s` · tool calls `0`

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
On Python 3.13 the docstring of the generated "not equal" method on attrs classes doesn't match what I get on 3.12.

I noticed this while comparing the auto-generated method's docstring across Python versions (I was checking it for a doc-generation tool). On 3.12 the docstring keeps its original indentation on the second line, but on 3.13 that indentation is stripped, so a strict string comparison between the two fails.

```python
import attr

@attr.s
class C:
    x = attr.ib()

print(repr(C.__eq__.__doc__))
```

Running this on 3.12 vs 3.13 gives differently-indented docstrings for the same generated method. I expected the docstring content/formatting to be consistent between versions, or at least documented as something that can vary, since anything relying on exact docstring text (like snapshot tests) breaks silently when moving to 3.13.
```

## 3. Tool calls

_No tools — this system answers in a single prompt._

## 4. Submitted test

```python
import inspect

import attr


def test_ne_docstring_is_properly_dedented():
    """
    Regression test for the generated ``__ne__`` method's docstring having
    inconsistent leading whitespace depending on the Python version used to
    run attrs (Python 3.13's compiler strips docstring indentation while
    earlier versions keep it as written in the source, leading to a
    docstring that differs across interpreter versions for the exact same
    generated code).

    The docstring should be normalized/consistent regardless of the Python
    version, i.e. it should already be in "clean" form (as produced by
    ``inspect.cleandoc``), with no stray leading whitespace on continuation
    lines.
    """

    @attr.s
    class C:
        x = attr.ib()

    doc = C.__ne__.__doc__

    assert doc is not None
    # If the docstring still carries the raw, un-normalized indentation
    # from the source code (the buggy behavior on Python < 3.13), then
    # running it through inspect.cleandoc() would change it, since
    # cleandoc() strips common leading whitespace from continuation lines.
    # A properly normalized docstring should be unaffected by cleandoc().
    assert doc == inspect.cleandoc(doc)
```

## 5. Two-sided gate

### Against `buggy/` — exit 0 (must be non-zero)

```
.                                                                        [100%]
1 passed in 0.01s
```

### Against `fixed/` — exit 0 (must be zero)

```
.                                                                        [100%]
1 passed in 0.01s
```

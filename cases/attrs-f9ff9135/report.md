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

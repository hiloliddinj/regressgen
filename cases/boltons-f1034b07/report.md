JSONLIterator hangs forever (never returns, never raises) when a `rel_seek` value lands inside the last line of a file that doesn't end with a newline. Also ran into the same hang using a negative `rel_seek` value on a normal file - I expected negative values to seek from the end (like negative indices usually work), but instead it seems to seek past the end of the file and then just spins.

Repro:

```python
from boltons.jsonutils import JSONLIterator

with open('no_trailing_newline.jsonl', 'w') as f:
    f.write('{"1": 1}\n{"2": 2}')

it = JSONLIterator(open('no_trailing_newline.jsonl'), rel_seek=0.9)
list(it)  # never returns

# separately:
it2 = JSONLIterator(open('some.jsonl'), rel_seek=-0.5)
list(it2)  # also hangs
```

Expected either construction or iteration to complete normally (returning whatever partial/tail lines make sense), or to raise a clear error for the bad seek value - not hang indefinitely with no output and no exception.

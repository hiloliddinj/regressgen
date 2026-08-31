`JSONLIterator` hangs (infinite loop, never raises, never returns) in two situations I ran into while reading logs with `rel_seek`.

First, if the seek target lands inside the final line of a file that has no trailing newline, construction never returns:

```python
from boltons.jsonutils import JSONLIterator

with open("no_trailing_newline.jsonl", "w") as f:
    f.write('{"1": 1}\n{"2": 2}')

with open("no_trailing_newline.jsonl") as f:
    it = JSONLIterator(f, rel_seek=0.9)  # hangs forever
    list(it)
```

Second, a negative `rel_seek` also hangs instead of either working relative to EOF or raising:

```python
with open("data.jsonl") as f:
    it = JSONLIterator(f, rel_seek=-0.5)  # hangs forever
    list(it)
```

Expected: in the first case, since the seek point is past the last newline, the iterator should just terminate with no more lines to yield (returning `[]` when there's nothing after the seek). In the second case, `rel_seek=-0.5` should behave like `rel_seek=0.5` from the end (i.e. negative values normalize to a fraction from EOF), yielding the same tail of records as the equivalent positive `rel_seek`. Neither case should ever loop indefinitely.

`interleave_evenly` blows up when given an empty list of iterables, instead of just returning an empty result.

```python
import more_itertools as mi

list(mi.interleave_evenly([]))
# also:
list(mi.interleave_evenly([], lengths=[]))
```

Both raise an exception (IndexError-ish, coming from somewhere inside the length/permutation handling) instead of returning `[]`. I'd expect calling this with an empty input to just produce an empty iterator, same as most other itertools-style functions handle degenerate/empty inputs gracefully. Since `lengths` also defaults sensibly to matching the number of iterables, I'd think zero iterables should be a trivial, valid case rather than an error condition. Ran into this while looping over a dynamically built list of sources that happened to be empty in one branch.

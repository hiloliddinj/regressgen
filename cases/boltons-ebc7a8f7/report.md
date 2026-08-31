copy.copy() and copy.deepcopy() on an OrderedMultiDict silently lose duplicate values for a key. Only the last value inserted per key survives the copy.

```python
import copy
from boltons.dictutils import OrderedMultiDict as OMD

omd = OMD([('a', 1), ('a', 2), ('b', 3)])

shallow = copy.copy(omd)
print(shallow == omd)          # False, expected True
print(shallow.getlist('a'))    # [2], expected [1, 2]

deep = copy.deepcopy(omd)
print(deep.getlist('a'))       # also [2], expected [1, 2]
```

I expected copying an OMD to produce an equal OMD that preserves every value for every key, same as pickling round-trips it correctly. Instead both copy.copy and copy.deepcopy end up keeping just one value per key, as if the earlier values were overwritten. This makes copy.copy/deepcopy unsafe to use on OMD instances that have any keys with more than one value, which is kind of the whole point of using OMD in the first place.

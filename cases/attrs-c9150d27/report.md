Unpickling old pickle data of a slotted attrs class fails to properly restore the object's attributes on current attrs.

I have a bunch of pickled objects created a while ago (slotted, frozen attrs class with attributes x, b, c). Loading them with `pickle.loads` on a newer attrs version gives back an object that looks fine in isolation but is actually missing an attribute — accessing it raises AttributeError, and comparing it to a freshly-constructed equal instance blows up instead of returning True/False.

```python
import pickle
import attr

@attr.s(slots=True, frozen=True)
class A:
    x = attr.ib()
    b = attr.ib()
    c = attr.ib()

a = A(1, 2, 3)

# pickle produced by an older attrs version, loaded now:
old_pickled = b"\x80\x04\x95&\x00\x00\x00\x00\x00\x00\x00\x8c\x10__main__\x94\x8c\x01A\x94\x93\x94)\x81\x94K\x01K\x02K\x03\x87\x94b."

restored = pickle.loads(old_pickled)
restored == a  # raises AttributeError instead of comparing
```

I expected old pickles to still unpickle into fully-populated, usable objects, not ones missing one of their attributes. This only shows up with frozen slotted classes for me.

Using `tabulate` with a list of dataclass instances and a `SEPARATING_LINE` mixed in raises an error instead of producing a table. If I just use plain dicts with the same separating line, it works fine, so it seems specific to dataclass rows.

```python
from dataclasses import make_dataclass
from tabulate import tabulate, SEPARATING_LINE

Person = make_dataclass("Person", ["name", "age", "height"])
data = [Person("Alice", 23, 169.5), SEPARATING_LINE, Person("Bob", 27, 175.0)]

print(tabulate(data, headers="keys"))
```

Expected: a table with headers derived from the dataclass fields, with a separating line drawn between the two rows, similar to how it works with lists-of-dicts input.

Instead it blows up with a traceback that looks like it's trying to treat the separating line marker itself as a dataclass row and failing when checking its fields. Would expect SEPARATING_LINE to just be skipped/handled the same way regardless of the row type used elsewhere in the list.

When `dynamic` in a core metadata mapping contains a disallowed field (`name`, `version`, or `metadata-version`), accessing `Metadata.dynamic` raises `InvalidMetadata`, but the error message is not useful when there are multiple entries in the list — it just dumps the whole list instead of pointing at the offending field.

```python
from packaging import metadata

meta = metadata.Metadata.from_raw(
    {"dynamic": ["name", "summary"]}, validate=False
)
meta.dynamic
```

Result:

```
packaging.metadata.InvalidMetadata: ['name', 'summary'] is not allowed as a dynamic field
```

I expected the message to name only the specific field that isn't allowed, e.g. something like:

```
packaging.metadata.InvalidMetadata: 'name' is not allowed as a dynamic field
```

instead of echoing back the entire list, which is confusing when `dynamic` has several entries and you have to guess which one triggered the error. `InvalidMetadata` is the right exception to raise here, but the message content should be precise.

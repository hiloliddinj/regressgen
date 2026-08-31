singularize() is stripping the trailing 's' off words that are already singular but happen to end in a double 's', like "glass", "boss", "kiss", "class", "address". These aren't plurals, but I get back "glas", "bos", "kis", "clas", "addres" instead of the original word unchanged.

```python
from boltons.strutils import singularize

singularize('glass')   # -> 'glas', expected 'glass'
singularize('boss')    # -> 'bos', expected 'boss'
singularize('kiss')    # -> 'kis', expected 'kiss'
singularize('class')   # -> 'clas', expected 'class'
singularize('address') # -> 'addres', expected 'address'
```

Actual plurals like "glasses" -> "glass" work fine, so the "sses" -> "ss" case seems handled, it's just the plain double-s singular words that get mangled. This also breaks idempotency — running singularize on its own output doesn't give back the same value, e.g. singularize(singularize('Glasses')) gives 'Glas' instead of staying 'Glass'. I'd expect words that are already singular to just pass through untouched.

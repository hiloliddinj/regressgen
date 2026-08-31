`nth_product` and `product_index` behave wrong (or crash) when the iterables passed to them are actual iterators instead of reusable sequences like strings/lists, combined with the `repeat` argument.

With plain sequences it works fine:

```python
import more_itertools as mi

mi.nth_product(123, 'AB', 'CD', 'EFG', repeat=2)  # works, matches expected result

mi.nth_product(123, iter('AB'), iter('CD'), iter('EFG'), repeat=2)  # wrong/broken result

mi.product_index(target, iter('AB'), iter('CD'), iter('EFG'), repeat=2)  # same issue
```

When I pass iterators instead of strings, the results no longer match what I get from manually repeating the iterables (e.g. `'AB', 'CD', 'EFG', 'AB', 'CD', 'EFG'`). It seems like `repeat` isn't applied correctly once the inputs are one-shot iterators rather than something that can be iterated multiple times. I'd expect `nth_product`/`product_index` to give the same result regardless of whether I pass a string or an iterator over that string, with or without `repeat`.

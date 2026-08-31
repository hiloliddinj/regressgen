# Trajectory — `baseline` on `attrs-09161fc9`

**Verdict: REPRO**  (fails on buggy, passes on fixed — reproduces the bug)

- cost `$0.04332` · wall `11.8s` · tool calls `0`

## 1. Agent instructions (system prompt)

```
You are given a Python repository that contains a real bug, plus the bug report a user filed against it.

Write ONE pytest test file that is a regression test for that bug.

HOW YOUR TEST IS GRADED — the two-sided gate:
  * It must FAIL on the current (buggy) code.
  * It must PASS on the fixed code, which you will never see.

Both halves matter and they pull against each other. `assert False` fails on the
buggy code and also fails on the fixed code, so it scores zero. A test of
behaviour that already works passes on both, so it scores zero too. Only a test
that pins down the CORRECT expected behaviour — the behaviour the report says
*should* happen — satisfies both halves.

So: assert what the code SHOULD do, never merely record what it currently does.

Return ONLY the complete test file, in a single ```python fenced code block.
No commentary before or after. The file must be self-contained and importable.
```

## 2. Task (user prompt)

The agent receives the bug report and the repository layout. It never sees the fixed tree, the upstream fix, or the maintainer's test.

```
Using a pre-init hook together with a keyword-only field that has a default value causes class creation to blow up with a syntax error in the generated init code, not even a normal Python exception you'd expect from bad user code.

Repro:

```python
import attr

@attr.define
class Foo:
    kw_and_default: int = attr.field(kw_only=True, default=3)

    def __attrs_pre_init__(self, *, kw_and_default):
        print(kw_and_default)

Foo()
```

This raises a SyntaxError coming from compiling the generated init source, with the traceback showing the generated code has a malformed parameter default assignment (something like `default=kw_and_default=attr_dict[...].default` duplicated oddly). It only shows up when all three things are combined: a pre-init hook that takes the field, kw_only=True, and a default value. Removing any one of those makes it work fine.

I expected the class to just be created normally and the pre-init hook to receive the default value like it does without kw_only. Instead the class definition itself fails before I even get to instantiate anything.
```

## 3. Tool calls

_No tools — this system answers in a single prompt._

## 4. Submitted test

```python
"""
Regression test for the bug where combining a pre-init hook that accepts
field arguments with a keyword-only field that has a default value produces
a `SyntaxError` in the generated __init__ code.

See: https://github.com/python-attrs/attrs/issues (pre_init + kw_only + default)
"""
import attr


def test_pre_init_with_kw_only_default_does_not_raise_syntax_error():
    """
    Defining a class with:
      - a pre-init hook that takes the kw_only field as an argument
      - a field that is kw_only=True with a default value

    should not raise a SyntaxError while generating __init__, and the
    pre-init hook should receive the correct (default) value.
    """
    received = {}

    @attr.define
    class Foo:
        kw_and_default: int = attr.field(kw_only=True, default=3)

        def __attrs_pre_init__(self, *, kw_and_default):
            received["value"] = kw_and_default

    # Class creation must succeed, and using the default value must work.
    instance = Foo()

    assert instance.kw_and_default == 3
    assert received["value"] == 3

    # Also make sure overriding the value explicitly still works correctly.
    received.clear()
    instance2 = Foo(kw_and_default=42)
    assert instance2.kw_and_default == 42
    assert received["value"] == 42
```

## 5. Two-sided gate

### Against `buggy/` — exit 1 (must be non-zero)

```
                                             [100%]
=================================== FAILURES ===================================
________ test_pre_init_with_kw_only_default_does_not_raise_syntax_error ________

    def test_pre_init_with_kw_only_default_does_not_raise_syntax_error():
        """
        Defining a class with:
          - a pre-init hook that takes the kw_only field as an argument
          - a field that is kw_only=True with a default value
    
        should not raise a SyntaxError while generating __init__, and the
        pre-init hook should receive the correct (default) value.
        """
        received = {}
    
>       @attr.define
         ^^^^^^^^^^^

tests/test_regressgen_candidate.py:22: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
<sandbox>:402: in define
    return wrap(maybe_cls)
           ^^^^^^^^^^^^^^^
<sandbox>:393: in wrap
    return do_it(cls, True)
           ^^^^^^^^^^^^^^^^
<sandbox>:339: in do_it
    return attrs(
<sandbox>:1403: in attrs
    return wrap(maybe_cls)
           ^^^^^^^^^^^^^^^
<sandbox>:1382: in wrap
    builder.add_init()
<sandbox>:972: in add_init
    _make_init(
<sandbox>:1875: in _make_init
    init = _make_method(
<sandbox>:239: in _make_method
    _compile_and_eval(script, globs, locs, filename)
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

script = "def __init__(self, *, kw_and_default=attr_dict['kw_and_default'].default):\n    self.__attrs_pre_init__(kw_and_defaul..._and_default'].default=kw_and_default=attr_dict['kw_and_default'].default)\n    self.kw_and_default = kw_and_default\n"
globs = {'@py_builtins': <module 'builtins' (built-in)>, '@pytest_ar': <module '_pytest.assertion.rewrite' from '/Users/hiloli...ass 'AssertionError'>, 'AttributeError': <class 'AttributeError'>, 'BaseException': <class 'BaseException'>, ...}, ...}
locs = {}
filename = '<attrs generated init tests.test_regressgen_candidate.test_pre_init_with_kw_only_default_does_not_raise_syntax_error.<locals>.Foo>'

    def _compile_and_eval(script, globs, locs=None, filename=""):
        """
        Evaluate the script with the given global (globs) and lo
... [800 more chars]
```

### Against `fixed/` — exit 0 (must be zero)

```
.                                                                        [100%]
1 passed in 0.01s
```

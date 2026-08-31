# Third-party code

The MIT licence in `LICENSE` covers the code written for this project:
`regressgen/`, `tools/`, `tests/`, and the documentation.

It does **not** cover the contents of `cases/*/buggy/` and `cases/*/fixed/`.
Those directories vendor source from third-party open-source libraries, used
here unmodified as subjects of evaluation. Each vendored tree carries its
upstream licence file, and each case records its licence and exact provenance
in `meta.json`.

| Library | Upstream | Licence |
|---|---|---|
| more-itertools | https://github.com/more-itertools/more-itertools | MIT |
| cachetools | https://github.com/tkem/cachetools | MIT |
| boltons | https://github.com/mahmoud/boltons | BSD-3-Clause |
| tabulate | https://github.com/astanin/python-tabulate | MIT |
| packaging | https://github.com/pypa/packaging | Apache-2.0 OR BSD-2-Clause |
| semver | https://github.com/python-semver/python-semver | BSD-3-Clause |

The only modification made to any vendored tree is the tree surgery described
in `docs/CORPUS.md`: `fixed/` pairs the fix commit's source with the parent
commit's tests, so the maintainer's regression test is held out. No file
contents are edited.

These libraries are included so the evaluation can be reproduced offline and
without network access. No library is redistributed as an installable package,
and no upstream project is affiliated with or endorses this work.

The bug reports in `cases/*/report.md` are generated text written for this
project, describing the behaviour of the vendored code. They are covered by the
MIT licence above.

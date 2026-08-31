"""Corpus integrity, and a regression test for a bug in our own validator.

The oracle has to run at the path it occupied upstream. Some maintainer tests
assert on their own module name — attrs has
`repr(C(1)).startswith("<tests.test_make.C object at 0x")` — and others pickle a
class defined in the test module. Rename the file and both break, which made
three perfectly good cases look invalid.
"""

from __future__ import annotations

import json

import pytest

from regressgen.corpus import load_cases


@pytest.fixture(scope="module")
def cases():
    cs = load_cases()
    if not cs:
        pytest.skip("no cases mined")
    return cs


def test_every_case_is_structurally_complete(cases):
    for c in cases:
        assert c.buggy.is_dir(), f"{c.id}: no buggy/"
        assert c.fixed.is_dir(), f"{c.id}: no fixed/"
        assert c.oracle_tests, f"{c.id}: no oracle test"
        assert (c.buggy / c.tests_dir).is_dir(), f"{c.id}: no {c.tests_dir}/"
        assert (c.buggy / c.pkg_dir).is_dir(), f"{c.id}: no {c.pkg_dir}/"


def test_every_case_has_a_bug_report(cases):
    for c in cases:
        assert c.report.strip(), f"{c.id}: empty report.md"
        assert len(c.report.split()) > 40, f"{c.id}: report is suspiciously short"


def test_every_case_records_its_provenance(cases):
    for c in cases:
        m = json.loads((c.root / "meta.json").read_text())
        for key in ("upstream", "license", "fix_commit", "buggy_commit", "subject"):
            assert m.get(key), f"{c.id}: meta.json missing {key}"
        assert len(m["fix_commit"]) == 40, f"{c.id}: fix_commit is not a full SHA"


def test_oracle_is_keyed_by_its_upstream_path(cases):
    """The validator bug: renaming the oracle changes its module path."""
    for c in cases:
        mapped = c.oracle_at_original_paths
        assert mapped, f"{c.id}: no oracle mapping"
        for rel in mapped:
            assert "/" in rel, f"{c.id}: {rel!r} is not a repo-relative path"
        for rel in c.meta.get("oracle_test_files", []):
            assert rel in mapped, f"{c.id}: {rel} not restored to its upstream path"


def test_no_case_ships_build_or_cache_artifacts(cases):
    """Caches written while mining must not be committed as if upstream."""
    junk = {"__pycache__", ".pytest_cache", ".hypothesis", ".ruff_cache", ".tox"}
    for c in cases:
        for tree in (c.buggy, c.fixed):
            found = [p for p in tree.rglob("*") if p.is_dir() and p.name in junk]
            assert not found, f"{c.id}: {[str(p) for p in found[:3]]}"


def test_the_answer_key_is_not_reachable_from_the_agents_tree(cases):
    """`fixed/` and `oracle/` are siblings of `buggy/`, never inside it."""
    for c in cases:
        assert not (c.buggy / "fixed").exists(), f"{c.id}: fixed/ inside buggy/"
        assert not (c.buggy / "oracle").exists(), f"{c.id}: oracle/ inside buggy/"
        assert c.fixed.resolve() != c.buggy.resolve()

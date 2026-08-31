"""Tests for the two-sided gate.

These are the tests that matter most in this project: if the gate can be fooled,
every number in the README is worthless. Each test here is one way somebody might
try to fool it.
"""

from __future__ import annotations

import pytest

from regressgen.baseline import extract_code
from regressgen.corpus import load_cases
from regressgen.verify import Verdict, verify

CASE_ID = "more-itertools-0e6acdf9"   # chunked() should reject negative n


@pytest.fixture(scope="module")
def case():
    cases = load_cases([CASE_ID])
    if not cases:
        pytest.skip(f"{CASE_ID} not mined")
    return cases[0]


def test_the_maintainers_own_test_scores_repro(case):
    """The upstream regression test is the gold standard; it must score REPRO."""
    oracle = "\n\n".join(p.read_text() for p in case.oracle_tests)
    assert verify(case, oracle).verdict == Verdict.REPRO


def test_assert_false_does_not_score(case):
    """The laziest cheat: fails on buggy, but also on fixed."""
    src = "def test_cheat():\n    assert False\n"
    assert verify(case, src).verdict == Verdict.WRONG_EXPECTATION


def test_a_test_of_working_behaviour_does_not_score(case):
    """The subtle failure: real test, real assertions, wrong bug. Passes both."""
    src = (
        "import more_itertools as mi\n\n"
        "def test_chunked_works_normally():\n"
        "    assert list(mi.chunked('ABCDE', 2)) == [['A','B'],['C','D'],['E']]\n"
    )
    assert verify(case, src).verdict == Verdict.VACUOUS


def test_inverted_test_does_not_score(case):
    """Asserting the buggy behaviour is correct: passes buggy, fails fixed."""
    src = (
        "import pytest\n"
        "import more_itertools as mi\n\n"
        "def test_negative_n_raises_islice_error():\n"
        "    with pytest.raises(ValueError, match='islice'):\n"
        "        list(mi.chunked('ABCDE', -1))\n"
    )
    assert verify(case, src).verdict == Verdict.INVERTED


def test_uncollectable_test_is_invalid(case):
    src = "def test_broken(:\n    pass\n"
    assert verify(case, src).verdict == Verdict.INVALID


@pytest.mark.parametrize("src", [
    "import json\nwith open('../fixed/more_itertools/more.py') as f: pass\n",
    "open('cases/x/meta.json')\n",
])
def test_reaching_for_the_answer_key_is_caught(case, src):
    assert verify(case, src).verdict == Verdict.LEAKED


def test_extract_code_prefers_the_longest_fenced_block():
    text = "blah\n```python\nx=1\n```\nmore\n```python\ndef test_a():\n    assert 1\n```\n"
    assert "def test_a" in extract_code(text)


def test_extract_code_accepts_unfenced_python():
    assert "def test_a" in extract_code("def test_a():\n    assert 1\n")


def test_extract_code_rejects_prose():
    assert extract_code("I cannot help with that.") == ""

"""The two-sided gate: does a candidate test actually reproduce the bug?

A test only counts if it FAILS on the buggy tree and PASSES on the fixed tree.
That pair is what makes the metric un-gameable:

    `assert False`        fails on both  -> WRONG_EXPECTATION
    a test of the happy path passes both -> VACUOUS
    only a test that pins the *correct* expected behaviour scores REPRO.

The agent never sees the fixed tree; it is the held-out half of the oracle.
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from enum import StrEnum

from .corpus import Case
from .sandbox import RunResult, run_candidate


class Verdict(StrEnum):
    REPRO = "REPRO"                          # fail on buggy, pass on fixed  <- the goal
    VACUOUS = "VACUOUS"                      # passes both: does not exercise the bug
    WRONG_EXPECTATION = "WRONG_EXPECTATION"  # fails both: asserts the wrong thing
    INVERTED = "INVERTED"                    # passes buggy, fails fixed
    INVALID = "INVALID"                      # will not import/collect
    LEAKED = "LEAKED"                        # tried to read the held-out fixed tree
    ERROR = "ERROR"                          # harness/API failure — NOT an agent result


# The agent is given only buggy/. Reaching for the answer key is disqualifying.
#
# Path-shaped only, deliberately. An earlier version matched the bare word
# "fixed" and the string literal 'fixed', which would false-positive on
# perfectly legitimate tests — tabulate, for one, is full of fixed-width
# columns. Escaping the sandbox requires a path, so match paths.
LEAK_RE = re.compile(
    r"""(\.\.[/\\]+fixed\b"""      # ../fixed
    r"""|[/\\]fixed[/\\]"""         # .../fixed/...
    r"""|(?<![\w/])fixed[/\\]"""     # fixed/ at a path start
    r"""|[/\\]oracle[/\\]"""        # .../oracle/...
    r"""|(?<![\w/])oracle[/\\]"""    # oracle/ at a path start
    r"""|\bmeta\.json\b)"""          # the provenance file
)


@dataclass
class CaseResult:
    case_id: str
    verdict: str
    buggy_rc: int
    fixed_rc: int
    buggy_output: str
    fixed_output: str
    test_source: str
    attempts: int = 1
    seconds: float = 0.0
    usd: float = 0.0

    @property
    def ok(self) -> bool:
        return self.verdict == Verdict.REPRO

    def to_dict(self) -> dict:
        return asdict(self)


def verify(case: Case, test_source: str) -> CaseResult:
    if LEAK_RE.search(test_source):
        return CaseResult(case.id, Verdict.LEAKED, -1, -1, "", "", test_source)

    buggy: RunResult = run_candidate(case.buggy, test_source, case.tests_dir)
    fixed: RunResult = run_candidate(case.fixed, test_source, case.tests_dir)

    if not buggy.collected or not fixed.collected:
        verdict = Verdict.INVALID
    elif not buggy.passed and fixed.passed:
        verdict = Verdict.REPRO
    elif buggy.passed and fixed.passed:
        verdict = Verdict.VACUOUS
    elif not buggy.passed and not fixed.passed:
        verdict = Verdict.WRONG_EXPECTATION
    else:
        verdict = Verdict.INVERTED

    return CaseResult(
        case.id, verdict, buggy.rc, fixed.rc,
        buggy.output[-3000:], fixed.output[-3000:], test_source,
    )

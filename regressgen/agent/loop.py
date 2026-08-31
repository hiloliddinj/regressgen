"""The agent: staged variants, one per changelog iteration."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum

from ..corpus import Case
from ..model import run_agent
from . import prompts
from .tools import ToolState, build_toolset


class Variant(StrEnum):
    V2_TOOLS = "v2-tools"            # repo navigation only
    V3_EXEC = "v3-exec"              # + run the test against buggy
    V4_DISCIPLINE = "v4-discipline"  # + reject wrong-reason failures
    V5_FIXPROBE = "v5-fixprobe"      # + hypothetical-fix self-verification
    V6_CRITIC = "v6-critic"          # + adversarial reviewer, one revision round


CONFIG = {
    Variant.V2_TOOLS:       dict(execute=False, discipline=False, fix_probe=False),
    Variant.V3_EXEC:        dict(execute=True,  discipline=False, fix_probe=False),
    Variant.V4_DISCIPLINE:  dict(execute=True,  discipline=True,  fix_probe=False),
    Variant.V5_FIXPROBE:    dict(execute=True,  discipline=True,  fix_probe=True),
    Variant.V6_CRITIC:      dict(execute=True,  discipline=True,  fix_probe=True),
}

MAX_TURNS = {
    Variant.V2_TOOLS: 20,
    Variant.V3_EXEC: 30,
    Variant.V4_DISCIPLINE: 30,
    Variant.V5_FIXPROBE: 40,
    Variant.V6_CRITIC: 40,
}


@dataclass
class Solution:
    test_source: str
    usd: float = 0.0
    turns: int = 0
    calls: list[dict] = field(default_factory=list)
    error: str | None = None
    rationale: str = ""


def _attempt(case: Case, variant: Variant, extra: str = "",
             python: str | None = None) -> tuple[Solution, ToolState]:
    cfg = CONFIG[variant]
    state = ToolState()
    servers, names = build_toolset(
        case, state,
        allow_exec=cfg["execute"], allow_fix_probe=cfg["fix_probe"], python=python,
    )
    system = prompts.build_system(
        navigate=True, execute=cfg["execute"], discipline=cfg["discipline"],
        fix_probe=cfg["fix_probe"], tool_output=True,
    )
    completion = run_agent(
        prompts.user_prompt(case, case.report) + extra,
        system, servers, names, max_turns=MAX_TURNS[variant],
    )
    sol = Solution(
        test_source=state.submitted or "",
        usd=completion.usd,
        turns=completion.turns,
        calls=state.calls,
        error=completion.error or (None if state.submitted else "no test submitted"),
        rationale=state.rationale,
    )
    return sol, state


def _objects(reply: str) -> bool:
    """Parse the critic's verdict line.

    The first version asked for a bare `APPROVE` token and treated anything else
    as an objection. The critic often wrote its analysis and never emitted the
    token, so approvals were misread as objections and triggered pointless — and
    expensive — revision rounds. Parse an explicit verdict line, and when the
    contract is broken, fall back to "no objection" rather than assuming one.
    """
    for line in reply.strip().splitlines()[:3]:
        t = line.strip().upper().removeprefix("**").removesuffix("**").strip()
        if t.startswith("VERDICT:"):
            return "OBJECT" in t
        if t == "APPROVE":
            return False
    return False


def _critique(case: Case, test_source: str) -> tuple[str, float, list[dict]]:
    """Fresh-context reviewer with read-only access to the buggy tree."""
    state = ToolState()
    servers, names = build_toolset(case, state, allow_exec=False, allow_fix_probe=False)
    names = [n for n in names if n.endswith(("list_files", "read_file", "search_code"))]
    prompt = (prompts.user_prompt(case, case.report)
              + f"\n\nTHE TEST UNDER REVIEW\n---------------------\n"
                f"```python\n{test_source}\n```\n")
    c = run_agent(prompt, prompts.CRITIC, servers, names, max_turns=15)
    return c.text.strip(), c.usd, state.calls


def solve(case: Case, variant: Variant, python: str | None = None) -> Solution:
    """`python` selects the interpreter tests run under.

    None means the harness venv, which is what every corpus evaluation uses so
    the numbers stay comparable. `solve` passes the target project's own
    interpreter instead, so its dependencies are importable.
    """
    sol, _ = _attempt(case, variant, python=python)
    if variant is not Variant.V6_CRITIC or not sol.test_source.strip():
        return sol

    objection, usd, ccalls = _critique(case, sol.test_source)
    sol.usd += usd
    sol.calls += [{"tool": "critic", "args": {}, "result": objection[:1500]}] + ccalls
    if not _objects(objection):
        return sol

    revised, _ = _attempt(case, variant, "\n\n" + prompts.REVISE.format(
        objection=objection, previous=sol.test_source), python=python)
    if not revised.test_source.strip():
        return sol                      # reviewer round failed; keep the original
    revised.usd += sol.usd
    revised.calls = sol.calls + [{"tool": "revision", "args": {},
                                  "result": "agent re-ran after the objection"}] + revised.calls
    return revised

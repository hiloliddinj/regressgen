"""The baseline: one direct prompt with basic instructions, no tools.

This is the "reasonable basic way to handle the task" the brief asks for — what
a developer does today, pasting the report and the relevant file into a chat
window. It is deliberately given an advantage the agent does not get: the exact
source files the real fix touched are inlined for it, so it never has to search.
Any gap the agent opens up is therefore not a gap in information access.
"""

from __future__ import annotations

import re

from .agent import prompts
from .corpus import Case
from .model import complete

FENCE = re.compile(r"```(?:python|py)?\s*\n(.*?)```", re.S)
# Whole files, not excerpts. At 24k the baseline saw only the first 11% of
# more_itertools/more.py and never reached the function under discussion, which
# made the comparison unfair rather than merely unfavourable. 250k covers every
# file in the corpus (largest: 172k) at roughly 45k tokens — well within one
# request, and a fair model of pasting the file into a chat window.
MAX_FILE_CHARS = 250_000
MAX_TOTAL_CHARS = 400_000


def extract_code(text: str) -> str:
    blocks = FENCE.findall(text)
    if blocks:
        return max(blocks, key=len).strip() + "\n"
    # no fence: accept the raw body if it at least looks like Python
    return text.strip() + "\n" if "def test" in text or "import" in text else ""


def solve(case: Case) -> tuple[str, float, str | None]:
    sources, budget = {}, MAX_TOTAL_CHARS
    for rel in case.meta.get("src_files", []):
        p = case.buggy / rel
        if p.exists() and budget > 0:
            text = p.read_text(errors="replace")[:min(MAX_FILE_CHARS, budget)]
            sources[rel] = text
            budget -= len(text)

    system = prompts.build_system(navigate=False, execute=False, discipline=False,
                                  fix_probe=False, tool_output=False)
    c = complete(prompts.user_prompt(case, case.report, sources), system=system)
    return extract_code(c.text), c.usd, c.error

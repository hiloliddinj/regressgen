"""In-process tools the agent uses to investigate a buggy repository.

Two properties matter here:

1. Every path is resolved and confined to `buggy/`. The held-out `fixed/` tree
   is unreachable by construction, not by instruction — the agent cannot cheat
   even if it tries.
2. Every call is recorded, which is what the trajectory deliverable is made of.
"""

from __future__ import annotations

import re
import shutil
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from claude_agent_sdk import create_sdk_mcp_server, tool

from ..corpus import Case
from ..sandbox import run_candidate, run_suite

MAX_CHARS = 40_000
OUTLINE_THRESHOLD = 400
RECORD_CHARS = 2_500
DEF_RE = re.compile(r"\s*(def |class |@)")
SERVER = "rg"


@dataclass
class ToolState:
    """Mutable scratchpad shared with the caller for one case."""
    submitted: str | None = None
    rationale: str = ""
    calls: list[dict] = field(default_factory=list)
    run_count: int = 0
    fix_probes: int = 0


def _ok(text: str) -> dict:
    return {"content": [{"type": "text", "text": text[:MAX_CHARS]}]}


def build_toolset(case: Case, state: ToolState, *,
                  allow_exec: bool, allow_fix_probe: bool,
                  python: str | None = None):
    """Return (mcp_servers, allowed_tool_names) for one case."""
    root = case.buggy.resolve()

    def safe(rel: str) -> Path:
        p = (root / rel).resolve()
        if not p.is_relative_to(root):
            raise ValueError(f"path escapes the repository: {rel}")
        return p

    def record(name: str, args: dict, response: str) -> None:
        """Store what the tool actually returned, not a description of it.

        The trajectory has to show the feedback that shaped the agent's next
        step — `run_test`'s pytest output above all. Recording "1472 chars"
        makes the trajectory unreadable as evidence.
        """
        state.calls.append({"tool": name, "args": args,
                            "result": response[:RECORD_CHARS]})

    @tool("list_files", "List Python files in the repository under test.", {"subdir": str})
    async def list_files(args):
        sub = (args.get("subdir") or "").strip().lstrip("/")
        base = safe(sub) if sub else root
        if not base.exists():
            out = f"no such directory: {sub}"
        else:
            files = sorted(p.relative_to(root).as_posix()
                           for p in base.rglob("*.py") if p.is_file())
            out = "\n".join(files) or "(no python files)"
        record("list_files", args, out)
        return _ok(out)

    @tool("read_file",
          "Read a source file with line numbers. Pass start/end to read a range; "
          "pass 0/0 for automatic. Files over 400 lines return a definition "
          "outline instead, so follow up with a range.",
          {"path": str, "start": int, "end": int})
    async def read_file(args):
        p = safe(args["path"])
        if not p.exists():
            record("read_file", args, "missing")
            return _ok(f"no such file: {args['path']}")
        lines = p.read_text(errors="replace").splitlines()
        start, end = int(args.get("start") or 0), int(args.get("end") or 0)

        if start or end:
            lo = max(1, start)
            hi = min(len(lines), end or len(lines))
            body = "\n".join(f"{i:5d}| {lines[i - 1]}" for i in range(lo, hi + 1))
            out = f"{args['path']} lines {lo}-{hi} of {len(lines)}\n\n{body}"
        elif len(lines) <= OUTLINE_THRESHOLD:
            out = "\n".join(f"{i:5d}| {line}" for i, line in enumerate(lines, 1))
        else:
            defs = [f"{i:5d}| {line.rstrip()}" for i, line in enumerate(lines, 1)
                    if DEF_RE.match(line)][:400]
            out = (f"{args['path']} is {len(lines)} lines — too long to show whole.\n"
                   f"Definition outline below; call read_file again with start/end "
                   f"to read a range.\n\n" + "\n".join(defs))
        record("read_file", args, out)
        return _ok(out)

    @tool("search_code", "Regex-search the repository's Python files.", {"pattern": str})
    async def search_code(args):
        try:
            rx = re.compile(args["pattern"])
        except re.error as e:
            return _ok(f"bad regex: {e}")
        hits = []
        for p in sorted(root.rglob("*.py")):
            try:
                for i, line in enumerate(p.read_text(errors="replace").splitlines(), 1):
                    if rx.search(line):
                        hits.append(f"{p.relative_to(root).as_posix()}:{i}: {line.strip()[:160]}")
                        if len(hits) >= 120:
                            break
            except OSError:
                continue
            if len(hits) >= 120:
                break
        out = "\n".join(hits) or "(no matches)"
        record("search_code", args, out)
        return _ok(out)

    @tool("run_test",
          "Run a candidate pytest file against the BUGGY code and return pytest output. "
          "Use this to confirm your test actually fails, and why.",
          {"test_source": str})
    async def run_test(args):
        state.run_count += 1
        r = run_candidate(root, args["test_source"], case.tests_dir, python=python)
        status = ("PASSED (exit 0) — this test does NOT reproduce the bug"
                  if r.passed else f"FAILED (exit {r.rc})")
        out = f"{status}\n\n{r.output}"
        record("run_test", {"test_source": args["test_source"][:800]}, out)
        return _ok(out)

    @tool("try_fix",
          "Apply a hypothetical one-string patch to the buggy source in a scratch copy, "
          "then run your test against it. Confirms your test would PASS once the bug is "
          "fixed. The patch is discarded; only your test is submitted.",
          {"path": str, "find": str, "replace": str, "test_source": str})
    async def try_fix(args):
        state.fix_probes += 1
        with tempfile.TemporaryDirectory(prefix="rg-fix-") as td:
            work = Path(td) / "t"
            shutil.copytree(root, work, symlinks=True)
            target = (work / args["path"]).resolve()
            if not target.is_relative_to(work.resolve()) or not target.exists():
                return _ok(f"no such file: {args['path']}")
            src = target.read_text()
            if args["find"] not in src:
                out = "patch not applied: `find` string does not occur in the file"
                record("try_fix", {"path": args["path"]}, out)
                return _ok(out)
            target.write_text(src.replace(args["find"], args["replace"], 1))

            t = run_candidate(work, args["test_source"], case.tests_dir, python=python)
            s = run_suite(work, case.tests_dir, python=python)
            verdict = ("your test PASSES with this fix" if t.passed
                       else "your test STILL FAILS with this fix")
            suite = ("existing suite still green" if s.passed
                     else "WARNING: this hypothetical fix breaks the existing suite")
            out = f"{verdict}\n{suite}\n\n{t.output[-1500:]}"
            record("try_fix", {"path": args["path"], "find": args["find"][:200]}, out)
            return _ok(out)

    @tool("submit_test", "Submit your final regression test file.",
          {"test_source": str, "rationale": str})
    async def submit_test(args):
        state.submitted = args["test_source"]
        state.rationale = args.get("rationale", "")
        record("submit_test", {"rationale": state.rationale[:600]},
               "Submitted.\n\n" + args["test_source"][:RECORD_CHARS])
        return _ok("Submitted.")

    tools = [list_files, read_file, search_code]
    if allow_exec:
        tools.append(run_test)
    if allow_fix_probe:
        tools.append(try_fix)
    tools.append(submit_test)

    server = create_sdk_mcp_server(SERVER, "1.0.0", tools)
    names = [f"mcp__{SERVER}__{t.name}" for t in tools]
    return {SERVER: server}, names

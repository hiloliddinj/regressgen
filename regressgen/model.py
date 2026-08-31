"""Thin wrapper over claude-agent-sdk.

Authenticates through the local Claude Code login, so no API key is required.
Every call reports cost and turn count, which is what feeds the cost-per-task
column of the evaluation table.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ResultMessage,
    TextBlock,
    ToolResultBlock,
    ToolUseBlock,
    query,
)

MODEL = "claude-sonnet-5"


@dataclass
class Step:
    """One observable event in a trajectory."""
    kind: str            # "text" | "tool_use" | "tool_result"
    name: str = ""
    payload: Any = None


@dataclass
class Completion:
    text: str
    usd: float = 0.0
    turns: int = 0
    steps: list[Step] = field(default_factory=list)
    error: str | None = None

    @property
    def tool_calls(self) -> list[Step]:
        return [s for s in self.steps if s.kind == "tool_use"]


async def _run(prompt: str, *, system: str, options_kw: dict) -> Completion:
    opts = ClaudeAgentOptions(
        model=MODEL,
        system_prompt=system,
        setting_sources=[],       # ignore ambient user/project settings -> reproducible
        **options_kw,
    )
    text_parts: list[str] = []
    steps: list[Step] = []
    usd = turns = 0
    err = None
    try:
        async for msg in query(prompt=prompt, options=opts):
            if isinstance(msg, AssistantMessage):
                for b in msg.content:
                    if isinstance(b, TextBlock):
                        text_parts.append(b.text)
                        steps.append(Step("text", payload=b.text))
                    elif isinstance(b, ToolUseBlock):
                        steps.append(Step("tool_use", b.name, b.input))
                    elif isinstance(b, ToolResultBlock):
                        steps.append(Step("tool_result", "", b.content))
            elif isinstance(msg, ResultMessage):
                usd = msg.total_cost_usd or 0.0
                turns = msg.num_turns or 0
                if msg.is_error:
                    err = str(msg.result)[:500]
    except Exception as e:
        err = f"{type(e).__name__}: {e}"[:500]
    return Completion("\n".join(text_parts), usd, turns, steps, err)


def complete(prompt: str, system: str = "", max_turns: int = 1) -> Completion:
    """Single-shot, no tools. This is what the baseline gets."""
    return asyncio.run(_run(prompt, system=system, options_kw={
        "max_turns": max_turns,
        "allowed_tools": [],
        "tools": [],
    }))


def run_agent(prompt: str, system: str, mcp_servers: dict,
              allowed_tools: list[str], max_turns: int = 30) -> Completion:
    """Tool-using loop. This is what the agent gets."""
    return asyncio.run(_run(prompt, system=system, options_kw={
        "max_turns": max_turns,
        "mcp_servers": mcp_servers,
        "allowed_tools": allowed_tools,
        "tools": [],              # no built-in tools; only ours
        "permission_mode": "bypassPermissions",
    }))

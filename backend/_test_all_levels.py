"""Smoke test: run the canonical solution for every level through the
grader and assert it passes. Run with:

    .venv/bin/python _test_all_levels.py
"""

import asyncio
import sys

from grader import grade

SOLUTIONS: dict[tuple[int, int], str] = {}


# ───────── World 1 ─────────
SOLUTIONS[(1, 1)] = '''
from mcp.server.fastmcp import FastMCP
mcp = FastMCP("pellet-tracker")

@mcp.tool()
def whoami(name: str) -> str:
    return f"Welcome to your Pellet Tracker, {name}!"

if __name__ == "__main__":
    mcp.run()
'''

SOLUTIONS[(1, 2)] = '''
from mcp.server.fastmcp import FastMCP
mcp = FastMCP("pellet-tracker")
PELLETS: list[str] = []

@mcp.tool()
def whoami(name: str) -> str:
    return f"Welcome to your Pellet Tracker, {name}!"

@mcp.tool()
def log_pellet(habit: str) -> str:
    PELLETS.append(habit)
    return f"Logged: {habit}"

@mcp.tool()
def list_pellets() -> list[str]:
    return PELLETS

if __name__ == "__main__":
    mcp.run()
'''

SOLUTIONS[(1, 3)] = '''
from mcp.server.fastmcp import FastMCP
mcp = FastMCP("pellet-tracker")
PELLETS: list[str] = []

@mcp.tool()
def whoami(name: str) -> str:
    return f"Welcome to your Pellet Tracker, {name}!"

@mcp.tool()
def log_pellet(habit: str) -> str:
    PELLETS.append(habit)
    return f"Logged: {habit}"

@mcp.tool()
def list_pellets() -> list[str]:
    return PELLETS

@mcp.tool()
def count_pellets(habit: str) -> int:
    return sum(1 for p in PELLETS if p == habit)

if __name__ == "__main__":
    mcp.run()
'''

SOLUTIONS[(1, 4)] = '''
import json
from pathlib import Path
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("pellet-tracker")
PELLETS_FILE = Path("pellets.json")

def _load() -> list[str]:
    try:
        with open(PELLETS_FILE) as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def _save(p: list[str]) -> None:
    with open(PELLETS_FILE, "w") as f:
        json.dump(p, f)

PELLETS: list[str] = _load()

@mcp.tool()
def whoami(name: str) -> str:
    return f"Welcome to your Pellet Tracker, {name}!"

@mcp.tool()
def log_pellet(habit: str) -> str:
    PELLETS.append(habit)
    _save(PELLETS)
    return f"Logged: {habit}"

@mcp.tool()
def list_pellets() -> list[str]:
    return PELLETS

@mcp.tool()
def count_pellets(habit: str) -> int:
    return sum(1 for p in PELLETS if p == habit)

if __name__ == "__main__":
    mcp.run()
'''


# ───────── World 2 ─────────
SOLUTIONS[(2, 1)] = '''
import json
from pathlib import Path
from typing import Annotated
from mcp.server.fastmcp import FastMCP
from pydantic import Field

mcp = FastMCP("pellet-tracker")
PELLETS_FILE = Path("pellets.json")

def _load():
    try:
        with open(PELLETS_FILE) as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def _save(p):
    with open(PELLETS_FILE, "w") as f:
        json.dump(p, f)

PELLETS: list[str] = _load()

@mcp.tool()
def whoami(name: str) -> str:
    return f"Welcome to your Pellet Tracker, {name}!"

@mcp.tool()
def log_pellet(
    habit: Annotated[str, Field(description="The name of the habit, e.g. 'reading'")],
) -> str:
    PELLETS.append(habit)
    _save(PELLETS)
    return f"Logged: {habit}"

@mcp.tool()
def list_pellets() -> list[str]:
    return PELLETS

@mcp.tool()
def count_pellets(habit: str) -> int:
    return sum(1 for p in PELLETS if p == habit)

if __name__ == "__main__":
    mcp.run()
'''

SOLUTIONS[(2, 2)] = '''
import json
from pathlib import Path
from typing import Annotated
from mcp.server.fastmcp import FastMCP
from pydantic import Field

mcp = FastMCP("pellet-tracker")
PELLETS_FILE = Path("pellets.json")

def _load():
    try:
        with open(PELLETS_FILE) as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def _save(p):
    with open(PELLETS_FILE, "w") as f:
        json.dump(p, f)

PELLETS: list[str] = _load()

@mcp.tool()
def whoami(name: str) -> str:
    return f"Welcome to your Pellet Tracker, {name}!"

@mcp.tool()
def log_pellet(
    habit: Annotated[str, Field(description="The name of the habit to log.")],
) -> str:
    PELLETS.append(habit)
    _save(PELLETS)
    return f"Logged: {habit}"

@mcp.tool(annotations={"readOnlyHint": True})
def list_pellets() -> list[str]:
    return PELLETS

@mcp.tool(annotations={"readOnlyHint": True})
def count_pellets(habit: str) -> int:
    return sum(1 for p in PELLETS if p == habit)

if __name__ == "__main__":
    mcp.run()
'''

SOLUTIONS[(2, 3)] = '''
import json
from pathlib import Path
from typing import Annotated
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

mcp = FastMCP("pellet-tracker")
PELLETS_FILE = Path("pellets.json")

def _load():
    try:
        with open(PELLETS_FILE) as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def _save(p):
    with open(PELLETS_FILE, "w") as f:
        json.dump(p, f)

PELLETS: list[str] = _load()

class StreakInfo(BaseModel):
    habit: str
    total: int
    longest_run: int

@mcp.tool()
def whoami(name: str) -> str:
    return f"Welcome to your Pellet Tracker, {name}!"

@mcp.tool()
def log_pellet(
    habit: Annotated[str, Field(description="The name of the habit to log.")],
) -> str:
    PELLETS.append(habit)
    _save(PELLETS)
    return f"Logged: {habit}"

@mcp.tool(annotations={"readOnlyHint": True})
def list_pellets() -> list[str]:
    return PELLETS

@mcp.tool(annotations={"readOnlyHint": True})
def count_pellets(habit: str) -> StreakInfo:
    total = sum(1 for p in PELLETS if p == habit)
    return StreakInfo(habit=habit, total=total, longest_run=total)

if __name__ == "__main__":
    mcp.run()
'''

SOLUTIONS[(2, 4)] = '''
import json
from pathlib import Path
from typing import Annotated
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

mcp = FastMCP("pellet-tracker")
PELLETS_FILE = Path("pellets.json")

def _load():
    try:
        with open(PELLETS_FILE) as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def _save(p):
    with open(PELLETS_FILE, "w") as f:
        json.dump(p, f)

PELLETS: list[str] = _load()

class StreakInfo(BaseModel):
    habit: str
    total: int
    longest_run: int

@mcp.tool()
def whoami(name: str) -> str:
    return f"Welcome to your Pellet Tracker, {name}!"

@mcp.tool()
def log_pellet(
    habit: Annotated[str, Field(description="The name of the habit to log.")],
) -> str:
    if not habit.strip():
        raise ValueError("habit cannot be empty")
    PELLETS.append(habit)
    _save(PELLETS)
    return f"Logged: {habit}"

@mcp.tool(annotations={"readOnlyHint": True})
def list_pellets() -> list[str]:
    return PELLETS

@mcp.tool(annotations={"readOnlyHint": True})
def count_pellets(habit: str) -> StreakInfo:
    total = sum(1 for p in PELLETS if p == habit)
    return StreakInfo(habit=habit, total=total, longest_run=total)

if __name__ == "__main__":
    mcp.run()
'''


# ───────── World 3 ─────────
SOLUTIONS[(3, 1)] = SOLUTIONS[(2, 4)].replace(
    'if __name__ == "__main__":',
    '''@mcp.resource("pellets://today")
def todays_pellets() -> str:
    return json.dumps(PELLETS)

if __name__ == "__main__":''')

SOLUTIONS[(3, 2)] = SOLUTIONS[(3, 1)].replace(
    'if __name__ == "__main__":',
    '''@mcp.resource("pellets://habit/{name}")
def pellets_for_habit(name: str) -> str:
    return json.dumps([p for p in PELLETS if p == name])

if __name__ == "__main__":''')


# ───────── World 4 ─────────
SOLUTIONS[(4, 1)] = SOLUTIONS[(3, 2)].replace(
    'if __name__ == "__main__":',
    '''@mcp.prompt()
def morning_check_in() -> str:
    return "Good morning! Which pellets will you eat today?"

if __name__ == "__main__":''')

SOLUTIONS[(4, 2)] = SOLUTIONS[(4, 1)].replace(
    'if __name__ == "__main__":',
    '''@mcp.prompt()
def weekly_recap(week_offset: int = 0) -> str:
    days = 7 + week_offset * 7
    return f"Summarize my pellets from the past {days} days."

if __name__ == "__main__":''')


# ───────── World 5 ─────────
# Tools that use Context must be decorated BEFORE mcp.run(), so we splice
# the new tools in *above* the `if __name__` block (and stitch in the
# necessary imports near the top).

def _splice_w5_tool(prev: str, new_tool_src: str) -> str:
    """Insert a new tool above the `if __name__` block; ensure Context +
    types imports are present near the top."""
    needed_imports = (
        "from mcp.server.fastmcp import Context\n"
        "from mcp.types import SamplingMessage, TextContent\n"
    )
    if "from mcp.server.fastmcp import Context" not in prev:
        prev = prev.replace(
            "from mcp.server.fastmcp import FastMCP",
            "from mcp.server.fastmcp import FastMCP\n" + needed_imports,
            1,
        )
    return prev.replace(
        'if __name__ == "__main__":',
        new_tool_src.rstrip() + '\n\nif __name__ == "__main__":',
        1,
    )


SOLUTIONS[(5, 1)] = _splice_w5_tool(
    SOLUTIONS[(4, 2)],
    '''
@mcp.tool()
async def analyze_my_week(ctx: Context) -> str:
    result = await ctx.session.create_message(
        messages=[SamplingMessage(role="user",
            content=TextContent(type="text", text=f"Reflect on: {PELLETS}"))],
        max_tokens=200,
    )
    return result.content.text
''',
)

SOLUTIONS[(5, 2)] = _splice_w5_tool(
    SOLUTIONS[(5, 1)],
    '''
class _HabitPrompt(BaseModel):
    habit: str


@mcp.tool()
async def start_habit(ctx: Context) -> str:
    result = await ctx.elicit(message="What habit?", schema=_HabitPrompt)
    if result.action != "accept":
        return "Cancelled."
    return f"Tracking {result.data.habit}"
''',
)

SOLUTIONS[(5, 3)] = _splice_w5_tool(
    SOLUTIONS[(5, 2)],
    '''
@mcp.tool()
async def bulk_import(ctx: Context, count: int) -> str:
    for i in range(count):
        await ctx.report_progress(progress=i + 1, total=count)
        PELLETS.append(f"imported_{i + 1}")
    _save(PELLETS)
    return f"Imported {count}"
''',
)


# ───────── World 6 (source-only) ─────────
SOLUTIONS[(6, 1)] = '''
CLAUDE_DESKTOP_SNIPPET = """
{
  "mcpServers": {
    "pellet-tracker": {
      "command": "python",
      "args": ["/path/to/server.py"]
    }
  }
}
"""
'''

SOLUTIONS[(6, 2)] = '''
CLAUDE_CODE_MCP_JSON = """
{
  "mcpServers": {
    "pellet-tracker": {
      "command": "python",
      "args": ["./server.py"]
    }
  }
}
"""
'''

SOLUTIONS[(6, 3)] = '''
MCP_INSPECTOR_CMD = "npx @modelcontextprotocol/inspector python ./server.py"
'''


# ───────── World 7 ─────────
SOLUTIONS[(7, 1)] = '''
from mcp.server.fastmcp import FastMCP
mcp = FastMCP("pellet-tracker")
if __name__ == "__main__":
    mcp.run(transport="streamable-http")
'''

SOLUTIONS[(7, 2)] = '''
from typing import Annotated
from mcp.server.fastmcp import FastMCP
from pydantic import Field

mcp = FastMCP("pellet-tracker")
PELLETS: list[str] = []

@mcp.tool()
def log_pellet(
    habit: Annotated[str, Field(description="The name of the habit to log.")],
    api_key: str,
) -> str:
    if api_key != "wakawaka":
        raise ValueError("Invalid API key")
    PELLETS.append(habit)
    return f"Logged: {habit}"

if __name__ == "__main__":
    mcp.run()
'''

SOLUTIONS[(7, 3)] = '''
OAUTH_CONFIG = """
{
  "authorization_endpoint": "https://auth.example.com/oauth/authorize",
  "token_endpoint": "https://auth.example.com/oauth/token",
  "client_id": "pellet-tracker",
  "scopes": ["pellets:read", "pellets:write"]
}
"""
'''


# ───────── World 8 ─────────
SOLUTIONS[(8, 1)] = '''
DXT_MANIFEST = """
{
  "dxt_version": "0.1",
  "name": "pellet-tracker",
  "version": "1.0.0",
  "description": "Personal habit tracker.",
  "author": {"name": "You"},
  "server": {
    "type": "python",
    "entry_point": "server.py",
    "mcp_config": {
      "command": "python",
      "args": ["${__dirname}/server.py"]
    }
  }
}
"""
'''

SOLUTIONS[(8, 2)] = '''
SKILL_MD = """
---
name: pellet-tracker
description: Use when the user mentions habits, streaks, or daily routines.
---

# When to use
When the user logs a habit or asks about progress, reach for Pellet Tracker.
"""
'''


async def main() -> int:
    failures = 0
    for (w, l), code in SOLUTIONS.items():
        r = await grade(w, l, code)
        status = "PASS" if r["passed"] else "FAIL"
        steps = len(r["steps"])
        passed_steps = sum(1 for s in r["steps"] if s["passed"])
        line = f"  W{w}L{l}  {status}   {passed_steps}/{steps} steps   trace={len(r['trace'])}"
        print(line)
        if not r["passed"]:
            failures += 1
            for e in r["errors"]:
                print(f"      ! {e}")
            if r["stderr"]:
                print(f"      stderr: {r['stderr'][:300]}")
    print()
    if failures:
        print(f"FAILED: {failures} lesson(s)")
        return 1
    print(f"ALL GOOD ({len(SOLUTIONS)} lessons)")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))

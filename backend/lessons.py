"""Lesson registry. All 19 levels build one growing server: **Pellet Tracker**.

Each level's `starter_code` already contains the canonical solution of all
prior levels. The player only edits the `# TODO` block.

World order (refined 2026-05-16):
  W1 Pellet Basics       — intro, state, computed values, persistence
  W2 Tool Maze           — descriptions, annotations, structured output, errors
  W3 Resource Tunnels    — static + templated resources
  W4 Prompt Power-Pellets— simple + parameterized prompts
  W5 Bidirectional MCP   — sampling, elicitation, progress notifications
  W6 Escape to Claude    — Claude Desktop, Claude Code, MCP Inspector
  W7 Going Public        — Streamable HTTP, API key, OAuth 2.1 + PKCE
  W8 Distribute + Skills — DXT packaging, SKILL.md companion
"""
from dataclasses import dataclass, field
from typing import Any


@dataclass
class GraderStep:
    kind: str
    params: dict[str, Any] = field(default_factory=dict)
    expect: dict[str, Any] = field(default_factory=dict)
    description: str = ""


@dataclass
class Lesson:
    world: int
    level: int
    title: str
    ghost: str
    concept: str
    story: str
    concept_brief: str
    instructions: str
    starter_code: str
    solution_hint: str
    post_pass_debrief: str
    pellet_reward: int
    grader_steps: list[GraderStep]


# ════════════════════════════════════════════════════════════════════════
# WORLD 1 — PELLET BASICS
# ════════════════════════════════════════════════════════════════════════

W1L1_STARTER = '''"""W1-L1: Greet your Pellet Tracker.

Build a tool called `whoami` that takes a `name` (string) and returns:
    Welcome to your Pellet Tracker, <name>!
"""
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("pellet-tracker")


@mcp.tool()
def whoami(name: str) -> str:
    """Identify the player using the tracker."""
    # TODO: return  Welcome to your Pellet Tracker, <name>!
    return ""


if __name__ == "__main__":
    mcp.run()
'''

W1L1_BRIEF = """\
## What is FastMCP?

**FastMCP** is the high-level Python SDK for building MCP servers. It turns
a regular function into a fully wired protocol endpoint with zero boilerplate.

Think of it as **Flask for MCP** — decorate Python functions and FastMCP
handles JSON-RPC, schemas, and the protocol lifecycle for you.

```python
from mcp.server.fastmcp import FastMCP
mcp = FastMCP("my-server")

@mcp.tool()
def my_function(x: int) -> str: ...
```

### What `@mcp.tool()` does
- Registers the function as a callable MCP tool
- Reads its **type hints** → generates a JSON Schema for input/output
- Reads its **docstring** → becomes the tool's description (which Claude reads when deciding to use it)

### What `mcp.run()` does
Starts a **JSON-RPC 2.0** loop over **stdio** — line-delimited JSON messages
on standard input/output. That's how Claude talks to your server. You'll
see those messages in the Protocol Inspector when you hit ► RUN.

### Why FastMCP instead of the low-level API
The lower-level `mcp.server.Server` exists too, but writing servers by hand
means manually building schemas, JSON-RPC handlers, and lifecycle callbacks.
FastMCP gives you the same result in 5 lines.
"""

W1L1_DEBRIEF = """\
**Power-pellet unlocked:**

- `FastMCP("name")` creates a server you'll add tools/resources/prompts to.
- `@mcp.tool()` registers a function — type hints become the schema, docstrings become the description.
- `mcp.run()` starts a JSON-RPC 2.0 loop over stdio.

Every level from here adds new decorators, new state, or new protocol features — but FastMCP is the foundation.
"""


W1L2_STARTER = '''"""W1-L2: Eat your first pellet.

Add two tools to log habits and list them back.
"""
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("pellet-tracker")

# Server state - survives across tool calls within one Claude session.
PELLETS: list[str] = []


@mcp.tool()
def whoami(name: str) -> str:
    """Identify the player using the tracker."""
    return f"Welcome to your Pellet Tracker, {name}!"


# TODO: add a tool `log_pellet(habit: str) -> str` that appends to PELLETS
#       and returns a confirmation like "Logged: <habit>".


# TODO: add a tool `list_pellets() -> list[str]` that returns PELLETS.


if __name__ == "__main__":
    mcp.run()
'''

W1L2_BRIEF = """\
## Multiple tools, shared state

An MCP server is just a Python module — so a module-level list (or dict)
works perfectly as your server's memory between tool calls.

```python
PELLETS: list[str] = []  # lives for the lifetime of the process

@mcp.tool()
def log_pellet(habit: str) -> str:
    PELLETS.append(habit)
    return f"Logged: {habit}"
```

### How return types become tool output
FastMCP looks at the return type and serializes:

- `str` → one text content block
- `list[str]` or `dict` → JSON-serialized text content block
- Pydantic models → structured content (World 2)

### One server, many tools
Any number of tools register against one `mcp` instance. Claude lists them
via `tools/list` and routes calls by name via `tools/call`.

### Lifetime gotcha
`PELLETS` resets to `[]` every time the **process** restarts. World 1's
last level adds real persistence so your habits survive restarts.
"""

W1L2_DEBRIEF = """\
**Power-pellet unlocked:**

- Module-level state survives across tool calls within one process.
- A server registers many tools; Claude lists them via `tools/list`.
- FastMCP auto-serializes returns (`list`, `dict`, `str`) into content blocks.

Next: tools that **compute** over your state.
"""


W1L3_STARTER = '''"""W1-L3: Count your pellets.

Add `count_pellets(habit: str) -> int` returning how many times the
habit appears. Return 0 if it was never logged.
"""
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


# TODO: add `count_pellets(habit: str) -> int` returning how many
#       times `habit` appears in PELLETS.


if __name__ == "__main__":
    mcp.run()
'''

W1L3_BRIEF = """\
## Tools that compute

Tools aren't limited to "set this" or "list that" — they can derive new
values from state. Same `@mcp.tool()` decorator, different return type.

```python
@mcp.tool()
def count_pellets(habit: str) -> int:
    return sum(1 for p in PELLETS if p == habit)
```

### Why typed returns matter
Returning `int` (instead of `str`) signals to Claude that the answer is
numeric. That helps when Claude plugs it into a sentence ("you've eaten 3
pellets") or compares it ("more than yesterday's 2").

### Be forgiving with inputs
Returning `0` when the habit was never logged is intentional. Tools that
*always* return a sensible value are easier for Claude to chain. World 2
will teach you when raising is the right call.
"""

W1L3_DEBRIEF = """\
**Power-pellet unlocked:**

- Tools can compute derived values — not just CRUD.
- Typed return values (`int`, `bool`) signal the answer's shape.
- Returning a sensible default is often friendlier than raising.

One more for World 1: making your state actually **persist**.
"""


W1L4_STARTER = '''"""W1-L4: Persist your pellets.

So far PELLETS lives only in memory — it resets every time the server
restarts. Add JSON-file persistence so your Pellet Tracker remembers
across restarts.

Implement `_load()` to read PELLETS from `pellets.json`, and update
`log_pellet` to call `_save()` after appending. `_save()` should write
`PELLETS` to `pellets.json` using `json.dump`.
"""
import json
from pathlib import Path

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("pellet-tracker")
PELLETS_FILE = Path("pellets.json")


def _load() -> list[str]:
    """Read PELLETS from the JSON file, or return [] if it doesn\'t exist."""
    # TODO: try to open PELLETS_FILE and json.load it. If the file is
    #       missing (FileNotFoundError), return [].
    return []


def _save(p: list[str]) -> None:
    """Write the list of pellets to the JSON file."""
    # TODO: open PELLETS_FILE for writing and json.dump `p` into it.
    pass


PELLETS: list[str] = _load()


@mcp.tool()
def whoami(name: str) -> str:
    return f"Welcome to your Pellet Tracker, {name}!"


@mcp.tool()
def log_pellet(habit: str) -> str:
    PELLETS.append(habit)
    _save(PELLETS)            # <- persists every write
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

W1L4_BRIEF = """\
## Real servers persist

In-memory state is fine for the first few levels, but real MCP servers
need to remember things across process restarts. Three common options:

| Backing store | When to use |
|---------------|-------------|
| **JSON file** | Single user, small data. Lowest friction. ← we'll use this. |
| **SQLite**    | Structured data, queries, single user. |
| **Postgres / etc.** | Multi-user, hosted, scale. |

### The pattern

```python
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

PELLETS: list[str] = _load()   # at server startup, read existing pellets
```

Then every write tool calls `_save(PELLETS)` after mutating state.

### Why a Path object
`pathlib.Path` works the same way on macOS, Linux, and Windows. Hardcoding
`"pellets.json"` here resolves *relative to where the server was started*
— in production you'd use `Path.home() / ".pellet-tracker.json"` or read
the path from env.
"""

W1L4_DEBRIEF = """\
**Power-pellet unlocked — World 1 complete!**

- MCP servers persist state with a backing store (JSON / SQLite / DB).
- Read once at startup, save after every write.
- `pathlib.Path` keeps file handling cross-platform.

Your Pellet Tracker now actually **remembers** habits. Welcome to World 2.
"""


# ════════════════════════════════════════════════════════════════════════
# WORLD 2 — THE TOOL MAZE
# ════════════════════════════════════════════════════════════════════════

W2L1_STARTER = '''"""W2-L1: Teach Claude what your params mean.

Use `Annotated[str, Field(description="...")]` for `log_pellet`\'s `habit`
parameter. The description must include the substring "name of the habit".
"""
import json
from pathlib import Path
from typing import Annotated

from mcp.server.fastmcp import FastMCP
from pydantic import Field

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


# TODO: replace the bare `habit: str` with an annotated version, e.g.:
#   habit: Annotated[str, Field(description="The name of the habit, e.g. \'reading\'")]
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

W2L1_BRIEF = """\
## Why descriptions matter

Claude doesn't pick tools by guessing — it reads each tool's name,
description, and parameter descriptions, then decides which one fits the
task. **Vague descriptions = bad tool choices.**

So far our `habit: str` parameter has no description. Claude knows the
type but not what it means.

### The standard pattern: `Annotated` + `Field`

```python
from typing import Annotated
from pydantic import Field

@mcp.tool()
def log_pellet(
    habit: Annotated[str, Field(description="The name of the habit, e.g. 'reading'")],
) -> str: ...
```

`Annotated` attaches metadata to a type without changing how Python uses
it. `Field` from pydantic carries the description through to the generated
JSON Schema.

### What Claude actually sees
```json
"properties": {
  "habit": {
    "type": "string",
    "description": "The name of the habit, e.g. 'reading'"
  }
}
```

Much easier to call correctly.
"""

W2L1_DEBRIEF = """\
**Power-pellet unlocked:**

- Claude reads parameter descriptions to decide *how* to call a tool.
- `Annotated[T, Field(description=...)]` is the modern way.
- Good descriptions are the single biggest factor in good tool choices.
"""


W2L2_STARTER = '''"""W2-L2: Annotate the safe tools.

Mark `list_pellets` AND `count_pellets` with annotations={"readOnlyHint": True}.
"""
import json
from pathlib import Path
from typing import Annotated

from mcp.server.fastmcp import FastMCP
from pydantic import Field

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
def log_pellet(
    habit: Annotated[str, Field(description="The name of the habit to log.")],
) -> str:
    PELLETS.append(habit)
    _save(PELLETS)
    return f"Logged: {habit}"


# TODO: add  annotations={"readOnlyHint": True}  to BOTH decorators below.
@mcp.tool()
def list_pellets() -> list[str]:
    return PELLETS


@mcp.tool()
def count_pellets(habit: str) -> int:
    return sum(1 for p in PELLETS if p == habit)


if __name__ == "__main__":
    mcp.run()
'''

W2L2_BRIEF = """\
## Tool annotations — safety hints for clients

Tools can carry **annotations** that tell clients (Claude Desktop, Claude
Code) how safe a tool is to run.

| Hint | Meaning |
|------|---------|
| `readOnlyHint: true`    | Tool does not change state. Claude can call freely. |
| `destructiveHint: true` | Tool may delete or alter data. Worth confirming. |
| `idempotentHint: true`  | Same input always produces the same effect. |
| `openWorldHint: true`   | Tool may touch external systems (APIs, web). |

```python
@mcp.tool(annotations={"readOnlyHint": True})
def list_pellets() -> list[str]: ...
```

### Why this matters for Claude
By default Claude Code asks before running any tool. `readOnlyHint=True`
lets the user configure Claude to auto-run it — dramatically improves flow
for reads (checking, browsing, summarizing) while keeping writes deliberate.

### Be honest
These are **hints**, not enforcement. A `readOnlyHint=True` tool that
actually mutates state erodes trust fast.
"""

W2L2_DEBRIEF = """\
**Power-pellet unlocked:**

- Annotations are safety hints clients use to decide auto-run policy.
- Four standards: `readOnlyHint`, `destructiveHint`, `idempotentHint`, `openWorldHint`.
- Be honest about what each tool actually does.
"""


W2L3_STARTER = '''"""W2-L3: Structured output.

So far `count_pellets` returns a plain int. Make it return a typed
`StreakInfo` object so Claude can see all stats at once.

Replace `count_pellets` to return a StreakInfo BaseModel with three
fields: habit (str), total (int), longest_run (int).

For now you can compute longest_run the same as total — we\'ll refine
in later worlds.
"""
import json
from pathlib import Path
from typing import Annotated

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

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


# TODO: define a `StreakInfo` BaseModel class with three fields:
#       habit: str
#       total: int
#       longest_run: int


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


# TODO: change the return type to StreakInfo and return an instance like:
#   total = sum(1 for p in PELLETS if p == habit)
#   return StreakInfo(habit=habit, total=total, longest_run=total)
@mcp.tool(annotations={"readOnlyHint": True})
def count_pellets(habit: str) -> int:
    return sum(1 for p in PELLETS if p == habit)


if __name__ == "__main__":
    mcp.run()
'''

W2L3_BRIEF = """\
## Structured tool output

Returning a `str` works but it's lossy — Claude has to parse the string
back into structure. **Structured output** lets a tool return typed data
that Claude can read directly.

### The shape

```python
from pydantic import BaseModel

class StreakInfo(BaseModel):
    habit: str
    total: int
    longest_run: int

@mcp.tool()
def count_pellets(habit: str) -> StreakInfo:
    n = sum(1 for p in PELLETS if p == habit)
    return StreakInfo(habit=habit, total=n, longest_run=n)
```

FastMCP generates an `outputSchema` from the Pydantic model and returns
the data in both the legacy text block (a JSON dump) AND in a new field
called `structuredContent`.

### What Claude sees

```json
{
  "content": [{"type": "text", "text": "{\\"habit\\":\\"reading\\",\\"total\\":3,...}"}],
  "structuredContent": {"habit": "reading", "total": 3, "longest_run": 3}
}
```

Plus an `outputSchema` on the tool definition so Claude knows the shape
before calling.

### When to use it
- Numeric stats, multi-field returns, anything you'd otherwise stringify.
- Skip for free-form text responses (logs, messages, summaries).
"""

W2L3_DEBRIEF = """\
**Power-pellet unlocked:**

- Pydantic return types → automatic `outputSchema` + `structuredContent`.
- Lets Claude consume typed data without re-parsing strings.
- Standard since MCP protocol version **2025-06-18**.
"""


W2L4_STARTER = '''"""W2-L4: Graceful errors.

What should happen if someone calls `log_pellet("")` with an empty string?
Right now we\'d cheerfully log an empty habit forever. Add a guard.

Modify `log_pellet` to raise `ValueError("habit cannot be empty")` when
`habit` is empty or only whitespace. FastMCP turns Python exceptions
into MCP error responses with `isError: true`.
"""
import json
from pathlib import Path
from typing import Annotated

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

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


class StreakInfo(BaseModel):
    habit: str
    total: int
    longest_run: int


@mcp.tool()
def whoami(name: str) -> str:
    return f"Welcome to your Pellet Tracker, {name}!"


# TODO: at the start of log_pellet, if `habit.strip() == ""`,
#       raise ValueError("habit cannot be empty").
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

W2L4_BRIEF = """\
## Errors that Claude can recover from

A naive tool just trusts every input. A good tool **validates** and
surfaces failures in a way Claude can recover from.

### Three ways to fail

| Approach | Wire result | When to use |
|----------|-------------|-------------|
| `raise ValueError("bad input")` | MCP error response, `isError: true` | Validation, missing data |
| `return "Error: ..."` | Plain text content, `isError: false` | Soft failures you want Claude to talk about |
| `raise ToolError("...")` | Same as ValueError, slightly more idiomatic | Same use case, FastMCP-native |

### The pattern

```python
@mcp.tool()
def log_pellet(habit: str) -> str:
    if not habit.strip():
        raise ValueError("habit cannot be empty")
    PELLETS.append(habit)
    return f"Logged: {habit}"
```

FastMCP catches the exception, formats it as an MCP-spec error, and sets
`isError: true` on the result. Claude sees the error text and can decide
to retry, ask the user for clarification, or surface the problem.

### Don't swallow real bugs
Reserve raising for **expected** failure modes (bad input, missing
resource). Let unexpected exceptions (KeyError, AttributeError) propagate
— they should crash the server in dev so you can fix them.
"""

W2L4_DEBRIEF = """\
**Power-pellet unlocked — World 2 complete!**

- `raise ValueError(...)` in FastMCP becomes an MCP error response (`isError: true`).
- Validate inputs at the top of every tool; reject empty / bad data.
- Reserve raising for *expected* failure modes — let real bugs crash.

Your tools now play well with Claude. Next: data Claude can **browse**.
"""


# ════════════════════════════════════════════════════════════════════════
# WORLD 3 — RESOURCE TUNNELS
# ════════════════════════════════════════════════════════════════════════

W3L1_STARTER = '''"""W3-L1: Your first resource.

Add a static resource at URI `pellets://today` that returns
`json.dumps(PELLETS)`.

    @mcp.resource("pellets://today")
    def todays_pellets() -> str:
        return json.dumps(PELLETS)
"""
import json
from pathlib import Path
from typing import Annotated

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

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


# TODO: add a resource at  pellets://today  that returns json.dumps(PELLETS).


if __name__ == "__main__":
    mcp.run()
'''

W3L1_BRIEF = """\
## Tools vs Resources — the two halves of MCP

You've been writing **tools** — Claude *calls* them, things happen.
Now you'll write a **resource** — Claude *reads* it, like opening a file.

| Tools           | Resources         |
|-----------------|-------------------|
| Imperative      | Read-only data    |
| `tools/call`    | `resources/read`  |
| Like a function | Like a URL        |
| Has side effects| No side effects   |

```python
@mcp.resource("pellets://today")
def todays_pellets() -> str:
    return json.dumps(PELLETS)
```

### URIs, not function names
Resources are identified by **URI** — any scheme you invent:

- `pellets://today` (static — always the same address)
- `pellets://habit/{name}` (templated — next level)
- `file:///path/to/something` (filesystem)
- `https://...` (web)

### Why both exist
If the user says *"summarize my week,"* Claude could call a `get_summary`
tool — or it could **read** `pellets://this-week` and generate the summary
itself. Resources let Claude **browse your state** without you exposing a
tool for every possible read.
"""

W3L1_DEBRIEF = """\
**Power-pellet unlocked:**

- Resources are **read-only data** Claude browses via URI.
- Tools are imperative; resources are like files.
- `@mcp.resource("scheme://path")` is the FastMCP decorator.
"""


W3L2_STARTER = '''"""W3-L2: Templated resources.

Static resources work for "today's pellets" — but what about
"pellets for a specific habit"? Use a URI template:

    @mcp.resource("pellets://habit/{name}")
    def pellets_for_habit(name: str) -> str:
        return json.dumps([p for p in PELLETS if p == name])

The `{name}` placeholder becomes a function parameter.
"""
import json
from pathlib import Path
from typing import Annotated

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

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


@mcp.resource("pellets://today")
def todays_pellets() -> str:
    return json.dumps(PELLETS)


# TODO: add a templated resource  pellets://habit/{name}
#       that returns the entries for that specific habit as JSON.


if __name__ == "__main__":
    mcp.run()
'''

W3L2_BRIEF = """\
## URI templates — path parameters for resources

Static URIs like `pellets://today` are great for fixed endpoints. For
parameterized data — "pellets for habit X" — use a **URI template** with
`{placeholders}`.

```python
@mcp.resource("pellets://habit/{name}")
def pellets_for_habit(name: str) -> str:
    return json.dumps([p for p in PELLETS if p == name])
```

The `{name}` in the URI matches a function parameter. When Claude asks
for `pellets://habit/running`, FastMCP routes the request, extracts
`name="running"`, and calls your function.

### How clients discover templates
Clients call `resources/templates/list` to see the URI templates the
server offers. Then they fill in the placeholders and call
`resources/read` with the substituted URI.

### Multiple placeholders work too
`pellets://habit/{name}/week/{offset}` is valid. Each placeholder becomes
a function parameter.

### Static vs templated
- Static (`pellets://today`) shows up in `resources/list` as a concrete URI.
- Templated (`pellets://habit/{name}`) shows up in `resources/templates/list` with the placeholders intact.
"""

W3L2_DEBRIEF = """\
**Power-pellet unlocked — World 3 complete!**

- URI templates let resources accept path parameters: `pellets://habit/{name}`.
- `{name}` becomes a function param; FastMCP routes the read for you.
- Discovered via `resources/templates/list` (separate from `resources/list`).
"""


# ════════════════════════════════════════════════════════════════════════
# WORLD 4 — PROMPT POWER-PELLETS
# ════════════════════════════════════════════════════════════════════════

W4L1_STARTER = '''"""W4-L1: Your first prompt.

Add `@mcp.prompt()` for `morning_check_in()` that returns a message
mentioning "pellets".
"""
import json
from pathlib import Path
from typing import Annotated

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

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


@mcp.resource("pellets://today")
def todays_pellets() -> str:
    return json.dumps(PELLETS)


@mcp.resource("pellets://habit/{name}")
def pellets_for_habit(name: str) -> str:
    return json.dumps([p for p in PELLETS if p == name])


# TODO: add a prompt `morning_check_in()` returning text that mentions "pellets".


if __name__ == "__main__":
    mcp.run()
'''

W4L1_BRIEF = """\
## Prompts — reusable workflows

Tools and resources are **capabilities**. Prompts are **workflows** —
templates the user (or Claude) invokes by name.

```python
@mcp.prompt()
def morning_check_in() -> str:
    return "Good morning! Which pellets will you eat today?"
```

### What this gives you
In Claude Desktop and Claude Code, prompts appear in the slash-command
menu. The user types `/morning_check_in` and the prompt text gets inserted
as if they typed it — letting Claude pick up the workflow.

### The cheat sheet
- **Tool** = function Claude calls
- **Resource** = data Claude reads
- **Prompt** = workflow the *user* invokes

### Where this shines
Common chores: a morning ritual, a weekly retro, a "summarize my day"
template. You're packaging up your favorite Claude interactions so they're
one keystroke away.
"""

W4L1_DEBRIEF = """\
**Power-pellet unlocked:**

- Prompts are reusable workflows users invoke by name (slash-commands).
- `@mcp.prompt()` is the FastMCP decorator; the return value is message text.
- Tools / Resources / Prompts = capability / data / workflow.
"""


W4L2_STARTER = '''"""W4-L2: Prompts with arguments.

Add a parameterized prompt `weekly_recap(week_offset: int = 0)` that
returns a message referencing the right time window.

For `week_offset=0` mention "past 7 days". For `week_offset=1` mention
"past 14 days" (offset doubles back). The grader checks for the
substring "14" when called with week_offset=1.
"""
import json
from pathlib import Path
from typing import Annotated

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

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


@mcp.resource("pellets://today")
def todays_pellets() -> str:
    return json.dumps(PELLETS)


@mcp.resource("pellets://habit/{name}")
def pellets_for_habit(name: str) -> str:
    return json.dumps([p for p in PELLETS if p == name])


@mcp.prompt()
def morning_check_in() -> str:
    return "Good morning! Which pellets will you eat today?"


# TODO: add a prompt `weekly_recap(week_offset: int = 0)` whose returned
#       text mentions `(7 + week_offset * 7)` days.
#       e.g. f"Summarize my pellets from the past {7 + week_offset * 7} days."


if __name__ == "__main__":
    mcp.run()
'''

W4L2_BRIEF = """\
## Parameterized prompts

Plain prompts work for fixed messages. For dynamic workflows, prompts can
take **typed arguments** — they show up as slash-command arguments in
clients.

```python
@mcp.prompt()
def weekly_recap(week_offset: int = 0) -> str:
    days = 7 + week_offset * 7
    return f"Summarize my pellets from the past {days} days."
```

### How clients see it
Calling `prompts/list` returns:

```json
{
  "name": "weekly_recap",
  "description": "...",
  "arguments": [
    {"name": "week_offset", "required": false}
  ]
}
```

Claude Desktop renders `/weekly_recap` with an input for `week_offset`.
Defaults make the argument optional.

### Tip: completion
You can also expose **completion** for prompt arguments — letting clients
suggest values to the user. Out of scope for this level, but the
`completion/complete` request is how it's wired.
"""

W4L2_DEBRIEF = """\
**Power-pellet unlocked — World 4 complete!**

- Prompts take typed arguments → slash-command args in clients.
- Defaults make arguments optional.
- Completion (`completion/complete`) lets clients suggest argument values.

Halfway through. Next: **bidirectional** MCP — your server talks back.
"""


# ════════════════════════════════════════════════════════════════════════
# WORLD 5 — BIDIRECTIONAL MCP  (sampling / elicitation / progress)
# ════════════════════════════════════════════════════════════════════════

W5L1_STARTER = '''"""W5-L1: Sampling — your server asks Claude to think.

So far Claude calls your tools. But what if a tool needs to *use Claude*
itself? That\'s **sampling** — your server asks the client to run an LLM
completion on its behalf.

Implement `analyze_my_week(ctx: Context)` so it asks Claude (via the
client) to write a brief reflection on the current PELLETS list.

The grader for this level only checks your source code — actually
exercising sampling needs a real Claude. To run it for real, deploy this
server to Claude Desktop (World 6) and call the tool.
"""
import json
from pathlib import Path
from typing import Annotated

from mcp.server.fastmcp import FastMCP, Context
from mcp.types import SamplingMessage, TextContent
from pydantic import BaseModel, Field

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


@mcp.resource("pellets://today")
def todays_pellets() -> str:
    return json.dumps(PELLETS)


@mcp.resource("pellets://habit/{name}")
def pellets_for_habit(name: str) -> str:
    return json.dumps([p for p in PELLETS if p == name])


@mcp.prompt()
def morning_check_in() -> str:
    return "Good morning! Which pellets will you eat today?"


@mcp.prompt()
def weekly_recap(week_offset: int = 0) -> str:
    days = 7 + week_offset * 7
    return f"Summarize my pellets from the past {days} days."


# TODO: implement this tool using ctx.session.create_message(...).
# Required: the function body must call  ctx.session.create_message
# Hint:
#   result = await ctx.session.create_message(
#       messages=[SamplingMessage(role="user",
#           content=TextContent(type="text",
#               text=f"Reflect briefly on these pellets: {PELLETS}"))],
#       max_tokens=200,
#   )
#   return result.content.text
@mcp.tool()
async def analyze_my_week(ctx: Context) -> str:
    """Ask Claude to reflect on the user\'s pellet log."""
    pass


if __name__ == "__main__":
    mcp.run()
'''

W5L1_BRIEF = """\
## Sampling — your server asks Claude to think

Up to now the protocol has been one-way: Claude calls your tools. Sometimes
a tool needs to *use Claude itself* — to summarize, classify, draft, or
reason. That's what **sampling** is for.

```python
from mcp.server.fastmcp import Context
from mcp.types import SamplingMessage, TextContent

@mcp.tool()
async def analyze_my_week(ctx: Context) -> str:
    result = await ctx.session.create_message(
        messages=[SamplingMessage(
            role="user",
            content=TextContent(type="text",
                text=f"Reflect on these pellets: {PELLETS}"))],
        max_tokens=200,
    )
    return result.content.text
```

### Why this exists
Without sampling, every server that needed LLM intelligence would have to
ship its own model + API key + provider abstraction. With sampling, the
server stays **LLM-agnostic** — it asks the client to handle inference,
and the client uses whatever the user is already paying for.

### Context, in one line
`ctx: Context` is auto-injected by FastMCP when you declare it as the
first parameter (or after positional args). It gives you access to the
session, logging, progress, elicitation — all the bidirectional features.

### Async required
Sampling waits on a round-trip with the client. The tool must be `async`.
"""

W5L1_DEBRIEF = """\
**Power-pellet unlocked:**

- `ctx.session.create_message(...)` lets the server invoke the client's LLM.
- Tools stay LLM-agnostic — the client handles inference + billing.
- Tools that use sampling must be `async` and accept `ctx: Context`.

The grader source-checks your code; deploy to Claude Desktop (World 6) to see it actually run.
"""


W5L2_STARTER = '''"""W5-L2: Elicitation — your server asks the user.

What if a tool needs follow-up info from the user mid-call? **Elicitation**
lets your server send the user a question with a schema, and pause until
they reply.

Implement `start_habit(ctx: Context)` so it asks the user "What habit
would you like to start tracking?" and returns a confirmation.

Like sampling, the grader checks source only — deploy for the real flow.
"""
import json
from pathlib import Path
from typing import Annotated

from mcp.server.fastmcp import FastMCP, Context
from mcp.types import SamplingMessage, TextContent
from pydantic import BaseModel, Field

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


@mcp.resource("pellets://today")
def todays_pellets() -> str:
    return json.dumps(PELLETS)


@mcp.resource("pellets://habit/{name}")
def pellets_for_habit(name: str) -> str:
    return json.dumps([p for p in PELLETS if p == name])


@mcp.prompt()
def morning_check_in() -> str:
    return "Good morning! Which pellets will you eat today?"


@mcp.prompt()
def weekly_recap(week_offset: int = 0) -> str:
    days = 7 + week_offset * 7
    return f"Summarize my pellets from the past {days} days."


@mcp.tool()
async def analyze_my_week(ctx: Context) -> str:
    result = await ctx.session.create_message(
        messages=[SamplingMessage(role="user",
            content=TextContent(type="text",
                text=f"Reflect briefly on these pellets: {PELLETS}"))],
        max_tokens=200,
    )
    return result.content.text


# Define the shape of the answer we expect. FastMCP elicitation uses a
# Pydantic model class (not a raw JSON Schema dict) for type safety.
class _HabitPrompt(BaseModel):
    habit: str


# TODO: implement this tool using ctx.elicit(...).
# Required: the function body must call  ctx.elicit
# Hint:
#   result = await ctx.elicit(message="What habit?", schema=_HabitPrompt)
#   if result.action != "accept":
#       return "Cancelled."
#   habit = result.data.habit
#   PELLETS.append(habit)
#   _save(PELLETS)
#   return f"Started tracking: {habit}"
@mcp.tool()
async def start_habit(ctx: Context) -> str:
    """Ask the user for a habit to track, then start tracking it."""
    pass


if __name__ == "__main__":
    mcp.run()
'''

W5L2_BRIEF = """\
## Elicitation — your server asks the user

Sometimes a tool needs more info before it can do its job. **Elicitation**
lets your server send a structured question to the user mid-call and wait
for a typed response.

```python
from pydantic import BaseModel

class HabitPrompt(BaseModel):
    habit: str

@mcp.tool()
async def start_habit(ctx: Context) -> str:
    result = await ctx.elicit(
        message="What habit would you like to track?",
        schema=HabitPrompt,
    )
    if result.action != "accept":
        return "Cancelled."
    return f"Tracking {result.data.habit}"
```

### Why a Pydantic model, not a JSON Schema?
FastMCP wants type safety end-to-end: you define the answer's shape as a
**Pydantic model class**, FastMCP generates the JSON Schema for the wire,
and on the way back it validates + parses the response into your model —
so `result.data` is a real typed object, not a dict you have to defensively
unpack.

### How it lands in Claude Desktop
Claude Desktop renders a modal form built from your schema. The user can
**accept**, **decline**, or **cancel** — the response's `action` tells
you which. Only `action == "accept"` gives you `result.data`.

### When to use it
- When the user's intent is clear but a parameter is missing.
- When you need explicit confirmation for a sensitive action.

### When NOT to use it
- For values Claude can infer from context — use a regular tool argument.
- For every tool call — elicitation interrupts flow.
"""

W5L2_DEBRIEF = """\
**Power-pellet unlocked:**

- `ctx.elicit(...)` lets the server ask the user for typed input mid-call.
- The user can accept, decline, or cancel — check `result.action`.
- Pairs well with tools that need missing info to proceed.
"""


W5L3_STARTER = '''"""W5-L3: Progress notifications.

For long-running tools, you should send progress updates so the user
knows the tool isn\'t hung. MCP defines `notifications/progress` for
exactly this — and `ctx.report_progress(...)` makes it one line.

Implement `bulk_import(ctx: Context, count: int)` that imports `count`
pellets named "imported_1", "imported_2", ..., calling
`ctx.report_progress(progress=i+1, total=count)` inside the loop.
"""
import json
from pathlib import Path
from typing import Annotated

from mcp.server.fastmcp import FastMCP, Context
from mcp.types import SamplingMessage, TextContent
from pydantic import BaseModel, Field

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


@mcp.resource("pellets://today")
def todays_pellets() -> str:
    return json.dumps(PELLETS)


@mcp.resource("pellets://habit/{name}")
def pellets_for_habit(name: str) -> str:
    return json.dumps([p for p in PELLETS if p == name])


@mcp.prompt()
def morning_check_in() -> str:
    return "Good morning! Which pellets will you eat today?"


@mcp.prompt()
def weekly_recap(week_offset: int = 0) -> str:
    days = 7 + week_offset * 7
    return f"Summarize my pellets from the past {days} days."


@mcp.tool()
async def analyze_my_week(ctx: Context) -> str:
    result = await ctx.session.create_message(
        messages=[SamplingMessage(role="user",
            content=TextContent(type="text",
                text=f"Reflect briefly on these pellets: {PELLETS}"))],
        max_tokens=200,
    )
    return result.content.text


class _HabitPrompt(BaseModel):
    habit: str


@mcp.tool()
async def start_habit(ctx: Context) -> str:
    result = await ctx.elicit(
        message="What habit would you like to start tracking?",
        schema=_HabitPrompt,
    )
    if result.action != "accept":
        return "Cancelled."
    habit = result.data.habit
    PELLETS.append(habit)
    _save(PELLETS)
    return f"Started tracking: {habit}"


# TODO: implement this tool. For i in range(count):
#         await ctx.report_progress(progress=i+1, total=count)
#         PELLETS.append(f"imported_{i+1}")
#       After the loop, _save(PELLETS) and return f"Imported {count}".
# Required: the function body must call  ctx.report_progress
@mcp.tool()
async def bulk_import(ctx: Context, count: int) -> str:
    """Import a batch of habits, reporting progress."""
    pass


if __name__ == "__main__":
    mcp.run()
'''

W5L3_BRIEF = """\
## Progress notifications — keeping the user informed

A tool that takes 30 seconds with no feedback feels broken. MCP defines
**progress notifications** so long-running tools can stream incremental
updates to the client.

```python
@mcp.tool()
async def bulk_import(ctx: Context, count: int) -> str:
    for i in range(count):
        await ctx.report_progress(progress=i + 1, total=count)
        PELLETS.append(f"imported_{i + 1}")
    _save(PELLETS)
    return f"Imported {count}"
```

### What lands on the wire
Each call emits a `notifications/progress` message:

```json
{"jsonrpc":"2.0","method":"notifications/progress",
 "params":{"progressToken":"...", "progress":3, "total":10}}
```

Clients use these to render progress bars, ETA estimates, or just
"working… 3 of 10".

### When to use it
- Imports / bulk operations
- Long API calls (after fetching, before parsing)
- Multi-stage workflows ("fetching… analyzing… saving…")

### `progress` and `total`
`progress` is current count; `total` is optional. Send both when you know
the total; just `progress` (a monotonically increasing value) when you
don't.
"""

W5L3_DEBRIEF = """\
**Power-pellet unlocked — World 5 complete!**

- `ctx.report_progress(progress, total)` streams updates to the client.
- Use for any tool that takes >2 seconds.
- World 5 covered the **bidirectional** half of MCP: sampling, elicitation, progress.

Up next: actually wiring your server into real Claude.
"""


# ════════════════════════════════════════════════════════════════════════
# WORLD 6 — ESCAPE TO CLAUDE
# ════════════════════════════════════════════════════════════════════════

W6L1_STARTER = '''"""W6-L1: Plug into Claude Desktop.

Time for instant gratification — wire your Pellet Tracker into the real
Claude Desktop. Fill in the CLAUDE_DESKTOP_SNIPPET constant with a valid
config block registering a server named "pellet-tracker".

Required keys: mcpServers → pellet-tracker → command, args
"""
import json

# TODO: replace the empty body with a valid config snippet like:
# {
#   "mcpServers": {
#     "pellet-tracker": {
#       "command": "python",
#       "args": ["/absolute/path/to/server.py"]
#     }
#   }
# }
CLAUDE_DESKTOP_SNIPPET = """
{
}
"""

# The grader only checks the string above. The full server below is the
# same one you\'ve been building — copy it into a real file when deploying.

from pathlib import Path
from typing import Annotated
from mcp.server.fastmcp import FastMCP, Context
from mcp.types import SamplingMessage, TextContent
from pydantic import BaseModel, Field

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


@mcp.resource("pellets://today")
def todays_pellets() -> str:
    return json.dumps(PELLETS)


@mcp.resource("pellets://habit/{name}")
def pellets_for_habit(name: str) -> str:
    return json.dumps([p for p in PELLETS if p == name])


@mcp.prompt()
def morning_check_in() -> str:
    return "Good morning! Which pellets will you eat today?"


@mcp.prompt()
def weekly_recap(week_offset: int = 0) -> str:
    days = 7 + week_offset * 7
    return f"Summarize my pellets from the past {days} days."


if __name__ == "__main__":
    mcp.run()
'''

W6L1_BRIEF = """\
## Plugging into Claude Desktop

Claude Desktop discovers MCP servers via a JSON config file:

```
~/Library/Application Support/Claude/claude_desktop_config.json
```

The config file's `mcpServers` map names each server and tells Claude
Desktop how to start it:

```json
{
  "mcpServers": {
    "pellet-tracker": {
      "command": "python",
      "args": ["/absolute/path/to/server.py"]
    }
  }
}
```

When Claude Desktop launches, it spawns each registered server as a
subprocess with the given command/args and connects over **stdio** —
the same JSON-RPC protocol you've been watching in the Inspector.

### After editing the config
Fully quit and restart Claude Desktop. The new server should appear in
the tools/resources/prompts menu.

### Tip: use absolute paths
Relative paths get resolved from Claude Desktop's working directory,
which isn't where you think. Always use absolute paths in `args`.
"""

W6L1_DEBRIEF = """\
**Power-pellet unlocked:**

- Claude Desktop reads `claude_desktop_config.json`.
- Each entry under `mcpServers` defines `command` + `args`.
- Restart Claude Desktop after edits.
- Use absolute paths.
"""


W6L2_STARTER = '''"""W6-L2: Plug into Claude Code.

Claude Code uses a different (but similar) config file: `.mcp.json` at
the repo root. Fill in CLAUDE_CODE_MCP_JSON with a valid project-scoped
config that registers a server named "pellet-tracker".

Required keys: mcpServers → pellet-tracker → command, args
"""
import json

# TODO: write a valid .mcp.json string. Same shape as Claude Desktop\'s
# config — `mcpServers` map with `command` and `args`. Example:
# {
#   "mcpServers": {
#     "pellet-tracker": {
#       "command": "python",
#       "args": ["./server.py"]
#     }
#   }
# }
CLAUDE_CODE_MCP_JSON = """
{
}
"""

# You could also have used the CLI:
#   claude mcp add pellet-tracker --command python --args ./server.py
# which writes the same config to .mcp.json for you.
'''

W6L2_BRIEF = """\
## Plugging into Claude Code

Claude Code (the CLI) is the other place you'll register MCP servers.
Two scopes:

| File | Scope |
|------|-------|
| `.mcp.json` at the repo root        | **Project** — checked in, shared with collaborators |
| `~/.claude.json`                    | **Global** — your personal install across all projects |

The shape is the **same** as Claude Desktop's `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "pellet-tracker": {
      "command": "python",
      "args": ["./server.py"]
    }
  }
}
```

### CLI shortcut
Instead of hand-editing JSON, use the `claude mcp` CLI:

```bash
claude mcp add pellet-tracker --command python --args ./server.py
```

Or for project scope:

```bash
claude mcp add --scope project pellet-tracker --command python --args ./server.py
```

### Why project scope rocks
Project-scoped servers live in the repo. Anyone who clones it gets the
same MCP wiring — perfect for team workflows or showing off your server
in OSS projects.
"""

W6L2_DEBRIEF = """\
**Power-pellet unlocked:**

- Claude Code uses `.mcp.json` (project) or `~/.claude.json` (global).
- Same shape as Claude Desktop's config.
- `claude mcp add` is the CLI shortcut.
- Project-scoped servers travel with the repo.
"""


W6L3_STARTER = '''"""W6-L3: Debug with the MCP Inspector.

Before you wire a server into Claude, the official debugging tool is the
**MCP Inspector** — a web UI that connects to your server and lets you
exercise every tool/resource/prompt.

Fill in MCP_INSPECTOR_CMD with the shell command that launches the
inspector against your local server. The grader checks for the substring
"@modelcontextprotocol/inspector".
"""

# TODO: replace the empty string with a valid command like:
#   npx @modelcontextprotocol/inspector python ./server.py
# or:
#   npx @modelcontextprotocol/inspector --command python --args ./server.py
MCP_INSPECTOR_CMD = ""

# Usage notes (for after you deploy):
# 1. Run the command in your terminal.
# 2. A browser tab opens to http://localhost:6274 with a UI.
# 3. Click "Connect" — the Inspector spawns your server and talks stdio to it.
# 4. Use the Tools / Resources / Prompts tabs to call each one.
# 5. The Messages panel shows raw JSON-RPC, just like your in-app Inspector.
'''

W6L3_BRIEF = """\
## The MCP Inspector — your debugging best friend

Before you wire a server into Claude, debug it with the **MCP Inspector**:
a web UI that connects to your server, lets you call every tool/resource/
prompt, and shows the raw JSON-RPC. Think of it as Postman for MCP.

### Launch it

```bash
npx @modelcontextprotocol/inspector python ./server.py
```

That spawns your server, opens a browser tab to `http://localhost:6274`,
and connects over stdio. You'll see:

- Tools panel — list, inspect schemas, call each one with custom args
- Resources panel — list, read, browse the URI templates
- Prompts panel — list, get
- Messages panel — raw JSON-RPC traffic (just like in this academy)

### Why it matters
A Claude-restart loop is slow. With the Inspector you can iterate in
seconds — edit your server, restart the Inspector, re-test. Save Claude
Desktop for end-to-end validation.

### When to reach for it
- After any non-trivial code change to your server
- When a tool works in the Inspector but not in Claude (rare — but tells you it's a wiring/config issue, not a server bug)
- When learning a new MCP feature

It's the single most useful tool in the MCP toolkit.
"""

W6L3_DEBRIEF = """\
**Power-pellet unlocked — World 6 complete!**

- `npx @modelcontextprotocol/inspector` is the canonical debugging UI.
- Lets you exercise every tool/resource/prompt without restarting Claude.
- Shows raw JSON-RPC, just like the Inspector you've been using here.
- **Use it after every meaningful change** before testing in real Claude.

Two worlds left. Next: going public.
"""


# ════════════════════════════════════════════════════════════════════════
# WORLD 7 — GOING PUBLIC  (HTTP transport, API key, OAuth)
# ════════════════════════════════════════════════════════════════════════

W7L1_STARTER = '''"""W7-L1: Streamable HTTP transport.

stdio works for local servers but useless for remote ones. The modern
remote transport is **Streamable HTTP**.

Change `mcp.run()` to `mcp.run(transport="streamable-http")` in the
__main__ block. (Source-check only — we won\'t actually start an HTTP
server inside the academy.)
"""
import json
from pathlib import Path
from typing import Annotated

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

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


@mcp.resource("pellets://today")
def todays_pellets() -> str:
    return json.dumps(PELLETS)


@mcp.resource("pellets://habit/{name}")
def pellets_for_habit(name: str) -> str:
    return json.dumps([p for p in PELLETS if p == name])


@mcp.prompt()
def morning_check_in() -> str:
    return "Good morning! Which pellets will you eat today?"


if __name__ == "__main__":
    # TODO: pass  transport="streamable-http"  as an argument to mcp.run()
    mcp.run()
'''

W7L1_BRIEF = """\
## Transports — how the wire works

You've been talking **stdio** — fine for one local user, useless for
remote access. MCP defines two transports:

| Transport         | When to use |
|-------------------|-------------|
| **stdio**         | Local servers spawned by Claude Desktop / Claude Code |
| **Streamable HTTP** | Remote servers hosted anywhere reachable by URL |

### Why Streamable HTTP, not SSE
The original MCP spec had a separate HTTP+SSE transport. That's now
**deprecated**. The modern spec defines **Streamable HTTP** — a single
HTTP endpoint that supports request/response *and* server-pushed
notifications over the same connection.

```python
if __name__ == "__main__":
    mcp.run(transport="streamable-http")
```

That's it. Your server now exposes its tools/resources/prompts over HTTP
— talking the same JSON-RPC protocol, framed in HTTP requests.

### What didn't change
Your tools, resources, and prompts are identical. The wire changed; the
business logic didn't.

### What did change
Auth becomes essential — anyone who can reach the URL can call your tools.
Next two levels address that.
"""

W7L1_DEBRIEF = """\
**Power-pellet unlocked:**

- MCP supports two transports: **stdio** (local) and **Streamable HTTP** (remote).
- SSE is **deprecated** — use Streamable HTTP for any HTTP-based server.
- One keyword arg switches transports; your tools/resources/prompts don't change.
- HTTP exposure means **you must add auth** — next.
"""


W7L2_STARTER = '''"""W7-L2: API key auth (the simple gate).

Add an api_key parameter to log_pellet. Reject calls where
api_key != "wakawaka" by raising ValueError("Invalid API key").
"""
import json
from pathlib import Path
from typing import Annotated

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

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


class StreakInfo(BaseModel):
    habit: str
    total: int
    longest_run: int


@mcp.tool()
def whoami(name: str) -> str:
    return f"Welcome to your Pellet Tracker, {name}!"


# TODO: add an `api_key: str` parameter and reject calls where
#       api_key != "wakawaka" by raising ValueError("Invalid API key").
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


@mcp.resource("pellets://today")
def todays_pellets() -> str:
    return json.dumps(PELLETS)


if __name__ == "__main__":
    mcp.run()
'''

W7L2_BRIEF = """\
## API key auth — the simple gate

Once your server is reachable over HTTP, you need to authenticate callers.
The fastest gate is an API key check inside each write tool.

```python
@mcp.tool()
def log_pellet(habit: str, api_key: str) -> str:
    if api_key != "wakawaka":
        raise ValueError("Invalid API key")
    PELLETS.append(habit)
    return f"Logged: {habit}"
```

When the key is wrong, raising returns an MCP error response with
`isError: true`. Claude (or the Inspector) sees the error and can ask
the user to provide the right key.

### Why this is a stopgap
- The key flows through tool arguments — same place as user input, easy to leak in logs.
- No expiration, rotation, or per-user scoping.
- No multi-user model — one secret for everyone.

It's fine for personal projects, hackathon demos, or single-tenant
internal tools. For anything else, use OAuth (next level).

### Real production pattern
Read the key from an env var or secret store, not a constant:

```python
import os
SERVER_API_KEY = os.environ["PELLET_API_KEY"]

if api_key != SERVER_API_KEY:
    raise ValueError("Invalid API key")
```
"""

W7L2_DEBRIEF = """\
**Power-pellet unlocked:**

- API key auth is the simplest tool-level gate.
- Raising returns `isError: true`, surfacing the rejection to Claude.
- Stopgap for personal use — OAuth is the production answer.
"""


W7L3_STARTER = '''"""W7-L3: OAuth 2.1 with PKCE.

API keys flow through tool arguments — auditable, but not the spec-
mandated approach for remote MCP. The MCP spec defines **OAuth 2.1 with
PKCE** at the transport layer: the server validates a bearer token in
the Authorization header before letting any JSON-RPC through.

Fill in OAUTH_CONFIG with a dict-shaped string referencing the standard
OAuth 2.1 endpoints. The grader checks the source contains:
  "authorization_endpoint", "token_endpoint", "client_id"

Source-only — actually wiring OAuth needs a real auth server.
"""

# TODO: replace with a config block containing at minimum:
#   authorization_endpoint, token_endpoint, client_id, scopes
# Example:
# {
#   "authorization_endpoint": "https://auth.example.com/oauth/authorize",
#   "token_endpoint": "https://auth.example.com/oauth/token",
#   "client_id": "pellet-tracker-client",
#   "scopes": ["pellets:read", "pellets:write"]
# }
OAUTH_CONFIG = """
{
}
"""

# In a real server you\'d wire OAuth at the transport layer (Streamable
# HTTP) by configuring auth middleware. The MCP Python SDK exposes an
# `mcp.server.auth` module with helpers for this — out of scope here but
# the spec-mandated path for production remote MCP servers.
'''

W7L3_BRIEF = """\
## OAuth 2.1 with PKCE — the production answer

The MCP spec mandates **OAuth 2.1 with PKCE** for remote servers. Here's
why and what changes.

### The threat model

| Risk | API key | OAuth 2.1 |
|------|---------|-----------|
| Key in logs / chat history | High | None — token is short-lived |
| Per-user scoping | Hard | Standard (scopes claim) |
| Revocation | Manual | Built-in |
| Multi-user | One key, shared | Each user gets their own token |

### The flow at a glance
1. Claude (the client) hits your server with no token.
2. Server responds 401 + a WWW-Authenticate header pointing to your auth server.
3. Claude opens the auth URL in the user's browser; user signs in.
4. Auth server redirects back with an authorization code.
5. Claude exchanges the code (with a PKCE verifier) for a short-lived **access token**.
6. Claude retries the MCP request with `Authorization: Bearer <token>`.
7. Your server validates the token and processes the request.

### What you write
Most of the OAuth flow is library code. You configure:

```python
OAUTH_CONFIG = {
    "authorization_endpoint": "https://auth.example.com/oauth/authorize",
    "token_endpoint":         "https://auth.example.com/oauth/token",
    "client_id":              "pellet-tracker",
    "scopes":                 ["pellets:read", "pellets:write"],
}
```

…and the MCP Python SDK's auth helpers validate every request for you.

### Where to learn the full flow
The MCP spec page "Authentication" walks through every header and
endpoint. This level just plants the seed — wire-up is a future
exercise.
"""

W7L3_DEBRIEF = """\
**Power-pellet unlocked — World 7 complete!**

- Remote MCP servers must use **OAuth 2.1 with PKCE** per the spec.
- You configure: `authorization_endpoint`, `token_endpoint`, `client_id`, `scopes`.
- Library code handles the dance; you handle the config.
- This is the production-ready path for any non-personal MCP server.

One world left.
"""


# ════════════════════════════════════════════════════════════════════════
# WORLD 8 — DISTRIBUTE + SKILLS
# ════════════════════════════════════════════════════════════════════════

W8L1_STARTER = '''"""W8-L1: DXT packaging — one-click install.

For sharing your server with users who don\'t want to edit config files,
MCP defines **DXT (Desktop Extension)** archives: a `.dxt` zip with your
server, dependencies, and a `manifest.json` describing it.

Fill in DXT_MANIFEST with a valid JSON manifest for Pellet Tracker. The
grader checks for these required substrings:
  "dxt_version", "name", "version", "server", "type"
"""

# TODO: write a valid DXT manifest. Minimum shape:
# {
#   "dxt_version": "0.1",
#   "name": "pellet-tracker",
#   "version": "1.0.0",
#   "description": "Personal habit tracker.",
#   "author": {"name": "You"},
#   "server": {
#     "type": "python",
#     "entry_point": "server.py",
#     "mcp_config": {
#       "command": "python",
#       "args": ["${__dirname}/server.py"]
#     }
#   }
# }
DXT_MANIFEST = """
{
}
"""

# Once you have a valid manifest:
#   1. Zip your server + manifest.json into pellet-tracker.dxt
#   2. Open it from Claude Desktop → it installs.
'''

W8L1_BRIEF = """\
## DXT — one-click MCP install

Hand-editing `claude_desktop_config.json` is fine for developers. For
shipping to non-developers, MCP defines **DXT (Desktop Extension)** —
a `.dxt` archive (basically a zip) that bundles:

- Your server code
- A `manifest.json` describing the server
- Optionally: bundled dependencies, icons, screenshots

The user double-clicks the `.dxt` from Claude Desktop and it installs
automatically — no terminal, no config editing.

### Minimum manifest

```json
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
```

### Required fields
- `dxt_version` — manifest schema version (currently `"0.1"`)
- `name`, `version` — your server's name + semver
- `server.type` — `"python"`, `"node"`, or `"binary"`
- `server.mcp_config` — the same shape as `claude_desktop_config.json`'s entry
- `${__dirname}` — placeholder Claude Desktop substitutes with the install path

### Packaging
```bash
zip -r pellet-tracker.dxt manifest.json server.py
```

### Distribution
- Direct download from your website
- Anthropic's DXT directory (eventually)
- Embed in OSS repos as a release artifact
"""

W8L1_DEBRIEF = """\
**Power-pellet unlocked:**

- DXT archives bundle your server + manifest into a one-click installer.
- Minimum manifest: `dxt_version`, `name`, `version`, `server.{type, entry_point, mcp_config}`.
- `${__dirname}` substitutes the install path at runtime.
- This is how you ship MCP servers to non-developer users.
"""


W8L2_STARTER = '''"""W8-L2: Bundle a SKILL.md companion.

An MCP server gives Claude *capabilities*. A SKILL.md tells Claude *when
to reach for them*. Bundle one alongside your server so Claude
automatically knows Pellet Tracker is the right play for habits.

Fill in SKILL_MD with a valid SKILL.md document. Required:
  • YAML frontmatter (two --- lines)
  • `name: pellet-tracker` in the frontmatter
  • `description:` mentioning "habit"
  • At least one Markdown # heading
"""

# TODO: replace with a real SKILL.md
SKILL_MD = """
"""
'''

W8L2_BRIEF = """\
## Skills × MCP — the modern Claude-native pattern

You've built an MCP server. Claude knows *what* tools, resources, and
prompts exist. But how does it know **when** to reach for them?

That's what **Skills** do. A Skill is a markdown file (`SKILL.md`) with
YAML frontmatter that describes a workflow and tells Claude when to
invoke it. Skills live in `.claude/skills/<name>/` and are loaded on
demand by Claude Code and Claude Desktop.

### Anatomy

```markdown
---
name: pellet-tracker
description: Use when the user mentions habits, streaks, or daily routines.
---

# When to use this skill
When the user logs a habit, asks about streaks, or wants a morning
check-in.

# What to do
Use the Pellet Tracker MCP server's `log_pellet`, `count_pellets`, and
`pellets://today` resource.
```

The `description:` is what Claude reads when deciding to load the skill
at all — write it like a tool description: specific, action-oriented.

### Why bundle them
- **MCP alone**: Claude has the capability but might not know to use it.
- **Skill alone**: Claude has guidance but no capability to act on.
- **Both**: Claude knows *when* (skill) and *what* (MCP). Complete.

This is the production pattern for Claude-native tooling. Skills + MCP +
DXT = a fully shippable Claude-first product.
"""

W8L2_DEBRIEF = """\
**🎮 ARCADE CLEARED. You won the game.**

You shipped a real, production-quality MCP server:
- Tools with descriptions, annotations, structured output, graceful errors
- Static + templated resources
- Simple + parameterized prompts
- Bidirectional features: sampling, elicitation, progress notifications
- Persistent storage
- Multiple transports (stdio + Streamable HTTP)
- Both deploy paths: Claude Desktop + Claude Code
- API key + OAuth 2.1 auth
- DXT packaging
- A Skill companion

That's the **complete** modern Claude-native stack. Go build something
people use.
"""


# ════════════════════════════════════════════════════════════════════════
# REGISTRY
# ════════════════════════════════════════════════════════════════════════

LESSONS: dict[tuple[int, int], Lesson] = {
    # ───── WORLD 1 ─────
    (1, 1): Lesson(
        world=1, level=1, title="Greet your Tracker",
        ghost="pacman", concept="intro",
        concept_brief=W1L1_BRIEF, post_pass_debrief=W1L1_DEBRIEF,
        story=("Pac-Hacker, the arcade has a new patron: you. Spin up your "
               "Pellet Tracker server and have it greet you by name."),
        instructions=("Build an MCP tool named **`whoami`**.\n\n"
                      "- Parameter: `name` (string)\n"
                      "- Returns: `Welcome to your Pellet Tracker, <name>!`"),
        starter_code=W1L1_STARTER,
        solution_hint='`return f"Welcome to your Pellet Tracker, {name}!"`',
        pellet_reward=100,
        grader_steps=[
            GraderStep(kind="initialize", description="Handshake"),
            GraderStep(kind="list_tools", expect={"tool_name": "whoami"},
                       description="`whoami` is registered"),
            GraderStep(kind="call_tool",
                       params={"name": "whoami", "arguments": {"name": "Emmi"}},
                       expect={"text_equals": "Welcome to your Pellet Tracker, Emmi!"},
                       description="Greet name='Emmi'"),
            GraderStep(kind="call_tool",
                       params={"name": "whoami", "arguments": {"name": "Pac-Hacker"}},
                       expect={"text_equals": "Welcome to your Pellet Tracker, Pac-Hacker!"},
                       description="Greet name='Pac-Hacker'"),
        ],
    ),
    (1, 2): Lesson(
        world=1, level=2, title="Eat your first pellet",
        ghost="pacman", concept="tools",
        concept_brief=W1L2_BRIEF, post_pass_debrief=W1L2_DEBRIEF,
        story=("A tracker that can't remember is just yelling into the void. "
               "Give your server some memory and two tools to read/write it."),
        instructions=("Add two tools:\n\n"
                      "- **`log_pellet(habit: str) -> str`** — append to `PELLETS`, "
                      'return `"Logged: <habit>"`.\n'
                      "- **`list_pellets() -> list[str]`** — return `PELLETS`."),
        starter_code=W1L2_STARTER,
        solution_hint=("```python\n"
                       "@mcp.tool()\n"
                       "def log_pellet(habit: str) -> str:\n"
                       "    PELLETS.append(habit)\n"
                       '    return f"Logged: {habit}"\n\n'
                       "@mcp.tool()\n"
                       "def list_pellets() -> list[str]:\n"
                       "    return PELLETS\n"
                       "```"),
        pellet_reward=150,
        grader_steps=[
            GraderStep(kind="initialize", description="Handshake"),
            GraderStep(kind="list_tools",
                       expect={"tools_include": ["whoami", "log_pellet", "list_pellets"]},
                       description="All three tools registered"),
            GraderStep(kind="call_tool",
                       params={"name": "log_pellet", "arguments": {"habit": "meditation"}},
                       expect={"text_contains": "meditation"},
                       description="log_pellet('meditation')"),
            GraderStep(kind="call_tool",
                       params={"name": "log_pellet", "arguments": {"habit": "running"}},
                       expect={"text_contains": "running"},
                       description="log_pellet('running')"),
            GraderStep(kind="call_tool",
                       params={"name": "list_pellets", "arguments": {}},
                       expect={"text_contains": ["meditation", "running"]},
                       description="list_pellets() returns both"),
        ],
    ),
    (1, 3): Lesson(
        world=1, level=3, title="Count your pellets",
        ghost="pacman", concept="tools",
        concept_brief=W1L3_BRIEF, post_pass_debrief=W1L3_DEBRIEF,
        story=("How many times have you eaten *this* pellet? Add a tool that counts."),
        instructions=("Add **`count_pellets(habit: str) -> int`** returning the "
                      "occurrence count. Return `0` if never logged."),
        starter_code=W1L3_STARTER,
        solution_hint=("```python\n"
                       "@mcp.tool()\n"
                       "def count_pellets(habit: str) -> int:\n"
                       "    return sum(1 for p in PELLETS if p == habit)\n"
                       "```"),
        pellet_reward=150,
        grader_steps=[
            GraderStep(kind="initialize", description="Handshake"),
            GraderStep(kind="list_tools", expect={"tool_name": "count_pellets"},
                       description="`count_pellets` is registered"),
            GraderStep(kind="call_tool",
                       params={"name": "log_pellet", "arguments": {"habit": "running"}},
                       expect={"text_contains": "running"},
                       description="Log 'running'"),
            GraderStep(kind="call_tool",
                       params={"name": "log_pellet", "arguments": {"habit": "running"}},
                       expect={"text_contains": "running"},
                       description="Log 'running' again"),
            GraderStep(kind="call_tool",
                       params={"name": "log_pellet", "arguments": {"habit": "reading"}},
                       expect={"text_contains": "reading"},
                       description="Log 'reading'"),
            GraderStep(kind="call_tool",
                       params={"name": "count_pellets", "arguments": {"habit": "running"}},
                       expect={"text_equals": "2"},
                       description="count_pellets('running') == 2"),
            GraderStep(kind="call_tool",
                       params={"name": "count_pellets", "arguments": {"habit": "reading"}},
                       expect={"text_equals": "1"},
                       description="count_pellets('reading') == 1"),
            GraderStep(kind="call_tool",
                       params={"name": "count_pellets", "arguments": {"habit": "nope"}},
                       expect={"text_equals": "0"},
                       description="count_pellets('nope') == 0"),
        ],
    ),
    (1, 4): Lesson(
        world=1, level=4, title="Persist your pellets",
        ghost="pacman", concept="persistence",
        concept_brief=W1L4_BRIEF, post_pass_debrief=W1L4_DEBRIEF,
        story=("In-memory state vanishes when the server restarts. Save your "
               "pellets to a real file so they stick around."),
        instructions=("Implement `_load()` and `_save()` using `json.load` / "
                      "`json.dump` against `PELLETS_FILE`. The grader spawns "
                      "your server **twice** in the same workdir: it logs a "
                      "habit in the first run, kills the server, then verifies "
                      "your second run reads it back."),
        starter_code=W1L4_STARTER,
        solution_hint=("```python\n"
                       "def _load():\n"
                       "    try:\n"
                       "        with open(PELLETS_FILE) as f:\n"
                       "            return json.load(f)\n"
                       "    except FileNotFoundError:\n"
                       "        return []\n\n"
                       "def _save(p):\n"
                       "    with open(PELLETS_FILE, 'w') as f:\n"
                       "        json.dump(p, f)\n"
                       "```"),
        pellet_reward=200,
        grader_steps=[
            GraderStep(kind="source_assert",
                       expect={"contains": ["json.load", "json.dump"]},
                       description="Code references json.load + json.dump"),
            GraderStep(kind="persistence_check",
                       params={"habit": "persist-test-running"},
                       description="A logged habit survives a server restart"),
        ],
    ),

    # ───── WORLD 2 ─────
    (2, 1): Lesson(
        world=2, level=1, title="Describe your params",
        ghost="blinky", concept="tools",
        concept_brief=W2L1_BRIEF, post_pass_debrief=W2L1_DEBRIEF,
        story=("Blinky has a complaint: Claude keeps calling `log_pellet` "
               "with garbage strings. Help him by describing what `habit` "
               "should look like."),
        instructions=("Use `Annotated[str, Field(description=...)]` for "
                      "`log_pellet`'s `habit`. Description must contain "
                      '"name of the habit".'),
        starter_code=W2L1_STARTER,
        solution_hint=("```python\n"
                       "habit: Annotated[str, Field(description=\"The name of the habit, e.g. 'reading'\")]\n"
                       "```"),
        pellet_reward=200,
        grader_steps=[
            GraderStep(kind="initialize", description="Handshake"),
            GraderStep(kind="list_tools",
                       expect={"tool_check": ["log_pellet",
                               {"schema_property_description_contains": ["habit", "name of the habit"]}]},
                       description="`log_pellet.habit` schema has the description"),
        ],
    ),
    (2, 2): Lesson(
        world=2, level=2, title="Annotate the safe tools",
        ghost="blinky", concept="tools",
        concept_brief=W2L2_BRIEF, post_pass_debrief=W2L2_DEBRIEF,
        story=("Claude wants to know which tools are safe to call without "
               "asking. Mark your read-only tools so Claude can auto-run them."),
        instructions=("Add `annotations={\"readOnlyHint\": True}` to both "
                      "`list_pellets` and `count_pellets` decorators."),
        starter_code=W2L2_STARTER,
        solution_hint='`@mcp.tool(annotations={"readOnlyHint": True})`',
        pellet_reward=200,
        grader_steps=[
            GraderStep(kind="initialize", description="Handshake"),
            GraderStep(kind="list_tools",
                       expect={"tool_check": ["list_pellets",
                               {"annotation_equals": ["readOnlyHint", True]}]},
                       description="`list_pellets` marked readOnly"),
            GraderStep(kind="list_tools",
                       expect={"tool_check": ["count_pellets",
                               {"annotation_equals": ["readOnlyHint", True]}]},
                       description="`count_pellets` marked readOnly"),
        ],
    ),
    (2, 3): Lesson(
        world=2, level=3, title="Structured output",
        ghost="blinky", concept="tools",
        concept_brief=W2L3_BRIEF, post_pass_debrief=W2L3_DEBRIEF,
        story=("`count_pellets` returns a plain int. Make it return a typed "
               "object so Claude sees all stats at once."),
        instructions=("Define a `StreakInfo` BaseModel with fields `habit: str`, "
                      "`total: int`, `longest_run: int`. Change `count_pellets` "
                      "to return a `StreakInfo` instance."),
        starter_code=W2L3_STARTER,
        solution_hint=("```python\n"
                       "class StreakInfo(BaseModel):\n"
                       "    habit: str\n"
                       "    total: int\n"
                       "    longest_run: int\n\n"
                       "@mcp.tool(annotations={'readOnlyHint': True})\n"
                       "def count_pellets(habit: str) -> StreakInfo:\n"
                       "    total = sum(1 for p in PELLETS if p == habit)\n"
                       "    return StreakInfo(habit=habit, total=total, longest_run=total)\n"
                       "```"),
        pellet_reward=250,
        grader_steps=[
            GraderStep(kind="initialize", description="Handshake"),
            GraderStep(kind="list_tools",
                       expect={"tool_check": ["count_pellets", {"has_output_schema": True}]},
                       description="`count_pellets` has an outputSchema"),
            GraderStep(kind="call_tool",
                       params={"name": "log_pellet", "arguments": {"habit": "running"}},
                       expect={"text_contains": "running"},
                       description="Log a pellet"),
            GraderStep(kind="call_tool",
                       params={"name": "count_pellets", "arguments": {"habit": "running"}},
                       expect={"structured_has": ["habit", "total", "longest_run"]},
                       description="count_pellets returns structuredContent"),
        ],
    ),
    (2, 4): Lesson(
        world=2, level=4, title="Graceful errors",
        ghost="blinky", concept="tools",
        concept_brief=W2L4_BRIEF, post_pass_debrief=W2L4_DEBRIEF,
        story=("Right now `log_pellet('')` cheerfully logs an empty habit. "
               "Add a guard so Claude can recover from bad input."),
        instructions=("At the top of `log_pellet`, if `habit.strip() == \"\"`, "
                      "`raise ValueError(\"habit cannot be empty\")`."),
        starter_code=W2L4_STARTER,
        solution_hint=("```python\n"
                       "if not habit.strip():\n"
                       "    raise ValueError(\"habit cannot be empty\")\n"
                       "```"),
        pellet_reward=200,
        grader_steps=[
            GraderStep(kind="initialize", description="Handshake"),
            GraderStep(kind="call_tool",
                       params={"name": "log_pellet", "arguments": {"habit": ""}},
                       expect={"is_error": True},
                       description="Empty habit → isError=True"),
            GraderStep(kind="call_tool",
                       params={"name": "log_pellet", "arguments": {"habit": "valid"}},
                       expect={"is_error": False, "text_contains": "valid"},
                       description="Valid habit → success"),
        ],
    ),

    # ───── WORLD 3 ─────
    (3, 1): Lesson(
        world=3, level=1, title="Tunnel to today's pellets",
        ghost="pinky", concept="resources",
        concept_brief=W3L1_BRIEF, post_pass_debrief=W3L1_DEBRIEF,
        story=("Pinky wants a peek at your day without calling a tool. Open "
               "a resource — a read-only data tunnel — at `pellets://today`."),
        instructions=("Decorate a function with `@mcp.resource(\"pellets://today\")` "
                      "that returns `json.dumps(PELLETS)`."),
        starter_code=W3L1_STARTER,
        solution_hint=("```python\n"
                       "@mcp.resource(\"pellets://today\")\n"
                       "def todays_pellets() -> str:\n"
                       "    return json.dumps(PELLETS)\n"
                       "```"),
        pellet_reward=250,
        grader_steps=[
            GraderStep(kind="initialize", description="Handshake"),
            GraderStep(kind="call_tool",
                       params={"name": "log_pellet", "arguments": {"habit": "reading"}},
                       expect={"text_contains": "reading"},
                       description="Log something first"),
            GraderStep(kind="list_resources", expect={"uri": "pellets://today"},
                       description="`pellets://today` is registered"),
            GraderStep(kind="read_resource",
                       params={"uri": "pellets://today"},
                       expect={"text_contains": "reading"},
                       description="Reading the resource returns your log"),
        ],
    ),
    (3, 2): Lesson(
        world=3, level=2, title="Templated resource URIs",
        ghost="pinky", concept="resources",
        concept_brief=W3L2_BRIEF, post_pass_debrief=W3L2_DEBRIEF,
        story=("Pinky wants to read just the entries for a specific habit. "
               "Open a templated resource."),
        instructions=("Decorate a function with `@mcp.resource(\"pellets://habit/{name}\")` "
                      "that returns a JSON list of pellets matching `name`."),
        starter_code=W3L2_STARTER,
        solution_hint=("```python\n"
                       "@mcp.resource(\"pellets://habit/{name}\")\n"
                       "def pellets_for_habit(name: str) -> str:\n"
                       "    return json.dumps([p for p in PELLETS if p == name])\n"
                       "```"),
        pellet_reward=300,
        grader_steps=[
            GraderStep(kind="initialize", description="Handshake"),
            GraderStep(kind="call_tool",
                       params={"name": "log_pellet", "arguments": {"habit": "running"}},
                       expect={"text_contains": "running"},
                       description="Log 'running'"),
            GraderStep(kind="list_resource_templates",
                       expect={"uri_template_contains": "pellets://habit/"},
                       description="Resource template registered"),
            GraderStep(kind="read_resource",
                       params={"uri": "pellets://habit/running"},
                       expect={"text_contains": "running"},
                       description="Read pellets://habit/running"),
        ],
    ),

    # ───── WORLD 4 ─────
    (4, 1): Lesson(
        world=4, level=1, title="Morning check-in prompt",
        ghost="inky", concept="prompts",
        concept_brief=W4L1_BRIEF, post_pass_debrief=W4L1_DEBRIEF,
        story=("Inky has a routine: every morning he asks what you'll do "
               "today. Make him a reusable prompt for that."),
        instructions=("Add a prompt named **`morning_check_in`**. The "
                      "returned text must contain the word **`pellets`**."),
        starter_code=W4L1_STARTER,
        solution_hint=("```python\n"
                       "@mcp.prompt()\n"
                       "def morning_check_in() -> str:\n"
                       "    return \"Good morning! Which pellets will you eat today?\"\n"
                       "```"),
        pellet_reward=250,
        grader_steps=[
            GraderStep(kind="initialize", description="Handshake"),
            GraderStep(kind="list_prompts", expect={"prompt_name": "morning_check_in"},
                       description="Prompt registered"),
            GraderStep(kind="get_prompt", params={"name": "morning_check_in"},
                       expect={"text_contains": "pellets"},
                       description="Prompt mentions pellets"),
        ],
    ),
    (4, 2): Lesson(
        world=4, level=2, title="Prompt with arguments",
        ghost="inky", concept="prompts",
        concept_brief=W4L2_BRIEF, post_pass_debrief=W4L2_DEBRIEF,
        story=("Inky wants to recap whatever week you specify. Make him a "
               "prompt that takes an argument."),
        instructions=("Add a prompt **`weekly_recap(week_offset: int = 0)`** "
                      "whose returned text mentions `(7 + week_offset * 7)`."),
        starter_code=W4L2_STARTER,
        solution_hint=("```python\n"
                       "@mcp.prompt()\n"
                       "def weekly_recap(week_offset: int = 0) -> str:\n"
                       "    days = 7 + week_offset * 7\n"
                       "    return f\"Summarize my pellets from the past {days} days.\"\n"
                       "```"),
        pellet_reward=250,
        grader_steps=[
            GraderStep(kind="initialize", description="Handshake"),
            GraderStep(kind="list_prompts", expect={"prompt_name": "weekly_recap"},
                       description="Prompt registered"),
            GraderStep(kind="get_prompt",
                       params={"name": "weekly_recap", "arguments": {"week_offset": "1"}},
                       expect={"text_contains": "14"},
                       description="weekly_recap(week_offset=1) mentions 14 days"),
        ],
    ),

    # ───── WORLD 5 ─────
    (5, 1): Lesson(
        world=5, level=1, title="Sampling — ask Claude to think",
        ghost="clyde", concept="bidirectional",
        concept_brief=W5L1_BRIEF, post_pass_debrief=W5L1_DEBRIEF,
        story=("Clyde wants Claude to write a reflection on the week's "
               "pellets. Wire `analyze_my_week` to use sampling."),
        instructions=("Implement `analyze_my_week` using "
                      "`ctx.session.create_message(...)`. The grader runs "
                      "your tool against a **mocked LLM** that replies with "
                      "`\"Mock LLM reflection: keep eating those pellets!\"` "
                      "— so you can see the round-trip in the Inspector."),
        starter_code=W5L1_STARTER,
        solution_hint=("```python\n"
                       "result = await ctx.session.create_message(\n"
                       "    messages=[SamplingMessage(role='user',\n"
                       "        content=TextContent(type='text', text=f'Reflect on: {PELLETS}'))],\n"
                       "    max_tokens=200,\n"
                       ")\n"
                       "return result.content.text\n"
                       "```"),
        pellet_reward=350,
        grader_steps=[
            GraderStep(kind="source_assert",
                       expect={"contains": "ctx.session.create_message"},
                       description="Tool calls ctx.session.create_message"),
            GraderStep(kind="initialize", description="Handshake"),
            GraderStep(kind="call_tool",
                       params={"name": "analyze_my_week", "arguments": {}},
                       expect={"is_error": False, "text_contains": "Mock LLM reflection"},
                       description="analyze_my_week returns the mocked LLM reply"),
        ],
    ),
    (5, 2): Lesson(
        world=5, level=2, title="Elicitation — ask the user",
        ghost="clyde", concept="bidirectional",
        concept_brief=W5L2_BRIEF, post_pass_debrief=W5L2_DEBRIEF,
        story=("Sometimes the user knows what they want but didn't tell you. "
               "Use elicitation to pause and ask."),
        instructions=("Implement `start_habit` using `ctx.elicit(...)`. The "
                      "grader runs your tool against a **mocked user** that "
                      "auto-accepts with `habit=\"stub-habit\"` — so you can "
                      "see the round-trip in the Inspector."),
        starter_code=W5L2_STARTER,
        solution_hint=("```python\n"
                       "result = await ctx.elicit(\n"
                       "    message='What habit?',\n"
                       "    schema=_HabitPrompt,    # the Pydantic class\n"
                       ")\n"
                       "if result.action != 'accept':\n"
                       "    return 'Cancelled.'\n"
                       "habit = result.data.habit\n"
                       "PELLETS.append(habit)\n"
                       "_save(PELLETS)\n"
                       "return f'Tracking {habit}'\n"
                       "```"),
        pellet_reward=350,
        grader_steps=[
            GraderStep(kind="source_assert",
                       expect={"contains": "ctx.elicit"},
                       description="Tool calls ctx.elicit"),
            GraderStep(kind="initialize", description="Handshake"),
            GraderStep(kind="call_tool",
                       params={"name": "start_habit", "arguments": {}},
                       expect={"is_error": False, "text_contains": "stub-habit"},
                       description="start_habit completes the mocked elicitation"),
        ],
    ),
    (5, 3): Lesson(
        world=5, level=3, title="Progress notifications",
        ghost="clyde", concept="bidirectional",
        concept_brief=W5L3_BRIEF, post_pass_debrief=W5L3_DEBRIEF,
        story=("Long-running tools should report progress so the UI doesn't "
               "feel hung. Wire `bulk_import` to send updates."),
        instructions=("Implement `bulk_import(count)` so it loops `count` "
                      "times, calling `await ctx.report_progress(progress=i+1, "
                      "total=count)` and appending `f\"imported_{i+1}\"` to "
                      "`PELLETS` each iteration."),
        starter_code=W5L3_STARTER,
        solution_hint=("```python\n"
                       "for i in range(count):\n"
                       "    await ctx.report_progress(progress=i+1, total=count)\n"
                       "    PELLETS.append(f'imported_{i+1}')\n"
                       "_save(PELLETS)\n"
                       "return f'Imported {count}'\n"
                       "```"),
        pellet_reward=350,
        grader_steps=[
            GraderStep(kind="source_assert",
                       expect={"contains": "ctx.report_progress"},
                       description="Tool calls ctx.report_progress"),
            GraderStep(kind="initialize", description="Handshake"),
            GraderStep(kind="call_tool",
                       params={"name": "bulk_import", "arguments": {"count": 3}},
                       expect={"is_error": False, "text_contains": "Imported 3"},
                       description="bulk_import(count=3) succeeds end-to-end"),
        ],
    ),

    # ───── WORLD 6 ─────
    (6, 1): Lesson(
        world=6, level=1, title="Plug into Claude Desktop",
        ghost="pacman", concept="deploy",
        concept_brief=W6L1_BRIEF, post_pass_debrief=W6L1_DEBRIEF,
        story=("Time for the real thing. Write the snippet that goes into "
               "your `claude_desktop_config.json`."),
        instructions=("Fill `CLAUDE_DESKTOP_SNIPPET` with a JSON config "
                      "containing `mcpServers`, `pellet-tracker`, `command`, "
                      "and `args`."),
        starter_code=W6L1_STARTER,
        solution_hint=("```json\n"
                       "{\n"
                       '  "mcpServers": {\n'
                       '    "pellet-tracker": {\n'
                       '      "command": "python",\n'
                       '      "args": ["/absolute/path/to/server.py"]\n'
                       "    }\n"
                       "  }\n"
                       "}\n"
                       "```"),
        pellet_reward=200,
        grader_steps=[
            GraderStep(kind="source_assert",
                       expect={"contains": ["mcpServers", "pellet-tracker", "command", "args"]},
                       description="Snippet has all four required keys"),
        ],
    ),
    (6, 2): Lesson(
        world=6, level=2, title="Plug into Claude Code",
        ghost="pacman", concept="deploy",
        concept_brief=W6L2_BRIEF, post_pass_debrief=W6L2_DEBRIEF,
        story=("Claude Code uses `.mcp.json` at the repo root. Same shape "
               "as Claude Desktop's config — fill it in."),
        instructions=("Fill `CLAUDE_CODE_MCP_JSON` with the same shape: "
                      "`mcpServers`, `pellet-tracker`, `command`, `args`."),
        starter_code=W6L2_STARTER,
        solution_hint=("Same shape as Claude Desktop. Or run "
                       "`claude mcp add pellet-tracker --command python --args ./server.py`."),
        pellet_reward=200,
        grader_steps=[
            GraderStep(kind="source_assert",
                       expect={"contains": ["mcpServers", "pellet-tracker", "command", "args"]},
                       description="Config has all four required keys"),
        ],
    ),
    (6, 3): Lesson(
        world=6, level=3, title="Debug with MCP Inspector",
        ghost="pacman", concept="deploy",
        concept_brief=W6L3_BRIEF, post_pass_debrief=W6L3_DEBRIEF,
        story=("Before you trust your server in Claude, exercise every tool "
               "in the MCP Inspector — the official debugging UI."),
        instructions=("Fill `MCP_INSPECTOR_CMD` with a valid shell command. "
                      "Must reference `@modelcontextprotocol/inspector`."),
        starter_code=W6L3_STARTER,
        solution_hint='`MCP_INSPECTOR_CMD = "npx @modelcontextprotocol/inspector python ./server.py"`',
        pellet_reward=200,
        grader_steps=[
            GraderStep(kind="source_assert",
                       expect={"contains": "@modelcontextprotocol/inspector"},
                       description="Command launches the MCP Inspector"),
        ],
    ),

    # ───── WORLD 7 ─────
    (7, 1): Lesson(
        world=7, level=1, title="Streamable HTTP warp",
        ghost="blinky", concept="transports",
        concept_brief=W7L1_BRIEF, post_pass_debrief=W7L1_DEBRIEF,
        story=("Time to host your tracker on the open web. Flip the "
               "transport from stdio to Streamable HTTP — one arg away."),
        instructions=('Change `mcp.run()` to '
                      '`mcp.run(transport="streamable-http")`.'),
        starter_code=W7L1_STARTER,
        solution_hint='`mcp.run(transport="streamable-http")`',
        pellet_reward=250,
        grader_steps=[
            GraderStep(kind="source_assert",
                       expect={"matches": r'mcp\.run\(\s*transport\s*=\s*[\'"]streamable-http[\'"]'},
                       description='`mcp.run(transport="streamable-http")` present'),
        ],
    ),
    (7, 2): Lesson(
        world=7, level=2, title="API key auth",
        ghost="blinky", concept="auth",
        concept_brief=W7L2_BRIEF, post_pass_debrief=W7L2_DEBRIEF,
        story=("Without auth, anyone who can reach your URL can log pellets "
               "to your account. Gate `log_pellet` behind an API key."),
        instructions=("Add an `api_key: str` parameter to `log_pellet`. "
                      "If `api_key != \"wakawaka\"`, raise "
                      "`ValueError(\"Invalid API key\")`. Otherwise log normally."),
        starter_code=W7L2_STARTER,
        solution_hint=("```python\n"
                       "def log_pellet(habit: ..., api_key: str) -> str:\n"
                       "    if api_key != 'wakawaka':\n"
                       "        raise ValueError('Invalid API key')\n"
                       "    ...\n"
                       "```"),
        pellet_reward=300,
        grader_steps=[
            GraderStep(kind="initialize", description="Handshake"),
            GraderStep(kind="call_tool",
                       params={"name": "log_pellet",
                               "arguments": {"habit": "running", "api_key": "wrong"}},
                       expect={"is_error": True},
                       description="Wrong API key → error"),
            GraderStep(kind="call_tool",
                       params={"name": "log_pellet",
                               "arguments": {"habit": "running", "api_key": "wakawaka"}},
                       expect={"is_error": False, "text_contains": "running"},
                       description="Right API key → success"),
        ],
    ),
    (7, 3): Lesson(
        world=7, level=3, title="OAuth 2.1 + PKCE",
        ghost="blinky", concept="auth",
        concept_brief=W7L3_BRIEF, post_pass_debrief=W7L3_DEBRIEF,
        story=("Boss-level auth: the MCP spec mandates OAuth 2.1 with PKCE "
               "for remote servers. Configure the endpoints."),
        instructions=("Fill `OAUTH_CONFIG` with a JSON config containing "
                      "`authorization_endpoint`, `token_endpoint`, and "
                      "`client_id`."),
        starter_code=W7L3_STARTER,
        solution_hint=("```json\n"
                       "{\n"
                       '  "authorization_endpoint": "https://auth.example.com/oauth/authorize",\n'
                       '  "token_endpoint": "https://auth.example.com/oauth/token",\n'
                       '  "client_id": "pellet-tracker-client",\n'
                       '  "scopes": ["pellets:read", "pellets:write"]\n'
                       "}\n"
                       "```"),
        pellet_reward=400,
        grader_steps=[
            GraderStep(kind="source_assert",
                       expect={"contains": ["authorization_endpoint", "token_endpoint", "client_id"]},
                       description="OAuth config has all three required keys"),
        ],
    ),

    # ───── WORLD 8 ─────
    (8, 1): Lesson(
        world=8, level=1, title="DXT one-click packaging",
        ghost="pacman", concept="distribute",
        concept_brief=W8L1_BRIEF, post_pass_debrief=W8L1_DEBRIEF,
        story=("To ship your server to non-developers, package it as a "
               "DXT archive — drop-in install for Claude Desktop."),
        instructions=("Fill `DXT_MANIFEST` with a valid manifest. Required "
                      "substrings: `dxt_version`, `name`, `version`, "
                      "`server`, `type`."),
        starter_code=W8L1_STARTER,
        solution_hint=("See the briefing — copy the minimum manifest example."),
        pellet_reward=350,
        grader_steps=[
            GraderStep(kind="source_assert",
                       expect={"contains": ["dxt_version", "name", "version", "server", "type"]},
                       description="Manifest has all required fields"),
        ],
    ),
    (8, 2): Lesson(
        world=8, level=2, title="Bundle a Skill companion",
        ghost="pacman", concept="skills",
        concept_brief=W8L2_BRIEF, post_pass_debrief=W8L2_DEBRIEF,
        story=("Final boss: tell Claude *when* to reach for Pellet Tracker. "
               "Write a SKILL.md that lives next to your server."),
        instructions=("Fill `SKILL_MD` with a SKILL.md containing: YAML "
                      "frontmatter (two `---` lines), `name: pellet-tracker`, "
                      "a `description:` mentioning **habit**, and at least "
                      "one `# Heading`."),
        starter_code=W8L2_STARTER,
        solution_hint=("```\n"
                       "---\n"
                       "name: pellet-tracker\n"
                       "description: Use when the user mentions habits, streaks, or daily routines.\n"
                       "---\n\n"
                       "# When to use\n"
                       "When the user logs a habit or asks about progress.\n"
                       "```"),
        pellet_reward=500,
        grader_steps=[
            GraderStep(kind="source_assert",
                       expect={"matches": r"---[\s\S]*?name:\s*pellet-tracker[\s\S]*?description:[^\n]*habit[\s\S]*?---[\s\S]*?\n#\s"},
                       description="SKILL.md has frontmatter + name + description (mentions habit) + heading"),
        ],
    ),
}


def list_lessons_summary() -> list[dict]:
    return [
        {
            "world": lesson.world,
            "level": lesson.level,
            "title": lesson.title,
            "ghost": lesson.ghost,
            "concept": lesson.concept,
            "pellet_reward": lesson.pellet_reward,
        }
        for lesson in LESSONS.values()
    ]


WORLD_ARC = [
    {"world": 1, "title": "Pellet Basics",        "concept": "intro",         "ghost": "pacman"},
    {"world": 2, "title": "The Tool Maze",        "concept": "tools",         "ghost": "blinky"},
    {"world": 3, "title": "Resource Tunnels",     "concept": "resources",     "ghost": "pinky"},
    {"world": 4, "title": "Prompt Power-Pellets", "concept": "prompts",       "ghost": "inky"},
    {"world": 5, "title": "Bidirectional MCP",    "concept": "bidirectional", "ghost": "clyde"},
    {"world": 6, "title": "Escape to Claude",     "concept": "deploy",        "ghost": "pacman"},
    {"world": 7, "title": "Going Public",         "concept": "remote",        "ghost": "blinky"},
    {"world": 8, "title": "Distribute + Skills",  "concept": "skills",        "ghost": "pacman"},
]

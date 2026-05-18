---
name: tools-must-annotate
applies-to: any MCP tool registered with `@mcp.tool()` in this repo
---

# Rule

Every MCP tool in this repo **must** declare at least one of these
annotations on its `@mcp.tool(...)` decorator:

- `readOnlyHint: True` — the tool does not change server state
- `destructiveHint: True` — the tool may delete or alter data
- `idempotentHint: True` — same input always produces the same effect
- `openWorldHint: True` — the tool touches external systems (web, APIs)

A tool that mixes properties (read + idempotent, etc.) should declare
all that apply.

# Why

MCP clients — Claude Desktop, Claude Code, the MCP Inspector — use these
hints to decide whether to auto-run a tool or ask the user first. Without
annotations, every call asks for confirmation, which destroys flow for
read-only tools (`list_pellets`, `count_pellets`) and dangerously hides
intent for write tools (`log_pellet`, `bulk_import`).

This is the concept introduced in **World 2, Level 2** of MCP Academy
(`backend/lessons.py` → `W2L2_BRIEF`). It's a hint, not enforcement — so
honesty matters: a `readOnlyHint: True` tool that actually mutates state
erodes user trust quickly.

# How to apply

When reviewing or writing tools at `.claude/mcp_servers/pellet-tracker/server.py`
or anywhere else in the project, check for this pattern:

```python
@mcp.tool(annotations={"readOnlyHint": True})
def list_pellets() -> list[str]:
    ...
```

Missing annotations on a new tool? **Block the change** and ask which
annotation applies. If unsure, default to no annotation rather than the
wrong one — but flag the omission.

For multi-effect tools, multiple keys are fine:

```python
@mcp.tool(annotations={"destructiveHint": True, "idempotentHint": False})
def reset_pellets() -> str:
    ...
```

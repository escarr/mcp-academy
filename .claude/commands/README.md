# Slash commands

Project-scoped `/commands` — markdown files that Claude Code surfaces as
`/command-name` in the prompt. Each file is one command. The body is the
prompt template; `$ARGUMENTS` is replaced with the rest of the line.

Layout:

```
.claude/commands/
└── <command-name>.md
```

`<command-name>.md` frontmatter (optional):
```markdown
---
description: One-liner shown in the slash-command picker.
argument-hint: <free-text shown after the slash command>
---

The prompt body. Reference $ARGUMENTS to inject whatever the user typed.
```

### Status

⬜ No project commands yet. Candidates as worlds ship:

- `/new-level` — scaffold a new lesson entry in `backend/lessons.py`.
- `/grade <world> <level>` — run the grader against a saved server snippet.
- `/dxt-pack <server-dir>` — package an MCP server in `.claude/mcp_servers/` into a `.dxt` for Claude Desktop (World 6).

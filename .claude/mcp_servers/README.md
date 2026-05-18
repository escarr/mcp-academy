# MCP Servers

Each subdirectory here is a complete, runnable MCP server. Two kinds will
accumulate as worlds unlock:

1. **Player artifacts** — the working server you wrote to clear each
   level lands here so the repo becomes your portfolio.
2. **Reference servers** — fully annotated example servers showcasing one
   concept (tools, resources, prompts, transports, sampling, auth).

Layout for each server:

```
.claude/mcp_servers/<server-name>/
├── README.md         ← what this server does, how it was built (which level)
├── pyproject.toml    ← dependencies + entry point
├── server.py         ← the server
└── claude_config.example.json   ← snippet to drop into claude_desktop_config.json or .mcp.json
```

### Wiring into Claude

Once a server is in this folder, it can be registered with Claude Code via:

```bash
claude mcp add --scope project <name> --command python <path-to-server.py>
```

…which writes a `.mcp.json` entry at the repo root. World 6 walks through
this flow end-to-end (Claude Desktop + Claude Code + DXT packaging).

### Status

⬜ Empty until you clear World 1, Level 1. Then `hello-pellet/` lands here.

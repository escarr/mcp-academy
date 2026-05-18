---
description: Launch the MCP Inspector against the in-progress pellet-tracker server.
argument-hint: (no args — just runs the inspector)
---

Run the MCP Inspector against the Pellet Tracker server I've been
building through MCP Academy. The server lives at
`.claude/mcp_servers/pellet-tracker/server.py` — it's auto-updated every
time I clear a level, so the version on disk is whatever I've passed so far.

Use this command:

```bash
npx @modelcontextprotocol/inspector \
    python .claude/mcp_servers/pellet-tracker/server.py
```

After it starts, open the URL it prints (usually <http://localhost:6274>)
and:

1. Hit **Connect** in the Inspector.
2. In the **Tools** tab, list and call every tool registered by the
   server. Confirm each one returns what you'd expect.
3. In the **Resources** tab, browse `pellets://today` (and any
   `pellets://habit/{name}` templated reads). Verify the content.
4. In the **Prompts** tab, fetch each prompt and confirm the rendered
   message text reads correctly.
5. In the **Messages** tab, sanity-check that the raw JSON-RPC matches
   what I saw in the academy's Protocol Inspector while I was building
   each level.

If anything looks off, tell me exactly which tool / resource / prompt
behaved differently from the lesson's expectations and why. Don't suggest
fixes until I see the problem myself — I want to debug, not be handed an
answer.

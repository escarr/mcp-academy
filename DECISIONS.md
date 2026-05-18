# Decisions Log

Append-only. Most recent on top. Use the template below.

```
## YYYY-MM-DD — <short title>
**Author:** <human | claude>
**Context:** what triggered the decision (1–2 sentences)
**Decision:** what we chose
**Alternatives:** what we considered and why we rejected them
**Consequences:** what this commits us to / what we'll have to revisit
```

---

## 2026-05-16 — 23-level curriculum, world reorder, strict locking, save-to-repo, intro screen
**Author:** human + claude
**Context:** Reviewed against modern MCP best practices. Original 11-level curriculum was missing sampling, elicitation, structured output, OAuth 2.1, DXT packaging, the MCP Inspector, persistence, resource templates, and Claude Code's `.mcp.json`. Also: levels were freely accessible (confusing because each starter assumes prior code is in place), and player work didn't materialize anywhere in the repo.
**Decision:**
1. **Curriculum expansion**: 11 → 23 levels, with a new **World 5 "Bidirectional MCP"** (sampling / elicitation / progress) and additions to W1, W2, W3, W4, W6, W7, W8.
2. **World order reorder**: swap deploy ahead of transport — old W5 (Streamable HTTP) became **W7.1**; old W6 (Claude Desktop) became **W6.1**. Rationale: HTTP only matters when going remote; deploy to local Claude should come first for instant gratification.
3. **Strict linear unlock**: within a world, level N requires level N-1 cleared; world N is accessible iff world N-1 is fully cleared. Unlock helper lives in `frontend/src/lib/unlock.ts`.
4. **Save-to-repo**: every passing level POSTs to `/api/save-to-repo` which writes the player's working code to `.claude/mcp_servers/pellet-tracker/server.py` + a regenerated `PROGRESS.md`. The repo becomes the artifact of their learning.
5. **Intro screen**: shown on first visit (`introSeen` flag in localStorage); replayable via `▸ INTRO` button in the HUD. Renders a marquee, a mission panel, a mock Claude chat showing the end-state Pellet Tracker, and an 8-world tour.
6. **Held in back pocket**: the "Sync to Notion" bonus world (real OAuth + external API integration) — not built now, but documented as the natural next addition.
**Alternatives:** Stuck with 11 levels (gaps remain); built only the new world without reorder (deploy-late confusion); free-roam unlocking (cumulative starters break); kept code in-browser only (loses the "real working server" payoff).
**Consequences:** lessons.py grows substantially (~1800 lines). Grader gains a new step kind (`source_assert` was already there but used extensively now). The repo now has a real growing MCP server at `.claude/mcp_servers/pellet-tracker/` that mirrors the user's progress.

## 2026-05-16 — All levels build one server: **Pellet Tracker**
**Author:** human + claude
**Context:** The original sketch had each level teach an MCP concept in isolation (`greet`, `add_note`, etc.). Player asked for a single real-world target server every level contributes to.
**Decision:** Switch the curriculum so every level adds to one growing MCP server, **Pellet Tracker** — a personal habit/streak tracker. By the end of World 8 the player has a usable habit-tracking server they can install in Claude Desktop. Pac-Man theme stays tight: pellets = habits, ghosts = anti-habits, power-pellets = streak bonuses.
**Alternatives:** "Quest Log" (gamified project tracker, narrower); "Code Journal" (dev-only audience). Pellet Tracker fits the theme literally, exercises every MCP primitive, and is universally useful.
**Consequences:** Every level's starter code now embeds the canonical solution from all previous levels — the player only edits the marked TODO block. Grader needs to handle resources, prompts, annotations, structured output, and error responses (extended in this commit).

## 2026-05-16 — Player progression has 8 worlds, ending in Skills × MCP
**Author:** human + claude
**Context:** Scoping the curriculum. The player asked whether to add a module on Skills + MCP integration.
**Decision:** Add an 8th world (`Skills × MCP`) covering bundling `SKILL.md` files alongside MCP servers, MCP-server-as-skill-provider, and writing Claude-friendly tool descriptions that skills can reference.
**Alternatives:** Leave it out (would dodge the most modern Claude integration pattern); cram into World 6 (would mix concerns — deploy vs. compose).
**Consequences:** World 8 must be designed before we promise it to the player; protocol topics from worlds 1–7 should reference it where natural.

## 2026-05-16 — Repo also functions as a Claude-native template
**Author:** human
**Context:** Player wants the finished repo to model Claude best practices (`CLAUDE.md` as repo OS, `.claude/` with skills/commands/rules/mcp_servers, settings.json, decisions log, .env).
**Decision:** Set up the full Claude-native scaffolding *now* (empty but documented), and have each world fill in matching pieces (e.g. completed MCP servers land in `.claude/mcp_servers/`).
**Alternatives:** Defer scaffolding until after worlds are written (loses the "your repo grows with you" feel); only document conventions in README (loses the muscle memory).
**Consequences:** Each level should consider what artifact it leaves behind in the repo; CLAUDE.md must be maintained as worlds ship.

## 2026-05-16 — Grader speaks raw JSON-RPC, not the SDK client
**Author:** claude
**Context:** Needed visibility into every wire message so the Protocol Inspector can show JSON-RPC traffic in real time.
**Decision:** The grader (`backend/grader.py`) spawns the student's server as a subprocess and writes/reads line-delimited JSON-RPC 2.0 directly — no `mcp.client.session` wrapper.
**Alternatives:** Use the SDK's `ClientSession` with a custom transport that taps the streams (more code, more abstraction, easier to break as SDK evolves).
**Consequences:** We own protocol-version negotiation manually — mitigated by reading `mcp.types.LATEST_PROTOCOL_VERSION` so we track the SDK without hardcoding.

## 2026-05-16 — Stack: FastAPI (Python) + Vite/React/Tailwind
**Author:** human + claude
**Context:** Player wanted a gamified, visual arcade UI and Python MCP lessons.
**Decision:** Python backend (FastAPI) because lessons are Python and the grader can `import mcp`. React/Vite frontend because a Pac-Man-themed arcade UI needs real frontend tooling (Monaco, animations, Web Audio SFX).
**Alternatives:** Pure-Python frontend (Streamlit/Gradio — too constrained for game UI); pure-JS with Pyodide running student code in-browser (no real stdio transport).
**Consequences:** Two languages in the repo, but the player only writes Python.

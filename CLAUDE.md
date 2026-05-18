# CLAUDE.md — The OS of `mcp-teacher`

> This file is auto-loaded as context for every Claude Code session in this
> repo. Treat it as the operating system: it tells Claude what the project
> is, where things live, what state we're in, and what conventions to honor.

---

## 1. Mission

**`mcp-teacher`** is a gamified arcade that teaches the Model Context
Protocol by making the learner *build* real Python MCP servers — one
level at a time — and visualizing the JSON-RPC traffic as the protocol
runs. Aesthetic: Pac-Man. Pedagogy: learn-by-doing.

Every level contributes to **one growing target server: Pellet Tracker**
— a personal habit-and-streak tracker. By the end of World 8 the learner
has a real, production-quality MCP server they can install in Claude
Desktop / Claude Code and use daily.

Three outcomes by the end:
1. The learner deeply understands MCP (tools, resources, prompts,
   transports, deployment, auth, skills × MCP).
2. They walk away with a working server they actually keep using.
3. The repo itself is a working **Claude-native template** they can
   reuse for future projects (skills, commands, rules, MCP server
   bundles, decisions log, sensible permissions).

---

## 2. Repo Map

```
mcp-teacher/
├── CLAUDE.md              ← you are here (project OS)
├── README.md              ← human onboarding + run instructions
├── DECISIONS.md           ← append-only log of design decisions
├── start.sh               ← boots backend + frontend
├── .env.example           ← template for runtime secrets
├── .gitignore
│
├── .claude/               ← Claude-native project surface
│   ├── settings.json      ← shared permissions (checked in)
│   ├── settings.local.json← personal overrides (gitignored)
│   ├── skills/            ← reusable Claude skills (SKILL.md + scripts + references + assets)
│   ├── commands/          ← project-scoped slash commands
│   ├── rules/             ← longer-form house rules referenced from CLAUDE.md
│   └── mcp_servers/       ← MCP servers built/used in this project
│
├── backend/               ← FastAPI grader + lesson registry
│   ├── main.py
│   ├── grader.py          ← raw JSON-RPC client; captures every message
│   ├── lessons.py         ← lesson + world-arc registry
│   ├── requirements.txt
│   └── .venv/             (gitignored)
│
└── frontend/              ← Vite + React + Tailwind arcade UI
    ├── index.html
    ├── tailwind.config.js
    ├── package.json
    └── src/
        ├── App.tsx
        ├── audio.ts             ← Web-Audio-synthesized arcade SFX
        ├── store.ts             ← localStorage save game
        ├── api.ts
        ├── types.ts
        └── components/
            ├── WorldMap.tsx
            ├── Level.tsx
            ├── CodeEditor.tsx          (Monaco)
            ├── ProtocolInspector.tsx   ← live JSON-RPC viewer
            ├── Ghost.tsx
            ├── Pacman.tsx
            ├── HUD.tsx
            └── LevelCompleteModal.tsx
```

---

## 3. Skill Development Tracker

Two parallel progressions: the **player's** MCP curriculum, and the
**repo's** Claude-native scaffolding (which fills in as worlds ship).

### Player curriculum — building **Pellet Tracker** (23 levels)

| Level | Title                       | What you add to the server                          |
|-------|----------------------------|------------------------------------------------------|
| 1.1   | Greet your Tracker         | `whoami` — first FastMCP tool                        |
| 1.2   | Eat your first pellet      | `log_pellet`, `list_pellets` + server state          |
| 1.3   | Count your pellets         | `count_pellets` (computed value)                     |
| 1.4   | Persist your pellets       | JSON file persistence (`_load`, `_save`)             |
| 2.1   | Describe your params       | `Annotated` + `Field(description=...)`               |
| 2.2   | Annotate safe tools        | `readOnlyHint` on read-only tools                    |
| 2.3   | Structured output          | Pydantic return → `outputSchema` + `structuredContent` |
| 2.4   | Graceful errors            | `raise ValueError(...)` → `isError: true`            |
| 3.1   | Tunnel to today's pellets  | `@mcp.resource("pellets://today")`                   |
| 3.2   | Templated resource URIs    | `pellets://habit/{name}`                             |
| 4.1   | Morning check-in prompt    | `@mcp.prompt() morning_check_in`                     |
| 4.2   | Prompt with arguments      | `weekly_recap(week_offset: int = 0)`                 |
| 5.1   | Sampling                   | `ctx.session.create_message(...)`                    |
| 5.2   | Elicitation                | `ctx.elicit(...)`                                    |
| 5.3   | Progress notifications     | `ctx.report_progress(...)`                           |
| 6.1   | Plug into Claude Desktop   | `claude_desktop_config.json` snippet                 |
| 6.2   | Plug into Claude Code      | `.mcp.json` + `claude mcp add`                       |
| 6.3   | Debug with MCP Inspector   | `npx @modelcontextprotocol/inspector`                |
| 7.1   | Streamable HTTP warp       | `mcp.run(transport="streamable-http")`               |
| 7.2   | API key auth               | gate `log_pellet` behind an API key                  |
| 7.3   | OAuth 2.1 + PKCE           | authorization_endpoint / token_endpoint / client_id  |
| 8.1   | DXT one-click packaging    | `manifest.json` for `.dxt` archive                   |
| 8.2   | Bundle a Skill companion   | `SKILL.md` next to the server                        |

**Strict linear unlock**: within a world, level N requires N-1 cleared.
World N is accessible iff world N-1 is fully cleared. Logic lives in
`frontend/src/lib/unlock.ts`.

Each level's starter code already includes the canonical solution from
all prior levels. Players only edit the marked `# TODO` section. Passing
a level writes the working code to `.claude/mcp_servers/pellet-tracker/server.py`
so the repo grows alongside the player's knowledge.

### Repo scaffolding (Claude-native)

| Surface                                | Status | Filled in when… |
|----------------------------------------|--------|-----------------|
| `CLAUDE.md` (this file)                | 🟢 live | updated each world |
| `DECISIONS.md`                         | 🟢 live | append on each design call |
| `.claude/settings.json`                | 🟢 init | tweak as new safe commands emerge |
| `.claude/skills/pellet-tracker/`       | ⬜ empty | World 8 unlocks the SKILL.md |
| `.claude/commands/grade-server.md`     | 🟢 live | `/grade-server` — boots the MCP Inspector against the in-progress server |
| `.claude/rules/tools-must-annotate.md` | 🟢 live | every MCP tool must declare `readOnlyHint` / `destructiveHint` / etc. (loaded below) |
| `.claude/mcp_servers/pellet-tracker/`  | 🟢 live | auto-updated on every level clear (server.py + PROGRESS.md; manifest.json on W8.1; SKILL.md mirrored to `.claude/skills/pellet-tracker/` on W8.2) |

---

## 4. Conventions Claude should honor

- **Tone & code:** terse, no over-explaining; no trailing summaries; no decorative comments. Comments only when the *why* is non-obvious.
- **Best-practice MCP:** use `FastMCP` decorators, type hints become schemas, prefer structured output over plain text where it adds clarity, set tool annotations (`readOnlyHint`, `destructiveHint`) when applicable.
- **Protocol version:** never hardcode — read `mcp.types.LATEST_PROTOCOL_VERSION`.
- **Python:** student code runs in the same venv as the grader (`sys.executable`). Don't introduce a second interpreter.
- **TypeScript:** strict on. No `any` unless wrapping protocol payloads.
- **Permissions:** if you want a new command auto-accepted, add it to `.claude/settings.json` *with a note in `DECISIONS.md`* — never widen blindly.
- **Decisions:** when you (Claude) make a non-obvious call, log it in `DECISIONS.md` before moving on. Use the template at the top of that file.

### House rules in force

These project rules are loaded as additional context. Treat them as
binding when reviewing or writing code in the relevant area.

- [.claude/rules/tools-must-annotate.md](.claude/rules/tools-must-annotate.md) — every MCP tool registered with `@mcp.tool()` must declare a safety annotation.

---

## 5. Running the project

```bash
./start.sh        # boots both services
```
- Backend: <http://127.0.0.1:8000>  ·  health: `/api/health`
- Frontend: <http://127.0.0.1:5173>

## 6. Where to look first

- New to MCP? Open `frontend/src/components/Level.tsx` and `backend/grader.py` side-by-side — together they show the full request/response cycle.
- Adding a level? Append to `LESSONS` in `backend/lessons.py`. The frontend will pick it up automatically.
- After any lesson change, run `backend/.venv/bin/python backend/_test_all_levels.py` to make sure the canonical solutions still pass.
- Tweaking the arcade aesthetic? `frontend/src/index.css` + `tailwind.config.js`.
- Considering a permissions change? Edit `.claude/settings.json` and log it.

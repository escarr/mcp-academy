# MCP Academy

A learn-by-doing **arcade** for the Model Context Protocol. You write
real Python MCP servers in the browser; the app spawns them, talks
JSON-RPC to them, and visualizes the protocol traffic as it happens.
Pac-Man-themed.

By the end of all 23 levels, you've built a **production-quality MCP
server** (Pellet Tracker — a personal habit-and-streak tool) that you
can install in Claude Desktop, plus your repo turns into a polished
Claude-native template.

## The curriculum — 8 worlds, 23 levels

| World | Title                  | What you add to your growing Pellet Tracker server               |
|-------|------------------------|-------------------------------------------------------------------|
| 1     | Pellet Basics          | FastMCP tools, server state, computed values, JSON persistence    |
| 2     | The Tool Maze          | Param descriptions, safety annotations, structured output, errors |
| 3     | Resource Tunnels       | Static + URI-templated resources                                  |
| 4     | Prompt Power-Pellets   | Reusable + parameterized slash-command prompts                    |
| 5     | Bidirectional MCP      | Sampling, elicitation, progress notifications                     |
| 6     | Escape to Claude       | Claude Desktop config, Claude Code `.mcp.json`, MCP Inspector     |
| 7     | Going Public           | Streamable HTTP transport, API keys, OAuth 2.1 + PKCE             |
| 8     | Distribute + Skills    | DXT packaging, bundled `SKILL.md` companion                       |

Levels unlock **strictly linearly** — clearing N.L unlocks N.(L+1).
Clearing a world's last level unlocks the next world.

## Run it

One command, any OS:

```bash
python start.py        # macOS, Linux, Windows — works everywhere
./start.sh             # macOS / Linux convenience shim
start.bat              # Windows convenience shim (cmd.exe or double-click)
```

First run creates `backend/.venv`, installs Python deps, runs
`npm install` for the frontend, then starts both servers:

- Frontend: <http://127.0.0.1:5173>
- Backend:  <http://127.0.0.1:8000>  ·  health: `/api/health`

Ctrl+C kills both.

Other modes:

```bash
python start.py --setup      # install deps and exit (no servers)
python start.py --backend    # backend only
python start.py --frontend   # frontend only
python start.py --test       # run the lesson smoke test
```

On first visit you get an **intro screen** with a marquee, the end-state
demo, and a tour of the 8 worlds. Replayable any time via the `▸ INTRO`
button in the HUD.

## What lives where

```
mcp-teacher/
├── CLAUDE.md              ← project OS (auto-loaded by Claude Code)
├── DECISIONS.md           ← append-only design-decision log
├── start.py               ← cross-platform launcher (the real entry point)
├── start.sh               ← POSIX shim → start.py
├── start.bat              ← Windows shim → start.py
├── .env.example           ← template for future secrets
├── .claude/
│   ├── settings.json      ← shared permissions
│   ├── launch.json        ← `frontend` + `backend` preview targets
│   ├── commands/
│   │   └── grade-server.md  ← `/grade-server` slash command
│   ├── rules/
│   │   └── tools-must-annotate.md
│   ├── skills/
│   │   └── pellet-tracker/SKILL.md      (written when you clear W8.2)
│   └── mcp_servers/
│       └── pellet-tracker/
│           ├── server.py     (rewritten on every level clear)
│           ├── PROGRESS.md
│           └── manifest.json (written when you clear W8.1)
│
├── backend/                  ← FastAPI grader + lesson registry
│   ├── main.py               API + save-to-repo
│   ├── grader.py             Spawns student code, talks JSON-RPC, captures trace
│   ├── lessons.py            All 23 lessons (briefs, debriefs, starters, grader steps)
│   ├── _test_all_levels.py   Smoke test: every canonical solution
│   └── requirements.txt
│
└── frontend/                 ← Vite + React + Tailwind arcade UI
    └── src/
        ├── App.tsx
        ├── api.ts            backend client
        ├── store.ts          localStorage save game
        ├── audio.ts          synthesized arcade SFX (Web Audio)
        ├── lib/unlock.ts     linear unlock logic
        └── components/
            ├── IntroScreen.tsx        marquee, mock Claude chat, world tour
            ├── WorldMap.tsx           Pac-Man world picker
            ├── WorldDetail.tsx        per-world level list with lock indicators
            ├── Level.tsx              briefing + editor + inspector
            ├── CodeEditor.tsx         Monaco
            ├── ProtocolInspector.tsx  live JSON-RPC viewer
            ├── ArcadeMarkdown.tsx     arcade-styled markdown for briefs
            ├── LevelCompleteModal.tsx debrief + saved-path callout
            ├── Ghost.tsx, Pacman.tsx  SVG mascots
            └── HUD.tsx
```

## How it works under the hood

```
┌─────────────┐   HTTP   ┌────────────┐  spawn (stdio)  ┌──────────────┐
│  React UI   │ ───────► │  FastAPI   │ ──────────────► │  Student     │
│  (Vite)     │ /api/run │  grader    │  JSON-RPC 2.0   │  MCP server  │
│             │ ◄─────── │            │ ◄────────────── │  (Python)    │
└─────────────┘  trace   └────────────┘                 └──────────────┘
                          │
                          └─► /api/save-to-repo writes the passing code to
                              .claude/mcp_servers/pellet-tracker/server.py
                              (and manifest.json / SKILL.md on W8 clears)
```

The grader is intentionally **raw JSON-RPC** (no SDK client) so every
line on the wire is captured and shown in the in-app Protocol Inspector.
You see exactly what `initialize`, `tools/list`, `tools/call`,
`resources/read`, `prompts/get`, and the bidirectional
`sampling/createMessage` / `elicitation/create` round-trips look like.

For W5 (bidirectional MCP), the grader **mocks the client side** so
sampling + elicitation tools can run end-to-end inside the academy
without needing a real LLM.

## Requirements

- Python 3.10+ on PATH as `python` or `python3` (3.11+ recommended)
- Node 18+ on PATH (Node 22 is fine)

Windows users: install Python from <https://www.python.org/downloads/>
with "Add to PATH" checked, and Node LTS from <https://nodejs.org/>.

## Reset save

Click `RESET` in the top-right HUD (also wipes intro-seen state), or
`localStorage.clear()` in DevTools.

## Verify the curriculum from the CLI

```bash
python start.py --test
```

Expects `ALL GOOD (23 lessons)`.

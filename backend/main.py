"""FastAPI app for mcp-teacher.

Endpoints:
  GET  /api/health                      — liveness
  GET  /api/world-arc                   — high-level world plan (for the map)
  GET  /api/lessons                     — implemented lessons (summaries)
  GET  /api/lessons/{world}/{level}     — full lesson detail + starter code
  POST /api/run                         — grade a code submission
  POST /api/save-to-repo                — persist passing artifacts into .claude/
"""
from __future__ import annotations

import ast
from dataclasses import asdict
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from grader import grade
from lessons import LESSONS, WORLD_ARC, list_lessons_summary

# repo root is the parent of the backend/ directory
REPO_ROOT = Path(__file__).resolve().parent.parent
PELLET_SERVER_DIR = REPO_ROOT / ".claude" / "mcp_servers" / "pellet-tracker"
PELLET_SKILL_DIR = REPO_ROOT / ".claude" / "skills" / "pellet-tracker"


def _extract_string_constant(source: str, name: str) -> str | None:
    """Pull a module-level string constant out of the student's source.

    Used to fish out `CLAUDE_DESKTOP_SNIPPET`, `DXT_MANIFEST`, `SKILL_MD`
    etc. — concept-level lessons store their answer in a constant rather
    than wiring it into the server's runtime behavior.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return None
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == name:
                    if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                        return node.value.value
    return None

app = FastAPI(title="mcp-teacher", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict:
    return {"ok": True}


@app.get("/api/world-arc")
def world_arc() -> dict:
    implemented_keys = {(l.world, l.level) for l in LESSONS.values()}
    implemented_worlds = {w for (w, _) in implemented_keys}
    return {
        "worlds": WORLD_ARC,
        "implemented_worlds": sorted(implemented_worlds),
        "implemented_levels": sorted(implemented_keys),
    }


@app.get("/api/lessons")
def get_lessons() -> list[dict]:
    return list_lessons_summary()


@app.get("/api/lessons/{world}/{level}")
def get_lesson(world: int, level: int) -> dict:
    lesson = LESSONS.get((world, level))
    if not lesson:
        raise HTTPException(404, f"No lesson at world {world}, level {level}")
    d = asdict(lesson)
    # asdict turns GraderStep dataclasses into dicts already — strip internal expects.
    d["grader_steps"] = [
        {"kind": s["kind"], "description": s["description"]}
        for s in d["grader_steps"]
    ]
    return d


class RunRequest(BaseModel):
    world: int
    level: int
    code: str


@app.post("/api/run")
async def run(req: RunRequest) -> dict:
    return await grade(req.world, req.level, req.code)


class SaveRequest(BaseModel):
    world: int
    level: int
    code: str


@app.post("/api/save-to-repo")
def save_to_repo(req: SaveRequest) -> dict:
    """Persist the player's passing submission into the actual repo.

    Always writes `server.py` + `PROGRESS.md`. For W8 levels that produce
    standalone artifacts (a DXT manifest in W8.1, a SKILL.md in W8.2),
    also extract the relevant Python string constant and write it to its
    canonical location so the repo accumulates the full bundle.
    """
    PELLET_SERVER_DIR.mkdir(parents=True, exist_ok=True)
    server_path = PELLET_SERVER_DIR / "server.py"
    server_path.write_text(req.code)

    extra_saved: dict[str, str] = {}

    # W8.1: extract DXT_MANIFEST → manifest.json
    if (req.world, req.level) == (8, 1):
        manifest = _extract_string_constant(req.code, "DXT_MANIFEST")
        if manifest and manifest.strip():
            manifest_path = PELLET_SERVER_DIR / "manifest.json"
            manifest_path.write_text(manifest.strip() + "\n")
            extra_saved["manifest"] = str(manifest_path.relative_to(REPO_ROOT))

    # W8.2: extract SKILL_MD → .claude/skills/pellet-tracker/SKILL.md
    if (req.world, req.level) == (8, 2):
        skill_md = _extract_string_constant(req.code, "SKILL_MD")
        if skill_md and skill_md.strip():
            PELLET_SKILL_DIR.mkdir(parents=True, exist_ok=True)
            skill_path = PELLET_SKILL_DIR / "SKILL.md"
            skill_path.write_text(skill_md.strip() + "\n")
            extra_saved["skill"] = str(skill_path.relative_to(REPO_ROOT))
            # Seed the conventional skill subdirs so future scripts/refs/assets land cleanly.
            for sub in ("scripts", "references", "assets"):
                (PELLET_SKILL_DIR / sub).mkdir(exist_ok=True)

    progress_path = PELLET_SERVER_DIR / "PROGRESS.md"
    lesson = LESSONS.get((req.world, req.level))
    title = lesson.title if lesson else f"W{req.world}L{req.level}"
    extras_block = ""
    if extra_saved:
        extras_block = "\n\n## Latest extras saved\n\n" + "\n".join(
            f"- `{p}`" for p in extra_saved.values()
        )
    progress_path.write_text(
        f"# Pellet Tracker — your in-progress server\n\n"
        f"Last passed: **World {req.world}, Level {req.level} — {title}**\n\n"
        f"This file is auto-updated by mcp-teacher every time you clear a level.\n"
        f"The current `server.py` is the cumulative working code through that level."
        f"{extras_block}\n\n"
        f"## How to use it\n\n"
        f"```bash\n"
        f"# Run it directly:\n"
        f"python {server_path.relative_to(REPO_ROOT)}\n\n"
        f"# Register with Claude Code (project scope):\n"
        f"claude mcp add pellet-tracker \\\n"
        f"    --command python \\\n"
        f"    --args ./{server_path.relative_to(REPO_ROOT)}\n"
        f"```\n"
    )
    return {
        "saved": True,
        "path": str(server_path.relative_to(REPO_ROOT)),
        "abs_path": str(server_path),
        **{f"saved_{k}": v for k, v in extra_saved.items()},
    }

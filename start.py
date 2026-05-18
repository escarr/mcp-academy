"""Cross-platform launcher for MCP Academy.

Usage:
  python start.py              run both backend (:8000) and frontend (:5173)
  python start.py --backend    backend only (used by .claude/launch.json)
  python start.py --frontend   frontend only (used by .claude/launch.json)
  python start.py --setup      install deps, don't launch anything
  python start.py --test       run backend/_test_all_levels.py in the venv

Works on macOS, Linux, and Windows. Requires Python 3.10+ and Node 18+ on PATH.
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BACKEND = ROOT / "backend"
FRONTEND = ROOT / "frontend"
VENV = BACKEND / ".venv"
IS_WIN = os.name == "nt"


def venv_bin(name: str) -> Path:
    sub = "Scripts" if IS_WIN else "bin"
    ext = ".exe" if IS_WIN else ""
    return VENV / sub / f"{name}{ext}"


def find_system_python() -> str:
    """Pick a Python 3.10+ to bootstrap the venv with."""
    if sys.version_info >= (3, 10):
        return sys.executable
    for cmd in ("python3.13", "python3.12", "python3.11", "python3.10", "python3", "python"):
        exe = shutil.which(cmd)
        if exe:
            return exe
    if IS_WIN:
        exe = shutil.which("py")
        if exe:
            return exe
    sys.exit(
        "✗ Python 3.10+ not found on PATH.\n"
        "  Install from https://www.python.org/downloads/ and re-run."
    )


def find_npm() -> str:
    exe = shutil.which("npm")
    if not exe:
        sys.exit(
            "✗ Node.js / npm not found on PATH.\n"
            "  Install from https://nodejs.org/ (LTS) and re-run."
        )
    return exe


def ensure_venv() -> None:
    if VENV.exists():
        return
    py = find_system_python()
    print("▌ creating backend venv…")
    subprocess.check_call([py, "-m", "venv", str(VENV)])
    pip = venv_bin("pip")
    subprocess.check_call([str(pip), "install", "--upgrade", "pip"])
    subprocess.check_call([str(pip), "install", "-r", str(BACKEND / "requirements.txt")])


def ensure_node_modules() -> None:
    if (FRONTEND / "node_modules").exists():
        return
    npm = find_npm()
    print("▌ installing frontend deps…")
    subprocess.check_call([npm, "install"], cwd=str(FRONTEND))


def spawn(cmd: list[str], cwd: Path) -> subprocess.Popen:
    kwargs: dict = {"cwd": str(cwd)}
    if IS_WIN:
        kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP  # type: ignore[attr-defined]
    return subprocess.Popen(cmd, **kwargs)


def backend_cmd() -> list[str]:
    return [
        str(venv_bin("uvicorn")),
        "main:app",
        "--reload",
        "--port",
        "8000",
        "--host",
        "127.0.0.1",
    ]


def frontend_cmd() -> list[str]:
    return [find_npm(), "run", "dev"]


def run_backend_only() -> int:
    ensure_venv()
    return subprocess.call(backend_cmd(), cwd=str(BACKEND))


def run_frontend_only() -> int:
    ensure_node_modules()
    return subprocess.call(frontend_cmd(), cwd=str(FRONTEND))


def run_both() -> int:
    ensure_venv()
    ensure_node_modules()
    print("▌ starting backend on http://127.0.0.1:8000")
    back = spawn(backend_cmd(), BACKEND)
    print("▌ starting frontend on http://127.0.0.1:5173")
    front = spawn(frontend_cmd(), FRONTEND)
    try:
        while True:
            for p in (back, front):
                if p.poll() is not None:
                    raise SystemExit(p.returncode or 0)
            try:
                back.wait(timeout=0.5)
            except subprocess.TimeoutExpired:
                pass
    except KeyboardInterrupt:
        print("\n▌ shutting down…")
    finally:
        for p in (back, front):
            if p.poll() is None:
                p.terminate()
        for p in (back, front):
            try:
                p.wait(timeout=5)
            except subprocess.TimeoutExpired:
                p.kill()
    return 0


def run_test() -> int:
    ensure_venv()
    return subprocess.call(
        [str(venv_bin("python")), str(BACKEND / "_test_all_levels.py")],
        cwd=str(BACKEND),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--backend", action="store_true", help="run backend only")
    group.add_argument("--frontend", action="store_true", help="run frontend only")
    group.add_argument("--setup", action="store_true", help="install deps and exit")
    group.add_argument("--test", action="store_true", help="run the lesson smoke test")
    args = parser.parse_args()

    if args.setup:
        ensure_venv()
        ensure_node_modules()
        print("▌ setup complete. run `python start.py` to launch.")
        return 0
    if args.backend:
        return run_backend_only()
    if args.frontend:
        return run_frontend_only()
    if args.test:
        return run_test()
    return run_both()


if __name__ == "__main__":
    sys.exit(main())

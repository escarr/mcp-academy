#!/usr/bin/env bash
# Launch mcp-teacher: backend on :8000, frontend on :5173.
# Both run in the foreground; Ctrl+C kills both via trap.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

if [ ! -d backend/.venv ]; then
  echo "▌ creating backend venv…"
  /usr/local/bin/python3.13 -m venv backend/.venv
  backend/.venv/bin/pip install --upgrade pip
  backend/.venv/bin/pip install -r backend/requirements.txt
fi

if [ ! -d frontend/node_modules ]; then
  echo "▌ installing frontend deps…"
  (cd frontend && npm install)
fi

trap 'echo; echo "▌ shutting down…"; kill $BACK_PID $FRONT_PID 2>/dev/null || true; exit 0' INT TERM

echo "▌ starting backend on http://127.0.0.1:8000"
(cd backend && .venv/bin/uvicorn main:app --reload --port 8000) &
BACK_PID=$!

echo "▌ starting frontend on http://127.0.0.1:5173"
(cd frontend && npm run dev) &
FRONT_PID=$!

wait $BACK_PID $FRONT_PID

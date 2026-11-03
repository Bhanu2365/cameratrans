#!/bin/bash
set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"
if [ ! -x "$ROOT/backend/.venv/bin/python" ] || [ ! -d "$ROOT/frontend/node_modules" ]; then
  echo "Run the setup steps in README.md first."
  read -r -p "Press Return to close..."
  exit 1
fi
cd "$ROOT/backend"
.venv/bin/python manage.py migrate
.venv/bin/python manage.py runserver 0.0.0.0:8000 > "$ROOT/backend-server.log" 2>&1 &
BACKEND_PID=$!
trap 'kill "$BACKEND_PID" 2>/dev/null || true' EXIT INT TERM
sleep 2
open "http://localhost:5173" 2>/dev/null || true
cd "$ROOT/frontend"
npm run dev -- --host 0.0.0.0

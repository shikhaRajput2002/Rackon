#!/bin/bash
# Runs the app locally.
#
#   ./dev.sh          API + Celery worker + Celery beat + frontend  (4 processes)
#   ./dev.sh light    API + frontend only, Celery tasks run inline  (2 processes)
#
# Use light mode on a machine with little RAM. Everything still works — the
# challenge and the review sweep just run in the request instead of on a queue.
set -e
cd "$(dirname "$0")"
VENV=./backend/reckon_venv/bin

if [ ! -x "$VENV/python" ]; then
  echo "No virtualenv. Run:"
  echo "  cd backend && python3.12 -m venv reckon_venv && ./reckon_venv/bin/pip install -r requirements.txt"
  exit 1
fi

trap 'kill 0' EXIT

if [ "$1" = "light" ]; then
  export CELERY_TASK_ALWAYS_EAGER=True
  echo "light mode — Celery tasks run inline, no worker or beat"
else
  if ! redis-cli ping > /dev/null 2>&1; then
    echo "Redis is not running. Start it with 'brew services start redis', or use ./dev.sh light"
    exit 1
  fi
  (cd backend && ./reckon_venv/bin/celery -A reckon worker -l warning --concurrency=1) &
  (cd backend && ./reckon_venv/bin/celery -A reckon beat -l warning) &
fi

(cd frontend && npm run dev) &
cd backend && ./reckon_venv/bin/python manage.py runserver 8000

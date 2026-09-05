#!/bin/bash
# Starts the whole app: API, Celery worker, Celery beat, and the frontend.
# Ctrl-C stops all four.
set -e
cd "$(dirname "$0")"
VENV=./backend/reckon_venv/bin

if [ ! -x "$VENV/python" ]; then
  echo "No virtualenv. Run:  cd backend && python3.12 -m venv reckon_venv && ./reckon_venv/bin/pip install -r requirements.txt"
  exit 1
fi

if ! redis-cli ping > /dev/null 2>&1; then
  echo "Redis is not running. Start it with: brew services start redis"
  exit 1
fi

trap 'kill 0' EXIT

(cd backend && ./reckon_venv/bin/celery -A reckon worker -l warning --concurrency=1) &
(cd backend && ./reckon_venv/bin/celery -A reckon beat -l warning) &
(cd frontend && npm run dev) &
cd backend && ./reckon_venv/bin/python manage.py runserver 8000

#!/bin/bash
# Starts the whole backend: API, Celery worker, Celery beat.
# Frontend runs separately: cd frontend && npm run dev
set -e
cd "$(dirname "$0")"
VENV=./reckon_venv/bin

if ! redis-cli ping > /dev/null 2>&1; then
  echo "Redis is not running. Start it with: brew services start redis"
  exit 1
fi

trap 'kill 0' EXIT
$VENV/celery -A reckon worker -l info --concurrency=2 &
$VENV/celery -A reckon beat -l info &
$VENV/python manage.py runserver 8000

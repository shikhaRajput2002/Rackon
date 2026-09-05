#!/bin/bash
set -e
set -o pipefail

autoflake --remove-all-unused-imports --in-place --recursive --exclude reckon_venv,frontend .
isort --profile black --line-length=120 --skip reckon_venv --skip frontend --atomic --combine-as .
black --line-length 120 --exclude '/(reckon_venv|frontend)/' .

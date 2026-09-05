#!/bin/bash
set -e
set -o pipefail

autoflake --remove-all-unused-imports --in-place --recursive --exclude reckon_venv .
isort --profile black --line-length=120 --skip reckon_venv --atomic --combine-as .
black --line-length 120 --exclude '/reckon_venv/' .

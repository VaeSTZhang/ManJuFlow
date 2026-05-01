#!/usr/bin/env bash
set -euo pipefail

# Start the local FastAPI backend for ManJuFlow development.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${PROJECT_ROOT}/apps/api"

source .venv/bin/activate 2>/dev/null || source ../../.venv/bin/activate

uvicorn app.main:app --reload

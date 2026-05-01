#!/usr/bin/env bash
set -euo pipefail

# Start the local FastAPI backend for ManJuFlow development.
# This script avoids sourcing venv activate directly, because activate scripts
# can behave differently under strict shell options.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
API_DIR="${PROJECT_ROOT}/apps/api"

cd "${API_DIR}"

if [[ -x "${API_DIR}/.venv/bin/python" ]]; then
  PYTHON_BIN="${API_DIR}/.venv/bin/python"
elif [[ -x "${PROJECT_ROOT}/.venv/bin/python" ]]; then
  PYTHON_BIN="${PROJECT_ROOT}/.venv/bin/python"
else
  echo "Could not find Python virtual environment."
  echo "Expected one of:"
  echo "- ${API_DIR}/.venv/bin/python"
  echo "- ${PROJECT_ROOT}/.venv/bin/python"
  exit 1
fi

echo "Starting ManJuFlow API..."
echo "API dir: ${API_DIR}"
echo "Python: ${PYTHON_BIN}"

exec "${PYTHON_BIN}" -m uvicorn app.main:app --reload

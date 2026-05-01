#!/usr/bin/env bash
set -euo pipefail

# Clear the local FastAPI backend port when it is occupied by uvicorn.
PORT="${1:-8000}"

echo "Checking port ${PORT}..."

PIDS="$(lsof -ti tcp:"${PORT}" || true)"

if [[ -z "${PIDS}" ]]; then
  echo "No process is using port ${PORT}."
  exit 0
fi

echo "Process(es) using port ${PORT}:"
echo "${PIDS}"

for PID in ${PIDS}; do
  echo "Sending SIGTERM to PID ${PID}..."
  kill "${PID}"
done

echo "Port ${PORT} cleanup requested."

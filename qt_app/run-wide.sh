#!/usr/bin/env bash
set -euo pipefail

if command -v xset >/dev/null 2>&1; then
  xset s off || true
  xset -dpms || true
  xset s noblank || true
fi

export QT_QPA_PLATFORM="${QT_QPA_PLATFORM:-xcb}"
export FITPRO_API_BASE_URL="${FITPRO_API_BASE_URL:-http://127.0.0.1:8000}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "${SCRIPT_DIR}/qt_venv/bin/python" "${SCRIPT_DIR}/main.py" --wide-screen

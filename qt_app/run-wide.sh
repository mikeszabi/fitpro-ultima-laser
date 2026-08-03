#!/usr/bin/env bash
set -euo pipefail

if command -v xset >/dev/null 2>&1; then
  xset s off || true
  xset -dpms || true
  xset s noblank || true
fi

export QT_QPA_PLATFORM="${QT_QPA_PLATFORM:-xcb}"
# Keep touchscreen input on the legacy X11 mouse path. Some Jetson/X11 setups
# delay Qt XInput2 touch delivery until another input event wakes the app.
export QT_XCB_NO_XI2="${QT_XCB_NO_XI2:-1}"
export FITPRO_QT_INPUT_PUMP_MS="${FITPRO_QT_INPUT_PUMP_MS:-0}"
export FITPRO_API_BASE_URL="${FITPRO_API_BASE_URL:-http://127.0.0.1:8000/api}"
export PYTHONUNBUFFERED="${PYTHONUNBUFFERED:-1}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "${SCRIPT_DIR}/qt_venv/bin/python" "${SCRIPT_DIR}/main.py" --wide-screen

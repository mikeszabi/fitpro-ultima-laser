#!/usr/bin/env bash
set -euo pipefail

# Disable screen saver and power management
if command -v xset >/dev/null 2>&1; then
  xset s off || true
  xset -dpms || true
  xset s noblank || true
fi

export QT_QPA_PLATFORM="${QT_QPA_PLATFORM:-xcb}"
export FITPRO_API_BASE_URL="${FITPRO_API_BASE_URL:-http://127.0.0.1:8000/api}"
export PYTHONUNBUFFERED="${PYTHONUNBUFFERED:-1}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Find the virtual environment - check multiple possible locations
VENV_PYTHON=""
for venv_path in "${SCRIPT_DIR}/qt_venv" "${SCRIPT_DIR}/.venv" "${SCRIPT_DIR}/venv"; do
  if [[ -f "${venv_path}/bin/python" ]]; then
    VENV_PYTHON="${venv_path}/bin/python"
    echo "Using Python from: ${VENV_PYTHON}" >&2
    break
  fi
done

# If no venv found, try system Python
if [[ -z "${VENV_PYTHON}" ]]; then
  echo "Warning: No virtual environment found in standard locations" >&2
  echo "Attempting to use system Python..." >&2
  VENV_PYTHON=$(command -v python3 || command -v python || echo "")
  
  if [[ -z "${VENV_PYTHON}" ]]; then
    echo "Error: Could not find Python interpreter" >&2
    exit 1
  fi
fi

echo "Starting FitPro Ultima Laser Qt application with: ${VENV_PYTHON}" >&2
exec "${VENV_PYTHON}" "${SCRIPT_DIR}/main.py" "$@"

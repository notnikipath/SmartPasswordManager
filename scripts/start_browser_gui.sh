#!/bin/sh
set -eu

DISPLAY_VALUE="${DISPLAY:-:1}"
VNC_PORT="${VNC_PORT:-5900}"
NOVNC_PORT="${NOVNC_PORT:-6080}"
XVFB_SCREEN="${XVFB_SCREEN:-1366x768x24}"
APP_PID=""

echo "[startup] DISPLAY=${DISPLAY_VALUE}, VNC_PORT=${VNC_PORT}, NOVNC_PORT=${NOVNC_PORT}"

Xvfb "${DISPLAY_VALUE}" -screen 0 "${XVFB_SCREEN}" -ac +extension GLX +render -noreset &
XVFB_PID=$!

sleep 1

fluxbox >/tmp/fluxbox.log 2>&1 &
FLUXBOX_PID=$!

x11vnc \
  -display "${DISPLAY_VALUE}" \
  -rfbport "${VNC_PORT}" \
  -forever \
  -shared \
  -nopw \
  -listen 0.0.0.0 \
  >/tmp/x11vnc.log 2>&1 &
X11VNC_PID=$!

if command -v novnc_proxy >/dev/null 2>&1; then
  novnc_proxy --listen "${NOVNC_PORT}" --vnc "localhost:${VNC_PORT}" >/tmp/novnc.log 2>&1 &
  NOVNC_PID=$!
elif [ -x /usr/share/novnc/utils/novnc_proxy ]; then
  /usr/share/novnc/utils/novnc_proxy --listen "${NOVNC_PORT}" --vnc "localhost:${VNC_PORT}" >/tmp/novnc.log 2>&1 &
  NOVNC_PID=$!
else
  websockify --web=/usr/share/novnc/ "${NOVNC_PORT}" "localhost:${VNC_PORT}" >/tmp/novnc.log 2>&1 &
  NOVNC_PID=$!
fi

cleanup() {
  [ -n "${APP_PID}" ] && kill "${APP_PID}" 2>/dev/null || true
  kill "${NOVNC_PID}" "${X11VNC_PID}" "${FLUXBOX_PID}" "${XVFB_PID}" 2>/dev/null || true
}

trap cleanup INT TERM

python src/app.py &
APP_PID=$!

wait "${APP_PID}"

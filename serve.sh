#!/usr/bin/env bash
# Space Blaster — booth launcher
#
# Copies the pristine base game (game-base.html) over game.html, installs pi
# and the Lemonade model if they are missing, and starts the booth HTTP server
# DETACHED from this terminal, so that the in-browser "Reset" (which closes
# every gnome-terminal window) never kills the server.
#
# The server is stdlib Python 3 only. pi brings its own Node.js if needed.

set -e

# Always operate from the directory this script lives in (the repo root).
cd "$(dirname "$0")"

PORT="${1:-8000}"
LOG="booth_server.log"

# 1. Provision the pristine base copy.
cp game-base.html game.html

echo ""
echo "  Space Blaster booth"
echo "  ─────────────────────────────────────"
echo "  Base game:       game-base.html"
echo "  Working game:    game.html"
echo "  Open in a browser: http://localhost:${PORT}"
echo ""

# 2. Install pi and the model now (the pi installer may ask to confirm), so
#    the first "Launch pi" click goes straight to the agent.
if ! ./launch_pi.sh --install-only; then
  echo "  WARNING: pi or the model is not installed. Rerun ./serve.sh to retry."
fi
echo ""

# 3. Free the port: stop any previous booth server (this one) OR a stale
#    legacy static server (python3 -m http.server) left on the same port.
pkill -f booth_server.py 2>/dev/null || true
pkill -f "http.server ${PORT}" 2>/dev/null || true
sleep 0.5

# 4. Launch the booth server fully detached from this terminal.
setsid python3 booth_server.py "$PORT" \
  >"$LOG" 2>&1 < /dev/null &
disown 2>/dev/null || true

sleep 1
echo "  Booth server started (detached).  Logs: $LOG"
echo "  Stop it later with:   pkill -f booth_server.py"
echo ""

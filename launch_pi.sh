#!/usr/bin/env bash
# Space Blaster — pi launcher
#
# Opens pi in this folder on the local Lemonade model, installing pi first if
# it is missing. booth_server.py runs this in a fresh gnome-terminal after every
# reset; serve.sh runs it with --install-only so the installs happen up front.
#
# Usage:
#   ./launch_pi.sh [MODEL]                 install pi if needed, then launch it
#   ./launch_pi.sh --install-only [MODEL]  install pi and the model, then exit
#
# MODEL defaults to $BOOTH_MODEL, else Qwen3.6-35B-A3B-ThinkingCoder. Passing
# -m is the deterministic equivalent of picking the recipe from the
# "lemonade launch pi" menu.

set -euo pipefail

# Always operate from the directory this script lives in (the repo root), so pi
# discovers .pi/ (agents, commands, sub-agent extension).
cd "$(dirname "$0")"

INSTALL_ONLY=0
if [ "${1:-}" = "--install-only" ]; then
  INSTALL_ONLY=1
  shift
fi
MODEL="${1:-${BOOTH_MODEL:-Qwen3.6-35B-A3B-ThinkingCoder}}"

# The pi installer puts its launcher in ~/.pi/agent/bin but only adds that to
# PATH through ~/.bashrc, which `bash -lc` (non-interactive) never reaches.
# Putting it first also makes the installer below pick this same directory.
export PATH="$HOME/.pi/agent/bin:$PATH"

if ! command -v pi >/dev/null 2>&1; then
  echo "[booth] pi is not installed — running the pi installer (https://pi.dev/install.sh)"
  # The installer brings its own Node.js when the system one is older than
  # 22.19, so no sudo is needed. Piping its output through cat stops it from
  # asking "Start pi now?" at the end (it only asks on a terminal), which would
  # open pi without the Lemonade model.
  curl -fsSL https://pi.dev/install.sh | sh | cat
  hash -r
  if ! command -v pi >/dev/null 2>&1; then
    echo "[booth] pi is still not on PATH after the install — see https://pi.dev" >&2
    exit 1
  fi
fi

if [ "$INSTALL_ONLY" = 1 ]; then
  # The default model is a recipe from Lemonade's coding-agents collection, not
  # a built-in model, so a fresh machine does not know it yet. Importing it
  # also downloads it (~20 GB); a built-in model only needs the download.
  downloaded=$(lemonade list --downloaded 2>/dev/null || true)
  if ! grep -q "^$MODEL " <<<"$downloaded"; then
    echo "[booth] adding $MODEL to Lemonade (one-time download)"
    lemonade import --directory coding-agents --recipe-file "$MODEL.json" --yes \
      || lemonade pull "$MODEL"
  fi
  echo "[booth] pi $(pi --version) ready: $(command -v pi)"
  echo "[booth] model ready: $MODEL"
  exit 0
fi

# --approve trusts this folder's .pi/ for the run, so a fresh session never
# stops at pi's project-trust prompt. lemonade passes it through after its own
# --provider/--model flags. The = form keeps lemonade from parsing it.
exec lemonade launch pi -m "$MODEL" --agent-args=--approve

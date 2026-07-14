#!/usr/bin/env python3
"""Space Blaster — booth server.

Serves the booth wrapper (index.html) and the working game.html, and exposes a
single POST /reset endpoint that:

  1. Restores game.html from the pristine game-base.html, and
  2. Closes the attendee's opencode session + gnome-terminal windows so the
     next player starts from scratch.

The server is meant to be launched DETACHED from any terminal (see serve.sh),
so closing every gnome-terminal window during a reset never kills the server.

Stdlib only — no third-party dependencies, matching the rest of the repo.
"""

import http.server
import json
import os
import shlex
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# Model to pre-select for opencode after a reset. This is the deterministic
# equivalent of picking the model from the "lemonade launch opencode" menu
# (formerly "option 9"). Override with the BOOTH_MODEL env var.
DEFAULT_MODEL = "Qwen3.6-35B-A3B-ThinkingCoder"
BASE_GAME = ROOT / "game-base.html"
WORKING_GAME = ROOT / "game.html"

# Paths that must never be cached, so the iframe always reloads the latest game
# (after an agent edit or a reset).
NO_CACHE_PATHS = {"/", "/index.html", "/game.html"}


def restore_base() -> bool:
    """Copy the pristine base game over the working game.html. Returns success."""
    if not BASE_GAME.exists():
        return False
    shutil.copyfile(BASE_GAME, WORKING_GAME)
    return True


def cleanup_terminals() -> None:
    """End the attendee's agent session, close all gnome-terminal windows, and
    open a fresh opencode session for the next visitor.

    The booth server runs detached (its own session), so it is not a child of
    gnome-terminal-server and survives the window kills.

    Set BOOTH_SKIP_CLEANUP=1 to restore the game without touching terminals
    (useful for local testing); BOOTH_NO_AUTOSTART=1 to close terminals but not
    reopen a fresh session.
    """
    if os.environ.get("BOOTH_SKIP_CLEANUP"):
        return
    # End the opencode agent + its launcher first (leaves the Lemonade
    # inference server warm for the next player).
    subprocess.run(["pkill", "-f", "opencode"], check=False)
    subprocess.run(["pkill", "-f", "lemonade launch"], check=False)
    # A single gnome-terminal-server owns every window; killing it closes them.
    subprocess.run(["pkill", "-x", "gnome-terminal-server"], check=False)
    # Let the old terminal server fully exit before opening a fresh window.
    time.sleep(1.5)
    start_fresh_session()


def start_fresh_session() -> None:
    """Open a new gnome-terminal in the booth folder and launch opencode with
    the model pre-selected, so the next visitor can prompt @gameplay-rules
    immediately.

    Running from the booth folder is what lets opencode discover
    .opencode/agents/. Passing -m replaces the manual model-menu pick
    ("option 9"). Set BOOTH_NO_AUTOSTART=1 to skip this.
    """
    if os.environ.get("BOOTH_NO_AUTOSTART"):
        return
    model = os.environ.get("BOOTH_MODEL", DEFAULT_MODEL)
    inner = (
        f"cd {shlex.quote(str(ROOT))} && "
        f"lemonade launch opencode -m {shlex.quote(model)}; "
        "echo; echo '[booth] session ended — press Enter to close'; read _"
    )
    subprocess.Popen(
        ["gnome-terminal", f"--working-directory={ROOT}", "--",
         "bash", "-lc", inner],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )


class BoothHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def end_headers(self):
        if self.path.split("?", 1)[0] in NO_CACHE_PATHS:
            self.send_header("Cache-Control", "no-store, must-revalidate")
            self.send_header("Pragma", "no-cache")
            self.send_header("Expires", "0")
        super().end_headers()

    def do_POST(self):
        if self.path.split("?", 1)[0] != "/reset":
            self.send_error(404, "Not found")
            return

        restored = restore_base()
        payload = json.dumps({
            "ok": restored,
            "base": str(BASE_GAME),
            "error": None if restored else f"base not found at {BASE_GAME}",
        }).encode()

        self.send_response(200 if restored else 500)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)
        try:
            self.wfile.flush()
        except Exception:
            pass

        # Tear down terminals only AFTER the browser has its confirmation.
        if restored:
            cleanup_terminals()

    def log_message(self, fmt, *args):
        sys.stderr.write("  [booth] " + (fmt % args) + "\n")


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000

    # Verify the pristine base exists.
    if not BASE_GAME.exists():
        sys.exit(f"No base game found ({BASE_GAME}).")

    # Every boot starts from a clean working copy.
    restore_base()

    httpd = http.server.ThreadingHTTPServer(("", port), BoothHandler)
    print(f"  Booth server live on http://localhost:{port}")
    print(f"  Base game: {BASE_GAME}")
    print(f"  Working game: {WORKING_GAME}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()


if __name__ == "__main__":
    main()

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

import atexit
import http.server
import json
import os
import shlex
import shutil
import signal
import subprocess
import sys
import threading
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

# SSE endpoint that streams live GPU telemetry into the booth's "Lemonade Logs"
# panel, so visitors can watch the local hardware work while the model runs.
GPU_STREAM_PATH = "/gpu-stream"


# `amd-smi monitor` in 1s watch mode, CSV so columns are keyed by name. Most
# fields read N/A on the Strix Halo APU; VRAM_USED (the resident Qwen model) is
# the meaningful GPU-usage signal, so we distil each row down to that.
GPU_MONITOR_CMD = ["amd-smi", "monitor", "-p", "-u", "-v", "-t", "--csv", "-w", "1"]

# amd-smi is itself a Python program that block-buffers stdout when piped, so in
# infinite watch mode its rows would never reach us. PYTHONUNBUFFERED forces each
# sample to flush immediately (also lets the read loop notice a dropped client).
GPU_MONITOR_ENV = {**os.environ, "PYTHONUNBUFFERED": "1"}

# Live amd-smi children run in their own session (so a dropped client can killpg
# the whole tree). That also means killing the server would ORPHAN them, so we
# track them and reap on shutdown (atexit + SIGTERM) as well as on disconnect.
_gpu_children = set()
_gpu_children_lock = threading.Lock()


def _kill_gpu_child(proc) -> None:
    try:
        os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
    except (ProcessLookupError, PermissionError):
        pass


def reap_gpu_children(*_) -> None:
    """Terminate every live amd-smi child. Registered with atexit and SIGTERM."""
    with _gpu_children_lock:
        procs = list(_gpu_children)
        _gpu_children.clear()
    for proc in procs:
        _kill_gpu_child(proc)


def format_gpu_row(cols: dict) -> str:
    """Distil one amd-smi CSV sample (name -> value dict) into a compact line
    highlighting GPU usage. VRAM is always shown; power / clock / temperature are
    appended only when the hardware actually reports them (not "N/A")."""
    def val(name):
        v = cols.get(name, "N/A")
        return None if v in ("", "N/A") else v

    used, total, pct = val("vram_used"), val("vram_total"), val("vram_percent")
    if used is None or total is None:
        return ""  # no VRAM data — nothing worth showing

    try:
        clock = time.strftime("%H:%M:%S", time.localtime(int(cols["timestamp"])))
    except (KeyError, ValueError):
        clock = time.strftime("%H:%M:%S")

    line = f"{clock}  VRAM {used}/{total} MB"
    if pct is not None:
        line += f" ({pct}%)"

    extras = []
    if val("power_usage"):
        extras.append(f"{cols['power_usage']} W")
    if val("gfx_clk"):
        extras.append(f"GFX {cols['gfx_clk']} MHz")
    if val("hotspot_temperature"):
        extras.append(f"{cols['hotspot_temperature']}°C")
    if extras:
        line += "  ·  " + "  ·  ".join(extras)
    return line


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
    # `bash -lc` is non-interactive, so ~/.bashrc returns before its PATH
    # export for the opencode installer; add the default install dir here.
    inner = (
        'export PATH="$HOME/.opencode/bin:$PATH"; '
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

    def do_GET(self):
        if self.path.split("?", 1)[0] == GPU_STREAM_PATH:
            self.stream_gpu()
            return
        super().do_GET()

    def stream_gpu(self):
        """Stream `amd-smi monitor` to the browser as Server-Sent Events.

        Each 1s CSV sample is distilled by format_gpu_row() into one compact
        SSE frame highlighting GPU/VRAM usage; the repeating header and spacer
        lines are dropped. The amd-smi child runs in its own process group so it
        can be killed cleanly when the visitor's browser goes away.
        """
        if not shutil.which("amd-smi"):
            self.send_error(503, "amd-smi not available")
            return
        try:
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache, no-store")
            self.send_header("Connection", "keep-alive")
            self.end_headers()
        except (BrokenPipeError, ConnectionResetError):
            return

        proc = subprocess.Popen(
            GPU_MONITOR_CMD,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            env=GPU_MONITOR_ENV,
            start_new_session=True,
        )
        with _gpu_children_lock:
            _gpu_children.add(proc)
        header = None  # CSV column names, refreshed each time amd-smi reprints them
        try:
            for raw in proc.stdout:
                stripped = raw.strip()
                # Drop the "CTRL+C to stop" banner and blank spacer lines.
                if not stripped or "CTRL" in stripped:
                    continue
                fields = stripped.split(",")
                # amd-smi reprints the header before every sample; capture it.
                if fields[0] == "timestamp":
                    header = fields
                    continue
                if header is None or len(fields) != len(header):
                    continue
                line = format_gpu_row(dict(zip(header, fields)))
                if line and not self._sse(line):
                    break  # browser disconnected
        finally:
            _kill_gpu_child(proc)
            with _gpu_children_lock:
                _gpu_children.discard(proc)
            if proc.stdout:
                proc.stdout.close()

    def _sse(self, text: str) -> bool:
        """Write one SSE `data:` frame; return False if the client disconnected."""
        try:
            self.wfile.write(("data: " + text + "\n\n").encode())
            self.wfile.flush()
            return True
        except (BrokenPipeError, ConnectionResetError):
            return False

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

    # Never leave amd-smi children behind when the server stops or is killed.
    atexit.register(reap_gpu_children)
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))

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

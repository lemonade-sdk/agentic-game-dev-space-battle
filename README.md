# 🚀 Space Blaster — Agentic Game Development with pi

> **Ask AI agents to add features to a space shooter — live, on your local AMD
> GPU. No cloud. No API keys.**

The whole game is one file, `game.html`. Five AI agents edit it from inside
**[pi](https://pi.dev)**, running on the **Qwen3.6-35B-A3B-ThinkingCoder** model
served locally by **[Lemonade Server](https://lemonade-server.ai)** on the
**AMD Ryzen AI Max 395 (Strix Halo)**. You tell an agent what to build, it edits
`game.html`, and you refresh the browser to play the result.

---

> **On Windows?** Every step works the same — just use the Windows commands
> shown under each step. See [Windows notes](#windows-notes) for what differs.

## Step 1 — Install Lemonade Server (once per machine)

```bash
sudo add-apt-repository ppa:lemonade-team/stable
sudo apt install lemonade-server
```

**Windows:** install Lemonade Server from
[lemonade-server.ai](https://lemonade-server.ai) and
[Python 3](https://www.python.org/downloads/).

You don't need to install pi or the model yourself. Step 3 does it.

## Step 2 — Get the workshop

```bash
git clone https://github.com/lemonade-sdk/agentic-game-dev-space-battle.git
cd agentic-game-dev-space-battle
```

## Step 3 — Start the booth

```bash
./serve.sh
```

**Windows:** run `serve.cmd` (or double-click it). It wraps `serve.ps1`, so no
execution-policy change is needed.

This:

1. resets `game.html` to the starting game (`game-base.html`)
2. installs pi if it is missing. If the pi installer asks you to confirm,
   press **Enter**. It brings its own Node.js, so no sudo is needed.
3. adds the `Qwen3.6-35B-A3B-ThinkingCoder` model to Lemonade if it isn't there
   yet. **The first run downloads about 22 GB.**
4. starts the booth server in the background on port 8000

## Step 4 — Open the booth page

Open **http://localhost:8000** in a browser.

- **Right:** the game. It already works, so try it:

  | Key | Action |
  |-----|--------|
  | `WASD` / Arrows | Move |
  | `Space` | Shoot |
  | `P` | Pause |
  | `R` | Restart after game over |

- **Left:** live GPU memory use from `amd-smi`, so you can watch the local
  model work. **⚡ Lemonade Logs** opens the Lemonade dashboard.

## Step 5 — Launch pi

Click **Launch pi with Lemonade**, then **Reset**.

A terminal opens with pi already running on the Qwen model in the workshop
folder. Every click also resets `game.html` and closes the previous terminals,
so each player starts fresh.

## Step 6 — Check the agents are loaded

In pi, type `/`. You should see one command per agent:

| Command | What it owns |
|---------|--------------|
| `/ui-renderer` | Everything you see: canvas, star-field, ships, particles, HUD |
| `/physics-movement` | Input, movement, bullets, collisions |
| `/gameplay-rules` | Score, levels, enemy spawning, lives, game over |
| `/vfx-polish` | Screen shake, hit flashes, damage vignette, trails, nebula |
| `/boss-ai` | A 3-phase boss with attack patterns and a health bar |

The agents are defined in `.pi/agents/`, one Markdown file each.

## Step 7 — Give an agent a task

Type the agent's command, then what you want:

```
/vfx-polish add screen shake on player hit and red vignette when lives = 1
```

The agent runs as a sub-agent with its own context. Its box shows a timer,
then `thinking… (N lines)`, then `✎ editing game.html · N lines` as the code
streams in. When it finishes, pi replies with a sentence on what changed.

You can also run `/agents`, pick an agent from the list, and type the request as
a plain message.

## Step 8 — Play the new version

Refresh the booth page (**F5**). The game reloads with the agent's changes.

Repeat Steps 7 and 8 as often as you like.

## Step 9 — Push the agents further

Try these, one at a time, putting the agent's command first.

**`/ui-renderer`**
```
add a pulsing cyan ring around the player when shield > 0
add a warp-speed animation when the level increases
make explosions leave a smoke cloud that fades slowly
```

**`/physics-movement`**
```
add a dodge-roll on Shift with invincibility frames and 2s cooldown
make cruiser enemies strafe side to side while descending
add a homing missile on the X key
make enemies shoot back at the player starting at level 4
```

**`/gameplay-rules`**
```
add a score combo — consecutive kills within 1.5s multiply points
add a shield power-up that drops from bombers with 15% chance
save the high score to localStorage and show it on game-over
add a survival wave at level 3 — only drones for 10 seconds
```

**`/vfx-polish`**
```
add an animated nebula drifting across the star-field
add a motion trail behind the player ship
```

**`/boss-ai`**
```
add a 3-phase boss called The Void Sovereign that spawns at level 5
```

## Step 10 — Hand over to the next player

Click **Launch pi with Lemonade** → **Reset** again.

---

## Troubleshooting

**Arrow keys don't move the ship.** Click the game to give it focus, or ask:
```
/physics-movement arrow keys not working — fix keyboard focus on the canvas
```

**An agent broke the game.** Click **Launch pi with Lemonade** → **Reset** to
go back to the starting game.

**The `/ui-renderer`-style commands are missing.** pi was started some other
way and skipped the project's `.pi/` folder. Close it and start pi from the
booth page, or from the workshop folder with:
```bash
./launch_pi.sh
```
(Windows: `powershell -ExecutionPolicy Bypass -File .\launch_pi.ps1`)

**Use a different model.** Start the booth with `BOOTH_MODEL` set to a
Lemonade model name, e.g. the faster non-thinking variant:
```bash
BOOTH_MODEL=Qwen3.6-35B-A3B-NoThinking ./serve.sh
```
```powershell
$env:BOOTH_MODEL = 'Qwen3.6-35B-A3B-NoThinking'; .\serve.cmd   # Windows
```

**Stop the booth server.**
```bash
pkill -f booth_server.py
```
On Windows: `powershell -ExecutionPolicy Bypass -File .\stop.ps1`.
Its log is in `booth_server.log`.

---

## Windows notes

| Linux | Windows |
|-------|---------|
| `serve.sh` | `serve.cmd` → `serve.ps1` |
| `launch_pi.sh` | `launch_pi.ps1` (`-InstallOnly`, `-Model NAME`) |
| `pkill -f booth_server.py` | `stop.ps1` |
| pi opens in a `gnome-terminal` window | pi opens in its own console window |
| GPU panel streams `amd-smi` | GPU panel streams Windows GPU counters (`gpu_monitor.ps1`) |

- **GPU panel.** `amd-smi` isn't available on Windows, so `gpu_monitor.ps1`
  reads the same counters Task Manager uses. On the Strix Halo the model sits
  in shared memory, so "VRAM" is the Radeon's dedicated + shared usage, out of
  the dedicated size plus the shared budget (half of system RAM). It also
  shows GPU utilization.
- **Reset** closes only the booth's pi console windows (found by their
  `launch_pi.ps1` command line), not your other terminals.
- **pi's installer** (`pi.dev/install.ps1`) may offer to install Git for
  Windows. Accept it: pi uses Git Bash for its shell tool.

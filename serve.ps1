# Space Blaster — booth launcher (Windows)
#
# Windows counterpart of serve.sh. Copies the pristine base game
# (game-base.html) over game.html, installs pi and the Lemonade model if they
# are missing, and starts the booth HTTP server DETACHED from this terminal,
# so that the in-browser "Reset" (which closes the pi console windows) never
# kills the server.
#
# Usage:  .\serve.ps1 [PORT]     (or double-click / run serve.cmd)
#
# The server is stdlib Python 3 only. pi brings its own Node.js if needed.

param([int]$Port = 8000)

$ErrorActionPreference = 'Stop'

# Always operate from the directory this script lives in (the repo root).
Set-Location $PSScriptRoot

$Log = 'booth_server.log'

# 1. Provision the pristine base copy.
Copy-Item game-base.html game.html -Force

Write-Host ''
Write-Host '  Space Blaster booth'
Write-Host '  -------------------------------------'
Write-Host '  Base game:       game-base.html'
Write-Host '  Working game:    game.html'
Write-Host "  Open in a browser: http://localhost:$Port"
Write-Host ''

# 2. Install pi and the model now (the pi installer may ask to confirm), so
#    the first "Launch pi" click goes straight to the agent.
try { & (Join-Path $PSScriptRoot 'launch_pi.ps1') -InstallOnly } catch { $LASTEXITCODE = 1 }
if ($LASTEXITCODE -ne 0) {
  Write-Host '  WARNING: pi or the model is not installed. Rerun serve.ps1 to retry.'
}
Write-Host ''

# 3. Free the port: stop any previous booth server OR a stale legacy static
#    server (python -m http.server) left on the same port.
& (Join-Path $PSScriptRoot 'stop.ps1') -Quiet
Get-CimInstance Win32_Process |
  Where-Object { $_.ProcessId -ne $PID -and $_.CommandLine -match "http\.server $Port" } |
  ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
Start-Sleep -Milliseconds 500

# 4. Launch the booth server fully detached from this terminal: a hidden cmd
#    with its own console, so closing this window does not take it down.
#    -u keeps the log unbuffered.
$python = if (Get-Command py -ErrorAction SilentlyContinue) { 'py -3' }
          elseif (Get-Command python -ErrorAction SilentlyContinue) { 'python' }
          else { throw 'Python 3 is not installed (https://www.python.org/downloads/).' }
Start-Process cmd.exe -WindowStyle Hidden -WorkingDirectory $PSScriptRoot `
  -ArgumentList '/c', "$python -u booth_server.py $Port > $Log 2>&1"

Start-Sleep -Seconds 1
Write-Host "  Booth server started (detached).  Logs: $Log"
Write-Host '  Stop it later with:   .\stop.ps1'
Write-Host ''

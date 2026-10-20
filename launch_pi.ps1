# Space Blaster — pi launcher (Windows)
#
# Windows counterpart of launch_pi.sh. Opens pi in this folder on the local
# Lemonade model, installing pi first if it is missing. booth_server.py runs
# this in a fresh console window after every reset; serve.ps1 runs it with
# -InstallOnly so the installs happen up front.
#
# Usage:
#   .\launch_pi.ps1 [-Model MODEL]                install pi if needed, then launch it
#   .\launch_pi.ps1 -InstallOnly [-Model MODEL]   install pi and the model, then exit
#
# MODEL defaults to $env:BOOTH_MODEL, else Qwen3.6-35B-A3B-ThinkingCoder.
# Passing -m is the deterministic equivalent of picking the recipe from the
# "lemonade launch pi" menu.

param(
  [switch]$InstallOnly,
  [string]$Model
)

# Not 'Stop': Windows PowerShell 5.1 turns a native command's stderr into a
# terminating error under it. Failures are checked via $LASTEXITCODE instead.
$ErrorActionPreference = 'Continue'

# Always operate from the directory this script lives in (the repo root), so pi
# discovers .pi/ (agents, commands, sub-agent extension).
Set-Location $PSScriptRoot

if (-not $Model) {
  $Model = if ($env:BOOTH_MODEL) { $env:BOOTH_MODEL } else { 'Qwen3.6-35B-A3B-ThinkingCoder' }
}

# The pi installer puts its launcher in ~\.pi\agent\bin; a console opened
# before the install does not see the updated user PATH yet.
$env:PATH = (Join-Path $HOME '.pi\agent\bin') + ';' + $env:PATH

if (-not (Get-Command pi -ErrorAction SilentlyContinue)) {
  Write-Host '[booth] pi is not installed - running the pi installer (https://pi.dev/install.ps1)'
  # Run the installer in its own PowerShell: it calls `exit`, which would end
  # this script too if it were invoked in-process. It brings its own Node.js
  # when the system one is older than 22.19, and offers Git for Windows, which
  # pi needs for its bash tool.
  $installer = Join-Path $env:TEMP 'pi-install.ps1'
  Invoke-WebRequest -UseBasicParsing https://pi.dev/install.ps1 -OutFile $installer
  $ps = (Get-Process -Id $PID).Path
  & $ps -NoProfile -ExecutionPolicy Bypass -File $installer
  if (-not (Get-Command pi -ErrorAction SilentlyContinue)) {
    [Console]::Error.WriteLine('[booth] pi is still not on PATH after the install - see https://pi.dev')
    exit 1
  }
}

if ($InstallOnly) {
  # The default model is a recipe from Lemonade's coding-agents collection, not
  # a built-in model, so a fresh machine does not know it yet. Importing it
  # also downloads it (~20 GB); a built-in model only needs the download.
  $downloaded = (& lemonade list --downloaded 2>$null) -join "`n"
  # Long names run straight into the "Yes" column, hence the alternative.
  if ($downloaded -notmatch ('(?m)^' + [regex]::Escape($Model) + '(\s|Yes\b)')) {
    Write-Host "[booth] adding $Model to Lemonade (one-time download)"
    & lemonade import --directory coding-agents --recipe-file "$Model.json" --yes
    if ($LASTEXITCODE -ne 0) { & lemonade pull $Model }
  }
  Write-Host "[booth] pi $(& pi --version) ready: $((Get-Command pi).Source)"
  Write-Host "[booth] model ready: $Model"
  exit 0
}

# --approve trusts this folder's .pi/ for the run, so a fresh session never
# stops at pi's project-trust prompt. lemonade passes it through after its own
# --provider/--model flags. The = form keeps lemonade from parsing it.
& lemonade launch pi -m $Model --agent-args=--approve
exit $LASTEXITCODE

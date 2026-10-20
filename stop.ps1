# Space Blaster — stop the booth server (Windows)
#
# Windows counterpart of `pkill -f booth_server.py`. Also stops any GPU monitor
# it left behind; pi sessions and the Lemonade server are left running.

param([switch]$Quiet)

$stopped = Get-CimInstance Win32_Process |
  Where-Object { $_.ProcessId -ne $PID -and $_.CommandLine -match 'booth_server\.py|gpu_monitor\.ps1' }
$stopped | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }

if (-not $Quiet) {
  Write-Host "  Stopped $(@($stopped).Count) booth process(es)."
}

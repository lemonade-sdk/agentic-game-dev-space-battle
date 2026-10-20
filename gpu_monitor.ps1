# Space Blaster — Windows GPU monitor
#
# Windows stand-in for `amd-smi monitor`: prints one CSV sample per second, in
# the same shape booth_server.py parses from amd-smi (a header line starting
# with "timestamp", then rows), built from the Windows GPU performance counters.
#
# On the Strix Halo APU the model mostly lives in shared (system) memory, not
# the small dedicated carve-out, so "vram" here is dedicated + shared usage of
# the Radeon adapter, against dedicated size + the shared budget (half of RAM).
#
# -ParentPid: exit once that process (the booth server) is gone, so a server
# killed without cleanup (taskkill /F, Stop-Process) never leaves this looping.

param([int]$ParentPid = 0)

$ErrorActionPreference = 'SilentlyContinue'

# Dedicated memory of the AMD adapter, from the display-class registry keys.
$displayClass = 'HKLM:\SYSTEM\CurrentControlSet\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}\0*'
$adapters = Get-ItemProperty $displayClass | Where-Object { $_.DriverDesc }
$amd = $adapters | Where-Object { $_.DriverDesc -match 'AMD|Radeon' } | Select-Object -First 1
if (-not $amd) { $amd = $adapters | Select-Object -First 1 }
$dedicatedBytes = [double]($amd.'HardwareInformation.qwMemorySize')
$sharedBytes = [double](Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 2
$totalMB = [math]::Round(($dedicatedBytes + $sharedBytes) / 1MB)

$counters = @(
  '\GPU Adapter Memory(*)\Dedicated Usage',
  '\GPU Adapter Memory(*)\Shared Usage',
  '\GPU Engine(*)\Utilization Percentage'
)

[Console]::Out.WriteLine('timestamp,vram_used,vram_total,vram_percent,gpu_util')
while ($true) {
  if ($ParentPid -and -not (Get-Process -Id $ParentPid)) { exit }
  # Get-Counter re-expands the wildcards on every call, so engines of a newly
  # started llama-server show up; the 1s sample interval paces the loop.
  $samples = (Get-Counter -Counter $counters -SampleInterval 1 -MaxSamples 1).CounterSamples
  if (-not $samples) { Start-Sleep -Seconds 1; continue }

  # Per-adapter memory, keyed by LUID ("luid_0x..._0x...").
  $mem = @{}
  foreach ($s in $samples | Where-Object { $_.Path -match 'gpu adapter memory' }) {
    $luid = ($s.InstanceName -replace '_phys_\d+$', '').ToLower()
    if (-not $mem[$luid]) { $mem[$luid] = @{ dedicated = 0.0; shared = 0.0 } }
    if ($s.Path -match 'dedicated usage$') { $mem[$luid].dedicated += $s.CookedValue }
    else { $mem[$luid].shared += $s.CookedValue }
  }
  # The Radeon is the adapter actually using dedicated memory (the NPU and the
  # Basic Render Driver have none).
  $gpu = $mem.Keys | Sort-Object { $mem[$_].dedicated } -Descending | Select-Object -First 1
  if (-not $gpu) { continue }
  $usedMB = [math]::Round(($mem[$gpu].dedicated + $mem[$gpu].shared) / 1MB)

  # Utilization like Task Manager: sum each engine type over processes, take the busiest.
  $byType = @{}
  foreach ($s in $samples | Where-Object { $_.InstanceName -match "$gpu.*engtype_(.+)$" }) {
    $byType[$Matches[1]] += $s.CookedValue
  }
  $util = 0
  if ($byType.Count) { $util = [math]::Min(100, [math]::Round(($byType.Values | Measure-Object -Maximum).Maximum)) }

  $pct = if ($totalMB) { [math]::Round(100 * $usedMB / $totalMB) } else { 'N/A' }
  $ts = [DateTimeOffset]::Now.ToUnixTimeSeconds()
  # A write to a closed pipe (reader gone) throws: stop then too.
  try { [Console]::Out.WriteLine("$ts,$usedMB,$totalMB,$pct,$util") } catch { exit }
}

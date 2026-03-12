$ErrorActionPreference = 'Continue'

$repoRoot = Split-Path -Parent $PSScriptRoot
$pidFile = Join-Path $repoRoot 'logs\dev-processes.json'

if (-not (Test-Path $pidFile)) {
    Write-Host "PID file not found: $pidFile"
    Write-Host 'Nothing to stop from saved state.'
    exit 0
}

try {
    $state = Get-Content -Raw -Path $pidFile | ConvertFrom-Json
} catch {
    Write-Host "Failed to parse PID file: $pidFile" -ForegroundColor Yellow
    exit 1
}

$targetPids = @()
if ($state.djangoPid) { $targetPids += [int]$state.djangoPid }
if ($state.cloudflaredPid) { $targetPids += [int]$state.cloudflaredPid }

foreach ($procId in $targetPids) {
    $proc = Get-Process -Id $procId -ErrorAction SilentlyContinue
    if ($proc) {
        Stop-Process -Id $procId -Force
        Write-Host "Stopped PID $procId ($($proc.ProcessName))"
    } else {
        Write-Host "PID $procId is not running"
    }
}

Remove-Item -Path $pidFile -Force -ErrorAction SilentlyContinue
Write-Host 'Done.'

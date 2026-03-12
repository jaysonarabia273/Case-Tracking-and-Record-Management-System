$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent $PSScriptRoot
$djangoDir = Join-Path $repoRoot 'Capstone'
$pythonExe = Join-Path $repoRoot 'venv\Scripts\python.exe'
$cloudflaredExe = Join-Path $PSScriptRoot 'cloudflared.exe'
$qrUrlFile = Join-Path $PSScriptRoot 'qr-url.txt'
$logsDir = Join-Path $repoRoot 'logs'
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$runserverLog = Join-Path $logsDir ("runserver-$stamp.log")
$runserverErrLog = Join-Path $logsDir ("runserver-$stamp.err.log")
$cloudflaredLog = Join-Path $logsDir ("cloudflared-$stamp.log")
$pidFile = Join-Path $logsDir 'dev-processes.json'

if (-not (Test-Path $pythonExe)) {
    throw "Python executable not found: $pythonExe"
}
if (-not (Test-Path $cloudflaredExe)) {
    throw "cloudflared executable not found: $cloudflaredExe"
}
if (-not (Test-Path (Join-Path $djangoDir 'manage.py'))) {
    throw "manage.py not found in: $djangoDir"
}

New-Item -ItemType Directory -Path $logsDir -Force | Out-Null

Write-Host 'Starting Django dev server on http://127.0.0.1:8000 ...'
$djangoProcess = Start-Process -FilePath $pythonExe `
    -ArgumentList @('manage.py', 'runserver', '0.0.0.0:8000') `
    -WorkingDirectory $djangoDir `
    -RedirectStandardOutput $runserverLog `
    -RedirectStandardError $runserverErrLog `
    -PassThru

Start-Sleep -Seconds 2
if ($djangoProcess.HasExited) {
    Write-Host 'Django server exited immediately. Recent log output:' -ForegroundColor Red
    if (Test-Path $runserverLog) {
        Get-Content $runserverLog -Tail 60
    }
    throw 'Django server failed to start.'
}

Write-Host 'Starting Cloudflare tunnel...'
$cloudflaredProcess = Start-Process -FilePath $cloudflaredExe `
    -ArgumentList @('tunnel', '--url', 'http://127.0.0.1:8000', '--loglevel', 'info', '--logfile', $cloudflaredLog) `
    -WorkingDirectory $repoRoot `
    -PassThru

$state = [ordered]@{
    djangoPid = $djangoProcess.Id
    cloudflaredPid = $cloudflaredProcess.Id
    startedAt = (Get-Date).ToString('o')
    runserverLog = $runserverLog
    runserverErrLog = $runserverErrLog
    cloudflaredLog = $cloudflaredLog
}
$state | ConvertTo-Json | Set-Content -Path $pidFile -Encoding UTF8

$publicUrl = $null
for ($i = 0; $i -lt 30; $i++) {
    Start-Sleep -Seconds 1

    if ($cloudflaredProcess.HasExited) {
        Write-Host 'Cloudflared exited early. Recent log output:' -ForegroundColor Yellow
        if (Test-Path $cloudflaredLog) {
            Get-Content $cloudflaredLog -Tail 80
        }
        break
    }

    if (Test-Path $cloudflaredLog) {
        $match = Select-String -Path $cloudflaredLog -Pattern 'https://[-a-z0-9]+\.trycloudflare\.com' -AllMatches |
            ForEach-Object { $_.Matches } |
            Select-Object -Last 1

        if ($match) {
            $publicUrl = $match.Value
            break
        }
    }
}

if ($publicUrl) {
    Write-Host "Generating QR code for public URL..."
    & $pythonExe (Join-Path $PSScriptRoot 'make_qr.py') $publicUrl | Out-Null
}

Write-Host ''
Write-Host "Django PID: $($djangoProcess.Id)"
Write-Host "Cloudflared PID: $($cloudflaredProcess.Id)"
Write-Host "Local URL: http://127.0.0.1:8000"
if ($publicUrl) {
    Write-Host "Public URL (QR): $publicUrl" -ForegroundColor Green
} else {
    Write-Host "Public URL not detected. Check log: $cloudflaredLog" -ForegroundColor Yellow
}
Write-Host "Stop both with: powershell -ExecutionPolicy Bypass -File $PSScriptRoot\stop-dev-with-cloudflare.ps1"

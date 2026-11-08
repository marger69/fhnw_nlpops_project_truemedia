param(
    # Maximale Wartezeit auf die Docker Engine in Sekunden.
    [ValidateRange(1, 600)]
    [int]$StartupTimeoutSeconds = 180
)

$ErrorActionPreference = 'Stop'

# Compose-Datei relativ zum Skript suchen, unabhängig vom aktuellen Verzeichnis.
$projectRoot = Split-Path -Parent $PSScriptRoot
$composeFile = Join-Path $projectRoot 'docker-compose.yml'
if (-not (Test-Path $composeFile)) {
    throw "Docker Compose-Konfiguration nicht gefunden: $composeFile"
}

# Docker CLI prüfen, bevor Docker Desktop oder der Stack gestartet wird.
$dockerCommand = Get-Command docker.exe -CommandType Application -ErrorAction SilentlyContinue
if (-not $dockerCommand) {
    throw 'Docker CLI nicht gefunden. Installiere Docker Desktop und stelle sicher, dass docker.exe im PATH liegt.'
}
$dockerPath = $dockerCommand.Source

# Docker Desktop bei Bedarf über einen der üblichen Installationspfade starten.
$desktopProcess = Get-Process -Name 'Docker Desktop' -ErrorAction SilentlyContinue
if (-not $desktopProcess) {
    $desktopPaths = @(
        (Join-Path $env:ProgramFiles 'Docker\Docker\Docker Desktop.exe')
        (Join-Path $env:LOCALAPPDATA 'Programs\Docker\Docker\Docker Desktop.exe')
    )
    $desktopPath = $desktopPaths | Where-Object { Test-Path $_ } | Select-Object -First 1
    if (-not $desktopPath) {
        throw 'Docker Desktop läuft nicht und die Anwendung wurde nicht gefunden. Installiere Docker Desktop oder starte es manuell.'
    }

    Write-Host 'Docker Desktop wird gestartet...'
    Start-Process -FilePath $desktopPath
}

Write-Host "Warte auf die Docker Engine (maximal $StartupTimeoutSeconds Sekunden)..."
# Die Engine kann auch nach dem Start von Docker Desktop noch nicht bereit sein.
$deadline = (Get-Date).AddSeconds($StartupTimeoutSeconds)
$engineReady = $false
while ((Get-Date) -lt $deadline) {
    $null = & $dockerPath info --format '{{.ServerVersion}}' 2>$null
    if ($LASTEXITCODE -eq 0) {
        $engineReady = $true
        break
    }
    Start-Sleep -Seconds 2
}

if (-not $engineReady) {
    throw "Docker Engine wurde innerhalb von $StartupTimeoutSeconds Sekunden nicht bereit. Prüfe Docker Desktop und dessen Linux-Engine."
}

Write-Host 'Docker Engine ist bereit. Starte Docker Compose...'
# Compose im Projektverzeichnis ausführen und das ursprüngliche Verzeichnis wiederherstellen.
Push-Location $projectRoot
try {
    & $dockerPath compose up --build
    if ($LASTEXITCODE -ne 0) {
        throw "docker compose up --build ist mit Exitcode $LASTEXITCODE fehlgeschlagen."
    }
}
finally {
    Pop-Location
}

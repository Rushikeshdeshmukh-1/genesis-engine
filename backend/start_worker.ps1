# Start Temporal Worker for Project RDx 00

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting Temporal Worker" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
$venvPath = Join-Path $PSScriptRoot "venv"
if (-not (Test-Path $venvPath)) {
    Write-Host "Virtual environment not found. Creating..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "  ✓ Virtual environment created" -ForegroundColor Green
    Write-Host ""
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
$activateScript = Join-Path $venvPath "Scripts\Activate.ps1"

if (Test-Path $activateScript) {
    & $activateScript
    Write-Host "  ✓ Virtual environment activated" -ForegroundColor Green
}
else {
    Write-Host "  ✗ Could not find activation script" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Check if Temporal is running
Write-Host "Checking Temporal server..." -ForegroundColor Yellow
$connection = New-Object System.Net.Sockets.TcpClient
try {
    $connection.Connect("localhost", 7233)
    $connection.Close()
    Write-Host "  ✓ Temporal server is running" -ForegroundColor Green
}
catch {
    Write-Host "  ✗ Temporal server is not running on port 7233" -ForegroundColor Red
    Write-Host "  Please start Temporal server first: temporal server start-dev" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# Start the worker
Write-Host "Starting Temporal worker..." -ForegroundColor Yellow
Write-Host "  Task Queue: idea-engine-tasks" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the worker" -ForegroundColor Gray
Write-Host ""

# Run worker
python -m app.workflows.worker

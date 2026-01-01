# Start FastAPI Backend for Project RDx 00

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting Backend API Server" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
$venvPath = Join-Path $PSScriptRoot "venv"
if (-not (Test-Path $venvPath)) {
    Write-Host "Virtual environment not found. Creating..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "  [OK] Virtual environment created" -ForegroundColor Green
    Write-Host ""
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
$activateScript = Join-Path $venvPath "Scripts\Activate.ps1"

if (Test-Path $activateScript) {
    & $activateScript
    Write-Host "  [OK] Virtual environment activated" -ForegroundColor Green
}
else {
    Write-Host "  [FAIL] Could not find activation script" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Check if dependencies are installed
Write-Host "Checking dependencies..." -ForegroundColor Yellow
$requirementsPath = Join-Path $PSScriptRoot "requirements.txt"

if (Test-Path $requirementsPath) {
    Write-Host "  Installing/updating dependencies..." -ForegroundColor White
    pip install -r $requirementsPath
    Write-Host "  [OK] Dependencies installed" -ForegroundColor Green
}
else {
    Write-Host "  [WARN] requirements.txt not found" -ForegroundColor Yellow
}

Write-Host ""

# Check if .env file exists
$envPath = Join-Path (Split-Path $PSScriptRoot -Parent) ".env"
if (-not (Test-Path $envPath)) {
    Write-Host "[WARN] .env file not found!" -ForegroundColor Yellow
    Write-Host "  Please copy .env.example to .env and configure it" -ForegroundColor White
    $continue = Read-Host "Continue anyway? (Y/N)"
    if ($continue -ne "Y" -and $continue -ne "y") {
        exit 1
    }
}

Write-Host ""

# Start the backend server
Write-Host "Starting FastAPI server..." -ForegroundColor Yellow
Write-Host "  URL: http://localhost:8000" -ForegroundColor Cyan
Write-Host "  Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Gray
Write-Host ""

# Run uvicorn
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

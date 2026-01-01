# Start Next.js Frontend for Project RDx 00

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting Frontend Development Server" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if node_modules exists
if (-not (Test-Path "node_modules")) {
    Write-Host "node_modules not found. Installing dependencies..." -ForegroundColor Yellow
    npm install
    Write-Host "  [OK] Dependencies installed" -ForegroundColor Green
    Write-Host ""
}

# Check if backend is running
Write-Host "Checking backend server..." -ForegroundColor Yellow
$connection = New-Object System.Net.Sockets.TcpClient
try {
    $connection.Connect("localhost", 8000)
    $connection.Close()
    Write-Host "  [OK] Backend server is running" -ForegroundColor Green
}
catch {
    Write-Host "  [WARN] Backend server is not running on port 8000" -ForegroundColor Yellow
    Write-Host "  Please start the backend first: cd backend; .\start_backend.ps1" -ForegroundColor White
    $continue = Read-Host "Continue anyway? (Y/N)"
    if ($continue -ne "Y" -and $continue -ne "y") {
        exit 1
    }
}

Write-Host ""

# Start the development server
Write-Host "Starting Next.js development server..." -ForegroundColor Yellow
Write-Host "  URL: http://localhost:3000" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Gray
Write-Host ""

# Run Next.js dev server
npm run dev

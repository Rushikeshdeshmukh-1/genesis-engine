# Stop all Project RDx 00 services

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Stopping Project RDx 00 Services" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Function to stop a Windows service
function Stop-WindowsService {
    param([string]$ServiceName)
    
    if (Get-Service -Name $ServiceName -ErrorAction SilentlyContinue) {
        Write-Host "Stopping $ServiceName..." -ForegroundColor Yellow
        Stop-Service -Name $ServiceName -Force
        Write-Host "  ✓ $ServiceName stopped" -ForegroundColor Green
    }
}

# Function to kill processes on a specific port
function Stop-ProcessOnPort {
    param(
        [int]$Port,
        [string]$ServiceName
    )
    
    Write-Host "Checking for processes on port $Port ($ServiceName)..." -ForegroundColor Yellow
    
    $connections = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
    
    if ($connections) {
        foreach ($conn in $connections) {
            $process = Get-Process -Id $conn.OwningProcess -ErrorAction SilentlyContinue
            if ($process) {
                Write-Host "  Stopping process: $($process.ProcessName) (PID: $($process.Id))" -ForegroundColor White
                Stop-Process -Id $process.Id -Force
                Write-Host "  ✓ Process stopped" -ForegroundColor Green
            }
        }
    }
    else {
        Write-Host "  No processes found on port $Port" -ForegroundColor Gray
    }
}

# Stop services
Write-Host "Stopping Windows services..." -ForegroundColor Cyan
Write-Host ""

Stop-WindowsService "postgresql*"
Stop-WindowsService "Redis"
Stop-WindowsService "RabbitMQ"

Write-Host ""
Write-Host "Stopping processes..." -ForegroundColor Cyan
Write-Host ""

Stop-ProcessOnPort -Port 9000 -ServiceName "MinIO"
Stop-ProcessOnPort -Port 7233 -ServiceName "Temporal"
Stop-ProcessOnPort -Port 11434 -ServiceName "Ollama"
Stop-ProcessOnPort -Port 8000 -ServiceName "Backend API"
Stop-ProcessOnPort -Port 3000 -ServiceName "Frontend"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "All services stopped!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

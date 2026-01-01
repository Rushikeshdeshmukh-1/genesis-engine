# Start all required services for Project RDx 00
# Run this script to start all services in the correct order

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting Project RDx 00 Services" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Function to check if a port is in use
function Test-Port {
    param([int]$Port)
    $connection = New-Object System.Net.Sockets.TcpClient
    try {
        $connection.Connect("localhost", $Port)
        $connection.Close()
        return $true
    }
    catch {
        return $false
    }
}

# Function to start a service and check if it's running
function Start-ServiceIfNotRunning {
    param(
        [string]$ServiceName,
        [int]$Port,
        [string]$Command,
        [string]$WorkingDirectory = $null
    )
    
    Write-Host "Checking $ServiceName..." -ForegroundColor Yellow
    
    if (Test-Port -Port $Port) {
        Write-Host "  [OK] $ServiceName is already running on port $Port" -ForegroundColor Green
        return $true
    }
    
    Write-Host "  Starting $ServiceName..." -ForegroundColor White
    
    try {
        if ($WorkingDirectory) {
            Start-Process -FilePath "powershell" -ArgumentList "-NoExit", "-Command", "cd '$WorkingDirectory'; $Command" -WindowStyle Normal
        }
        else {
            Start-Process -FilePath "powershell" -ArgumentList "-NoExit", "-Command", $Command -WindowStyle Normal
        }
        
        # Wait for service to start
        $maxWait = 30
        $waited = 0
        while (-not (Test-Port -Port $Port) -and $waited -lt $maxWait) {
            Start-Sleep -Seconds 1
            $waited++
            Write-Host "  Waiting for $ServiceName to start... ($waited/$maxWait)" -ForegroundColor Gray
        }
        
        if (Test-Port -Port $Port) {
            Write-Host "  [OK] $ServiceName started successfully!" -ForegroundColor Green
            return $true
        }
        else {
            Write-Host "  [FAIL] $ServiceName failed to start within $maxWait seconds" -ForegroundColor Red
            return $false
        }
    }
    catch {
        Write-Host "  [FAIL] Error starting $ServiceName : $_" -ForegroundColor Red
        return $false
    }
}

# Start services in order
Write-Host "Starting infrastructure services..." -ForegroundColor Cyan
Write-Host ""

# 1. PostgreSQL
if (Get-Service -Name "postgresql*" -ErrorAction SilentlyContinue) {
    Write-Host "Starting PostgreSQL service..." -ForegroundColor Yellow
    Start-Service -Name "postgresql*"
    Start-Sleep -Seconds 3
    if (Test-Port -Port 5432) {
        Write-Host "  [OK] PostgreSQL is running on port 5432" -ForegroundColor Green
    }
    else {
        Write-Host "  [FAIL] PostgreSQL failed to start" -ForegroundColor Red
    }
}
else {
    Write-Host "  [WARN] PostgreSQL service not found. Please start it manually." -ForegroundColor Yellow
}

Write-Host ""

# 2. Redis
if (Get-Service -Name "Redis" -ErrorAction SilentlyContinue) {
    Write-Host "Starting Redis service..." -ForegroundColor Yellow
    Start-Service -Name "Redis"
    Start-Sleep -Seconds 2
    if (Test-Port -Port 6379) {
        Write-Host "  [OK] Redis is running on port 6379" -ForegroundColor Green
    }
    else {
        Write-Host "  [FAIL] Redis failed to start" -ForegroundColor Red
    }
}
else {
    Write-Host "Checking Redis..." -ForegroundColor Yellow
    if (Test-Port -Port 6379) {
        Write-Host "  [OK] Redis is already running on port 6379" -ForegroundColor Green
    }
    else {
        Write-Host "  [WARN] Redis not running. Starting manually..." -ForegroundColor Yellow
        if (Test-Path "C:\Redis\redis-server.exe") {
            Start-Process -FilePath "C:\Redis\redis-server.exe" -WindowStyle Normal
            Start-Sleep -Seconds 3
        }
        else {
            Write-Host "  [FAIL] Redis not found. Please start it manually." -ForegroundColor Red
        }
    }
}

Write-Host ""

# 3. RabbitMQ
if (Get-Service -Name "RabbitMQ" -ErrorAction SilentlyContinue) {
    Write-Host "Starting RabbitMQ service..." -ForegroundColor Yellow
    Start-Service -Name "RabbitMQ"
    Start-Sleep -Seconds 5
    if (Test-Port -Port 5672) {
        Write-Host "  [OK] RabbitMQ is running on port 5672" -ForegroundColor Green
    }
    else {
        Write-Host "  [FAIL] RabbitMQ failed to start" -ForegroundColor Red
    }
}
else {
    Write-Host "  [WARN] RabbitMQ service not found. Please start it manually." -ForegroundColor Yellow
}

Write-Host ""

# 4. MinIO
Write-Host "Checking MinIO..." -ForegroundColor Yellow
if (Test-Port -Port 9000) {
    Write-Host "  [OK] MinIO is already running on port 9000" -ForegroundColor Green
}
else {
    Write-Host "  Starting MinIO..." -ForegroundColor White
    if (Test-Path "C:\minio\minio.exe") {
        Start-Process -FilePath "powershell" -ArgumentList "-NoExit", "-Command", "cd C:\minio; .\minio.exe server C:\minio\data --console-address :9001" -WindowStyle Normal
        Start-Sleep -Seconds 5
        if (Test-Port -Port 9000) {
            Write-Host "  [OK] MinIO started successfully!" -ForegroundColor Green
        }
        else {
            Write-Host "  [FAIL] MinIO failed to start" -ForegroundColor Red
        }
    }
    else {
        Write-Host "  [FAIL] MinIO not found at C:\minio\minio.exe. Please start it manually." -ForegroundColor Red
    }
}

Write-Host ""

# 5. Temporal
Write-Host "Checking Temporal..." -ForegroundColor Yellow
if (Test-Port -Port 7233) {
    Write-Host "  [OK] Temporal is already running on port 7233" -ForegroundColor Green
}
else {
    Write-Host "  Starting Temporal development server..." -ForegroundColor White
    Start-Process -FilePath "powershell" -ArgumentList "-NoExit", "-Command", "temporal server start-dev" -WindowStyle Normal
    Start-Sleep -Seconds 10
    if (Test-Port -Port 7233) {
        Write-Host "  [OK] Temporal started successfully!" -ForegroundColor Green
    }
    else {
        Write-Host "  [FAIL] Temporal failed to start" -ForegroundColor Red
    }
}

Write-Host ""

# 6. Ollama
Write-Host "Checking Ollama..." -ForegroundColor Yellow
if (Test-Port -Port 11434) {
    Write-Host "  [OK] Ollama is already running on port 11434" -ForegroundColor Green
}
else {
    Write-Host "  Starting Ollama..." -ForegroundColor White
    Start-Process -FilePath "ollama" -ArgumentList "serve" -WindowStyle Normal
    Start-Sleep -Seconds 5
    if (Test-Port -Port 11434) {
        Write-Host "  [OK] Ollama started successfully!" -ForegroundColor Green
    }
    else {
        Write-Host "  [FAIL] Ollama failed to start" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Service Startup Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$services = @(
    @{Name = "PostgreSQL"; Port = 5432 },
    @{Name = "Redis"; Port = 6379 },
    @{Name = "RabbitMQ"; Port = 5672 },
    @{Name = "MinIO"; Port = 9000 },
    @{Name = "Temporal"; Port = 7233 },
    @{Name = "Ollama"; Port = 11434 }
)

foreach ($service in $services) {
    $status = if (Test-Port -Port $service.Port) { "[OK] Running" } else { "[FAIL] Not Running" }
    $color = if (Test-Port -Port $service.Port) { "Green" } else { "Red" }
    Write-Host "$($service.Name) (Port $($service.Port)): $status" -ForegroundColor $color
}

Write-Host ""
Write-Host "Access URLs:" -ForegroundColor Yellow
Write-Host "  - MinIO Console: http://localhost:9001" -ForegroundColor White
Write-Host "  - RabbitMQ Management: http://localhost:15672" -ForegroundColor White
Write-Host "  - Temporal Web UI: http://localhost:8080" -ForegroundColor White
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Start backend: cd backend; .\start_backend.ps1" -ForegroundColor White
Write-Host "  2. Start frontend: cd frontend; .\start_frontend.ps1" -ForegroundColor White
Write-Host ""

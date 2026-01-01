# Local Development Setup Script for Project RDx 00
# This script guides you through installing all required services locally on Windows

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Project RDx 00 - Local Setup Guide" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$services = @(
    @{
        Name = "PostgreSQL 16 with pgvector"
        Port = "5432"
        Download = "https://www.postgresql.org/download/windows/"
        Instructions = @"
1. Download PostgreSQL 16 installer from the link above
2. Run the installer and follow the wizard
3. Set password for postgres user (use: postgres_password)
4. Default port: 5432
5. After installation, install pgvector extension:
   - Download from: https://github.com/pgvector/pgvector/releases
   - Or use: winget install pgvector.pgvector
"@
    },
    @{
        Name = "Redis"
        Port = "6379"
        Download = "https://github.com/microsoftarchive/redis/releases"
        Instructions = @"
1. Download Redis for Windows from the link above
2. Extract to C:\Redis
3. Run redis-server.exe
4. Or install as Windows service:
   redis-server --service-install
   redis-server --service-start
"@
    },
    @{
        Name = "RabbitMQ"
        Port = "5672, 15672"
        Download = "https://www.rabbitmq.com/download.html"
        Instructions = @"
1. First install Erlang: https://www.erlang.org/downloads
2. Then install RabbitMQ from the link above
3. Enable management plugin:
   rabbitmq-plugins enable rabbitmq_management
4. Create user:
   rabbitmqctl add_user rabbitmq rabbitmq_password
   rabbitmqctl set_user_tags rabbitmq administrator
   rabbitmqctl set_permissions -p / rabbitmq ".*" ".*" ".*"
"@
    },
    @{
        Name = "MinIO"
        Port = "9000, 9001"
        Download = "https://min.io/download"
        Instructions = @"
1. Download MinIO for Windows from the link above
2. Create directory: mkdir C:\minio\data
3. Run MinIO server:
   minio.exe server C:\minio\data --console-address :9001
4. Default credentials: minioadmin / minioadmin
5. Access console at: http://localhost:9001
"@
    },
    @{
        Name = "Temporal"
        Port = "7233, 8080"
        Download = "https://docs.temporal.io/cli#install"
        Instructions = @"
1. Install Temporal CLI:
   winget install Temporal.CLI
2. Start Temporal development server:
   temporal server start-dev
3. This will start both Temporal server (7233) and Web UI (8080)
"@
    },
    @{
        Name = "Ollama"
        Port = "11434"
        Download = "https://ollama.ai/download"
        Instructions = @"
1. Download Ollama for Windows from the link above
2. Run the installer
3. Ollama will start automatically as a service
4. Pull the required model:
   ollama pull llama3.1:8b
5. This may take some time (model is ~4.7GB)
"@
    }
)

Write-Host "This script will guide you through installing the following services:" -ForegroundColor Yellow
Write-Host ""
foreach ($service in $services) {
    Write-Host "  - $($service.Name) (Port: $($service.Port))" -ForegroundColor White
}
Write-Host ""

$continue = Read-Host "Do you want to continue? (Y/N)"
if ($continue -ne "Y" -and $continue -ne "y") {
    Write-Host "Setup cancelled." -ForegroundColor Red
    exit
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Installation Instructions" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

foreach ($service in $services) {
    Write-Host "----------------------------------------" -ForegroundColor Yellow
    Write-Host "Service: $($service.Name)" -ForegroundColor Green
    Write-Host "Port(s): $($service.Port)" -ForegroundColor White
    Write-Host "Download: $($service.Download)" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Instructions:" -ForegroundColor Yellow
    Write-Host $service.Instructions -ForegroundColor White
    Write-Host ""
    
    $installed = Read-Host "Have you installed $($service.Name)? (Y/N/Skip)"
    if ($installed -eq "Skip" -or $installed -eq "S" -or $installed -eq "s") {
        Write-Host "Skipping $($service.Name)..." -ForegroundColor Yellow
        continue
    }
    
    while ($installed -ne "Y" -and $installed -ne "y") {
        Write-Host "Please install $($service.Name) before continuing." -ForegroundColor Red
        Write-Host "Opening download page..." -ForegroundColor Yellow
        Start-Process $service.Download
        $installed = Read-Host "Have you installed $($service.Name)? (Y/N)"
    }
    
    Write-Host "$($service.Name) marked as installed!" -ForegroundColor Green
    Write-Host ""
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Service Installation Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Run .\init_database.ps1 to initialize PostgreSQL database" -ForegroundColor White
Write-Host "2. Copy .env.example to .env and verify settings" -ForegroundColor White
Write-Host "3. Run .\start_services.ps1 to start all services" -ForegroundColor White
Write-Host "4. Install Python dependencies: cd backend; pip install -r requirements.txt" -ForegroundColor White
Write-Host "5. Install Node.js dependencies: cd frontend; npm install" -ForegroundColor White
Write-Host "6. Start the backend: cd backend; .\start_backend.ps1" -ForegroundColor White
Write-Host "7. Start the frontend: cd frontend; .\start_frontend.ps1" -ForegroundColor White
Write-Host ""

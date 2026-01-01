# Install Missing Services for Project RDx 00
# This script provides instructions and automated installation for Temporal, MinIO, and RabbitMQ

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Service Installation Guide" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Function to check if running as administrator
function Test-Administrator {
    $currentUser = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
    return $currentUser.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

if (-not (Test-Administrator)) {
    Write-Host "⚠ WARNING: This script should be run as Administrator for best results" -ForegroundColor Yellow
    Write-Host ""
}

# 1. TEMPORAL INSTALLATION
Write-Host "1. TEMPORAL CLI INSTALLATION" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Gray
Write-Host ""

$temporalInstalled = Get-Command temporal -ErrorAction SilentlyContinue
if ($temporalInstalled) {
    Write-Host "✓ Temporal CLI is already installed" -ForegroundColor Green
    temporal version
}
else {
    Write-Host "Installing Temporal CLI..." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Method 1: Using Scoop (Recommended)" -ForegroundColor Cyan
    Write-Host "  scoop install temporal" -ForegroundColor White
    Write-Host ""
    Write-Host "Method 2: Manual Download" -ForegroundColor Cyan
    Write-Host "  1. Visit: https://github.com/temporalio/cli/releases" -ForegroundColor White
    Write-Host "  2. Download: temporal_cli_*_windows_amd64.zip" -ForegroundColor White
    Write-Host "  3. Extract to C:\temporal\" -ForegroundColor White
    Write-Host "  4. Add C:\temporal to PATH" -ForegroundColor White
    Write-Host ""
    
    $install = Read-Host "Install Temporal using Scoop now? (Y/N)"
    if ($install -eq "Y" -or $install -eq "y") {
        # Check if scoop is installed
        $scoopInstalled = Get-Command scoop -ErrorAction SilentlyContinue
        if ($scoopInstalled) {
            scoop install temporal
            Write-Host "✓ Temporal CLI installed" -ForegroundColor Green
        }
        else {
            Write-Host "Scoop is not installed. Installing Scoop first..." -ForegroundColor Yellow
            Set-ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
            Invoke-RestMethod get.scoop.sh | Invoke-Expression
            scoop install temporal
            Write-Host "✓ Temporal CLI installed" -ForegroundColor Green
        }
    }
}

Write-Host ""

# 2. MINIO INSTALLATION
Write-Host "2. MINIO INSTALLATION" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Gray
Write-Host ""

$minioPath = "C:\minio\minio.exe"
if (Test-Path $minioPath) {
    Write-Host "✓ MinIO is already installed at $minioPath" -ForegroundColor Green
}
else {
    Write-Host "Installing MinIO..." -ForegroundColor Yellow
    Write-Host ""
    
    # Create MinIO directory
    New-Item -ItemType Directory -Force -Path "C:\minio" | Out-Null
    New-Item -ItemType Directory -Force -Path "C:\minio\data" | Out-Null
    
    Write-Host "Downloading MinIO..." -ForegroundColor Cyan
    $minioUrl = "https://dl.min.io/server/minio/release/windows-amd64/minio.exe"
    
    try {
        Invoke-WebRequest -Uri $minioUrl -OutFile $minioPath
        Write-Host "✓ MinIO downloaded successfully" -ForegroundColor Green
        
        # Create MinIO start script
        $minioStartScript = @"
@echo off
cd C:\minio
minio.exe server C:\minio\data --console-address :9001
"@
        $minioStartScript | Out-File -FilePath "C:\minio\start-minio.bat" -Encoding ASCII
        Write-Host "✓ MinIO start script created at C:\minio\start-minio.bat" -ForegroundColor Green
        
    }
    catch {
        Write-Host "✗ Failed to download MinIO: $_" -ForegroundColor Red
        Write-Host "Please download manually from: https://min.io/download" -ForegroundColor Yellow
    }
}

Write-Host ""

# 3. RABBITMQ INSTALLATION
Write-Host "3. RABBITMQ INSTALLATION" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Gray
Write-Host ""

$rabbitMQInstalled = Get-Service -Name "RabbitMQ" -ErrorAction SilentlyContinue
if ($rabbitMQInstalled) {
    Write-Host "✓ RabbitMQ is already installed" -ForegroundColor Green
}
else {
    Write-Host "RabbitMQ requires Erlang to be installed first." -ForegroundColor Yellow
    Write-Host ""
    
    # Check for Erlang
    $erlangInstalled = Test-Path "C:\Program Files\Erlang*"
    if (-not $erlangInstalled) {
        Write-Host "Step 1: Install Erlang" -ForegroundColor Cyan
        Write-Host "  1. Download from: https://www.erlang.org/downloads" -ForegroundColor White
        Write-Host "  2. Download: OTP 26.x Windows 64-bit Binary" -ForegroundColor White
        Write-Host "  3. Run the installer" -ForegroundColor White
        Write-Host ""
        Write-Host "Or use Chocolatey:" -ForegroundColor Cyan
        Write-Host "  choco install erlang" -ForegroundColor White
        Write-Host ""
    }
    else {
        Write-Host "✓ Erlang is installed" -ForegroundColor Green
    }
    
    Write-Host "Step 2: Install RabbitMQ" -ForegroundColor Cyan
    Write-Host "  Method 1: Using Chocolatey (Recommended)" -ForegroundColor Yellow
    Write-Host "    choco install rabbitmq" -ForegroundColor White
    Write-Host ""
    Write-Host "  Method 2: Manual Download" -ForegroundColor Yellow
    Write-Host "    1. Visit: https://www.rabbitmq.com/download.html" -ForegroundColor White
    Write-Host "    2. Download: RabbitMQ Windows Installer" -ForegroundColor White
    Write-Host "    3. Run the installer" -ForegroundColor White
    Write-Host ""
    
    $chocoInstalled = Get-Command choco -ErrorAction SilentlyContinue
    if ($chocoInstalled) {
        $install = Read-Host "Install RabbitMQ using Chocolatey now? (Y/N)"
        if ($install -eq "Y" -or $install -eq "y") {
            if (-not $erlangInstalled) {
                Write-Host "Installing Erlang first..." -ForegroundColor Yellow
                choco install erlang -y
            }
            Write-Host "Installing RabbitMQ..." -ForegroundColor Yellow
            choco install rabbitmq -y
            Write-Host "✓ RabbitMQ installed" -ForegroundColor Green
        }
    }
    else {
        Write-Host "Chocolatey is not installed." -ForegroundColor Yellow
        Write-Host "Install Chocolatey from: https://chocolatey.org/install" -ForegroundColor White
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Installation Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check installation status
$temporalInstalled = Get-Command temporal -ErrorAction SilentlyContinue
$minioInstalled = Test-Path "C:\minio\minio.exe"
$rabbitMQInstalled = Get-Service -Name "RabbitMQ" -ErrorAction SilentlyContinue

Write-Host "Temporal CLI: $(if($temporalInstalled){'✓ Installed'}else{'✗ Not Installed'})" -ForegroundColor $(if ($temporalInstalled) { 'Green' }else { 'Red' })
Write-Host "MinIO: $(if($minioInstalled){'✓ Installed'}else{'✗ Not Installed'})" -ForegroundColor $(if ($minioInstalled) { 'Green' }else { 'Red' })
Write-Host "RabbitMQ: $(if($rabbitMQInstalled){'✓ Installed'}else{'✗ Not Installed'})" -ForegroundColor $(if ($rabbitMQInstalled) { 'Green' }else { 'Red' })

Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Run .\start_services.ps1 to start all services" -ForegroundColor White
Write-Host "2. Verify services are running with: make health-check" -ForegroundColor White
Write-Host ""

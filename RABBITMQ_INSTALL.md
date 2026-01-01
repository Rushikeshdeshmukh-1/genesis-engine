# RabbitMQ Installation Guide

## Overview
RabbitMQ requires Administrator privileges to install. Follow these steps to install it manually.

## Prerequisites
- **Erlang OTP 26.x** must be installed first
- **Administrator access** required

## Installation Steps

### Step 1: Install Erlang

1. Download Erlang OTP 26.x from: https://www.erlang.org/downloads
2. Choose: **Windows 64-bit Binary File**
3. Run the installer as Administrator
4. Accept default installation path: `C:\Program Files\Erlang`

### Step 2: Install RabbitMQ

**Option A: Using Chocolatey (Recommended)**

Open PowerShell as Administrator and run:
```powershell
# Install Chocolatey if not already installed
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Install Erlang and RabbitMQ
choco install erlang -y
choco install rabbitmq -y
```

**Option B: Manual Installation**

1. Download RabbitMQ from: https://www.rabbitmq.com/download.html
2. Choose: **Windows Installer**
3. Run the installer as Administrator
4. Accept default installation path

### Step 3: Start RabbitMQ Service

Open PowerShell as Administrator:
```powershell
# Start the service
Start-Service RabbitMQ

# Enable management plugin
cd "C:\Program Files\RabbitMQ Server\rabbitmq_server-*\sbin"
.\rabbitmq-plugins.bat enable rabbitmq_management
```

### Step 4: Verify Installation

1. Check service is running:
```powershell
Get-Service RabbitMQ
```

2. Access management UI:
   - URL: http://localhost:15672
   - Default credentials: `guest` / `guest`

3. Test port connectivity:
```powershell
Test-NetConnection -ComputerName localhost -Port 5672
Test-NetConnection -ComputerName localhost -Port 15672
```

## Configuration for Project RDx 00

The project is configured to use:
- **Username**: `rabbitmq`
- **Password**: `rabbitmq_password`
- **AMQP Port**: 5672
- **Management Port**: 15672

To create the user:
```powershell
cd "C:\Program Files\RabbitMQ Server\rabbitmq_server-*\sbin"
.\rabbitmqctl.bat add_user rabbitmq rabbitmq_password
.\rabbitmqctl.bat set_user_tags rabbitmq administrator
.\rabbitmqctl.bat set_permissions -p / rabbitmq ".*" ".*" ".*"
```

## Troubleshooting

**Service won't start**:
- Ensure Erlang is installed
- Check Windows Event Viewer for errors
- Verify firewall isn't blocking ports 5672 and 15672

**Can't access management UI**:
- Ensure management plugin is enabled
- Try: `.\rabbitmq-plugins.bat enable rabbitmq_management`
- Restart service: `Restart-Service RabbitMQ`

## Note

RabbitMQ is **optional** for basic Project RDx 00 functionality. The application can run without it for idea generation and research features.

# Initialize PostgreSQL database for Project RDx 00

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Initializing PostgreSQL Database" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$PGHOST = "localhost"
$PGPORT = "5432"
$PGUSER = "postgres"
$PGPASSWORD = "postgres_password"
$PGDATABASE = "idea_engine"

# Set environment variable for password
$env:PGPASSWORD = $PGPASSWORD

Write-Host "Database Configuration:" -ForegroundColor Yellow
Write-Host "  Host: $PGHOST" -ForegroundColor White
Write-Host "  Port: $PGPORT" -ForegroundColor White
Write-Host "  User: $PGUSER" -ForegroundColor White
Write-Host "  Database: $PGDATABASE" -ForegroundColor White
Write-Host ""

# Check if PostgreSQL is running
Write-Host "Checking PostgreSQL connection..." -ForegroundColor Yellow
$connection = New-Object System.Net.Sockets.TcpClient
try {
    $connection.Connect($PGHOST, $PGPORT)
    $connection.Close()
    Write-Host "  ✓ PostgreSQL is running" -ForegroundColor Green
}
catch {
    Write-Host "  ✗ PostgreSQL is not running on port $PGPORT" -ForegroundColor Red
    Write-Host "  Please start PostgreSQL and try again." -ForegroundColor Red
    exit 1
}

Write-Host ""

# Check if psql is available
Write-Host "Checking for psql command..." -ForegroundColor Yellow
$psqlPath = (Get-Command psql -ErrorAction SilentlyContinue).Source

if (-not $psqlPath) {
    Write-Host "  ✗ psql command not found" -ForegroundColor Red
    Write-Host "  Please add PostgreSQL bin directory to your PATH" -ForegroundColor Red
    Write-Host "  Example: C:\Program Files\PostgreSQL\16\bin" -ForegroundColor Yellow
    exit 1
}

Write-Host "  ✓ Found psql at: $psqlPath" -ForegroundColor Green
Write-Host ""

# Create database if it doesn't exist
Write-Host "Creating database '$PGDATABASE'..." -ForegroundColor Yellow
$createDbCommand = "SELECT 1 FROM pg_database WHERE datname='$PGDATABASE'"
$dbExists = & psql -h $PGHOST -p $PGPORT -U $PGUSER -d postgres -t -c $createDbCommand 2>$null

if ($dbExists -match "1") {
    Write-Host "  ⚠ Database '$PGDATABASE' already exists" -ForegroundColor Yellow
    $recreate = Read-Host "Do you want to recreate it? This will DELETE all data! (yes/no)"
    if ($recreate -eq "yes") {
        Write-Host "  Dropping existing database..." -ForegroundColor Yellow
        & psql -h $PGHOST -p $PGPORT -U $PGUSER -d postgres -c "DROP DATABASE $PGDATABASE;" 2>$null
        & psql -h $PGHOST -p $PGPORT -U $PGUSER -d postgres -c "CREATE DATABASE $PGDATABASE;" 2>$null
        Write-Host "  ✓ Database recreated" -ForegroundColor Green
    }
    else {
        Write-Host "  Keeping existing database" -ForegroundColor Yellow
    }
}
else {
    & psql -h $PGHOST -p $PGPORT -U $PGUSER -d postgres -c "CREATE DATABASE $PGDATABASE;" 2>$null
    Write-Host "  ✓ Database created" -ForegroundColor Green
}

Write-Host ""

# Install extensions
Write-Host "Installing PostgreSQL extensions..." -ForegroundColor Yellow

Write-Host "  Installing pgvector extension..." -ForegroundColor White
& psql -h $PGHOST -p $PGPORT -U $PGUSER -d $PGDATABASE -c "CREATE EXTENSION IF NOT EXISTS vector;" 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "    ✓ pgvector extension installed" -ForegroundColor Green
}
else {
    Write-Host "    ✗ Failed to install pgvector extension" -ForegroundColor Red
    Write-Host "    Please install pgvector manually: https://github.com/pgvector/pgvector" -ForegroundColor Yellow
}

Write-Host "  Installing uuid-ossp extension..." -ForegroundColor White
& psql -h $PGHOST -p $PGPORT -U $PGUSER -d $PGDATABASE -c "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";" 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "    ✓ uuid-ossp extension installed" -ForegroundColor Green
}
else {
    Write-Host "    ✗ Failed to install uuid-ossp extension" -ForegroundColor Red
}

Write-Host ""

# Run initialization SQL
Write-Host "Running database initialization..." -ForegroundColor Yellow

$initSqlPath = Join-Path $PSScriptRoot "backend\init_db.sql"
if (Test-Path $initSqlPath) {
    Write-Host "  Executing init_db.sql..." -ForegroundColor White
    & psql -h $PGHOST -p $PGPORT -U $PGUSER -d $PGDATABASE -f $initSqlPath 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ Database initialized successfully" -ForegroundColor Green
    }
    else {
        Write-Host "  ✗ Error running init_db.sql" -ForegroundColor Red
    }
}
else {
    Write-Host "  ⚠ init_db.sql not found at: $initSqlPath" -ForegroundColor Yellow
    Write-Host "  Creating schema manually..." -ForegroundColor White
    
    $initSql = @"
CREATE SCHEMA IF NOT EXISTS idea_engine;
SET search_path TO idea_engine, public;
GRANT ALL PRIVILEGES ON SCHEMA idea_engine TO postgres;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA idea_engine TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA idea_engine TO postgres;
"@
    
    $initSql | & psql -h $PGHOST -p $PGPORT -U $PGUSER -d $PGDATABASE 2>$null
    Write-Host "  ✓ Schema created" -ForegroundColor Green
}

Write-Host ""

# Verify installation
Write-Host "Verifying database setup..." -ForegroundColor Yellow
$verifyCommand = "SELECT extname FROM pg_extension WHERE extname IN ('vector', 'uuid-ossp');"
$extensions = & psql -h $PGHOST -p $PGPORT -U $PGUSER -d $PGDATABASE -t -c $verifyCommand 2>$null

Write-Host "  Installed extensions:" -ForegroundColor White
if ($extensions -match "vector") {
    Write-Host "    ✓ vector" -ForegroundColor Green
}
else {
    Write-Host "    ✗ vector (not installed)" -ForegroundColor Red
}

if ($extensions -match "uuid-ossp") {
    Write-Host "    ✓ uuid-ossp" -ForegroundColor Green
}
else {
    Write-Host "    ✗ uuid-ossp (not installed)" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Database Initialization Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Connection String:" -ForegroundColor Yellow
Write-Host "  postgresql://${PGUSER}:${PGPASSWORD}@${PGHOST}:${PGPORT}/${PGDATABASE}" -ForegroundColor White
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Update .env file with database connection string" -ForegroundColor White
Write-Host "  2. Run database migrations: cd backend; alembic upgrade head" -ForegroundColor White
Write-Host ""

# Clear password from environment
$env:PGPASSWORD = $null

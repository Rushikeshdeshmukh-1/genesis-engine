.PHONY: help setup start stop clean test lint format install-models health-check

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@powershell -Command "Get-Content Makefile | Select-String -Pattern '^[a-zA-Z_-]+:.*?## ' | ForEach-Object { $_.Line -replace ':', '' -replace '##', ' -' }"

setup: ## Initial setup - copy env file and create directories
	@echo "Setting up project..."
	@if not exist .env copy .env.example .env
	@if not exist reports mkdir reports
	@if not exist backend\logs mkdir backend\logs
	@echo "Setup complete! Please edit .env file with your configuration."
	@echo ""
	@echo "Next steps:"
	@echo "  1. Run setup_local.ps1 to install required services"
	@echo "  2. Run init_database.ps1 to initialize the database"
	@echo "  3. Run 'make install-deps' to install dependencies"

install-deps: ## Install Python and Node.js dependencies
	@echo "Installing backend dependencies..."
	cd backend && python -m venv venv && .\venv\Scripts\activate && pip install -r requirements.txt
	@echo "Installing frontend dependencies..."
	cd frontend && npm install
	@echo "Dependencies installed!"

start-services: ## Start all infrastructure services
	@echo "Starting infrastructure services..."
	@powershell -ExecutionPolicy Bypass -File .\start_services.ps1

stop-services: ## Stop all infrastructure services
	@echo "Stopping infrastructure services..."
	@powershell -ExecutionPolicy Bypass -File .\stop_services.ps1

start-backend: ## Start backend API server
	@echo "Starting backend..."
	cd backend && powershell -ExecutionPolicy Bypass -File .\start_backend.ps1

start-worker: ## Start Temporal worker
	@echo "Starting Temporal worker..."
	cd backend && powershell -ExecutionPolicy Bypass -File .\start_worker.ps1

start-frontend: ## Start frontend development server
	@echo "Starting frontend..."
	cd frontend && powershell -ExecutionPolicy Bypass -File .\start_frontend.ps1

start: start-services ## Start all services (infrastructure + backend + frontend)
	@echo "All services starting..."
	@echo "Please run 'make start-backend' and 'make start-frontend' in separate terminals"

stop: stop-services ## Stop all services
	@echo "All services stopped!"

install-models: ## Download required LLM models
	@echo "Pulling Llama 3.1 8B model..."
	ollama pull llama3.1:8b
	@echo "Model installation complete!"

test: ## Run all tests
	cd backend && .\venv\Scripts\activate && pytest -v

test-coverage: ## Run tests with coverage
	cd backend && .\venv\Scripts\activate && pytest --cov=app --cov-report=html --cov-report=term

lint: ## Run linting
	cd backend && .\venv\Scripts\activate && ruff check app/
	cd frontend && npm run lint

format: ## Format code
	cd backend && .\venv\Scripts\activate && ruff format app/
	cd frontend && npm run format

migrate: ## Run database migrations
	cd backend && .\venv\Scripts\activate && alembic upgrade head

migrate-create: ## Create new migration (use NAME=migration_name)
	cd backend && .\venv\Scripts\activate && alembic revision --autogenerate -m "$(NAME)"

clean: ## Clean up generated files and caches
	@echo "Cleaning up..."
	@if exist backend\__pycache__ rmdir /s /q backend\__pycache__
	@if exist backend\.pytest_cache rmdir /s /q backend\.pytest_cache
	@if exist backend\venv rmdir /s /q backend\venv
	@if exist frontend\.next rmdir /s /q frontend\.next
	@if exist frontend\node_modules rmdir /s /q frontend\node_modules
	@echo "Clean complete!"

generate-ideas: ## Generate 20 new ideas (requires services running)
	curl -X POST http://localhost:8000/api/v1/ideas/generate -H "Content-Type: application/json" -d "{\"count\": 20}"

trigger-workflow: ## Trigger complete pipeline workflow
	curl -X POST http://localhost:8000/api/v1/workflows/pipeline -H "Content-Type: application/json" -d "{\"idea_count\": 10}"

health-check: ## Check health of all services
	@echo "Checking service health..."
	@powershell -Command "try { Invoke-WebRequest -Uri http://localhost:5432 -UseBasicParsing -TimeoutSec 2 | Out-Null; Write-Host 'PostgreSQL: UP' -ForegroundColor Green } catch { Write-Host 'PostgreSQL: DOWN' -ForegroundColor Red }"
	@powershell -Command "try { Invoke-WebRequest -Uri http://localhost:6379 -UseBasicParsing -TimeoutSec 2 | Out-Null; Write-Host 'Redis: UP' -ForegroundColor Green } catch { Write-Host 'Redis: DOWN' -ForegroundColor Red }"
	@powershell -Command "try { Invoke-WebRequest -Uri http://localhost:15672 -UseBasicParsing -TimeoutSec 2 | Out-Null; Write-Host 'RabbitMQ: UP' -ForegroundColor Green } catch { Write-Host 'RabbitMQ: DOWN' -ForegroundColor Red }"
	@powershell -Command "try { Invoke-WebRequest -Uri http://localhost:9001 -UseBasicParsing -TimeoutSec 2 | Out-Null; Write-Host 'MinIO: UP' -ForegroundColor Green } catch { Write-Host 'MinIO: DOWN' -ForegroundColor Red }"
	@powershell -Command "try { Invoke-WebRequest -Uri http://localhost:8080 -UseBasicParsing -TimeoutSec 2 | Out-Null; Write-Host 'Temporal UI: UP' -ForegroundColor Green } catch { Write-Host 'Temporal UI: DOWN' -ForegroundColor Red }"
	@powershell -Command "try { Invoke-WebRequest -Uri http://localhost:11434 -UseBasicParsing -TimeoutSec 2 | Out-Null; Write-Host 'Ollama: UP' -ForegroundColor Green } catch { Write-Host 'Ollama: DOWN' -ForegroundColor Red }"
	@powershell -Command "try { Invoke-WebRequest -Uri http://localhost:8000/health -UseBasicParsing -TimeoutSec 2 | Out-Null; Write-Host 'Backend: UP' -ForegroundColor Green } catch { Write-Host 'Backend: DOWN' -ForegroundColor Red }"
	@powershell -Command "try { Invoke-WebRequest -Uri http://localhost:3000 -UseBasicParsing -TimeoutSec 2 | Out-Null; Write-Host 'Frontend: UP' -ForegroundColor Green } catch { Write-Host 'Frontend: DOWN' -ForegroundColor Red }"
	@echo "Health check complete!"

dev-setup: setup install-deps ## Complete development setup
	@echo "Development environment setup complete!"
	@echo ""
	@echo "Next steps:"
	@echo "  1. Run .\setup_local.ps1 to install required services"
	@echo "  2. Run .\init_database.ps1 to initialize the database"
	@echo "  3. Run 'make start-services' to start infrastructure"
	@echo "  4. Run 'make install-models' to download LLM models"
	@echo "  5. Run 'make start-backend' to start the backend"
	@echo "  6. Run 'make start-frontend' to start the frontend"

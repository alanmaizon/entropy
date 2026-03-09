.PHONY: dev test lint run install help

help:  ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:  ## Install Python dependencies
	pip install -e ".[dev]"

dev:  ## Start the backend in development mode (hot-reload)
	uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

run:  ## Start the backend in production mode
	uvicorn backend.main:app --host 0.0.0.0 --port 8000

test:  ## Run tests
	pytest tests/ -v

lint:  ## Run ruff linter
	ruff check backend/ tests/

format:  ## Auto-fix lint issues and format code
	ruff check --fix backend/ tests/
	ruff format backend/ tests/

docker-up:  ## Start all services with Docker Compose
	docker compose -f infrastructure/docker-compose.yml up -d

docker-down:  ## Stop all Docker services
	docker compose -f infrastructure/docker-compose.yml down

frontend-install:  ## Install frontend dependencies
	cd frontend && npm install

frontend-dev:  ## Start the frontend dev server
	cd frontend && npm run dev

frontend-build:  ## Build the frontend for production
	cd frontend && npm run build

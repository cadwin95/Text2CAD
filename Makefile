.PHONY: install up dev test lint clean

install:
	@echo "📦 Installing dependencies..."
	@cd backend && uv sync
	@cd frontend && npm install

up:
	@echo "🚀 Starting services with Docker..."
	@docker compose up --build

dev:
	@echo "🛠️ Starting local development..."
	@./start_dev.sh

test:
	@echo "🧪 Running tests..."
	@cd backend && uv run pytest
	@cd frontend && npm run test --if-present

lint:
	@echo "🧹 Linting..."
	@cd backend && uv run ruff check . && uv run mypy .
	@cd frontend && npm run lint

clean:
	@echo "🗑️ Cleaning up..."
	@rm -rf backend/.venv frontend/node_modules backend/__pycache__

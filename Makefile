.PHONY: install dev test lint scan clean help

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install skill-lint (project-local)
	uv sync --extra dev

install-global: ## Install skill-lint globally
	uv tool install -e . --force

dev: install ## Install + run scan to verify setup
	uv run skill-lint .

test: ## Run all tests
	uv run pytest -v

lint: ## Run linter
	uv run ruff check src/ tests/

lint-fix: ## Auto-fix lint issues
	uv run ruff check --fix src/ tests/

scan: ## Scan this project's skill files
	uv run skill-lint .

clean: ## Remove build artifacts
	rm -rf dist/ build/ *.egg-info .pytest_cache .ruff_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

.PHONY: help install dev-install test lint format type-check clean sync-version

help:  ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install:  ## Install the package
	uv pip install -e .

dev-install:  ## Install the package with dev dependencies
	uv pip install -e ".[dev]"
	pre-commit install

test:  ## Run tests
	pytest -m "not integration" --cov=blender_mcp --cov-report=term-missing

test-all:  ## Run all tests including integration tests
	pytest --cov=blender_mcp --cov-report=term-missing

test-integration:  ## Run only integration tests
	pytest -m integration

lint:  ## Run linter (ruff)
	ruff check src/ tests/

format:  ## Format code with black
	black src/ tests/

format-check:  ## Check code formatting
	black --check src/ tests/

type-check:  ## Run type checker (mypy)
	mypy src/

check: lint type-check format-check  ## Run all checks (lint, type-check, format-check)

fix:  ## Auto-fix linting issues
	ruff check --fix src/ tests/

clean:  ## Clean up build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

sync-version:  ## Sync version across all files
	python scripts/sync_version.py

docs:  ## Generate documentation (placeholder)
	@echo "Documentation generation not yet implemented"

release: clean test  ## Prepare for release
	@echo "Ready for release!"

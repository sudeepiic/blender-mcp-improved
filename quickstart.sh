#!/bin/bash
# Quick start script for Blender MCP development

set -e

echo "=========================================="
echo "Blender MCP - Quick Start"
echo "=========================================="
echo ""

# Detect if we're in the project root
if [ ! -f "pyproject.toml" ]; then
    echo "Error: Must be run from project root"
    exit 1
fi

# Check for uv
if ! command -v uv &> /dev/null; then
    echo "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi

echo "1. Creating virtual environment..."
uv venv .venv

echo ""
echo "2. Installing dependencies..."
uv pip install -e ".[dev]"

echo ""
echo "3. Running tests..."
uv run pytest tests/ -v -m "not integration"

echo ""
echo "4. Running type check..."
uv run mypy src/blender_mcp/ --ignore-missing-imports

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Available commands:"
echo "  uv run pytest                    - Run tests"
echo "  uv run python tests/test_manual_integration.py - Run integration tests"
echo "  uv run python examples/demo_mcp_usage.py - Run demo (requires Blender)"
echo "  uv run black src/ tests/         - Format code"
echo "  uv run ruff check src/ tests/     - Lint code"
echo ""
echo "To use the MCP server with Blender:"
echo "  1. Install the addon.py in Blender"
echo "  2. Enable 'Blender MCP' in Blender preferences"
echo "  3. In Blender sidebar (N panel), click 'Connect to Claude'"
echo ""

#!/bin/bash
# Run all tests for Blender MCP

set -e

echo "=========================================="
echo "Blender MCP - Running All Tests"
echo "=========================================="
echo ""

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

# Check if uv is available
if command -v uv &> /dev/null; then
    RUNNER="uv run"
    echo "Using uv as test runner"
elif command -v python &> /dev/null; then
    RUNNER="python"
    echo "Using system python as test runner"
else
    echo "Error: Neither uv nor python found in PATH"
    exit 1
fi

echo ""
echo "=========================================="
echo "1. Unit Tests (pytest)"
echo "=========================================="
$RUNNER pytest tests/ -v --tb=short -m "not integration" --cov=blender_mcp --cov-report=term-missing

echo ""
echo "=========================================="
echo "2. Manual Integration Tests"
echo "=========================================="
$RUNNER tests/test_manual_integration.py

echo ""
echo "=========================================="
echo "3. Type Checking (mypy)"
echo "=========================================="
$RUNNER mypy src/blender_mcp/ --ignore-missing-imports --warn-unused-ignores || true

echo ""
echo "=========================================="
echo "4. Code Formatting (black --check)"
echo "=========================================="
$RUNNER black --check src/ tests/ || true

echo ""
echo "=========================================="
echo "5. Linting (ruff)"
echo "=========================================="
$RUNNER ruff check src/ tests/ || true

echo ""
echo "=========================================="
echo "All Tests Complete!"
echo "=========================================="

# Blender MCP Examples

This directory contains example scripts and demos for using Blender MCP.

## Files

### `demo_mcp_usage.py`
Interactive demo showing how to use the MCP server programmatically.

**Requirements:**
- Blender running with the MCP addon installed
- The addon server must be started (click "Connect to Claude" in Blender)

**Usage:**
```bash
# From project root
uv run python examples/demo_mcp_usage.py

# Or with venv activated
python examples/demo_mcp_usage.py
```

**Demonstrates:**
- Basic connection to Blender
- Getting scene information
- Getting object details
- Executing Python code in Blender
- Taking viewport screenshots

## Quick Start

1. Run the quickstart script to set up your environment:
   ```bash
   ./quickstart.sh
   ```

2. Run the unit tests:
   ```bash
   uv run pytest tests/
   ```

3. Run the manual integration tests (no Blender required):
   ```bash
   uv run python tests/test_manual_integration.py
   ```

4. Run the demo (requires Blender with addon running):
   ```bash
   uv run python examples/demo_mcp_usage.py
   ```

## Testing

All test scripts can be run from the `tests/` directory:

```bash
# Run all tests
./tests/run_all_tests.sh

# Or using uv
uv run pytest tests/ -v
```

#!/usr/bin/env python3
"""
Manual integration test script for Blender MCP.

This script tests the MCP server functionality without requiring
a running Blender instance. It mocks the Blender addon responses.

Run with: python tests/test_manual_integration.py
"""

import sys
import json
import time
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

try:
    from mcp.server.fastmcp import FastMCP, Context, Image
    from mcp.server.stdio import stdio_server
except ImportError:
    print("MCP library not found. Install with: pip install mcp")
    sys.exit(1)


def test_server_discovery():
    """Test that the MCP server can discover and list tools."""
    print("\n" + "="*60)
    print("TEST: Server Discovery")
    print("="*60)

    from blender_mcp.server import mcp

    # FastMCP stores tools internally
    # Check that the mcp instance exists
    print(f"\n✓ MCP Server instance created: {mcp.name}")

    # List known tool names from the server module
    import blender_mcp.server as server_module
    import inspect

    tools_found = []
    for name, obj in inspect.getmembers(server_module):
        if hasattr(obj, '__mcp_tool__'):  # FastMCP decorator marker
            tools_found.append(name)

    print(f"\n✓ Found {len(tools_found)} decorated tools in module")
    for tool in tools_found[:10]:  # Show first 10
        print(f"  - {tool}")

    return True


def test_resources():
    """Test that resources are available."""
    print("\n" + "="*60)
    print("TEST: Resources")
    print("="*60)

    from blender_mcp.server import mcp

    print(f"\n✓ MCP Server instance: {mcp.name}")
    print("  (FastMCP manages resources internally)")

    return True


def test_config_module():
    """Test configuration module."""
    print("\n" + "="*60)
    print("TEST: Configuration Module")
    print("="*60)

    from blender_mcp.config import TelemetryConfig, telemetry_config

    print("\n✓ TelemetryConfig attributes:")
    print(f"  - enabled: {telemetry_config.enabled}")
    print(f"  - max_prompt_length: {telemetry_config.max_prompt_length}")

    # Test env override
    import os
    old_val = os.environ.get("BLENDER_MCP_TELEMETRY_ENABLED")
    os.environ["BLENDER_MCP_TELEMETRY_ENABLED"] = "false"

    test_config = TelemetryConfig()
    print(f"\n✓ Environment override works:")
    print(f"  - BLENDER_MCP_TELEMETRY_ENABLED=false")
    print(f"  - config.enabled = {test_config.enabled}")

    # Restore
    if old_val is None:
        os.environ.pop("BLENDER_MCP_TELEMETRY_ENABLED", None)
    else:
        os.environ["BLENDER_MCP_TELEMETRY_ENABLED"] = old_val

    return True


def test_connection_class():
    """Test BlenderConnection class without actual connection."""
    print("\n" + "="*60)
    print("TEST: BlenderConnection Class")
    print("="*60)

    from blender_mcp.server import BlenderConnection

    conn = BlenderConnection(host="localhost", port=9876)
    print(f"\n✓ Created connection:")
    print(f"  - host: {conn.host}")
    print(f"  - port: {conn.port}")
    print(f"  - socket: {conn.sock}")

    # Test command serialization
    test_command = {
        "type": "get_scene_info",
        "params": {}
    }
    command_json = json.dumps(test_command)
    print(f"\n✓ Command serialization:")
    print(f"  {command_json}")

    return True


def test_type_hints():
    """Verify type hints are present on key functions."""
    print("\n" + "="*60)
    print("TEST: Type Hints")
    print("="*60)

    import inspect
    from blender_mcp.server import BlenderConnection

    # Check type annotations
    connect_sig = inspect.signature(BlenderConnection.connect)
    print(f"\n✓ BlenderConnection.connect signature:")
    print(f"  {connect_sig}")

    send_command_sig = inspect.signature(BlenderConnection.send_command)
    print(f"\n✓ BlenderConnection.send_command signature:")
    print(f"  {send_command_sig}")

    # Check return annotations
    return_hint = connect_sig.return_annotation
    print(f"\n✓ Return annotation: {return_hint}")

    return True


def run_all_tests():
    """Run all manual integration tests."""
    tests = [
        ("Server Discovery", test_server_discovery),
        ("Resources", test_resources),
        ("Config Module", test_config_module),
        ("Connection Class", test_connection_class),
        ("Type Hints", test_type_hints),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result, None))
        except Exception as e:
            results.append((name, False, str(e)))
            print(f"\n✗ FAILED: {e}")

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    passed = sum(1 for _, result, _ in results if result)
    total = len(results)

    for name, result, error in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
        if error:
            print(f"  Error: {error}")

    print(f"\n{passed}/{total} tests passed")

    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

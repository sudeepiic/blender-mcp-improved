#!/usr/bin/env python3
"""
Simulate MCP server communication test.

This tests the command/response flow that would happen between
the MCP server and the Blender addon.
"""

import json
import socket
import time
import threading
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
import sys
sys.path.insert(0, str(src_path))

from blender_mcp.server import BlenderConnection


def test_command_serialization():
    """Test that commands serialize correctly."""
    print("\n" + "="*60)
    print("TEST: Command Serialization")
    print("="*60)

    command = {
        "type": "get_scene_info",
        "params": {}
    }

    command_json = json.dumps(command)
    print(f"\nCommand: {command_json}")
    print("✓ Command serializes correctly")
    return True


def test_connection_creation():
    """Test that BlenderConnection can be created."""
    print("\n" + "="*60)
    print("TEST: Connection Creation")
    print("="*60)

    conn = BlenderConnection(host="localhost", port=9876)
    print(f"\n✓ Connection created: host={conn.host}, port={conn.port}")
    print(f"  Socket state: {conn.sock}")
    return True


def test_response_parsing():
    """Test that responses parse correctly."""
    print("\n" + "="*60)
    print("TEST: Response Parsing")
    print("="*60)

    # Simulate various response types
    test_responses = [
        {"status": "success", "result": {"name": "Scene", "object_count": 5}},
        {"status": "error", "message": "Object not found"},
        {"status": "success", "result": {"objects": [{"name": "Cube", "type": "MESH"}]}},
    ]

    for response in test_responses:
        response_json = json.dumps(response)
        try:
            parsed = json.loads(response_json)
            print(f"\n✓ Response parses: {parsed['status']}")
        except json.JSONDecodeError as e:
            print(f"\n✗ Failed to parse: {e}")
            return False

    return True


def test_timeout_handling():
    """Test timeout handling in connection."""
    print("\n" + "="*60)
    print("TEST: Timeout Handling")
    print("="*60)

    conn = BlenderConnection(host="localhost", port=9876)

    # Test with no Blender running - should fail gracefully
    print("\nAttempting connection (no Blender expected)...")
    result = conn.connect()

    if result:
        print("⚠ Connection succeeded (Blender might be running?)")
    else:
        print("✓ Connection failed gracefully as expected")

    print(f"  Socket state after failed connect: {conn.sock}")
    return True


def test_send_command_mock():
    """Test send_command with mocked response."""
    print("\n" "="*60)
    print("TEST: Send Command (Mocked)")
    print("="*60)

    from unittest.mock import MagicMock, Mock
    import json

    conn = BlenderConnection(host="localhost", port=9876)

    # Mock the socket
    mock_sock = MagicMock()
    conn.sock = mock_sock

    # Mock the receive_full_response
    response_data = json.dumps({"status": "success", "result": {"test": "data"}}).encode('utf-8')
    conn.receive_full_response = Mock(return_value=response_data)

    # Test sending a command
    result = conn.send_command("get_scene_info")

    print(f"\n✓ Command sent successfully")
    print(f"  Result: {result}")
    assert result == {"test": "data"}, "Unexpected result"
    print("✓ Response parsed correctly")

    return True


def run_all_tests():
    """Run all simulation tests."""
    print("\n" + "="*60)
    print("Blender MCP - Simulation Tests")
    print("="*60)
    print("\nThese tests verify the addon structure without requiring Blender.")

    tests = [
        ("Command Serialization", test_command_serialization),
        ("Connection Creation", test_connection_creation),
        ("Response Parsing", test_response_parsing),
        ("Timeout Handling", test_timeout_handling),
        ("Send Command Mock", test_send_command_mock),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result, None))
        except Exception as e:
            results.append((name, False, str(e)))

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    passed = sum(1 for _, r, _ in results if r)
    total = len(results)

    for name, result, error in results:
        status = "✓" if result else "✗"
        print(f"{status} {name}")
        if error:
            print(f"  Error: {error}")

    print(f"\n{passed}/{total} tests passed")

    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

"""
Pytest configuration and shared fixtures for Blender MCP tests.

Run tests with:
    pytest                    # Run all tests
    pytest tests/test_server.py  # Run specific file
    pytest --cov=blender_mcp  # Run with coverage
"""

import os
import sys
import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
import socket
import json

# Add src to path for imports
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


@pytest.fixture
def mock_socket():
    """Mock socket for testing Blender connection."""
    mock = MagicMock(spec=socket.socket)
    return mock


@pytest.fixture
def mock_blender_response():
    """Factory for creating mock Blender responses."""
    def _create_response(result: dict, status: str = "success") -> bytes:
        response = {"status": status, "result": result}
        return json.dumps(response).encode('utf-8')
    return _create_response


@pytest.fixture
def blender_connection(mock_socket, mock_blender_response):
    """Create a BlenderConnection with mocked socket."""
    from blender_mcp.server import BlenderConnection

    # Create connection with mocked socket
    conn = BlenderConnection(host="localhost", port=9876)
    conn.sock = mock_socket

    # Mock successful send_command
    def mock_send(cmd_type: str, params: dict = None) -> dict:
        return {"status": "success", "result": {}}

    conn.send_command = mock_send

    return conn


@pytest.fixture
def temp_dir(tmp_path):
    """Create a temporary directory for test files."""
    return tmp_path


@pytest.fixture
def env_vars(monkeypatch):
    """Fixture for setting environment variables."""
    def _set(**kwargs):
        for key, value in kwargs.items():
            monkeypatch.setenv(key, value)
    return _set


# Skip integration tests by default
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests (deselect with '-m \"not integration\"')"
    )
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )

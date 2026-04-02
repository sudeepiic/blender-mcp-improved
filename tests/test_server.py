"""
Tests for the Blender MCP server module.
"""

import pytest
import json
from unittest.mock import Mock, MagicMock, patch, call
import socket

from blender_mcp.server import (
    BlenderConnection,
    get_blender_connection,
    DEFAULT_HOST,
    DEFAULT_PORT,
)


class TestBlenderConnection:
    """Tests for BlenderConnection class."""

    def test_init(self):
        """Test connection initialization."""
        conn = BlenderConnection(host="localhost", port=9876)
        assert conn.host == "localhost"
        assert conn.port == 9876
        assert conn.sock is None

    def test_connect_success(self):
        """Test successful connection to Blender."""
        conn = BlenderConnection(host="localhost", port=9876)

        with patch('socket.socket') as mock_socket_class:
            mock_socket = MagicMock()
            mock_socket_class.return_value = mock_socket

            result = conn.connect()

            assert result is True
            assert conn.sock is not None
            mock_socket.connect.assert_called_once_with(("localhost", 9876))

    def test_connect_failure(self):
        """Test connection failure handling."""
        conn = BlenderConnection(host="localhost", port=9876)

        with patch('socket.socket') as mock_socket_class:
            mock_socket = MagicMock()
            mock_socket.connect.side_effect = OSError("Connection refused")
            mock_socket_class.return_value = mock_socket

            result = conn.connect()

            assert result is False
            assert conn.sock is None

    def test_disconnect(self):
        """Test disconnection from Blender."""
        conn = BlenderConnection(host="localhost", port=9876)
        mock_sock = MagicMock()
        conn.sock = mock_sock

        conn.disconnect()

        # Check close was called before sock was set to None
        mock_sock.close.assert_called_once()
        assert conn.sock is None

    def test_disconnect_with_error(self):
        """Test disconnect with socket error."""
        conn = BlenderConnection(host="localhost", port=9876)
        conn.sock = MagicMock()
        conn.sock.close.side_effect = OSError("Socket error")

        # Should not raise exception
        conn.disconnect()

        assert conn.sock is None

    def test_send_command_success(self, mock_blender_response):
        """Test sending command successfully."""
        conn = BlenderConnection(host="localhost", port=9876)
        mock_sock = MagicMock()

        # Mock the receive_full_response to return complete JSON
        response_data = mock_blender_response({"objects": []})
        conn.receive_full_response = Mock(return_value=response_data)

        conn.sock = mock_sock

        result = conn.send_command("get_scene_info")

        assert result == {"objects": []}
        mock_sock.sendall.assert_called_once()
        conn.receive_full_response.assert_called_once_with(mock_sock)

    def test_send_command_not_connected(self):
        """Test sending command when not connected."""
        conn = BlenderConnection(host="localhost", port=9876)
        conn.sock = None

        with patch.object(conn, 'connect', return_value=False):
            with pytest.raises(ConnectionError, match="Not connected to Blender"):
                conn.send_command("get_scene_info")

    def test_send_command_with_params(self, mock_blender_response):
        """Test sending command with parameters."""
        conn = BlenderConnection(host="localhost", port=9876)
        mock_sock = MagicMock()

        response_data = mock_blender_response({"success": True})
        conn.receive_full_response = Mock(return_value=response_data)

        conn.sock = mock_sock

        result = conn.send_command("create_cube", {"size": 2.0})

        assert result == {"success": True}

        # Verify the command JSON structure
        sent_data = json.loads(mock_sock.sendall.call_args[0][0].decode('utf-8'))
        assert sent_data["type"] == "create_cube"
        assert sent_data["params"] == {"size": 2.0}

    def test_send_command_error_response(self, mock_blender_response):
        """Test handling error response from Blender."""
        conn = BlenderConnection(host="localhost", port=9876)
        mock_sock = MagicMock()

        # Create error response
        response = json.dumps({"status": "error", "message": "Object not found"}).encode('utf-8')
        conn.receive_full_response = Mock(return_value=response)

        conn.sock = mock_sock

        with pytest.raises(Exception, match="Object not found"):
            conn.send_command("get_object", {"name": "nonexistent"})

    def test_send_command_timeout(self):
        """Test handling socket timeout."""
        conn = BlenderConnection(host="localhost", port=9876)
        mock_sock = MagicMock()

        mock_sock.sendall.side_effect = socket.timeout()
        conn.sock = mock_sock

        with pytest.raises(Exception, match="Timeout waiting for Blender response"):
            conn.send_command("get_scene_info")

        assert conn.sock is None  # Socket should be invalidated

    def test_receive_full_response_single_chunk(self):
        """Test receiving response in single chunk."""
        conn = BlenderConnection(host="localhost", port=9876)
        mock_sock = MagicMock()

        response = json.dumps({"status": "success", "result": {}}).encode('utf-8')
        mock_sock.recv.return_value = response

        result = conn.receive_full_response(mock_sock)

        assert result == response

    def test_receive_full_response_multiple_chunks(self):
        """Test receiving response in multiple chunks."""
        conn = BlenderConnection(host="localhost", port=9876)
        mock_sock = MagicMock()

        response = json.dumps({"status": "success", "result": {}}).encode('utf-8')
        # Split response into two chunks
        chunk1 = response[:len(response)//2]
        chunk2 = response[len(response)//2:]

        mock_sock.recv.side_effect = [chunk1, chunk2, b'']  # Last call returns empty

        result = conn.receive_full_response(mock_sock)

        assert result == response


class TestGetBlenderConnection:
    """Tests for get_blender_connection function."""

    @pytest.fixture
    def reset_global_connection(self):
        """Reset global connection between tests."""
        import blender_mcp.server
        original = blender_mcp.server._blender_connection
        blender_mcp.server._blender_connection = None
        yield
        blender_mcp.server._blender_connection = original

    def test_creates_new_connection(self, reset_global_connection):
        """Test creating a new Blender connection."""
        with patch('blender_mcp.server.BlenderConnection') as mock_conn_class:
            mock_conn = MagicMock()
            mock_conn.connect.return_value = True
            mock_conn.send_command.return_value = {"enabled": False}
            mock_conn_class.return_value = mock_conn

            result = get_blender_connection()

            assert result is mock_conn
            mock_conn_class.assert_called_once_with(host=DEFAULT_HOST, port=DEFAULT_PORT)
            mock_conn.connect.assert_called_once()

    def test_reuses_existing_connection(self, reset_global_connection):
        """Test reusing an existing valid connection."""
        import blender_mcp.server

        # Set up existing connection
        mock_conn = MagicMock()
        mock_conn.send_command.return_value = {"enabled": False}
        blender_mcp.server._blender_connection = mock_conn

        result = get_blender_connection()

        assert result is mock_conn
        # Should not create a new connection
        mock_conn.connect.assert_not_called()

    def test_connection_from_env_vars(self, reset_global_connection, env_vars):
        """Test connection using environment variables."""
        env_vars(BLENDER_HOST="192.168.1.1", BLENDER_PORT="9999")

        with patch('blender_mcp.server.BlenderConnection') as mock_conn_class:
            mock_conn = MagicMock()
            mock_conn.connect.return_value = True
            mock_conn.send_command.return_value = {"enabled": False}
            mock_conn_class.return_value = mock_conn

            get_blender_connection()

            mock_conn_class.assert_called_once_with(host="192.168.1.1", port=9999)

    def test_failed_connection_raises(self, reset_global_connection):
        """Test that failed connection raises exception."""
        with patch('blender_mcp.server.BlenderConnection') as mock_conn_class:
            mock_conn = MagicMock()
            mock_conn.connect.return_value = False
            mock_conn_class.return_value = mock_conn

            with pytest.raises(Exception, match="Could not connect to Blender"):
                get_blender_connection()


@pytest.mark.integration
class TestIntegration:
    """Integration tests (require running Blender addon)."""

    def test_real_connection_skip_if_not_running(self):
        """Test that real connection fails gracefully when Blender not running."""
        conn = BlenderConnection(host="localhost", port=9876)

        # This should fail if Blender addon is not running
        result = conn.connect()
        # We expect connection to fail in CI/test environment
        if not result:
            assert conn.sock is None

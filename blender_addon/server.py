"""
Blender MCP Socket Server.

This module contains the BlenderMCPServer class that handles socket communication
between Blender and the MCP server.
"""

import json
import socket
import threading
import time
import traceback
from typing import Dict, Any, Callable, Optional

import bpy


# Default headers for API requests
import requests
REQ_HEADERS = requests.utils.default_headers()
REQ_HEADERS.update({"User-Agent": "blender-mcp"})


def get_rodin_free_trial_key() -> str:
    """
    Get the Rodin free trial API key from environment variable or use default.
    Users can override by setting RODIN_FREE_TRIAL_KEY environment variable.
    """
    import os
    return os.environ.get("RODIN_FREE_TRIAL_KEY", "k9TcfFoEhNd9cCPP2guHAHHHkctZHIRhZDywZ1euGUXwihbYLpOjQhofby80NJez")


class BlenderMCPServer:
    """Socket server for communication with the MCP server."""

    def __init__(self, host: str = 'localhost', port: int = 9876) -> None:
        """Initialize the server.

        Args:
            host: Host address to bind to.
            port: Port number to bind to.
        """
        self.host = host
        self.port = port
        self.running = False
        self.socket: Optional[socket.socket] = None
        self.server_thread: Optional[threading.Thread] = None

    def start(self) -> None:
        """Start the socket server."""
        if self.running:
            print("Server is already running")
            return

        self.running = True

        try:
            # Create socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((self.host, self.port))
            self.socket.listen(1)

            # Start server thread
            self.server_thread = threading.Thread(target=self._server_loop)
            self.server_thread.daemon = True
            self.server_thread.start()

            print(f"BlenderMCP server started on {self.host}:{self.port}")
        except Exception as e:
            print(f"Failed to start server: {str(e)}")
            self.stop()

    def stop(self) -> None:
        """Stop the socket server."""
        self.running = False

        # Close socket
        if self.socket:
            try:
                self.socket.close()
            except Exception:
                pass
            self.socket = None

        # Wait for thread to finish
        if self.server_thread:
            try:
                if self.server_thread.is_alive():
                    self.server_thread.join(timeout=1.0)
            except Exception:
                pass
            self.server_thread = None

        print("BlenderMCP server stopped")

    def _server_loop(self) -> None:
        """Main server loop in a separate thread."""
        print("Server thread started")
        assert self.socket is not None  # For type checker
        self.socket.settimeout(1.0)  # Timeout to allow for stopping

        while self.running:
            try:
                # Accept new connection
                try:
                    client, address = self.socket.accept()
                    print(f"Connected to client: {address}")

                    # Handle client in a separate thread
                    client_thread = threading.Thread(
                        target=self._handle_client,
                        args=(client,)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                except socket.timeout:
                    # Just check running condition
                    continue
                except Exception as e:
                    print(f"Error accepting connection: {str(e)}")
                    time.sleep(0.5)
            except Exception as e:
                print(f"Error in server loop: {str(e)}")
                if not self.running:
                    break
                time.sleep(0.5)

        print("Server thread stopped")

    def _handle_client(self, client: socket.socket) -> None:
        """Handle connected client.

        Args:
            client: The client socket.
        """
        print("Client handler started")
        client.settimeout(None)  # No timeout
        buffer = b''

        try:
            while self.running:
                # Receive data
                try:
                    data = client.recv(8192)
                    if not data:
                        print("Client disconnected")
                        break

                    buffer += data
                    try:
                        # Try to parse command
                        command = json.loads(buffer.decode('utf-8'))
                        buffer = b''

                        # Execute command in Blender's main thread
                        def execute_wrapper():
                            try:
                                response = self.execute_command(command)
                                response_json = json.dumps(response)
                                try:
                                    client.sendall(response_json.encode('utf-8'))
                                except Exception:
                                    print("Failed to send response - client disconnected")
                            except Exception as e:
                                print(f"Error executing command: {str(e)}")
                                traceback.print_exc()
                                try:
                                    error_response = {
                                        "status": "error",
                                        "message": str(e)
                                    }
                                    client.sendall(json.dumps(error_response).encode('utf-8'))
                                except Exception:
                                    pass
                            return None

                        # Schedule execution in main thread
                        bpy.app.timers.register(execute_wrapper, first_interval=0.0)
                    except json.JSONDecodeError:
                        # Incomplete data, wait for more
                        pass
                except Exception as e:
                    print(f"Error receiving data: {str(e)}")
                    break
        except Exception as e:
            print(f"Error in client handler: {str(e)}")
        finally:
            try:
                client.close()
            except Exception:
                pass
            print("Client handler stopped")

    def execute_command(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a command in the main Blender thread.

        Args:
            command: Command dictionary with 'type' and optional 'params'.

        Returns:
            Response dictionary with 'status' and 'result' or 'message'.
        """
        try:
            return self._execute_command_internal(command)

        except Exception as e:
            print(f"Error executing command: {str(e)}")
            traceback.print_exc()
            return {"status": "error", "message": str(e)}

    def _execute_command_internal(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """Internal command execution with proper context.

        Args:
            command: Command dictionary.

        Returns:
            Response dictionary.
        """
        from . import handlers

        cmd_type = command.get("type")
        params = command.get("params", {})

        # Get all available handlers
        all_handlers = handlers.get_handlers()

        handler = all_handlers.get(cmd_type)
        if handler:
            try:
                print(f"Executing handler for {cmd_type}")
                result = handler(**params)
                print(f"Handler execution complete")
                return {"status": "success", "result": result}
            except Exception as e:
                print(f"Error in handler: {str(e)}")
                traceback.print_exc()
                return {"status": "error", "message": str(e)}
        else:
            return {"status": "error", "message": f"Unknown command type: {cmd_type}"}

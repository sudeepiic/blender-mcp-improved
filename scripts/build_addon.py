#!/usr/bin/env python3
"""
Build a complete Blender addon from the modular structure.

This script combines all the modular code into a single installable addon.py file.
"""

import os
import sys
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
ADDON_SRC = PROJECT_ROOT / "blender_addon"
OUTPUT_FILE = PROJECT_ROOT / "addon_modular.py"


def build_addon():
    """Build the complete addon from modular components."""

    print("Building modular Blender addon...")

    # Read the original addon header
    original_addon = PROJECT_ROOT / "addon.py"
    with open(original_addon, 'r') as f:
        content = f.read()

    # Extract the header (up to the class definition)
    lines = content.split('\n')
    header_lines = []
    in_header = True

    for i, line in enumerate(lines):
        if 'class BlenderMCPServer:' in line:
            in_header = False
            break
        if in_header:
            # Replace the hardcoded key with the function version
            if 'RODIN_FREE_TRIAL_KEY = ' in line:
                continue  # Skip the hardcoded key line
            header_lines.append(line)

    # Add the improved function version
    header_lines.append("")
    header_lines.append("def get_rodin_free_trial_key() -> str:")
    header_lines.append('    """Get Rodin API key from env or use default."""')
    header_lines.append('    import os')
    header_lines.append('    return os.environ.get("RODIN_FREE_TRIAL_KEY",')
    header_lines.append('        "k9TcfFoEhNd9cCPP2guHAHHHkctZHIRhZDywZ1euGUXwihbYLpOjQhofby80NJez")')
    header_lines.append('    )')
    header_lines.append("")

    header = '\n'.join(header_lines)

    # Read modular components
    components = []

    # Read the complete polyhaven integration
    polyhaven_file = ADDON_SRC / "integrations" / "polyhaven.py"
    with open(polyhaven_file, 'r') as f:
        polyhaven_code = f.read()
        # Extract functions (skip imports at top)
        polyhaven_funcs = '\n'.join([
            line for line in polyhaven_code.split('\n')
            if not line.strip().startswith('import ') and
               not line.strip().startswith('from ') and
               not line.strip().startswith('# ') and
               line.strip()
        ])
        components.append(f"\n    #region Poly Haven Integration")
        components.append(polyhaven_funcs)
        components.append(f"    #endregion\n")

    # Read the complete sketchfab integration
    sketchfab_file = ADDON_SRC / "integrations" / "sketchfab.py"
    with open(sketchfab_file, 'r') as f:
        sketchfab_code = f.read()
        sketchfab_funcs = '\n'.join([
            line for line in sketchfab_code.split('\n')
            if not line.strip().startswith('import ') and
               not line.strip().startswith('from ') and
               not line.strip().startswith('# ') and
               line.strip()
        ])
        components.append(f"\n    #region Sketchfab Integration")
        components.append(sketchfab_funcs)
        components.append(f"    #endregion\n")

    # Build the complete addon
    output_parts = [header]

    # Add the server class wrapper
    output_parts.append("""
class BlenderMCPServer:
    \"\"\"Socket server for communication with the MCP server.\"\"\"

    def __init__(self, host: str = 'localhost', port: int = 9876):
        self.host = host
        self.port = port
        self.running = False
        self.socket = None
        self.server_thread = None

    def start(self):
        if self.running:
            print("Server is already running")
            return

        self.running = True

        try:
            import socket
            import threading

            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((self.host, self.port))
            self.socket.listen(1)

            self.server_thread = threading.Thread(target=self._server_loop)
            self.server_thread.daemon = True
            self.server_thread.start()

            print(f"BlenderMCP server started on {self.host}:{self.port}")
        except Exception as e:
            print(f"Failed to start server: {str(e)}")
            self.stop()

    def stop(self):
        self.running = False

        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None

        if self.server_thread:
            try:
                if self.server_thread.is_alive():
                    self.server_thread.join(timeout=1.0)
            except:
                pass
            self.server_thread = None

        print("BlenderMCP server stopped")

    def _server_loop(self):
        import socket
        import json
        import time

        print("Server thread started")
        self.socket.settimeout(1.0)

        while self.running:
            try:
                try:
                    client, address = self.socket.accept()
                    print(f"Connected to client: {address}")

                    client_thread = threading.Thread(
                        target=self._handle_client,
                        args=(client,)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                except socket.timeout:
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

    def _handle_client(self, client):
        import json
        import time

        print("Client handler started")
        client.settimeout(None)
        buffer = b''

        try:
            while self.running:
                try:
                    data = client.recv(8192)
                    if not data:
                        print("Client disconnected")
                        break

                    buffer += data
                    try:
                        command = json.loads(buffer.decode('utf-8'))
                        buffer = b''

                        def execute_wrapper():
                            try:
                                response = self.execute_command(command)
                                response_json = json.dumps(response)
                                try:
                                    client.sendall(response_json.encode('utf-8'))
                                except:
                                    print("Failed to send response - client disconnected")
                            except Exception as e:
                                print(f"Error executing command: {str(e)}")
                                try:
                                    error_response = {"status": "error", "message": str(e)}
                                    client.sendall(json.dumps(error_response).encode('utf-8'))
                                except:
                                    pass
                            return None

                        import bpy
                        bpy.app.timers.register(execute_wrapper, first_interval=0.0)
                    except json.JSONDecodeError:
                        pass
                except Exception as e:
                    print(f"Error receiving data: {str(e)}")
                    break
        except Exception as e:
            print(f"Error in client handler: {str(e)}")
        finally:
            try:
                client.close()
            except:
                pass
            print("Client handler stopped")

    def execute_command(self, command):
        try:
            return self._execute_command_internal(command)
        except Exception as e:
            print(f"Error executing command: {str(e)}")
            import traceback
            traceback.print_exc()
            return {"status": "error", "message": str(e)}

    def _execute_command_internal(self, command):
        cmd_type = command.get("type")
        params = command.get("params", {})

        # Import integration modules
        from blender_addon.integrations import polyhaven, sketchfab
        import blender_addon.handlers as handlers

        handlers = {
            "get_scene_info": handlers.get_scene_info,
            "get_object_info": handlers.get_object_info,
            "get_viewport_screenshot": handlers.get_viewport_screenshot,
            "execute_code": handlers.execute_code,
            "get_telemetry_consent": handlers.get_telemetry_consent,
        }

        # Add conditional handlers
        import bpy
        if bpy.context.scene.blendermcp_use_polyhaven:
            handlers.update({
                "get_polyhaven_categories": polyhaven.get_categories,
                "search_polyhaven_assets": polyhaven.search_assets,
                "download_polyhaven_asset": polyhaven.download_asset,
                "set_texture": handlers.set_texture,
            })

        if bpy.context.scene.blendermcp_use_sketchfab:
            handlers.update({
                "search_sketchfab_models": sketchfab.search_models,
                "get_sketchfab_model_preview": sketchfab.get_model_preview,
                "download_sketchfab_model": sketchfab.download_model,
            })

        # Get status handlers
        handlers.update({
            "get_polyhaven_status": handlers.get_polyhaven_status,
            "get_hyper3d_status": handlers.get_hyper3d_status,
            "get_sketchfab_status": handlers.get_sketchfab_status,
            "get_hunyuan3d_status": handlers.get_hunyuan3d_status,
        })

        handler = handlers.get(cmd_type)
        if handler:
            try:
                print(f"Executing handler for {cmd_type}")
                result = handler(**params)
                print(f"Handler execution complete")
                return {"status": "success", "result": result}
            except Exception as e:
                print(f"Error in handler: {str(e)}")
                import traceback
                traceback.print_exc()
                return {"status": "error", "message": str(e)}
        else:
            return {"status": "error", "message": f"Unknown command type: {cmd_type}"}
""")

    # Now add all the integration functions inline
    # This is a simplified approach - for full modular structure, you'd need proper packaging

    output_parts.append("\n# Include handler functions")
    output_parts.append("""
# Get scene info handler
def get_scene_info():
    import bpy
    scene_info = {
        "name": bpy.context.scene.name,
        "object_count": len(bpy.context.scene.objects),
        "objects": [],
        "materials_count": len(bpy.data.materials),
    }
    for i, obj in enumerate(bpy.context.scene.objects):
        if i >= 10:
            break
        scene_info["objects"].append({
            "name": obj.name,
            "type": obj.type,
            "location": [round(float(obj.location.x), 2),
            [round(float(obj.location.y), 2)],
            [round(float(obj.location.z), 2)],
        })
    return scene_info
""")

    # Write the complete addon
    output = '\n'.join(output_parts)

    with open(OUTPUT_FILE, 'w') as f:
        f.write(output)

    print(f"✓ Built addon: {OUTPUT_FILE}")
    print(f"  Size: {len(output)} characters")

    return OUTPUT_FILE


if __name__ == "__main__":
    build_addon()

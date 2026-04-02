#!/usr/bin/env python3
"""
Demo script showing how to use the Blender MCP server programmatically.

This demonstrates how to:
1. Connect to the Blender addon
2. Send commands to Blender
3. Handle responses

Note: This requires the Blender addon to be running with the server started.
"""

import sys
import json
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from blender_mcp.server import BlenderConnection, get_blender_connection


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "="*60)
    print(title)
    print("="*60)


def demo_basic_connection():
    """Demonstrate basic connection to Blender."""
    print_section("DEMO: Basic Connection")

    # Create a connection
    conn = BlenderConnection(host="localhost", port=9876)

    # Try to connect
    print(f"\nConnecting to {conn.host}:{conn.port}...")
    if conn.connect():
        print("✓ Connected successfully!")
        conn.disconnect()
        return True
    else:
        print("✗ Connection failed. Make sure Blender addon is running.")
        return False


def demo_get_scene_info():
    """Demonstrate getting scene information from Blender."""
    print_section("DEMO: Get Scene Info")

    try:
        conn = get_blender_connection()
        print("\nFetching scene information...")

        result = conn.send_command("get_scene_info")

        print(f"\n✓ Scene: {result.get('name')}")
        print(f"✓ Objects: {result.get('object_count')}")
        print(f"✓ Materials: {result.get('materials_count')}")

        if result.get('objects'):
            print("\nObjects in scene:")
            for obj in result['objects'][:5]:  # Show first 5
                print(f"  - {obj['name']} ({obj['type']}) at {obj['location']}")

        return True

    except ConnectionError:
        print("\n✗ Could not connect to Blender.")
        print("  Make sure the Blender addon is installed and running.")
        return False
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return False


def demo_execute_code():
    """Demonstrate executing arbitrary Python code in Blender."""
    print_section("DEMO: Execute Python Code")

    try:
        conn = get_blender_connection()

        # Simple code to list all objects
        code = """
import bpy
for obj in bpy.context.scene.objects:
    print(f"{obj.name}: {obj.type}")
"""

        print("\nExecuting Python code in Blender...")
        print(f"Code:\n{code}")

        result = conn.send_command("execute_code", {"code": code})

        if result.get("executed"):
            print("\n✓ Code executed successfully")
            output = result.get("result", "")
            if output:
                print(f"Output:\n{output}")
        else:
            print("\n✗ Code execution failed")

        return True

    except Exception as e:
        print(f"\n✗ Error: {e}")
        return False


def demo_get_object_info():
    """Demonstrate getting detailed object information."""
    print_section("DEMO: Get Object Info")

    try:
        conn = get_blender_connection()

        # First get scene to find an object
        scene = conn.send_command("get_scene_info")
        objects = scene.get("objects", [])

        if not objects:
            print("\n✗ No objects found in scene")
            return False

        # Get info for first object
        obj_name = objects[0]["name"]
        print(f"\nFetching info for: {obj_name}")

        result = conn.send_command("get_object_info", {"name": obj_name})

        print(f"\n✓ Type: {result.get('type')}")
        print(f"✓ Location: {result.get('location')}")
        print(f"✓ Rotation: {result.get('rotation')}")
        print(f"✓ Scale: {result.get('scale')}")
        print(f"✓ Visible: {result.get('visible')}")

        if "mesh" in result:
            mesh = result["mesh"]
            print(f"\n  Mesh Stats:")
            print(f"  - Vertices: {mesh['vertices']}")
            print(f"  - Edges: {mesh['edges']}")
            print(f"  - Polygons: {mesh['polygons']}")

        return True

    except Exception as e:
        print(f"\n✗ Error: {e}")
        return False


def demo_screenshot():
    """Demonstrate taking a screenshot of the viewport."""
    print_section("DEMO: Viewport Screenshot")

    import tempfile

    try:
        conn = get_blender_connection()

        # Create temp file for screenshot
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            screenshot_path = f.name

        print(f"\nCapturing screenshot to: {screenshot_path}")

        result = conn.send_command("get_viewport_screenshot", {
            "filepath": screenshot_path,
            "max_size": 400
        })

        if result.get("success"):
            print(f"✓ Screenshot captured: {result.get('width')}x{result.get('height')}px")
            print(f"  Saved to: {screenshot_path}")
        else:
            print(f"✗ Screenshot failed: {result.get('error')}")

        return True

    except Exception as e:
        print(f"\n✗ Error: {e}")
        return False


def main():
    """Run all demos."""
    print("\n" + "="*60)
    print("Blender MCP - Usage Demo")
    print("="*60)
    print("\nThis demo requires Blender to be running with the MCP addon.")
    print("Start the addon in Blender:")
    print("  1. Open Blender")
    print("  2. Press N to open sidebar")
    print("  3. Find 'BlenderMCP' tab")
    print("  4. Click 'Connect to Claude'")

    input("\nPress Enter when Blender addon is running...")

    demos = [
        ("Basic Connection", demo_basic_connection),
        ("Get Scene Info", demo_get_scene_info),
        ("Get Object Info", demo_get_object_info),
        ("Execute Python Code", demo_execute_code),
        ("Viewport Screenshot", demo_screenshot),
    ]

    results = []
    for name, demo_func in demos:
        try:
            result = demo_func()
            results.append((name, result))
        except KeyboardInterrupt:
            print("\n\nDemo interrupted by user")
            break
        except Exception as e:
            print(f"\n✗ Demo '{name}' crashed: {e}")
            results.append((name, False))

    # Summary
    print_section("Demo Summary")
    passed = sum(1 for _, r in results if r)
    total = len(results)

    for name, result in results:
        status = "✓" if result else "✗"
        print(f"{status} {name}")

    print(f"\n{passed}/{total} demos successful")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

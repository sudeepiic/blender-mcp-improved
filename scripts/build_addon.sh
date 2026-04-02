#!/bin/bash
# Build the modular Blender addon into a single installable file

echo "=========================================="
echo "Building Modular Blender Addon"
echo "=========================================="

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

# Create the combined addon file
OUTPUT="blender_mcp_complete.py"

echo "Creating $OUTPUT..."

# Start with the original addon but with the security fix
cat > "$OUTPUT" << 'HEADER'
# Code created by Siddharth Ahuja: www.github.com/ahujasid © 2025
# Improved version with modular architecture

import re
import bpy
import mathutils
import json
import threading
import socket
import time
import requests
import tempfile
import traceback
import os
import shutil
import zipfile
from bpy.props import IntProperty, BoolProperty
import io
from datetime import datetime
import hashlib, hmac, base64
import os.path as osp
from contextlib import redirect_stdout, suppress

bl_info = {
    "name": "Blender MCP",
    "author": "Siddharth Ahuja",
    "version": (1, 5, 5),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > BlenderMCP",
    "description": "Connect Blender to Claude via MCP (Improved modular version)",
    "category": "Interface",
}

# API Headers
REQ_HEADERS = requests.utils.default_headers()
REQ_HEADERS.update({"User-Agent": "blender-mcp"})

# API Key function with environment variable support
def get_rodin_free_trial_key():
    """Get the Rodin free trial API key from environment variable or use default."""
    return os.environ.get("RODIN_FREE_TRIAL_KEY", "k9TcfFoEhNd9cCPP2guHAHHHkctZHIRhZDywZ1euGUXwihbYLpOjQhofby80NJez")

HEADER

# Append the original addon with security fix
# We need to remove the hardcoded key line and add our function
grep -v "^RODIN_FREE_TRIAL_KEY = " addon.py >> "$OUTPUT"

# Add the function version
cat >> "$OUTPUT" << 'KEYFUNC'

# Use environment variable for API key (allows override)
RODIN_FREE_TRIAL_KEY = get_rodin_free_trial_key()
KEYFUNC

# Append the rest of the addon
tail -n +35 addon.py >> "$OUTPUT"

echo ""
echo "✓ Built: $OUTPUT"
echo ""
echo "To install in Blender:"
echo "  1. Copy blender_mcp_complete.py to ~/.config/blender/addons/"
echo "  2. In Blender: Edit → Preferences → Add-ons → Install..."
echo "  3. Select blender_mcp_complete.py"
echo "  4. Enable 'Interface: Blender MCP'"
echo ""
echo "Or use the original addon.py (has security fix applied)"

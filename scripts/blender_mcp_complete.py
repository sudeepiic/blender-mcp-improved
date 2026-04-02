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


# Use environment variable for API key (allows override)
RODIN_FREE_TRIAL_KEY = get_rodin_free_trial_key()

"""
Blender MCP Addon - Main entry point.

This addon connects Blender to Claude AI through the Model Context Protocol (MCP).
"""

bl_info = {
    "name": "Blender MCP",
    "author": "Siddharth Ahuja",
    "version": (1, 5, 5),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > BlenderMCP",
    "description": "Connect Blender to Claude via MCP",
    "category": "Interface",
}

# Import submodules
from . import server
from . import properties
from . import ui

# Import operators
from .ui import (
    BLENDERMCP_OT_StartServer,
    BLENDERMCP_OT_StopServer,
    BLENDERMCP_OT_SetFreeTrialHyper3DAPIKey,
    BLENDERMCP_OT_OpenTerms,
    BlenderMCP_PT_Panel,
)


def register():
    """Register all addon classes and properties."""
    # Register properties
    properties.register()

    # Register UI operators and panels
    ui.register()


def unregister():
    """Unregister all addon classes and properties."""
    # Unregister UI first
    ui.unregister()

    # Unregister properties
    properties.unregister()

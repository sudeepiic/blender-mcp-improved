"""
UI components for the Blender MCP addon.

This module contains the panel and operators for the Blender UI.
"""

import webbrowser

import bpy

from . import server
from .server import get_rodin_free_trial_key


class BlenderMCP_PT_Panel(bpy.types.Panel):
    """Main panel for the Blender MCP addon in the 3D View sidebar."""

    bl_label = "BlenderMCP"
    bl_idname = "BLENDERMCP_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'BlenderMCP'

    def draw(self, context: bpy.types.Context) -> None:
        """Draw the panel UI."""
        layout = self.layout
        scene = context.scene

        # Telemetry section
        box = layout.box()
        box.label(text="Telemetry", icon='INFO')
        box.prop(scene, "blendermcp_telemetry_consent",
                 text="Allow anonymous usage data collection")
        box.operator("blendermcp.open_terms", text="View Terms and Conditions")

        layout.separator()

        # Poly Haven section
        box = layout.box()
        box.label(text="Poly Haven Assets", icon='TEXTURE')
        box.prop(scene, "blendermcp_use_polyhaven", text="Use Poly Haven")

        # Hyper3D section
        box = layout.box()
        box.label(text="Hyper3D Rodin Generation", icon='MOD_NODES')
        box.prop(scene, "blendermcp_use_hyper3d", text="Use Hyper3D Rodin")
        if scene.blendermcp_use_hyper3d:
            box.prop(scene, "blendermcp_hyper3d_mode", text="Mode")
            box.prop(scene, "blendermcp_hyper3d_api_key", text="API Key")
            row = box.row()
            row.operator("blendermcp.set_hyper3d_free_trial_api_key",
                        text="Use Free Trial Key")

        # Sketchfab section
        box = layout.box()
        box.label(text="Sketchfab Models", icon='MESH_MONKEY')
        box.prop(scene, "blendermcp_use_sketchfab", text="Use Sketchfab")
        if scene.blendermcp_use_sketchfab:
            box.prop(scene, "blendermcp_sketchfab_api_key", text="API Key")

        # Hunyuan3D section
        box = layout.box()
        box.label(text="Tencent Hunyuan 3D", icon='MOD_SCULPT')
        box.prop(scene, "blendermcp_use_hunyuan3d",
                 text="Use Tencent Hunyuan 3D model generation")
        if scene.blendermcp_use_hunyuan3d:
            box.prop(scene, "blendermcp_hunyuan3d_mode", text="Hunyuan3D Mode")
            if scene.blendermcp_hunyuan3d_mode == 'OFFICIAL_API':
                box.prop(scene, "blendermcp_hunyuan3d_secret_id", text="SecretId")
                box.prop(scene, "blendermcp_hunyuan3d_secret_key", text="SecretKey")
            if scene.blendermcp_hunyuan3d_mode == 'LOCAL_API':
                box.prop(scene, "blendermcp_hunyuan3d_api_url", text="API URL")
                box.prop(scene, "blendermcp_hunyuan3d_octree_resolution",
                         text="Octree Resolution")
                box.prop(scene, "blendermcp_hunyuan3d_num_inference_steps",
                         text="Number of Inference Steps")
                box.prop(scene, "blendermcp_hunyuan3d_guidance_scale", text="Guidance Scale")
                box.prop(scene, "blendermcp_hunyuan3d_texture", text="Generate Texture")

        layout.separator()

        # Connection section
        if not scene.blendermcp_server_running:
            layout.operator("blendermcp.start_server", text="Connect to MCP server")
        else:
            layout.operator("blendermcp.stop_server", text="Disconnect from MCP server")
            layout.label(text=f"Running on port {scene.blendermcp_port}")


class BLENDERMCP_OT_SetFreeTrialHyper3DAPIKey(bpy.types.Operator):
    """Operator to set the free trial Hyper3D API key."""

    bl_idname = "blendermcp.set_hyper3d_free_trial_api_key"
    bl_label = "Set Free Trial API Key"

    def execute(self, context: bpy.types.Context) -> set:
        """Set the free trial API key."""
        context.scene.blendermcp_hyper3d_api_key = get_rodin_free_trial_key()
        context.scene.blendermcp_hyper3d_mode = 'MAIN_SITE'
        self.report({'INFO'}, "API Key set successfully!")
        return {'FINISHED'}


class BLENDERMCP_OT_StartServer(bpy.types.Operator):
    """Operator to start the Blender MCP server."""

    bl_idname = "blendermcp.start_server"
    bl_label = "Connect to Claude"
    bl_description = "Start the BlenderMCP server to connect with Claude"

    def execute(self, context: bpy.types.Context) -> set:
        """Start the server."""
        scene = context.scene

        # Create a new server instance
        if not hasattr(bpy.types, "blendermcp_server") or not bpy.types.blendermcp_server:
            bpy.types.blendermcp_server = server.BlenderMCPServer(port=scene.blendermcp_port)

        # Start the server
        bpy.types.blendermcp_server.start()
        scene.blendermcp_server_running = True

        return {'FINISHED'}


class BLENDERMCP_OT_StopServer(bpy.types.Operator):
    """Operator to stop the Blender MCP server."""

    bl_idname = "blendermcp.stop_server"
    bl_label = "Stop the connection to Claude"
    bl_description = "Stop the connection to Claude"

    def execute(self, context: bpy.types.Context) -> set:
        """Stop the server."""
        scene = context.scene

        # Stop the server if it exists
        if hasattr(bpy.types, "blendermcp_server") and bpy.types.blendermcp_server:
            bpy.types.blendermcp_server.stop()
            del bpy.types.blendermcp_server

        scene.blendermcp_server_running = False

        return {'FINISHED'}


class BLENDERMCP_OT_OpenTerms(bpy.types.Operator):
    """Operator to open the terms and conditions in a web browser."""

    bl_idname = "blendermcp.open_terms"
    bl_label = "View Terms and Conditions"
    bl_description = "Open the Terms and Conditions document"

    def execute(self, context: bpy.types.Context) -> set:
        """Open the terms and conditions URL."""
        terms_url = "https://github.com/ahujasid/blender-mcp/blob/main/TERMS_AND_CONDITIONS.md"
        try:
            webbrowser.open(terms_url)
            self.report({'INFO'}, "Terms and Conditions opened in browser")
        except Exception as e:
            self.report({'ERROR'}, f"Could not open Terms and Conditions: {str(e)}")

        return {'FINISHED'}


def register() -> None:
    """Register all UI classes."""
    bpy.utils.register_class(BlenderMCP_PT_Panel)
    bpy.utils.register_class(BLENDERMCP_OT_StartServer)
    bpy.utils.register_class(BLENDERMCP_OT_StopServer)
    bpy.utils.register_class(BLENDERMCP_OT_SetFreeTrialHyper3DAPIKey)
    bpy.utils.register_class(BLENDERMCP_OT_OpenTerms)


def unregister() -> None:
    """Unregister all UI classes."""
    bpy.utils.unregister_class(BlenderMCP_PT_Panel)
    bpy.utils.unregister_class(BLENDERMCP_OT_StartServer)
    bpy.utils.unregister_class(BLENDERMCP_OT_StopServer)
    bpy.utils.unregister_class(BLENDERMCP_OT_SetFreeTrialHyper3DAPIKey)
    bpy.utils.unregister_class(BLENDERMCP_OT_OpenTerms)

"""
Command handlers for the Blender MCP addon.

This module contains all the functions that handle commands from the MCP server.
Each handler corresponds to a command type that can be sent from the MCP server.
"""

import io
import contextlib
from typing import Dict, Any, Callable, Optional

import bpy
import mathutils


def get_handlers() -> Dict[str, Callable]:
    """Get all available command handlers.

    Returns:
        Dictionary mapping command type names to handler functions.
    """
    # Base handlers that are always available
    handlers: Dict[str, Callable] = {
        "get_scene_info": get_scene_info,
        "get_object_info": get_object_info,
        "get_viewport_screenshot": get_viewport_screenshot,
        "execute_code": execute_code,
        "get_telemetry_consent": get_telemetry_consent,
        "get_polyhaven_status": get_polyhaven_status,
        "get_hyper3d_status": get_hyper3d_status,
        "get_sketchfab_status": get_sketchfab_status,
        "get_hunyuan3d_status": get_hunyuan3d_status,
    }

    # Add Polyhaven handlers only if enabled
    if bpy.context.scene.blendermcp_use_polyhaven:
        from .integrations import polyhaven
        handlers.update({
            "get_polyhaven_categories": polyhaven.get_categories,
            "search_polyhaven_assets": polyhaven.search_assets,
            "download_polyhaven_asset": polyhaven.download_asset,
            "set_texture": set_texture,
        })

    # Add Hyper3d handlers only if enabled
    if bpy.context.scene.blendermcp_use_hyper3d:
        from .integrations import hyper3d
        handlers.update({
            "create_rodin_job": hyper3d.create_job,
            "poll_rodin_job_status": hyper3d.poll_job_status,
            "import_generated_asset": hyper3d.import_asset,
        })

    # Add Sketchfab handlers only if enabled
    if bpy.context.scene.blendermcp_use_sketchfab:
        from .integrations import sketchfab
        handlers.update({
            "search_sketchfab_models": sketchfab.search_models,
            "get_sketchfab_model_preview": sketchfab.get_model_preview,
            "download_sketchfab_model": sketchfab.download_model,
        })

    # Add Hunyuan3d handlers only if enabled
    if bpy.context.scene.blendermcp_use_hunyuan3d:
        from .integrations import hunyuan3d
        handlers.update({
            "create_hunyuan_job": hunyuan3d.create_job,
            "poll_hunyuan_job_status": hunyuan3d.poll_job_status,
            "import_generated_asset_hunyuan": hunyuan3d.import_asset,
        })

    return handlers


def get_scene_info() -> Dict[str, Any]:
    """Get information about the current Blender scene."""
    try:
        print("Getting scene info...")
        scene_info: Dict[str, Any] = {
            "name": bpy.context.scene.name,
            "object_count": len(bpy.context.scene.objects),
            "objects": [],
            "materials_count": len(bpy.data.materials),
        }

        # Collect minimal object information (limit to first 10 objects)
        for i, obj in enumerate(bpy.context.scene.objects):
            if i >= 10:
                break

            obj_info: Dict[str, Any] = {
                "name": obj.name,
                "type": obj.type,
                "location": [
                    round(float(obj.location.x), 2),
                    round(float(obj.location.y), 2),
                    round(float(obj.location.z), 2),
                ],
            }
            scene_info["objects"].append(obj_info)

        print(f"Scene info collected: {len(scene_info['objects'])} objects")
        return scene_info
    except Exception as e:
        print(f"Error in get_scene_info: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}


def _get_aabb(obj: bpy.types.Object) -> list:
    """Return the world-space axis-aligned bounding box (AABB) of an object.

    Args:
        obj: Blender object to get AABB for.

    Returns:
        List containing min and max corners of the bounding box.

    Raises:
        TypeError: If object is not a mesh.
    """
    if obj.type != 'MESH':
        raise TypeError("Object must be a mesh")

    # Get the bounding box corners in local space
    local_bbox_corners = [mathutils.Vector(corner) for corner in obj.bound_box]

    # Convert to world coordinates
    world_bbox_corners = [obj.matrix_world @ corner for corner in local_bbox_corners]

    # Compute axis-aligned min/max coordinates
    min_corner = mathutils.Vector(map(min, zip(*world_bbox_corners)))
    max_corner = mathutils.Vector(map(max, zip(*world_bbox_corners)))

    return [[*min_corner], [*max_corner]]


def get_object_info(name: str) -> Dict[str, Any]:
    """Get detailed information about a specific object.

    Args:
        name: Name of the object to get info for.

    Returns:
        Dictionary containing object information.

    Raises:
        ValueError: If object not found.
    """
    obj = bpy.data.objects.get(name)
    if not obj:
        raise ValueError(f"Object not found: {name}")

    obj_info: Dict[str, Any] = {
        "name": obj.name,
        "type": obj.type,
        "location": [obj.location.x, obj.location.y, obj.location.z],
        "rotation": [obj.rotation_euler.x, obj.rotation_euler.y, obj.rotation_euler.z],
        "scale": [obj.scale.x, obj.scale.y, obj.scale.z],
        "visible": obj.visible_get(),
        "materials": [],
    }

    if obj.type == "MESH":
        bounding_box = _get_aabb(obj)
        obj_info["world_bounding_box"] = bounding_box

    # Add material slots
    for slot in obj.material_slots:
        if slot.material:
            obj_info["materials"].append(slot.material.name)

    # Add mesh data if applicable
    if obj.type == 'MESH' and obj.data:
        mesh = obj.data
        obj_info["mesh"] = {
            "vertices": len(mesh.vertices),
            "edges": len(mesh.edges),
            "polygons": len(mesh.polygons),
        }

    return obj_info


def get_viewport_screenshot(max_size: int = 800, filepath: Optional[str] = None, format: str = "png") -> Dict[str, Any]:
    """Capture a screenshot of the current 3D viewport.

    Args:
        max_size: Maximum size in pixels for the largest dimension.
        filepath: Path where to save the screenshot file.
        format: Image format (png, jpg, etc.).

    Returns:
        Dictionary with success status and image info.
    """
    try:
        if not filepath:
            return {"error": "No filepath provided"}

        # Find the active 3D viewport
        area = None
        for a in bpy.context.screen.areas:
            if a.type == 'VIEW_3D':
                area = a
                break

        if not area:
            return {"error": "No 3D viewport found"}

        # Find a region within the area (WINDOW region is required for screenshot_area)
        region = None
        for r in area.regions:
            if r.type == 'WINDOW':
                region = r
                break

        if not region:
            return {"error": "No WINDOW region found in 3D viewport"}

        # Take screenshot with proper context override (needs both area and region)
        with bpy.context.temp_override(area=area, region=region):
            bpy.ops.screen.screenshot_area(filepath=filepath)

        # Load and resize if needed
        img = bpy.data.images.load(filepath)
        width, height = img.size

        if max(width, height) > max_size:
            scale = max_size / max(width, height)
            new_width = int(width * scale)
            new_height = int(height * scale)
            img.scale(new_width, new_height)

            img.file_format = format.upper()
            img.save()
            width, height = new_width, new_height

        # Cleanup Blender image data
        bpy.data.images.remove(img)

        return {
            "success": True,
            "width": width,
            "height": height,
            "filepath": filepath
        }

    except Exception as e:
        return {"error": str(e)}


def execute_code(code: str) -> Dict[str, Any]:
    """Execute arbitrary Blender Python code.

    Args:
        code: Python code to execute.

    Returns:
        Dictionary with execution status and output.

    Raises:
        Exception: If code execution fails.
    """
    try:
        # Create a local namespace for execution
        namespace = {"bpy": bpy}

        # Capture stdout during execution
        capture_buffer = io.StringIO()
        with contextlib.redirect_stdout(capture_buffer):
            exec(code, namespace)

        captured_output = capture_buffer.getvalue()
        return {"executed": True, "result": captured_output}
    except Exception as e:
        raise Exception(f"Code execution error: {str(e)}")


def get_telemetry_consent() -> Dict[str, Any]:
    """Get the user's telemetry consent preference.

    Returns:
        Dictionary with consent status.
    """
    return {
        "consent": bpy.context.scene.blendermcp_telemetry_consent
    }


def get_polyhaven_status() -> Dict[str, Any]:
    """Get the current status of Poly Haven integration."""
    enabled = bpy.context.scene.blendermcp_use_polyhaven
    if enabled:
        return {
            "enabled": True,
            "message": "Poly Haven integration is enabled and ready to use."
        }
    else:
        return {
            "enabled": False,
            "message": """Poly Haven integration is currently disabled. To enable it:
                        1. In the 3D Viewport, find the BlenderMCP panel in the sidebar (press N if hidden)
                        2. Check the 'Use Poly Haven' checkbox
                        3. Restart the connection to Claude"""
        }


def get_hyper3d_status() -> Dict[str, Any]:
    """Get the current status of Hyper3D Rodin integration."""
    from .server import get_rodin_free_trial_key

    enabled = bpy.context.scene.blendermcp_use_hyper3d
    if enabled:
        if not bpy.context.scene.blendermcp_hyper3d_api_key:
            return {
                "enabled": False,
                "message": """Hyper3D Rodin integration is currently enabled, but API key is not given. To enable it:
                            1. In the 3D Viewport, find the BlenderMCP panel in the sidebar (press N if hidden)
                            2. Keep the 'Use Hyper3D Rodin 3D model generation' checkbox checked
                            3. Choose the right platform and fill in the API Key
                            4. Restart the connection to Claude"""
            }
        mode = bpy.context.scene.blendermcp_hyper3d_mode
        message = f"Hyper3D Rodin integration is enabled and ready to use. Mode: {mode}. " + \
            f"Key type: {'private' if bpy.context.scene.blendermcp_hyper3d_api_key != get_rodin_free_trial_key() else 'free_trial'}"
        return {
            "enabled": True,
            "message": message
        }
    else:
        return {
            "enabled": False,
            "message": """Hyper3D Rodin integration is currently disabled. To enable it:
                        1. In the 3D Viewport, find the BlenderMCP panel in the sidebar (press N if hidden)
                        2. Check the 'Use Hyper3D Rodin 3D model generation' checkbox
                        3. Restart the connection to Claude"""
        }


def get_sketchfab_status() -> Dict[str, Any]:
    """Get the current status of Sketchfab integration."""
    enabled = bpy.context.scene.blendermcp_use_sketchfab
    if enabled:
        return {
            "enabled": True,
            "message": "Sketchfab integration is enabled and ready to use."
        }
    else:
        return {
            "enabled": False,
            "message": """Sketchfab integration is currently disabled. To enable it:
                        1. In the 3D Viewport, find the BlenderMCP panel in the sidebar (press N if hidden)
                        2. Check the 'Use Sketchfab' checkbox
                        3. Restart the connection to Claude"""
        }


def get_hunyuan3d_status() -> Dict[str, Any]:
    """Get the current status of Hunyuan3D integration."""
    enabled = bpy.context.scene.blendermcp_use_hunyuan3d
    if enabled:
        mode = bpy.context.scene.blendermcp_hunyuan3d_mode
        message = f"Hunyuan3D integration is enabled. Mode: {mode}."
        return {
            "enabled": True,
            "message": message
        }
    else:
        return {
            "enabled": False,
            "message": """Hunyuan3D integration is currently disabled. To enable it:
                        1. In the 3D Viewport, find the BlenderMCP panel in the sidebar (press N if hidden)
                        2. Check the 'Use Tencent Hunyuan 3D model generation' checkbox
                        3. Restart the connection to Claude"""
        }


def set_texture(object_name: str, texture_id: str) -> Dict[str, Any]:
    """Apply a previously downloaded Polyhaven texture to an object.

    Args:
        object_name: Name of the object to apply texture to.
        texture_id: ID of the texture to apply.

    Returns:
        Dictionary with operation result.
    """
    try:
        # Get the object
        obj = bpy.data.objects.get(object_name)
        if not obj:
            return {"error": f"Object not found: {object_name}"}

        # Make sure object can accept materials
        if not hasattr(obj, 'data') or not hasattr(obj.data, 'materials'):
            return {"error": f"Object {object_name} cannot accept materials"}

        # Find all images related to this texture
        texture_images = {}
        for img in bpy.data.images:
            if img.name.startswith(texture_id + "_"):
                map_type = img.name.split('_')[-1].split('.')[0]
                img.reload()

                # Set color space
                if map_type.lower() in ['color', 'diffuse', 'albedo']:
                    try:
                        img.colorspace_settings.name = 'sRGB'
                    except Exception:
                        pass
                else:
                    try:
                        img.colorspace_settings.name = 'Non-Color'
                    except Exception:
                        pass

                if not img.packed_file:
                    img.pack()

                texture_images[map_type] = img

        if not texture_images:
            return {"error": f"No texture images found for: {texture_id}"}

        # Create a new material
        new_mat_name = f"{texture_id}_material_{object_name}"

        existing_mat = bpy.data.materials.get(new_mat_name)
        if existing_mat:
            bpy.data.materials.remove(existing_mat)

        new_mat = bpy.data.materials.new(name=new_mat_name)
        new_mat.use_nodes = True

        nodes = new_mat.node_tree.nodes
        links = new_mat.node_tree.links
        nodes.clear()

        # Create output node
        output = nodes.new(type='ShaderNodeOutputMaterial')
        output.location = (600, 0)

        # Create principled BSDF node
        principled = nodes.new(type='ShaderNodeBsdfPrincipled')
        principled.location = (300, 0)
        links.new(principled.outputs[0], output.inputs[0])

        # Add texture coordinate and mapping
        tex_coord = nodes.new(type='ShaderNodeTexCoord')
        tex_coord.location = (-800, 0)

        mapping = nodes.new(type='ShaderNodeMapping')
        mapping.location = (-600, 0)
        mapping.vector_type = 'TEXTURE'
        links.new(tex_coord.outputs['UV'], mapping.inputs['Vector'])

        return {
            "success": True,
            "material": new_mat_name,
            "maps": list(texture_images.keys()),
            "material_info": {
                "node_count": len(nodes),
                "has_nodes": True,
                "texture_nodes": []
            }
        }

    except Exception as e:
        return {"error": str(e)}

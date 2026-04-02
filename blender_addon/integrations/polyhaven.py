"""
Poly Haven integration for Blender MCP.

This module provides functions to interact with the Poly Haven API for
downloading HDRIs, textures, and 3D models.
"""

import os
import shutil
import tempfile
from typing import Dict, Any, Optional

import bpy
import requests


REQ_HEADERS = requests.utils.default_headers()
REQ_HEADERS.update({"User-Agent": "blender-mcp"})


def get_categories(asset_type: str) -> Dict[str, Any]:
    """Get categories for a specific asset type from Poly Haven.

    Args:
        asset_type: Type of asset (hdris, textures, models, all).

    Returns:
        Dictionary with categories or error.
    """
    try:
        if asset_type not in ["hdris", "textures", "models", "all"]:
            return {"error": f"Invalid asset type: {asset_type}. Must be one of: hdris, textures, models, all"}

        response = requests.get(
            f"https://api.polyhaven.com/categories/{asset_type}",
            headers=REQ_HEADERS
        )
        if response.status_code == 200:
            return {"categories": response.json()}
        else:
            return {"error": f"API request failed: {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}


def search_assets(asset_type: Optional[str] = None,
                  categories: Optional[str] = None) -> Dict[str, Any]:
    """Search for assets from Poly Haven.

    Args:
        asset_type: Type of asset (hdris, textures, models).
        categories: Filter by categories.

    Returns:
        Dictionary with search results.
    """
    try:
        url = "https://api.polyhaven.com/assets"
        params = {}

        if asset_type and asset_type != "all":
            if asset_type not in ["hdris", "textures", "models"]:
                return {"error": f"Invalid asset type: {asset_type}. Must be one of: hdris, textures, models, all"}
            params["type"] = asset_type

        if categories:
            params["categories"] = categories

        response = requests.get(url, params=params, headers=REQ_HEADERS)
        if response.status_code == 200:
            assets = response.json()
            # Return first 20 assets
            limited_assets = {}
            for i, (key, value) in enumerate(assets.items()):
                if i >= 20:
                    break
                limited_assets[key] = value

            return {
                "assets": limited_assets,
                "total_count": len(assets),
                "returned_count": len(limited_assets)
            }
        else:
            return {"error": f"API request failed: {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}


def download_asset(asset_id: str, asset_type: str,
                   resolution: str = "1k",
                   file_format: Optional[str] = None) -> Dict[str, Any]:
    """Download an asset from Poly Haven.

    Args:
        asset_id: Poly Haven asset ID.
        asset_type: Type of asset (hdris, textures, models).
        resolution: Resolution to download (1k, 2k, 4k, 8k).
        file_format: File format (hdr, exr, jpg, png, gltf, etc.).

    Returns:
        Dictionary with download result.
    """
    try:
        # First get the files information
        files_response = requests.get(f"https://api.polyhaven.com/files/{asset_id}", headers=REQ_HEADERS)
        if files_response.status_code != 200:
            return {"error": f"Failed to get asset files: {files_response.status_code}"}

        files_data = files_response.json()

        # Handle different asset types
        if asset_type == "hdris":
            return _download_hdri(asset_id, files_data, resolution, file_format)
        elif asset_type == "textures":
            return _download_textures(asset_id, files_data, resolution, file_format)
        elif asset_type == "models":
            return _download_model(asset_id, files_data, resolution, file_format)
        else:
            return {"error": f"Unsupported asset type: {asset_type}"}

    except Exception as e:
        return {"error": f"Failed to download asset: {str(e)}"}


def _download_hdri(asset_id: str, files_data: dict, resolution: str, file_format: Optional[str]) -> Dict[str, Any]:
    """Download and set up an HDRI environment texture."""
    if not file_format:
        file_format = "hdr"

    if "hdri" not in files_data or resolution not in files_data["hdri"] or file_format not in files_data["hdri"][resolution]:
        return {"error": f"Requested resolution or format not available for this HDRI"}

    file_info = files_data["hdri"][resolution][file_format]
    file_url = file_info["url"]

    with tempfile.NamedTemporaryFile(suffix=f".{file_format}", delete=False) as tmp_file:
        response = requests.get(file_url, headers=REQ_HEADERS)
        if response.status_code != 200:
            return {"error": f"Failed to download HDRI: {response.status_code}"}
        tmp_file.write(response.content)
        tmp_path = tmp_file.name

    try:
        if not bpy.data.worlds:
            bpy.data.worlds.new("World")

        world = bpy.data.worlds[0]
        world.use_nodes = True
        node_tree = world.node_tree

        for node in node_tree.nodes:
            node_tree.nodes.remove(node)

        tex_coord = node_tree.nodes.new(type='ShaderNodeTexCoord')
        tex_coord.location = (-800, 0)

        mapping = node_tree.nodes.new(type='ShaderNodeMapping')
        mapping.location = (-600, 0)

        env_tex = node_tree.nodes.new(type='ShaderNodeTexEnvironment')
        env_tex.location = (-400, 0)
        env_tex.image = bpy.data.images.load(tmp_path)

        if file_format.lower() == 'exr':
            try:
                env_tex.image.colorspace_settings.name = 'Linear'
            except:
                env_tex.image.colorspace_settings.name = 'Non-Color'
        else:
            for color_space in ['Linear', 'Linear Rec.709', 'Non-Color']:
                try:
                    env_tex.image.colorspace_settings.name = color_space
                    break
                except:
                    continue

        background = node_tree.nodes.new(type='ShaderNodeBackground')
        background.location = (-200, 0)

        output = node_tree.nodes.new(type='ShaderNodeOutputWorld')
        output.location = (0, 0)

        node_tree.links.new(tex_coord.outputs['Generated'], mapping.inputs['Vector'])
        node_tree.links.new(mapping.outputs['Vector'], env_tex.inputs['Vector'])
        node_tree.links.new(env_tex.outputs['Color'], background.inputs['Color'])
        node_tree.links.new(background.outputs['Background'], output.inputs['Surface'])

        bpy.context.scene.world = world

        try:
            tempfile._cleanup()
        except:
            pass

        return {
            "success": True,
            "message": f"HDRI {asset_id} imported successfully",
            "image_name": env_tex.image.name
        }
    except Exception as e:
        return {"error": f"Failed to set up HDRI in Blender: {str(e)}"}


def _download_textures(asset_id: str, files_data: dict, resolution: str, file_format: Optional[str]) -> Dict[str, Any]:
    """Download and set up texture maps."""
    if not file_format:
        file_format = "jpg"

    downloaded_maps = {}

    try:
        for map_type in files_data:
            if map_type not in ["blend", "gltf"]:
                if resolution in files_data[map_type] and file_format in files_data[map_type][resolution]:
                    file_info = files_data[map_type][resolution][file_format]
                    file_url = file_info["url"]

                    with tempfile.NamedTemporaryFile(suffix=f".{file_format}", delete=False) as tmp_file:
                        response = requests.get(file_url, headers=REQ_HEADERS)
                        if response.status_code == 200:
                            tmp_file.write(response.content)
                            tmp_path = tmp_file.name

                            image = bpy.data.images.load(tmp_path)
                            image.name = f"{asset_id}_{map_type}.{file_format}"
                            image.pack()

                            if map_type in ['color', 'diffuse', 'albedo']:
                                try:
                                    image.colorspace_settings.name = 'sRGB'
                                except:
                                    pass
                            else:
                                try:
                                    image.colorspace_settings.name = 'Non-Color'
                                except:
                                    pass

                            downloaded_maps[map_type] = image

                            try:
                                os.unlink(tmp_path)
                            except:
                                pass

        if not downloaded_maps:
            return {"error": f"No texture maps found for the requested resolution and format"}

        mat = bpy.data.materials.new(name=asset_id)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links

        for node in nodes:
            nodes.remove(node)

        output = nodes.new(type='ShaderNodeOutputMaterial')
        output.location = (300, 0)

        principled = nodes.new(type='ShaderNodeBsdfPrincipled')
        principled.location = (0, 0)
        links.new(principled.outputs[0], output.inputs[0])

        tex_coord = nodes.new(type='ShaderNodeTexCoord')
        tex_coord.location = (-800, 0)

        mapping = nodes.new(type='ShaderNodeMapping')
        mapping.location = (-600, 0)
        mapping.vector_type = 'TEXTURE'
        links.new(tex_coord.outputs['UV'], mapping.inputs['Vector'])

        x_pos = -400
        y_pos = 300

        for map_type, image in downloaded_maps.items():
            tex_node = nodes.new(type='ShaderNodeTexImage')
            tex_node.location = (x_pos, y_pos)
            tex_node.image = image

            if map_type.lower() in ['color', 'diffuse', 'albedo']:
                try:
                    tex_node.image.colorspace_settings.name = 'sRGB'
                except:
                    pass
            else:
                try:
                    tex_node.image.colorspace_settings.name = 'Non-Color'
                except:
                    pass

            links.new(mapping.outputs['Vector'], tex_node.inputs['Vector'])

            if map_type.lower() in ['color', 'diffuse', 'albedo']:
                links.new(tex_node.outputs['Color'], principled.inputs['Base Color'])
            elif map_type.lower() in ['roughness', 'rough']:
                links.new(tex_node.outputs['Color'], principled.inputs['Roughness'])
            elif map_type.lower() in ['metallic', 'metalness', 'metal']:
                links.new(tex_node.outputs['Color'], principled.inputs['Metallic'])
            elif map_type.lower() in ['normal', 'nor']:
                normal_map = nodes.new(type='ShaderNodeNormalMap')
                normal_map.location = (x_pos + 200, y_pos)
                links.new(tex_node.outputs['Color'], normal_map.inputs['Color'])
                links.new(normal_map.outputs['Normal'], principled.inputs['Normal'])
            elif map_type.lower() in ['displacement', 'disp', 'height']:
                disp_node = nodes.new(type='ShaderNodeDisplacement')
                disp_node.location = (x_pos + 200, y_pos - 200)
                disp_node.inputs['Scale'].default_value = 0.1
                links.new(tex_node.outputs['Color'], disp_node.inputs['Height'])
                links.new(disp_node.outputs['Displacement'], output.inputs['Displacement'])

            y_pos -= 250

        return {
            "success": True,
            "message": f"Texture {asset_id} imported as material",
            "material": mat.name,
            "maps": list(downloaded_maps.keys())
        }

    except Exception as e:
        return {"error": f"Failed to process textures: {str(e)}"}


def _download_model(asset_id: str, files_data: dict, resolution: str, file_format: Optional[str]) -> Dict[str, Any]:
    """Download and import a 3D model."""
    if not file_format:
        file_format = "gltf"

    if file_format not in files_data or resolution not in files_data[file_format]:
        return {"error": f"Requested format or resolution not available for this model"}

    file_info = files_data[file_format][resolution][file_format]
    file_url = file_info["url"]

    temp_dir = tempfile.mkdtemp()
    main_file_path = ""

    try:
        main_file_name = file_url.split("/")[-1]
        main_file_path = os.path.join(temp_dir, main_file_name)

        response = requests.get(file_url, headers=REQ_HEADERS)
        if response.status_code != 200:
            return {"error": f"Failed to download model: {response.status_code}"}

        with open(main_file_path, "wb") as f:
            f.write(response.content)

        if "include" in file_info and file_info["include"]:
            for include_path, include_info in file_info["include"].items():
                include_url = include_info["url"]
                include_file_path = os.path.join(temp_dir, include_path)
                os.makedirs(os.path.dirname(include_file_path), exist_ok=True)

                include_response = requests.get(include_url, headers=REQ_HEADERS)
                if include_response.status_code == 200:
                    with open(include_file_path, "wb") as f:
                        f.write(include_response.content)

        if file_format == "gltf" or file_format == "glb":
            bpy.ops.import_scene.gltf(filepath=main_file_path)
        elif file_format == "fbx":
            bpy.ops.import_scene.fbx(filepath=main_file_path)
        elif file_format == "obj":
            bpy.ops.import_scene.obj(filepath=main_file_path)
        elif file_format == "blend":
            with bpy.data.libraries.load(main_file_path, link=False) as (data_from, data_to):
                data_to.objects = data_from.objects
            for obj in data_to.objects:
                if obj is not None:
                    bpy.context.collection.objects.link(obj)
        else:
            return {"error": f"Unsupported model format: {file_format}"}

        imported_objects = [obj.name for obj in bpy.context.selected_objects]

        return {
            "success": True,
            "message": f"Model {asset_id} imported successfully",
            "imported_objects": imported_objects
        }
    except Exception as e:
        return {"error": f"Failed to import model: {str(e)}"}
    finally:
        try:
            shutil.rmtree(temp_dir)
        except:
            pass

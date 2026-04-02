"""
Sketchfab integration for Blender MCP.

This module provides functions to interact with the Sketchfab API for
searching and downloading 3D models.
"""

import base64
import json
import os
import shutil
import tempfile
import zipfile
from typing import Dict, Any, Optional
from contextlib import suppress

import bpy
import mathutils
import requests


def search_models(query: str,
                  categories: Optional[str] = None,
                  count: int = 20,
                  downloadable: bool = True) -> Dict[str, Any]:
    """Search for models on Sketchfab.

    Args:
        query: Search query string.
        categories: Comma-separated category filters.
        count: Maximum number of results.
        downloadable: Only include downloadable models.

    Returns:
        Dictionary with search results.
    """
    try:
        api_key = bpy.context.scene.blendermcp_sketchfab_api_key
        if not api_key:
            return {"error": "Sketchfab API key is not configured"}

        params = {
            "type": "models",
            "q": query,
            "count": count,
            "downloadable": downloadable,
            "archives_flavours": False
        }

        if categories:
            params["categories"] = categories

        headers = {"Authorization": f"Token {api_key}"}

        response = requests.get(
            "https://api.sketchfab.com/v3/search",
            headers=headers,
            params=params,
            timeout=30
        )

        if response.status_code == 401:
            return {"error": "Authentication failed (401). Check your API key."}

        if response.status_code != 200:
            return {"error": f"API request failed: {response.status_code}"}

        response_data = response.json()

        if response_data is None:
            return {"error": "Received empty response from Sketchfab API"}

        results = response_data.get("results", [])
        if not isinstance(results, list):
            return {"error": f"Unexpected response format: {response_data}"}

        return response_data

    except requests.exceptions.Timeout:
        return {"error": "Request timed out. Check your internet connection."}
    except json.JSONDecodeError as e:
        return {"error": f"Invalid JSON response: {str(e)}"}
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}


def get_model_preview(uid: str) -> Dict[str, Any]:
    """Get thumbnail preview of a Sketchfab model.

    Args:
        uid: Sketchfab model UID.

    Returns:
        Dictionary with preview image data.
    """
    try:
        api_key = bpy.context.scene.blendermcp_sketchfab_api_key
        if not api_key:
            return {"error": "Sketchfab API key is not configured"}

        headers = {"Authorization": f"Token {api_key}"}

        response = requests.get(
            f"https://api.sketchfab.com/v3/models/{uid}",
            headers=headers,
            timeout=30
        )

        if response.status_code == 401:
            return {"error": "Authentication failed (401). Check your API key."}
        if response.status_code == 404:
            return {"error": f"Model not found: {uid}"}
        if response.status_code != 200:
            return {"error": f"Failed to get model info: {response.status_code}"}

        data = response.json()
        thumbnails = data.get("thumbnails", {}).get("images", [])

        if not thumbnails:
            return {"error": "No thumbnail available for this model"}

        # Find suitable thumbnail
        selected_thumbnail = None
        for thumb in thumbnails:
            width = thumb.get("width", 0)
            if 400 <= width <= 800:
                selected_thumbnail = thumb
                break

        if not selected_thumbnail:
            selected_thumbnail = thumbnails[0]

        thumbnail_url = selected_thumbnail.get("url")
        if not thumbnail_url:
            return {"error": "Thumbnail URL not found"}

        img_response = requests.get(thumbnail_url, timeout=30)
        if img_response.status_code != 200:
            return {"error": f"Failed to download thumbnail: {img_response.status_code}"}

        image_data = base64.b64encode(img_response.content).decode('ascii')

        content_type = img_response.headers.get("Content-Type", "")
        if "png" in content_type or thumbnail_url.endswith(".png"):
            img_format = "png"
        else:
            img_format = "jpeg"

        return {
            "success": True,
            "image_data": image_data,
            "format": img_format,
            "model_name": data.get("name", "Unknown"),
            "author": data.get("user", {}).get("username", "Unknown"),
            "uid": uid,
            "thumbnail_width": selected_thumbnail.get("width"),
            "thumbnail_height": selected_thumbnail.get("height")
        }

    except requests.exceptions.Timeout:
        return {"error": "Request timed out."}
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": f"Failed to get model preview: {str(e)}"}


def download_model(uid: str,
                   normalize_size: bool = False,
                   target_size: float = 1.0) -> Dict[str, Any]:
    """Download a model from Sketchfab.

    Args:
        uid: Sketchfab model UID.
        normalize_size: Scale model to target_size.
        target_size: Target size for largest dimension.

    Returns:
        Dictionary with download result.
    """
    try:
        api_key = bpy.context.scene.blendermcp_sketchfab_api_key
        if not api_key:
            return {"error": "Sketchfab API key is not configured"}

        headers = {"Authorization": f"Token {api_key}"}
        download_endpoint = f"https://api.sketchfab.com/v3/models/{uid}/download"

        response = requests.get(download_endpoint, headers=headers, timeout=30)

        if response.status_code == 401:
            return {"error": "Authentication failed (401). Check your API key."}
        if response.status_code != 200:
            return {"error": f"Download request failed: {response.status_code}"}

        data = response.json()
        if data is None:
            return {"error": "Received empty response from Sketchfab API"}

        gltf_data = data.get("gltf")
        if not gltf_data:
            return {"error": "No gltf download available. Response: " + str(data)}

        download_url = gltf_data.get("url")
        if not download_url:
            return {"error": "No download URL available"}

        model_response = requests.get(download_url, timeout=60)
        if model_response.status_code != 200:
            return {"error": f"Model download failed: {model_response.status_code}"}

        # Save and extract
        temp_dir = tempfile.mkdtemp()
        zip_file_path = os.path.join(temp_dir, f"{uid}.zip")

        with open(zip_file_path, "wb") as f:
            f.write(model_response.content)

        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            for file_info in zip_ref.infolist():
                file_path = file_info.filename
                target_path = os.path.join(temp_dir, os.path.normpath(file_path))

                abs_temp_dir = os.path.abspath(temp_dir)
                abs_target_path = os.path.abspath(target_path)

                if not abs_target_path.startswith(abs_temp_dir):
                    with suppress(Exception):
                        shutil.rmtree(temp_dir)
                    return {"error": "Security issue: Zip contains path traversal"}

                if ".." in file_path:
                    with suppress(Exception):
                        shutil.rmtree(temp_dir)
                    return {"error": "Security issue: Zip contains directory traversal"}

            zip_ref.extractall(temp_dir)

        gltf_files = [f for f in os.listdir(temp_dir) if f.endswith('.gltf') or f.endswith('.glb')]
        if not gltf_files:
            with suppress(Exception):
                shutil.rmtree(temp_dir)
            return {"error": "No glTF file found in downloaded model"}

        main_file = os.path.join(temp_dir, gltf_files[0])
        bpy.ops.import_scene.gltf(filepath=main_file)

        imported_objects = list(bpy.context.selected_objects)
        imported_object_names = [obj.name for obj in imported_objects]

        with suppress(Exception):
            shutil.rmtree(temp_dir)

        # Calculate bounding box
        root_objects = [obj for obj in imported_objects if obj.parent is None]

        def get_all_mesh_children(obj):
            meshes = []
            if obj.type == 'MESH':
                meshes.append(obj)
            for child in obj.children:
                meshes.extend(get_all_mesh_children(child))
            return meshes

        all_meshes = []
        for obj in root_objects:
            all_meshes.extend(get_all_mesh_children(obj))

        if all_meshes:
            all_min = mathutils.Vector((float('inf'), float('inf'), float('inf')))
            all_max = mathutils.Vector((float('-inf'), float('-inf'), float('-inf')))

            for mesh_obj in all_meshes:
                for corner in mesh_obj.bound_box:
                    world_corner = mesh_obj.matrix_world @ mathutils.Vector(corner)
                    all_min.x = min(all_min.x, world_corner.x)
                    all_min.y = min(all_min.y, world_corner.y)
                    all_min.z = min(all_min.z, world_corner.z)
                    all_max.x = max(all_max.x, world_corner.x)
                    all_max.y = max(all_max.y, world_corner.y)
                    all_max.z = max(all_max.z, world_corner.z)

            dimensions = [
                all_max.x - all_min.x,
                all_max.y - all_min.y,
                all_max.z - all_min.z
            ]
            max_dimension = max(dimensions)

            scale_applied = 1.0
            if normalize_size and max_dimension > 0:
                scale_factor = target_size / max_dimension
                scale_applied = scale_factor

                for root in root_objects:
                    root.scale = (
                        root.scale.x * scale_factor,
                        root.scale.y * scale_factor,
                        root.scale.z * scale_factor
                    )

                bpy.context.view_layer.update()

            world_bounding_box = [[all_min.x, all_min.y, all_min.z], [all_max.x, all_max.y, all_max.z]]
        else:
            world_bounding_box = None
            dimensions = None
            scale_applied = 1.0

        result = {
            "success": True,
            "message": "Model imported successfully",
            "imported_objects": imported_object_names
        }

        if world_bounding_box:
            result["world_bounding_box"] = world_bounding_box
        if dimensions:
            result["dimensions"] = [round(d, 4) for d in dimensions]
        if normalize_size:
            result["scale_applied"] = round(scale_applied, 6)
            result["normalized"] = True

        return result

    except requests.exceptions.Timeout:
        return {"error": "Request timed out."}
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": f"Failed to download model: {str(e)}"}

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
            return {"error": f"Invalid asset type: {asset_type}"}

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
                return {"error": f"Invalid asset type: {asset_type}"}
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

    Note: This is a stub implementation. The full implementation would be
    in the original addon.py file.

    Args:
        asset_id: Poly Haven asset ID.
        asset_type: Type of asset (hdris, textures, models).
        resolution: Resolution to download (1k, 2k, 4k, 8k).
        file_format: File format (hdr, exr, jpg, png, gltf, etc.).

    Returns:
        Dictionary with download result.
    """
    # This is a placeholder - the actual implementation is in addon.py
    # To keep the modular structure clean, this function would contain
    # the full download logic from the original addon.py
    return {"error": "Not implemented - use original addon.py for now"}

"""
Hyper3D Rodin integration for Blender MCP.

This module provides functions to interact with the Hyper3D Rodin API for
AI-generated 3D models.
"""

from typing import Dict, Any, Optional

import bpy


def create_job(text_prompt: Optional[str] = None,
               images: Optional[list] = None,
               bbox_condition: Optional[list] = None) -> Dict[str, Any]:
    """Create a new Hyper3D Rodin generation job.

    Note: This is a stub implementation.

    Args:
        text_prompt: Text description for generation.
        images: List of images for image-to-image generation.
        bbox_condition: Bounding box condition for aspect ratio.

    Returns:
        Dictionary with job creation result.
    """
    return {"error": "Not implemented - use original addon.py for now"}


def poll_job_status(subscription_key: Optional[str] = None,
                    request_id: Optional[str] = None) -> Dict[str, Any]:
    """Poll the status of a Hyper3D Rodin job.

    Note: This is a stub implementation.

    Args:
        subscription_key: Subscription key for main site mode.
        request_id: Request ID for fal.ai mode.

    Returns:
        Dictionary with job status.
    """
    return {"error": "Not implemented - use original addon.py for now"}


def import_asset(name: str,
                 task_uuid: Optional[str] = None,
                 request_id: Optional[str] = None) -> Dict[str, Any]:
    """Import a generated Hyper3D asset into Blender.

    Note: This is a stub implementation.

    Args:
        name: Name for the imported object.
        task_uuid: Task UUID for main site mode.
        request_id: Request ID for fal.ai mode.

    Returns:
        Dictionary with import result.
    """
    return {"error": "Not implemented - use original addon.py for now"}

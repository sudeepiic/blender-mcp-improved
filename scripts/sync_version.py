#!/usr/bin/env python3
"""Sync version across all project files.

Run this script after updating the version in pyproject.toml to ensure
all files have consistent version information.
"""

import re
import sys
from pathlib import Path


def get_version_from_pyproject() -> str:
    """Extract version from pyproject.toml."""
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
    content = pyproject_path.read_text()
    match = re.search(r'version = "(\d+\.\d+\.\d+)"', content)
    if not match:
        raise ValueError("Version not found in pyproject.toml")
    return match.group(1)


def update_init_file(version: str) -> None:
    """Update __init__.py with new version."""
    init_path = Path(__file__).parent.parent / "src" / "blender_mcp" / "__init__.py"
    content = init_path.read_text()
    content = re.sub(r'__version__ = "[^"]+"', f'__version__ = "{version}"', content)
    init_path.write_text(content)
    print(f"Updated src/blender_mcp/__init__.py -> {version}")


def update_blender_addon(version: str) -> None:
    """Update addon.py bl_info version."""
    addon_path = Path(__file__).parent.parent / "addon.py"
    content = addon_path.read_text()

    # Parse version (e.g., "1.5.5" -> (1, 5, 5))
    major, minor, patch = version.split(".")
    version_tuple = f"({major}, {minor}, {patch})"

    content = re.sub(
        r'"version": \(\d+, \d+, \d+\)',
        f'"version": {version_tuple}',
        content
    )
    addon_path.write_text(content)
    print(f"Updated addon.py bl_info -> {version_tuple}")


def main() -> int:
    """Main entry point."""
    try:
        version = get_version_from_pyproject()
        print(f"Current version: {version}")

        update_init_file(version)
        update_blender_addon(version)

        print("\nVersion sync complete!")
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

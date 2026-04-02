#!/bin/bash
# Blender MCP - Quick Setup Script

set -e

echo "=========================================="
echo "Blender MCP - Quick Setup"
echo "=========================================="
echo ""

# Check dependencies
echo "1. Checking dependencies..."

if ! command -v uv &> /dev/null; then
    echo "   Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi
echo "   ✓ uv found"

if ! command -v blender &> /dev/null; then
    echo "   ⚠ Blender not found in PATH"
    echo "   You'll need to install Blender manually"
fi

echo ""
echo "2. Installing MCP server..."
uv pip install -e blender-mcp

echo ""
echo "3. Downloading Blender addon..."
ADDON_DIR="$HOME/.config/blender/addons"
mkdir -p "$ADDON_DIR"

if [ -f "addon.py" ]; then
    cp addon.py "$ADDON_DIR/blender_mcp.py"
    echo "   ✓ addon.py copied to $ADDON_DIR"
else
    echo "   ⚠ addon.py not found in current directory"
    echo "   Download from: https://github.com/sudeepiic/blender-mcp-improved"
fi

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Open Blender"
echo "2. Go to Edit → Preferences → Add-ons"
echo "3. Click 'Install...' and select:"
echo "   $ADDON_DIR/blender_mcp.py"
echo "4. Enable 'Interface: Blender MCP'"
echo "5. In 3D View sidebar (press N), find 'BlenderMCP' tab"
echo "6. Click 'Connect to Claude'"
echo ""
echo "To configure Claude Desktop, edit:"
echo "   ~/.config/Claude/claude_desktop_config.json"
echo ""
echo "Add:"
echo '  "mcpServers": {'
echo '    "blender": {'
echo '      "command": "uvx",'
echo '      "args": ["blender-mcp"]'
echo '    }'
echo '  }'
echo ""

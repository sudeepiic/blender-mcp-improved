# Blender MCP - Installation Guide

## Quick Install

### Option 1: Use the Improved `addon.py` (Recommended)

The original `addon.py` has been improved with security fixes and is fully functional:

```bash
# Download the improved addon
wget https://raw.githubusercontent.com/sudeepiic/blender-mcp-improved/main/addon.py -O blender_mcp.py

# Or with curl
curl -o blender_mcp.py https://raw.githubusercontent.com/sudeepiic/blender-mcp-improved/main/addon.py
```

**Then in Blender:**
1. **Edit → Preferences → Add-ons**
2. Click **"Install..."**
3. Select `blender_mcp.py`
4. Enable **"Interface: Blender MCP"**

**To connect:**
- Press **N** in Blender to open sidebar
- Find **"BlenderMCP"** tab
- Click **"Connect to Claude"**

### Option 2: Install from Source

```bash
# Clone the repository
git clone https://github.com/sudeepiic/blender-mcp-improved.git
cd blender-mcp-improved

# Install the MCP server
uv pip install -e .
```

## Configure Claude Desktop

Edit `~/.config/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "blender": {
      "command": "uvx",
      "args": ["blender-mcp"]
    }
  }
}
```

## Environment Variables

```bash
# Connection settings (optional)
export BLENDER_HOST="localhost"
export BLENDER_PORT="9876"

# Disable telemetry (optional)
export DISABLE_TELEMETRY="true"

# Hyper3D API key override (optional)
export RODIN_FREE_TRIAL_KEY="your-key-here"
```

## Features

- ✅ **Scene inspection**: Get info about objects, materials, cameras
- ✅ **Object manipulation**: Create, modify, delete 3D objects
- ✅ **Python execution**: Run arbitrary Python in Blender
- ✅ **Poly Haven**: Download HDRIs, textures, and 3D models
- ✅ **Sketchfab**: Search and download Sketchfab models
- ✅ **Hyper3D Rodin**: AI-generated 3D models
- ✅ **Hunyuan3D**: Tencent's 3D model generation
- ✅ **Viewport screenshots**: Capture Blender viewport
- ✅ **Telemetry control**: Opt out of data collection

## Troubleshooting

### "Not connected to Blender"
- Make sure the addon is installed in Blender
- Click "Connect to Claude" in the Blender sidebar
- Check the port matches (default: 9876)

### Port already in use
- Change port in Blender sidebar
- Or set: `export BLENDER_PORT=9877`

### API key errors
- For Hyper3D: Set `RODIN_FREE_TRIAL_KEY` environment variable
- For Sketchfab: Enter your API key in the Blender sidebar

## Development Setup

For contributing to the project:

```bash
# Run tests
uv run pytest tests/

# Run all checks
./tests/run_all_tests.sh

# Format code
uv run black src/ tests/
```

## Links

- **Repository**: https://github.com/sudeepiic/blender-mcp-improved
- **Original**: https://github.com/ahujasid/blender-mcp
- **Issues**: https://github.com/sudeepiic/blender-mcp-improved/issues

## What's Improved?

- 🔒 Security: Hardcoded API key now reads from environment
- 📝 Type hints: Added to server.py for better IDE support
- 🧪 Tests: Comprehensive test suite with pytest
- 🔧 Dev tools: Pre-commit hooks, Makefile, linters
- 📚 Documentation: CONTRIBUTING.md, INSTALL.md
- 🏗️ Modular structure: Separated concerns for maintainability

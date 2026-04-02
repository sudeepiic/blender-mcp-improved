# Blender MCP - Installation Guide

## Quick Install

### 1. Install the MCP Server

```bash
# Using uv (recommended)
uv pip install git+https://github.com/sudeepiic/blender-mcp-improved.git

# Or clone and install
git clone https://github.com/sudeepiic/blender-mcp-improved.git
cd blender-mcp-improved
uv pip install -e .
```

### 2. Install the Blender Addon

1. Download `addon.py` from the repository
2. Open Blender
3. Go to **Edit → Preferences → Add-ons**
4. Click **"Install..."** and select `addon.py`
5. Enable **"Interface: Blender MCP"**

### 3. Start the Connection

In Blender:
1. Press **N** to open the sidebar
2. Find the **"BlenderMCP"** tab
3. Click **"Connect to Claude"**

### 4. Configure Claude Desktop

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

## Environment Variables (Optional)

```bash
export BLENDER_HOST="localhost"  # Default
export BLENDER_PORT="9876"         # Default
export DISABLE_TELEMETRY="true"    # Disable telemetry
export RODIN_FREE_TRIAL_KEY="your-key"  # Hyper3D API key
```

## Verification

Once connected, you should see a hammer icon 🛠️ in Claude with Blender tools available.

## Troubleshooting

**"Not connected to Blender"**
- Make sure Blender addon is installed
- Click "Connect to Claude" in Blender sidebar
- Check Blender and Claude are both running

**Port already in use**
- Change port in Blender sidebar (e.g., 9877)
- Set `BLENDER_PORT=9877` environment variable

**For more help:** See [CONTRIBUTING.md](CONTRIBUTING.md)

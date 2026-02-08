---
description: Start ClawCat services (uses launcher scripts)
---

# Start ClawCat

This command starts ClawCat services. It uses platform-specific launcher scripts that automatically handle conda environment activation.

**Prerequisites**:

- **Conda** must be installed (recommended) or Python 3.8+ with dependencies installed
- Frontend files are already provided in the repository (no build needed)

**Note**: Services will run in the background. The ClawCat window will appear and stay open.

## Method 1: Using Service Manager (Recommended)

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/service_manager.py" start
```

This will:

1. Check and install Python dependencies (using conda if available)
2. Check port availability
3. Launch the window using platform-specific scripts

## Method 2: Direct Script Launch

You can also launch directly using the platform-specific scripts:

### Windows

```bash
"${CLAUDE_PLUGIN_ROOT}/scripts/start_window.bat"
```

### Unix/Linux/macOS

```bash
bash "${CLAUDE_PLUGIN_ROOT}/scripts/start_window.sh"
```

The launcher scripts will:

- Automatically detect and activate conda base environment
- Start the ClawCat window with all dependencies

## Alternative Commands

- **Direct Script**: `/clawcat:start_window` - Uses launcher scripts directly
- **EXE Version**: `/clawcat:start_exe` - Uses bundled executable (no dependencies needed)

## Dependency Installation

Python dependencies are automatically installed when you run `/clawcat:start` via `service_manager.py`. The script will use conda if available, otherwise use pip directly.

To stop ClawCat, use `/clawcat:stop` or press Ctrl+C in the terminal where it's running.

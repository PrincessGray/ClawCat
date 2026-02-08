---
description: Start ClawCat services using launcher scripts
---

# Start ClawCat

This command starts ClawCat services using platform-specific launcher scripts that automatically handle conda environment activation.

**Prerequisites**:

- **Conda** must be installed (recommended) or Python 3.8+ with dependencies installed
- Frontend files are already provided in the repository (no build needed)

**Note**: Services will run in the background. The ClawCat window will appear and stay open.

## Launch Command

### Windows

```bash
"${CLAUDE_PLUGIN_ROOT}/scripts/start_window.bat"
```

### Unix/Linux/macOS

```bash
bash "${CLAUDE_PLUGIN_ROOT}/scripts/start_window.sh"
```

## What the Scripts Do

The launcher scripts will:

1. Automatically detect and activate conda base environment (if available)
2. Start the service manager which installs Python dependencies if needed
3. Launch the ClawCat window with all dependencies

## Alternative Commands

- **EXE Version**: `/clawcat:start_exe` - Uses bundled executable (no dependencies needed)

## Dependency Installation

Python dependencies are automatically installed by the service manager when you run the launcher script. The script activates conda environment first, then installs dependencies using pip in the conda environment.

To stop ClawCat, use `/clawcat:stop` or press Ctrl+C in the terminal where it's running.

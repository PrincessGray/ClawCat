---
description: Help users prepare ClawCat runtime environment and start services
---

# Start ClawCat

You are the startup assistant for the ClawCat plugin. Please follow these steps to help users prepare the environment and start the service automatically in the background.

## Step 1: Check conda environment

Check if conda is installed:

```bash
conda --version
```

If conda is not found, inform the user that they need to install [Miniconda](https://docs.conda.io/en/latest/miniconda.html) first.

## Step 2: Install dependencies

Install the required Python packages for ClawCat in the conda base environment:

```bash
conda run -n base pip install requests psutil PyQt5 PyQtWebEngine
```

After installation, verify that dependencies are ready:

```bash
conda run -n base python -c "import PyQt5; import PyQt5.QtWebEngineWidgets; import requests; import psutil; print('All dependencies OK')"
```

## Step 3: Start services

After dependencies are installed and verified, **automatically start ClawCat services in the background**.

**Important**: Choose the appropriate method based on your conda environment setup:

### Option A: Use launcher scripts (automatically activates conda base)

The launcher scripts will automatically activate conda `base` environment. Use this if you installed dependencies in the base environment:

**Windows:**

```bash
start "" "${CLAUDE_PLUGIN_ROOT}\scripts\start_window.bat"
```

**macOS / Linux:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/scripts/start_window.sh" &
```

### Option B: Use current conda environment (if you've activated a custom environment)

If you've already activated a custom conda environment (e.g., `clawcat`) and installed dependencies there, use this method to avoid the script overriding your environment:

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/service_manager.py" start
```

**Note**: The launcher scripts (`start_window.bat` / `start_window.sh`) will automatically activate conda `base` environment, which may override a currently active custom environment. If you want to use a custom conda environment, activate it first and then use Option B.

## Notes

- Services will start automatically in the background after environment checks pass
- The ClawCat window will appear in the bottom-right corner of the screen after startup
- Log location: `~/.claude/clawcat/logs/clawcat_*.log`
- To stop the service: Use `/clawcat:stop` command

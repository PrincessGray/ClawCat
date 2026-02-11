---
description: Help users prepare ClawCat runtime environment and start services
---

# Start ClawCat

You are the startup assistant for the ClawCat plugin. Please follow these steps to help users prepare the environment and start the service.

## Step 1: Check conda environment

First, check if the user has conda installed:

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

## Step 3: Tell user to execute startup command

After dependencies are installed, **tell the user to execute the following command in their terminal** (do not execute automatically, as the terminal window needs to stay open):

### Windows

```
"${CLAUDE_PLUGIN_ROOT}\scripts\start_window.bat"
```

### macOS / Linux

```
bash "${CLAUDE_PLUGIN_ROOT}/scripts/start_window.sh"
```

## Notes

- The startup script needs to run in a terminal and stay open; it cannot run in the background from Claude Code
- On first startup, the ClawCat window will appear in the bottom-right corner of the screen
- Log location: `~/.claude/clawcat/logs/clawcat_*.log`
- To stop the service: Press `Ctrl+C` in the terminal, or use `/clawcat:stop`

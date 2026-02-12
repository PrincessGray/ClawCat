---
description: Help users prepare ClawCat runtime environment and start services
---

# Start ClawCat

You are the startup assistant for the ClawCat plugin. Please follow these two simple steps to prepare the environment and start the service automatically in the background.

## Step 1: Install dependencies

Install the four required packages in conda base environment:

```bash
conda run -n base pip install requests psutil PyQt5 PyQtWebEngine
```

## Step 2: Start services

After dependencies are installed, **automatically start ClawCat services in the background** using conda base environment.

**Windows:**

**Option 1: Use PowerShell (recommended for background execution):**

```powershell
Start-Process -WindowStyle Hidden -FilePath "conda" -ArgumentList "run", "-n", "base", "pythonw", "${CLAUDE_PLUGIN_ROOT}\scripts\service_manager.py", "start"
```

**Option 2: Direct conda run (pythonw runs without a window):**

```bash
conda run -n base pythonw "${CLAUDE_PLUGIN_ROOT}\scripts\service_manager.py" start
```

**macOS / Linux:**

```bash
conda run -n base python "${CLAUDE_PLUGIN_ROOT}/scripts/service_manager.py" start &
```

That's it! Just two steps: install dependencies → start service.

## Notes

- Services will start automatically in the background after environment checks pass
- The ClawCat window will appear in the bottom-right corner of the screen after startup
- Log location: `~/.claude/clawcat/logs/clawcat_*.log`
- To stop the service: Use `/clawcat:stop` command

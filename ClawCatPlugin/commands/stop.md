---
description: Help users stop ClawCat services
---

# Stop ClawCat

**You must automatically execute the stop command** to stop ClawCat services. Do not ask the user to run it manually.

**Important**: Use the same Python environment that was used to start ClawCat. Try conda base first, then fall back to system Python if conda is not available.

## Stop services

Execute the following command to stop all ClawCat services:

**Windows:**

```bash
conda run -n base python "${CLAUDE_PLUGIN_ROOT}\scripts\service_manager.py" stop
```

**macOS / Linux:**

```bash
conda run -n base python "${CLAUDE_PLUGIN_ROOT}/scripts/service_manager.py" stop
```

**If conda command fails** (e.g., conda not found or conda error), fall back to system Python:

**Windows:**

```bash
python "${CLAUDE_PLUGIN_ROOT}\scripts\service_manager.py" stop
```

**macOS / Linux:**

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/service_manager.py" stop
```

This will:

- Close the ClawCat window
- Stop the HTTP server
- Clean up all running processes

After executing, verify that services have been stopped by checking the status:

```bash
# Try conda first
conda run -n base python "${CLAUDE_PLUGIN_ROOT}/scripts/service_manager.py" status

# Or use system Python if conda fails
python "${CLAUDE_PLUGIN_ROOT}/scripts/service_manager.py" status
```

If services are still running, you may need to force stop them.

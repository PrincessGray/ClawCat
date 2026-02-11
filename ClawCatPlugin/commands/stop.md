---
description: Help users stop ClawCat services
---

# Stop ClawCat

## Method 1: Stop via terminal

Tell the user to press `Ctrl+C` in the terminal window where ClawCat is running.

## Method 2: Stop via command

If the user cannot find the original terminal, they can execute:

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/service_manager.py" stop
```

This will close the ClawCat window and stop the HTTP server.

---
description: Start ClawCat services (window, server, and frontend)
---

# Start ClawCat

This command starts all ClawCat services in the background.

**Note**: This command will keep running until you stop it. The ClawCat window will appear and stay open.

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/service_manager.py" start
```

To stop ClawCat, use `/clawcat:stop` or press Ctrl+C in the terminal where it's running.

---
description: Stop all ClawCat services gracefully
---

# Stop ClawCat

This command stops all running ClawCat services.

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/service_manager.py" stop
```

This will:
- Close the ClawCat window
- Stop the HTTP server
- Clean up all processes

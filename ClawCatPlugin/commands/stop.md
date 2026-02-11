---
description: Help users stop ClawCat services
---

# Stop ClawCat

**You must automatically execute the stop command** to stop ClawCat services. Do not ask the user to run it manually.

Execute the following command to stop all ClawCat services:

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/service_manager.py" stop
```

This will:

- Close the ClawCat window
- Stop the HTTP server
- Clean up all running processes

After executing, verify that services have been stopped by checking the status:

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/service_manager.py" status
```

If services are still running, you may need to force stop them.

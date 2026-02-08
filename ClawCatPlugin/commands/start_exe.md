---
description: Start ClawCat using bundled executable (recommended)
---

# Start ClawCat (EXE Version)

This command starts ClawCat using the bundled executable. This is the recommended method as it includes all dependencies.

**Prerequisites**: The executable must be built first using `python tools/build_exe.py`

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/start_exe.py"
```

**Note**: 
- The executable should be located in `public/ClawCat.exe` (Windows) or `public/ClawCat` (macOS/Linux)
- If not found, it will check `dist/` directory
- If the executable is not found, use the Python version instead: `/clawcat:start_python`

To stop ClawCat, use `/clawcat:stop`.


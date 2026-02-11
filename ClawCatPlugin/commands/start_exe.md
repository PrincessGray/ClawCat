---
description: Help users start ClawCat using bundled EXE (no dependency installation needed)
---

# Start ClawCat (EXE Version)

The EXE version includes all dependencies and does not require a Python environment.

## Check if EXE exists

First, check if the executable exists:

```bash
ls "${CLAUDE_PLUGIN_ROOT}/public/ClawCat.exe"
```

If it doesn't exist, guide the user to download it from GitHub Releases:

1. **Download from GitHub Releases**: Visit [https://github.com/PrincessGray/ClawCat/releases/](https://github.com/PrincessGray/ClawCat/releases/)
2. **Download the appropriate asset**:
   - Windows: Download `ClawCat.exe` or `ClawCat-windows.exe`
   - macOS: Download `ClawCat-macos` or `ClawCat`
   - Linux: Download `ClawCat-linux` or `ClawCat`
3. **Double-click the downloaded file** to run it - that's it!

## Tell user to execute startup command

If the EXE already exists in the plugin directory, **tell the user to execute in their terminal**:

### Windows

```bash
"${CLAUDE_PLUGIN_ROOT}\public\ClawCat.exe"
```

### macOS / Linux

```bash
"${CLAUDE_PLUGIN_ROOT}/public/ClawCat"
```

## Notes

- The EXE version does not require conda or Python environment
- To stop the service: Use `/clawcat:stop`

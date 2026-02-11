#!/usr/bin/env python3
"""
ClawCat Start Script - EXE Version
Starts ClawCat using the bundled executable
"""

import sys
import subprocess
import platform
from pathlib import Path

PLUGIN_ROOT = Path(__file__).parent.parent.absolute()

def main():
    """Start ClawCat using bundled executable"""
    if platform.system() == "Windows":
        exe_name = "ClawCat.exe"
    else:
        exe_name = "ClawCat"
    
    # Check for bundled executable
    bundled_exe = PLUGIN_ROOT / "public" / exe_name
    if not bundled_exe.exists():
        bundled_exe = PLUGIN_ROOT / "dist" / exe_name
    if not bundled_exe.exists():
        bundled_exe = PLUGIN_ROOT / exe_name
    
    if not bundled_exe.exists():
        print(f"error Bundled executable not found: {exe_name}")
        print("  Please run: python tools/build_exe.py")
        print("  Or use: python scripts/start_python.py")
        sys.exit(1)
    
    print(f"Starting ClawCat (EXE version): {bundled_exe}")
    
    # Start the executable
    if platform.system() == "Windows":
        subprocess.Popen(
            [str(bundled_exe)],
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
            cwd=str(PLUGIN_ROOT)
        )
    else:
        subprocess.Popen(
            [str(bundled_exe)],
            cwd=str(PLUGIN_ROOT)
        )
    
    print("ok ClawCat started (EXE version)")
    print("  Server: http://localhost:22622")

if __name__ == "__main__":
    main()


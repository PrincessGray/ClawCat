#!/usr/bin/env python3
"""
ClawCat Dependency Installer for SessionStart Hook
Installs Python dependencies from requirements.txt
"""

import sys
import subprocess
import json
import shutil
import platform
from pathlib import Path

PLUGIN_ROOT = Path(__file__).parent.parent.absolute()
REQUIREMENTS_FILE = PLUGIN_ROOT / "requirements.txt"

def find_conda():
    """Find conda executable"""
    # First try which/where
    conda_path = shutil.which("conda")
    if conda_path:
        return conda_path
    
    # Try common locations
    if platform.system() == "Windows":
        conda_paths = [
            Path.home() / "miniconda3" / "Scripts" / "conda.exe",
            Path.home() / "anaconda3" / "Scripts" / "conda.exe",
            Path("C:/ProgramData/miniconda3/Scripts/conda.exe"),
            Path("C:/ProgramData/anaconda3/Scripts/conda.exe"),
        ]
    else:
        conda_paths = [
            Path.home() / "miniconda3" / "bin" / "conda",
            Path.home() / "anaconda3" / "bin" / "conda",
        ]
    
    for path in conda_paths:
        if path.exists():
            return str(path)
    
    return None

def check_package(package_name):
    """Check if a package is installed"""
    try:
        if package_name == "PyQtWebEngine":
            # PyQtWebEngine needs special import
            __import__("PyQt5.QtWebEngineWidgets")
        else:
            __import__(package_name)
        return True
    except ImportError:
        return False

def print_message(message, is_error=False):
    """Print message in hook format or normal format"""
    # Check if running as hook (non-interactive) or directly
    if not sys.stdout.isatty():
        # Hook context - use JSON format
        print(json.dumps({
            "hookSpecificOutput": {
                "message": message
            }
        }))
    else:
        # Direct execution - use normal output
        print(message, file=sys.stderr if is_error else sys.stdout)

def install_dependencies():
    """Install Python dependencies from requirements.txt using conda if available"""
    if not REQUIREMENTS_FILE.exists():
        print_message(f"✗ requirements.txt not found at {REQUIREMENTS_FILE}", is_error=True)
        return False
    
    # Check if dependencies are already installed
    required_packages = ["requests", "psutil", "PyQt5", "PyQtWebEngine"]
    missing = [pkg for pkg in required_packages if not check_package(pkg)]
    
    if not missing:
        # All dependencies already installed
        print_message("✓ All Python dependencies are already installed")
        return True
    
    # Try to use conda if available
    conda_path = find_conda()
    if conda_path:
        print_message("Using conda environment...")
        # Use conda run to execute pip in conda environment
        if platform.system() == "Windows":
            cmd = [conda_path, "run", "-n", "base", "--no-capture-output", 
                   "python", "-m", "pip", "install", "-r", str(REQUIREMENTS_FILE)]
        else:
            cmd = [conda_path, "run", "-n", "base", "--no-capture-output",
                   "python", "-m", "pip", "install", "-r", str(REQUIREMENTS_FILE)]
    else:
        # No conda, use current Python
        cmd = [sys.executable, "-m", "pip", "install", "-r", str(REQUIREMENTS_FILE)]
    
    # Install dependencies
    print_message(f"Installing Python dependencies: {', '.join(missing)}")
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode == 0:
            print_message(f"✓ Installed Python dependencies: {', '.join(missing)}")
            return True
        else:
            error_msg = result.stderr[:200] if result.stderr else result.stdout[:200]
            print_message(f"✗ Failed to install dependencies: {error_msg}", is_error=True)
            return False
    except subprocess.TimeoutExpired:
        print_message("✗ Installation timeout (exceeded 5 minutes)", is_error=True)
        return False
    except Exception as e:
        print_message(f"✗ Error installing dependencies: {str(e)[:200]}", is_error=True)
        return False

def main():
    """Main entry point for SessionStart hook"""
    # SessionStart hook doesn't need to read stdin
    # Just install dependencies directly
    # Install dependencies
    success = install_dependencies()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()


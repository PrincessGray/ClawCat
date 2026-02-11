#!/usr/bin/env python3
"""
ClawCat Dependency Installer
Checks and installs required Python and Node.js dependencies.
"""

import sys
import subprocess
import shutil
from pathlib import Path

PLUGIN_ROOT = Path(__file__).parent.parent.absolute()

def check_python_packages():
    """Check which Python packages are missing"""
    required_packages = ["PyQt5", "PyQtWebEngine", "requests", "psutil"]
    missing = []

    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)

    return missing

def check_node_modules():
    """Check if node_modules exists"""
    node_modules = PLUGIN_ROOT / "node_modules"
    return node_modules.exists()

def install_python_packages():
    """Install Python packages from requirements.txt"""
    requirements_file = PLUGIN_ROOT / "requirements.txt"

    if not requirements_file.exists():
        print(f"Error: requirements.txt not found at {requirements_file}")
        return False

    print("Installing Python dependencies...")
    print(f"  Using: {sys.executable}")
    print(f"  From: {requirements_file}")

    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", str(requirements_file)],
            capture_output=True,
            text=True,
            check=True
        )
        print("ok Python dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"error Error installing Python dependencies:")
        print(e.stderr)
        return False

def install_node_packages():
    """Install Node.js packages"""
    package_json = PLUGIN_ROOT / "package.json"

    if not package_json.exists():
        print(f"Error: package.json not found at {package_json}")
        return False

    # Determine which package manager to use
    npm_cmd = "npm"
    if shutil.which("pnpm"):
        npm_cmd = "pnpm"
    elif shutil.which("yarn"):
        npm_cmd = "yarn"

    print(f"Installing Node.js dependencies using {npm_cmd}...")
    print(f"  Working directory: {PLUGIN_ROOT}")

    try:
        result = subprocess.run(
            [npm_cmd, "install"],
            cwd=str(PLUGIN_ROOT),
            capture_output=True,
            text=True,
            check=True
        )
        print(f"ok Node.js dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"error Error installing Node.js dependencies:")
        print(e.stderr)
        return False

def main():
    print("ClawCat Dependency Installer")
    print("=" * 50)

    # Check Python packages
    print("\nChecking Python packages...")
    missing_python = check_python_packages()

    if missing_python:
        print(f"Missing Python packages: {', '.join(missing_python)}")
        if not install_python_packages():
            print("\nerror Failed to install Python dependencies")
            sys.exit(1)
    else:
        print("ok All Python packages are installed")

    # Check Node.js packages
    print("\nChecking Node.js packages...")
    if not check_node_modules():
        print("node_modules not found")
        if not install_node_packages():
            print("\nerror Failed to install Node.js dependencies")
            sys.exit(1)
    else:
        print("ok node_modules exists")

    print("\n" + "=" * 50)
    print("ok All dependencies are installed!")
    sys.exit(0)

if __name__ == "__main__":
    main()


#!/usr/bin/env python3
"""
ClawCat Service Manager
Manages the lifecycle of ClawCat services: Vite dev server, HTTP server, and PyQt window.
"""

import os
import sys
import json
import time
import subprocess
import platform
import shutil
from pathlib import Path
from typing import Dict, Optional, List

# Constants
REQUIRED_PYTHON_VERSION = (3, 8)
REQUIRED_NODE_VERSION = (18, 0)
VITE_PORT = 6173
SERVER_PORT = 22622
PID_FILE_DIR = Path.home() / ".claude" / "clawcat"
PID_FILE = PID_FILE_DIR / "pids.json"
PLUGIN_ROOT = Path(__file__).parent.parent.absolute()

def ensure_pid_dir():
    """Ensure PID directory exists"""
    PID_FILE_DIR.mkdir(parents=True, exist_ok=True)

def check_environment() -> Dict:
    """Check if Python and Node.js meet minimum version requirements"""
    result = {"python": False, "node": False, "errors": []}

    # Check Python version
    current_python = sys.version_info[:2]
    if current_python >= REQUIRED_PYTHON_VERSION:
        result["python"] = True
    else:
        result["errors"].append(
            f"Python {REQUIRED_PYTHON_VERSION[0]}.{REQUIRED_PYTHON_VERSION[1]}+ required, "
            f"found {current_python[0]}.{current_python[1]}"
        )

    # Check Node.js version
    try:
        node_version = subprocess.check_output(
            ["node", "--version"],
            stderr=subprocess.DEVNULL,
            text=True
        ).strip()
        # Parse version like "v18.17.0"
        version_parts = node_version.lstrip('v').split('.')
        major = int(version_parts[0])
        if major >= REQUIRED_NODE_VERSION[0]:
            result["node"] = True
        else:
            result["errors"].append(
                f"Node.js {REQUIRED_NODE_VERSION[0]}+ required, found {major}"
            )
    except (subprocess.CalledProcessError, FileNotFoundError, ValueError):
        result["errors"].append("Node.js not found or invalid version")

    return result

def check_port_available(port: int) -> bool:
    """Check if a port is available"""
    import socket
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('127.0.0.1', port))
            return True
    except OSError:
        return False

def check_dependencies() -> Dict:
    """Check if required dependencies are installed"""
    result = {"python_deps": False, "node_deps": False, "missing": []}

    # Check Python dependencies
    required_python_packages = ["PyQt5", "PyQtWebEngine", "requests", "psutil"]
    missing_python = []

    for package in required_python_packages:
        try:
            __import__(package)
        except ImportError:
            missing_python.append(package)

    if not missing_python:
        result["python_deps"] = True
    else:
        result["missing"].extend(missing_python)

    # Check Node.js dependencies
    node_modules = PLUGIN_ROOT / "node_modules"
    if node_modules.exists() and (node_modules / ".package-lock.json").exists():
        result["node_deps"] = True
    else:
        result["missing"].append("node_modules")

    return result

def install_python_deps() -> bool:
    """Install Python dependencies"""
    requirements_file = PLUGIN_ROOT / "requirements.txt"
    if not requirements_file.exists():
        print(f"Error: requirements.txt not found at {requirements_file}")
        return False

    print("Installing Python dependencies...")
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-r", str(requirements_file)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print("✓ Python dependencies installed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing Python dependencies: {e}")
        return False

def install_node_deps() -> bool:
    """Install Node.js dependencies"""
    package_json = PLUGIN_ROOT / "package.json"
    if not package_json.exists():
        print(f"Error: package.json not found at {package_json}")
        return False

    print("Installing Node.js dependencies...")

    # Determine which package manager to use
    npm_cmd = "npm"
    if shutil.which("pnpm"):
        npm_cmd = "pnpm"
    elif shutil.which("yarn"):
        npm_cmd = "yarn"

    try:
        subprocess.check_call(
            [npm_cmd, "install"],
            cwd=str(PLUGIN_ROOT),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print(f"✓ Node.js dependencies installed using {npm_cmd}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing Node.js dependencies: {e}")
        return False

def read_pids() -> Dict:
    """Read PIDs from file"""
    if not PID_FILE.exists():
        return {}
    try:
        with open(PID_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}

def write_pids(pids: Dict):
    """Write PIDs to file"""
    ensure_pid_dir()
    with open(PID_FILE, 'w') as f:
        json.dump(pids, f, indent=2)

def is_process_running(pid: int) -> bool:
    """Check if a process is running"""
    try:
        import psutil
        return psutil.pid_exists(pid)
    except ImportError:
        # Fallback if psutil not available
        if platform.system() == "Windows":
            try:
                subprocess.check_output(
                    ["tasklist", "/FI", f"PID eq {pid}"],
                    stderr=subprocess.DEVNULL
                )
                return True
            except subprocess.CalledProcessError:
                return False
        else:
            try:
                os.kill(pid, 0)
                return True
            except OSError:
                return False

def terminate_process(pid: int, timeout: int = 5) -> bool:
    """Terminate a process gracefully, force kill if necessary"""
    if not is_process_running(pid):
        return True

    try:
        import psutil
        process = psutil.Process(pid)
        process.terminate()

        # Wait for graceful shutdown
        try:
            process.wait(timeout=timeout)
            return True
        except psutil.TimeoutExpired:
            # Force kill
            process.kill()
            process.wait(timeout=2)
            return True
    except ImportError:
        # Fallback without psutil
        if platform.system() == "Windows":
            try:
                subprocess.check_call(
                    ["taskkill", "/F", "/PID", str(pid)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                return True
            except subprocess.CalledProcessError:
                return False
        else:
            try:
                os.kill(pid, 15)  # SIGTERM
                time.sleep(timeout)
                if is_process_running(pid):
                    os.kill(pid, 9)  # SIGKILL
                return True
            except OSError:
                return False

def get_service_status() -> Dict:
    """Get status of all services"""
    pids = read_pids()
    status = {
        "vite": {"running": False, "pid": None},
        "server": {"running": False, "pid": None},
        "window": {"running": False, "pid": None}
    }

    for service in ["vite", "server", "window"]:
        pid_key = f"{service}_pid"
        if pid_key in pids:
            pid = pids[pid_key]
            if is_process_running(pid):
                status[service]["running"] = True
                status[service]["pid"] = pid

    return status

def is_service_running() -> bool:
    """Check if any ClawCat service is running"""
    status = get_service_status()
    return any(s["running"] for s in status.values())

def start_services() -> Dict:
    """Start all ClawCat services"""
    result = {"success": False, "pids": {}, "errors": []}

    # Check if already running
    if is_service_running():
        status = get_service_status()
        print("ClawCat services are already running:")
        for service, info in status.items():
            if info["running"]:
                print(f"  {service}: PID {info['pid']}")
        return {"success": False, "error": "Services already running"}

    # Check environment
    env_check = check_environment()
    if not (env_check["python"] and env_check["node"]):
        for error in env_check["errors"]:
            print(f"✗ {error}")
        return {"success": False, "errors": env_check["errors"]}

    # Check dependencies
    deps_check = check_dependencies()
    if not (deps_check["python_deps"] and deps_check["node_deps"]):
        print("Missing dependencies detected:")
        for dep in deps_check["missing"]:
            print(f"  - {dep}")

        # Install dependencies
        if not deps_check["python_deps"]:
            if not install_python_deps():
                return {"success": False, "error": "Failed to install Python dependencies"}

        if not deps_check["node_deps"]:
            if not install_node_deps():
                return {"success": False, "error": "Failed to install Node.js dependencies"}

    # Check port availability
    if not check_port_available(VITE_PORT):
        error = f"Port {VITE_PORT} is already in use"
        print(f"✗ {error}")
        return {"success": False, "error": error}

    if not check_port_available(SERVER_PORT):
        error = f"Port {SERVER_PORT} is already in use"
        print(f"✗ {error}")
        return {"success": False, "error": error}

    pids = {}

    try:
        # Start Vite dev server
        print("Starting Vite dev server...")
        vite_process = subprocess.Popen(
            ["npm", "run", "dev"],
            cwd=str(PLUGIN_ROOT),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if platform.system() == "Windows" else 0
        )
        pids["vite_pid"] = vite_process.pid
        print(f"✓ Vite server started (PID: {vite_process.pid})")

        # Wait for Vite to be ready
        time.sleep(3)

        # Start Python HTTP server
        print("Starting HTTP server...")
        server_script = PLUGIN_ROOT / "src" / "server.py"
        server_process = subprocess.Popen(
            [sys.executable, str(server_script)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if platform.system() == "Windows" else 0
        )
        pids["server_pid"] = server_process.pid
        print(f"✓ HTTP server started (PID: {server_process.pid})")

        # Wait for server to be ready
        time.sleep(2)

        # Start PyQt window
        print("Starting ClawCat window...")
        window_script = PLUGIN_ROOT / "src" / "launch_window.py"
        window_process = subprocess.Popen(
            [sys.executable, str(window_script)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if platform.system() == "Windows" else 0
        )
        pids["window_pid"] = window_process.pid
        print(f"✓ ClawCat window started (PID: {window_process.pid})")

        # Save PIDs
        write_pids(pids)

        print("\n✓ All ClawCat services started successfully!")
        print(f"  Vite: http://localhost:{VITE_PORT}")
        print(f"  Server: http://localhost:{SERVER_PORT}")

        result["success"] = True
        result["pids"] = pids

    except Exception as e:
        print(f"\n✗ Error starting services: {e}")
        # Clean up any started processes
        for pid in pids.values():
            terminate_process(pid)
        result["success"] = False
        result["error"] = str(e)

    return result

def stop_services() -> bool:
    """Stop all ClawCat services"""
    pids = read_pids()

    if not pids:
        print("No ClawCat services are running")
        return True

    print("Stopping ClawCat services...")

    # Stop in reverse order: window, server, vite
    for service in ["window", "server", "vite"]:
        pid_key = f"{service}_pid"
        if pid_key in pids:
            pid = pids[pid_key]
            if is_process_running(pid):
                print(f"Stopping {service} (PID: {pid})...")
                if terminate_process(pid):
                    print(f"✓ {service} stopped")
                else:
                    print(f"✗ Failed to stop {service}")

    # Clean up PID file
    if PID_FILE.exists():
        PID_FILE.unlink()

    print("\n✓ All ClawCat services stopped")
    return True

def main():
    if len(sys.argv) < 2:
        print("Usage: service_manager.py [start|stop|status]")
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "start":
        result = start_services()
        sys.exit(0 if result["success"] else 1)

    elif command == "stop":
        stop_services()
        sys.exit(0)

    elif command == "status":
        status = get_service_status()
        print("ClawCat Service Status:")
        for service, info in status.items():
            if info["running"]:
                print(f"  {service}: Running (PID: {info['pid']})")
            else:
                print(f"  {service}: Not running")
        sys.exit(0)

    else:
        print(f"Unknown command: {command}")
        print("Usage: service_manager.py [start|stop|status]")
        sys.exit(1)

if __name__ == "__main__":
    main()

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
REQUIRED_NODE_VERSION = (18, 0)  # Only needed for building frontend
SERVER_PORT = 22622  # Server serves both API and frontend
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

    # Check if frontend files exist (should be provided in repository)
    public_dir = PLUGIN_ROOT / "public"
    index_html = public_dir / "index.html"
    if not index_html.exists():
        result["missing"].append("public/index.html (should be provided in repository)")

    return result

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

def install_python_deps() -> bool:
    """Install Python dependencies using current Python environment"""
    requirements_file = PLUGIN_ROOT / "requirements.txt"
    if not requirements_file.exists():
        print(f"Error: requirements.txt not found at {requirements_file}")
        return False

    print("Installing Python dependencies...")
    print(f"  Using Python: {sys.executable}")
    
    # Use current Python (conda environment should already be activated by launcher script)
    cmd = [sys.executable, "-m", "pip", "install", "-r", str(requirements_file)]
    
    try:
        # Run with timeout and capture output
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=300,  # 5 minute timeout
            check=False  # Don't raise on non-zero exit
        )
        
        if result.returncode == 0:
            print("✓ Python dependencies installed")
            return True
        else:
            # Show error output if available
            if result.stdout:
                error_lines = result.stdout.strip().split('\n')
                # Show last few lines of error
                for line in error_lines[-5:]:
                    if line.strip():
                        print(f"  {line}")
            print("✗ Failed to install Python dependencies")
            return False
            
    except subprocess.TimeoutExpired:
        print("✗ Installation timeout (exceeded 5 minutes)")
        return False
    except Exception as e:
        print(f"✗ Error installing Python dependencies: {e}")
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
        "window": {"running": False, "pid": None}  # window includes server and frontend
    }

    for service in ["window"]:
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

    # Check which services are running
    status = get_service_status()
    running_services = [s for s, info in status.items() if info["running"]]
    
    if running_services:
        print("Some ClawCat services are already running:")
        for service in running_services:
            print(f"  {service}: PID {status[service]['pid']}")
        
        # Check if all required services are running
        required_services = ["window"]  # window includes server and frontend
        missing_services = [s for s in required_services if not status[s]["running"]]
        
        if missing_services:
            print(f"\n⚠ Missing services: {', '.join(missing_services)}")
            print("Starting missing services...")
            # Continue to start missing services instead of returning
        else:
            print("\n✓ All services are already running")
            return {"success": False, "error": "All services already running"}

    # Check environment (only Python is required now, Node.js only needed for building)
    env_check = check_environment()
    if not env_check["python"]:
        for error in env_check["errors"]:
            if "Python" in error:  # Only show Python errors
                print(f"✗ {error}")
        if not env_check["python"]:
            return {"success": False, "errors": [e for e in env_check["errors"] if "Python" in e]}

    # Install Python dependencies (always run once, pip will skip if already installed)
    # Note: Dependencies will also be installed by the launcher scripts if needed
    print("Installing Python dependencies...")
    if not install_python_deps():
        print("⚠ Dependency installation failed, but continuing...")
        print("  The launcher script will attempt to install dependencies if needed")

    # Check server port (window process includes server and frontend)
    if not status.get("window", {}).get("running", False):
        if not check_port_available(SERVER_PORT):
            error = f"Port {SERVER_PORT} is already in use"
            print(f"✗ {error}")
            return {"success": False, "error": error}

    # Check if public/ exists and has index.html (frontend files should be in repository)
    public_dir = PLUGIN_ROOT / "public"
    index_html = public_dir / "index.html"
    if not index_html.exists():
        print("✗ Frontend files not found: public/index.html")
        print("  Frontend files should be provided in the repository.")
        return {"success": False, "error": "public/index.html not found"}

    pids = {}
    existing_pids = read_pids()  # Read existing PIDs to preserve running services

    try:
        # Start PyQt window (only if not already running)
        # Note: launch_window.py will start the HTTP server internally, which serves both API and frontend
        if not status.get("window", {}).get("running", False):
            print("Starting ClawCat window...")
            
            # Start window directly (conda environment should already be activated by launcher script)
            window_script = PLUGIN_ROOT / "src" / "launch_window.py"
            
            if platform.system() == "Windows":
                # On Windows, use CREATE_NEW_PROCESS_GROUP to allow GUI window to show
                # Don't use DETACHED_PROCESS so output can be seen in console
                window_process = subprocess.Popen(
                    [sys.executable, str(window_script)],
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
                    cwd=str(PLUGIN_ROOT)
                )
            else:
                # On Unix-like systems, use normal process (output will go to console)
                window_process = subprocess.Popen(
                    [sys.executable, str(window_script)],
                    cwd=str(PLUGIN_ROOT)
                )
            
            # Wait a moment to check if process started successfully
            time.sleep(1.0)
            if window_process.poll() is not None:
                # Process exited immediately, get error
                error_msg = "Window process exited immediately"
                
                # Try to read error from log file
                log_dir = PID_FILE_DIR / "logs"
                if log_dir.exists():
                    log_files = sorted(log_dir.glob("clawcat_*.log"), key=lambda p: p.stat().st_mtime, reverse=True)
                    if log_files:
                        try:
                            with open(log_files[0], 'r', encoding='utf-8', errors='ignore') as f:
                                log_content = f.read()
                                if log_content:
                                    lines = log_content.strip().split('\n')
                                    last_lines = '\n'.join(lines[-10:]) if len(lines) > 10 else log_content
                                    error_msg = f"{error_msg}\nLast log entries:\n{last_lines}"
                        except:
                            pass
                
                if platform.system() != "Windows":
                    try:
                        stderr_output = window_process.stderr.read().decode('utf-8', errors='ignore')
                        if stderr_output:
                            error_msg = f"{error_msg}\n{stderr_output}"
                    except:
                        pass
                
                print(f"✗ {error_msg}")
                return {"success": False, "error": error_msg}
            
            pids["window_pid"] = window_process.pid
            # Get log file location (from launch_window.py)
            log_dir = PID_FILE_DIR / "logs"
            if log_dir.exists():
                log_files = sorted(log_dir.glob("clawcat_*.log"), key=lambda p: p.stat().st_mtime, reverse=True)
                if log_files:
                    print(f"✓ ClawCat window started (PID: {window_process.pid})")
                    print(f"  Window should appear shortly...")
                    print(f"  📝 Log file: {log_files[0]}")
                else:
                    print(f"✓ ClawCat window started (PID: {window_process.pid})")
                    print(f"  Window should appear shortly...")
                    print(f"  📝 Log directory: {log_dir}")
            else:
                print(f"✓ ClawCat window started (PID: {window_process.pid})")
                print(f"  Window should appear shortly...")
                print(f"  📝 Log directory: {log_dir}")
        else:
            # Window already running, use existing PID
            if "window_pid" in existing_pids:
                pids["window_pid"] = existing_pids["window_pid"]
                print(f"✓ Using existing ClawCat window (PID: {existing_pids['window_pid']})")

        # Save PIDs
        write_pids(pids)

        print(f"\n✓ ClawCat started successfully!")
        print(f"  Server: http://localhost:{SERVER_PORT} (serves both API and frontend)")

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

    # Stop window (includes server and frontend)
    for service in ["window"]:
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
        if not result["success"]:
            sys.exit(1)

        # Keep running to maintain MCP Server process
        # This allows Claude Code to manage the lifecycle
        print("\n🐱 ClawCat is running. Press Ctrl+C to stop.")
        try:
            import signal

            def signal_handler(sig, frame):
                print("\n\nReceived interrupt signal, stopping services...")
                stop_services()
                sys.exit(0)

            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)

            # Keep the process alive
            while True:
                time.sleep(1)

        except KeyboardInterrupt:
            print("\n\nStopping services...")
            stop_services()
            sys.exit(0)

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


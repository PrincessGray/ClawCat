#!/usr/bin/env python3
"""
ClawCat Server - Pure Python HTTP server
Cross-platform support: Windows & macOS
"""
import json
import os
import sys
import subprocess
import platform
from pathlib import Path
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
import threading
import time
from datetime import datetime

# ============================================================================
# Platform Detection & Window Control Import
# ============================================================================
PLATFORM = platform.system()  # 'Windows', 'Darwin', 'Linux'
print(f"[Platform] Detected: {PLATFORM}", file=sys.stderr, flush=True)

try:
    if PLATFORM == 'Darwin':  # macOS
        print(f"[Platform] Loading macOS window control", file=sys.stderr, flush=True)
        try:
            from .window_control_mac import minimize_window, restore_window, activate_window, set_window_topmost
        except ImportError:
            from window_control_mac import minimize_window, restore_window, activate_window, set_window_topmost
    elif PLATFORM == 'Windows':
        print(f"[Platform] Loading Windows window control", file=sys.stderr, flush=True)
        try:
            from .window_control import minimize_window, restore_window, activate_window, set_window_topmost
        except ImportError:
            from window_control import minimize_window, restore_window, activate_window, set_window_topmost
    else:
        raise ImportError(f"Unsupported platform: {PLATFORM}")
except ImportError as e:
    print(f"Warning: window control not available ({e}), window control disabled", file=sys.stderr, flush=True)
    def minimize_window(pid): return False
    def restore_window(pid): return False
    def activate_window(pid): return False
    def set_window_topmost(pid, topmost=True): return False

# ============================================================================
# Configuration
# ============================================================================
SERVER_PORT = 22622  # Must match CAT_SERVER port in notify.py

# Get base directory for static files
if getattr(sys, 'frozen', False):
    # Packaged executable
    STATIC_DIR = Path(sys._MEIPASS)
else:
    # Development mode
    STATIC_DIR = Path(__file__).parent.parent

# Frontend files location (all in public directory)
FRONTEND_PUBLIC = STATIC_DIR / "public"

# File cache for static files (in-memory cache)
_file_cache = {}
_file_cache_timestamps = {}

def get_file_with_cache(file_path: Path):
    """Get file content with caching"""
    file_str = str(file_path)
    mtime = file_path.stat().st_mtime if file_path.exists() else 0
    
    # Check if cache is valid
    if file_str in _file_cache and _file_cache_timestamps.get(file_str) == mtime:
        return _file_cache[file_str]
    
    # Read and cache file
    if file_path.exists():
        with open(file_path, 'rb') as f:
            content = f.read()
        _file_cache[file_str] = content
        _file_cache_timestamps[file_str] = mtime
        return content
    return None

# Shared state
class ServerState:
    def __init__(self):
        self.spy_mode = True  # Default to slacking mode
        self.current_pid = 0
        self.current_state = "resting"  # resting, working, confirming
        self.pending_response = None
        self.pending_response_lock = threading.Lock()
        self.callbacks = []  # UI update callbacks
        self.pending_hook_payload = None  # Store hook payload for confirming state
        self.pending_hook_type = None  # Store hook type (PermissionRequest/Notification)
        self.pending_hook_action = None  # Store hook action (ask_permission/ask_user)
        self.current_hook_payload = None  # Store current hook payload for all states (including working)
        self.queued_notification_need = None  # Store notification_need that was ignored during confirming state
        # Terminal commands for each mode (can be configured)
        self.spy_mode_command = None  # Command to execute when entering slacking mode
        self.monitor_mode_command = None  # Command to execute when entering spying mode

server_state = ServerState()

class ClawCatHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        """Handle POST requests"""
        parsed_path = urlparse(self.path)

        if parsed_path.path == "/claude-hook":
            self.handle_hook()
        elif parsed_path.path == "/toggle-mode":
            self.handle_toggle_mode()
        elif parsed_path.path == "/activate-terminal":
            self.handle_activate_terminal()
        elif parsed_path.path == "/set-topmost":
            self.handle_set_topmost()
        elif parsed_path.path == "/hook-response":
            self.handle_hook_response()
        elif parsed_path.path == "/set-state":
            self.handle_set_state()
        elif parsed_path.path == "/execute-command":
            self.handle_execute_command()
        elif parsed_path.path == "/set-mode-command":
            self.handle_set_mode_command()
        else:
            self.send_error(404, "Not Found")

    def do_GET(self):
        """Handle GET requests - all files served from public directory"""
        parsed_path = urlparse(self.path)

        if parsed_path.path == "/status":
            self.handle_status()
        elif parsed_path.path == "/" or parsed_path.path == "/index.html":
            # Serve index.html from public
            self.serve_static_file(FRONTEND_PUBLIC / "index.html", "text/html")
        elif parsed_path.path.startswith("/assets/") or parsed_path.path.startswith("/js/") or parsed_path.path.startswith("/models/"):
            # Serve all static files from public directory
            file_path = FRONTEND_PUBLIC / parsed_path.path[1:]  # Remove leading /
            if file_path.exists():
                content_type = self.get_content_type(file_path)
                self.serve_static_file(file_path, content_type)
            else:
                self.send_error(404, "Not Found")
        else:
            self.send_error(404, "Not Found")
    
    def get_content_type(self, file_path):
        """Get content type based on file extension"""
        ext = file_path.suffix.lower()
        content_types = {
            '.html': 'text/html',
            '.js': 'application/javascript',
            '.css': 'text/css',
            '.json': 'application/json',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.svg': 'image/svg+xml',
            '.ico': 'image/x-icon',
            '.flac': 'audio/flac',
            '.moc3': 'application/octet-stream',
            '.motion3.json': 'application/json',
            '.exp3.json': 'application/json',
            '.cdi3.json': 'application/json',
            '.model3.json': 'application/json',
        }
        return content_types.get(ext, 'application/octet-stream')
    
    def serve_static_file(self, file_path, content_type):
        """Serve a static file with caching"""
        try:
            content = get_file_with_cache(file_path)
            if content is None:
                self.send_error(404, "Not Found")
                return
            
            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(content)))
            self.send_header('Access-Control-Allow-Origin', '*')
            
            # Enable browser caching for static assets (1 hour)
            # But no-cache for HTML to ensure updates are seen
            if content_type == 'text/html':
                self.send_header('Cache-Control', 'no-cache, must-revalidate')
            else:
                # Cache static assets for 1 hour
                self.send_header('Cache-Control', 'public, max-age=3600')
            
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            print(f"Error serving file {file_path}: {e}", file=sys.stderr, flush=True)
            self.send_error(500, "Internal Server Error")
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests (CORS preflight)"""
        print(f"[CORS] OPTIONS request for {self.path}", file=sys.stderr, flush=True)
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Access-Control-Max-Age', '86400')  # 24 hours
        self.end_headers()
    
    def handle_hook(self):
        """Handle hook requests from notify.py"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            payload = json.loads(body.decode('utf-8'))
            
            action = payload.get("action", "")
            mode = payload.get("mode", "")
            print(f"[Hook] Action: {action}, Mode: {mode}, PID: {payload.get('pid', 0)}", file=sys.stderr, flush=True)

            # If we're already in confirming state (waiting for UI response), 
            # queue fire_and_forget requests (like notification_need) to show after timeout
            if server_state.current_state == "confirming" and mode == "fire_and_forget":
                if action == "notification_need":
                    # Save notification_need to show after timeout
                    server_state.queued_notification_need = payload
                    print(f"[State] Queued {action} (will show after confirming timeout)", file=sys.stderr, flush=True)
                else:
                    print(f"[State] Ignoring {action} (already in confirming state, waiting for UI response)", file=sys.stderr, flush=True)
                response = {"choice": None, "user_input": None}
                self.send_json_response(200, response)
                return

            # Update current PID directly from payload (terminal PID from notify.py)
            if payload.get("pid", 0) > 0:
                server_state.current_pid = payload.get("pid", 0)
            
            # Update state based on action and mode
            old_state = server_state.current_state
            
            # Handle set_state action
            if action == "set_state" and "data" in payload and "state" in payload["data"]:
                new_state = payload["data"]["state"]
                if new_state in ["resting", "working", "confirming"]:
                    server_state.current_state = new_state
                    # Store payload for all states (especially working for UI notification)
                    server_state.current_hook_payload = payload
                    print(f"[State] {old_state} -> {new_state} (Caption: {payload['data'].get('caption', 'N/A')})", file=sys.stderr, flush=True)
            # Handle blocking mode
            elif payload.get("mode") == "blocking":
                server_state.current_state = "confirming"
                # Store hook type and action for UI
                server_state.pending_hook_payload = payload
                server_state.pending_hook_type = payload.get("action", "")  # ask_permission or ask_user
                server_state.pending_hook_action = payload.get("action", "")
                server_state.current_hook_payload = payload
                print(f"[State] {old_state} -> confirming (Blocking request)", file=sys.stderr, flush=True)
            # Handle notification_need: fire_and_forget, show notification like session stop
            elif action == "notification_need":
                server_state.current_state = "resting"
                server_state.current_hook_payload = payload
                print(f"[State] {old_state} -> resting (Notification need)", file=sys.stderr, flush=True)
            # Default to working for other actions
            elif action not in ["ignore", "pulse"]:
                server_state.current_state = "working"
                server_state.current_hook_payload = payload
                print(f"[State] {old_state} -> working (Action: {action})", file=sys.stderr, flush=True)
            
            # In slacking mode, return __IGNORE__ for blocking requests
            if server_state.spy_mode:
                if payload.get("mode") == "blocking":
                    # Complete logging for blocking POST in slacking mode
                    print(f"[Blocking POST - Slacking Mode]", file=sys.stderr, flush=True)
                    print(f"  Path: {self.path}", file=sys.stderr, flush=True)
                    print(f"  Action: {payload.get('action', 'N/A')}", file=sys.stderr, flush=True)
                    print(f"  Mode: {payload.get('mode', 'N/A')}", file=sys.stderr, flush=True)
                    print(f"  PID: {payload.get('pid', 0)}", file=sys.stderr, flush=True)
                    print(f"  Hook Type: {payload.get('action', 'N/A')}", file=sys.stderr, flush=True)
                    print(f"  Timeout: {payload.get('timeout', 'N/A')}", file=sys.stderr, flush=True)
                    print(f"  Full Payload: {json.dumps(payload, indent=2, ensure_ascii=False)}", file=sys.stderr, flush=True)
                    response = {
                        "choice": "__IGNORE__",
                        "user_input": "__IGNORE__"
                    }
                    print(f"  Response: {json.dumps(response, indent=2, ensure_ascii=False)}", file=sys.stderr, flush=True)
                    self.send_json_response(200, response)
                    server_state.current_state = "resting"
                    server_state.pending_hook_payload = None
                    server_state.pending_hook_type = None
                    server_state.pending_hook_action = None
                    return
                # Allow visual updates in slacking mode
                self.notify_ui(payload)
                response = {"choice": None, "user_input": None}
                self.send_json_response(200, response)
                return
            
            # Spying mode - handle normally
            if payload.get("mode") == "blocking":
                # Complete logging for blocking POST in spying mode
                print(f"[Blocking POST - Spying Mode]", file=sys.stderr, flush=True)
                print(f"  Path: {self.path}", file=sys.stderr, flush=True)
                print(f"  Action: {payload.get('action', 'N/A')}", file=sys.stderr, flush=True)
                print(f"  Mode: {payload.get('mode', 'N/A')}", file=sys.stderr, flush=True)
                print(f"  PID: {payload.get('pid', 0)}", file=sys.stderr, flush=True)
                print(f"  Hook Type: {payload.get('action', 'N/A')}", file=sys.stderr, flush=True)
                print(f"  Timeout: {payload.get('timeout', 'N/A')}", file=sys.stderr, flush=True)
                print(f"  Full Payload: {json.dumps(payload, indent=2, ensure_ascii=False)}", file=sys.stderr, flush=True)
                # For blocking requests, store payload and wait for UI response
                self.notify_ui(payload)
                response = self.wait_for_ui_response(payload)
                print(f"  Response: {json.dumps(response, indent=2, ensure_ascii=False)}", file=sys.stderr, flush=True)
                self.send_json_response(200, response)
                server_state.current_state = "resting"
                server_state.pending_hook_payload = None
                server_state.pending_hook_type = None
                server_state.pending_hook_action = None
                # Clear queued notification_need if user responded (no need to show it)
                server_state.queued_notification_need = None
            else:
                # Fire and forget - just notify UI
                self.notify_ui(payload)
                response = {"choice": None, "user_input": None}
                self.send_json_response(200, response)
                
        except Exception as e:
            print(f"Error handling hook: {e}", file=sys.stderr)
            self.send_error(500, str(e))
    
    def handle_toggle_mode(self):
        """Handle mode toggle requests"""
        old_mode = "slacking" if server_state.spy_mode else "spying"
        server_state.spy_mode = not server_state.spy_mode
        mode = "slacking" if server_state.spy_mode else "spying"
        
        print(f"[Toggle Mode] {old_mode} -> {mode}, PID: {server_state.current_pid}", file=sys.stderr, flush=True)

        # Send response immediately
        response = {
            "mode": mode,
            "pid": server_state.current_pid
        }
        self.send_json_response(200, response)

        # Everything else happens in background thread (non-blocking)
        def background_tasks():
            try:
                # Notify UI
                self.notify_ui({"type": "mode_changed", "mode": mode})

                # Control terminal window
                if server_state.current_pid > 0:
                    if server_state.spy_mode:
                        # Slacking mode: 激活 terminal（自动恢复+置顶）
                        print(f"[Window] Activating window for PID {server_state.current_pid}", file=sys.stderr, flush=True)
                        result = activate_window(server_state.current_pid)
                        print(f"[Window] activate_window={result} (includes restore + topmost)", file=sys.stderr, flush=True)
                        # 执行 slacking 模式的命令（如果有配置）
                        if server_state.spy_mode_command:
                            self.execute_terminal_command("slacking", server_state.spy_mode_command)
                    else:
                        # Spying mode: 关闭 terminal
                        print(f"[Window] Minimizing window for PID {server_state.current_pid}", file=sys.stderr, flush=True)
                        result = minimize_window(server_state.current_pid)
                        print(f"[Window] minimize_window={result}", file=sys.stderr, flush=True)
                        # 执行 spying 模式的命令（如果有配置）
                        if server_state.monitor_mode_command:
                            self.execute_terminal_command("spying", server_state.monitor_mode_command)
                else:
                    print(f"[Window] Skipping window control: no valid PID (current_pid={server_state.current_pid})", file=sys.stderr, flush=True)
            except Exception as e:
                print(f"[Window] Background task error: {e}", file=sys.stderr, flush=True)

        # Run everything in background
        threading.Thread(target=background_tasks, daemon=True).start()

    def handle_activate_terminal(self):
        """Handle activate terminal request"""
        success = activate_terminal()
        response = {"success": success}
        self.send_json_response(200, response)
    
    def handle_set_topmost(self):
        """Handle set window topmost request"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            payload = json.loads(body.decode('utf-8'))
            
            topmost = payload.get("topmost", True)
            
            if server_state.current_pid > 0:
                success = set_window_topmost(server_state.current_pid, topmost)
                response = {"success": success}
            else:
                response = {"success": False, "error": "No PID available"}
            
            self.send_json_response(200, response)
        except Exception as e:
            print(f"Error setting topmost: {e}", file=sys.stderr)
            self.send_error(500, str(e))
    
    def handle_hook_response(self):
        """Handle hook response from UI (for confirming state)"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            payload = json.loads(body.decode('utf-8'))
            
            choice = payload.get("choice", "deny")
            user_input = payload.get("user_input")
            
            print(f"[Hook Response] Received from UI: choice={choice}, user_input={user_input}", file=sys.stderr, flush=True)
            
            # Store response for waiting hook
            with server_state.pending_response_lock:
                server_state.pending_response = {
                    "choice": choice,
                    "user_input": user_input
                }
            
            print(f"[Hook Response] Stored response, notifying waiting thread", file=sys.stderr, flush=True)
            
            # Update state back to resting
            server_state.current_state = "resting"
            server_state.pending_hook_payload = None
            server_state.pending_hook_type = None
            server_state.pending_hook_action = None
            
            response = {"success": True}
            self.send_json_response(200, response)
            print(f"[Hook Response] Response sent to UI", file=sys.stderr, flush=True)
        except Exception as e:
            print(f"Error handling hook response: {e}", file=sys.stderr)
            self.send_error(500, str(e))
    
    def handle_set_state(self):
        """Handle set state request"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            payload = json.loads(body.decode('utf-8'))
            
            new_state = payload.get("state", "resting")
            if new_state in ["resting", "working", "confirming"]:
                server_state.current_state = new_state
                response = {"success": True, "state": new_state}
            else:
                response = {"success": False, "error": "Invalid state"}
            
            self.send_json_response(200, response)
        except Exception as e:
            print(f"Error setting state: {e}", file=sys.stderr)
            self.send_error(500, str(e))
    
    def handle_execute_command(self):
        """Handle execute command request"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            payload = json.loads(body.decode('utf-8'))
            
            mode = payload.get("mode", "")
            command = payload.get("command", "")
            
            if mode and command:
                success = self.execute_terminal_command(mode, command)
                response = {"success": success}
            else:
                response = {"success": False, "error": "Missing mode or command"}
            
            self.send_json_response(200, response)
        except Exception as e:
            print(f"Error executing command: {e}", file=sys.stderr)
            self.send_error(500, str(e))
    
    def handle_set_mode_command(self):
        """Handle set mode command request (configure commands for each mode)"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            payload = json.loads(body.decode('utf-8'))
            
            spy_command = payload.get("spy_command")
            monitor_command = payload.get("monitor_command")
            
            if spy_command is not None:
                server_state.spy_mode_command = spy_command
            if monitor_command is not None:
                server_state.monitor_mode_command = monitor_command
            
            response = {
                "success": True,
                "spy_command": server_state.spy_mode_command,
                "monitor_command": server_state.monitor_mode_command
            }
            self.send_json_response(200, response)
        except Exception as e:
            print(f"Error setting mode command: {e}", file=sys.stderr)
            self.send_error(500, str(e))
    
    def execute_terminal_command(self, mode, custom_command=None):
        """Execute terminal command based on mode"""
        try:
            if server_state.current_pid <= 0:
                print(f"Cannot execute command: no valid PID (current_pid={server_state.current_pid})", file=sys.stderr)
                return False
            
            # 根据模式执行不同的命令
            if mode == "spy":
                # Spy 模式：可以执行激活 terminal 的命令
                # 这里可以添加自定义命令，例如：
                # command = custom_command or "echo 'Spy mode activated'"
                if custom_command:
                    return self.send_command_to_terminal(custom_command)
                # 默认行为：已经通过 restore_window 和 activate_window 处理
                return True
            elif mode == "monitor":
                # Monitor 模式：可以执行最小化 terminal 的命令
                # 这里可以添加自定义命令，例如：
                # command = custom_command or "echo 'Monitor mode activated'"
                if custom_command:
                    return self.send_command_to_terminal(custom_command)
                # 默认行为：已经通过 minimize_window 处理
                return True
            else:
                return False
        except Exception as e:
            print(f"Error executing terminal command: {e}", file=sys.stderr)
            return False
    
    def send_command_to_terminal(self, command):
        """Send command to terminal window (Windows Terminal)"""
        try:
            if server_state.current_pid <= 0:
                return False
            
            # 方法：使用 Windows Terminal 的 wt.exe 在指定窗口中执行命令
            # 或者使用 PowerShell 在指定进程中执行命令
            
            # 尝试使用 Windows Terminal 的 wt.exe
            # wt.exe -w 0 表示在当前窗口，new-tab 创建新标签页
            try:
                # 检查是否是 Windows Terminal
                import psutil
                proc = psutil.Process(server_state.current_pid)
                proc_name = proc.name().lower()
                
                if 'windowsterminal' in proc_name or 'wt.exe' in proc_name:
                    # 使用 wt.exe 执行命令
                    subprocess.Popen([
                        'wt.exe', 
                        '-w', '0',  # 当前窗口
                        'new-tab',  # 新标签页
                        '--', 
                        'powershell', 
                        '-Command', 
                        command
                    ], shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
                    return True
                else:
                    # 其他 terminal，尝试使用 PowerShell 执行
                    # 在指定进程的上下文中执行命令
                    ps_script = f'''
                    $pid = {server_state.current_pid}
                    $proc = Get-Process -Id $pid -ErrorAction SilentlyContinue
                    if ($proc) {{
                        Start-Process powershell -ArgumentList "-NoExit", "-Command", "{command}" -WindowStyle Normal
                    }}
                    '''
                    subprocess.Popen([
                        'powershell', 
                        '-Command', 
                        ps_script
                    ], shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
                    return True
            except ImportError:
                # 如果没有 psutil，使用简单的方法
                subprocess.Popen([
                    'powershell', 
                    '-Command', 
                    command
                ], shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
                return True
            
        except Exception as e:
            print(f"Error sending command to terminal: {e}", file=sys.stderr)
            return False

    def handle_status(self):
        """Handle status request"""
        response = {
            "mode": "slacking" if server_state.spy_mode else "spying",
            "pid": server_state.current_pid,
            "state": server_state.current_state,
            "message": self.get_status_message()
        }
        # Include hook payload for all states (for working notification and confirming)
        if server_state.current_hook_payload:
            response["hook_payload"] = server_state.current_hook_payload
        # Only include hook type/action if in confirming state
        if server_state.current_state == "confirming" and server_state.pending_hook_payload:
            response["hook_type"] = server_state.pending_hook_type
            response["hook_action"] = server_state.pending_hook_action
        self.send_json_response(200, response)
    
    def get_status_message(self):
        """Get status message based on current state"""
        if server_state.current_state == "confirming":
            return "等待用户确认..."
        elif server_state.current_state == "working":
            return "正在工作..."
        else:
            return "Standing by..."
    
    def wait_for_ui_response(self, payload):
        """Wait for UI to provide response (with timeout)"""
        timeout = payload.get("timeout", 90)
        
        print(f"[Wait] Starting to wait for UI response (timeout={timeout}s)", file=sys.stderr, flush=True)
        
        # Notify UI
        self.notify_ui(payload)
        
        # Wait for response
        with server_state.pending_response_lock:
            server_state.pending_response = None
        
        start_time = time.time()
        poll_count = 0
        while time.time() - start_time < timeout:
            with server_state.pending_response_lock:
                if server_state.pending_response is not None:
                    response = server_state.pending_response
                    server_state.pending_response = None
                    elapsed = time.time() - start_time
                    print(f"[Wait] ✅ Received response after {elapsed:.1f}s: {response}", file=sys.stderr, flush=True)
                    return response
            poll_count += 1
            if poll_count % 50 == 0:  # Log every 5 seconds
                elapsed = time.time() - start_time
                print(f"[Wait] Still waiting... ({elapsed:.1f}s elapsed)", file=sys.stderr, flush=True)
            time.sleep(0.1)
        
        # Timeout
        print(f"[Wait] ⏰ Timeout after {timeout}s, returning deny", file=sys.stderr, flush=True)
        
        # Check if there's a queued notification_need to show after timeout
        if server_state.queued_notification_need:
            queued_payload = server_state.queued_notification_need
            server_state.queued_notification_need = None
            print(f"[State] Showing queued notification_need after timeout", file=sys.stderr, flush=True)
            # Change state to resting and notify UI
            server_state.current_state = "resting"
            server_state.current_hook_payload = queued_payload
            self.notify_ui(queued_payload)
        
        return {"choice": "deny", "user_input": None}
    
    def notify_ui(self, payload):
        """Notify UI about hook update"""
        action = payload.get("action", "N/A")
        print(f"[UI Notify] Action: {action}, Callbacks: {len(server_state.callbacks)}", file=sys.stderr, flush=True)
        for callback in server_state.callbacks:
            try:
                callback(payload)
            except Exception as e:
                print(f"Error in UI callback: {e}", file=sys.stderr)
    
    def send_json_response(self, status, data):
        """Send JSON response"""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
    
    def log_message(self, format, *args):
        """Override to reduce logging noise"""
        # Skip GET requests completely
        if self.command == 'GET':
            return
        # Only log errors for other requests
        if args[1] != 200:
            super().log_message(format, *args)

def get_server_state():
    """Get current server state (for UI)"""
    return {
        "spy_mode": server_state.spy_mode,
        "current_pid": server_state.current_pid
    }

def activate_terminal():
    """Activate terminal window (called by UI double-click)"""
    if server_state.current_pid > 0:
        return activate_window(server_state.current_pid)
    else:
        print(f"Cannot activate terminal: no valid PID (current_pid={server_state.current_pid})", file=sys.stderr)
        return False

def send_hook_response(choice=None, user_input=None):
    """Send response from UI (called by UI components)"""
    with server_state.pending_response_lock:
        server_state.pending_response = {
            "choice": choice,
            "user_input": user_input
        }

def register_ui_callback(callback):
    """Register a callback for UI updates"""
    server_state.callbacks.append(callback)

def start_server(port=SERVER_PORT):
    """Start the HTTP server (multi-threaded to handle concurrent requests)"""
    server = ThreadingHTTPServer(('127.0.0.1', port), ClawCatHandler)
    print(f"ClawCat server listening on port {port}")
    print(f"Multi-threaded server ready - debug logging enabled", flush=True)
    
    def run_server():
        server.serve_forever()
    
    thread = threading.Thread(target=run_server, daemon=True)
    thread.start()
    return server, thread

if __name__ == "__main__":
    server, thread = start_server()
    print("ClawCat server started. Press Ctrl+C to stop.")
    try:
        thread.join()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.shutdown()


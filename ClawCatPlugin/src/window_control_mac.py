#!/usr/bin/env python3
"""
macOS Window Control Module
Control terminal windows by PID using AppleScript wrapper
"""
import subprocess
import sys

# ============================================================================
# AppleScript Wrapper
# ============================================================================

def run_applescript(script):
    """
    Execute AppleScript code from Python
    
    This is the "wrapper" pattern: Python calls macOS's osascript command
    to execute AppleScript, which controls the window system.
    
    Returns:
        (success: bool, output: str)
    """
    try:
        result = subprocess.run(
            ['osascript', '-e', script],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0, result.stdout.strip()
    except subprocess.TimeoutExpired:
        print(f"[AppleScript] Timeout", file=sys.stderr, flush=True)
        return False, ""
    except Exception as e:
        print(f"[AppleScript] Error: {e}", file=sys.stderr, flush=True)
        return False, ""

# ============================================================================
# Window Discovery
# ============================================================================

def find_window_by_pid(pid):
    """
    Find application by process ID
    
    If no window is found for the given PID, recursively searches parent
    processes (up to 10 levels) to find the terminal application.
    
    Returns:
        Application name (str) or None
    """
    script = f'''
        tell application "System Events"
            try
                set theProcess to first process whose unix id is {pid}
                return name of theProcess
            on error
                return ""
            end try
        end tell
    '''
    
    success, app_name = run_applescript(script)
    if success and app_name:
        print(f"[FindWindow] Found process for PID {pid}: {app_name}", 
              file=sys.stderr, flush=True)
        return app_name
    
    # No window found, search parent processes
    print(f"[FindWindow] No window for PID {pid}, searching parent chain...", 
          file=sys.stderr, flush=True)
    
    try:
        import psutil
        current_pid = pid
        max_depth = 10
        
        for depth in range(max_depth):
            try:
                proc = psutil.Process(current_pid)
                parent = proc.parent()
                
                if not parent or parent.pid == current_pid:
                    print(f"[FindWindow] Reached end of parent chain", 
                          file=sys.stderr, flush=True)
                    break
                
                parent_pid = parent.pid
                print(f"[FindWindow] Trying parent PID {parent_pid} ({parent.name()})", 
                      file=sys.stderr, flush=True)
                
                script = f'''
                    tell application "System Events"
                        try
                            set theProcess to first process whose unix id is {parent_pid}
                            return name of theProcess
                        on error
                            return ""
                        end try
                    end tell
                '''
                success, app_name = run_applescript(script)
                if success and app_name:
                    return app_name
                
                current_pid = parent_pid
                
            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                print(f"[FindWindow] Error accessing parent: {e}", 
                      file=sys.stderr, flush=True)
                break
                
    except ImportError:
        print(f"[FindWindow] psutil not available", file=sys.stderr, flush=True)
    except Exception as e:
        print(f"[FindWindow] Error: {e}", file=sys.stderr, flush=True)
    
    print(f"[FindWindow] No window found for PID {pid}", file=sys.stderr, flush=True)
    return None

# ============================================================================
# Window Control Functions (compatible with Windows version)
# ============================================================================

def minimize_window(pid):
    """
    Minimize window to dock
    
    AppleScript: set visible to false = hide the application
    """
    print(f"[MinimizeWindow] PID {pid}", file=sys.stderr, flush=True)
    
    script = f'''
        tell application "System Events"
            try
                set visible of first process whose unix id is {pid} to false
                return "success"
            on error errMsg
                return errMsg
            end try
        end tell
    '''
    
    success, output = run_applescript(script)
    result = success and output == "success"
    print(f"[MinimizeWindow] Result: {result}", file=sys.stderr, flush=True)
    return result


def maximize_window(pid):
    """
    Maximize window (fullscreen on macOS)
    
    Note: macOS doesn't have traditional "maximize", this enters fullscreen
    """
    script = f'''
        tell application "System Events"
            try
                tell (first process whose unix id is {pid})
                    set value of attribute "AXFullScreen" of window 1 to true
                end tell
                return "success"
            on error errMsg
                return errMsg
            end try
        end tell
    '''
    
    success, output = run_applescript(script)
    return success and output == "success"


def restore_window(pid):
    """
    Restore window from minimized state
    
    On macOS, this is the same as activate_window
    """
    return activate_window(pid)


def activate_window(pid):
    """
    Activate window and bring to front
    
    This is the primary window activation function that:
    1. Shows the window if hidden
    2. Brings it to the foreground
    3. Note: macOS doesn't support always-on-top natively
    """
    print(f"[ActivateWindow] PID {pid}", file=sys.stderr, flush=True)
    
    # Two-step process: show + activate
    script = f'''
        tell application "System Events"
            try
                set theProcess to first process whose unix id is {pid}
                set visible of theProcess to true
                set frontmost of theProcess to true
                return "success"
            on error errMsg
                return errMsg
            end try
        end tell
    '''
    
    success, output = run_applescript(script)
    result = success and output == "success"
    print(f"[ActivateWindow] Result: {result}", file=sys.stderr, flush=True)
    return result


def set_window_topmost(pid, topmost=True):
    """
    Set or remove always-on-top status
    
    ⚠️ macOS Limitation: No native always-on-top API
    This function only activates the window, cannot keep it topmost
    
    Args:
        pid: Process ID
        topmost: True to activate, False to do nothing
    """
    print(f"[SetTopmost] PID {pid}, topmost={topmost}", file=sys.stderr, flush=True)
    print(f"[SetTopmost] ⚠️ macOS does not support always-on-top", 
          file=sys.stderr, flush=True)
    
    if topmost:
        # Can only bring to front, cannot "pin" on top
        return activate_window(pid)
    else:
        # No-op: cannot remove topmost (it doesn't exist)
        return True


def hide_window(pid):
    """Hide window (same as minimize on macOS)"""
    return minimize_window(pid)


def show_window(pid):
    """Show previously hidden window"""
    script = f'''
        tell application "System Events"
            try
                set visible of first process whose unix id is {pid} to true
                return "success"
            on error errMsg
                return errMsg
            end try
        end tell
    '''
    
    success, output = run_applescript(script)
    return success and output == "success"


def get_window_state(pid):
    """
    Get current window state
    
    Returns:
        'minimized', 'maximized', 'normal', or 'not_found'
    """
    # Check if visible (not hidden/minimized)
    script = f'''
        tell application "System Events"
            try
                return visible of first process whose unix id is {pid}
            on error
                return "not_found"
            end try
        end tell
    '''
    success, visible = run_applescript(script)
    
    if not success or visible == "not_found":
        return "not_found"
    
    if visible == "false":
        return "minimized"
    
    # Check if fullscreen
    script = f'''
        tell application "System Events"
            try
                tell (first process whose unix id is {pid})
                    return value of attribute "AXFullScreen" of window 1
                end tell
            on error
                return "false"
            end try
        end tell
    '''
    success, fullscreen = run_applescript(script)
    
    if fullscreen == "true":
        return "maximized"
    
    return "normal"

# ============================================================================
# Command Line Interface (for testing)
# ============================================================================

def main():
    """CLI entry point for testing"""
    if len(sys.argv) < 3:
        print("Usage: window_control_mac.py <pid> <action>")
        print("Actions: minimize, maximize, restore, activate, hide, show, state, topmost, notopmost")
        print("\nNote: 'topmost' on macOS only brings window to front, cannot keep it always-on-top")
        sys.exit(1)
    
    try:
        pid = int(sys.argv[1])
        action = sys.argv[2].lower()
    except ValueError:
        print(f"Error: Invalid PID: {sys.argv[1]}")
        sys.exit(1)
    
    actions = {
        "minimize": (minimize_window, "Minimize"),
        "maximize": (maximize_window, "Maximize (Fullscreen)"),
        "restore": (restore_window, "Restore"),
        "activate": (activate_window, "Activate"),
        "hide": (hide_window, "Hide"),
        "show": (show_window, "Show"),
        "topmost": (lambda p: set_window_topmost(p, True), "Bring to Front (no topmost)"),
        "notopmost": (lambda p: set_window_topmost(p, False), "No-op (no topmost)"),
    }
    
    if action == "state":
        state = get_window_state(pid)
        print(f"Window state (PID {pid}): {state}")
        sys.exit(0)
    
    if action in actions:
        func, desc = actions[action]
        result = func(pid)
        print(f"{desc} (PID {pid}): {'Success' if result else 'Failed'}")
        sys.exit(0 if result else 1)
    
    print(f"Error: Unknown action: {action}")
    print(f"Valid actions: {', '.join(actions.keys())}, state")
    sys.exit(1)


if __name__ == "__main__":
    main()


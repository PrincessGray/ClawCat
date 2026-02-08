#!/usr/bin/env python3
"""
Windows Terminal Control Module
Control terminal windows by PID using Win32 API
"""
import sys
import ctypes
from ctypes import wintypes

# ============================================================================
# Win32 API Constants
# ============================================================================
# ShowWindow commands
SW_HIDE = 0
SW_SHOWNORMAL = 1
SW_SHOWMINIMIZED = 2
SW_SHOWMAXIMIZED = 3
SW_SHOWNOACTIVATE = 4
SW_SHOW = 5
SW_MINIMIZE = 6
SW_SHOWMINNOACTIVE = 7
SW_SHOWNA = 8
SW_RESTORE = 9
SW_SHOWDEFAULT = 10
SW_FORCEMINIMIZE = 11

# SetWindowPos constants
HWND_TOPMOST = -1
HWND_NOTOPMOST = -2
SWP_NOMOVE = 0x0002
SWP_NOSIZE = 0x0001

# Win32 API bindings
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

# ============================================================================
# Window Discovery
# ============================================================================

def find_window_by_pid(pid):
    """
    Find window handle by process ID
    
    If no window is found for the given PID, recursively searches parent
    processes (up to 10 levels) to find the terminal window.
    
    Returns:
        HWND or None
    """
    def enum_windows_callback(hwnd, lParam):
        """Callback to enumerate windows and match by PID"""
        process_id = ctypes.c_ulong()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(process_id))
        
        if process_id.value == lParam:
            # Only consider visible windows with titles
            if user32.IsWindowVisible(hwnd):
                window_text = ctypes.create_unicode_buffer(256)
                user32.GetWindowTextW(hwnd, window_text, 256)
                if window_text.value:
                    print(f"[FindWindow] Found window for PID {lParam}: hwnd={hwnd}, title='{window_text.value}'", 
                          file=sys.stderr, flush=True)
                    windows.append(hwnd)
        return True
    
    # Try to find window for this PID
    windows = []
    callback_type = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
    user32.EnumWindows(callback_type(enum_windows_callback), pid)
    
    if windows:
        return windows[0]
    
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
                    print(f"[FindWindow] Reached end of parent chain", file=sys.stderr, flush=True)
                    break
                
                parent_pid = parent.pid
                print(f"[FindWindow] Trying parent PID {parent_pid} ({parent.name()})", 
                      file=sys.stderr, flush=True)
                
                # Search for window with parent PID
                windows = []
                user32.EnumWindows(callback_type(enum_windows_callback), parent_pid)
                
                if windows:
                    return windows[0]
                
                current_pid = parent_pid
                
            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                print(f"[FindWindow] Error accessing parent: {e}", file=sys.stderr, flush=True)
                break
                
    except ImportError:
        print(f"[FindWindow] psutil not available", file=sys.stderr, flush=True)
    except Exception as e:
        print(f"[FindWindow] Error: {e}", file=sys.stderr, flush=True)
    
    print(f"[FindWindow] No window found for PID {pid}", file=sys.stderr, flush=True)
    return None

# ============================================================================
# Window Control Functions
# ============================================================================

def minimize_window(pid):
    """Minimize window to taskbar"""
    print(f"[MinimizeWindow] PID {pid}", file=sys.stderr, flush=True)
    hwnd = find_window_by_pid(pid)
    
    if hwnd:
        result = user32.ShowWindow(hwnd, SW_MINIMIZE)
        print(f"[MinimizeWindow] Result: {result}", file=sys.stderr, flush=True)
        return True
    
    print(f"[MinimizeWindow] Failed: No window found", file=sys.stderr, flush=True)
    return False


def maximize_window(pid):
    """Maximize window to full screen"""
    hwnd = find_window_by_pid(pid)
    
    if hwnd:
        user32.ShowWindow(hwnd, SW_SHOWMAXIMIZED)
        return True
    
    return False


def restore_window(pid):
    """Restore window from minimized/maximized state"""
    print(f"[RestoreWindow] PID {pid}", file=sys.stderr, flush=True)
    hwnd = find_window_by_pid(pid)
    
    if hwnd:
        result1 = user32.ShowWindow(hwnd, SW_RESTORE)
        result2 = user32.SetForegroundWindow(hwnd)
        print(f"[RestoreWindow] ShowWindow: {result1}, SetForeground: {result2}", 
              file=sys.stderr, flush=True)
        return True
    
    print(f"[RestoreWindow] Failed: No window found", file=sys.stderr, flush=True)
    return False


def activate_window(pid):
    """
    Activate window and bring to front
    
    This is the primary window activation function that:
    1. Restores the window if minimized
    2. Brings it to the foreground
    3. Sets it to always-on-top
    """
    print(f"[ActivateWindow] PID {pid}", file=sys.stderr, flush=True)
    hwnd = find_window_by_pid(pid)
    
    if hwnd:
        # Restore from minimized/maximized
        result1 = user32.ShowWindow(hwnd, SW_RESTORE)
        
        # Bring to foreground
        result2 = user32.SetForegroundWindow(hwnd)
        result3 = user32.BringWindowToTop(hwnd)
        
        # Set to always-on-top
        result4 = user32.SetWindowPos(
            hwnd,
            HWND_TOPMOST,
            0, 0, 0, 0,
            SWP_NOMOVE | SWP_NOSIZE
        )
        
        print(f"[ActivateWindow] Results - Restore: {result1}, Foreground: {result2}, "
              f"BringToTop: {result3}, Topmost: {result4}", file=sys.stderr, flush=True)
        return True
    
    print(f"[ActivateWindow] Failed: No window found", file=sys.stderr, flush=True)
    return False


def set_window_topmost(pid, topmost=True):
    """
    Set or remove always-on-top status
    
    Args:
        pid: Process ID
        topmost: True to set always-on-top, False to remove
    """
    print(f"[SetTopmost] PID {pid}, topmost={topmost}", file=sys.stderr, flush=True)
    hwnd = find_window_by_pid(pid)
    
    if hwnd:
        # First activate the window
        user32.ShowWindow(hwnd, SW_RESTORE)
        user32.SetForegroundWindow(hwnd)
        
        # Set topmost status
        hwnd_insert = HWND_TOPMOST if topmost else HWND_NOTOPMOST
        result = user32.SetWindowPos(
            hwnd,
            hwnd_insert,
            0, 0, 0, 0,
            SWP_NOMOVE | SWP_NOSIZE
        )
        
        print(f"[SetTopmost] Result: {result}", file=sys.stderr, flush=True)
        return bool(result)
    
    print(f"[SetTopmost] Failed: No window found", file=sys.stderr, flush=True)
    return False


def hide_window(pid):
    """Hide window (not minimized, completely hidden)"""
    hwnd = find_window_by_pid(pid)
    
    if hwnd:
        user32.ShowWindow(hwnd, SW_HIDE)
        return True
    
    return False


def show_window(pid):
    """Show previously hidden window"""
    hwnd = find_window_by_pid(pid)
    
    if hwnd:
        user32.ShowWindow(hwnd, SW_SHOW)
        return True
    
    return False


def get_window_state(pid):
    """
    Get current window state
    
    Returns:
        'minimized', 'maximized', 'normal', or 'not_found'
    """
    hwnd = find_window_by_pid(pid)
    
    if hwnd:
        if user32.IsIconic(hwnd):
            return "minimized"
        elif user32.IsZoomed(hwnd):
            return "maximized"
        else:
            return "normal"
    
    return "not_found"

# ============================================================================
# Command Line Interface
# ============================================================================

def main():
    """CLI entry point for testing"""
    if len(sys.argv) < 3:
        print("Usage: window_control.py <pid> <action>")
        print("Actions: minimize, maximize, restore, activate, hide, show, state, topmost, notopmost")
        sys.exit(1)
    
    try:
        pid = int(sys.argv[1])
        action = sys.argv[2].lower()
    except ValueError:
        print(f"Error: Invalid PID: {sys.argv[1]}")
        sys.exit(1)
    
    actions = {
        "minimize": (minimize_window, "Minimize"),
        "maximize": (maximize_window, "Maximize"),
        "restore": (restore_window, "Restore"),
        "activate": (activate_window, "Activate"),
        "hide": (hide_window, "Hide"),
        "show": (show_window, "Show"),
        "topmost": (lambda p: set_window_topmost(p, True), "Set Topmost"),
        "notopmost": (lambda p: set_window_topmost(p, False), "Remove Topmost"),
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

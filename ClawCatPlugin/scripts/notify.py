#!/usr/bin/env python3
"""
Claude Code Hook Script for ClawCat Terminal Agent
Intercepts Claude events and sends notifications to the cat UI server
Cross-platform support: Windows & macOS
"""
import sys
import json
import os
import platform
import requests

# ============================================================================
# Configuration
# ============================================================================
CAT_SERVER_URL = "http://localhost:22622/claude-hook"
BLOCKING_TIMEOUT = 90      # Wait for user interaction (ask_permission, ask_user)
NONBLOCKING_TIMEOUT = 0.1  # Fire-and-forget visual updates
PLATFORM = platform.system()  # 'Windows', 'Darwin', 'Linux'

# ============================================================================
# Core Functions
# ============================================================================

def get_terminal_pid():
    """
    Find the terminal PID by recursively searching parent processes
    Cross-platform: supports Windows Terminal, macOS Terminal, iTerm2
    """
    try:
        import psutil
        current = psutil.Process(os.getpid())
        
        # Search up to 10 levels in process tree
        for _ in range(10):
            try:
                parent = current.parent()
                if not parent or parent.pid == current.pid:
                    break
                
                name = parent.name().lower()
                
                # Platform-specific terminal detection
                if PLATFORM == 'Windows':
                    # Windows Terminal
                    if 'windowsterminal' in name or 'wt.exe' in name:
                        return parent.pid
                elif PLATFORM == 'Darwin':
                    # macOS: Terminal.app, iTerm2, Warp, Alacritty
                    if any(term in name for term in ['terminal', 'iterm2', 'warp', 'alacritty']):
                        return parent.pid
                else:
                    # Linux: common terminals
                    if any(term in name for term in ['gnome-terminal', 'konsole', 'xterm', 'alacritty']):
                        return parent.pid
                
                current = parent
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                break
    except (ImportError, Exception):
        pass
    
    # Fallback to environment variable or 0
    return int(os.environ.get("TERMINAL_PID", 0))


def read_hook_context():
    """Read hook input from stdin and parse as JSON
    
    Returns:
        tuple: (parsed_context, raw_input_string)
    """
    try:
        raw_input = sys.stdin.read()
        if raw_input and raw_input.strip():
            parsed = json.loads(raw_input)
            return parsed, raw_input
    except (json.JSONDecodeError, Exception):
        pass
    return {}, ""


def truncate_text(text, max_length=40):
    """Truncate text and add ellipsis if needed"""
    if len(text) > max_length:
        return text[:max_length] + "..."
    return text


def send_payload(payload, timeout):
    """Send payload to cat server and return response with graceful degradation"""
    try:
        response = requests.post(CAT_SERVER_URL, json=payload, timeout=timeout)
        return response if response.status_code == 200 else None
    except requests.exceptions.ConnectionError:
        # Service not running - fail silently for non-blocking hooks
        if payload.get("mode") == "fire_and_forget":
            return None
        # For blocking hooks, output helpful message
        print(json.dumps({
            "hookSpecificOutput": {
                "message": "ClawCat service not running. Start with: /clawcat:start"
            }
        }))
        return None
    except requests.exceptions.Timeout:
        # Expected when user takes too long
        return None
    except Exception as e:
        # Only log unexpected errors
        if "Connection" not in str(e) and "timeout" not in str(e).lower():
            print(f"Error: {e}", file=sys.stderr)
        return None


def handle_blocking_response(hook_type, decision, context):
    """
    Process user decision from frontend and output to Claude
    
    __IGNORE__ marker means: local operation, don't send anything to Claude
    - User jumped to terminal
    - User is slacking (not responding)
    - Other local-only actions
    """
    choice = decision.get("choice", "")
    user_input = decision.get("user_input", "")
    
    # Check if this is a local-only operation
    if choice == "__IGNORE__" or user_input == "__IGNORE__":
        return
    
    # Handle permission request
    if hook_type == "PermissionRequest":
        behavior = "deny"  # Default to deny for safety
        
        if choice == "always":
            behavior = "allow"
            suggestions = context.get("permission_suggestions", []) or context.get("suggestions", [])
            output = {"behavior": behavior}
            if suggestions:
                output["updatedPermissions"] = suggestions
        elif choice == "allow":
            behavior = "allow"
            output = {"behavior": behavior}
        else:
            output = {"behavior": "deny"}
        
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PermissionRequest",
                "decision": output
            }
        }))
    
    # Handle user input request
    elif hook_type == "Notification":
        if user_input and user_input.strip():
            print(json.dumps({
                "hookSpecificOutput": {
                    "hookEventName": "Notification",
                    "additionalContext": user_input
                }
            }))


# ============================================================================
# Hook Handlers
# ============================================================================

def handle_user_prompt_submit(context, pid):
    """Handle UserPromptSubmit: User sent a message to Claude"""
    prompt_text = context.get("prompt", "") or context.get("user_prompt", "")
    caption = truncate_text(prompt_text, 40) if prompt_text else "Thinking..."
    
    return {
        "pid": pid,
        "mode": "fire_and_forget",
        "action": "set_state",
        "data": {
            "state": "working",
            "caption": "Thinking..."
        }
    }, NONBLOCKING_TIMEOUT


def handle_pre_tool_use(context, pid):
    """Handle PreToolUse: Claude is about to use a tool"""
    # Extract tool name from various possible locations
    tool_input = context.get("tool_input", {})
    if isinstance(tool_input, dict):
        tool_name = tool_input.get("tool_name") or tool_input.get("tool") or "Tool"
    else:
        tool_name = context.get("tool_name") or context.get("tool", "Tool")
    
    return {
        "pid": pid,
        "mode": "fire_and_forget",
        "action": "set_state",
        "data": {
            "state": "working",
            "caption": f"Run: {tool_name}"
        }
    }, NONBLOCKING_TIMEOUT


def handle_post_tool_use(context, pid):
    """Handle PostToolUse: Tool execution completed, pulse the cat"""
    result = context.get("result", "") or context.get("tool_result", "")
    intensity = min(len(str(result)) // 100, 10)  # Cap at 10
    
    return {
        "pid": pid,
        "mode": "fire_and_forget",
        "action": "pulse",
        "data": {
            "intensity": intensity
        }
    }, NONBLOCKING_TIMEOUT


def handle_stop(context, pid):
    """Handle Stop: Session ended"""
    return {
        "pid": pid,
        "mode": "fire_and_forget",
        "action": "set_state",
        "data": {
            "state": "resting",
            "caption": f"Session {pid} stopped!"
        }
    }, NONBLOCKING_TIMEOUT


def handle_permission_request(context, pid):
    """Handle PermissionRequest: Claude needs user permission"""
    message = context.get("message", "") or context.get("permission_message", "Permission Request")
    tool_name = context.get("tool_name", "")
    tool_input = context.get("tool_input", {})
    
    # Extract description from tool_input if available
    description = ""
    if isinstance(tool_input, dict):
        description = tool_input.get("description", "") or tool_input.get("command", "")
    
    # Check if it's AskUserQuestion - only show jump button
    if tool_name == "AskUserQuestion":
        return {
            "pid": pid,
            "mode": "blocking",
            "action": "ask_permission",
            "data": {
                "caption": f"Allow? {message}",
                "can_always": False,
                "jump_only": True  # Flag to show only jump button
            }
        }, BLOCKING_TIMEOUT
    
    # Use description if available, otherwise use message
    if description:
        display_text = description
    else:
        # Clean up message
        clean_msg = message.replace("Claude wants to ", "").replace("Claude would like to ", "")
        display_text = truncate_text(clean_msg, 30)
    
    suggestions = context.get("permission_suggestions", []) or context.get("suggestions", [])
    
    return {
        "pid": pid,
        "mode": "blocking",
        "action": "ask_permission",
        "data": {
            "caption": f"Allow? {display_text}",
            "can_always": len(suggestions) > 0
        }
    }, BLOCKING_TIMEOUT


def handle_notification(context, pid):
    """Handle Notification: Claude needs user input - non-blocking, just notify"""
    # Notification is now non-blocking, just notify UI and return immediately
    return {
        "pid": pid,
        "mode": "fire_and_forget",
        "action": "notification_need",
        "data": {
            "caption": "Notification need",
            "type": "jump"
        }
    }, NONBLOCKING_TIMEOUT


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    # Get hook type from environment or context
    hook_type = os.environ.get("CLAUDE_HOOK_TYPE", "")
    context, raw_input = read_hook_context()
    
    if not hook_type and "hook_event_name" in context:
        hook_type = context.get("hook_event_name", "")
    
    # Get terminal PID
    pid = get_terminal_pid()
    
    # Dispatch to appropriate handler
    handlers = {
        "UserPromptSubmit": handle_user_prompt_submit,
        "PreToolUse": handle_pre_tool_use,
        "PostToolUse": handle_post_tool_use,
        "Stop": handle_stop,
        "PermissionRequest": handle_permission_request,
        "Notification": handle_notification,
    }
    
    handler = handlers.get(hook_type)
    if not handler:
        # Unknown hook type, ignore
        sys.exit(0)
    
    # Build payload and send
    payload, timeout = handler(context, pid)
    
    # Add raw hook input for debugging
    if raw_input:
        try:
            # Parse raw input as JSON to include it in payload
            payload["raw_input"] = json.loads(raw_input)
        except (json.JSONDecodeError, Exception):
            # If parsing fails, include raw string (first 1000 chars to avoid payload size issues)
            payload["raw_input"] = raw_input[:1000] if len(raw_input) > 1000 else raw_input
    
    response = send_payload(payload, timeout)
    
    # Handle blocking responses
    if payload["mode"] == "blocking" and response:
        try:
            response_data = response.json()
            handle_blocking_response(hook_type, response_data, context)
        except (json.JSONDecodeError, Exception):
            pass
    
    sys.exit(0)


if __name__ == "__main__":
    main()

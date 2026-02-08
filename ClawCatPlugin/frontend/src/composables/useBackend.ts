import { ref } from 'vue'

// ============================================================================
// Configuration
// ============================================================================
const SERVER_URL = 'http://127.0.0.1:22622'

// ============================================================================
// Type Definitions
// ============================================================================
export interface BackendStatus {
  mode: 'slacking' | 'spying'
  pid: number
  state: 'resting' | 'working' | 'confirming'
  message: string
  hook_payload?: HookPayload
  hook_type?: string
  hook_action?: string
}

export interface HookPayload {
  type?: string
  mode?: string
  pid?: number
  choice?: string
  user_input?: string
  timeout?: number
  data?: {
    caption?: string
    can_always?: boolean
    [key: string]: any
  }
  [key: string]: any
}

// ============================================================================
// Composable
// ============================================================================
export function useBackend() {
  // Reactive state
  const currentStatus = ref<BackendStatus>({
    mode: 'slacking',
    pid: 0,
    state: 'resting',
    message: 'Standing by...',
    hook_payload: undefined,
    hook_type: undefined,
    hook_action: undefined
  })

  // --------------------------------------------------------------------------
  // HTTP Helper
  // --------------------------------------------------------------------------
  async function apiRequest(
    endpoint: string,
    method: 'GET' | 'POST' = 'GET',
    body?: any
  ): Promise<any> {
    try {
      const options: RequestInit = { method }
      
      if (body) {
        options.headers = { 'Content-Type': 'application/json' }
        options.body = JSON.stringify(body)
      }
      
      const response = await fetch(`${SERVER_URL}${endpoint}`, options)
      
      if (response.ok) {
        return await response.json()
      }
      
      // Only log non-status endpoint errors (status polling failures are expected)
      if (endpoint !== '/status') {
        console.error(`API request failed: ${endpoint}, status: ${response.status}`)
      }
      return null
    } catch (error) {
      // Only log non-status endpoint errors (status polling failures are expected)
      if (endpoint !== '/status') {
        console.error(`API request error: ${endpoint}`, error)
      }
      return null
    }
  }

  // --------------------------------------------------------------------------
  // Status Management
  // --------------------------------------------------------------------------
  
  /**
   * Fetch current backend status (mode, state, hook payload)
   */
  async function fetchStatus(): Promise<BackendStatus | null> {
    const data = await apiRequest('/status')
    
    if (data) {
      currentStatus.value = {
        mode: data.mode || 'slacking',
        pid: data.pid || 0,
        state: data.state || 'resting',
        message: data.message || 'Standing by...',
        hook_payload: data.hook_payload,
        hook_type: data.hook_type,
        hook_action: data.hook_action
      }
      return currentStatus.value
    }
    
    return null
  }

  // --------------------------------------------------------------------------
  // Mode Management
  // --------------------------------------------------------------------------
  
  /**
   * Toggle between slacking and spying modes
   * Also activates/minimizes terminal window
   */
  async function toggleMode(): Promise<boolean> {
    const data = await apiRequest('/toggle-mode', 'POST')
    
    if (data) {
      currentStatus.value.mode = data.mode || 'slacking'
      currentStatus.value.pid = data.pid || 0
      return true
    }
    
    return false
  }

  /**
   * Toggle monitor mode with status refresh
   */
  async function toggleMonitor(): Promise<boolean> {
    const success = await toggleMode()
    
    if (success) {
      // Wait for backend to complete
      await new Promise(resolve => setTimeout(resolve, 100))
      // Refresh status
      await fetchStatus()
      return true
    }
    
    return false
  }

  // --------------------------------------------------------------------------
  // Terminal Control
  // --------------------------------------------------------------------------
  
  /**
   * Activate terminal window (restore + focus + topmost)
   */
  async function activateTerminal(): Promise<boolean> {
    const data = await apiRequest('/activate-terminal', 'POST')
    return data?.success === true
  }

  /**
   * Set window always-on-top status
   */
  async function setWindowTopmost(topmost: boolean = true): Promise<boolean> {
    const data = await apiRequest('/set-topmost', 'POST', { topmost })
    return data?.success === true
  }

  /**
   * Execute command in terminal
   */
  async function executeCommand(mode: 'slacking' | 'spying', command?: string): Promise<boolean> {
    const data = await apiRequest('/execute-command', 'POST', {
      mode,
      command: command || ''
    })
    return data?.success === true
  }

  // --------------------------------------------------------------------------
  // Hook Response
  // --------------------------------------------------------------------------
  
  /**
   * Send user response to blocking hook (permission/input request)
   * 
   * @param choice - User choice: 'allow', 'deny', 'always', '__IGNORE__'
   * @param userInput - User text input (for ask_user hooks)
   */
  async function sendHookResponse(choice: string, userInput?: string): Promise<boolean> {
    const payload: any = { choice }
    
    // Add user_input if provided (for Notification hooks)
    if (userInput !== undefined) {
      payload.user_input = userInput || null
    }
    
    console.log('📤 Sending hook response:', payload)
    const success = await apiRequest('/hook-response', 'POST', payload)
    console.log('📥 Hook response result:', success ? 'OK' : 'Failed')
    
    return !!success
  }

  /**
   * Move window to specified position (for drag support)
   */
  async function moveWindow(x: number, y: number): Promise<boolean> {
    const data = await apiRequest('/move-window', 'POST', { x, y })
    return data?.success === true
  }

  // --------------------------------------------------------------------------
  // Public API
  // --------------------------------------------------------------------------
  return {
    // State
    currentStatus,

    // Actions
    fetchStatus,
    toggleMode,
    toggleMonitor,
    activateTerminal,
    setWindowTopmost,
    sendHookResponse,
    executeCommand,
    moveWindow
  }
}

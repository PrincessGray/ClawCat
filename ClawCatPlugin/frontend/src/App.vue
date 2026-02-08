<template>
  <div class="clawcat-app">
    <!-- 拖拽层 - 覆盖整个窗口用于拖拽 -->
    <div class="drag-layer" @mousedown="handleDragStart"></div>
    <!-- 背景图片 -->
    <img
      v-if="backgroundImagePath"
      class="background-image"
      :src="backgroundImagePath"
      alt=""
    />
    
    <!-- Live2D Canvas -->
    <canvas id="live2dCanvas" />
    
    <!-- 按键图片（当按键被按下时显示） -->
    <img
      v-for="path in Object.values(pressedKeys)"
      :key="path"
      class="key-image"
      :src="path"
      alt=""
    />
    
    <!-- Spying 模式下的工作状态提示（3秒自动消失，点击跳转） -->
    <div v-if="showWorkingNotification" class="working-notification" @click.stop="handleNotificationClick">
      <div class="working-content">
        <div class="working-icon">{{ workingNotificationIcon }}</div>
        <div class="working-message">{{ workingNotificationMessage }}</div>
      </div>
    </div>
    
    <!-- Confirming 状态下的输入和按钮 -->
    <div v-if="currentMode === 'spying' && currentState === 'confirming'" class="confirming-panel" @click.stop>
      <!-- PermissionRequest: 显示"是否允许：context" -->
      <div v-if="confirmingType === 'ask_permission'" class="confirming-content">
        <div class="confirming-message">是否允许：{{ confirmingContext }}</div>
        <div class="confirming-buttons">
          <!-- AskUserQuestion: 只显示跳转按钮 -->
          <template v-if="jumpOnly">
            <button class="confirming-btn cancel" @click.stop="handleNotificationCancel">
              跳转
            </button>
          </template>
          <!-- 普通权限请求：显示允许/拒绝按钮 -->
          <template v-else>
            <button 
              v-if="canAlways" 
              class="confirming-btn always" 
              @click.stop="handleConfirm('always')"
            >
              总是允许
            </button>
            <button class="confirming-btn allow" @click.stop="handleConfirm('allow')">
              允许
            </button>
            <button class="confirming-btn deny" @click.stop="handleConfirm('deny')">
              拒绝
            </button>
            <button 
              v-if="!canAlways" 
              class="confirming-btn cancel" 
              @click.stop="handleNotificationCancel"
            >
              跳转
            </button>
          </template>
        </div>
      </div>
      
      <!-- Notification: 显示 context + 输入框或直接跳转 -->
      <div v-else-if="confirmingType === 'ask_user'" class="confirming-content">
        <div class="confirming-message">{{ confirmingContext }}</div>
        <!-- 通用提示：只显示跳转按钮 -->
        <div v-if="needsJumpOnly" class="confirming-buttons">
          <button class="confirming-btn cancel" @click.stop="handleNotificationCancel">
            跳转
          </button>
        </div>
        <!-- 需要输入：显示输入框 -->
        <template v-else>
          <div class="confirming-input-section">
            <input
              v-model="userInput"
              type="text"
              class="confirming-input"
              placeholder="请输入内容"
              @keyup.enter="handleNotificationSubmit"
              autofocus
            />
          </div>
          <div class="confirming-buttons">
            <button class="confirming-btn submit" @click.stop="handleNotificationSubmit">
              发送给claude
            </button>
            <button class="confirming-btn cancel" @click.stop="handleNotificationCancel">
              跳转
            </button>
          </div>
        </template>
      </div>
      
      <!-- 未知类型的 confirming 请求 -->
      <div v-else class="confirming-content">
        <div class="confirming-message error">⚠️ 未知的确认类型</div>
        <div class="confirming-context">{{ confirmingContext || '等待后端响应...' }}</div>
        <div class="confirming-buttons">
          <button class="confirming-btn deny" @click.stop="handleUnknownConfirm">
            取消并跳转
          </button>
        </div>
      </div>
    </div>

          <!-- 左下角切换模式按钮 -->
          <button class="monitor-toggle-btn" @click.stop="handleToggleMonitor">
            {{ currentMode === 'slacking' ? 'Slacking' : 'Spying' }}
          </button>

    <!-- 测试控制面板（开发用，按 T 键显示/隐藏） -->
    <div v-if="showTestPanel" class="test-panel" @click.stop>
      <div class="test-title">测试控制</div>
      
      <div class="test-section">
        <div class="test-label">模式：</div>
            <button class="test-btn" @click.stop="toggleMode">
              {{ currentMode === 'slacking' ? 'Slacking' : 'Spying' }}
            </button>
      </div>
      
      <div class="test-section">
        <div class="test-label">状态：</div>
        <button class="test-btn" @click.stop="toggleState">
          {{ currentState }}
        </button>
      </div>

      <div class="test-section">
        <div class="test-label">测试按键：</div>
        <button class="test-btn small" @click.stop="testKeyPress('KeyA')">A</button>
        <button class="test-btn small" @click.stop="testKeyPress('Space')">Space</button>
        <button class="test-btn small" @click.stop="testKeyRelease">释放</button>
      </div>
      
      <div class="test-section">
        <div class="test-label">测试 Confirming：</div>
        <button class="test-btn small" @click.stop="testPermissionRequest">权限请求</button>
        <button class="test-btn small" @click.stop="testNotification">用户输入</button>
      </div>
      
      <div class="test-section">
        <button class="test-btn" @click.stop="showTestPanel = false">关闭</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useModeState } from './composables/useModeState'
import { useModel } from './composables/useModel'
import { useBackend } from './composables/useBackend'

const { handleDestroy } = useModel()

// 使用统一的模式和状态管理
const {
  currentMode,
  currentState,
  showTestPanel,
  pressedKeys,
  backgroundImagePath,
  toggleMode,
  toggleState,
  testKeyPress,
  testKeyRelease,
  updateModeBehavior,
  stopAgentActions,
  stopSpyStickControl,
  handleResize,
  setMode,
  setState,
} = useModeState()

// 后端通信
const { currentStatus, fetchStatus, toggleMonitor, sendHookResponse, activateTerminal, setWindowTopmost, moveWindow } = useBackend()

// 窗口拖拽相关
const isDragging = ref(false)
const dragStartX = ref(0)
const dragStartY = ref(0)
const windowStartX = ref(0)
const windowStartY = ref(0)

// 开始拖拽
function handleDragStart(event: MouseEvent) {
  // 只响应左键
  if (event.button !== 0) return

  isDragging.value = true
  dragStartX.value = event.screenX
  dragStartY.value = event.screenY
  // 获取当前窗口位置
  windowStartX.value = window.screenX
  windowStartY.value = window.screenY

  // 添加全局事件监听
  document.addEventListener('mousemove', handleDragMove)
  document.addEventListener('mouseup', handleDragEnd)

  event.preventDefault()
}

// 拖拽移动
function handleDragMove(event: MouseEvent) {
  if (!isDragging.value) return

  const deltaX = event.screenX - dragStartX.value
  const deltaY = event.screenY - dragStartY.value

  const newX = windowStartX.value + deltaX
  const newY = windowStartY.value + deltaY

  // 发送移动请求到后端
  moveWindow(newX, newY)
}

// 结束拖拽
function handleDragEnd() {
  isDragging.value = false
  document.removeEventListener('mousemove', handleDragMove)
  document.removeEventListener('mouseup', handleDragEnd)
}

// Confirming 状态相关
const confirmingMessage = ref('等待确认...')
const confirmingContext = ref('')
const confirmingType = ref<'ask_permission' | 'ask_user' | null>(null)
const canAlways = ref(false)
const userInput = ref('')
const needsJumpOnly = ref(false) // 标记是否需要直接跳转（通用提示）
const jumpOnly = ref(false) // 标记是否只显示跳转按钮（AskUserQuestion）

// Working 状态提示（spying 模式下显示）
const showWorkingNotification = ref(false)
const workingNotificationMessage = ref('')
const workingNotificationIcon = ref('⚡')
const isSessionStopped = ref(false)
let workingNotificationTimer: number | null = null

// 处理确认（允许/拒绝/总是允许）
async function handleConfirm(choice: 'allow' | 'deny' | 'always') {
  console.log('🔘 handleConfirm called with choice:', choice)
  
  // 立即切换到 resting 状态
  setState('resting')
  userInput.value = ''
  confirmingMessage.value = '等待确认...'
  confirmingContext.value = ''
  confirmingType.value = null
  canAlways.value = false
  needsJumpOnly.value = false
  jumpOnly.value = false
  
  const success = await sendHookResponse(choice)
  console.log('📡 sendHookResponse result:', success)
  if (!success) {
    console.error('❌ Failed to send response')
  }
}

// 处理通知提交（输入文本）
async function handleNotificationSubmit() {
  const input = userInput.value.trim()
  if (!input) {
    return // 不允许空输入
  }
  
  // 立即切换到 resting 状态
  setState('resting')
  userInput.value = ''
  confirmingMessage.value = '等待确认...'
  confirmingContext.value = ''
  confirmingType.value = null
  needsJumpOnly.value = false
  
  const success = await sendHookResponse('allow', input)
  if (!success) {
    console.error('❌ Failed to send response')
  }
}

// 处理通知跳转（跳转到 terminal）
async function handleNotificationCancel() {
  console.log('🔄 User chose to jump to terminal (sending IGNORE)')
  
  // 立即切换到 resting 状态
  setState('resting')
  userInput.value = ''
  confirmingMessage.value = '等待确认...'
  confirmingContext.value = ''
  confirmingType.value = null
  needsJumpOnly.value = false
  
  // 发送 __IGNORE__ 标记（不向 Claude 输出，本地操作）
  const success = await sendHookResponse('__IGNORE__', '__IGNORE__')
  if (!success) {
    console.warn('⚠️ Failed to send ignore response, continuing anyway')
  }
  
  // 激活 terminal 窗口（会自动置顶）
  console.log('🖱️ Activating terminal window...')
  const activated = await activateTerminal()
  if (activated) {
    console.log('✅ Terminal window activated and set to topmost')
  } else {
    console.error('❌ Failed to activate terminal window')
  }
}

// 处理未知类型确认（取消并跳转）
async function handleUnknownConfirm() {
  console.log('⚠️ Handling unknown confirming type, jumping to terminal (sending IGNORE)')
  
  // 立即切换到 resting 状态
  setState('resting')
  userInput.value = ''
  confirmingMessage.value = '等待确认...'
  confirmingContext.value = ''
  confirmingType.value = null
  canAlways.value = false
  needsJumpOnly.value = false
  jumpOnly.value = false
  
  // 发送 __IGNORE__ 标记（不向 Claude 输出）
  const success = await sendHookResponse('__IGNORE__', '__IGNORE__')
  if (!success) {
    console.warn('⚠️ Failed to send ignore response, continuing anyway')
  }
  
  // 激活 terminal 窗口（会自动置顶）
  console.log('🖱️ Activating terminal window...')
  const activated = await activateTerminal()
  if (activated) {
    console.log('✅ Terminal window activated and set to topmost')
  } else {
    console.error('❌ Failed to activate terminal window')
  }
}

// 显示工作状态提示（3秒后自动消失）
function showWorkingNotificationToast(message: string, sessionStopped: boolean = false) {
  // 清除之前的定时器
  if (workingNotificationTimer) {
    clearTimeout(workingNotificationTimer)
  }
  
  // 解析图标和消息
  let icon = '⚡'
  let text = message
  
  if (message.startsWith('🛑')) {
    icon = '🛑'
    text = message.substring(2).trim()
  }
  
  // 显示提示
  workingNotificationIcon.value = icon
  workingNotificationMessage.value = text
  isSessionStopped.value = sessionStopped
  showWorkingNotification.value = true
  console.log('💬 Showing working notification:', text, 'sessionStopped:', sessionStopped)
  
  // 3秒后自动隐藏（session stopped 需要用户点击）
  if (!sessionStopped) {
    workingNotificationTimer = window.setTimeout(() => {
      showWorkingNotification.value = false
      isSessionStopped.value = false
      console.log('💬 Hiding working notification')
    }, 3000)
  }
}

// 处理通知点击
async function handleNotificationClick() {
  if (isSessionStopped.value) {
    console.log('🖱️ Notification clicked - jumping to terminal')
    showWorkingNotification.value = false
    isSessionStopped.value = false
    
    // Session stopped 或 notification_need 时不需要发送响应（已经结束了或 fire_and_forget）
    // 直接激活窗口（会自动置顶）
    const activated = await activateTerminal()
    if (activated) {
      console.log('✅ Terminal window activated and set to topmost')
    } else {
      console.error('❌ Failed to activate terminal window')
    }
  }
}

// 切换模式
async function handleToggleMonitor() {
  console.log('handleToggleMonitor called, current mode:', currentMode.value)
  const success = await toggleMonitor()
  console.log('toggleMonitor result:', success)
  if (success) {
    // 同步模式到前端
    await fetchStatus()
    console.log('Fetched status, mode:', currentStatus.value.mode)
    if (currentStatus.value.mode) {
      setMode(currentStatus.value.mode)
      console.log('Set mode to:', currentMode.value)
    }
  } else {
    console.error('Failed to toggle mode')
  }
}

// 测试 PermissionRequest（权限请求）
function testPermissionRequest() {
  console.log('测试 PermissionRequest')
  // 模拟后端发送的 hook payload
  setState('confirming')
  confirmingType.value = 'ask_permission'
  confirmingContext.value = '访问文件系统'
  canAlways.value = true
}

// 测试 Notification（用户输入）
function testNotification() {
  console.log('测试 Notification')
  // 模拟后端发送的 hook payload
  setState('confirming')
  confirmingType.value = 'ask_user'
  confirmingContext.value = '请输入内容'
  userInput.value = ''
}

// 定期获取后端状态（用于同步）
let statusPollInterval: number | null = null

// 监听后端状态变化
watch(() => currentStatus.value.mode, (newMode) => {
  if (newMode && currentMode.value !== newMode) {
    setMode(newMode)
  }
})

// 监听 working 状态下的 caption 变化
let lastWorkingCaption = ''

watch(() => currentStatus.value.state, (newState, oldState) => {
  if (newState && currentState.value !== newState) {
    setState(newState)
  }
  
  // 检测切换到 resting 状态（session stopped 或 notification_need）
  if (newState === 'resting' && oldState !== 'resting' && currentMode.value === 'spying') {
    if (currentStatus.value.hook_payload) {
      const payload = currentStatus.value.hook_payload
      const action = payload.action || ''
      
      // 检测 notification_need
      if (action === 'notification_need') {
        console.log('📍 Notification need detected, showing notification (click to jump)')
        showWorkingNotificationToast('🔔 Notification need (点击跳转)', true)
        return
      }
      
      // 检查是否是 session stopped
      const data = payload.data || {}
      const caption = (data.caption || '').toLowerCase()
      
      // 检测 "stopped", "ended", "session" 等关键词
      if (caption.includes('stopped') || caption.includes('ended') || caption.includes('session')) {
        console.log('📍 Session stopped detected, showing notification (click to jump)')
        showWorkingNotificationToast('🛑 Session Stopped (点击跳转)', true)
      }
    }
  }
  
  // 清除 caption 缓存（如果不是 working 状态）
  if (newState !== 'working') {
    lastWorkingCaption = ''
  }
  
  // 更新 confirming 消息和类型
  if (newState === 'confirming' && currentStatus.value.hook_payload) {
    const payload = currentStatus.value.hook_payload
    const action = currentStatus.value.hook_action || currentStatus.value.hook_type
    
    console.log('📋 Confirming state detected, action:', action, 'payload:', payload)
    
    if (action === 'ask_permission') {
      // PermissionRequest: 提取 context（从 caption 中移除 "Allow? " 前缀）
      confirmingType.value = 'ask_permission'
      const data = payload.data || {}
      let caption = data.caption || '需要权限确认'
      // 移除 "Allow? " 前缀（如果存在）
      if (caption.startsWith('Allow? ')) {
        caption = caption.substring(7)
      }
      confirmingContext.value = caption
      canAlways.value = data.can_always || false
      jumpOnly.value = data.jump_only || false
      console.log('✅ Set confirming type: ask_permission, context:', caption, 'canAlways:', canAlways.value, 'jumpOnly:', jumpOnly.value)
    } else if (action === 'ask_user') {
      // Notification: 显示 context
      confirmingType.value = 'ask_user'
      const data = payload.data || {}
      const caption = data.caption || '请输入内容'
      confirmingContext.value = caption
      
      // 检查是否是通用提示，需要直接跳转
      const genericPrompts = [
        'Claude Code needs your attention',
        'Claude needs your attention',
        'Input required',
        'Ready.'
      ]
      needsJumpOnly.value = genericPrompts.some(prompt => 
        caption.toLowerCase().includes(prompt.toLowerCase())
      )
      
      console.log('✅ Set confirming type: ask_user, context:', confirmingContext.value, 'needsJumpOnly:', needsJumpOnly.value)
    } else {
      // 未知类型，默认显示
      confirmingType.value = null
      confirmingContext.value = '需要确认操作'
      console.warn('⚠️ Unknown confirming action:', action, 'Available:', currentStatus.value)
    }
  } else if (newState !== 'confirming') {
    confirmingMessage.value = '等待确认...'
    confirmingContext.value = ''
    confirmingType.value = null
    canAlways.value = false
    needsJumpOnly.value = false
    jumpOnly.value = false
  }
})

// 单独监听 working 状态的 payload 变化（检测 caption 变化）
watch(() => {
  if (currentStatus.value.state === 'working' && currentStatus.value.hook_payload) {
    const payload = currentStatus.value.hook_payload
    const data = payload.data || {}
    return data.caption || ''
  }
  return ''
}, (newCaption) => {
  // Spying 模式下，caption 变化时立即显示
  if (newCaption && currentMode.value === 'spying' && newCaption !== lastWorkingCaption) {
    lastWorkingCaption = newCaption
    showWorkingNotificationToast(newCaption)
  }
})

// 单独监听 resting 状态的 notification_need
watch(() => {
  if (currentStatus.value.state === 'resting' && currentStatus.value.hook_payload) {
    const payload = currentStatus.value.hook_payload
    const action = payload.action || ''
    if (action === 'notification_need') {
      return 'notification_need'
    }
  }
  return ''
}, (newAction) => {
  // notification_need: show notification like session stop (click to jump)
  if (newAction === 'notification_need' && currentMode.value === 'spying') {
    showWorkingNotificationToast('🔔 Notification need (点击跳转)', true)
  }
})

// 加载 Live2D 模型
onMounted(async () => {
    try {
    window.addEventListener('resize', handleResize)

    // 初始化模式行为（会加载模型）
    await updateModeBehavior(true)

    // 获取后端状态
    await fetchStatus()
    if (currentStatus.value.mode) {
      setMode(currentStatus.value.mode)
    }
    if (currentStatus.value.state) {
      setState(currentStatus.value.state)
    } else {
      // 如果没有状态，确保初始状态启动动画
      // slacking 模式默认 resting 状态，应该启动摇杆控制
      if (currentMode.value === 'slacking') {
        console.log('🎮 Initial slacking mode: Ensuring stick control starts')
      }
    }

    // 定期获取后端状态（每 1s，减少服务器压力）
    statusPollInterval = window.setInterval(async () => {
      await fetchStatus()
    }, 1000)

    // 监听键盘事件：按 T 键显示/隐藏测试面板
    window.addEventListener('keydown', (e) => {
      if (e.key === 't' || e.key === 'T') {
        showTestPanel.value = !showTestPanel.value
      }
    })

    console.log('✅ Live2D model loaded successfully')
    console.log('💡 Press T to toggle test panel')
  } catch (error) {
    console.error('❌ Failed to load Live2D model:', error)
  }
})

onUnmounted(() => {
  handleDestroy()
  window.removeEventListener('resize', handleResize)
  stopAgentActions()
  stopSpyStickControl()
  if (statusPollInterval) {
    clearInterval(statusPollInterval)
  }
})
</script>

<style scoped>
.clawcat-app {
  width: 100%;
  height: 100%;
  position: relative;
  overflow: hidden;
  background: transparent;
  user-select: none;
  -webkit-user-drag: none;
  margin: 0;
  padding: 0;
}

/* 拖拽层 - 覆盖整个窗口 */
.drag-layer {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
  cursor: grab;
  -webkit-app-region: drag;
}

.drag-layer:active {
  cursor: grabbing;
}

.background-image,
#live2dCanvas,
.key-image {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  margin: 0;
  padding: 0;
  border: none;
  outline: none;
  display: block;
  pointer-events: none;
}

.background-image {
  z-index: 0;
  -webkit-user-drag: none;
  object-fit: cover;
  object-position: center;
}

#live2dCanvas {
  z-index: 1;
  margin: 0;
  padding: 0;
  border: none;
  outline: none;
}

.key-image {
  z-index: 2;
  pointer-events: none;
  -webkit-user-drag: none;
  object-fit: cover;
  object-position: center;
}

/* 测试面板样式 */
.test-panel {
  position: absolute;
  top: 10px;
  right: 10px;
  background: rgba(30, 30, 30, 0.95);
  border: 1px solid #444;
  border-radius: 8px;
  padding: 15px;
  z-index: 10000;
  min-width: 200px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
  pointer-events: auto;
}

.test-title {
  color: #fff;
  font-size: 14px;
  font-weight: bold;
  margin-bottom: 12px;
  text-align: center;
}

.test-section {
  margin-bottom: 10px;
}

.test-label {
  color: #aaa;
  font-size: 11px;
  margin-bottom: 5px;
}

.test-btn {
  background: #444;
  color: #fff;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  font-size: 11px;
  cursor: pointer;
  transition: background 0.2s;
  margin-right: 5px;
  margin-bottom: 5px;
  pointer-events: auto;
  user-select: none;
}

.test-btn:hover {
  background: #555;
}

.test-btn:active {
  background: #666;
}

.test-btn.small {
  padding: 4px 8px;
  font-size: 10px;
}

/* Confirming 面板样式 - Bongo Cat 风格 */
/* 工作状态提示 - 漫画风格对话框 */
.working-notification {
  position: absolute;
  top: 40px;
  left: 40px;
  z-index: 10000;
  pointer-events: auto;
  cursor: pointer;
  animation: slideInBounce 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

@keyframes slideInBounce {
  0% {
    opacity: 0;
    transform: translate(-20px, -20px) scale(0.8);
  }
  100% {
    opacity: 1;
    transform: translate(0, 0) scale(1);
  }
}

.working-content {
  position: relative;
  background: #ffffff;
  border: 4px solid #000000;
  border-radius: 24px;
  padding: 20px 32px;
  min-width: 280px;
  max-width: 500px;
  box-shadow: 6px 6px 0 rgba(0, 0, 0, 0.15);
  display: flex;
  align-items: center;
  gap: 16px;
  transition: all 0.2s ease;
}

/* 漫画风格气泡尾巴 */
.working-content::before {
  content: '';
  position: absolute;
  bottom: -15px;
  left: 30px;
  width: 20px;
  height: 20px;
  background: #ffffff;
  border-left: 3px solid #000000;
  border-bottom: 3px solid #000000;
  border-radius: 0 0 0 8px;
  transform: rotate(-10deg) skewX(-10deg);
}

/* 第二个尾巴（漫画风格多层效果） */
.working-content::after {
  content: '';
  position: absolute;
  bottom: -25px;
  left: 20px;
  width: 15px;
  height: 15px;
  background: #ffffff;
  border-left: 3px solid #000000;
  border-bottom: 3px solid #000000;
  border-radius: 0 0 0 6px;
  transform: rotate(-15deg) skewX(-15deg);
}

.working-icon {
  font-size: 32px;
  line-height: 1;
  animation: pulse 1s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.2);
  }
}

.working-message {
  color: #000000;
  font-size: 20px;
  font-weight: bold;
  line-height: 1.4;
  text-shadow: 0 0 1px rgba(0, 0, 0, 0.1);
}

.working-notification:hover .working-content {
  transform: scale(1.05);
  box-shadow: 6px 6px 0 rgba(0, 0, 0, 0.2);
}

/* Session Stopped 提示框样式（已删除，统一使用 working-notification） */
/* 保留注释以防需要恢复 */

.confirming-panel {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: #ffffff;
  border: 3px solid #000000;
  border-radius: 12px;
  padding: 24px;
  z-index: 10001;
  min-width: 400px;
  max-width: 600px;
  box-shadow: 4px 4px 0 rgba(0, 0, 0, 0.2);
  pointer-events: auto;
}

.confirming-message {
  color: #000000;
  font-size: 16px;
  margin-bottom: 20px;
  text-align: center;
  min-height: 24px;
  font-weight: bold;
  line-height: 1.4;
}

.confirming-message.error {
  color: #ff4444;
}

.confirming-context {
  color: #666666;
  font-size: 14px;
  margin-bottom: 20px;
  text-align: center;
  font-style: italic;
}

.confirming-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.confirming-input-section {
  margin: 0;
}

.confirming-input {
  width: 100%;
  padding: 12px;
  background: #ffffff;
  border: 2px solid #000000;
  border-radius: 8px;
  color: #000000;
  font-size: 14px;
  outline: none;
  box-sizing: border-box;
  font-family: inherit;
}

.confirming-input:focus {
  border-color: #00ffff;
  background: #f0ffff;
  box-shadow: 0 0 0 2px rgba(0, 255, 255, 0.3);
}

.confirming-buttons {
  display: flex;
  gap: 12px;
  justify-content: center;
}

.confirming-btn {
  flex: 1;
  padding: 12px 20px;
  border: 2px solid #000000;
  border-radius: 8px;
  font-size: 14px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.15s;
  pointer-events: auto;
  user-select: none;
  background: #ffffff;
  color: #000000;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.confirming-btn:hover {
  background: #f5f5f5;
  transform: translateY(-1px);
  box-shadow: 2px 2px 0 rgba(0, 0, 0, 0.2);
}

.confirming-btn:active {
  transform: translateY(0);
  box-shadow: 1px 1px 0 rgba(0, 0, 0, 0.2);
}

.confirming-btn.allow {
  background: #ffffff;
  color: #000000;
}

.confirming-btn.allow:hover {
  background: #00ffff;
  color: #000000;
  border-color: #00ffff;
}

.confirming-btn.allow:active {
  background: #00cccc;
  color: #000000;
}

.confirming-btn.deny {
  background: #ffffff;
  color: #000000;
}

.confirming-btn.deny:hover {
  background: #000000;
  color: #ffffff;
}

.confirming-btn.deny:active {
  background: #333333;
  color: #ffffff;
}

.confirming-btn.always {
  background: #ffffff;
  color: #000000;
}

.confirming-btn.always:hover {
  background: #00ffff;
  color: #000000;
  border-color: #00ffff;
}

.confirming-btn.always:active {
  background: #00cccc;
  color: #000000;
}

.confirming-btn.submit {
  background: #ffffff;
  color: #000000;
}

.confirming-btn.submit:hover {
  background: #00ffff;
  color: #000000;
  border-color: #00ffff;
}

.confirming-btn.submit:active {
  background: #00cccc;
  color: #000000;
}

.confirming-btn.cancel {
  background: #ffffff;
  color: #000000;
}

.confirming-btn.cancel:hover {
  background: #000000;
  color: #ffffff;
}

.confirming-btn.cancel:active {
  background: #333333;
  color: #ffffff;
}

/* Monitor 切换按钮（左下角）- Bongo Cat 风格 */
.monitor-toggle-btn {
  position: absolute;
  bottom: 10px;
  left: 10px;
  background: #ffffff;
  border: 3px solid #000000;  /* 边框加粗 (2px * 1.5 = 3px) */
  border-radius: 12px;  /* 圆角放大 (8px * 1.5 = 12px) */
  padding: 8px 16px;  /* 缩小边距 */
  color: #000000;
  font-size: 18px;  /* 字体放大 1.5 倍 (12px * 1.5 = 18px) */
  font-weight: bold;
  cursor: pointer;
  transition: all 0.15s;
  z-index: 10000;
  pointer-events: auto;
  user-select: none;
  text-transform: uppercase;
  letter-spacing: 0.75px;  /* 字间距放大 (0.5px * 1.5 = 0.75px) */
  box-shadow: 3px 3px 0 rgba(0, 0, 0, 0.25);  /* 阴影放大 */
}

.monitor-toggle-btn:hover {
  background: #00ffff;
  color: #000000;
  border-color: #00ffff;
  transform: translateY(-1.5px);  /* 悬停效果放大 */
  box-shadow: 4px 4px 0 rgba(0, 0, 0, 0.25);  /* 悬停阴影放大 */
}

.monitor-toggle-btn:active {
  background: #00cccc;
  transform: translateY(0);
  box-shadow: 1.5px 1.5px 0 rgba(0, 0, 0, 0.25);  /* 按下阴影放大 */
}
</style>

import { ref, computed, watch, type Ref } from 'vue'
import { useModel } from './useModel'
import { useStickControl } from './useStickControl'
import { useAgentActions } from './useAgentActions'
import { useResources } from './useResources'
import { useHandControl } from './useHandControl'
import { useLightningEffect } from './useLightningEffect'
import live2d from '../utils/live2d'

export function useModeState() {
  const { handleLoad, handleDestroy, handleResize } = useModel()

  // 模式状态
  const currentMode = ref<'slacking' | 'spying'>('slacking')
  const currentState = ref<'resting' | 'working' | 'confirming'>('resting')
  const showTestPanel = ref(false)

  // 根据模式动态选择模型路径
  const MODEL_PATH = computed(() => {
    // slacking 模式使用 gamepad 模型（摇杆）
    // spying 模式使用 standard 模型（键盘）
    return currentMode.value === 'slacking' ? '/models/gamepad' : '/models/standard'
  })

  const RESOURCES_PATH = computed(() => {
    return currentMode.value === 'slacking'
      ? '/models/gamepad/resources'
      : '/models/standard/resources'
  })

  // 按下的按键（key -> 图片路径）
  const pressedKeys = ref<Record<string, string>>({})

  // 初始化 composables
  const { stickActive, startSpyStickControl, stopSpyStickControl } = useStickControl(currentMode)
  const { supportKeys, backgroundImagePath, loadResources } = useResources(RESOURCES_PATH)
  const { startAgentAutoActions, stopAgentActions } = useAgentActions(
    currentMode,
    currentState,
    pressedKeys,
    supportKeys
  )

  // 手部控制
  useHandControl(pressedKeys, stickActive, currentMode, currentState)

  // 闪电特效
  const { triggerLightning } = useLightningEffect()

  // 更新模式行为
  async function updateModeBehavior(reloadModel = true) {
    // 清除之前的定时器
    stopAgentActions()
    stopSpyStickControl()

    // 切换模式时重新加载模型和资源
    if (reloadModel) {
      try {
        // 先销毁旧模型
        handleDestroy()

        // 等待一帧，确保旧模型完全从 stage 移除
        await new Promise(resolve => requestAnimationFrame(resolve))

        // 清空按下的按键和资源
        pressedKeys.value = {}
        supportKeys.value = {}
        backgroundImagePath.value = undefined

        // 重新加载模型和资源
        await handleLoad(MODEL_PATH.value)
        await loadResources()
        handleResize()

        console.log(`✅ Model switched to: ${MODEL_PATH.value}`)
      } catch (error) {
        console.error('❌ Failed to switch model:', error)
      }
    }

    if (currentMode.value === 'slacking') {
      // Slacking mode: 只控制摇杆打游戏，不显示摇杆的手
      live2d.setParameterValue('CatParamStickShowLeftHand', false)
      live2d.setParameterValue('CatParamStickShowRightHand', false)

      // Slacking mode: 随机控制摇杆打游戏
      startSpyStickControl()
    } else {
      // Spying mode: 如果当前是 working 状态，启动自动动作
      if (currentState.value === 'working') {
        startAgentAutoActions()
      }
    }
  }

  // 更新状态行为
  function updateStateBehavior() {
    console.log(`State changed to: ${currentState.value}`)

    // 清除之前的定时器
    stopAgentActions()

    // 停止 Slacking mode 摇杆控制（如果切换到其他模式）
    if (currentMode.value !== 'slacking') {
      stopSpyStickControl()
    }

    // Slacking mode: 所有状态都有摇杆控制（已在 updateModeBehavior 中启动，这里确保继续运行）
    if (currentMode.value === 'slacking') {
      // 确保摇杆控制正在运行
      startSpyStickControl()
      console.log('🎮 State changed: Ensuring stick control is running')
    }

    // Spying mode: 只在 working 状态时触发自动动作
    if (currentMode.value === 'spying' && currentState.value === 'working') {
      startAgentAutoActions()
    }

    // Spying mode: 进入 confirming 状态时触发闪电特效
    if (currentMode.value === 'spying' && currentState.value === 'confirming') {
      triggerLightning()
    }
  }

  // 监听模式变化，自动切换模型
  watch(currentMode, async () => {
    await updateModeBehavior()
  })

  // 监听状态变化，自动更新行为
  watch(currentState, () => {
    updateStateBehavior()
  })

  // 切换模式
  function toggleMode() {
    console.log('Toggle mode clicked')
    currentMode.value = currentMode.value === 'slacking' ? 'spying' : 'slacking'
    console.log('Current mode:', currentMode.value)
  }

  // 切换状态
  function toggleState() {
    console.log('Toggle state clicked')
    const states: Array<'resting' | 'working' | 'confirming'> = ['resting', 'working', 'confirming']
    const currentIndex = states.indexOf(currentState.value)
    currentState.value = states[(currentIndex + 1) % states.length]
    console.log('Current state:', currentState.value)
  }

  // 测试按键按下
  function testKeyPress(key: string) {
    console.log('Test key press:', key)
    const path = supportKeys.value[key]
    console.log('Key path:', path, 'Available keys:', Object.keys(supportKeys.value))
    if (path) {
      pressedKeys.value[key] = path
      console.log('Pressed keys:', pressedKeys.value)
    } else {
      console.warn(`Key not found: ${key}. Available keys:`, Object.keys(supportKeys.value))
    }
  }

  // 测试按键释放
  function testKeyRelease() {
    console.log('Test key release')
    pressedKeys.value = {}
    console.log('All keys released')
  }

  // 设置模式（用于与后端同步）
  function setMode(mode: 'slacking' | 'spying') {
    console.log('setMode called with:', mode, 'current mode:', currentMode.value)
    if (currentMode.value !== mode) {
      console.log('Updating mode from', currentMode.value, 'to', mode)
      currentMode.value = mode
      console.log('Mode updated to:', currentMode.value)
    } else {
      console.log('Mode already set to', mode, ', skipping update')
    }
  }

  // 设置状态（用于与后端同步）
  function setState(state: 'resting' | 'working' | 'confirming') {
    if (currentState.value !== state) {
      currentState.value = state
    }
  }

  return {
    currentMode,
    currentState,
    showTestPanel,
    pressedKeys,
    supportKeys,
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
  }
}


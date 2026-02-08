import { ref, type Ref } from 'vue'
import live2d from '../utils/live2d'

export function useAgentActions(
  currentMode: Ref<'slacking' | 'spying'>,
  currentState: Ref<'resting' | 'working' | 'confirming'>,
  pressedKeys: Ref<Record<string, string>>,
  supportKeys: Ref<Record<string, string>>
) {
  let agentActionTimer: number | null = null
  let agentMouseTimer: number | null = null
  let agentMouseRaf: number | null = null

  // 鼠标当前位置（0..1），用于平滑拖动
  const currentMouseRatio = ref({ x: 0.5, y: 0.5 })

  function stopAgentMouseDrag() {
    if (agentMouseRaf != null) {
      cancelAnimationFrame(agentMouseRaf)
      agentMouseRaf = null
    }
  }

  function applyMouseRatio(xRatio: number, yRatio: number) {
    const xr = Math.max(0, Math.min(1, xRatio))
    const yr = Math.max(0, Math.min(1, yRatio))
    currentMouseRatio.value = { x: xr, y: yr }

    for (const id of ['ParamMouseX', 'ParamMouseY', 'ParamAngleX', 'ParamAngleY']) {
      const { min, max } = live2d.getParameterRange(id)
      if (min === 0 && max === 0) continue

      const isXAxis = id.endsWith('X')
      const ratio = isXAxis ? xr : yr
      const value = max - (ratio * (max - min))

      live2d.setParameterValue(id, value)
    }
  }

  function startAgentAutoActions() {
    // 随机触发按键
    const triggerRandomKey = () => {
      // 检查是否还在 working 状态
      if (currentMode.value !== 'spying' || currentState.value !== 'working') {
        return
      }

      // 随机选择一个按键
      const availableKeys = Object.keys(supportKeys.value).filter(key =>
        !key.includes('_') // 排除带 _left-keys 或 _right-keys 的 key
      )

      if (availableKeys.length === 0) return

      const randomKey = availableKeys[Math.floor(Math.random() * availableKeys.length)]
      const path = supportKeys.value[randomKey]

      if (path) {
        // 按下按键
        pressedKeys.value[randomKey] = path

        // 随机持续时间 100-500ms
        const duration = 100 + Math.random() * 400

        setTimeout(() => {
          // 释放按键
          if (pressedKeys.value[randomKey]) {
            delete pressedKeys.value[randomKey]
          }
        }, duration)
      }
    }

    // 随机触发鼠标移动
    const triggerRandomMouseMove = () => {
      // 检查是否还在 working 状态
      if (currentMode.value !== 'spying' || currentState.value !== 'working') {
        return
      }

      // 目标点（0..1）
      const targetX = Math.random()
      const targetY = Math.random()

      // 平滑拖动：300-900ms
      const duration = 300 + Math.random() * 600
      const start = performance.now()
      const from = { ...currentMouseRatio.value }

      stopAgentMouseDrag()

      const easeInOut = (t: number) => (t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2)

      const tick = (now: number) => {
        if (currentMode.value !== 'spying' || currentState.value !== 'working') {
          stopAgentMouseDrag()
          return
        }

        const t = Math.min(1, (now - start) / duration)
        const k = easeInOut(t)
        const xr = from.x + (targetX - from.x) * k
        const yr = from.y + (targetY - from.y) * k

        applyMouseRatio(xr, yr)

        if (t < 1) {
          agentMouseRaf = requestAnimationFrame(tick)
        } else {
          agentMouseRaf = null
        }
      }

      agentMouseRaf = requestAnimationFrame(tick)
    }

    // 每 200-800ms 触发一次随机按键
    const scheduleNextKeyAction = () => {
      if (currentMode.value !== 'spying' || currentState.value !== 'working') {
        if (agentActionTimer) {
          clearTimeout(agentActionTimer)
          agentActionTimer = null
        }
        return
      }

      triggerRandomKey()

      const nextDelay = 200 + Math.random() * 300
      agentActionTimer = window.setTimeout(scheduleNextKeyAction, nextDelay)
    }

    // 每 500-1500ms 触发一次鼠标移动
    const scheduleNextMouseMove = () => {
      if (currentMode.value !== 'spying' || currentState.value !== 'working') {
        if (agentMouseTimer) {
          clearTimeout(agentMouseTimer)
          agentMouseTimer = null
        }
        return
      }

      triggerRandomMouseMove()

      const nextDelay = 500 + Math.random() * 1000
      agentMouseTimer = window.setTimeout(scheduleNextMouseMove, nextDelay)
    }

    scheduleNextKeyAction()
    scheduleNextMouseMove()
  }

  function stopAgentActions() {
    if (agentActionTimer) {
      clearTimeout(agentActionTimer)
      agentActionTimer = null
    }
    if (agentMouseTimer) {
      clearTimeout(agentMouseTimer)
      agentMouseTimer = null
    }
    stopAgentMouseDrag()
  }

  return {
    startAgentAutoActions,
    stopAgentActions,
    stopAgentMouseDrag,
  }
}


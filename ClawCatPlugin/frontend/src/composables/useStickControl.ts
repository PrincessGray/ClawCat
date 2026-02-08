import { ref, type Ref } from 'vue'
import live2d from '../utils/live2d'

export function useStickControl(currentMode: Ref<'slacking' | 'spying'>) {
  let spyStickTimer: number | null = null
  let spyStickRaf: number | null = null
  const stickActive = ref({ left: false, right: false })

  // 当前摇杆位置（归一化到 -1 到 1）
  let leftStickX = 0
  let leftStickY = 0
  let rightStickX = 0
  let rightStickY = 0

  // 目标摇杆位置
  let targetLeftX = 0
  let targetLeftY = 0
  let targetRightX = 0
  let targetRightY = 0

  function startSpyStickControl() {
    // 检查摇杆参数是否存在
    const checkStickParam = (id: string) => {
      const { min, max } = live2d.getParameterRange(id)
      return min !== 0 || max !== 0
    }

    // 检查是否有摇杆参数
    const hasLeftStick = checkStickParam('CatParamStickLX') && checkStickParam('CatParamStickLY')
    const hasRightStick = checkStickParam('CatParamStickRX') && checkStickParam('CatParamStickRY')

    if (!hasLeftStick && !hasRightStick) {
      console.log('⚠️ 当前模型不支持摇杆参数，跳过摇杆控制')
      return
    }

    // 清除之前的定时器
    if (spyStickTimer) {
      clearTimeout(spyStickTimer)
      spyStickTimer = null
    }
    if (spyStickRaf) {
      cancelAnimationFrame(spyStickRaf)
      spyStickRaf = null
    }

    // 更新摇杆位置（平滑移动）
    const updateSticks = () => {
      if (currentMode.value !== 'slacking') {
        if (spyStickRaf) {
          cancelAnimationFrame(spyStickRaf)
          spyStickRaf = null
        }
        return
      }

      // 平滑移动到目标位置
      const lerp = (start: number, end: number, factor: number) => start + (end - start) * factor
      const factor = 0.1 // 移动速度

      if (hasLeftStick) {
        leftStickX = lerp(leftStickX, targetLeftX, factor)
        leftStickY = lerp(leftStickY, targetLeftY, factor)

        // 设置左摇杆参数（需要转换为模型参数范围）
        const { min: lxMin, max: lxMax } = live2d.getParameterRange('CatParamStickLX')
        const { min: lyMin, max: lyMax } = live2d.getParameterRange('CatParamStickLY')

        if (lxMin !== 0 || lxMax !== 0) {
          const lxValue = (leftStickX + 1) / 2 * (lxMax - lxMin) + lxMin
          live2d.setParameterValue('CatParamStickLX', lxValue)
        }
        if (lyMin !== 0 || lyMax !== 0) {
          const lyValue = (leftStickY + 1) / 2 * (lyMax - lyMin) + lyMin
          live2d.setParameterValue('CatParamStickLY', lyValue)
        }

        // 显示左摇杆和左手，并更新摇杆激活状态
        const leftStickActive = Math.abs(leftStickX) > 0.1 || Math.abs(leftStickY) > 0.1
        stickActive.value.left = leftStickActive
        if (leftStickActive) {
          live2d.setParameterValue('CatParamStickShowLeftHand', true)
          live2d.setParameterValue('CatParamStickLeftDown', true)
        } else {
          live2d.setParameterValue('CatParamStickShowLeftHand', false)
          live2d.setParameterValue('CatParamStickLeftDown', false)
        }
      }

      if (hasRightStick) {
        rightStickX = lerp(rightStickX, targetRightX, factor)
        rightStickY = lerp(rightStickY, targetRightY, factor)

        // 设置右摇杆参数
        const { min: rxMin, max: rxMax } = live2d.getParameterRange('CatParamStickRX')
        const { min: ryMin, max: ryMax } = live2d.getParameterRange('CatParamStickRY')

        if (rxMin !== 0 || rxMax !== 0) {
          const rxValue = (rightStickX + 1) / 2 * (rxMax - rxMin) + rxMin
          live2d.setParameterValue('CatParamStickRX', rxValue)
        }
        if (ryMin !== 0 || ryMax !== 0) {
          const ryValue = (rightStickY + 1) / 2 * (ryMax - ryMin) + ryMin
          live2d.setParameterValue('CatParamStickRY', ryValue)
        }

        // 显示右摇杆和右手，并更新摇杆激活状态
        const rightStickActive = Math.abs(rightStickX) > 0.1 || Math.abs(rightStickY) > 0.1
        stickActive.value.right = rightStickActive
        if (rightStickActive) {
          live2d.setParameterValue('CatParamStickShowRightHand', true)
          live2d.setParameterValue('CatParamStickRightDown', true)
        } else {
          live2d.setParameterValue('CatParamStickShowRightHand', false)
          live2d.setParameterValue('CatParamStickRightDown', false)
        }
      }

      spyStickRaf = requestAnimationFrame(updateSticks)
    }

    // 随机改变摇杆目标位置
    const randomizeStickTarget = () => {
      if (currentMode.value !== 'slacking') {
        if (spyStickTimer) {
          clearTimeout(spyStickTimer)
          spyStickTimer = null
        }
        return
      }

      // 随机生成新的目标位置（-1 到 1）
      if (hasLeftStick) {
        targetLeftX = (Math.random() - 0.5) * 2 // -1 到 1
        targetLeftY = (Math.random() - 0.5) * 2
      }
      if (hasRightStick) {
        targetRightX = (Math.random() - 0.5) * 2
        targetRightY = (Math.random() - 0.5) * 2
      }

      // 每 500-2000ms 随机改变一次
      const nextDelay = 500 + Math.random() * 1500
      spyStickTimer = window.setTimeout(randomizeStickTarget, nextDelay)
    }

    // 启动
    updateSticks()
    randomizeStickTarget()
  }

  function stopSpyStickControl() {
    if (spyStickTimer) {
      clearTimeout(spyStickTimer)
      spyStickTimer = null
    }
    if (spyStickRaf) {
      cancelAnimationFrame(spyStickRaf)
      spyStickRaf = null
    }

    // 重置摇杆参数和状态
    live2d.setParameterValue('CatParamStickShowLeftHand', false)
    live2d.setParameterValue('CatParamStickShowRightHand', false)
    live2d.setParameterValue('CatParamStickLeftDown', false)
    live2d.setParameterValue('CatParamStickRightDown', false)
    stickActive.value = { left: false, right: false }
  }

  return {
    stickActive,
    startSpyStickControl,
    stopSpyStickControl,
  }
}


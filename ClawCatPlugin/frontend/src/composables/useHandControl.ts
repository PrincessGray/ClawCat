import { watch, type Ref } from 'vue'
import live2d from '../utils/live2d'

export function useHandControl(
  pressedKeys: Ref<Record<string, string>>,
  stickActive: Ref<{ left: boolean; right: boolean }>,
  currentMode: Ref<'slacking' | 'spying'>,
  currentState: Ref<'resting' | 'working' | 'confirming'>
) {
  // 根据按键路径判断是左手还是右手
  function getHandFromPath(path: string): 'left' | 'right' | null {
    if (path.includes('/left-keys/')) return 'left'
    if (path.includes('/right-keys/')) return 'right'
    return null
  }

  // 监听按键和摇杆状态变化，自动更新 Live2D 参数（参考 BongoCat）
  watch([pressedKeys, stickActive, currentMode, currentState], ([keys, active, mode, state]) => {
    const paths = Object.values(keys)
    const hasLeft = paths.some(path => getHandFromPath(path) === 'left')
    const hasRight = paths.some(path => getHandFromPath(path) === 'right')
    const hasAnyKey = Object.keys(keys).length > 0

    // 在 Spying mode 的 working 状态，即使没有按键也要保持手部显示
    const isMonitorWorking = mode === 'spying' && state === 'working'

    // 更新 Live2D 参数：当有按键或摇杆激活时，手放下（隐藏举着的手）
    // 在 Monitor working 状态，如果没有按键，保持手部显示（设为 true）
    live2d.setParameterValue('CatParamLeftHandDown', active.left || hasLeft || (isMonitorWorking && !hasAnyKey))
    live2d.setParameterValue('CatParamRightHandDown', active.right || hasRight || (isMonitorWorking && !hasAnyKey))

    // 当有按键被按下时，隐藏摇杆的手（参考 BongoCat）
    if (hasAnyKey) {
      live2d.setParameterValue('CatParamStickShowLeftHand', false)
      live2d.setParameterValue('CatParamStickShowRightHand', false)
    }

    console.log('Keys/Stick updated:', { hasLeft, hasRight, hasAnyKey, stickActive: active, isMonitorWorking, keys: Object.keys(keys) })
  }, { deep: true })
}


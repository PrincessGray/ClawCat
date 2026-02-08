import { ref } from 'vue'
import live2d from '../utils/live2d'

export interface ModelSize {
  width: number
  height: number
}

export function useModel() {
  const modelSize = ref<ModelSize>()

  async function handleLoad(modelUrl: string) {
    try {
      const { width, height } = await live2d.load(modelUrl)
      modelSize.value = { width, height }
      console.log(`✅ Model loaded - Actual size: ${width}x${height}, Ratio: ${(width/height).toFixed(2)}:1`)
      handleResize()
    } catch (error) {
      console.error('Failed to load model:', error)
    }
  }

  function handleDestroy() {
    live2d.destroy()
  }

  function handleResize() {
    if (!modelSize.value) return
    live2d.resizeModel(modelSize.value)
  }

  function handleKeyChange(isLeft = true, pressed = true) {
    const id = isLeft ? 'CatParamLeftHandDown' : 'CatParamRightHandDown'
    live2d.setParameterValue(id, pressed)
  }

  function handleMouseChange(key: string, pressed = true) {
    const id = key === 'Left' ? 'ParamMouseLeftDown' : 'ParamMouseRightDown'
    live2d.setParameterValue(id, pressed)
  }

  function handleMouseMove(cursorPoint: { x: number; y: number }) {
    // 简化版：使用窗口相对位置
    const xRatio = cursorPoint.x / window.innerWidth
    const yRatio = cursorPoint.y / window.innerHeight

    for (const id of ['ParamMouseX', 'ParamMouseY', 'ParamAngleX', 'ParamAngleY']) {
      const { min, max } = live2d.getParameterRange(id)
      if (min === 0 && max === 0) continue

      const isXAxis = id.endsWith('X')
      const ratio = isXAxis ? xRatio : yRatio
      const value = max - (ratio * (max - min))

      live2d.setParameterValue(id, value)
    }
  }

  return {
    modelSize,
    handleLoad,
    handleDestroy,
    handleResize,
    handleKeyChange,
    handleMouseChange,
    handleMouseMove,
  }
}


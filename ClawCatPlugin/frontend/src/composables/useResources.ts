import { ref, type Ref, type ComputedRef } from 'vue'

export function useResources(resourcesPath: ComputedRef<string>) {
  const backgroundImagePath = ref<string>()
  const supportKeys = ref<Record<string, string>>({})

  async function loadResources() {
    try {
      // 清空之前的资源
      supportKeys.value = {}
      backgroundImagePath.value = undefined

      // 加载背景图片
      const bgResponse = await fetch(`${resourcesPath.value}/background.png`)
      if (bgResponse.ok) {
        backgroundImagePath.value = `${resourcesPath.value}/background.png`
      }

      // 加载键盘图片资源（同时加载 left-keys 和 right-keys）
      const groups = ['left-keys', 'right-keys']
      for (const group of groups) {
        // 尝试加载常见的按键图片
        const commonKeys = [
          // 字母键
          'KeyA', 'KeyB', 'KeyC', 'KeyD', 'KeyE', 'KeyF', 'KeyG', 'KeyH',
          'KeyI', 'KeyJ', 'KeyK', 'KeyL', 'KeyM', 'KeyN', 'KeyO', 'KeyP',
          'KeyQ', 'KeyR', 'KeyS', 'KeyT', 'KeyU', 'KeyV', 'KeyW', 'KeyX',
          'KeyY', 'KeyZ',
          // 功能键
          'Space', 'Enter', 'Backspace', 'Tab', 'Escape', 'Delete',
          // 修饰键（通用版本）
          'Shift', 'Control', 'Alt', 'Meta',
          // 修饰键（左右版本）
          'ShiftLeft', 'ShiftRight', 'ControlLeft', 'ControlRight',
          // 数字键
          'Num0', 'Num1', 'Num2', 'Num3', 'Num4', 'Num5', 'Num6', 'Num7', 'Num8', 'Num9',
          // 其他键
          'BackQuote', 'Slash', 'CapsLock', 'Fn', 'AltGr', 'Return',
          // Gamepad keys
          'DPadDown', 'DPadLeft', 'DPadRight', 'DPadUp', 'LeftTrigger', 'LeftTrigger2',
          'East', 'North', 'RightTrigger', 'RightTrigger2', 'South', 'West',
        ]

        for (const key of commonKeys) {
          const keyPath = `${resourcesPath.value}/${group}/${key}.png`
          // 检查文件是否存在（通过尝试加载）
          try {
            const response = await fetch(keyPath)
            if (response.ok) {
              // 使用完整路径作为 key，这样可以根据路径判断是 left 还是 right
              const fullKey = `${key}_${group}`
              supportKeys.value[fullKey] = keyPath
              // 同时保留原始 key 的映射（优先使用 left-keys）
              if (!supportKeys.value[key] || group === 'left-keys') {
                supportKeys.value[key] = keyPath
              }
            }
          } catch {
            // 文件不存在，忽略
          }
        }
      }

      console.log(`✅ Loaded ${Object.keys(supportKeys.value).length} keyboard keys`)
    } catch (error) {
      console.warn('⚠️ Failed to load some resources:', error)
    }
  }

  return {
    backgroundImagePath,
    supportKeys,
    loadResources,
  }
}


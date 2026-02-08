import live2d from '../utils/live2d'

export function useLightningEffect() {
  // 触发闪电特效（参考 BongoCat：使用 motion 播放闪电动画）
  function triggerLightning() {
    // 方法1: 播放 motion（推荐，参考 BongoCat 的 live2d_motion1.motion3.json）
    // CAT_motion 组的第 0 个 motion 是闪电动画
    const motionPromise = live2d.playMotion('CAT_motion', 0)
    
    if (motionPromise) {
      console.log('✅ 播放闪电 motion')
      return
    }

    // 方法2: 如果 motion 不存在，使用参数和 Parts 控制（备用方案）
    console.log('⚠️ Motion 不存在，使用参数控制')
    
    const paramRange = live2d.getParameterRange('Param')
    const param2Range = live2d.getParameterRange('Param2')

    // 显示闪电 Parts（Part4 和 Part6 是闪电图层）
    live2d.setPartOpacity('Part4', 1)
    live2d.setPartOpacity('Part6', 1)

    // 设置闪电参数
    if (paramRange.min !== 0 || paramRange.max !== 0) {
      live2d.setParameterValue('Param', paramRange.max)
    }

    if (param2Range.min !== 0 || param2Range.max !== 0) {
      live2d.setParameterValue('Param2', param2Range.max)
      
      // 根据 motion 文件，Param2 在约 1.133 秒后恢复
      setTimeout(() => {
        live2d.setParameterValue('Param2', param2Range.min)
        live2d.setPartOpacity('Part4', 0)
        live2d.setPartOpacity('Part6', 0)
        if (paramRange.min !== 0 || paramRange.max !== 0) {
          live2d.setParameterValue('Param', paramRange.min)
        }
      }, 1133)
    } else {
      // 如果没有 Param2，500ms 后恢复
      setTimeout(() => {
        live2d.setPartOpacity('Part4', 0)
        live2d.setPartOpacity('Part6', 0)
        if (paramRange.min !== 0 || paramRange.max !== 0) {
          live2d.setParameterValue('Param', paramRange.min)
        }
      }, 500)
    }
  }

  // 清理（目前不需要，motion 会自动播放完成）
  function cleanup() {
    // Motion 会自动播放完成，无需手动清理
  }

  return {
    triggerLightning,
    cleanup,
  }
}


import type { Cubism4InternalModel } from 'pixi-live2d-display'

import JSON5 from 'json5'
import { Cubism4ModelSettings, Live2DModel } from 'pixi-live2d-display'
import { Application, Ticker } from 'pixi.js'

// 类型定义（避免循环依赖）
export interface ModelSize {
  width: number
  height: number
}

Live2DModel.registerTicker(Ticker)

class Live2d {
  private app: Application | null = null
  public model: Live2DModel | null = null

  constructor() { }

  private initApp() {
    if (this.app) return

    const view = document.getElementById('live2dCanvas') as HTMLCanvasElement
    if (!view) return

    this.app = new Application({
      view,
      resizeTo: window,
      backgroundAlpha: 0,
      resolution: devicePixelRatio,
    })
  }

  /**
   * 加载模型（从静态资源目录）
   * @param modelPath 模型路径，例如 '/models/standard'（相对于 public 目录）
   */
  public async load(modelPath: string) {
    this.initApp()
    this.destroy()

    try {
      // 确保 stage 完全干净（双重保险）
      if (this.app && this.app.stage.children.length > 0) {
        this.app.stage.removeChildren()
      }

      // 从静态资源加载模型文件
      const modelUrl = `${modelPath}/cat.model3.json`
      const modelListResponse = await fetch(modelUrl)
      if (!modelListResponse.ok) {
        throw new Error(`Model file not found: ${modelUrl}`)
      }

      const modelJSON = JSON5.parse(await modelListResponse.text())

      // 创建模型设置，使用静态资源路径
      const modelSettings = new Cubism4ModelSettings({
        ...modelJSON,
        url: modelUrl,
      })

      // 替换所有文件路径为静态资源路径
      modelSettings.replaceFiles((file) => {
        return `${modelPath}/${file}`
      })

      this.model = await Live2DModel.from(modelSettings)
      
      // 再次确保 stage 干净（防止在异步加载过程中有残留）
      if (this.app && this.app.stage.children.length > 0) {
        this.app.stage.removeChildren()
      }
      
      this.app?.stage.addChild(this.model)

      const { width, height } = this.model
      const { motions, expressions } = modelSettings

      return {
        width,
        height,
        motions,
        expressions,
      }
    } catch (error) {
      console.error('Failed to load Live2D model:', error)
      throw error
    }
  }

  public destroy() {
    if (!this.model) {
      // 即使没有 model 引用，也清理 stage 上可能残留的子元素
      if (this.app && this.app.stage.children.length > 0) {
        this.app.stage.removeChildren()
      }
      return
    }
    
    // 从 stage 中移除模型
    if (this.app) {
      // 移除所有子元素，确保没有残留
      const index = this.app.stage.children.indexOf(this.model)
      if (index !== -1) {
        this.app.stage.removeChildAt(index)
      }
      // 如果还有其他子元素，也一并清理
      if (this.app.stage.children.length > 0) {
        this.app.stage.removeChildren()
      }
    }
    
    // 销毁模型
    this.model?.destroy()
    this.model = null
  }

  public resizeModel(modelSize: ModelSize) {
    if (!this.model) return

    const { width, height } = modelSize
    const scaleX = innerWidth / width
    const scaleY = innerHeight / height
    const scale = Math.min(scaleX, scaleY)

    this.model.scale.set(scale)
    this.model.x = innerWidth / 2
    this.model.y = innerHeight / 2
    this.model.anchor.set(0.5)
  }

  public getCoreModel() {
    const internalModel = this.model?.internalModel as Cubism4InternalModel
    return internalModel?.coreModel
  }

  public getParameterRange(id: string) {
    const coreModel = this.getCoreModel()
    if (!coreModel) return { min: 0, max: 0 }

    const index = coreModel.getParameterIndex(id)
    const min = coreModel.getParameterMinimumValue(index)
    const max = coreModel.getParameterMaximumValue(index)

    return { min, max }
  }

  public setParameterValue(id: string, value: number | boolean) {
    const coreModel = this.getCoreModel()
    if (!coreModel) return false

    return coreModel.setParameterValueById?.(id, Number(value)) ?? false
  }

  public playMotion(group: string, index: number) {
    return this.model?.motion(group, index)
  }

  public playExpression(index: number) {
    return this.model?.expression(index)
  }

  public getMotions() {
    // 返回可用的动作组（从模型配置中获取）
    // 这里简化处理，实际应该从 modelSettings 获取
    return {
      'CAT_motion': [0, 1], // 普通动作组，有2个动作
      'CAT_motion_lock': [0, 1] // 锁定动作组，有2个动作
    }
  }

  /**
   * 设置 Part 的透明度（用于显示/隐藏 Parts）
   * @param partId Part ID，例如 'Part4', 'Part6'
   * @param opacity 透明度 0-1，0 为完全透明（隐藏），1 为完全不透明（显示）
   */
  public setPartOpacity(partId: string, opacity: number) {
    const coreModel = this.getCoreModel()
    if (!coreModel) return false

    const partIndex = coreModel.getPartIndex(partId)
    if (partIndex === -1) {
      console.warn(`Live2D part not found: ${partId}`)
      return false
    }

    coreModel.setPartOpacityByIndex(partIndex, opacity)
    return true
  }
}

const live2d = new Live2d()

export default live2d


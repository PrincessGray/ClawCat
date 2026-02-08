// 适配版本：移除 Tauri 依赖
export function join(...paths: string[]): string {
  return paths
    .filter(Boolean)
    .map((path, index) => {
      if (index === 0) {
        return path.replace(/[/\\]+$/, '')
      } else {
        return path.replace(/^[/\\]+|[/\\]+$/g, '')
      }
    })
    .join('/')
}

// 获取路径分隔符（Web 环境统一使用 /）
export function sep(): string {
  return '/'
}


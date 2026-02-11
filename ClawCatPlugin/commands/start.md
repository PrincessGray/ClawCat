---
description: One-click start ClawCat
---

# 一键启动 ClawCat

## 🚀 快速启动

### Windows

在 Claude Code 中执行：

```bash
"${CLAUDE_PLUGIN_ROOT}/scripts/start_window.bat"
```

或者直接双击运行：
```
ClawCatPlugin/scripts/start_window.bat
```

### macOS / Linux

在 Claude Code 中执行：

```bash
bash "${CLAUDE_PLUGIN_ROOT}/scripts/start_window.sh"
```

## ✨ 自动完成

启动脚本会自动：

1. ✅ 检测并激活 conda 环境（如果已安装）
2. ✅ 安装 Python 依赖（如果需要）
3. ✅ 启动 ClawCat 窗口和服务器

## 📝 说明

- **首次启动**：会自动安装依赖，可能需要几分钟
- **窗口位置**：ClawCat 窗口会出现在屏幕右下角
- **日志文件**：`~/.claude/clawcat/logs/clawcat_*.log`

## 🛑 停止服务

- 在运行窗口按 `Ctrl+C`
- 或使用命令：`/clawcat:stop`

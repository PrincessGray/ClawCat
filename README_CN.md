# ClawCat 🐱

一个与 Claude Code 集成的 Live2D 桌面宠物，提供可视化反馈和交互覆盖层。

[English Documentation](./README.md) | [中文文档](./README_CN.md) | [插件文档](./ClawCatPlugin/README_CN.md)

![ClawCat 演示](ClawCatPlugin/public/cover.png)

## 快速开始

### 通过 Claude Code 市场安装

```bash

# 1. 添加市场
/plugin marketplace add PrincessGray/ClawCat

# 2. 安装插件
/plugin install clawcat
```

### 激活 Hooks

安装后，您需要退出并重新启动 Claude Code 以激活 hooks：

```bash
# 退出 Claude Code
exit

# 重新启动 Claude Code（这会激活 hooks）
claude-resume

# 现在可以启动 ClawCat
/clawcat:start
```

### 使用方法

使用单个命令启动 ClawCat：

```bash
/clawcat:start
```

完成后停止 ClawCat：

```bash
/clawcat:stop
```

就这么简单！依赖项将在首次启动时自动安装。

### 从 GitHub 安装

如果您希望直接从 GitHub 仓库运行 ClawCat（JS 前端已打包，正常使用不需要 Node.js）：

```bash
# 1. 克隆仓库
git clone https://github.com/PrincessGray/ClawCat.git
cd ClawCat/ClawCatPlugin

# 2. 准备 conda 环境：
# 启动脚本会自动激活 conda 'base' 环境。
# 如果您希望使用专用环境，请先创建并激活它：

conda create -n clawcat python=3.10
conda activate clawcat

# 3. 安装 Python 依赖（或让脚本在首次运行时自动安装）
pip install -r requirements.txt
```

然后启动 ClawCat：

**选项 A：使用启动脚本**（自动激活 conda base）：

- 在 **Windows**（PowerShell 或 cmd）：

```bash
scripts\start_window.bat
```

- 在 **macOS / Linux**：

```bash
bash scripts/start_window.sh
```

**选项 B：使用当前的 conda 环境**（如果您已激活自定义环境）：

```bash
python scripts/service_manager.py start
```

**注意**：启动脚本（`start_window.bat` / `start_window.sh`）会自动激活 conda `base` 环境。如果您想使用自定义 conda 环境，请先激活它，然后使用选项 B。  
只有在您想要**开发**或**修改**前端时才需要 Node.js 和 npm；仅从 GitHub 运行 ClawCat 不需要它们。

## 功能特性

- **Live2D 动画**：可爱的猫咪角色，流畅的动画效果
- **Claude Code 集成**：通过 hooks 为 Claude 的操作提供可视化反馈
- **交互状态**：休息、工作和确认模式
- **监视模式**：在监视 Claude 和摸鱼之间切换
- **跨平台**：支持 Windows、macOS 和 Linux
- **透明窗口**：无边框、可拖动的覆盖层，始终置顶

## 文档

详细文档请参阅：

- [English Documentation](./ClawCatPlugin/README.md)
- [中文文档](./ClawCatPlugin/README_CN.md)
- [实现总结](./IMPLEMENTATION_SUMMARY.md)

## 系统要求

- **Python**：3.8 或更高版本
- **Node.js**：18 或更高版本（仅开发需要）
- **操作系统**：Windows、macOS 或 Linux

## 项目结构

```text
ClawCat/
├── marketplace.json              # 市场配置
├── ClawCatPlugin/                # 插件目录
│   ├── .claude-plugin/           # 插件元数据
│   ├── commands/                 # 命令定义
│   ├── hooks/                    # Hook 配置
│   ├── scripts/                  # Python 脚本
│   ├── frontend/                 # Vue.js 前端
│   ├── src/                      # Python 后端
│   ├── public/                   # Live2D 模型
│   ├── README.md                 # 英文文档
│   └── README_CN.md              # 中文文档
├── LICENSE                       # MIT 许可证
└── IMPLEMENTATION_SUMMARY.md     # 实现细节
```

## 开发

开发说明请参阅[插件文档](./ClawCatPlugin/README.md#development)。

## 许可证

MIT 许可证 - 详情请参阅 [LICENSE](./LICENSE) 文件。

## 致谢

本项目受到 [Bongo Cat](https://github.com/Externalizable/bongo.cat) 项目的启发和参考。我们感谢 Bongo Cat 社区的创意工作和开源贡献。

- **Bongo Cat**：原始桌面宠物概念和动画创意
- **Live2D**：角色动画技术
- **Claude Code**：Hook 系统和插件架构

## 贡献

欢迎贡献！请随时提交问题或拉取请求。

## 支持

如有问题、疑问或功能请求，请在 GitHub 上提交 issue。

---

**注意**：此插件需要安装并运行 Claude Code。它通过可视化反馈增强您的 Claude Code 体验，但不会修改 Claude 的核心功能。


# ClawCat 🐱

一个与 Claude Code 集成的 Live2D 桌面宠物，提供可视化反馈和交互覆盖层。

![ClawCat 演示](public/cover.png)

## 功能特性

- **Live2D 动画**：可爱的猫咪角色，流畅的动画效果
- **Claude Code 集成**：通过钩子为 Claude 的操作提供可视化反馈
- **交互状态**：
  - 休息中：猫咪处于空闲状态
  - 工作中：当 Claude 思考或使用工具时，猫咪显示活动状态
  - 确认中：猫咪显示权限请求，带有交互按钮
- **监视模式**：在监视 Claude 和摸鱼之间切换
- **跨平台**：支持 Windows、macOS 和 Linux
- **透明窗口**：无边框、可拖动的覆盖层，始终置顶

## 安装

### 通过 Claude Code 市场安装

1. 添加 ClawCat 市场：
   ```bash
   /plugin marketplace add YOUR_USERNAME/ClawCat
   ```

2. 安装插件：
   ```bash
   /plugin install clawcat
   ```

就这么简单！首次启动时会自动安装依赖项。

### 手动安装

如果您更喜欢手动安装：

1. 克隆仓库
2. 安装 Python 依赖：
   ```bash
   pip install -r ClawCatPlugin/requirements.txt
   ```
3. 安装 Node.js 依赖：
   ```bash
   cd ClawCatPlugin
   npm install
   ```

## 快速开始

使用单个命令启动 ClawCat：

```bash
/clawcat:start
```

这将：
- 检查并安装任何缺失的依赖项
- 启动 Vite 开发服务器（前端）
- 启动 HTTP 服务器（后端）
- 启动 ClawCat 窗口

完成后停止 ClawCat：

```bash
/clawcat:stop
```

## 使用方法

### 钩子集成

ClawCat 自动响应 Claude Code 事件：

1. **UserPromptSubmit**：当您发送消息时，猫咪进入"工作中"状态
2. **PreToolUse**：猫咪显示 Claude 即将使用的工具
3. **PostToolUse**：猫咪根据结果大小产生脉冲效果
4. **PermissionRequest**：猫咪显示交互式权限对话框
5. **Notification**：当 Claude 需要输入时，猫咪会通知您
6. **Stop**：会话结束时，猫咪返回"休息中"状态

### 交互功能

- **拖动移动**：点击并拖动猫咪以重新定位
- **监视模式切换**：点击猫咪在监视和摸鱼之间切换
- **权限对话框**：当 Claude 请求权限时：
  - **允许**：授予此操作的权限
  - **总是允许**：授予权限并保存到设置
  - **拒绝**：拒绝权限请求
  - **跳转**：切换到终端查看详细信息

### 状态

- **休息中**（蓝色）：猫咪空闲，等待活动
- **工作中**（绿色）：猫咪活跃，Claude 正在思考或工作
- **确认中**（黄色）：猫咪等待您的权限决定

## 配置

### 端口配置

默认情况下，ClawCat 使用：
- Vite 开发服务器：`http://localhost:6173`
- HTTP 服务器：`http://localhost:22622`

要更改端口，请编辑：
- `ClawCatPlugin/vite.config.ts` 用于 Vite 端口
- `ClawCatPlugin/src/server.py` 用于 HTTP 服务器端口
- `ClawCatPlugin/scripts/notify.py` 用于钩子客户端端口

### 窗口大小

要调整窗口大小，请编辑 `ClawCatPlugin/src/launch_window.py`：

```python
DEFAULT_SCALE = 1.0  # 改为 0.5 表示 50%，2.0 表示 200%，等等
```

## 命令

### `/clawcat:start`

启动所有 ClawCat 服务。如果需要，会自动检查并安装依赖项。

**执行内容：**
1. 验证 Python 和 Node.js 版本
2. 检查缺失的依赖项
3. 如果需要，安装依赖项
4. 验证端口是否可用
5. 启动 Vite 开发服务器
6. 启动 HTTP 服务器
7. 启动 PyQt 窗口

### `/clawcat:stop`

优雅地停止所有 ClawCat 服务。

**执行内容：**
1. 终止 PyQt 窗口
2. 终止 HTTP 服务器
3. 终止 Vite 开发服务器
4. 清理 PID 文件

## 故障排除

### 服务无法启动

**问题**：端口已被占用

**解决方案**：检查是否有其他进程正在使用端口 6173 或 22622：

```bash
# Windows
netstat -ano | findstr :6173
netstat -ano | findstr :22622

# macOS/Linux
lsof -i :6173
lsof -i :22622
```

终止该进程或在配置文件中更改端口。

### 窗口未出现

**问题**：PyQt5 未正确安装

**解决方案**：重新安装 PyQt5：

```bash
pip uninstall PyQt5 PyQtWebEngine
pip install PyQt5 PyQtWebEngine
```

### 钩子不工作

**问题**：ClawCat 服务未运行

**解决方案**：确保使用 `/clawcat:start` 启动了 ClawCat。如果服务未运行，钩子会优雅降级。

### 猫咪没有动画

**问题**：Live2D 模型未加载

**解决方案**：
1. 检查 `public/` 目录是否包含 Live2D 模型
2. 验证 Vite 开发服务器是否在端口 6173 上运行
3. 检查浏览器控制台是否有错误（在窗口中打开开发者工具）

## 开发

### 项目结构

```
ClawCatPlugin/
├── .claude-plugin/
│   └── plugin.json          # 插件元数据
├── commands/
│   ├── start.json           # 启动命令定义
│   └── stop.json            # 停止命令定义
├── hooks/
│   └── hooks.json           # 钩子配置
├── scripts/
│   ├── notify.py            # 钩子处理脚本
│   ├── service_manager.py   # 服务生命周期管理器
│   └── install_deps.py      # 依赖安装器
├── frontend/                # Vue.js 前端
│   ├── src/
│   │   ├── App.vue          # 主应用组件
│   │   └── main.ts          # 入口点
│   └── ...
├── src/                     # Python 后端
│   ├── server.py            # HTTP 服务器
│   ├── launch_window.py     # PyQt 窗口启动器
│   └── window_control*.py   # 平台特定的窗口控制
├── public/                  # Live2D 模型和资源
└── ...
```

### 在开发模式下运行

1. 手动启动服务：
   ```bash
   # 终端 1：启动 Vite
   cd ClawCatPlugin
   npm run dev

   # 终端 2：启动服务器
   python ClawCatPlugin/src/server.py

   # 终端 3：启动窗口
   python ClawCatPlugin/src/launch_window.py
   ```

2. 修改代码
3. Vite 会热重载前端更改
4. 后端更改需要重启服务器/窗口

### 添加新动画

1. 将 Live2D 模型文件添加到 `public/`
2. 更新 `frontend/src/App.vue` 以加载新模型
3. 在状态管理逻辑中添加动画触发器

## 系统要求

- **Python**：3.8 或更高版本
- **Node.js**：18 或更高版本
- **操作系统**：Windows、macOS 或 Linux

### Python 依赖

- `requests>=2.31.0` - 用于钩子通信的 HTTP 客户端
- `psutil>=5.9.0` - 进程管理
- `PyQt5>=5.15.10` - GUI 框架
- `PyQtWebEngine>=5.15.6` - Web 渲染

### Node.js 依赖

- `vue` - 前端框架
- `vite` - 构建工具和开发服务器
- `pixi-live2d-display` - Live2D 渲染

## 许可证

MIT 许可证 - 详见 [LICENSE](../LICENSE) 文件。

## 致谢

本项目受到 [Bongo Cat](https://github.com/Externalizable/bongo.cat) 项目的启发并参考了其设计。我们感谢 Bongo Cat 社区的创意工作和开源贡献。

特别感谢：
- **Bongo Cat** - 原始桌面宠物概念和动画创意
- **Live2D** - 角色动画技术
- **Claude Code** - 钩子系统和插件架构
- **Vue.js、Vite、PyQt5** - 前端和桌面应用框架

## 贡献

欢迎贡献！请随时提交问题或拉取请求。

## 致谢

- Live2D 模型：[指定您的模型来源]
- 使用 Vue.js、Vite 和 PyQt5 构建
- 通过钩子与 Claude Code 集成

## 支持

如有问题、疑问或功能请求，请在 GitHub 上提交问题。

---

**注意**：此插件需要安装并运行 Claude Code。它通过可视化反馈增强您的 Claude Code 体验，但不会修改 Claude 的核心功能。

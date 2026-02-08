# ClawCat 打包指南

## 打包 Python Server 和 Window

使用 PyInstaller 将 `launch_window.py`（包含 server）打包成可执行文件。

## 前置要求

1. **安装依赖**：
   ```bash
   pip install -r requirements.txt
   pip install pyinstaller
   ```

2. **构建前端**：
   ```bash
   npm run build
   ```
   确保 `dist/` 目录存在且包含前端构建文件。

## 打包步骤

### 方法 1: 使用打包脚本（推荐）

```bash
python tools/build_exe.py
```

脚本会自动：
- 检查 PyInstaller 是否安装
- 检查所有依赖
- 检查前端构建文件
- 执行打包
- 输出可执行文件到 `dist_exe/` 目录

### 方法 2: 手动使用 PyInstaller

```bash
pyinstaller build.spec
```

## 打包配置

- **配置文件**: `build.spec`
- **输出目录**: `dist_exe/`
- **可执行文件名**: 
  - Windows: `ClawCat.exe`
  - macOS/Linux: `ClawCat`

## 打包内容

打包后的可执行文件包含：
- Python 解释器和所有依赖
- `launch_window.py` 和 `server.py`
- `dist/` 目录（前端构建文件）
- `public/` 目录（Live2D 模型）

## 注意事项

1. **前端服务器**: 打包后的可执行文件仍然需要前端服务器运行在 `http://localhost:6173`。你可以：
   - 使用 `npm run dev` 启动开发服务器
   - 或使用 `python -m http.server 6173 --directory dist` 启动静态文件服务器

2. **文件大小**: 由于包含 PyQt5 和 PyQtWebEngine，打包后的文件会比较大（通常 100-200MB）。

3. **平台特定**: 需要在目标平台上打包（Windows 上打包 Windows 版本，macOS 上打包 macOS 版本）。

## 使用打包后的可执行文件

1. 确保前端服务器运行在 `http://localhost:6173`
2. 运行可执行文件：
   ```bash
   # Windows
   dist_exe/ClawCat.exe
   
   # macOS/Linux
   dist_exe/ClawCat
   ```

## 故障排除

### PyInstaller 找不到模块

如果遇到模块导入错误，在 `build.spec` 的 `hiddenimports` 中添加缺失的模块。

### PyQtWebEngine 问题

如果 PyQtWebEngine 相关功能不工作，可能需要：
1. 确保 PyQtWebEngine 已正确安装
2. 检查 `hiddenimports` 中是否包含所有 PyQt5 相关模块

### 前端文件未包含

确保 `build.spec` 中的 `datas` 部分正确包含了 `dist/` 和 `public/` 目录。


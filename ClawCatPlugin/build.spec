# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for ClawCat
打包 launch_window.py (包含 server)
"""

import sys
import os
from pathlib import Path

# 获取项目根目录
# PyInstaller 设置 SPECPATH 为 spec 文件所在目录（不是文件路径）
try:
    # SPECPATH 是目录路径，直接使用
    PLUGIN_ROOT = Path(SPECPATH).resolve()
except NameError:
    # 如果 SPECPATH 不存在，使用当前文件所在目录
    PLUGIN_ROOT = Path(__file__).parent.resolve()

# 调试：打印路径确认
# print(f"PLUGIN_ROOT: {PLUGIN_ROOT}")
# print(f"launch_window.py: {PLUGIN_ROOT / 'src' / 'launch_window.py'}")
# print(f"Exists: {(PLUGIN_ROOT / 'src' / 'launch_window.py').exists()}")

block_cipher = None

# 使用绝对路径确保正确
launch_window_path = str(PLUGIN_ROOT / 'src' / 'launch_window.py')
public_path = str(PLUGIN_ROOT / 'public')
icon_path = str(PLUGIN_ROOT / 'icon.ico')

# 验证文件存在
if not os.path.exists(launch_window_path):
    raise FileNotFoundError(f"launch_window.py not found at: {launch_window_path}")
if not os.path.exists(public_path):
    raise FileNotFoundError(f"public directory not found at: {public_path}")

# 检查图标文件
if not os.path.exists(icon_path):
    print(f"[WARN] Icon file not found: {icon_path}")
    print("  Icon will not be embedded in the executable")
    icon_path = None
else:
    print(f"[INFO] Using icon: {icon_path}")

a = Analysis(
    [launch_window_path],
    pathex=[str(PLUGIN_ROOT / 'src'), str(PLUGIN_ROOT)],
    binaries=[],
    datas=[
        # 包含 public 目录（前端构建文件、Live2D 模型等）- server 会提供这些文件
        (public_path, 'public'),
        # 包含图标文件（用于系统托盘）
    ] + ([
        (icon_path, '.'),
    ] if icon_path and os.path.exists(icon_path) else []) + ([
        (str(PLUGIN_ROOT / 'public' / 'logo.png'), '.'),
    ] if os.path.exists(str(PLUGIN_ROOT / 'public' / 'logo.png')) else []),
    hiddenimports=[
        'PyQt5',
        'PyQt5.QtCore',
        'PyQt5.QtWidgets',
        'PyQt5.QtGui',
        'PyQt5.QtWebEngineWidgets',
        'PyQt5.QtWebEngineCore',
        'server',
        'window_control',
        'window_control_mac',
        'requests',
        'psutil',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # 排除不需要的 Qt 模块以减小体积
        'PyQt5.QtBluetooth',
        'PyQt5.QtDBus',
        'PyQt5.QtDesigner',
        'PyQt5.QtHelp',
        'PyQt5.QtLocation',
        'PyQt5.QtMultimedia',
        'PyQt5.QtMultimediaWidgets',
        'PyQt5.QtNfc',
        'PyQt5.QtOpenGL',
        'PyQt5.QtPositioning',
        'PyQt5.QtQml',
        'PyQt5.QtQuick',
        'PyQt5.QtQuickWidgets',
        'PyQt5.QtSensors',
        'PyQt5.QtSerialPort',
        'PyQt5.QtSql',
        'PyQt5.QtSvg',
        'PyQt5.QtTest',
        'PyQt5.QtWebSockets',
        'PyQt5.QtXml',
        'PyQt5.QtXmlPatterns',
        # 排除不需要的 Python 模块
        'pydoc',
        'doctest',
        'unittest',
        'test',
        'distutils',
        'email',
        'http',
        'xml',
        'xmlrpc',
        'pdb',
        'pydoc_data',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# 直接输出到 public 目录
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ClawCat',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,  # Windows 上通常没有 strip 工具，禁用以避免警告
    upx=True,  # 使用 UPX 压缩（需要在 PATH 中或通过 build_exe.py 自动配置）
    upx_exclude=[
        # Python DLL 通常无法被 UPX 压缩
        'python*.dll',
        # PyQt5 DLL 可能无法压缩
        'PyQt5/Qt5/bin/*.dll',
        # QtWebEngine 相关文件
        'QtWebEngineProcess.exe',
    ],
    runtime_tmpdir=None,
    console=False,  # Windows: 不显示控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_path if icon_path else None,
    distpath=str(PLUGIN_ROOT / 'public'),  # 直接输出到 public 目录
)


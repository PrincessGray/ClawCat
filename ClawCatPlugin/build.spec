# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for ClawCat
打包 launch_window.py (包含 server)
"""

import sys
from pathlib import Path

# 获取项目根目录
try:
    PLUGIN_ROOT = Path(SPECPATH).parent
except NameError:
    # 如果 SPECPATH 未定义，使用当前文件所在目录
    PLUGIN_ROOT = Path(__file__).parent

block_cipher = None

a = Analysis(
    [str(PLUGIN_ROOT / 'src' / 'launch_window.py')],
    pathex=[str(PLUGIN_ROOT / 'src')],
    binaries=[],
    datas=[
        # 包含 public 目录（前端构建文件、Live2D 模型等）- server 会提供这些文件
        (str(PLUGIN_ROOT / 'public'), 'public'),
    ],
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
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

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
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Windows: 不显示控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # 可以添加 .ico 文件路径
)


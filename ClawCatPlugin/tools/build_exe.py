#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ClawCat 打包脚本
使用 PyInstaller 打包 launch_window.py 为可执行文件
"""

import sys
import subprocess
import shutil
import io
import os
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

PLUGIN_ROOT = Path(__file__).parent.parent.absolute()
SPEC_FILE = PLUGIN_ROOT / "build.spec"
DIST_DIR = PLUGIN_ROOT / "dist"  # PyInstaller 默认输出目录
BUILD_DIR = PLUGIN_ROOT / "build"
PUBLIC_DIR = PLUGIN_ROOT / "public"  # 目标目录

def check_pyinstaller():
    """检查 PyInstaller 是否已安装"""
    try:
        import PyInstaller
        print(f"[OK] PyInstaller found: {PyInstaller.__version__}")
        return True
    except ImportError:
        print("[ERROR] PyInstaller not found")
        print("  Installing PyInstaller...")
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "pyinstaller"],
                stdout=sys.stdout,
                stderr=sys.stderr
            )
            print("[OK] PyInstaller installed")
            return True
        except subprocess.CalledProcessError:
            print("[ERROR] Failed to install PyInstaller")
            return False

def check_dependencies():
    """检查依赖是否已安装"""
    required = {
        "PyQt5": "PyQt5",
        "PyQtWebEngine": "PyQt5.QtWebEngineWidgets",  # PyQtWebEngine 需要这样导入
        "requests": "requests",
        "psutil": "psutil"
    }
    missing = []
    
    for package_name, import_name in required.items():
        try:
            __import__(import_name)
        except ImportError:
            missing.append(package_name)
    
    if missing:
        print(f"[ERROR] Missing dependencies: {', '.join(missing)}")
        print("  Install them with: pip install -r requirements.txt")
        return False
    
    print("[OK] All dependencies found")
    return True

def create_icon():
    """从 logo.png 创建图标文件"""
    try:
        from PIL import Image
        
        # 使用 logo.png
        logo_path = PLUGIN_ROOT / "public" / "logo.png"
        
        if not logo_path.exists():
            print(f"[WARN] logo.png not found at {logo_path}, skipping icon creation")
            return None
        
        # 创建图标文件
        icon_path = PLUGIN_ROOT / "icon.ico"
        
        # 打开图片并调整大小
        img = Image.open(logo_path)
        # 创建多个尺寸的图标（Windows 需要）
        sizes = [(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)]
        img.save(icon_path, format='ICO', sizes=sizes)
        
        print(f"[OK] Icon created from logo.png: {icon_path}")
        return icon_path
    except ImportError:
        print("[WARN] PIL/Pillow not installed, skipping icon creation")
        print("  Install with: pip install Pillow")
        return None
    except Exception as e:
        print(f"[WARN] Failed to create icon: {e}")
        return None

def check_dist():
    """检查前端构建文件是否存在"""
    public_dir = PLUGIN_ROOT / "public"
    if not public_dir.exists():
        print("[ERROR] Frontend public/ directory not found")
        print("  Build frontend first with: npm run build")
        return False
    
    index_html = public_dir / "index.html"
    if not index_html.exists():
        print("[ERROR] Frontend index.html not found in public/")
        print("  Build frontend first with: npm run build")
        return False
    
    print("[OK] Frontend build found in public/")
    return True

def build():
    """执行打包"""
    print("=" * 60)
    print("  ClawCat Build Script")
    print("=" * 60)
    print()
    
    # 检查依赖
    if not check_pyinstaller():
        return False
    
    if not check_dependencies():
        return False
    
    if not check_dist():
        return False
    
    # 创建图标文件
    icon_path = create_icon()
    
    # 清理旧的构建文件
    if DIST_DIR.exists():
        print(f"Cleaning old build directory: {DIST_DIR}")
        shutil.rmtree(DIST_DIR)
    
    if BUILD_DIR.exists():
        print(f"Cleaning old build cache: {BUILD_DIR}")
        shutil.rmtree(BUILD_DIR)
    
    # 执行打包
    print()
    print("Building executable...")
    print(f"  Spec file: {SPEC_FILE}")
    print(f"  Output: {DIST_DIR}")
    print()
    
    # 配置 UPX 路径（如果存在）
    upx_path = Path("C:/Users/45391/Downloads/upx-5.1.0-win64/upx-5.1.0-win64")
    env = os.environ.copy()
    if sys.platform == 'win32' and upx_path.exists() and (upx_path / "upx.exe").exists():
        # 将 UPX 目录添加到 PATH
        current_path = env.get("PATH", "")
        env["PATH"] = str(upx_path) + os.pathsep + current_path
        print(f"[OK] UPX found at: {upx_path}")
        print("  UPX compression will be enabled")
    else:
        print("[INFO] UPX not found, compression will be disabled")
    
    print()
    
    try:
        subprocess.check_call(
            [sys.executable, "-m", "PyInstaller", str(SPEC_FILE)],
            cwd=str(PLUGIN_ROOT),
            env=env,
            stdout=sys.stdout,
            stderr=sys.stderr
        )
        
        # Executable is already in public/ directory (configured in build.spec with distpath)
        if sys.platform == 'win32':
            exe_name = 'ClawCat.exe'
        else:
            exe_name = 'ClawCat'
        
        exe_path = PUBLIC_DIR / exe_name
        
        print()
        print("=" * 60)
        print("[OK] Build completed successfully!")
        print("=" * 60)
        print(f"  Executable: {exe_path}")
        if exe_path.exists():
            print(f"  Icon: Applied from logo.png")
        print()
        return True
        
    except subprocess.CalledProcessError as e:
        print()
        print("[ERROR] Build failed")
        print(f"  Error: {e}")
        return False

if __name__ == "__main__":
    success = build()
    sys.exit(0 if success else 1)


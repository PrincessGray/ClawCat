#!/usr/bin/env python3
"""
ClawCat 打包脚本
使用 PyInstaller 打包 launch_window.py 为可执行文件
"""

import sys
import subprocess
import shutil
from pathlib import Path

PLUGIN_ROOT = Path(__file__).parent.parent.absolute()
SPEC_FILE = PLUGIN_ROOT / "build.spec"
DIST_DIR = PLUGIN_ROOT / "dist_exe"
BUILD_DIR = PLUGIN_ROOT / "build"

def check_pyinstaller():
    """检查 PyInstaller 是否已安装"""
    try:
        import PyInstaller
        print(f"✓ PyInstaller found: {PyInstaller.__version__}")
        return True
    except ImportError:
        print("✗ PyInstaller not found")
        print("  Installing PyInstaller...")
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "pyinstaller"],
                stdout=sys.stdout,
                stderr=sys.stderr
            )
            print("✓ PyInstaller installed")
            return True
        except subprocess.CalledProcessError:
            print("✗ Failed to install PyInstaller")
            return False

def check_dependencies():
    """检查依赖是否已安装"""
    required = ["PyQt5", "PyQtWebEngine", "requests", "psutil"]
    missing = []
    
    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"✗ Missing dependencies: {', '.join(missing)}")
        print("  Install them with: pip install -r requirements.txt")
        return False
    
    print("✓ All dependencies found")
    return True

def check_dist():
    """检查前端构建文件是否存在"""
    public_dir = PLUGIN_ROOT / "public"
    if not public_dir.exists():
        print("✗ Frontend public/ directory not found")
        print("  Build frontend first with: npm run build")
        return False
    
    index_html = public_dir / "index.html"
    if not index_html.exists():
        print("✗ Frontend index.html not found in public/")
        print("  Build frontend first with: npm run build")
        return False
    
    print("✓ Frontend build found in public/")
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
    
    try:
        subprocess.check_call(
            [sys.executable, "-m", "PyInstaller", str(SPEC_FILE)],
            cwd=str(PLUGIN_ROOT),
            stdout=sys.stdout,
            stderr=sys.stderr
        )
        
        print()
        print("=" * 60)
        print("✓ Build completed successfully!")
        print("=" * 60)
        print(f"  Executable: {DIST_DIR / 'ClawCat.exe' if sys.platform == 'win32' else DIST_DIR / 'ClawCat'}")
        print()
        return True
        
    except subprocess.CalledProcessError as e:
        print()
        print("✗ Build failed")
        print(f"  Error: {e}")
        return False

if __name__ == "__main__":
    success = build()
    sys.exit(0 if success else 1)


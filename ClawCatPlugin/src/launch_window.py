#!/usr/bin/env python3
"""
ClawCat Window Launcher - PyQt5 版本
支持透明背景、无边框窗口
"""
import sys
import os
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings
from PyQt5.QtGui import QScreen, QColor

# 导入同目录下的 server 模块
try:
    from .server import start_server
except ImportError:
    from server import start_server

# 配置
FRONTEND_URL = 'http://localhost:6173'  # Vite 开发服务器

# 根据 cover.png 的实际比例设置窗口尺寸
# cover.png: 612x354, 比例 1.73:1
DEFAULT_MODEL_WIDTH = 612    # 默认模型宽度（像素，来自 cover.png）
DEFAULT_MODEL_HEIGHT = 354   # 默认模型高度（像素，来自 cover.png）
DEFAULT_SCALE = 1.0          # 默认缩放比例（100%，使用原始尺寸）

# 计算窗口尺寸
WINDOW_WIDTH = int(DEFAULT_MODEL_WIDTH * DEFAULT_SCALE)
WINDOW_HEIGHT = int(DEFAULT_MODEL_HEIGHT * DEFAULT_SCALE)


class TransparentWebView(QWebEngineView):
    """透明背景的 WebView"""
    
    def __init__(self):
        super().__init__()
        
        # 设置窗口属性
        self.setWindowFlags(
            Qt.FramelessWindowHint |  # 无边框
            Qt.WindowStaysOnTopHint |  # 置顶
            Qt.Tool  # 不显示在任务栏（可选）
        )
        
        # 设置透明背景（关键！）
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # 设置网页背景透明（关键！）
        self.page().setBackgroundColor(QColor(0, 0, 0, 0))  # 完全透明
        
        # 启用透明背景支持
        settings = self.settings()
        settings.setAttribute(QWebEngineSettings.ShowScrollBars, False)
        settings.setAttribute(QWebEngineSettings.LocalContentCanAccessFileUrls, True)
        
        # 设置窗口大小
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
        
        # 加载前端页面
        self.load(QUrl(FRONTEND_URL))
        
        # 拖动相关
        self.drag_position = None
    
    def mousePressEvent(self, event):
        """鼠标按下事件 - 用于拖动窗口"""
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        """鼠标移动事件 - 拖动窗口"""
        if event.buttons() == Qt.LeftButton and self.drag_position:
            self.move(event.globalPos() - self.drag_position)
            event.accept()
    
    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        self.drag_position = None


def position_window_bottom_right(window):
    """将窗口定位到屏幕右下角"""
    screen = QApplication.primaryScreen()
    screen_geometry = screen.availableGeometry()
    
    x = screen_geometry.width() - window.width() - 20
    y = screen_geometry.height() - window.height() - 20
    
    window.move(x, y)


def main():
    """主函数"""
    print("=" * 50)
    print("  ClawCat Window Launcher (PyQt5)")
    print("=" * 50)
    
    # 启动后端服务器
    print("Starting ClawCat server on port 22622...")
    server, server_thread = start_server()
    print("✅ Server started successfully")
    
    # 创建 Qt 应用
    app = QApplication(sys.argv)
    
    # 创建透明窗口
    print("Creating transparent window...")
    window = TransparentWebView()
    
    # 定位到右下角
    position_window_bottom_right(window)
    
    # 显示窗口
    window.show()
    
    print("Launching window...")
    print(f"  URL: {FRONTEND_URL}")
    print(f"  Size: {WINDOW_WIDTH}x{WINDOW_HEIGHT}")
    print(f"  Position: Bottom-right corner")
    print(f"  Frameless: Yes")
    print(f"  Transparent: Yes")
    print("\n💡 Drag the window to move it")
    print("💡 Press Ctrl+C to exit\n")
    
    # 运行应用
    try:
        sys.exit(app.exec_())
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.shutdown()


if __name__ == "__main__":
    main()


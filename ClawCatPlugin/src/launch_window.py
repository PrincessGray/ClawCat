#!/usr/bin/env python3
"""
ClawCat Window Launcher - PyQt5 版本
支持透明背景、无边框窗口
"""
import sys
import os
from PyQt5.QtCore import Qt, QUrl, QPoint
from PyQt5.QtWidgets import QApplication, QMenu, QAction
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
        # 移除 Qt.Tool 以显示在任务栏，保留无边框和置顶
        self.setWindowFlags(
            Qt.FramelessWindowHint |  # 无边框
            Qt.WindowStaysOnTopHint   # 置顶
            # 移除 Qt.Tool 以显示在任务栏
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
    
    def contextMenuEvent(self, event):
        """右键菜单事件"""
        menu = QMenu(self)
        
        # 大小调整选项
        size_menu = menu.addMenu("大小")
        size_50 = QAction("50%", self)
        size_75 = QAction("75%", self)
        size_100 = QAction("100%", self)
        size_125 = QAction("125%", self)
        size_150 = QAction("150%", self)
        size_200 = QAction("200%", self)
        
        size_50.triggered.connect(lambda: self.resize_window(0.5))
        size_75.triggered.connect(lambda: self.resize_window(0.75))
        size_100.triggered.connect(lambda: self.resize_window(1.0))
        size_125.triggered.connect(lambda: self.resize_window(1.25))
        size_150.triggered.connect(lambda: self.resize_window(1.5))
        size_200.triggered.connect(lambda: self.resize_window(2.0))
        
        size_menu.addAction(size_50)
        size_menu.addAction(size_75)
        size_menu.addAction(size_100)
        size_menu.addAction(size_125)
        size_menu.addAction(size_150)
        size_menu.addAction(size_200)
        
        menu.addSeparator()
        
        # 最小化
        minimize_action = QAction("最小化", self)
        minimize_action.triggered.connect(self.showMinimized)
        menu.addAction(minimize_action)
        
        # 置顶切换
        topmost_action = QAction("取消置顶" if self.windowFlags() & Qt.WindowStaysOnTopHint else "置顶", self)
        topmost_action.triggered.connect(self.toggle_topmost)
        menu.addAction(topmost_action)
        
        menu.addSeparator()
        
        # 退出
        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.close)
        menu.addAction(exit_action)
        
        menu.exec_(event.globalPos())
    
    def resize_window(self, scale):
        """调整窗口大小"""
        new_width = int(DEFAULT_MODEL_WIDTH * scale)
        new_height = int(DEFAULT_MODEL_HEIGHT * scale)
        self.resize(new_width, new_height)
        print(f"[Window] Resized to {new_width}x{new_height} (scale: {scale})", file=sys.stderr, flush=True)
    
    def toggle_topmost(self):
        """切换置顶状态"""
        if self.windowFlags() & Qt.WindowStaysOnTopHint:
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)
            print("[Window] Topmost disabled", file=sys.stderr, flush=True)
        else:
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
            print("[Window] Topmost enabled", file=sys.stderr, flush=True)
        self.show()  # 重新显示窗口以应用标志


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


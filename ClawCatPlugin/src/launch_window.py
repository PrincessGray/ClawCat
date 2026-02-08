#!/usr/bin/env python3
"""
ClawCat Window Launcher - PyQt5 版本
支持透明背景、无边框窗口
"""
import sys
import os
from pathlib import Path
from datetime import datetime
from PyQt5.QtCore import Qt, QUrl, QPoint
from PyQt5.QtWidgets import QApplication, QMenu, QAction, QSystemTrayIcon
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings
from PyQt5.QtGui import QScreen, QColor, QIcon

# 日志文件配置
LOG_DIR = Path.home() / ".claude" / "clawcat" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / f"clawcat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

# 设置日志文件
class TeeOutput:
    """同时输出到文件和控制台"""
    def __init__(self, file_path, stream):
        self.file = open(file_path, 'w', encoding='utf-8', errors='replace')
        self.stream = stream
        self.isatty = stream.isatty if hasattr(stream, 'isatty') else lambda: False
    
    def write(self, text):
        try:
            self.stream.write(text)
            self.file.write(text)
            self.file.flush()
        except:
            pass  # 忽略写入错误
    
    def flush(self):
        try:
            self.stream.flush()
            self.file.flush()
        except:
            pass
    
    def close(self):
        try:
            self.file.close()
        except:
            pass

# 保存原始 stderr
_original_stderr = sys.stderr

# 重定向 stderr 到日志文件和控制台
sys.stderr = TeeOutput(LOG_FILE, _original_stderr)

# 导入同目录下的 server 模块
try:
    from .server import start_server
except ImportError:
    from server import start_server

# 配置
# 统一使用服务器 URL（server 会提供前端文件）
FRONTEND_URL = 'http://localhost:22622/'

# 获取资源文件路径（支持打包和开发模式）
def get_resource_path(relative_path):
    """获取资源文件路径（支持打包和开发模式）"""
    if getattr(sys, 'frozen', False):
        # 打包模式：从临时目录或 exe 所在目录
        base_path = Path(sys.executable).parent
    else:
        # 开发模式：从项目根目录
        base_path = Path(__file__).parent.parent
    
    return base_path / relative_path

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
        # 使用 Qt.Tool 和 Qt.FramelessWindowHint 以隐藏任务栏显示
        self.setWindowFlags(
            Qt.FramelessWindowHint |  # 无边框
            Qt.WindowStaysOnTopHint |  # 置顶
            Qt.Tool  # 不显示在任务栏，只显示在系统托盘
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
        self.dragging = False
        
        # 设置鼠标跟踪，确保能捕获所有鼠标移动事件
        self.setMouseTracking(True)
    
    def mousePressEvent(self, event):
        """鼠标按下事件 - 用于拖动窗口"""
        # 左键按下时开始拖动
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            self.dragging = True
            # 设置鼠标捕获，确保能接收到所有鼠标事件
            self.setCursor(Qt.ClosedHandCursor)
            event.accept()
            return
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """鼠标移动事件 - 拖动窗口"""
        # 如果正在拖动，移动窗口
        if self.dragging and event.buttons() == Qt.LeftButton and self.drag_position:
            new_pos = event.globalPos() - self.drag_position
            self.move(new_pos)
            event.accept()
            return
        super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        if event.button() == Qt.LeftButton:
            self.drag_position = None
            self.dragging = False
            # 恢复默认光标
            self.setCursor(Qt.ArrowCursor)
            event.accept()
            return
        super().mouseReleaseEvent(event)
    
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
        """调整窗口大小，保持右边和下边贴着桌面边缘"""
        new_width = int(DEFAULT_MODEL_WIDTH * scale)
        new_height = int(DEFAULT_MODEL_HEIGHT * scale)
        
        # 获取屏幕尺寸
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        
        # 计算新位置：右边和下边贴着屏幕边缘
        new_x = screen_geometry.width() - new_width - 5  # 右边留 5px 边距
        new_y = screen_geometry.height() - new_height - 5  # 下边留 5px 边距
        
        # 先调整大小，再移动位置
        self.resize(new_width, new_height)
        self.move(new_x, new_y)
        
        print(f"[Window] Resized to {new_width}x{new_height} (scale: {scale})", file=sys.stderr, flush=True)
        print(f"[Window] Position: ({new_x}, {new_y}) - Right and bottom aligned", file=sys.stderr, flush=True)
    
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
    
    x = screen_geometry.width() - window.width() - 5
    y = screen_geometry.height() - window.height() - 5
    
    window.move(x, y)


def main():
    """主函数"""
    print("=" * 50, file=sys.stderr)
    print("  ClawCat Window Launcher (PyQt5)", file=sys.stderr)
    print("=" * 50, file=sys.stderr)
    print(f"📝 Log file: {LOG_FILE}", file=sys.stderr, flush=True)
    
    # 启动后端服务器
    print("Starting ClawCat server on port 22622...", file=sys.stderr, flush=True)
    server, server_thread = start_server()
    print("✅ Server started successfully", file=sys.stderr, flush=True)
    
    # 创建 Qt 应用
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # 关闭窗口时不退出应用
    
    # 创建透明窗口（无论是否有系统托盘都需要）
    print("Creating transparent window...", file=sys.stderr, flush=True)
    window = TransparentWebView()
    position_window_bottom_right(window)
    window.show()
    
    # 创建系统托盘图标
    tray = None
    if QSystemTrayIcon.isSystemTrayAvailable():
        # 查找图标文件
        icon_paths = [
            get_resource_path("icon.ico"),
            get_resource_path("public/logo.png"),
            get_resource_path("logo.png"),
        ]
        
        tray_icon = None
        for icon_path in icon_paths:
            if icon_path.exists():
                tray_icon = QIcon(str(icon_path))
                print(f"✅ Using tray icon: {icon_path}", file=sys.stderr, flush=True)
                break
        
        if tray_icon is None:
            # 使用默认图标
            tray_icon = QIcon()
            print("⚠ No icon found, using default", file=sys.stderr, flush=True)
        
        # 创建系统托盘
        tray = QSystemTrayIcon(app)
        tray.setIcon(tray_icon)
        tray.setToolTip("ClawCat")
        
        # 创建托盘菜单
        tray_menu = QMenu()
        
        # 显示/隐藏窗口
        show_action = QAction("显示窗口", tray_menu)
        show_action.triggered.connect(lambda: (window.show(), window.raise_(), window.activateWindow()))
        tray_menu.addAction(show_action)
        
        hide_action = QAction("隐藏窗口", tray_menu)
        hide_action.triggered.connect(window.hide)
        tray_menu.addAction(hide_action)
        
        tray_menu.addSeparator()
        
        # 退出
        quit_action = QAction("退出", tray_menu)
        quit_action.triggered.connect(lambda: (server.shutdown(), app.quit()))
        tray_menu.addAction(quit_action)
        
        tray.setContextMenu(tray_menu)
        
        # 托盘图标点击事件（显示/隐藏窗口）
        def toggle_window(reason):
            if reason == QSystemTrayIcon.Trigger:  # 左键单击
                if window.isVisible():
                    window.hide()
                else:
                    window.show()
                    window.raise_()
                    window.activateWindow()
        
        tray.activated.connect(toggle_window)
        
        # 显示托盘图标
        tray.show()
        print("✅ System tray icon created", file=sys.stderr, flush=True)
    else:
        print("⚠ System tray is not available", file=sys.stderr, flush=True)
    
    print("Launching window...", file=sys.stderr, flush=True)
    print(f"  URL: {FRONTEND_URL}", file=sys.stderr, flush=True)
    print(f"  Size: {WINDOW_WIDTH}x{WINDOW_HEIGHT}", file=sys.stderr, flush=True)
    print(f"  Position: Bottom-right corner", file=sys.stderr, flush=True)
    print(f"  Frameless: Yes", file=sys.stderr, flush=True)
    print(f"  Transparent: Yes", file=sys.stderr, flush=True)
    print(f"  Taskbar: Hidden (System tray only)", file=sys.stderr, flush=True)
    print(f"\n💡 Click tray icon to show/hide window", file=sys.stderr, flush=True)
    print(f"💡 Right-click tray icon for menu", file=sys.stderr, flush=True)
    print(f"📝 Logs: {LOG_FILE}\n", file=sys.stderr, flush=True)
    
    # 运行应用
    try:
        sys.exit(app.exec_())
    except KeyboardInterrupt:
        print("\nShutting down...", file=sys.stderr, flush=True)
        server.shutdown()
    finally:
        # 关闭日志文件
        if hasattr(sys.stderr, 'close'):
            sys.stderr.close()


if __name__ == "__main__":
    main()


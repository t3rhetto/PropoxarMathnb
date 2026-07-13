"""macOS Liquid Glass 窗口效果封装

使用PyObjC调用NSVisualEffectView实现原生液态玻璃效果。
"""

import sys
import platform
from PySide6.QtCore import Qt, QPoint, QTimer
from PySide6.QtGui import QColor, QPainter, QBrush
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout

# macOS原生实现
if sys.platform == "darwin":
    try:
        _mac_ver = tuple(int(x) for x in platform.mac_ver()[0].split("."))
        HAS_MODERN_MACOS = _mac_ver >= (15, 0)
    except (ValueError, IndexError):
        HAS_MODERN_MACOS = False
    
    if HAS_MODERN_MACOS:
        try:
            import objc
            from Cocoa import (
                NSVisualEffectView, NSWindow, NSColor, NSView,
                NSVisualEffectBlendingModeBehindWindow,
                NSVisualEffectMaterial,
                NSWindowStyleMaskTitled,
                NSWindowStyleMaskClosable,
                NSWindowStyleMaskMiniaturizable,
                NSWindowStyleMaskResizable,
                NSWindowStyleMaskFullSizeContentView,
                NSBackingStoreBuffered,
            )
            from Quartz import CALayer
            HAS_NATIVE_GLASS = True
        except ImportError:
            HAS_NATIVE_GLASS = False
    else:
        HAS_NATIVE_GLASS = False
else:
    HAS_NATIVE_GLASS = False


class GlassWindow(QMainWindow):
    """液态玻璃风格主窗口"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("MathNotebook")
        self.setMinimumSize(1000, 700)
        self._native_glass_ready = False
        
        if HAS_NATIVE_GLASS:
            # 延迟到窗口显示后再设置原生玻璃效果，确保原生句柄已就绪
            QTimer.singleShot(0, self._setup_native_glass)
        else:
            self._setup_fallback_glass()
        
        # 设置中心部件
        self._setup_central_widget()
    
    def _setup_native_glass(self):
        """使用原生NSVisualEffectView实现液态玻璃效果"""
        if self._native_glass_ready:
            return
        
        try:
            # 通过winId获取原生窗口句柄，需要用objc转换
            win_id = int(self.winId())
            ns_window = objc.objc_object(c_void_p=win_id)
            
            # 设置窗口样式：无标题栏背景，全尺寸内容视图
            style_mask = (
                NSWindowStyleMaskTitled |
                NSWindowStyleMaskClosable |
                NSWindowStyleMaskMiniaturizable |
                NSWindowStyleMaskResizable |
                NSWindowStyleMaskFullSizeContentView
            )
            ns_window.setStyleMask_(style_mask)
            ns_window.setTitlebarAppearsTransparent_(True)
            ns_window.setTitleVisibility_(1)  # NSWindowTitleHidden
            
            # 设置窗口背景为透明
            ns_window.setBackgroundColor_(NSColor.clearColor())
            
            # 创建NSVisualEffectView
            content_view = ns_window.contentView()
            bounds = content_view.bounds()
            
            self._glass_view = NSVisualEffectView.alloc().initWithFrame_(bounds)
            self._glass_view.setAutoresizingMask_(18)  # Width + Height flexible
            self._glass_view.setBlendingMode_(NSVisualEffectBlendingModeBehindWindow)
            self._glass_view.setMaterial_(NSVisualEffectMaterial.underWindowBackground)
            self._glass_view.setState_(1)  # NSVisualEffectStateActive
            self._glass_view.setAppearance_(None)  # 跟随系统
            
            # 添加到内容视图
            content_view.addSubview_(self._glass_view)
            self._native_glass_ready = True
        except Exception as e:
            # 原生效果设置失败时降级处理
            print(f"[GlassWindow] 原生玻璃效果设置失败，使用降级方案: {e}")
            self._setup_fallback_glass()
    
    def _setup_fallback_glass(self):
        """降级方案：使用Qt样式模拟毛玻璃效果"""
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("""
            QMainWindow {
                background: rgba(255, 255, 255, 0.85);
            }
        """)
    
    def _setup_central_widget(self):
        """设置中心部件"""
        central = QWidget()
        central.setStyleSheet("background: transparent;")
        self.setCentralWidget(central)
        return central
    
    def paintEvent(self, event):
        """绘制背景模糊效果（降级方案）"""
        if HAS_NATIVE_GLASS:
            super().paintEvent(event)
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 绘制半透明背景
        bg_color = QColor(255, 255, 255, 220)  # 85%不透明度
        painter.fillRect(self.rect(), bg_color)
        
        super().paintEvent(event)


class GlassWidget(QWidget):
    """液态玻璃风格部件（用于嵌入内容）"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground)
    
    def paintEvent(self, event):
        """绘制半透明玻璃背景"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 绘制圆角矩形背景
        bg_color = QColor(255, 255, 255, 180)  # 70%不透明度
        painter.setBrush(QBrush(bg_color))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), 12, 12)
        
        super().paintEvent(event)


def create_glass_window(title="MathNotebook", size=(1000, 700)):
    """创建液态玻璃窗口的工厂函数"""
    window = GlassWindow()
    window.setWindowTitle(title)
    window.resize(*size)
    return window

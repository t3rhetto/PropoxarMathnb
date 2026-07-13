"""MathNotebook - AI驱动的高数学习助手

Mac桌面应用入口
"""

import sys
import os

# 确保能找到math_notebook包
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QCoreApplication
from PySide6.QtGui import QIcon

from gui.main_window import MainWindow


def setup_app_info():
    """设置应用信息"""
    QCoreApplication.setApplicationName("MathNotebook")
    QCoreApplication.setApplicationVersion("1.0.0")
    QCoreApplication.setOrganizationName("MathNotebook")
    QCoreApplication.setOrganizationDomain("mathnotebook.app")


def setup_macos_specific(app: QApplication):
    """设置macOS特定属性"""
    if sys.platform == "darwin":
        # 设置应用图标（如果有的话）
        # icon_path = os.path.join(os.path.dirname(__file__), "resources", "icon.icns")
        # if os.path.exists(icon_path):
        #     app.setWindowIcon(QIcon(icon_path))
        pass


def main():
    """主函数"""
    # 设置高DPI支持
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
    
    # 创建应用
    app = QApplication(sys.argv)
    
    # 设置应用信息
    setup_app_info()
    
    # macOS特定设置
    setup_macos_specific(app)
    
    # 设置全局样式
    app.setStyleSheet("""
        QMainWindow {
            background: transparent;
        }
        QWidget {
            font-family: -apple-system, "PingFang SC", "Microsoft YaHei", sans-serif;
        }
        QToolTip {
            background: rgba(30, 30, 30, 0.9);
            color: white;
            border: none;
            border-radius: 6px;
            padding: 8px 12px;
            font-size: 12px;
        }
    """)
    
    # 创建主窗口
    window = MainWindow()
    window.show()
    
    # 运行应用
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

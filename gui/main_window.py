"""主窗口 - 整合所有组件"""

import sys
import os
from pathlib import Path
from PySide6.QtCore import Qt, QSize, QTimer
from PySide6.QtGui import QIcon, QAction, QActionGroup
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QStackedWidget, QPushButton, QLabel, QFrame,
    QMenuBar, QMenu, QMessageBox, QApplication
)

from gui.glass_window import GlassWindow, GlassWidget
from gui.upload_widget import UploadWidget
from gui.analysis_page import AnalysisResultPage, AnalysisLoadingWidget
from gui.task_manager import get_task_manager
from math_notebook.config import Config, get_default_config
from math_notebook.extractor import extract_source
from math_notebook.analyzer import analyze_content


class SidebarButton(QPushButton):
    """侧边栏按钮"""
    
    def __init__(self, text: str, icon: str, parent=None):
        super().__init__(parent)
        self.setText(f"{icon}  {text}")
        self.setCheckable(True)
        self.setFixedHeight(48)
        self.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                text-align: left;
                font-size: 14px;
                color: #666;
            }
            QPushButton:checked {
                background: rgba(0, 122, 255, 0.15);
                color: #007AFF;
                font-weight: 500;
            }
            QPushButton:hover {
                background: rgba(0, 0, 0, 0.05);
            }
        """)


class MainWindow(GlassWindow):
    """主窗口"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._config = get_default_config()
        self._task_manager = get_task_manager()
        self._setup_ui()
        self._setup_menu()
        self._connect_signals()
    
    def _setup_ui(self):
        """设置UI"""
        # 获取中心部件
        central = self.centralWidget()
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 侧边栏
        self._setup_sidebar(main_layout)
        
        # 内容区域
        self._setup_content(main_layout)
    
    def _setup_sidebar(self, parent_layout):
        """设置侧边栏"""
        sidebar = QFrame()
        sidebar.setFixedWidth(200)
        sidebar.setStyleSheet("""
            QFrame {
                background: rgba(0, 0, 0, 0.03);
                border-right: 1px solid rgba(0, 0, 0, 0.1);
            }
        """)
        
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(12, 12, 12, 12)
        sidebar_layout.setSpacing(8)
        
        # Logo
        logo = QLabel("📚 MathNotebook")
        logo.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: 600;
                color: #1a1a1a;
                padding: 8px;
                border: none;
                background: transparent;
            }
        """)
        sidebar_layout.addWidget(logo)
        
        sidebar_layout.addSpacing(20)
        
        # 导航按钮
        self._btn_upload = SidebarButton("上传分析", "📄")
        self._btn_notes = SidebarButton("笔记预览", "📝")
        self._btn_review = SidebarButton("每日复习", "📊")
        self._btn_graph = SidebarButton("知识图谱", "🗺️")
        self._btn_settings = SidebarButton("设置", "⚙️")
        
        sidebar_layout.addWidget(self._btn_upload)
        sidebar_layout.addWidget(self._btn_notes)
        sidebar_layout.addWidget(self._btn_review)
        sidebar_layout.addWidget(self._btn_graph)
        sidebar_layout.addStretch()
        sidebar_layout.addWidget(self._btn_settings)
        
        # 版本信息
        version = QLabel("v1.0.0")
        version.setStyleSheet("""
            QLabel {
                color: #999;
                font-size: 11px;
                border: none;
                background: transparent;
            }
        """)
        sidebar_layout.addWidget(version)
        
        parent_layout.addWidget(sidebar)
    
    def _setup_content(self, parent_layout):
        """设置内容区域"""
        content = QWidget()
        content.setStyleSheet("background: transparent;")
        
        self._content_stack = QStackedWidget(content)
        
        # 上传分析页面
        self._upload_page = UploadWidget()
        self._content_stack.addWidget(self._upload_page)
        
        # 分析加载页面
        self._loading_page = AnalysisLoadingWidget()
        self._content_stack.addWidget(self._loading_page)
        
        # 分析结果页面
        self._result_page = AnalysisResultPage()
        self._content_stack.addWidget(self._result_page)
        
        # 笔记预览页面（占位）
        notes_placeholder = QLabel("📝 笔记预览\n\n此功能将在后续版本实现")
        notes_placeholder.setAlignment(Qt.AlignCenter)
        notes_placeholder.setStyleSheet("""
            QLabel {
                font-size: 16px;
                color: #666;
                border: none;
                background: transparent;
            }
        """)
        self._content_stack.addWidget(notes_placeholder)
        
        # 每日复习页面（占位）
        review_placeholder = QLabel("📊 每日复习\n\n此功能将在后续版本实现")
        review_placeholder.setAlignment(Qt.AlignCenter)
        review_placeholder.setStyleSheet("""
            QLabel {
                font-size: 16px;
                color: #666;
                border: none;
                background: transparent;
            }
        """)
        self._content_stack.addWidget(review_placeholder)
        
        # 知识图谱页面（占位）
        graph_placeholder = QLabel("🗺️ 知识图谱\n\n此功能将在后续版本实现")
        graph_placeholder.setAlignment(Qt.AlignCenter)
        graph_placeholder.setStyleSheet("""
            QLabel {
                font-size: 16px;
                color: #666;
                border: none;
                background: transparent;
            }
        """)
        self._content_stack.addWidget(graph_placeholder)
        
        # 设置页面（占位）
        settings_placeholder = QLabel("⚙️ 设置\n\n此功能将在后续版本实现")
        settings_placeholder.setAlignment(Qt.AlignCenter)
        settings_placeholder.setStyleSheet("""
            QLabel {
                font-size: 16px;
                color: #666;
                border: none;
                background: transparent;
            }
        """)
        self._content_stack.addWidget(settings_placeholder)
        
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.addWidget(self._content_stack)
        
        parent_layout.addWidget(content)
    
    def _setup_menu(self):
        """设置菜单栏"""
        menu_bar = self.menuBar()
        menu_bar.setStyleSheet("""
            QMenuBar {
                background: transparent;
            }
            QMenuBar::item {
                background: transparent;
                padding: 4px 8px;
            }
            QMenuBar::item:selected {
                background: rgba(0, 0, 0, 0.1);
                border-radius: 4px;
            }
        """)
        
        # 文件菜单
        file_menu = menu_bar.addMenu("文件")
        
        open_action = QAction("打开文件...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self._on_open_file)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        quit_action = QAction("退出", self)
        quit_action.setShortcut("Ctrl+Q")
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)
        
        # 编辑菜单
        edit_menu = menu_bar.addMenu("编辑")
        
        # 视图菜单
        view_menu = menu_bar.addMenu("视图")
        
        # 帮助菜单
        help_menu = menu_bar.addMenu("帮助")
        
        about_action = QAction("关于 MathNotebook", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _connect_signals(self):
        """连接信号"""
        # 侧边栏按钮 —— 使用 ButtonGroup 保证互斥
        from PySide6.QtWidgets import QButtonGroup
        self._sidebar_group = QButtonGroup(self)
        self._sidebar_group.setExclusive(True)
        self._sidebar_group.addButton(self._btn_upload, 0)
        self._sidebar_group.addButton(self._btn_notes, 3)
        self._sidebar_group.addButton(self._btn_review, 4)
        self._sidebar_group.addButton(self._btn_graph, 5)
        self._sidebar_group.addButton(self._btn_settings, 6)
        
        self._sidebar_group.idClicked.connect(self._switch_page)
        
        # 默认选中上传按钮
        self._btn_upload.setChecked(True)
        
        # 上传组件信号
        self._upload_page.analyze_requested.connect(self._on_analyze_file)
        
        # 任务管理器信号
        self._task_manager.task_started.connect(self._on_task_started)
        self._task_manager.task_finished.connect(self._on_task_finished)
        self._task_manager.task_error.connect(self._on_task_error)
        self._task_manager.task_progress.connect(self._on_task_progress)
    
    def _switch_page(self, index: int):
        """切换页面"""
        self._content_stack.setCurrentIndex(index)
        
        # ButtonGroup 已处理互斥，无需额外逻辑
    
    def _on_analyze_file(self, filepath: str):
        """请求分析文件"""
        # 显示加载页面
        self._content_stack.setCurrentIndex(1)
        self._loading_page.set_status(f"🔄 正在分析: {Path(filepath).name}")
        
        # 提交异步任务
        self._task_manager.submit_task(
            f"analyze_{filepath}",
            self._analyze_file_task,
            filepath
        )
    
    def _analyze_file_task(self, filepath: str):
        """分析文件任务（在后台线程执行）"""
        # 提取内容
        source_data = extract_source(filepath)
        
        # AI分析
        analysis = analyze_content(source_data, self._config)
        
        return analysis
    
    def _on_task_started(self, task_id: str):
        """任务开始"""
        pass
    
    def _on_task_finished(self, task_id: str, result):
        """任务完成"""
        if task_id.startswith("analyze_"):
            # 从chapters结构中提取所有concepts
            concepts = []
            for chapter in result.get("chapters", []):
                for section in chapter.get("sections", []):
                    for concept in section.get("concepts", []):
                        concept["chapter"] = chapter.get("title", "")
                        concept["section"] = section.get("title", "")
                        concepts.append(concept)
            
            # 显示结果页面
            self._result_page.set_analysis_result({"concepts": concepts})
            self._content_stack.setCurrentIndex(2)
    
    def _on_task_error(self, task_id: str, error: str):
        """任务错误"""
        QMessageBox.critical(self, "分析失败", f"分析过程中出现错误:\n\n{error}")
        # 返回上传页面
        self._content_stack.setCurrentIndex(0)
    
    def _on_task_progress(self, task_id: str, message: str):
        """任务进度"""
        self._loading_page.set_status(f"🔄 {message}")
    
    def _on_open_file(self):
        """打开文件"""
        from PySide6.QtWidgets import QFileDialog
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "打开高数资料",
            "",
            "所有支持的文件 (*.pdf *.png *.jpg *.jpeg *.bmp *.webp *.md *.txt)"
        )
        if filepath:
            self._on_analyze_file(filepath)
    
    def _show_about(self):
        """显示关于对话框"""
        QMessageBox.about(
            self,
            "关于 MathNotebook",
            "MathNotebook v1.0.0\n\n"
            "AI驱动的高数学习助手\n\n"
            "功能：\n"
            "• 智能分析高数资料\n"
            "• 自动识别重要知识点\n"
            "• 分类整理学习内容\n"
            "• 生成复习计划\n\n"
            "© 2026 MathNotebook"
        )

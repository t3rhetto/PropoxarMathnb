"""拖拽上传组件 - 支持PDF、图片、Markdown文件"""

import os
from pathlib import Path
from PySide6.QtCore import Qt, Signal, QMimeData, QSize
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor, QPen, QBrush
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout,
    QListWidget, QListWidgetItem, QFileDialog, QFrame
)


class DropZone(QFrame):
    """拖拽区域组件"""
    
    file_dropped = Signal(str)  # 文件路径信号
    
    SUPPORTED_EXTENSIONS = {'.pdf', '.png', '.jpg', '.jpeg', '.bmp', '.webp', '.md', '.txt'}
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setMinimumHeight(200)
        self._setup_ui()
        self._is_dragging = False
    
    def _setup_ui(self):
        """设置UI"""
        self.setStyleSheet("""
            QFrame {
                border: 2px dashed #c0c0c0;
                border-radius: 16px;
                background: rgba(255, 255, 255, 0.3);
            }
            QFrame:hover {
                border-color: #007AFF;
                background: rgba(0, 122, 255, 0.1);
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        
        # 图标
        self._icon_label = QLabel()
        self._icon_label.setAlignment(Qt.AlignCenter)
        self._icon_label.setStyleSheet("border: none; background: transparent;")
        self._update_icon(False)
        layout.addWidget(self._icon_label)
        
        # 提示文字
        self._text_label = QLabel("拖拽高数资料到这里\n支持 PDF、图片、Markdown")
        self._text_label.setAlignment(Qt.AlignCenter)
        self._text_label.setStyleSheet("""
            QLabel {
                border: none;
                background: transparent;
                color: #666;
                font-size: 14px;
                line-height: 1.5;
            }
        """)
        layout.addWidget(self._text_label)
        
        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignCenter)
        
        self._select_btn = QPushButton("选择文件")
        self._select_btn.setStyleSheet("""
            QPushButton {
                background: #007AFF;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 24px;
                font-size: 14px;
                font-weight: 500;
            }
            QPushButton:hover {
                background: #0056CC;
            }
            QPushButton:pressed {
                background: #004099;
            }
        """)
        self._select_btn.clicked.connect(self._on_select_clicked)
        btn_layout.addWidget(self._select_btn)
        
        layout.addLayout(btn_layout)
    
    def _update_icon(self, is_dragging: bool):
        """更新图标状态"""
        self._is_dragging = is_dragging
        # 使用Unicode符号作为图标
        if is_dragging:
            self._icon_label.setText("📥")
            self._icon_label.setStyleSheet("""
                QLabel {
                    border: none;
                    background: transparent;
                    font-size: 48px;
                }
            """)
        else:
            self._icon_label.setText("📄")
            self._icon_label.setStyleSheet("""
                QLabel {
                    border: none;
                    background: transparent;
                    font-size: 48px;
                }
            """)
    
    def dragEnterEvent(self, event):
        """拖入事件"""
        if event.mimeData().hasUrls():
            # 检查是否有支持的文件类型
            for url in event.mimeData().urls():
                if self._is_supported(url.toLocalFile()):
                    event.acceptProposedAction()
                    self._update_icon(True)
                    self.setStyleSheet("""
                        QFrame {
                            border: 2px dashed #007AFF;
                            border-radius: 16px;
                            background: rgba(0, 122, 255, 0.15);
                        }
                    """)
                    return
        event.ignore()
    
    def dragLeaveEvent(self, event):
        """拖出事件"""
        self._update_icon(False)
        self.setStyleSheet("""
            QFrame {
                border: 2px dashed #c0c0c0;
                border-radius: 16px;
                background: rgba(255, 255, 255, 0.3);
            }
        """)
    
    def dropEvent(self, event):
        """放下事件"""
        self._update_icon(False)
        self.setStyleSheet("""
            QFrame {
                border: 2px dashed #c0c0c0;
                border-radius: 16px;
                background: rgba(255, 255, 255, 0.3);
            }
        """)
        
        for url in event.mimeData().urls():
            filepath = url.toLocalFile()
            if self._is_supported(filepath):
                self.file_dropped.emit(filepath)
    
    def _is_supported(self, filepath: str) -> bool:
        """检查文件是否支持"""
        return Path(filepath).suffix.lower() in self.SUPPORTED_EXTENSIONS
    
    def _on_select_clicked(self):
        """点击选择文件"""
        filepaths, _ = QFileDialog.getOpenFileNames(
            self,
            "选择高数资料",
            "",
            "所有支持的文件 (*.pdf *.png *.jpg *.jpeg *.bmp *.webp *.md *.txt);;PDF文件 (*.pdf);;图片文件 (*.png *.jpg *.jpeg *.bmp *.webp);;Markdown文件 (*.md);;文本文件 (*.txt)"
        )
        for filepath in filepaths:
            self.file_dropped.emit(filepath)


class FileListItem(QFrame):
    """文件列表项"""
    
    remove_clicked = Signal(str)  # 移除信号
    analyze_clicked = Signal(str)  # 分析信号
    
    def __init__(self, filepath: str, parent=None):
        super().__init__(parent)
        self.filepath = filepath
        self._setup_ui()
    
    def _setup_ui(self):
        """设置UI"""
        self.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.5);
                border-radius: 8px;
                padding: 8px;
            }
            QFrame:hover {
                background: rgba(255, 255, 255, 0.7);
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        
        # 文件图标
        icon_label = QLabel(self._get_file_icon())
        icon_label.setStyleSheet("font-size: 24px; border: none; background: transparent;")
        icon_label.setFixedWidth(32)
        layout.addWidget(icon_label)
        
        # 文件信息
        info_layout = QVBoxLayout()
        
        name_label = QLabel(Path(self.filepath).name)
        name_label.setStyleSheet("""
            QLabel {
                border: none;
                background: transparent;
                font-weight: 500;
                color: #333;
            }
        """)
        info_layout.addWidget(name_label)
        
        size = os.path.getsize(self.filepath) if os.path.exists(self.filepath) else 0
        if size > 1024 * 1024:
            size_str = f"{size / (1024*1024):.1f} MB"
        elif size > 1024:
            size_str = f"{size / 1024:.1f} KB"
        else:
            size_str = f"{size} B"
        
        detail_label = QLabel(f"{size_str}  •  {Path(self.filepath).suffix.upper()}")
        detail_label.setStyleSheet("""
            QLabel {
                border: none;
                background: transparent;
                color: #888;
                font-size: 12px;
            }
        """)
        info_layout.addWidget(detail_label)
        
        layout.addLayout(info_layout)
        layout.addStretch()
        
        # 分析按钮
        analyze_btn = QPushButton("分析")
        analyze_btn.setStyleSheet("""
            QPushButton {
                background: #34C759;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 6px 16px;
                font-size: 13px;
                font-weight: 500;
            }
            QPushButton:hover {
                background: #2DB84D;
            }
        """)
        analyze_btn.clicked.connect(lambda: self.analyze_clicked.emit(self.filepath))
        layout.addWidget(analyze_btn)
        
        # 移除按钮
        remove_btn = QPushButton("✕")
        remove_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #999;
                border: none;
                font-size: 16px;
                padding: 4px;
            }
            QPushButton:hover {
                color: #FF3B30;
            }
        """)
        remove_btn.clicked.connect(lambda: self.remove_clicked.emit(self.filepath))
        layout.addWidget(remove_btn)
    
    def _get_file_icon(self) -> str:
        """根据文件类型返回图标"""
        ext = Path(self.filepath).suffix.lower()
        if ext == '.pdf':
            return "📕"
        elif ext in ('.png', '.jpg', '.jpeg', '.bmp', '.webp'):
            return "🖼️"
        elif ext in ('.md', '.txt'):
            return "📝"
        return "📄"


class UploadWidget(QWidget):
    """完整的上传组件：拖拽区域 + 文件列表"""
    
    file_added = Signal(str)  # 文件添加信号
    file_removed = Signal(str)  # 文件移除信号
    analyze_requested = Signal(str)  # 请求分析信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._files = []
        self._setup_ui()
    
    def _setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # 标题
        title = QLabel("📚 上传高数资料")
        title.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: 600;
                color: #1a1a1a;
                border: none;
                background: transparent;
            }
        """)
        layout.addWidget(title)
        
        # 拖拽区域
        self._drop_zone = DropZone()
        self._drop_zone.file_dropped.connect(self._on_file_dropped)
        layout.addWidget(self._drop_zone)
        
        # 文件列表标题
        self._list_title = QLabel("已添加的文件")
        self._list_title.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: 500;
                color: #666;
                border: none;
                background: transparent;
            }
        """)
        self._list_title.hide()
        layout.addWidget(self._list_title)
        
        # 文件列表
        self._file_list = QVBoxLayout()
        self._file_list.setSpacing(8)
        layout.addLayout(self._file_list)
        
        layout.addStretch()
    
    def _on_file_dropped(self, filepath: str):
        """文件被拖入或选择"""
        if filepath not in self._files:
            self._files.append(filepath)
            self._add_file_item(filepath)
            self.file_added.emit(filepath)
    
    def _add_file_item(self, filepath: str):
        """添加文件项到列表"""
        self._list_title.show()
        
        item = FileListItem(filepath)
        item.remove_clicked.connect(self._on_remove_file)
        item.analyze_clicked.connect(self._on_analyze_file)
        self._file_list.addWidget(item)
    
    def _on_remove_file(self, filepath: str):
        """移除文件"""
        if filepath in self._files:
            self._files.remove(filepath)
            self.file_removed.emit(filepath)
            
            # 重新构建列表
            self._rebuild_file_list()
    
    def _on_analyze_file(self, filepath: str):
        """请求分析文件"""
        self.analyze_requested.emit(filepath)
    
    def _rebuild_file_list(self):
        """重建文件列表"""
        # 清空现有列表
        while self._file_list.count():
            item = self._file_list.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # 重新添加
        for filepath in self._files:
            self._add_file_item(filepath)
        
        if not self._files:
            self._list_title.hide()
    
    def get_files(self) -> list:
        """获取所有文件路径"""
        return self._files.copy()

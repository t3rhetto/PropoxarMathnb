"""分析结果展示组件 - 显示AI分析的重要性/记忆方式分类"""

from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QFont, QColor
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QGridLayout, QProgressBar, QSizePolicy
)


class ImportanceBadge(QLabel):
    """重要性标签"""
    
    STYLES = {
        "必背": "background: #FF3B30; color: white;",
        "理解": "background: #FF9500; color: white;",
        "了解": "background: #34C759; color: white;",
        "重点": "background: #AF52DE; color: white;",
    }
    
    def __init__(self, level: str, parent=None):
        super().__init__(level, parent)
        self.setStyleSheet(f"""
            QLabel {{
                {self.STYLES.get(level, self.STYLES['了解'])}
                border: none;
                border-radius: 4px;
                padding: 2px 8px;
                font-size: 12px;
                font-weight: 600;
            }}
        """)
        self.setAlignment(Qt.AlignCenter)
        self.setFixedHeight(22)


class MemoryTypeBadge(QLabel):
    """记忆方式标签"""
    
    def __init__(self, mem_type: str, parent=None):
        super().__init__(mem_type, parent)
        if "背" in mem_type:
            style = "background: #5856D6; color: white;"
        else:
            style = "background: #007AFF; color: white;"
        
        self.setStyleSheet(f"""
            QLabel {{
                {style}
                border: none;
                border-radius: 4px;
                padding: 2px 8px;
                font-size: 12px;
                font-weight: 600;
            }}
        """)
        self.setAlignment(Qt.AlignCenter)
        self.setFixedHeight(22)


class ConceptCard(QFrame):
    """知识点卡片"""
    
    detail_clicked = Signal(dict)  # 点击详情信号
    
    def __init__(self, concept_data: dict, parent=None):
        super().__init__(parent)
        self.data = concept_data
        self._setup_ui()
    
    def _setup_ui(self):
        """设置UI"""
        self.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.7);
                border-radius: 12px;
                padding: 16px;
            }
            QFrame:hover {
                background: rgba(255, 255, 255, 0.9);
            }
        """)
        self.setCursor(Qt.PointingHandCursor)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        
        # 标题行
        title_layout = QHBoxLayout()
        
        name = self.data.get("name", "未知知识点")
        title = QLabel(f"📖 {name}")
        title.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: 600;
                color: #1a1a1a;
                border: none;
                background: transparent;
            }
        """)
        title_layout.addWidget(title)
        title_layout.addStretch()
        
        # 难度星级
        difficulty = self.data.get("difficulty", 3)
        stars = "⭐" * difficulty
        stars_label = QLabel(stars)
        stars_label.setStyleSheet("""
            QLabel {
                border: none;
                background: transparent;
                font-size: 14px;
            }
        """)
        title_layout.addWidget(stars_label)
        
        layout.addLayout(title_layout)
        
        # 标签行
        tags_layout = QHBoxLayout()
        
        # 重要性标签
        importance = self.data.get("importance", "理解")
        importance_badge = ImportanceBadge(importance)
        tags_layout.addWidget(importance_badge)
        
        # 记忆方式标签
        memory_type = self.data.get("memory_type", "做题理解")
        memory_badge = MemoryTypeBadge(memory_type)
        tags_layout.addWidget(memory_badge)
        
        tags_layout.addStretch()
        
        layout.addLayout(tags_layout)
        
        # 解释摘要
        explanation = self.data.get("explanation", "")
        if explanation:
            summary = QLabel(explanation[:100] + ("..." if len(explanation) > 100 else ""))
            summary.setWordWrap(True)
            summary.setStyleSheet("""
                QLabel {
                    color: #666;
                    font-size: 13px;
                    border: none;
                }
            """)
            layout.addWidget(summary)
        
        # 公式预览
        formulas = self.data.get("formulas", [])
        if formulas:
            formula_text = "  ".join(formulas[:2])
            formula_label = QLabel(f"📐 {formula_text}")
            formula_label.setStyleSheet("""
                QLabel {
                    color: #5856D6;
                    font-size: 12px;
                    font-family: 'Menlo', monospace;
                    border: none;
                    background: rgba(88, 86, 214, 0.1);
                    border-radius: 4px;
                    padding: 4px 8px;
                }
            """)
            layout.addWidget(formula_label)
        
        # 底部信息
        footer_layout = QHBoxLayout()
        
        # 关联概念
        related = self.data.get("related_concepts", [])
        if related:
            related_text = ", ".join(related[:3])
            related_label = QLabel(f"🔗 {related_text}")
            related_label.setStyleSheet("""
                QLabel {
                    color: #888;
                    font-size: 12px;
                    border: none;
                }
            """)
            footer_layout.addWidget(related_label)
        
        footer_layout.addStretch()
        
        # 详情按钮
        detail_btn = QPushButton("查看详情")
        detail_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #007AFF;
                border: none;
                font-size: 13px;
                font-weight: 500;
            }
            QPushButton:hover {
                color: #0056CC;
            }
        """)
        detail_btn.clicked.connect(lambda: self.detail_clicked.emit(self.data))
        footer_layout.addWidget(detail_btn)
        
        layout.addLayout(footer_layout)


class AnalysisResultPage(QWidget):
    """分析结果页面"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._concepts = []
        self._setup_ui()
    
    def _setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # 标题
        title_layout = QHBoxLayout()
        
        self._title = QLabel("📊 分析结果")
        self._title.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: 600;
                color: #1a1a1a;
                border: none;
                background: transparent;
            }
        """)
        title_layout.addWidget(self._title)
        title_layout.addStretch()
        
        # 统计标签
        self._stats_label = QLabel()
        self._stats_label.setStyleSheet("""
            QLabel {
                color: #666;
                font-size: 13px;
                border: none;
            }
        """)
        title_layout.addWidget(self._stats_label)
        
        layout.addLayout(title_layout)
        
        # 筛选按钮行
        filter_layout = QHBoxLayout()
        
        self._filter_all = self._create_filter_button("全部", True)
        self._filter_memorize = self._create_filter_button("🔴 必背", False)
        self._filter_understand = self._create_filter_button("🟡 理解", False)
        self._filter_know = self._create_filter_button("🟢 了解", False)
        
        filter_layout.addWidget(self._filter_all)
        filter_layout.addWidget(self._filter_memorize)
        filter_layout.addWidget(self._filter_understand)
        filter_layout.addWidget(self._filter_know)
        filter_layout.addStretch()
        
        layout.addLayout(filter_layout)
        
        # 滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                background: transparent;
                width: 8px;
            }
            QScrollBar::handle:vertical {
                background: rgba(0, 0, 0, 0.2);
                border-radius: 4px;
            }
        """)
        
        # 卡片容器
        self._cards_widget = QWidget()
        self._cards_widget.setStyleSheet("background: transparent;")
        self._cards_layout = QVBoxLayout(self._cards_widget)
        self._cards_layout.setSpacing(12)
        
        scroll.setWidget(self._cards_widget)
        layout.addWidget(scroll)
    
    def _create_filter_button(self, text: str, is_active: bool) -> QPushButton:
        """创建筛选按钮"""
        btn = QPushButton(text)
        btn.setCheckable(True)
        btn.setChecked(is_active)
        btn.setStyleSheet("""
            QPushButton {
                background: rgba(0, 0, 0, 0.05);
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 13px;
                color: #666;
            }
            QPushButton:checked {
                background: #007AFF;
                color: white;
            }
            QPushButton:hover {
                background: rgba(0, 0, 0, 0.1);
            }
            QPushButton:checked:hover {
                background: #0056CC;
            }
        """)
        btn.clicked.connect(lambda: self._on_filter_clicked(btn))
        return btn
    
    def _on_filter_clicked(self, clicked_btn: QPushButton):
        """筛选按钮点击"""
        # 取消其他按钮的选中状态
        for btn in [self._filter_all, self._filter_memorize, 
                    self._filter_understand, self._filter_know]:
            btn.setChecked(btn == clicked_btn)
        
        # 更新显示
        self._update_card_visibility()
    
    def _update_card_visibility(self):
        """根据筛选更新卡片可见性"""
        filter_map = {
            self._filter_all: None,
            self._filter_memorize: "必背",
            self._filter_understand: "理解",
            self._filter_know: "了解",
        }
        
        active_filter = None
        for btn, importance in filter_map.items():
            if btn.isChecked():
                active_filter = importance
                break
        
        for i in range(self._cards_layout.count()):
            item = self._cards_layout.itemAt(i)
            if item and item.widget():
                card = item.widget()
                if hasattr(card, 'data'):
                    if active_filter is None or card.data.get('importance') == active_filter:
                        card.show()
                    else:
                        card.hide()
    
    def set_analysis_result(self, analysis: dict):
        """设置分析结果"""
        self._concepts = analysis.get("concepts", [])
        
        # 清空现有卡片
        while self._cards_layout.count():
            item = self._cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # 添加新卡片
        for concept in self._concepts:
            card = ConceptCard(concept)
            card.detail_clicked.connect(self._on_concept_detail)
            self._cards_layout.addWidget(card)
        
        self._cards_layout.addStretch()
        
        # 更新统计
        total = len(self._concepts)
        memorize = sum(1 for c in self._concepts if c.get("importance") == "必背")
        understand = sum(1 for c in self._concepts if c.get("importance") == "理解")
        know = sum(1 for c in self._concepts if c.get("importance") == "了解")
        
        self._stats_label.setText(f"共 {total} 个知识点  •  必背 {memorize}  理解 {understand}  了解 {know}")
    
    def _on_concept_detail(self, concept: dict):
        """点击知识点详情"""
        # TODO: 实现详情对话框或导航
        print(f"查看详情: {concept.get('name')}")


class AnalysisLoadingWidget(QWidget):
    """分析加载中状态"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        
        # 加载动画（使用文本模拟）
        self._status_label = QLabel("🔄 正在分析中...")
        self._status_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: 500;
                color: #1a1a1a;
                border: none;
                background: transparent;
            }
        """)
        self._status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self._status_label)
        
        # 进度条
        self._progress = QProgressBar()
        self._progress.setRange(0, 0)  # 不确定进度模式
        self._progress.setFixedWidth(300)
        self._progress.setStyleSheet("""
            QProgressBar {
                border: none;
                background: rgba(0, 0, 0, 0.1);
                border-radius: 4px;
                height: 8px;
            }
            QProgressBar::chunk {
                background: #007AFF;
                border-radius: 4px;
            }
        """)
        layout.addWidget(self._progress, alignment=Qt.AlignCenter)
        
        # 提示文字
        hint = QLabel("AI正在识别知识点并分析重要性...")
        hint.setStyleSheet("""
            QLabel {
                color: #888;
                font-size: 13px;
                border: none;
                background: transparent;
            }
        """)
        hint.setAlignment(Qt.AlignCenter)
        layout.addWidget(hint)
    
    def set_status(self, text: str):
        """设置状态文字"""
        self._status_label.setText(text)

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from browser.theme_manager import ThemeManager


class SettingsWindow(QDialog):
    """Cửa sổ cài đặt với theme selector"""
    
    def __init__(self, theme_manager: ThemeManager, parent=None):
        super().__init__(parent)
        self.theme_manager = theme_manager
        self.setWindowTitle("Cài đặt")
        self.setMinimumSize(500, 400)
        self.setModal(True)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Tiêu đề
        title_label = QLabel("Cài đặt")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(title_label)
        
        # Phân cách
        layout.addWidget(QLabel(""))  # Khoảng cách
        
        # Section Theme
        theme_label = QLabel("Giao diện")
        theme_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(theme_label)
        
        # Theme selector
        theme_layout = QHBoxLayout()
        theme_layout.addWidget(QLabel("Theme:"))
        
        self.theme_combo = QComboBox()
        theme_names = self.theme_manager.get_theme_display_names()
        for key, display_name in theme_names.items():
            self.theme_combo.addItem(display_name, key)
        
        # Set theme hiện tại
        current_index = self.theme_combo.findData(self.theme_manager.current_theme)
        if current_index >= 0:
            self.theme_combo.setCurrentIndex(current_index)
        
        self.theme_combo.currentIndexChanged.connect(self.on_theme_changed)
        theme_layout.addWidget(self.theme_combo)
        theme_layout.addStretch()
        
        layout.addLayout(theme_layout)
        
        # Preview area
        preview_label = QLabel("Xem trước:")
        preview_label.setStyleSheet("font-size: 12px;")
        layout.addWidget(preview_label)
        
        self.preview_widget = QWidget()
        self.preview_widget.setFixedHeight(150)
        preview_layout = QVBoxLayout(self.preview_widget)
        preview_layout.setContentsMargins(10, 10, 10, 10)
        
        # Preview buttons
        preview_btn_layout = QHBoxLayout()
        self.preview_btn1 = QPushButton("Nút 1")
        self.preview_btn2 = QPushButton("Nút 2")
        preview_btn_layout.addWidget(self.preview_btn1)
        preview_btn_layout.addWidget(self.preview_btn2)
        preview_btn_layout.addStretch()
        preview_layout.addLayout(preview_btn_layout)
        
        # Preview input
        self.preview_input = QLineEdit()
        self.preview_input.setPlaceholderText("Thanh địa chỉ...")
        preview_layout.addWidget(self.preview_input)
        
        # Preview tab
        self.preview_tab = QTabBar()
        self.preview_tab.addTab("Tab 1")
        self.preview_tab.addTab("Tab 2")
        self.preview_tab.setCurrentIndex(0)
        preview_layout.addWidget(self.preview_tab)
        
        layout.addWidget(self.preview_widget)

        # Web content options
        layout.addWidget(QLabel(""))  # Khoảng cách
        web_section_label = QLabel("Web content")
        web_section_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(web_section_label)

        self.force_dark_checkbox = QCheckBox("Force dark mode for web pages")
        self.force_dark_checkbox.setChecked(self.theme_manager.force_web_dark_mode)
        self.force_dark_checkbox.stateChanged.connect(self.on_force_web_dark_mode_toggled)
        layout.addWidget(self.force_dark_checkbox)
        
        layout.addStretch()
        
        # Nút đóng
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        btn_close = QPushButton("Đóng")
        btn_close.clicked.connect(self.accept)
        button_layout.addWidget(btn_close)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Áp dụng theme hiện tại
        self.apply_theme_preview()
    
    def on_theme_changed(self, index):
        """Xử lý khi theme thay đổi"""
        theme_key = self.theme_combo.itemData(index)
        if theme_key:
            self.theme_manager.set_theme(theme_key)
            self.apply_theme_preview()
    
    def apply_theme_preview(self):
        """Áp dụng theme cho preview area"""
        theme = self.theme_manager.get_theme()
        
        # Cập nhật border của preview widget dựa trên theme
        border_color = theme["address_bar_border"]
        self.preview_widget.setStyleSheet(
            f"border: 1px solid {border_color}; border-radius: 5px;"
        )
        
        # Áp dụng stylesheet cho các widget preview
        stylesheet = self.theme_manager.get_stylesheet()
        self.preview_btn1.setStyleSheet(stylesheet)
        self.preview_btn2.setStyleSheet(stylesheet)
        self.preview_input.setStyleSheet(stylesheet)
        self.preview_tab.setStyleSheet(stylesheet)

    def on_force_web_dark_mode_toggled(self, state):
        """Bật/tắt dark mode cho nội dung web"""
        enabled = state == Qt.Checked
        self.theme_manager.set_force_web_dark_mode(enabled)


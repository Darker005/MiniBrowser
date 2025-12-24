import json
import os
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtGui import QPalette, QColor


class ThemeManager(QObject):
    """Quản lý themes cho trình duyệt"""
    theme_changed = pyqtSignal(str)  # Signal khi theme thay đổi
    force_web_dark_mode_changed = pyqtSignal(bool)  # Signal khi bật/tắt dark mode web
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings_file = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            "data", 
            "settings.json"
        )
        
        # Đảm bảo thư mục data tồn tại
        os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
        
        # Định nghĩa các themes
        self.themes = {
            "light": {
                "name": "Sáng",
                "window_bg": "#FFFFFF",
                "window_fg": "#000000",
                "button_bg": "#F0F0F0",
                "button_fg": "#000000",
                "button_hover": "#E0E0E0",
                "address_bar_bg": "#FFFFFF",
                "address_bar_fg": "#000000",
                "address_bar_border": "#CCCCCC",
                "tab_bg": "#F5F5F5",
                "tab_fg": "#000000",
                "tab_selected_bg": "#FFFFFF",
                "tab_selected_fg": "#000000",
                "tab_hover_bg": "#E8E8E8",
            },
            "dark": {
                "name": "Tối",
                "window_bg": "#1E1E1E",
                "window_fg": "#FFFFFF",
                "button_bg": "#2D2D2D",
                "button_fg": "#FFFFFF",
                "button_hover": "#3D3D3D",
                "address_bar_bg": "#2D2D2D",
                "address_bar_fg": "#FFFFFF",
                "address_bar_border": "#404040",
                "tab_bg": "#252525",
                "tab_fg": "#FFFFFF",
                "tab_selected_bg": "#1E1E1E",
                "tab_selected_fg": "#FFFFFF",
                "tab_hover_bg": "#353535",
            },
            "blue": {
                "name": "Xanh dương",
                "window_bg": "#E3F2FD",
                "window_fg": "#000000",
                "button_bg": "#2196F3",
                "button_fg": "#FFFFFF",
                "button_hover": "#1976D2",
                "address_bar_bg": "#FFFFFF",
                "address_bar_fg": "#000000",
                "address_bar_border": "#90CAF9",
                "tab_bg": "#BBDEFB",
                "tab_fg": "#000000",
                "tab_selected_bg": "#2196F3",
                "tab_selected_fg": "#FFFFFF",
                "tab_hover_bg": "#90CAF9",
            },
            "green": {
                "name": "Xanh lá",
                "window_bg": "#E8F5E9",
                "window_fg": "#000000",
                "button_bg": "#4CAF50",
                "button_fg": "#FFFFFF",
                "button_hover": "#388E3C",
                "address_bar_bg": "#FFFFFF",
                "address_bar_fg": "#000000",
                "address_bar_border": "#A5D6A7",
                "tab_bg": "#C8E6C9",
                "tab_fg": "#000000",
                "tab_selected_bg": "#4CAF50",
                "tab_selected_fg": "#FFFFFF",
                "tab_hover_bg": "#A5D6A7",
            },
            "purple": {
                "name": "Tím",
                "window_bg": "#F3E5F5",
                "window_fg": "#000000",
                "button_bg": "#9C27B0",
                "button_fg": "#FFFFFF",
                "button_hover": "#7B1FA2",
                "address_bar_bg": "#FFFFFF",
                "address_bar_fg": "#000000",
                "address_bar_border": "#CE93D8",
                "tab_bg": "#E1BEE7",
                "tab_fg": "#000000",
                "tab_selected_bg": "#9C27B0",
                "tab_selected_fg": "#FFFFFF",
                "tab_hover_bg": "#CE93D8",
            }
        }
        
        # Load theme đã lưu hoặc mặc định là "light"
        self.current_theme = self.load_theme()
        # Bật/tắt dark mode cho nội dung web
        self.force_web_dark_mode = self.load_force_web_dark_mode()
    
    def load_theme(self):
        """Load theme đã lưu từ file"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    theme = settings.get("theme", "light")
                    if theme in self.themes:
                        return theme
        except Exception as e:
            print(f"Lỗi khi load theme: {e}")
        return "light"
    
    def save_theme(self, theme_name):
        """Lưu theme vào file"""
        try:
            settings = {}
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
            
            settings["theme"] = theme_name
            
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Lỗi khi lưu theme: {e}")
    
    def set_theme(self, theme_name):
        """Thiết lập theme mới"""
        if theme_name not in self.themes:
            return False
        
        self.current_theme = theme_name
        self.save_theme(theme_name)
        self.theme_changed.emit(theme_name)
        return True

    def set_force_web_dark_mode(self, enabled: bool):
        """Bật/tắt chế độ dark cho nội dung web"""
        enabled = bool(enabled)
        self.force_web_dark_mode = enabled
        self.save_force_web_dark_mode(enabled)
        self.force_web_dark_mode_changed.emit(enabled)
        return True
    
    def get_theme(self, theme_name=None):
        """Lấy thông tin theme"""
        if theme_name is None:
            theme_name = self.current_theme
        return self.themes.get(theme_name, self.themes["light"])
    
    def get_theme_names(self):
        """Lấy danh sách tên themes"""
        return list(self.themes.keys())
    
    def get_theme_display_names(self):
        """Lấy danh sách tên hiển thị của themes"""
        return {key: theme["name"] for key, theme in self.themes.items()}

    def load_force_web_dark_mode(self) -> bool:
        """Đọc trạng thái dark mode cho trang web"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    return bool(settings.get("web_dark_mode", False))
        except Exception as e:
            print(f"Lỗi khi load web dark mode: {e}")
        return False

    def save_force_web_dark_mode(self, enabled: bool):
        """Lưu trạng thái dark mode cho trang web"""
        try:
            settings = {}
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
            
            settings["web_dark_mode"] = bool(enabled)
            
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Lỗi khi lưu web dark mode: {e}")
    
    def get_stylesheet(self, theme_name=None):
        """Tạo stylesheet cho theme"""
        theme = self.get_theme(theme_name)
        
        stylesheet = f"""
        QMainWindow {{
            background-color: {theme["window_bg"]};
            color: {theme["window_fg"]};
        }}
        
        QWidget {{
            background-color: {theme["window_bg"]};
            color: {theme["window_fg"]};
        }}
        
        QPushButton {{
            background-color: {theme["button_bg"]};
            color: {theme["button_fg"]};
            border: 1px solid {theme["button_bg"]};
            border-radius: 4px;
            padding: 5px 10px;
            min-height: 20px;
        }}
        
        QPushButton:hover {{
            background-color: {theme["button_hover"]};
        }}
        
        QPushButton:pressed {{
            background-color: {theme["button_hover"]};
        }}
        
        QLineEdit {{
            background-color: {theme["address_bar_bg"]};
            color: {theme["address_bar_fg"]};
            border: 1px solid {theme["address_bar_border"]};
            border-radius: 4px;
            padding: 5px;
        }}
        
        QLineEdit:focus {{
            border: 2px solid {theme["button_bg"]};
        }}
        
        QTabBar::tab {{
            background-color: {theme["tab_bg"]};
            color: {theme["tab_fg"]};
            border: 1px solid {theme["address_bar_border"]};
            border-bottom: none;
            padding: 8px 16px;
            margin-right: 2px;
        }}
        
        QTabBar::tab:selected {{
            background-color: {theme["tab_selected_bg"]};
            color: {theme["tab_selected_fg"]};
            border-bottom: 2px solid {theme["button_bg"]};
        }}
        
        QTabBar::tab:hover {{
            background-color: {theme["tab_hover_bg"]};
        }}
        
        QMenu {{
            background-color: {theme["window_bg"]};
            color: {theme["window_fg"]};
            border: 1px solid {theme["address_bar_border"]};
        }}
        
        QMenu::item {{
            padding: 5px 20px;
        }}
        
        QMenu::item:selected {{
            background-color: {theme["button_hover"]};
        }}
        
        QDialog {{
            background-color: {theme["window_bg"]};
            color: {theme["window_fg"]};
        }}
        
        QLabel {{
            background-color: transparent;
            color: {theme["window_fg"]};
        }}
        
        QScrollArea {{
            background-color: {theme["window_bg"]};
            border: none;
        }}
        
        QListWidget {{
            background-color: {theme["window_bg"]};
            color: {theme["window_fg"]};
            border: 1px solid {theme["address_bar_border"]};
        }}
        
        QListWidget::item {{
            padding: 5px;
        }}
        
        QListWidget::item:selected {{
            background-color: {theme["button_hover"]};
        }}
        
        QListWidget::item:hover {{
            background-color: {theme["tab_hover_bg"]};
        }}
        
        QTableWidget {{
            background-color: {theme["window_bg"]};
            color: {theme["window_fg"]};
            border: 1px solid {theme["address_bar_border"]};
            gridline-color: {theme["address_bar_border"]};
        }}
        
        QTableWidget::item {{
            padding: 5px;
        }}
        
        QTableWidget::item:selected {{
            background-color: {theme["button_hover"]};
            color: {theme["window_fg"]};
        }}
        
        QTableWidget::item:hover {{
            background-color: {theme["tab_hover_bg"]};
        }}
        
        QHeaderView::section {{
            background-color: {theme["button_bg"]};
            color: {theme["button_fg"]};
            padding: 5px;
            border: 1px solid {theme["address_bar_border"]};
        }}
        
        QHeaderView::section:hover {{
            background-color: {theme["button_hover"]};
        }}
        """
        
        return stylesheet


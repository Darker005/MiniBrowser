import sys
import os
# sys.path.append(r"E:\WorkSpace\MiniBrowser")
from browser.controller import *
from browser.tab_manager import *
from browser.history_manager import *
from browser.history_window import *
from browser.bookmark_manager import *
from browser.bookmark_window import *
from browser.downloader import *
from browser.search_suggestion import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


# ===================== ASSET PATH HELPER =====================
def asset_path(relative_path: str) -> str:
    """
    Trả về đường dẫn tuyệt đối tới thư mục assets
    Hoạt động đúng dù chạy ở đâu
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))   # /browser
    project_root = os.path.dirname(base_dir)                # /MiniBrowser
    return os.path.join(project_root, "assets", relative_path)
# =============================================================



class MiniBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mini Browser")
        self.setWindowIcon(QIcon(asset_path("icons/browser.png")))
        self.resize(1200, 800)


         # tạo thanh tab
        self.tab_bar = QTabBar(movable=True, tabsClosable=True)

        # thêm nút + để mở tab mới
        self.btn_new_tab = QPushButton("+")
        self.btn_new_tab.setFixedWidth(30)
        

        # layout chứa tab
        layout_tabs = QHBoxLayout()
        layout_tabs.addWidget(self.tab_bar)
        layout_tabs.addWidget(self.btn_new_tab)

        # Thanh công cụ
        self.address_bar = QLineEdit()
        self.address_bar.setPlaceholderText("Enter URL")

        # các nút bấm
        btn_back = QPushButton("Back")
        btn_next = QPushButton("Next")
        btn_reload = QPushButton("Reload")

        # ⭐ Add Bookmark button
        self.btn_bookmark = QPushButton("✩")  # ban đầu rỗng
        self.btn_bookmark.setStyleSheet("font-size: 20px; border: none; background: none; color: gray;")
        self.btn_bookmark.setCursor(Qt.PointingHandCursor)


        # ⋮ Menu button
        btn_menu = QPushButton("⋮")
        btn_menu.setFixedWidth(35)

        # layout top
        layout_top = QHBoxLayout()
        layout_top.addWidget(btn_back)
        layout_top.addWidget(btn_next)
        layout_top.addWidget(btn_reload)
        layout_top.addWidget(self.address_bar)
        layout_top.addWidget(self.btn_bookmark)
        layout_top.addWidget(btn_menu)


        # stack chứa nhiều browser
        self.web_container = QStackedWidget()

        # layout chính
        layout_main = QVBoxLayout()
        layout_main.addLayout(layout_tabs)
        layout_main.addLayout(layout_top)
        layout_main.addWidget(self.web_container)

        # central widget
        central_widget = QWidget()
        central_widget.setLayout(layout_main)
        self.setCentralWidget(central_widget)

        # tạo controller, TabManager, HistoryManager
        dummy_browser = QWebEngineView()
        self.controller = BrowserController(
            dummy_browser, 
            self.address_bar, 
            btn_back=btn_back, 
            btn_next=btn_next
        )

        self.history_manager = HistoryManager()
        self.bookmark_manager = BookmarkManager()
        self.search_suggestion_manager = SearchSuggestionManager(
            self.address_bar,
            self.history_manager,
            self.bookmark_manager
        )

        
        # Tạo DownloadManager và profile chung cho tất cả browser
        self.download_manager = DownloadManager(self)
        self.web_profile = QWebEngineProfile.defaultProfile()
        self.download_manager.setup_profile(self.web_profile)

        self.tab_manager = TabManager(
            self.tab_bar,
            self.web_container,
            self.address_bar,
            self.controller,
            self,
            self.history_manager,
            self.web_profile
        )



        # menu pop_up
        self.menu_popup = QMenu()

        action_new_tab = QAction("New Tab", self)
        action_new_window = QAction("New Window", self)
        action_history = QAction("History", self)
        action_bookmarks = QAction("Bookmarks", self)
        action_downloads = QAction("Downloads", self)
        action_settings = QAction("Settings", self)

        self.menu_popup.addAction(action_new_tab)
        self.menu_popup.addAction(action_new_window)
        self.menu_popup.addSeparator()
        self.menu_popup.addAction(action_history)
        self.menu_popup.addAction(action_bookmarks)
        self.menu_popup.addAction(action_downloads)
        self.menu_popup.addSeparator()
        self.menu_popup.addAction(action_settings)



        # kết nối sự kiện
        # xử lý các nút
        btn_back.clicked.connect(self.controller.go_back)
        btn_next.clicked.connect(self.controller.go_forward)
        btn_reload.clicked.connect(self.controller.reload_page)
        self.btn_new_tab.clicked.connect(lambda: self.tab_manager.add_new_tab())

        # xử lý khi chuyên sang trang mới hay url thay đổi 
        self.address_bar.returnPressed.connect(self.controller.navigate_to_url)


        # Bookmark click 
        self.btn_bookmark.clicked.connect(self.add_or_toggle_bookmark)

        # Menu click → popup
        btn_menu.clicked.connect(
            lambda: self.menu_popup.exec_(btn_menu.mapToGlobal(QPoint(0, btn_menu.height())))
        )

        # Menu actions
        action_new_tab.triggered.connect(lambda: self.tab_manager.add_new_tab())
        action_new_window.triggered.connect(lambda: print("New Window clicked!"))
        action_history.triggered.connect(self.open_history_window)
        action_bookmarks.triggered.connect(self.open_bookmark_window)
        action_downloads.triggered.connect(self.open_downloads_window)
        action_settings.triggered.connect(lambda: print("Settings clicked!"))

        #  tab đầu tiên
        self.tab_manager.add_new_tab(QUrl("https://www.google.com"))
        # Khi tab mới được chọn hoặc URL thay đổi, update nút bookmark
        self.tab_manager.tab_changed.connect(self.update_bookmark_button)

    #  hàm để mở ra cái history_window
    def open_history_window(self):
        self.history_window = HistoryWindow(self.history_manager)
        # truyền main_window để HistoryWindow có thể mở tab
        self.history_window.main_window = self
        self.history_window.show()
    
    #  hàm để mở ra cái bookmark_window
    def open_bookmark_window(self):
        if not hasattr(self, "bookmark_window"):
            self.bookmark_window = BookmarkWindow(self.bookmark_manager)
            self.bookmark_window.main_window = self  # để mở URL từ bookmark

        self.bookmark_window.load_bookmarks()
        self.bookmark_window.show()
    
    #  hàm để mở ra cái download_window
    def open_downloads_window(self):
        self.download_manager.show_downloads(self)
    
    # hàm thêm cái trang mà mình bấm vào để lưu bookmark
    def add_current_page_to_bookmarks(self):
        current_view = self.web_container.currentWidget()
        if not current_view:
            return

        url = current_view.url().toString()
        title = current_view.title() or url

        # Thêm vào database
        self.bookmark_manager.add_bookmark(title, url)

        QMessageBox.information(self, "Bookmark Added", f"Saved:\n{title}")
    
    # ---------- Bookmark functions ----------
    def add_or_toggle_bookmark(self):
        """Thêm trang hiện tại vào bookmark (nếu chưa) hoặc bỏ qua nếu đã có"""
        current_view = self.web_container.currentWidget()
        if not current_view:
            return

        url = current_view.url().toString()
        title = current_view.title() or url

        # Thêm vào database nếu chưa có
        if not self.bookmark_manager.get_by_url(url):
            self.bookmark_manager.add_bookmark(title, url)
            QMessageBox.information(self, "Bookmark Added", f"Saved:\n{title}")

        # Cập nhật nút màu
        self.update_bookmark_button()

    def update_bookmark_button(self):
        """Cập nhật trạng thái nút bookmark dựa trên URL hiện tại"""
        current_view = self.web_container.currentWidget()
        if not current_view:
            return

        url = current_view.url().toString()
        exists = self.bookmark_manager.get_by_url(url)

        if exists:
            self.btn_bookmark.setText("★")
            self.btn_bookmark.setStyleSheet("color: gold; font-size: 20px; border: none; background: none;")
        else:
            self.btn_bookmark.setText("✩")
            self.btn_bookmark.setStyleSheet("color: gray; font-size: 20px; border: none; background: none;")






    

# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     window = MiniBrowser()
#     window.show()
#     sys.exit(app.exec_())


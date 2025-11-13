import sys
# sys.path.append(r"E:\WorkSpace\MiniBrowser")
from browser.controller import *
from browser.tab_manager import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *



class MiniBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mini Browser")
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

        # layout top
        layout_top = QHBoxLayout()
        layout_top.addWidget(btn_back)
        layout_top.addWidget(btn_next)
        layout_top.addWidget(btn_reload)
        layout_top.addWidget(self.address_bar)

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

        # tạo controller và TabManager
        dummy_browser = QWebEngineView()
        self.controller = BrowserController(
            dummy_browser, 
            self.address_bar, 
            btn_back=btn_back, 
            btn_next=btn_next
        )
        self.tab_manager = TabManager(
            self.tab_bar,
            self.web_container,
            self.address_bar,
            self.controller,
            self
        )

        # kết nối sự kiện
        # xử lý các nút
        btn_back.clicked.connect(self.controller.go_back)
        btn_next.clicked.connect(self.controller.go_forward)
        btn_reload.clicked.connect(self.controller.reload_page)
        self.btn_new_tab.clicked.connect(lambda: self.tab_manager.add_new_tab())

        # xử lý khi chuyên sang trang mới hay url thay đổi 
        self.address_bar.returnPressed.connect(self.controller.navigate_to_url)

        #  tab đầu tiên
        self.tab_manager.add_new_tab(QUrl("https://www.google.com"))

# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     window = MiniBrowser()
#     window.show()
#     sys.exit(app.exec_())


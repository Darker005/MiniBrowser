import sys
# sys.path.append(r"E:\WorkSpace\MiniBrowser")
from browser.controller import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtCore import *




class MiniBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mini Browser")
        self.resize(1200, 800)


        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl("https://www.google.com"))

        # Thanh công cụ
        self.address_bar = QLineEdit()
        self.address_bar.setPlaceholderText("Enter URL")

        btn_back = QPushButton("Back")
        btn_next = QPushButton("Next")
        btn_reload = QPushButton("Reload")

        # layout top
        layout_top = QHBoxLayout()
        layout_top.addWidget(btn_back)
        layout_top.addWidget(btn_next)
        layout_top.addWidget(btn_reload)
        layout_top.addWidget(self.address_bar)

        # layout chính
        layout_main = QVBoxLayout()
        layout_main.addLayout(layout_top)
        layout_main.addWidget(self.browser)

        # central widget
        central_widget = QWidget()
        central_widget.setLayout(layout_main)
        self.setCentralWidget(central_widget)

        # tạo controller
        self.controller = BrowserController(
            self.browser, 
            self.address_bar, 
            btn_back=btn_back, 
            btn_next=btn_next
        )

        


        # kết nối sự kiện
        # xử lý các nút
        btn_back.clicked.connect(self.controller.go_back)
        btn_next.clicked.connect(self.controller.go_forward)
        btn_reload.clicked.connect(self.controller.reload_page)

        # xử lý khi chuyên sang trang mới hay url thay đổi 
        self.browser.urlChanged.connect(self.controller.update_url_bar)
        self.browser.loadFinished.connect(self.controller.check_load)
        self.browser.loadFinished.connect(self.controller.update_navigation_buttons)
        self.address_bar.returnPressed.connect(self.controller.navigate_to_url)



# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     window = MiniBrowser()
#     window.show()
#     sys.exit(app.exec_())


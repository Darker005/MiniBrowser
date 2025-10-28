import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLineEdit, QVBoxLayout, QPushButton, QHBoxLayout
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl


miniBrowser = QApplication(sys.argv)

# tạo cửa sổ
window = QWidget()
window.setWindowTitle("Mini Browser")
window.resize(900, 600)

# tạo các layout

#layout chính
layout_main = QVBoxLayout()

# layout chứa các nút và thanh url
layout_top = QHBoxLayout()
#layout chứa các nút
layout_contain_button = QHBoxLayout()
# các nút
btn_back = QPushButton("Back")
btn_next = QPushButton("Next")
btn_reload = QPushButton("reload")
# thêm các nút
layout_contain_button.addWidget(btn_back)
layout_contain_button.addWidget(btn_next)
layout_contain_button.addWidget(btn_reload)
# layout chứa thanh url
layout_contain_addressBar = QHBoxLayout()
# thanh url
address_bar = QLineEdit()
address_bar.setPlaceholderText("enter url")
# thêm thanh url
layout_contain_addressBar.addWidget(address_bar)

# thêm layout phần phía trên
layout_top.addLayout(layout_contain_button)
layout_top.addLayout(layout_contain_addressBar)

# tạo trình duyệt
browser = QWebEngineView()
browser.setUrl(QUrl("https://www.google.com"))
# thêm layout vào layout chính
layout_main.addLayout(layout_top)
layout_main.addWidget(browser)
#xử lý sự kiện 
btn_back.clicked.connect(browser.back)
btn_next.clicked.connect(browser.forward)

def navigate_to_url():
    url = address_bar.text().strip()
    if not url:
        return
    if not url.startswith(("http://","https://")):
        if "." in url:
            url = "https://"+url
        else:
            url = f"https://www.google.com/search?q={url}"
    browser.setUrl(QUrl(url))

def reload_page(qurl):
    current_url = browser.url().toString()
    browser.setUrl(QUrl(current_url))

def update_url_bar(qurl):
    address_bar.setText(qurl.toString())

def check_load(ok):
    if not ok:
        browser.setHtml("<h1>Page not found</h1>")

address_bar.returnPressed.connect(navigate_to_url)
btn_reload.clicked.connect(reload_page)
browser.urlChanged.connect(update_url_bar)
browser.loadFinished.connect(check_load)
# set layout
window.setLayout(layout_main)
window.show()
sys.exit(miniBrowser.exec_())

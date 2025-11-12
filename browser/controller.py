from PyQt5.QtCore import *

class BrowserController:
    def __init__(self, browser, address_bar, btn_back=None, btn_next=None):
        self.browser = browser
        self.address_bar = address_bar
        self.btn_back = btn_back
        self.btn_next = btn_next

    def navigate_to_url(self):
        url = self.address_bar.text().strip()
        if not url:
            return
        if not url.startswith(("http://", "https://")):
            if "." in url:
                url = "https://" + url
            else:
                url = f"https://www.google.com/search?q={url}"
        self.browser.setUrl(QUrl(url))

    #  Hàm cập nhật thanh url khi chuyển sang 1 trang khác
    def update_url_bar(self, qurl):
        self.address_bar.setText(qurl.toString())

    # hàm load trang
    def reload_page(self):
        current_url = self.browser.url().toString()
        self.browser.setUrl(QUrl(current_url))
    
    # hàm kiểm tra nếu lỗi hoặc tìm không ra url thì hiện html
    def check_load(self, ok):
        if not ok:
            self.browser.setHtml("<h1>Page not found</h1>")
    # hàm xử lý nút lùi 
    def go_back(self):
            self.browser.back()
    # hàm xử lý nút tiến
    def go_forward(self):
            self.browser.forward()

    # hàm xử lý các nút nếu không thể next hay lùi
    def update_navigation_buttons(self):
        if self.btn_back and self.btn_next:
            self.btn_back.setEnabled(self.browser.history().canGoBack())
            self.btn_next.setEnabled(self.browser.history().canGoForward())

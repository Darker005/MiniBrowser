from PyQt5.QtCore import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

class TabManager:
    def __init__(self, tab_bar, web_container, address_bar, controller, main_window):
        self.tab_bar = tab_bar
        self.web_container = web_container
        self.address_bar = address_bar
        self.controller = controller
        self.main_window = main_window

        self.browsers = []

        # xử lý khi có sự kiện nào đó xảy ra với thanh tab_bar
        self.tab_bar.tabCloseRequested.connect(self.close_tab)
        self.tab_bar.currentChanged.connect(self.switch_tab)

        # shortcuts
        QShortcut(QKeySequence("Ctrl+T"), main_window, activated=self.add_new_tab)
        QShortcut(QKeySequence("Ctrl+W"), main_window, activated=lambda: self.close_tab(self.tab_bar.currentIndex()))
        QShortcut(QKeySequence("Ctrl+Tab"), main_window, activated=self.next_tab)
        QShortcut(QKeySequence("Ctrl+Shift+Tab"), main_window, activated=self.previous_tab)
    
    # các hàm xử lý tab
    def add_new_tab(self, qurl=None):
        if qurl is None:
            qurl = QUrl("https://www.google.com")
        
        browser = QWebEngineView()
        browser.setUrl(qurl)

        # thêm cái browser mà mình mới add vào container
        self.web_container.addWidget(browser)
        self.web_container.setCurrentWidget(browser)

        # lưu vào list
        self.browsers.append(browser)

        # thêm tab
        i = self.tab_bar.addTab("New Tab")
        self.tab_bar.setCurrentIndex(i)

        # kêt nối sự kiện
        browser.iconChanged.connect(lambda icon, i=i: self.tab_bar.setTabIcon(i, icon))
        browser.urlChanged.connect(lambda url, i=i: self.update_url_bar(url, i))
        browser.titleChanged.connect(lambda title, i=i: self.tab_bar.setTabText(i, title[:15]))
        browser.loadFinished.connect(lambda: self.controller.update_navigation_buttons())

        # cập nhật controller sang browser hiện tại
        self.controller.browser = browser

    def close_tab(self, index):
        if len(self.browsers) <= 1:
            self.main_window.close()
            return
        
        browser = self.browsers.pop(index)
        self.web_container.removeWidget(browser)
        browser.deleteLater()
        self.tab_bar.removeTab(index)

        new_index = len(self.browsers) - 1
        self.tab_bar.setCurrentIndex(new_index)
        self.switch_tab(new_index)

    def switch_tab(self, index):
        if 0 <= index <= len(self.browsers):
            browser = self.browsers[index]
            self.web_container.setCurrentWidget(browser)
            self.controller.browser = browser
            self.address_bar.setText(browser.url().toString())
            self.controller.update_navigation_buttons()
    
    def update_url_bar(self, url, index):
        if index == self.tab_bar.currentIndex():
            self.address_bar.setText(url.toString())
    
    # các hàm xử lý tổ hơp phím làm việc với tab
    def next_tab(self):
        count = self.tab_bar.count()
        if count > 1:
            new_index = (self.tab_bar.currentIndex() + 1) % count
            self.tab_bar.setCurrentIndex(new_index)

    def previous_tab(self):
        count = self.tab_bar.count()
        if count > 1:
            new_index = (self.tab_bar.currentIndex() - 1) % count
            self.tab_bar.setCurrentIndex(new_index)
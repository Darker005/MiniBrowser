from PyQt5.QtCore import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

class TabManager(QObject):
    tab_changed = pyqtSignal()
    def __init__(self, tab_bar, web_container, address_bar, controller, main_window, history_manager, web_profile=None):
        super().__init__()
        self.tab_bar = tab_bar
        self.web_container = web_container
        self.address_bar = address_bar
        self.controller = controller
        self.main_window = main_window
        self.history_manager = history_manager
        self.web_profile = web_profile

        self.browsers = []
        # Script CSS ép dark mode cho trang web
        self._dark_mode_script = r"""
(function() {
  const STYLE_ID = "__mini_browser_dark_mode__";
  let style = document.getElementById(STYLE_ID);
  if (!style) {
    style = document.createElement("style");
    style.id = STYLE_ID;
    style.textContent = `
      html {
        background: #121212 !important;
        color: #e0e0e0 !important;
        filter: invert(0.9) hue-rotate(180deg);
      }
      body {
        background: #121212 !important;
        color: #e0e0e0 !important;
      }
      img, picture, video, iframe, canvas {
        filter: invert(1) hue-rotate(180deg) brightness(0.9) contrast(1.05);
        background: transparent !important;
      }
      input, textarea, select, option, button {
        background: #1f1f1f !important;
        color: #e0e0e0 !important;
        border-color: #3c3c3c !important;
      }
      a { color: #8ab4f8 !important; }
    `;
    document.documentElement.appendChild(style);
  }
})();
"""
        self._dark_mode_cleanup_script = r"""
(function() {
  const style = document.getElementById("__mini_browser_dark_mode__");
  if (style) {
    style.remove();
  }
  document.documentElement.style.filter = "";
})();
"""

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
        
        # Kiểm tra URL hợp lệ
        if not qurl.isValid() or qurl.scheme() == "":
            # URL không hợp lệ → mở tab lỗi
            browser = QWebEngineView()
            page = None
            if self.web_profile:
                page = QWebEnginePage(self.web_profile, browser)
                browser.setPage(page)
            browser.setHtml("<h1>Invalid URL</h1>")  # Hiển thị thông báo lỗi
        else:
            browser = QWebEngineView()
            page = None
            if self.web_profile:
                page = QWebEnginePage(self.web_profile, browser)
                browser.setPage(page)
                # Setup network monitoring cho page
                if hasattr(self.main_window, 'network_monitor') and self.main_window.network_monitor:
                    self.main_window.network_monitor.setup_page(page)
            browser.setUrl(qurl)

        # Lưu lại page để cấu hình dark mode
        if page is None:
            page = browser.page()
        self._attach_dark_mode_handler(page)

        # thêm cái browser vào container
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
        browser.loadFinished.connect(lambda ok, br=browser: self.on_page_loaded(br))
        browser.loadFinished.connect(lambda ok: self.tab_changed.emit())

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
            self.tab_changed.emit()
    
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

    # hàm lưu vào history khi mà load xong 1 trang
    def on_page_loaded(self, browser):
        title = browser.title()
        url = browser.url().toString()

        # tránh lưu URL rỗng hoặc about:blank
        if url and url not in ("", "about:blank"):
            self.history_manager.add_entry(title, url)
            # print để kiểm tra
            print("Saved history:", title, url)
    
    def current_browser(self):
        if self.browsers:
            return self.browsers[self.tab_bar.currentIndex()]
        return None

    def _attach_dark_mode_handler(self, page: QWebEnginePage):
        """Gắn sự kiện để ép dark mode mỗi khi trang load"""
        if not page:
            return
        page.loadFinished.connect(lambda ok, p=page: self.apply_dark_mode_to_page(p))

    def apply_dark_mode_to_page(self, page: QWebEnginePage, enabled: bool = None):
        """Inject/cleanup CSS dark mode tùy theo cài đặt"""
        if not page:
            return
        if enabled is None:
            enabled = getattr(self.main_window.theme_manager, "force_web_dark_mode", False)
        script = self._dark_mode_script if enabled else self._dark_mode_cleanup_script
        page.runJavaScript(script)

    def apply_dark_mode_to_all_pages(self, enabled: bool = None):
        """Áp dụng trạng thái dark mode cho tất cả các tab đang mở"""
        for browser in self.browsers:
            page = browser.page()
            if page:
                self.apply_dark_mode_to_page(page, enabled)

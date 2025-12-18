from PyQt5.QtWidgets import QCompleter
from PyQt5.QtCore import *
from browser.google_suggest import *
class SearchSuggestionManager:
    def __init__(self, address_bar, history_manager, bookmark_manager):
        self.address_bar = address_bar
        self.history_manager = history_manager
        self.bookmark_manager = bookmark_manager

        self.google_provider = GoogleSuggestProvider()
        self.google_provider.suggestions_ready.connect(self.on_google_suggestions)

        self.pending_keyword = ""
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.fetch_google)



        self.model = QStringListModel()
        self.completer = QCompleter(self.model)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setFilterMode(Qt.MatchContains)

        self.address_bar.setCompleter(self.completer)

        # lắng nghe khi user gõ
        self.address_bar.textEdited.connect(self.update_suggestions)

    def update_suggestions(self, text):
        if not text or len(text) < 2:
            self.model.setStringList([])
            return

        suggestions = []

        # 1️⃣ Offline suggestions
        for title, url in self.bookmark_manager.search(text):
            suggestions.append(url)

        for title, url in self.history_manager.search(text):
            if url not in suggestions:
                suggestions.append(url)

        # show offline immediately
        self.model.setStringList(suggestions)

        # 2️⃣ Schedule Google suggest (debounce)
        self.pending_keyword = text
        self.timer.start(300)  # 300ms
    
    def fetch_google(self):
        self.google_provider.fetch(self.pending_keyword)

    def on_google_suggestions(self, google_list):
        current = self.model.stringList()

        for s in google_list:
            if s not in current:
                current.append(s)

        self.model.setStringList(current)

        # ⭐ BẮT BUỘC: show popup
        if current:
            self.completer.complete()




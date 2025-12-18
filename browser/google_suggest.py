import json
from PyQt5.QtCore import QObject, pyqtSignal, QUrl
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest


class GoogleSuggestProvider(QObject):
    suggestions_ready = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.manager = QNetworkAccessManager()
        self.manager.finished.connect(self.on_finished)

    def fetch(self, keyword):
        if not keyword or len(keyword) < 2:
            return

        url = QUrl(
            f"https://suggestqueries.google.com/complete/search"
            f"?client=firefox&q={keyword}"
        )
        request = QNetworkRequest(url)
        self.manager.get(request)

    def on_finished(self, reply):
        if reply.error():
            self.suggestions_ready.emit([])
            return

        data = reply.readAll().data()
        try:
            json_data = json.loads(data)
            suggestions = json_data[1]
        except Exception:
            suggestions = []

        self.suggestions_ready.emit(suggestions)

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QCursor, QColor
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl

class HistoryWindow(QWidget):
    def __init__(self, history_manager):
        super().__init__()
        self.history_manager = history_manager

        self.setWindowTitle("Browsing History")
        self.resize(900, 500)

        layout = QVBoxLayout()

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Select", "Title", "URL", "Time"])
        self.table.setAlternatingRowColors(True)
        self.table.setCursor(QCursor(Qt.PointingHandCursor))
        self.table.setWordWrap(True)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setHighlightSections(False)

        # Hover style
        self.table.setStyleSheet("""
            QTableWidget::item:selected { background-color: #80deea; color: black; }
        """)

        layout.addWidget(self.table)

        # Buttons layout
        button_layout = QHBoxLayout()
        self.btn_delete_selected = QPushButton("Delete Selected")
        self.btn_delete_selected.setEnabled(False)
        self.btn_delete_selected.clicked.connect(self.delete_selected_entries)
        button_layout.addWidget(self.btn_delete_selected)

        # Clear History button
        self.btn_clear_history = QPushButton("Clear History")
        self.btn_clear_history.clicked.connect(self.clear_history_confirm)
        button_layout.addWidget(self.btn_clear_history)

        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.close)
        button_layout.addWidget(btn_close)

        layout.addLayout(button_layout)
        self.setLayout(layout)

        # Load history entries
        self.load_history()

        # Double-click mở URL
        self.table.cellDoubleClicked.connect(self.on_row_double_clicked)

        # Theo dõi check/uncheck để enable/disable Delete button
        self.table.itemChanged.connect(self.update_delete_button_state)

    def load_history(self):
        self.table.blockSignals(True)
        entries = self.history_manager.get_all()  # id, title, url, timestamp
        self.table.setRowCount(len(entries))

        for row, (id_, title, url, timestamp) in enumerate(entries):
            # Checkbox
            checkbox_item = QTableWidgetItem()
            checkbox_item.setCheckState(Qt.Unchecked)
            checkbox_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            checkbox_item.setData(Qt.UserRole, id_)
            self.table.setItem(row, 0, checkbox_item)

            # Title
            self.table.setItem(row, 1, QTableWidgetItem(title))
            # URL
            self.table.setItem(row, 2, QTableWidgetItem(url))
            # Time
            self.table.setItem(row, 3, QTableWidgetItem(timestamp.strftime("%d %b %Y, %H:%M")))

            # Reset background
            for col in range(1, 4):
                self.table.item(row, col).setBackground(QColor("white"))

        self.table.blockSignals(False)
        self.update_delete_button_state(None)
        
        # Vô hiệu hóa nút Clear History nếu không còn row nào
        self.btn_clear_history.setEnabled(self.table.rowCount() > 0)

    def update_delete_button_state(self, item):
        any_checked = False
        for row in range(self.table.rowCount()):
            checkbox_item = self.table.item(row, 0)
            checked = checkbox_item.checkState() == Qt.Checked
            if checked:
                any_checked = True
                bg_color = QColor("#ffe0b2")  # màu row tick
            else:
                bg_color = QColor("white")  # màu normal
            for col in range(1, 4):
                self.table.item(row, col).setBackground(bg_color)
        self.btn_delete_selected.setEnabled(any_checked)

    def on_row_double_clicked(self, row, column):
        url_item = self.table.item(row, 2)
        title_item = self.table.item(row, 1)
        if url_item and hasattr(self, 'main_window'):
            url_text = url_item.text()
            title_text = title_item.text() if title_item else url_text
            # Open in new tab
            self.main_window.tab_manager.add_new_tab(QUrl(url_text))
            # Add to history
            self.history_manager.add_entry(title_text, url_text)
            # Reload table
            self.load_history()

    def delete_selected_entries(self):
        for row in range(self.table.rowCount()):
            checkbox_item = self.table.item(row, 0)
            if checkbox_item.checkState() == Qt.Checked:
                entry_id = checkbox_item.data(Qt.UserRole)
                if entry_id is not None:
                    self.history_manager.delete_entry_by_id(entry_id)
        self.load_history()

    def clear_history_confirm(self):
        reply = QMessageBox.question(self, "Clear History",
                                     "Are you sure you want to clear all browsing history?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.history_manager.clear()
            self.load_history()

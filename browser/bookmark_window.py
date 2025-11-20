from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QCursor, QColor
from PyQt5.QtCore import QUrl

class BookmarkWindow(QWidget):
    def __init__(self, bookmark_manager):
        super().__init__()
        self.bookmark_manager = bookmark_manager

        self.setWindowTitle("Bookmarks")
        self.resize(1000, 500)

        layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Select", "Title", "URL", "Edit"])
        self.table.setAlternatingRowColors(True)
        self.table.setCursor(QCursor(Qt.PointingHandCursor))
        self.table.setWordWrap(True)

        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)

        layout.addWidget(self.table)

        # Buttons: Delete, Clear All, Close
        button_layout = QHBoxLayout()

        self.btn_delete_selected = QPushButton("Delete Selected")
        self.btn_delete_selected.setEnabled(False)
        self.btn_delete_selected.clicked.connect(self.delete_selected)
        button_layout.addWidget(self.btn_delete_selected)

        self.btn_clear_all = QPushButton("Clear All Bookmarks")
        self.btn_clear_all.clicked.connect(self.clear_all)
        button_layout.addWidget(self.btn_clear_all)

        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.close)
        button_layout.addWidget(btn_close)

        layout.addLayout(button_layout)
        self.setLayout(layout)

        # Signals
        self.table.itemChanged.connect(self.on_item_changed)
        self.table.cellDoubleClicked.connect(self.open_bookmark)

        self.load_bookmarks()

    def load_bookmarks(self):
        self.table.blockSignals(True)
        entries = self.bookmark_manager.list_bookmarks()
        self.table.setRowCount(len(entries))

        for row, (id_, title, url) in enumerate(entries):
            # Checkbox
            check_item = QTableWidgetItem()
            check_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            check_item.setCheckState(Qt.Unchecked)
            check_item.setData(Qt.UserRole, id_)
            self.table.setItem(row, 0, check_item)

            # Title
            title_item = QTableWidgetItem(title)
            title_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.table.setItem(row, 1, title_item)

            # URL
            url_item = QTableWidgetItem(url)
            url_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.table.setItem(row, 2, url_item)

            # Edit button
            btn_edit = QPushButton("Edit")
            btn_edit.clicked.connect(lambda _, r=row: self.edit_row(r))
            self.table.setCellWidget(row, 3, btn_edit)

        self.table.blockSignals(False)
        self.update_delete_button()
        self.btn_clear_all.setEnabled(len(entries) > 0)

    def update_delete_button(self):
        any_checked = any(self.table.item(r, 0).checkState() == Qt.Checked
                          for r in range(self.table.rowCount()))
        self.btn_delete_selected.setEnabled(any_checked)

    def on_item_changed(self, item):
        if item.column() == 0:
            self.update_delete_button()

    def edit_row(self, row):
        bookmark_id = self.table.item(row, 0).data(Qt.UserRole)
        title = self.table.item(row, 1).text()
        url = self.table.item(row, 2).text()

        dialog = EditBookmarkDialog(title, url)
        if dialog.exec_():
            new_title, new_url = dialog.get_data()
            self.bookmark_manager.update_bookmark(bookmark_id, new_title, new_url)
            self.load_bookmarks()  # reload dữ liệu mới

    def open_bookmark(self, row, column):
        # Chỉ mở khi double-click vào Title hoặc URL
        if column not in [1, 2]:
            return

        title_item = self.table.item(row, 1)
        url_item = self.table.item(row, 2)
        if not url_item:
            return

        title = title_item.text()
        url = url_item.text()

        if hasattr(self, "main_window"):
            self.main_window.tab_manager.add_new_tab(QUrl(url))
            self.main_window.history_manager.add_entry(title, url)

    def delete_selected(self):
        confirm = QMessageBox.question(
            self, "Confirm Delete",
            "Are you sure you want to delete selected bookmarks?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm != QMessageBox.Yes:
            return

        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item.checkState() == Qt.Checked:
                bookmark_id = item.data(Qt.UserRole)
                self.bookmark_manager.delete_bookmark_by_id(bookmark_id)
        self.load_bookmarks()

    def clear_all(self):
        if self.table.rowCount() == 0:
            QMessageBox.information(self, "No bookmarks", "You do not have any bookmarks.")
            return

        confirm = QMessageBox.warning(
            self,
            "Clear All Bookmarks",
            "Are you sure you want to delete ALL bookmarks?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm != QMessageBox.Yes:
            return

        cursor = self.bookmark_manager.conn.cursor()
        cursor.execute("DELETE FROM bookmarks")
        cursor.connection.commit()
        self.load_bookmarks()


#  class này là của BookmarkDialog khi ấn vào nút edit
class EditBookmarkDialog(QDialog):
    def __init__(self, title, url):
        super().__init__()
        self.setWindowTitle("Edit Bookmark")

        self.input_title = QLineEdit(title)
        self.input_url = QLineEdit(url)

        btn_save = QPushButton("Save")

        layout = QVBoxLayout()
        layout.addWidget(self.input_title)
        layout.addWidget(self.input_url)
        layout.addWidget(btn_save)

        btn_save.clicked.connect(self.accept)

        self.setLayout(layout)

    def get_data(self):
        return self.input_title.text(), self.input_url.text()

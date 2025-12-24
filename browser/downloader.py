import os
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtGui import *
from datetime import datetime


class DownloadItem(QWidget):
    """Widget hiển thị một item tải xuống trong danh sách"""
    def __init__(self, download_item, parent=None):
        super().__init__(parent)
        self.download_item = download_item
        
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 5, 10, 5)
        
        # Tên file và nút
        top_layout = QHBoxLayout()
        self.label_filename = QLabel()
        self.label_filename.setWordWrap(True)
        top_layout.addWidget(self.label_filename)
        
        self.btn_cancel = QPushButton("Hủy")
        self.btn_cancel.setFixedWidth(60)
        self.btn_cancel.clicked.connect(self.cancel_download)
        top_layout.addWidget(self.btn_cancel)
        
        layout.addLayout(top_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        layout.addWidget(self.progress_bar)
        
        # Thông tin tải xuống
        info_layout = QHBoxLayout()
        self.label_status = QLabel("Đang tải...")
        self.label_speed = QLabel("")
        self.label_size = QLabel("")
        
        info_layout.addWidget(self.label_status)
        info_layout.addStretch()
        info_layout.addWidget(self.label_speed)
        info_layout.addWidget(self.label_size)
        
        layout.addLayout(info_layout)
        
        self.setLayout(layout)
        
        # Kết nối signals
        download_item.downloadProgress.connect(self.update_progress)
        download_item.finished.connect(self.on_finished)
        download_item.stateChanged.connect(self.on_state_changed)
        
        # Cập nhật thông tin ban đầu
        self.update_info()
    
    def update_info(self):
        """Cập nhật thông tin hiển thị"""
        path = self.download_item.path()
        filename = os.path.basename(path) if path else "Đang tải..."
        self.label_filename.setText(filename)
        
        # Cập nhật kích thước
        total_bytes = self.download_item.totalBytes()
        if total_bytes > 0:
            size_str = self.format_size(total_bytes)
            self.label_size.setText(size_str)
        else:
            self.label_size.setText("")
    
    def update_progress(self, bytes_received, bytes_total):
        """Cập nhật thanh tiến trình"""
        if bytes_total > 0:
            progress = int((bytes_received / bytes_total) * 100)
            self.progress_bar.setValue(progress)
            
            # Cập nhật kích thước
            received_str = self.format_size(bytes_received)
            total_str = self.format_size(bytes_total)
            self.label_size.setText(f"{received_str} / {total_str}")
        else:
            self.progress_bar.setValue(0)
            if bytes_received > 0:
                self.label_size.setText(self.format_size(bytes_received))
    
    def on_state_changed(self, state):
        """Xử lý khi trạng thái tải xuống thay đổi"""
        if state == QWebEngineDownloadItem.DownloadCompleted:
            self.label_status.setText("Hoàn thành")
            self.btn_cancel.setText("Mở")
            self.btn_cancel.clicked.disconnect()
            self.btn_cancel.clicked.connect(self.open_file)
        elif state == QWebEngineDownloadItem.DownloadCancelled:
            self.label_status.setText("Đã hủy")
            self.btn_cancel.setEnabled(False)
        elif state == QWebEngineDownloadItem.DownloadInterrupted:
            self.label_status.setText("Bị gián đoạn")
        else:
            self.label_status.setText("Đang tải...")
    
    def on_finished(self):
        """Xử lý khi tải xuống hoàn tất"""
        if self.download_item.state() == QWebEngineDownloadItem.DownloadCompleted:
            self.progress_bar.setValue(100)
            self.label_status.setText("Hoàn thành")
            self.btn_cancel.setText("Mở")
            self.btn_cancel.clicked.disconnect()
            self.btn_cancel.clicked.connect(self.open_file)
    
    def cancel_download(self):
        """Hủy tải xuống"""
        if self.download_item.state() == QWebEngineDownloadItem.DownloadInProgress:
            self.download_item.cancel()
    
    def open_file(self):
        """Mở file đã tải xuống"""
        path = self.download_item.path()
        if path and os.path.exists(path):
            QDesktopServices.openUrl(QUrl.fromLocalFile(path))
    
    def format_size(self, bytes_size):
        """Định dạng kích thước file"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.1f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.1f} TB"


class DownloadWindow(QDialog):
    """Cửa sổ quản lý tải xuống"""
    def __init__(self, download_manager, parent=None):
        super().__init__(parent)
        self.download_manager = download_manager
        self.setWindowTitle("Tải xuống")
        self.setMinimumSize(600, 400)
        
        layout = QVBoxLayout()
        
        # Tiêu đề
        title_label = QLabel("Tải xuống")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title_label)
        
        # Scroll area chứa danh sách tải xuống
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.downloads_container = QWidget()
        self.downloads_layout = QVBoxLayout()
        self.downloads_layout.setAlignment(Qt.AlignTop)
        self.downloads_container.setLayout(self.downloads_layout)
        
        scroll_area.setWidget(self.downloads_container)
        layout.addWidget(scroll_area)
        
        # Nút đóng
        btn_close = QPushButton("Đóng")
        btn_close.clicked.connect(self.close)
        layout.addWidget(btn_close)
        
        self.setLayout(layout)
        
        # Kết nối với download manager
        download_manager.download_added.connect(self.add_download_item)
    
    def add_download_item(self, download_item):
        """Thêm một item tải xuống vào danh sách"""
        item_widget = DownloadItem(download_item)
        self.downloads_layout.addWidget(item_widget)
        
        # Tự động hiển thị cửa sổ khi có tải xuống mới
        if not self.isVisible():
            self.show()


class DownloadManager(QObject):
    """Quản lý các tải xuống"""
    download_added = pyqtSignal(QWebEngineDownloadItem)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.downloads = []
        self.download_window = None
        
        # Tạo thư mục Downloads nếu chưa có
        self.downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads", "MiniBrowser")
        os.makedirs(self.downloads_dir, exist_ok=True)
    
    def setup_profile(self, profile):
        """Thiết lập profile để bắt các yêu cầu tải xuống"""
        profile.downloadRequested.connect(self.handle_download_request)
    
    def handle_download_request(self, download_item):
        """Xử lý yêu cầu tải xuống"""
        # Lấy tên file từ URL
        url = download_item.url().toString()
        suggested_filename = download_item.suggestedFileName()
        
        if not suggested_filename:
            # Nếu không có tên file gợi ý, tạo tên từ URL
            suggested_filename = os.path.basename(url.split('?')[0])
            if not suggested_filename or '.' not in suggested_filename:
                suggested_filename = "download"
        
        # Đường dẫn đầy đủ
        file_path = os.path.join(self.downloads_dir, suggested_filename)
        
        # Xử lý trường hợp file đã tồn tại
        base_path = file_path
        counter = 1
        while os.path.exists(file_path):
            name, ext = os.path.splitext(base_path)
            file_path = f"{name} ({counter}){ext}"
            counter += 1
        
        # Thiết lập đường dẫn tải xuống
        download_item.setPath(file_path)
        
        # Chấp nhận tải xuống
        download_item.accept()
        
        # Lưu vào danh sách
        self.downloads.append(download_item)
        
        # Phát signal
        self.download_added.emit(download_item)
        
        print(f"Bắt đầu tải xuống: {suggested_filename} -> {file_path}")
    
    def get_download_window(self, parent=None):
        """Lấy hoặc tạo cửa sổ quản lý tải xuống"""
        if self.download_window is None:
            self.download_window = DownloadWindow(self, parent)
        return self.download_window
    
    def show_downloads(self, parent=None):
        """Hiển thị cửa sổ quản lý tải xuống"""
        window = self.get_download_window(parent)
        window.show()
        window.raise_()
        window.activateWindow()



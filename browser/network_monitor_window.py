from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from browser.network_monitor import NetworkMonitor, NetworkRequest, NetworkUtilities
import json
from datetime import datetime


class RequestDetailsDialog(QDialog):
    """Dialog hiển thị chi tiết request"""
    def __init__(self, request: NetworkRequest, parent=None):
        super().__init__(parent)
        self.request = request
        self.setWindowTitle("Request Details")
        self.setMinimumSize(800, 600)
        
        layout = QVBoxLayout()
        
        # Tabs
        tabs = QTabWidget()
        
        # Overview tab
        overview_tab = QWidget()
        overview_layout = QVBoxLayout()
        
        # URL
        url_label = QLabel("URL:")
        url_label.setStyleSheet("font-weight: bold;")
        url_text = QTextEdit()
        url_text.setReadOnly(True)
        url_text.setMaximumHeight(60)
        url_text.setText(request.url)
        overview_layout.addWidget(url_label)
        overview_layout.addWidget(url_text)
        
        # Method và Status
        info_layout = QHBoxLayout()
        method_label = QLabel(f"Method: {request.method}")
        status_label = QLabel(f"Status: {request.status_code or 'Pending'}")
        time_label = QLabel(f"Duration: {request.duration:.2f}ms" if request.duration else "Duration: Pending")
        info_layout.addWidget(method_label)
        info_layout.addWidget(status_label)
        info_layout.addWidget(time_label)
        overview_layout.addLayout(info_layout)
        
        # Size và Type
        size_layout = QHBoxLayout()
        size_label = QLabel(f"Size: {NetworkRequest.format_size(request.response_size)}")
        type_label = QLabel(f"Type: {request.mime_type or 'Unknown'}")
        ip_label = QLabel(f"IP: {request.ip_address or 'Resolving...'}")
        size_layout.addWidget(size_label)
        size_layout.addWidget(type_label)
        size_layout.addWidget(ip_label)
        overview_layout.addLayout(size_layout)
        
        overview_layout.addStretch()
        overview_tab.setLayout(overview_layout)
        tabs.addTab(overview_tab, "Overview")
        
        # Request Headers tab
        req_headers_tab = QWidget()
        req_headers_layout = QVBoxLayout()
        req_headers_text = QTextEdit()
        req_headers_text.setReadOnly(True)
        req_headers_text.setFont(QFont("Courier", 9))
        if request.headers:
            headers_str = "\n".join(f"{k}: {v}" for k, v in request.headers.items())
        else:
            headers_str = "No headers"
        req_headers_text.setText(headers_str)
        req_headers_layout.addWidget(req_headers_text)
        req_headers_tab.setLayout(req_headers_layout)
        tabs.addTab(req_headers_tab, "Request Headers")
        
        # Response Headers tab
        resp_headers_tab = QWidget()
        resp_headers_layout = QVBoxLayout()
        resp_headers_text = QTextEdit()
        resp_headers_text.setReadOnly(True)
        resp_headers_text.setFont(QFont("Courier", 9))
        if request.response_headers:
            headers_str = "\n".join(f"{k}: {v}" for k, v in request.response_headers.items())
        else:
            headers_str = "No response headers yet"
        resp_headers_text.setText(headers_str)
        resp_headers_layout.addWidget(resp_headers_text)
        resp_headers_tab.setLayout(resp_headers_layout)
        tabs.addTab(resp_headers_tab, "Response Headers")
        
        # POST Data tab
        if request.post_data:
            post_tab = QWidget()
            post_layout = QVBoxLayout()
            post_text = QTextEdit()
            post_text.setReadOnly(True)
            post_text.setFont(QFont("Courier", 9))
            post_text.setText(request.post_data)
            post_layout.addWidget(post_text)
            post_tab.setLayout(post_layout)
            tabs.addTab(post_tab, "POST Data")
        
        # Network Info tab
        network_tab = QWidget()
        network_layout = QVBoxLayout()
        network_text = QTextEdit()
        network_text.setReadOnly(True)
        network_text.setFont(QFont("Courier", 9))
        
        host, port = request.get_host_info()
        network_info = f"Host: {host}\n"
        network_info += f"Port: {port}\n"
        network_info += f"IP Address: {request.ip_address or 'Not resolved'}\n"
        network_info += f"Start Time: {datetime.fromtimestamp(request.start_time).strftime('%Y-%m-%d %H:%M:%S')}\n"
        if request.end_time:
            network_info += f"End Time: {datetime.fromtimestamp(request.end_time).strftime('%Y-%m-%d %H:%M:%S')}\n"
        if request.error:
            network_info += f"Error: {request.error}\n"
        
        # Parse URL
        url_info = NetworkUtilities.parse_url(request.url)
        if url_info:
            network_info += f"\nURL Components:\n"
            network_info += f"  Scheme: {url_info.get('scheme', 'N/A')}\n"
            network_info += f"  Hostname: {url_info.get('hostname', 'N/A')}\n"
            network_info += f"  Path: {url_info.get('path', 'N/A')}\n"
            network_info += f"  Query: {url_info.get('query', 'N/A')}\n"
        
        network_text.setText(network_info)
        network_layout.addWidget(network_text)
        network_tab.setLayout(network_layout)
        tabs.addTab(network_tab, "Network Info")
        
        layout.addWidget(tabs)
        
        # Close button
        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)
        
        self.setLayout(layout)


class NetworkMonitorWindow(QDialog):
    """Cửa sổ Network Monitor"""
    def __init__(self, network_monitor: NetworkMonitor, parent=None):
        super().__init__(parent)
        self.network_monitor = network_monitor
        self.setWindowTitle("Network Monitor")
        self.setMinimumSize(1000, 600)
        
        layout = QVBoxLayout()
        
        # Toolbar
        toolbar = QHBoxLayout()
        
        self.btn_start = QPushButton("Start Monitoring")
        self.btn_stop = QPushButton("Stop Monitoring")
        self.btn_clear = QPushButton("Clear")
        self.btn_export = QPushButton("Export")
        self.btn_test_connection = QPushButton("Test Connection")
        
        toolbar.addWidget(self.btn_start)
        toolbar.addWidget(self.btn_stop)
        toolbar.addWidget(self.btn_clear)
        toolbar.addWidget(self.btn_export)
        toolbar.addWidget(self.btn_test_connection)
        toolbar.addStretch()
        
        # Statistics label
        self.stats_label = QLabel("Requests: 0")
        toolbar.addWidget(self.stats_label)
        
        layout.addLayout(toolbar)
        
        # Filter bar
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Filter:"))
        
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Filter by URL, status, or type...")
        self.filter_input.textChanged.connect(self.apply_filter)
        filter_layout.addWidget(self.filter_input)
        
        # Filter by status
        self.status_filter = QComboBox()
        self.status_filter.addItem("All Status Codes")
        self.status_filter.addItem("200 OK")
        self.status_filter.addItem("404 Not Found")
        self.status_filter.addItem("500 Server Error")
        self.status_filter.currentIndexChanged.connect(self.apply_filter)
        filter_layout.addWidget(self.status_filter)
        
        # Filter by type
        self.type_filter = QComboBox()
        self.type_filter.addItem("All Types")
        self.type_filter.addItem("text/html")
        self.type_filter.addItem("application/json")
        self.type_filter.addItem("image")
        self.type_filter.addItem("javascript")
        self.type_filter.addItem("css")
        self.type_filter.currentIndexChanged.connect(self.apply_filter)
        filter_layout.addWidget(self.type_filter)
        
        layout.addLayout(filter_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "Method", "URL", "Status", "Type", "Size", "Time"
        ])
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSortingEnabled(True)
        self.table.doubleClicked.connect(self.show_request_details)
        
        # Resize columns
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        
        layout.addWidget(self.table)
        
        # Context menu
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.accept)
        button_layout.addWidget(btn_close)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Connect signals
        self.btn_start.clicked.connect(self.start_monitoring)
        self.btn_stop.clicked.connect(self.stop_monitoring)
        self.btn_clear.clicked.connect(self.clear_requests)
        self.btn_export.clicked.connect(self.export_requests)
        self.btn_test_connection.clicked.connect(self.test_connection_dialog)
        
        self.network_monitor.request_added.connect(self.add_request_to_table)
        self.network_monitor.request_updated.connect(self.update_request_in_table)
        
        # Load existing requests
        self.refresh_table()
    
    def start_monitoring(self):
        """Bắt đầu monitoring"""
        self.network_monitor.monitoring = True
        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(True)
    
    def stop_monitoring(self):
        """Dừng monitoring"""
        self.network_monitor.monitoring = False
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)
    
    def clear_requests(self):
        """Xóa tất cả requests"""
        reply = QMessageBox.question(
            self, "Clear Requests", 
            "Are you sure you want to clear all requests?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.network_monitor.clear_requests()
            self.refresh_table()
    
    def add_request_to_table(self, request: NetworkRequest):
        """Thêm request vào table"""
        self.refresh_table()
    
    def update_request_in_table(self, request: NetworkRequest):
        """Cập nhật request trong table"""
        self.refresh_table()
    
    def refresh_table(self):
        """Refresh toàn bộ table"""
        self.table.setRowCount(0)
        
        requests = self.network_monitor.requests
        for request in requests:
            self.add_row(request)
        
        self.update_statistics()
    
    def add_row(self, request: NetworkRequest):
        """Thêm một row vào table"""
        row = self.table.rowCount()
        self.table.insertRow(row)
        
        # ID
        self.table.setItem(row, 0, QTableWidgetItem(str(request.request_id)))
        
        # Method
        method_item = QTableWidgetItem(request.method)
        if request.method == "GET":
            method_item.setForeground(QColor(0, 100, 0))
        elif request.method == "POST":
            method_item.setForeground(QColor(200, 100, 0))
        self.table.setItem(row, 1, method_item)
        
        # URL
        self.table.setItem(row, 2, QTableWidgetItem(request.url))
        
        # Status
        status_text = str(request.status_code) if request.status_code else "Pending"
        status_item = QTableWidgetItem(status_text)
        if request.status_code:
            if 200 <= request.status_code < 300:
                status_item.setForeground(QColor(0, 150, 0))
            elif 300 <= request.status_code < 400:
                status_item.setForeground(QColor(0, 100, 200))
            elif 400 <= request.status_code < 500:
                status_item.setForeground(QColor(200, 100, 0))
            elif request.status_code >= 500:
                status_item.setForeground(QColor(200, 0, 0))
        self.table.setItem(row, 3, status_item)
        
        # Type
        self.table.setItem(row, 4, QTableWidgetItem(request.mime_type or "Unknown"))
        
        # Size
        self.table.setItem(row, 5, QTableWidgetItem(NetworkRequest.format_size(request.response_size)))
        
        # Time
        time_text = f"{request.duration:.2f}ms" if request.duration else "Pending"
        self.table.setItem(row, 6, QTableWidgetItem(time_text))
        
        # Store request object
        self.table.item(row, 0).setData(Qt.UserRole, request)
    
    def apply_filter(self):
        """Áp dụng filter"""
        filter_text = self.filter_input.text().lower()
        status_filter = self.status_filter.currentText()
        type_filter = self.type_filter.currentText()
        
        self.table.setRowCount(0)
        
        for request in self.network_monitor.requests:
            # Filter by text
            if filter_text and filter_text not in request.url.lower():
                continue
            
            # Filter by status
            if status_filter != "All Status Codes":
                expected_status = int(status_filter.split()[0])
                if request.status_code != expected_status:
                    continue
            
            # Filter by type
            if type_filter != "All Types":
                if type_filter.lower() not in (request.mime_type or "").lower():
                    continue
            
            self.add_row(request)
        
        self.update_statistics()
    
    def update_statistics(self):
        """Cập nhật statistics"""
        stats = self.network_monitor.get_statistics()
        total = stats.get('total_requests', 0)
        total_size = stats.get('total_size', 0)
        self.stats_label.setText(
            f"Requests: {total} | "
            f"Total Size: {NetworkRequest.format_size(total_size)}"
        )
    
    def show_request_details(self, index):
        """Hiển thị chi tiết request"""
        row = index.row()
        item = self.table.item(row, 0)
        if item:
            request = item.data(Qt.UserRole)
            if request:
                dialog = RequestDetailsDialog(request, self)
                dialog.exec_()
    
    def show_context_menu(self, position):
        """Hiển thị context menu"""
        item = self.table.itemAt(position)
        if not item:
            return
        
        menu = QMenu(self)
        
        action_details = QAction("View Details", self)
        action_details.triggered.connect(lambda: self.show_request_details(self.table.indexAt(position)))
        menu.addAction(action_details)
        
        action_copy_url = QAction("Copy URL", self)
        action_copy_url.triggered.connect(lambda: self.copy_url(item))
        menu.addAction(action_copy_url)
        
        menu.exec_(self.table.viewport().mapToGlobal(position))
    
    def copy_url(self, item):
        """Copy URL to clipboard"""
        request = item.data(Qt.UserRole)
        if request:
            clipboard = QApplication.clipboard()
            clipboard.setText(request.url)
    
    def export_requests(self):
        """Export requests to JSON"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Requests", "", "JSON Files (*.json)"
        )
        if file_path:
            try:
                data = []
                for request in self.network_monitor.requests:
                    data.append({
                        'id': request.request_id,
                        'url': request.url,
                        'method': request.method,
                        'status_code': request.status_code,
                        'headers': request.headers,
                        'response_headers': request.response_headers,
                        'size': request.response_size,
                        'duration': request.duration,
                        'mime_type': request.mime_type,
                        'ip_address': request.ip_address,
                        'error': request.error
                    })
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                QMessageBox.information(self, "Export", "Requests exported successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export: {str(e)}")
    
    def test_connection_dialog(self):
        """Dialog để test connection"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Test Connection")
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        
        # Host input
        host_layout = QHBoxLayout()
        host_layout.addWidget(QLabel("Host:"))
        host_input = QLineEdit()
        host_input.setPlaceholderText("example.com")
        host_layout.addWidget(host_input)
        layout.addLayout(host_layout)
        
        # Port input
        port_layout = QHBoxLayout()
        port_layout.addWidget(QLabel("Port:"))
        port_input = QSpinBox()
        port_input.setRange(1, 65535)
        port_input.setValue(80)
        port_layout.addWidget(port_input)
        layout.addLayout(port_layout)
        
        # SSL checkbox
        ssl_checkbox = QCheckBox("Use SSL/TLS")
        layout.addWidget(ssl_checkbox)
        
        # Result text
        result_text = QTextEdit()
        result_text.setReadOnly(True)
        result_text.setFont(QFont("Courier", 9))
        layout.addWidget(result_text)
        
        def test_connection():
            host = host_input.text().strip()
            port = port_input.value()
            use_ssl = ssl_checkbox.isChecked()
            
            if not host:
                result_text.setText("Please enter a hostname")
                return
            
            result_text.clear()
            result_text.append(f"Testing connection to {host}:{port}...\n")
            result_text.append(f"SSL/TLS: {use_ssl}\n\n")
            
            # Get host info
            host_info = NetworkUtilities.get_host_info(host)
            if 'error' in host_info:
                result_text.append(f"DNS Resolution Error: {host_info['error']}\n")
            else:
                result_text.append(f"IP Address: {host_info.get('ip', 'N/A')}\n")
                if 'hostname' in host_info:
                    result_text.append(f"Resolved Hostname: {host_info['hostname']}\n")
                result_text.append("\n")
            
            # Test connection
            if use_ssl:
                success, cert_info = NetworkUtilities.test_ssl_connection(host, port)
                if success:
                    result_text.append("✓ SSL Connection: SUCCESS\n")
                    if isinstance(cert_info, dict):
                        result_text.append(f"Certificate Subject: {cert_info.get('subject', 'N/A')}\n")
                else:
                    result_text.append(f"✗ SSL Connection: FAILED\n")
                    result_text.append(f"Error: {cert_info}\n")
            else:
                success = NetworkUtilities.test_connection(host, port)
                if success:
                    result_text.append("✓ TCP Connection: SUCCESS\n")
                else:
                    result_text.append("✗ TCP Connection: FAILED\n")
        
        # Buttons
        button_layout = QHBoxLayout()
        btn_test = QPushButton("Test")
        btn_test.clicked.connect(test_connection)
        btn_close = QPushButton("Close")
        btn_close.clicked.connect(dialog.accept)
        button_layout.addWidget(btn_test)
        button_layout.addWidget(btn_close)
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        dialog.exec_()


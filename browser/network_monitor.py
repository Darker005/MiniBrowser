import socket
import ssl
import time
import urllib.parse
from datetime import datetime
from PyQt5.QtCore import QObject, pyqtSignal, QUrl, QByteArray
from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor
from PyQt5.QtWebEngineWidgets import QWebEngineProfile


class NetworkRequest:
    """Class đại diện cho một network request"""
    def __init__(self, request_id, url, method="GET", headers=None, post_data=None):
        self.request_id = request_id
        self.url = url
        self.method = method
        self.headers = headers or {}
        self.post_data = post_data
        self.status_code = None
        self.response_headers = {}
        self.response_size = 0
        self.start_time = time.time()
        self.end_time = None
        self.duration = None
        self.error = None
        self.mime_type = None
        self.ip_address = None
        self.port = None
        
    def finish(self, status_code=None, response_headers=None, response_size=0, error=None):
        """Hoàn thành request và tính toán thời gian"""
        self.end_time = time.time()
        self.duration = (self.end_time - self.start_time) * 1000  # milliseconds
        self.status_code = status_code
        self.response_headers = response_headers or {}
        self.response_size = response_size
        self.error = error
        
        # Extract MIME type from response headers
        content_type = self.response_headers.get('Content-Type', '')
        if ';' in content_type:
            self.mime_type = content_type.split(';')[0].strip()
        else:
            self.mime_type = content_type.strip()
    
    def get_host_info(self):
        """Lấy thông tin host và port từ URL"""
        try:
            parsed = urllib.parse.urlparse(self.url)
            host = parsed.hostname
            port = parsed.port
            if port is None:
                port = 443 if parsed.scheme == 'https' else 80
            return host, port
        except:
            return None, None
    
    def resolve_ip(self):
        """Resolve IP address của host"""
        try:
            host, _ = self.get_host_info()
            if host:
                self.ip_address = socket.gethostbyname(host)
                return self.ip_address
        except Exception as e:
            self.error = f"DNS Resolution failed: {str(e)}"
        return None
    
    def to_dict(self):
        """Chuyển đổi thành dictionary để hiển thị"""
        return {
            'id': self.request_id,
            'method': self.method,
            'url': self.url,
            'status': self.status_code or 'Pending',
            'type': self.mime_type or 'Unknown',
            'size': self.format_size(self.response_size),
            'time': f"{self.duration:.2f}ms" if self.duration else 'Pending',
            'ip': self.ip_address or 'Resolving...',
            'error': self.error
        }
    
    @staticmethod
    def format_size(size):
        """Format kích thước file"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"


class NetworkRequestInterceptor(QWebEngineUrlRequestInterceptor):
    """Interceptor để capture các HTTP requests"""
    def __init__(self, network_monitor):
        super().__init__()
        self.network_monitor = network_monitor
    
    def interceptRequest(self, info):
        """Intercept mỗi request"""
        if not self.network_monitor.monitoring:
            return
        
        url = info.requestUrl().toString()
        method = info.requestMethod().data().decode('utf-8')
        
        # Capture request headers
        # Note: QWebEngineUrlRequestInfo doesn't provide direct access to all headers
        # Headers are added by Chromium at a later stage for security reasons
        headers = {}
        try:
            # Try to get resource type and other available info
            resource_type = info.resourceType()
            # We can't get full headers here, but we can capture what's available
            # Headers will be empty for now, but URL and method are captured
        except Exception:
            pass
        
        # Capture POST data if available
        post_data = None
        try:
            if method == 'POST' and info.requestBody():
                body = info.requestBody()
                if body:
                    post_data = body.data().decode('utf-8', errors='ignore')
        except Exception:
            pass
        
        # Tạo NetworkRequest object
        request = NetworkRequest(
            request_id=len(self.network_monitor.requests) + 1,
            url=url,
            method=method,
            headers=headers,
            post_data=post_data
        )
        
        # Resolve IP address (async)
        request.resolve_ip()
        
        # Thêm vào danh sách
        self.network_monitor.add_request(request)


class NetworkMonitor(QObject):
    """Quản lý network monitoring"""
    request_added = pyqtSignal(object)  # Signal khi có request mới
    request_updated = pyqtSignal(object)  # Signal khi request được cập nhật
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.requests = []
        self.request_map = {}  # Map URL -> NetworkRequest để update
        self.interceptor = NetworkRequestInterceptor(self)
        self.monitoring = False
        self.max_requests = 1000  # Giới hạn số lượng requests
    
    def setup_profile(self, profile: QWebEngineProfile):
        """Thiết lập interceptor cho profile"""
        profile.setUrlRequestInterceptor(self.interceptor)
        self.monitoring = True
    
    def setup_page(self, page):
        """Thiết lập monitoring cho một page để capture response"""
        if not self.monitoring:
            return
        
        # Connect to loadFinished signal để capture response info
        page.loadFinished.connect(lambda ok: self.on_page_loaded(page, ok))
    
    def on_page_loaded(self, page, ok):
        """Khi page load xong, lấy thông tin response"""
        url = page.url().toString()
        
        # Tìm request tương ứng
        request = self.request_map.get(url)
        if request:
            # Update với thông tin response cơ bản
            status_code = 200 if ok else 500
            request.finish(status_code=status_code, response_size=0)
            self.update_request(request)
    
    def add_request(self, request: NetworkRequest):
        """Thêm request mới vào danh sách"""
        if not self.monitoring:
            return
        
        self.requests.append(request)
        
        # Lưu vào map để có thể update sau
        self.request_map[request.url] = request
        
        # Giới hạn số lượng requests
        if len(self.requests) > self.max_requests:
            old_request = self.requests.pop(0)
            if old_request.url in self.request_map:
                del self.request_map[old_request.url]
        
        # Emit signal
        self.request_added.emit(request)
    
    def update_request(self, request: NetworkRequest):
        """Cập nhật thông tin request"""
        self.request_updated.emit(request)
    
    def clear_requests(self):
        """Xóa tất cả requests"""
        self.requests.clear()
    
    def get_requests_by_url(self, url_pattern):
        """Lọc requests theo URL pattern"""
        return [r for r in self.requests if url_pattern.lower() in r.url.lower()]
    
    def get_requests_by_status(self, status_code):
        """Lọc requests theo status code"""
        return [r for r in self.requests if r.status_code == status_code]
    
    def get_requests_by_type(self, mime_type):
        """Lọc requests theo MIME type"""
        return [r for r in self.requests if mime_type.lower() in (r.mime_type or '').lower()]
    
    def get_statistics(self):
        """Lấy thống kê về network requests"""
        if not self.requests:
            return {}
        
        total_size = sum(r.response_size for r in self.requests if r.response_size)
        total_time = sum(r.duration for r in self.requests if r.duration) or 0
        
        status_codes = {}
        mime_types = {}
        
        for req in self.requests:
            if req.status_code:
                status_codes[req.status_code] = status_codes.get(req.status_code, 0) + 1
            if req.mime_type:
                mime_types[req.mime_type] = mime_types.get(req.mime_type, 0) + 1
        
        return {
            'total_requests': len(self.requests),
            'total_size': total_size,
            'total_time': total_time,
            'average_time': total_time / len([r for r in self.requests if r.duration]) if any(r.duration for r in self.requests) else 0,
            'status_codes': status_codes,
            'mime_types': mime_types
        }


class NetworkUtilities:
    """Các utility functions cho network programming"""
    
    @staticmethod
    def parse_http_headers(header_string):
        """Parse HTTP headers từ string"""
        headers = {}
        if not header_string:
            return headers
        
        lines = header_string.split('\r\n')
        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                headers[key.strip()] = value.strip()
        return headers
    
    @staticmethod
    def parse_url(url_string):
        """Parse URL và trả về các thành phần"""
        try:
            parsed = urllib.parse.urlparse(url_string)
            return {
                'scheme': parsed.scheme,
                'netloc': parsed.netloc,
                'path': parsed.path,
                'params': parsed.params,
                'query': parsed.query,
                'fragment': parsed.fragment,
                'hostname': parsed.hostname,
                'port': parsed.port
            }
        except:
            return None
    
    @staticmethod
    def test_connection(host, port, timeout=5):
        """Test kết nối TCP đến host:port"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except Exception as e:
            return False
    
    @staticmethod
    def test_ssl_connection(host, port=443, timeout=5):
        """Test SSL connection đến host:port"""
        try:
            context = ssl.create_default_context()
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            ssl_sock = context.wrap_socket(sock, server_hostname=host)
            ssl_sock.connect((host, port))
            cert = ssl_sock.getpeercert()
            ssl_sock.close()
            return True, cert
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def get_host_info(hostname):
        """Lấy thông tin về hostname"""
        try:
            ip = socket.gethostbyname(hostname)
            try:
                hostname_info = socket.gethostbyaddr(ip)
                return {
                    'ip': ip,
                    'hostname': hostname_info[0],
                    'aliases': hostname_info[1],
                    'addresses': hostname_info[2]
                }
            except:
                return {'ip': ip, 'hostname': hostname}
        except Exception as e:
            return {'error': str(e)}
    
    @staticmethod
    def format_http_request(method, url, headers, body=None):
        """Format HTTP request thành string"""
        parsed = urllib.parse.urlparse(url)
        path = parsed.path or '/'
        if parsed.query:
            path += '?' + parsed.query
        
        request_line = f"{method} {path} HTTP/1.1\r\n"
        header_lines = "\r\n".join(f"{k}: {v}" for k, v in headers.items())
        
        request = request_line + header_lines + "\r\n\r\n"
        if body:
            request += body
        
        return request


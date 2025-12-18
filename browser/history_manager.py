import os
import sqlite3
from datetime import datetime, timezone, timedelta

class HistoryManager:
    def __init__(self, db_path=None):
        if db_path is None:
            # lấy file MiniBrowser.db trong folder data cùng cấp với Browser
            project_root = os.path.dirname(os.path.dirname(__file__))  # lên 1 cấp từ Browser
            db_path = os.path.join(project_root, "data", "MiniBrowser.db")
        self.conn = sqlite3.connect(db_path)
        self.create_table()

    def create_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            url TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
        self.conn.execute(query)
        self.conn.commit()

    def add_entry(self, title, url):
        """Thêm 1 entry vào lịch sử"""
        query = "INSERT INTO history (title, url) VALUES (?, ?)"
        self.conn.execute(query, (title, url))
        self.conn.commit()

    def get_all(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, title, url, timestamp FROM history ORDER BY timestamp DESC")
        rows = cursor.fetchall()

        result = []
        for id_, title, url, ts in rows:
            dt_utc = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
            dt_local = dt_utc.astimezone()
            result.append((id_, title, url, dt_local))
        return result


    def delete_entry_by_id(self, entry_id):
        """Xóa 1 entry theo id"""
        self.conn.execute("DELETE FROM history WHERE id = ?", (entry_id,))
        self.conn.commit()

    def clear(self):
        """Xoá toàn bộ history"""
        self.conn.execute("DELETE FROM history")
        self.conn.commit()
    
    def search(self, keyword, limit=5):
        cursor = self.conn.cursor()
        query = """
        SELECT title, url
        FROM history
        WHERE title LIKE ? OR url LIKE ?
        GROUP BY url
        ORDER BY MAX(timestamp) DESC
        LIMIT ?
        """
        like = f"%{keyword}%"
        cursor.execute(query, (like, like, limit))
        return cursor.fetchall()



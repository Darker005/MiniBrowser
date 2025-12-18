import os
import sqlite3

class BookmarkManager:
    def __init__(self, db_path=None):
        if db_path is None:
            project_root = os.path.dirname(os.path.dirname(__file__))
            db_path = os.path.join(project_root, "data", "MiniBrowser.db")

        self.conn = sqlite3.connect(db_path)
        self.create_table()

    def create_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS bookmarks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            url TEXT NOT NULL UNIQUE
        )
        """
        self.conn.execute(query)
        self.conn.commit()

    # ------------------------------
    # CRUD FUNCTIONS
    # ------------------------------

    def add_bookmark(self, title, url):
        """Thêm bookmark (không thêm nếu trùng URL)"""
        if self.get_by_url(url) is not None:
            return False  # đã tồn tại, không thêm

        query = "INSERT INTO bookmarks (title, url) VALUES (?, ?)"
        self.conn.execute(query, (title, url))
        self.conn.commit()
        return True

    def delete_bookmark_by_id(self, bookmark_id):
        """Xoá bookmark theo ID"""
        query = "DELETE FROM bookmarks WHERE id = ?"
        self.conn.execute(query, (bookmark_id,))
        self.conn.commit()

    def delete_bookmark_by_url(self, url):
        """Xoá bookmark theo URL"""
        query = "DELETE FROM bookmarks WHERE url = ?"
        self.conn.execute(query, (url,))
        self.conn.commit()

    def list_bookmarks(self):
        """Lấy tất cả bookmark (id, title, url)"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, title, url FROM bookmarks ORDER BY id DESC")
        return cursor.fetchall()

    def get_by_url(self, url):
        """Lấy bookmark theo URL (để kiểm tra trùng)"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, title, url FROM bookmarks WHERE url = ?", (url,))
        return cursor.fetchone()

    def update_bookmark(self, bookmark_id, title, url):
        """Sửa bookmark"""
        query = "UPDATE bookmarks SET title = ?, url = ? WHERE id = ?"
        self.conn.execute(query, (title, url, bookmark_id))
        self.conn.commit()
    
    def search(self, keyword, limit=5):
        cursor = self.conn.cursor()
        query = """
        SELECT title, url FROM bookmarks
        WHERE title LIKE ? OR url LIKE ?
        ORDER BY
            CASE
                WHEN url LIKE ? THEN 0
                ELSE 1
            END
        LIMIT ?
        """
        like = f"%{keyword}%"
        cursor.execute(query, (like, like, like, limit))
        return cursor.fetchall()


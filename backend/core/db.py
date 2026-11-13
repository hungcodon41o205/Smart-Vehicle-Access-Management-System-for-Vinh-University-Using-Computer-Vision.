"""
File: backend/core/db.py
Module kết nối MySQL độc lập và chuẩn hóa cho toàn bộ Backend VinhGate.
Đọc cấu hình động từ .env thông qua config.py.
"""
import sys
from pathlib import Path

# Đảm bảo thư mục gốc dự án luôn nằm trong sys.path để import an toàn
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pymysql
from pymysql.cursors import DictCursor
from backend.core.config import DB_CONFIG

def get_connection():
    """Tạo và trả về đối tượng kết nối MySQL đến database cấu hình trong .env."""
    return pymysql.connect(
        **DB_CONFIG,
        cursorclass=DictCursor,
        autocommit=True
    )

if __name__ == "__main__":
    try:
        conn = get_connection()
        db_name = DB_CONFIG.get("database")
        print(f"✅ Kết nối MySQL thành công tới database '{db_name}'!")
        with conn.cursor() as cur:
            cur.execute("SELECT DATABASE() AS current_db, NOW() AS thoi_gian;")
            print("Kết quả:", cur.fetchone())
        conn.close()
    except Exception as e:
        print("❌ Lỗi kết nối:", e)

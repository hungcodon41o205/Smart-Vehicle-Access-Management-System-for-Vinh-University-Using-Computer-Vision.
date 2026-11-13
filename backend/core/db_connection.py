import sys
from pathlib import Path

# Đảm bảo thư mục gốc dự án luôn nằm trong sys.path để import an toàn
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pymysql
from pymysql.cursors import DictCursor
from backend.core.config import DATABASE_DIR, SQL_QUERIES_DIR
from backend.core.db import DB_CONFIG, get_connection

def get_db_connection(include_db: bool = True):
    """
    Tạo kết nối tới MySQL vinh_gate, trả về DictCursor.
    """
    if include_db:
        return get_connection()
    cfg = DB_CONFIG.copy()
    cfg.pop("database", None)
    return pymysql.connect(**cfg, cursorclass=DictCursor, autocommit=True)

def test_mysql_connection() -> dict:
    """
    Kiểm tra trạng thái kết nối tới MySQL mà KHÔNG can thiệp hay sửa đổi CSDL.
    """
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT DATABASE() AS cur_db, VERSION() AS ver, NOW() AS thoi_gian;")
            row = cursor.fetchone()
            cursor.execute("SHOW TABLES;")
            tables = [list(r.values())[0] for r in cursor.fetchall()]
        conn.close()
        return {
            "connected": True,
            "version": row.get("ver"),
            "current_database": row.get("cur_db"),
            "tables_count": len(tables),
            "tables": tables,
            "message": f"Kết nối MySQL thành công tới database '{row.get('cur_db')}' (MySQL {row.get('ver')})"
        }
    except Exception as e:
        return {
            "connected": False,
            "error": str(e),
            "host": DB_CONFIG.get("host"),
            "port": DB_CONFIG.get("port"),
            "user": DB_CONFIG.get("user"),
            "message": f"Chưa kết nối được MySQL: {e}"
        }

def load_sql_query(query_filename: str) -> str:
    """
    Đọc nội dung câu lệnh SQL từ thư mục `VinhGate/database/queries/<query_filename>`.
    """
    sql_path = SQL_QUERIES_DIR / query_filename
    if not sql_path.exists():
        raise FileNotFoundError(f"Không tìm thấy file SQL tại: {sql_path}")
    return sql_path.read_text(encoding="utf-8")

def execute_sql_script_file(script_filename: str):
    """
    Đọc và thực thi file kịch bản SQL khi cần.
    """
    script_path = DATABASE_DIR / script_filename
    if not script_path.exists():
        raise FileNotFoundError(f"Không tìm thấy file kịch bản SQL tại: {script_path}")
        
    sql_content = script_path.read_text(encoding="utf-8")
    conn = get_db_connection(include_db=False)
    try:
        with conn.cursor() as cursor:
            statements = [s.strip() for s in sql_content.split(";") if s.strip()]
            for stmt in statements:
                lines = [line for line in stmt.splitlines() if not line.strip().startswith("--")]
                clean_stmt = "\n".join(lines).strip()
                if clean_stmt:
                    cursor.execute(clean_stmt)
        print(f"[SQL SUCCESS] Đã thực thi thành công file: {script_path.name}")
    except Exception as e:
        print(f"[SQL ERROR] Lỗi khi chạy file {script_filename}: {e}")
        raise
    finally:
        conn.close()

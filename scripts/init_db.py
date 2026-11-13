#!/usr/bin/env python3
"""
Kịch bản khởi tạo Cơ sở dữ liệu cho hệ thống VinhGate.
Chạy file schema.sql (13 bảng Cách B) và seed_data.sql từ thư mục database/.
"""
import sys
from pathlib import Path

# Đảm bảo import được backend.core
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from backend.core.db_connection import execute_sql_script_file

def main():
    print("=" * 65)
    print("      VINHGATE - TIẾN TRÌNH KHỞI TẠO CƠ SỞ DỮ LIỆU MYSQL (13 BẢNG)")
    print("=" * 65)
    try:
        print("[1/2] Đang thực thi 'database/schema.sql' (Tạo Database & 13 Bảng)...")
        execute_sql_script_file("schema.sql")

        print("[2/2] Đang nạp 'database/seed_data.sql' (Dữ liệu mẫu Đại học Vinh)...")
        execute_sql_script_file("seed_data.sql")

        print("=" * 65)
        print(">>> KHỞI TẠO CƠ SỞ DỮ LIỆU THÀNH CÔNG VÀ SẴN SÀNG SỬ DỤNG! <<<")
        print("=" * 65)
    except Exception as e:
        print(f"\n[LỖI NGHIÊM TRỌNG]: Không thể khởi tạo CSDL: {e}")
        print("Gợi ý: Kiểm tra lại thông số DB_HOST, DB_USER, DB_PASSWORD trong file .env")
        sys.exit(1)

if __name__ == "__main__":
    main()

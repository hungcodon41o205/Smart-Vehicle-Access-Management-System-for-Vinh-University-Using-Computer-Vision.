import uuid
from datetime import datetime, timedelta
from backend.core.db_connection import get_db_connection

def generate_guest_code() -> str:
    """Tạo mã phiếu khách tạm thời theo chuẩn VG-YYYYMMDD-XXXX."""
    today_str = datetime.now().strftime("%Y%m%d")
    short_uuid = uuid.uuid4().hex[:4].upper()
    return f"VG-{today_str}-{short_uuid}"

def create_guest_ticket(
    ho_ten: str,
    bien_so: str,
    loai_xe: str,
    ma_the: str = None,
    so_dien_thoai: str = None,
    so_cccd: str = None,
    don_vi_cong_tac: str = None,
    ly_do_den: str = None,
    nguoi_tiep_don: str = None,
    tu_luc: datetime = None,
    den_luc: datetime = None,
    phi_gui_xe: float = 0.0,
    nguoi_tao_id: int = 1
) -> dict:
    """
    Tạo hoặc tái sử dụng thông tin Khách trong bảng KHACH,
    gán thẻ từ khách (nếu có) và sinh phiếu DANG_KY_KHACH (Cách B) để đối chiếu khi xe qua cổng.
    """
    if tu_luc is None:
        tu_luc = datetime.now()
    if den_luc is None:
        # Mặc định hiệu lực trong 8 tiếng
        den_luc = tu_luc + timedelta(hours=8)

    ma_tam = generate_guest_code()
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # 1. Tìm hoặc thêm khách vào bảng khach
            khach_id = None
            if so_cccd:
                cursor.execute("SELECT id FROM khach WHERE so_cccd = %s LIMIT 1", (so_cccd,))
                row = cursor.fetchone()
                if row:
                    khach_id = row["id"]
            if not khach_id and so_dien_thoai:
                cursor.execute("SELECT id FROM khach WHERE so_dien_thoai = %s LIMIT 1", (so_dien_thoai,))
                row = cursor.fetchone()
                if row:
                    khach_id = row["id"]

            if not khach_id:
                cursor.execute("""
                    INSERT INTO khach (ho_ten, so_dien_thoai, so_cccd, don_vi_cong_tac, ly_do_den, nguoi_tiep_don)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (ho_ten, so_dien_thoai, so_cccd, don_vi_cong_tac, ly_do_den, nguoi_tiep_don))
                khach_id = cursor.lastrowid
            else:
                cursor.execute("""
                    UPDATE khach 
                    SET ho_ten = %s, don_vi_cong_tac = COALESCE(%s, don_vi_cong_tac),
                        ly_do_den = COALESCE(%s, ly_do_den), nguoi_tiep_don = COALESCE(%s, nguoi_tiep_don)
                    WHERE id = %s
                """, (ho_ten, don_vi_cong_tac, ly_do_den, nguoi_tiep_don, khach_id))

            # 2. Xử lý thẻ từ mượn
            the_tu_id = None
            if ma_the:
                clean_card = ma_the.strip().upper()
                cursor.execute("SELECT id FROM the_tu WHERE ma_the = %s", (clean_card,))
                card_row = cursor.fetchone()
                if card_row:
                    the_tu_id = card_row["id"]
                    cursor.execute("UPDATE the_tu SET trang_thai = 'DANG_SU_DUNG' WHERE id = %s", (the_tu_id,))
                else:
                    cursor.execute("""
                        INSERT INTO the_tu (ma_the, loai_the, trang_thai, ngay_cap, ghi_chu)
                        VALUES (%s, 'KHACH', 'DANG_SU_DUNG', NOW(), 'Thẻ khách tạm thời')
                    """, (clean_card,))
                    the_tu_id = cursor.lastrowid

            # 3. Tạo phiếu đăng ký khách (dang_ky_khach)
            cursor.execute("""
                INSERT INTO dang_ky_khach (
                    khach_id, the_tu_id, bien_so, loai_xe, ma_tam, ly_do_den,
                    nguoi_tiep_don, tu_luc, den_luc, phi_gui_xe,
                    trang_thai, nguoi_tao_id
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'DANG_HIEU_LUC', %s)
            """, (
                khach_id, the_tu_id, bien_so.strip().upper(), loai_xe, ma_tam, ly_do_den,
                nguoi_tiep_don, tu_luc, den_luc, phi_gui_xe, nguoi_tao_id
            ))
            ticket_id = cursor.lastrowid
            conn.commit()

            return {
                "ticket_id": ticket_id,
                "khach_id": khach_id,
                "the_tu_id": the_tu_id,
                "ma_the": ma_the,
                "ma_tam": ma_tam,
                "bien_so": bien_so.strip().upper(),
                "loai_xe": loai_xe,
                "ho_ten": ho_ten,
                "tu_luc": tu_luc.strftime("%Y-%m-%d %H:%M:%S"),
                "den_luc": den_luc.strftime("%Y-%m-%d %H:%M:%S"),
                "trang_thai": "DANG_HIEU_LUC"
            }
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def list_guest_tickets(trang_thai: str = None, limit: int = 50):
    """Liệt kê danh sách các phiếu đăng ký khách gần đây kèm mã thẻ."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                SELECT dkk.id, dkk.ma_tam, dkk.bien_so, dkk.loai_xe, dkk.ly_do_den,
                       dkk.nguoi_tiep_don, dkk.tu_luc, dkk.den_luc, dkk.trang_thai,
                       dkk.phi_gui_xe, t.ma_the AS ma_the_muon,
                       k.ho_ten AS ten_khach, k.so_dien_thoai, k.don_vi_cong_tac
                FROM dang_ky_khach dkk
                LEFT JOIN khach k ON dkk.khach_id = k.id
                LEFT JOIN the_tu t ON dkk.the_tu_id = t.id
            """
            params = []
            if trang_thai:
                sql += " WHERE dkk.trang_thai = %s"
                params.append(trang_thai)
            sql += " ORDER BY dkk.id DESC LIMIT %s"
            params.append(limit)

            cursor.execute(sql, tuple(params))
            return cursor.fetchall()
    finally:
        conn.close()

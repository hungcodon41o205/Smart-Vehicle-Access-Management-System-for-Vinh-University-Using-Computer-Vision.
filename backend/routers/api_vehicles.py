from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from backend.core.db_connection import get_db_connection

router = APIRouter(prefix="/api/vehicles", tags=["Quản lý Phương tiện, Thẻ từ & Khách"])

class RegisterInternalVehicleRequest(BaseModel):
    ma_dinh_danh: str
    ho_ten: str
    loai_nguoi_dung: str = Field("SINH_VIEN", pattern="^(SINH_VIEN|GIANG_VIEN|CAN_BO)$")
    don_vi: Optional[str] = None
    so_dien_thoai: Optional[str] = None
    bien_so: str
    loai_xe: str = Field(..., pattern="^(XE_MAY|O_TO)$")
    nhan_hieu_mau: Optional[str] = None
    ma_the: Optional[str] = Field(None, description="Mã thẻ từ RFID gán cho xe (1 thẻ tối đa 3 xe)")

class AssignCardRequest(BaseModel):
    ma_the: str
    bien_so: str

class CreateCardRequest(BaseModel):
    ma_the: str
    loai_the: str = Field("NOI_BO", pattern="^(NOI_BO|KHACH)$")
    nguoi_dung_id: Optional[int] = None
    ghi_chu: Optional[str] = None

class GuestTicketRequest(BaseModel):
    ho_ten: str
    bien_so: str
    loai_xe: str = Field(..., pattern="^(XE_MAY|O_TO)$")
    ma_the: Optional[str] = None
    so_dien_thoai: Optional[str] = None
    so_cccd: Optional[str] = None
    don_vi_cong_tac: Optional[str] = None
    ly_do_den: Optional[str] = None
    nguoi_tiep_don: Optional[str] = None
    tu_luc: Optional[datetime] = None
    den_luc: Optional[datetime] = None
    phi_gui_xe: float = 0.0

class BlacklistRequest(BaseModel):
    bien_so: str
    ly_do: str
    muc_do: Optional[str] = "CANH_BAO"

# -------------------------------------------------------------
# 1. Quản lý Xe Nội Bộ
# -------------------------------------------------------------
@router.get("/internal")
def get_internal_vehicles(search: Optional[str] = None):
    """Lấy danh sách xe đã đăng ký kèm thông tin thẻ từ."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                SELECT pt.id, pt.bien_so, pt.loai_xe, pt.nhan_hieu, pt.mau_sac, pt.ngay_dang_ky, pt.trang_thai,
                       pt.the_tu_id, t.ma_the, t.trang_thai AS trang_thai_the,
                       nd.ma_dinh_danh, nd.ho_ten, nd.loai AS loai_nguoi_dung, nd.don_vi, nd.so_dien_thoai
                FROM phuong_tien pt
                JOIN nguoi_dung nd ON pt.nguoi_dung_id = nd.id
                LEFT JOIN the_tu t ON pt.the_tu_id = t.id
            """
            params = []
            if search:
                sql += " WHERE pt.bien_so LIKE %s OR nd.ho_ten LIKE %s OR nd.ma_dinh_danh LIKE %s OR t.ma_the LIKE %s"
                pattern = f"%{search}%"
                params.extend([pattern, pattern, pattern, pattern])
            sql += " ORDER BY pt.id DESC"
            cursor.execute(sql, tuple(params))
            return cursor.fetchall()
    finally:
        conn.close()

@router.post("/internal")
def register_internal_vehicle(req: RegisterInternalVehicleRequest):
    """Đăng ký mới xe nội bộ và gán thẻ từ (Ràng buộc tối đa 3 xe/thẻ)."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            clean_plate = req.bien_so.strip().upper()
            cursor.execute("SELECT id FROM phuong_tien WHERE bien_so = %s", (clean_plate,))
            if cursor.fetchone():
                raise HTTPException(status_code=400, detail="Biển số này đã được đăng ký trong hệ thống!")

            # 1. Tìm hoặc thêm người dùng
            cursor.execute("SELECT id FROM nguoi_dung WHERE ma_dinh_danh = %s", (req.ma_dinh_danh.strip(),))
            user_row = cursor.fetchone()
            if user_row:
                user_id = user_row["id"]
            else:
                cursor.execute("""
                    INSERT INTO nguoi_dung (ma_dinh_danh, ho_ten, loai, don_vi, so_dien_thoai, tao_luc)
                    VALUES (%s, %s, %s, %s, %s, NOW())
                """, (req.ma_dinh_danh.strip(), req.ho_ten.strip(), req.loai_nguoi_dung, req.don_vi, req.so_dien_thoai))
                user_id = cursor.lastrowid

            # 2. Xử lý thẻ từ (nếu có)
            the_tu_id = None
            if req.ma_the:
                clean_card = req.ma_the.strip().upper()
                cursor.execute("SELECT id, nguoi_dung_id FROM the_tu WHERE ma_the = %s", (clean_card,))
                card_row = cursor.fetchone()
                if card_row:
                    the_tu_id = card_row["id"]
                    # Kiểm tra số lượng xe hiện tại của thẻ này (RÀNG BUỘC TỐI ĐA 3 XE)
                    cursor.execute("SELECT COUNT(*) AS total FROM phuong_tien WHERE the_tu_id = %s", (the_tu_id,))
                    count_row = cursor.fetchone()
                    if count_row and count_row["total"] >= 3:
                        raise HTTPException(status_code=400, detail=f"Thẻ [{clean_card}] đã đăng ký đủ 3 xe (Tối đa 3 xe/thẻ)!")
                else:
                    # Tạo thẻ mới gán cho người dùng
                    cursor.execute("""
                        INSERT INTO the_tu (ma_the, loai_the, nguoi_dung_id, trang_thai, ngay_cap, ghi_chu)
                        VALUES (%s, 'NOI_BO', %s, 'SAN_SANG', NOW(), %s)
                    """, (clean_card, user_id, f"Thẻ của {req.ho_ten}"))
                    the_tu_id = cursor.lastrowid

            # 3. Tạo phương tiện
            cursor.execute("""
                INSERT INTO phuong_tien (nguoi_dung_id, the_tu_id, bien_so, loai_xe, nhan_hieu, ngay_dang_ky, trang_thai)
                VALUES (%s, %s, %s, %s, %s, CURDATE(), 'HOAT_DONG')
            """, (user_id, the_tu_id, clean_plate, req.loai_xe, req.nhan_hieu_mau or "Không rõ"))
            return {"success": True, "message": "Đăng ký xe và gán thẻ thành công", "the_tu_id": the_tu_id}
    finally:
        conn.close()

# -------------------------------------------------------------
# 2. Quản lý Kho Thẻ Từ (RFID Cards)
# -------------------------------------------------------------
@router.get("/cards")
def get_all_cards(loai_the: Optional[str] = None):
    """Liệt kê toàn bộ thẻ trong hệ thống kèm số xe gán."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                SELECT t.id, t.ma_the, t.loai_the, t.trang_thai, t.ngay_cap, t.ghi_chu,
                       nd.ho_ten AS chu_the, nd.ma_dinh_danh,
                       COUNT(pt.id) AS so_xe_da_gan,
                       GROUP_CONCAT(pt.bien_so SEPARATOR ', ') AS danh_sach_bien_so
                FROM the_tu t
                LEFT JOIN nguoi_dung nd ON t.nguoi_dung_id = nd.id
                LEFT JOIN phuong_tien pt ON pt.the_tu_id = t.id
            """
            params = []
            if loai_the:
                sql += " WHERE t.loai_the = %s"
                params.append(loai_the)
            sql += " GROUP BY t.id ORDER BY t.id ASC"
            cursor.execute(sql, tuple(params))
            return cursor.fetchall()
    finally:
        conn.close()

@router.post("/cards")
def create_card(req: CreateCardRequest):
    """Tạo mới một thẻ từ vào kho (Nội bộ hoặc Khách)."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            clean_card = req.ma_the.strip().upper()
            cursor.execute("SELECT id FROM the_tu WHERE ma_the = %s", (clean_card,))
            if cursor.fetchone():
                raise HTTPException(status_code=400, detail="Mã thẻ này đã tồn tại trong hệ thống!")

            cursor.execute("""
                INSERT INTO the_tu (ma_the, loai_the, nguoi_dung_id, trang_thai, ngay_cap, ghi_chu)
                VALUES (%s, %s, %s, 'SAN_SANG', NOW(), %s)
            """, (clean_card, req.loai_the, req.nguoi_dung_id, req.ghi_chu))
            return {"success": True, "message": f"Đã thêm thẻ [{clean_card}] thành công"}
    finally:
        conn.close()

@router.post("/cards/assign")
def assign_card_to_vehicle(req: AssignCardRequest):
    """Gán thẻ từ cho một biển số xe (Kiểm tra tối đa 3 xe/thẻ)."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            clean_card = req.ma_the.strip().upper()
            clean_plate = req.bien_so.strip().upper()

            cursor.execute("SELECT id, loai_the FROM the_tu WHERE ma_the = %s", (clean_card,))
            card = cursor.fetchone()
            if not card:
                raise HTTPException(status_code=404, detail="Không tìm thấy mã thẻ này!")

            cursor.execute("SELECT id FROM phuong_tien WHERE bien_so = %s", (clean_plate,))
            veh = cursor.fetchone()
            if not veh:
                raise HTTPException(status_code=404, detail="Không tìm thấy biển số xe này!")

            # Kiểm tra số lượng xe hiện tại gán vào thẻ này
            cursor.execute("SELECT COUNT(*) AS total FROM phuong_tien WHERE the_tu_id = %s", (card["id"],))
            total = cursor.fetchone()["total"]
            if total >= 3:
                raise HTTPException(status_code=400, detail=f"Thẻ [{clean_card}] đã gán đủ 3 xe (Tối đa 3 xe/thẻ)!")

            cursor.execute("UPDATE phuong_tien SET the_tu_id = %s WHERE id = %s", (card["id"], veh["id"]))
            return {"success": True, "message": f"Đã gán xe [{clean_plate}] vào thẻ [{clean_card}] (Xe thứ {total + 1}/3)"}
    finally:
        conn.close()

# -------------------------------------------------------------
# 3. Phiếu đăng ký khách & Danh sách đen
# -------------------------------------------------------------
@router.get("/guest-tickets")
def get_guest_tickets(trang_thai: Optional[str] = None):
    """Danh sách phiếu đăng ký khách kèm thông tin thẻ mượn."""
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
            sql += " ORDER BY dkk.id DESC LIMIT 50"
            cursor.execute(sql, tuple(params))
            return cursor.fetchall()
    finally:
        conn.close()

@router.post("/guest-tickets")
def post_guest_ticket(req: GuestTicketRequest):
    """Tạo phiếu đăng ký cho khách vãng lai (có thể gán thẻ từ tạm)."""
    from backend.services.guest_service import create_guest_ticket
    try:
        data = create_guest_ticket(
            ho_ten=req.ho_ten,
            bien_so=req.bien_so,
            loai_xe=req.loai_xe,
            ma_the=req.ma_the,
            so_dien_thoai=req.so_dien_thoai,
            so_cccd=req.so_cccd,
            don_vi_cong_tac=req.don_vi_cong_tac,
            ly_do_den=req.ly_do_den,
            nguoi_tiep_don=req.nguoi_tiep_don,
            tu_luc=req.tu_luc,
            den_luc=req.den_luc,
            phi_gui_xe=req.phi_gui_xe
        )
        return {"success": True, "data": data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/blacklist")
def get_blacklist():
    """Lấy danh sách các biển số bị chặn trong bảng danh_sach_den."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, bien_so, ly_do, muc_do, con_hieu_luc, them_luc FROM danh_sach_den ORDER BY id DESC")
            return cursor.fetchall()
    finally:
        conn.close()

@router.post("/blacklist")
def add_to_blacklist(req: BlacklistRequest):
    """Thêm một biển số vào danh sách đen."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO danh_sach_den (bien_so, ly_do, muc_do, con_hieu_luc, them_luc, them_boi)
                VALUES (%s, %s, %s, 1, NOW(), 1)
                ON DUPLICATE KEY UPDATE ly_do = VALUES(ly_do), con_hieu_luc = 1
            """, (req.bien_so.strip().upper(), req.ly_do, req.muc_do or 'CANH_BAO'))
            return {"success": True, "message": "Đã thêm vào danh sách đen"}
    finally:
        conn.close()

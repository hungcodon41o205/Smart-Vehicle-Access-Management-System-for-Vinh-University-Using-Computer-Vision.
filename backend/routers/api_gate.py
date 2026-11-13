from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List
from backend.services.gate_service import (
    process_vehicle_event,
    get_current_vehicles_in_campus,
    manual_confirm_entry,
    is_in_cooldown,
    get_available_guest_cards,
    get_card_info
)
from backend.core.db_connection import get_db_connection

router = APIRouter(prefix="/api/gate", tags=["Quản lý cổng, Thẻ từ & Lượt xe"])

class VehicleEventRequest(BaseModel):
    camera_id: int = 1
    huong: str = Field(..., pattern="^(VAO|RA)$")
    bien_so: str = Field(..., min_length=4, max_length=20)
    loai_xe: str = Field(..., pattern="^(XE_MAY|O_TO)$")
    do_tin_cay: float = Field(0.95, ge=0.0, le=1.0)
    ma_the: Optional[str] = Field(None, description="Mã thẻ từ RFID hoặc mã thẻ giả lập, VD: 1001, KH-01")
    thoi_gian_xu_ly_ms: int = 120
    toan_canh_path: Optional[str] = None
    bien_so_path: Optional[str] = None
    bypass_cooldown: bool = False

class ManualConfirmRequest(BaseModel):
    luot_id: int
    bien_so_xac_nhan: str
    ket_qua: str = Field(..., pattern="^(CHO_PHEP|TU_CHOI)$")
    ghi_chu: Optional[str] = None
    user_id: int = 1

@router.get("/counts")
def api_get_counts():
    """Lấy số lượng xe đang trong trường theo thời gian thực."""
    try:
        return get_current_vehicles_in_campus()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/lanes")
def api_get_lanes():
    """Lấy danh sách các camera và phân luồng làn (Nội bộ / Khách)."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT cam.id, cam.ten AS ten_camera, cam.huong, cam.loai_lan, cam.trang_thai,
                       c.ten AS ten_cong
                FROM camera cam
                JOIN cong c ON cam.cong_id = c.id
                ORDER BY cam.id ASC
            """)
            return cursor.fetchall()
    finally:
        conn.close()

@router.get("/guest-cards/available")
def api_get_available_guest_cards():
    """Lấy danh sách thẻ khách sẵn sàng để cấp cho khách tại cổng vào."""
    try:
        return get_available_guest_cards()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/card/{ma_the}")
def api_lookup_card(ma_the: str):
    """Tra cứu chi tiết thẻ từ: thông tin chủ thẻ, tối đa 3 biển số đăng ký."""
    card = get_card_info(ma_the.strip().upper())
    if not card:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy thẻ có mã [{ma_the}]")
    return card

@router.post("/event")
def api_post_vehicle_event(req: VehicleEventRequest):
    """
    Tiếp nhận sự kiện phương tiện qua cổng từ AI Module hoặc Web Simulation.
    Thực hiện đầy đủ pipeline kiểm tra CSDL kết hợp Thẻ từ định danh (2FA).
    """
    clean_bien_so = req.bien_so.strip().upper()
    clean_ma_the = req.ma_the.strip().upper() if req.ma_the else None
    
    if not req.bypass_cooldown and is_in_cooldown(clean_bien_so, req.huong, clean_ma_the):
        return {
            "success": False,
            "message": f"Biển số {clean_bien_so} vừa được ghi nhận, đang trong thời gian giãn cách (Debounce).",
            "is_cooldown": True
        }

    try:
        result = process_vehicle_event(
            camera_id=req.camera_id,
            huong=req.huong,
            bien_so_doc=clean_bien_so,
            loai_xe=req.loai_xe,
            do_tin_cay=req.do_tin_cay,
            thoi_gian_xu_ly_ms=req.thoi_gian_xu_ly_ms,
            toan_canh_path=req.toan_canh_path,
            bien_so_path=req.bien_so_path,
            ma_the=clean_ma_the
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi xử lý sự kiện cổng: {str(e)}")

@router.post("/manual-confirm")
def api_manual_confirm(req: ManualConfirmRequest):
    """Xác nhận hoặc hiệu chỉnh thủ công biển số và mở barie từ Dashboard."""
    try:
        ok = manual_confirm_entry(
            luot_id=req.luot_id,
            bien_so_xac_nhan=req.bien_so_xac_nhan.strip().upper(),
            ket_qua=req.ket_qua,
            user_id=req.user_id,
            ghi_chu=req.ghi_chu
        )
        if not ok:
            raise HTTPException(status_code=404, detail="Không tìm thấy lượt xe để xác nhận.")
        return {"success": True, "message": "Xác nhận thành công", "mo_barie": (req.ket_qua == "CHO_PHEP")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recent-logs")
def api_get_recent_logs(limit: int = Query(20, ge=1, le=100)):
    """Lấy danh sách các lượt ra vào gần đây kèm thông tin thẻ từ và đối chiếu."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT lrv.id, lrv.huong, lrv.bien_so_doc, lrv.bien_so_xac_nhan,
                       lrv.ma_the_quyet AS ma_the, t.loai_the,
                       lrv.loai_xe, lrv.do_tin_cay, lrv.thoi_gian,
                       lrv.ket_qua, lrv.ghi_chu,
                       c.ten AS ten_cong, cam.ten AS ten_camera, cam.loai_lan,
                       pt.id AS phuong_tien_id, nd.ho_ten AS chu_xe_noibo,
                       k.ho_ten AS ten_khach
                FROM luot_ra_vao lrv
                LEFT JOIN camera cam ON lrv.camera_id = cam.id
                LEFT JOIN cong c ON cam.cong_id = c.id
                LEFT JOIN the_tu t ON lrv.the_tu_id = t.id
                LEFT JOIN phuong_tien pt ON lrv.phuong_tien_id = pt.id
                LEFT JOIN nguoi_dung nd ON pt.nguoi_dung_id = nd.id
                LEFT JOIN dang_ky_khach dkk ON lrv.dang_ky_khach_id = dkk.id
                LEFT JOIN khach k ON dkk.khach_id = k.id
                ORDER BY lrv.id DESC
                LIMIT %s
            """, (limit,))
            rows = cursor.fetchall()
            return rows
    finally:
        conn.close()

@router.get("/alerts")
def api_get_alerts(unresolved_only: bool = True):
    """Lấy danh sách các cảnh báo an ninh, sai thẻ, trộm xe."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                SELECT id, luot_id, loai, muc_do, noi_dung, trang_thai, tao_luc
                FROM canh_bao
            """
            if unresolved_only:
                sql += " WHERE trang_thai = 'MOI'"
            sql += " ORDER BY id DESC LIMIT 50"
            cursor.execute(sql)
            return cursor.fetchall()
    finally:
        conn.close()

@router.post("/alerts/{alert_id}/resolve")
def api_resolve_alert(alert_id: int):
    """Đánh dấu một cảnh báo đã được xử lý."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("UPDATE canh_bao SET trang_thai = 'DA_XU_LY', xu_ly_luc = NOW() WHERE id = %s", (alert_id,))
            return {"success": True, "message": "Đã xử lý cảnh báo."}
    finally:
        conn.close()

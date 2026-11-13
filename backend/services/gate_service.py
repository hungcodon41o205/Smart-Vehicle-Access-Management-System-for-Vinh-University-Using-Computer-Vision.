import os
from datetime import datetime
from backend.core.config import MIN_CONFIDENCE_THRESHOLD, COOLDOWN_SECONDS
from backend.core.db_connection import get_db_connection

# Cache chống đọc trùng trong khoảng thời gian COOLDOWN_SECONDS
recent_detections = {}

def get_current_vehicles_in_campus() -> dict:
    """
    Đếm số xe đang trong trường theo thời gian thực:
    Đếm các lượt VÀO hợp lệ mà chưa có lượt RA tương ứng.
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    COUNT(*) AS tong_xe_trong_truong,
                    SUM(CASE WHEN v_in.loai_xe = 'XE_MAY' THEN 1 ELSE 0 END) AS so_xe_may,
                    SUM(CASE WHEN v_in.loai_xe = 'O_TO' THEN 1 ELSE 0 END) AS so_o_to
                FROM luot_ra_vao v_in
                LEFT JOIN luot_ra_vao v_out 
                    ON v_out.luot_vao_id = v_in.id AND v_out.huong = 'RA'
                WHERE v_in.huong = 'VAO'
                  AND v_in.ket_qua = 'CHO_PHEP'
                  AND v_out.id IS NULL;
            """)
            row = cursor.fetchone()
            return {
                "tong_xe_trong_truong": int(row["tong_xe_trong_truong"] or 0),
                "so_xe_may": int(row["so_xe_may"] or 0),
                "so_o_to": int(row["so_o_to"] or 0)
            }
    finally:
        conn.close()

def is_in_cooldown(bien_so: str, huong: str, ma_the: str = None) -> bool:
    """Kiểm tra debounce / cooldown tránh đọc trùng 1 xe liên tiếp trong COOLDOWN_SECONDS."""
    now = datetime.now().timestamp()
    key = f"{bien_so}_{huong}_{ma_the or ''}"
    last_time = recent_detections.get(key)
    if last_time and (now - last_time < COOLDOWN_SECONDS):
        return True
    recent_detections[key] = now
    return False

def get_available_guest_cards() -> list:
    """Lấy danh sách các thẻ khách rảnh (SẴN SÀNG) để chốt bảo vệ cấp cho khách."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id, ma_the, loai_the, trang_thai, ghi_chu
                FROM the_tu
                WHERE loai_the = 'KHACH' AND trang_thai = 'SAN_SANG'
                ORDER BY id ASC
            """)
            return cursor.fetchall()
    finally:
        conn.close()

def get_card_info(ma_the: str) -> dict:
    """Tra cứu chi tiết thẻ từ: Chủ thẻ, loại thẻ, danh sách biển số đã đăng ký."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT t.id, t.ma_the, t.loai_the, t.trang_thai, t.ngay_cap, t.ghi_chu,
                       nd.id AS nguoi_dung_id, nd.ma_dinh_danh, nd.ho_ten, nd.don_vi, nd.loai AS loai_nguoi_dung
                FROM the_tu t
                LEFT JOIN nguoi_dung nd ON t.nguoi_dung_id = nd.id
                WHERE t.ma_the = %s
                LIMIT 1
            """, (ma_the,))
            card = cursor.fetchone()
            if not card:
                return None

            # Lấy danh sách biển số xe gán với thẻ này (Tối đa 3 xe)
            cursor.execute("""
                SELECT id, bien_so, loai_xe, nhan_hieu, mau_sac, trang_thai
                FROM phuong_tien
                WHERE the_tu_id = %s
            """, (card["id"],))
            vehicles = cursor.fetchall()

            card["danh_sach_xe"] = vehicles
            card["so_xe_dang_ky"] = len(vehicles)
            return card
    finally:
        conn.close()

def process_vehicle_event(
    camera_id: int,
    huong: str,
    bien_so_doc: str,
    loai_xe: str,
    do_tin_cay: float,
    thoi_gian_xu_ly_ms: int = 0,
    toan_canh_path: str = None,
    bien_so_path: str = None,
    user_id: int = None,
    ma_the: str = None
) -> dict:
    """
    Xử lý trọn gói luồng nghiệp vụ 1 lượt xe qua cổng kết hợp Thẻ từ định danh (2FA):
    1. Kiểm tra danh sách đen (danh_sach_den) -> TỪ CHỐI
    2. Kiểm tra độ tin cậy AI
    3. Xác thực thẻ từ định danh & Phân luồng:
       a) Xe nội bộ: Khớp thẻ với 1 trong tối đa 3 biển số đăng ký + Kiểm tra Anti-passback
       b) Xe khách:
          - Chiều VÀO: Cấp/gán thẻ khách và lưu biển số
          - Chiều RA: So khớp biển số lúc vào với lúc ra gắn với mã thẻ (Chống trộm xe/tráo biển)
    4. Ghi nhận lượt ra vào, hình ảnh và cảnh báo
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            phuong_tien_id = None
            dang_ky_khach_id = None
            luot_vao_id = None
            the_tu_id = None
            ket_qua = "CHO_PHEP"
            canh_bao_info = None
            thong_tin_chu_xe = None
            anh_vao_so_sanh = None
            clean_ma_the = ma_the.strip().upper() if ma_the else None

            # Lấy thông tin Camera và Làn xe
            cursor.execute("SELECT id, ten, huong, loai_lan FROM camera WHERE id = %s LIMIT 1", (camera_id,))
            cam_row = cursor.fetchone() or {"ten": "Camera", "loai_lan": "HON_HOP"}
            loai_lan_cam = cam_row.get("loai_lan", "HON_HOP")

            # -------------------------------------------------------------
            # BƯỚC 1: KIỂM TRA DANH SÁCH ĐEN (BLACKLIST)
            # -------------------------------------------------------------
            cursor.execute(
                "SELECT id, bien_so, ly_do, muc_do FROM danh_sach_den WHERE bien_so = %s AND con_hieu_luc = 1 LIMIT 1",
                (bien_so_doc,)
            )
            black_row = cursor.fetchone()
            if black_row:
                ket_qua = "TU_CHOI"
                canh_bao_info = {
                    "loai": "DANH_SACH_DEN",
                    "muc_do": "KHAN_CAP",
                    "noi_dung": f"Biển số {bien_so_doc} trong DANH SÁCH ĐEN! Lý do: {black_row['ly_do']}"
                }

            # -------------------------------------------------------------
            # BƯỚC 2: KIỂM TRA ĐỘ TIN CẬY NHẬN DIỆN AI
            # -------------------------------------------------------------
            elif do_tin_cay < MIN_CONFIDENCE_THRESHOLD:
                ket_qua = "CHO_XAC_NHAN"
                canh_bao_info = {
                    "loai": "DO_TIN_CAY_THAP",
                    "muc_do": "TRUNG_BINH",
                    "noi_dung": f"Biển số {bien_so_doc} độ tin cậy thấp ({do_tin_cay:.2f} < {MIN_CONFIDENCE_THRESHOLD}). Cần xác nhận thủ công."
                }

            # -------------------------------------------------------------
            # BƯỚC 3: XÁC THỰC THẺ TỪ ĐỊNH DANH (2FA) & ĐỐI CHIẾU
            # -------------------------------------------------------------
            if ket_qua != "TU_CHOI":
                if clean_ma_the:
                    # Tra cứu thẻ trong bảng the_tu
                    cursor.execute("""
                        SELECT id, ma_the, loai_the, nguoi_dung_id, trang_thai
                        FROM the_tu
                        WHERE ma_the = %s
                        LIMIT 1
                    """, (clean_ma_the,))
                    the_row = cursor.fetchone()

                    if not the_row:
                        ket_qua = "TU_CHOI"
                        canh_bao_info = {
                            "loai": "THE_KHONG_KHOP_BIEN_SO",
                            "muc_do": "CAO",
                            "noi_dung": f"Mã thẻ [{clean_ma_the}] không tồn tại trong hệ thống VinhGate!"
                        }
                    elif the_row["trang_thai"] in ("KHOA", "DA_MAT"):
                        ket_qua = "TU_CHOI"
                        canh_bao_info = {
                            "loai": "THE_KHONG_KHOP_BIEN_SO",
                            "muc_do": "KHAN_CAP",
                            "noi_dung": f"Thẻ [{clean_ma_the}] đang ở trạng thái {the_row['trang_thai']} (Bị khóa hoặc Báo mất)!"
                        }
                    else:
                        the_tu_id = the_row["id"]
                        loai_the = the_row["loai_the"]

                        # -----------------------------------------------------
                        # 3.A: XE NỘI BỘ (CÁN BỘ / GIẢNG VIÊN / SINH VIÊN)
                        # -----------------------------------------------------
                        if loai_the == "NOI_BO":
                            if loai_lan_cam == "KHACH":
                                canh_bao_info = {
                                    "loai": "DI_SAI_LAN_QUY_DINH",
                                    "muc_do": "THAP",
                                    "noi_dung": f"Xe nội bộ ({clean_ma_the}) đang đi vào Làn dành riêng cho xe Khách."
                                }

                            # Lấy thông tin chủ thẻ và tất cả xe đăng ký (Tối đa 3 xe)
                            cursor.execute("""
                                SELECT pt.id, pt.bien_so, pt.loai_xe, pt.nhan_hieu, pt.mau_sac, pt.trang_thai,
                                       nd.id AS nd_id, nd.ho_ten, nd.ma_dinh_danh, nd.don_vi, nd.loai AS loai_nguoi_dung
                                FROM phuong_tien pt
                                JOIN nguoi_dung nd ON pt.nguoi_dung_id = nd.id
                                WHERE pt.the_tu_id = %s AND pt.trang_thai = 'HOAT_DONG'
                            """, (the_tu_id,))
                            pt_rows = cursor.fetchall()

                            danh_sach_bien_hop_le = [p["bien_so"] for p in pt_rows]

                            # Kiểm tra xem biển số AI nhận diện có khớp với 1 trong các xe của thẻ này không
                            matched_pt = next((p for p in pt_rows if p["bien_so"] == bien_so_doc), None)

                            if not matched_pt:
                                ket_qua = "TU_CHOI"
                                chu_the_ten = pt_rows[0]["ho_ten"] if pt_rows else "Chưa gán"
                                canh_bao_info = {
                                    "loai": "THE_KHONG_KHOP_BIEN_SO",
                                    "muc_do": "KHAN_CAP",
                                    "noi_dung": f"CẢNH BÁO LỆCH THẺ: Thẻ [{clean_ma_the}] (Chủ thẻ: {chu_the_ten}) đăng ký các biển: {danh_sach_bien_hop_le}, nhưng biển số camera chụp là [{bien_so_doc}]! Nghi vấn trộm xe!"
                                }
                            else:
                                phuong_tien_id = matched_pt["id"]
                                thong_tin_chu_xe = {
                                    "loai_doi_tuong": "NOI_BO",
                                    "ho_ten": matched_pt["ho_ten"],
                                    "ma_dinh_danh": matched_pt["ma_dinh_danh"],
                                    "don_vi": matched_pt["don_vi"],
                                    "ma_the": clean_ma_the,
                                    "danh_sach_xe_cua_the": danh_sach_bien_hop_le
                                }

                                # Kiểm tra quy tắc Anti-Passback (1 thẻ chỉ có 1 xe trong trường cùng lúc)
                                if huong == "VAO":
                                    cursor.execute("""
                                        SELECT v_in.id, v_in.bien_so_doc, v_in.thoi_gian
                                        FROM luot_ra_vao v_in
                                        LEFT JOIN luot_ra_vao v_out ON v_out.luot_vao_id = v_in.id AND v_out.huong = 'RA'
                                        WHERE v_in.the_tu_id = %s
                                          AND v_in.huong = 'VAO'
                                          AND v_in.ket_qua = 'CHO_PHEP'
                                          AND v_out.id IS NULL
                                        LIMIT 1
                                    """, (the_tu_id,))
                                    anti_row = cursor.fetchone()
                                    if anti_row:
                                        ket_qua = "TU_CHOI"
                                        canh_bao_info = {
                                            "loai": "THE_VI_PHAM_ANTI_PASSBACK",
                                            "muc_do": "CAO",
                                            "noi_dung": f"VI PHẠM ANTI-PASSBACK: Thẻ [{clean_ma_the}] đã có xe [{anti_row['bien_so_doc']}] đang trong bãi đỗ trường từ lúc {anti_row['thoi_gian']}!"
                                        }

                        # -----------------------------------------------------
                        # 3.B: XE KHÁCH VÃNG LAI (DÙNG THẺ TẠM XOAY VÒNG)
                        # -----------------------------------------------------
                        elif loai_the == "KHACH":
                            if loai_lan_cam == "NOI_BO":
                                canh_bao_info = {
                                    "loai": "DI_SAI_LAN_QUY_DINH",
                                    "muc_do": "THAP",
                                    "noi_dung": f"Xe Khách ({clean_ma_the}) đang đi vào Làn dành cho xe Nội bộ."
                                }

                            if huong == "VAO":
                                # Cấp thẻ khách cho biển số này
                                cursor.execute("""
                                    INSERT INTO dang_ky_khach (
                                        the_tu_id, bien_so, loai_xe, ma_tam, ly_do_den,
                                        tu_luc, den_luc, trang_thai, nguoi_tao_id
                                    ) VALUES (%s, %s, %s, %s, %s, NOW(), DATE_ADD(NOW(), INTERVAL 8 HOUR), 'DA_VAO', %s)
                                """, (
                                    the_tu_id, bien_so_doc, loai_xe,
                                    f"TICKET-{clean_ma_the}-{datetime.now().strftime('%Y%m%d%H%M')}",
                                    "Khách vãng lai qua cổng", user_id
                                ))
                                dang_ky_khach_id = cursor.lastrowid

                                # Đổi trạng thái thẻ sang ĐANG SỬ DỤNG
                                cursor.execute("UPDATE the_tu SET trang_thai = 'DANG_SU_DUNG' WHERE id = %s", (the_tu_id,))

                                thong_tin_chu_xe = {
                                    "loai_doi_tuong": "KHACH",
                                    "ho_ten": "Khách vãng lai",
                                    "ma_the": clean_ma_the,
                                    "trang_thai_the": "DANG_SU_DUNG"
                                }

                            elif huong == "RA":
                                # Khách trả thẻ lúc ra: Tìm lượt vào gắn với thẻ này
                                cursor.execute("""
                                    SELECT dkk.id, dkk.bien_so AS bien_so_vao, dkk.tu_luc, dkk.trang_thai
                                    FROM dang_ky_khach dkk
                                    WHERE dkk.the_tu_id = %s AND dkk.trang_thai IN ('DANG_HIEU_LUC', 'DA_VAO')
                                    ORDER BY dkk.id DESC LIMIT 1
                                """, (the_tu_id,))
                                dkk_row = cursor.fetchone()

                                if dkk_row:
                                    dang_ky_khach_id = dkk_row["id"]
                                    bien_so_vao = dkk_row["bien_so_vao"]

                                    # Tìm ảnh lúc VÀO để đối chiếu trực quan
                                    cursor.execute("""
                                        SELECT hal.duong_dan 
                                        FROM hinh_anh_luot hal
                                        JOIN luot_ra_vao lrv ON hal.luot_id = lrv.id
                                        WHERE lrv.dang_ky_khach_id = %s AND lrv.huong = 'VAO'
                                        ORDER BY hal.id DESC LIMIT 1
                                    """, (dang_ky_khach_id,))
                                    img_row = cursor.fetchone()
                                    if img_row:
                                        anh_vao_so_sanh = img_row["duong_dan"]

                                    # SO SÁNH BIỂN SỐ VÀO VÀ BIỂN SỐ RA
                                    if bien_so_doc != bien_so_vao:
                                        ket_qua = "TU_CHOI"
                                        canh_bao_info = {
                                            "loai": "THE_KHACH_LECH_BIEN_SO_RA_VAO",
                                            "muc_do": "KHAN_CAP",
                                            "noi_dung": f"CẢNH BÁO ĐỎ TRÁO BIỂN / TRỘM XE: Thẻ khách [{clean_ma_the}] lúc VÀO là biển [{bien_so_vao}], nhưng lúc RA là biển [{bien_so_doc}]! Giữ xe khẩn cấp!"
                                        }
                                    else:
                                        # Khớp biển số: Hoàn tất lượt khách, giải phóng thẻ về SẴN SÀNG
                                        cursor.execute("UPDATE dang_ky_khach SET trang_thai = 'DA_RA' WHERE id = %s", (dang_ky_khach_id,))
                                        cursor.execute("UPDATE the_tu SET trang_thai = 'SAN_SANG' WHERE id = %s", (the_tu_id,))
                                        thong_tin_chu_xe = {
                                            "loai_doi_tuong": "KHACH",
                                            "ho_ten": "Khách vãng lai (Đã trả thẻ)",
                                            "ma_the": clean_ma_the,
                                            "bien_so_vao": bien_so_vao
                                        }
                                else:
                                    ket_qua = "CHO_XAC_NHAN"
                                    canh_bao_info = {
                                        "loai": "LUOT_RA_KHONG_CO_VAO",
                                        "muc_do": "CAO",
                                        "noi_dung": f"Thẻ khách [{clean_ma_the}] quẹt ra nhưng không tìm thấy dữ liệu lượt VÀO tương ứng!"
                                    }

                else:
                    # TRƯỜNG HỢP: KHÔNG QUẸT THẺ (CHỈ CÓ CAMERA ĐỌC BIỂN SỐ)
                    cursor.execute("""
                        SELECT pt.id, pt.bien_so, pt.the_tu_id, t.ma_the, nd.ho_ten, nd.ma_dinh_danh, nd.don_vi
                        FROM phuong_tien pt
                        JOIN nguoi_dung nd ON pt.nguoi_dung_id = nd.id
                        LEFT JOIN the_tu t ON pt.the_tu_id = t.id
                        WHERE pt.bien_so = %s
                        LIMIT 1
                    """, (bien_so_doc,))
                    pt_no_card = cursor.fetchone()

                    if pt_no_card:
                        phuong_tien_id = pt_no_card["id"]
                        the_tu_id = pt_no_card["the_tu_id"]
                        ket_qua = "CHO_XAC_NHAN"
                        canh_bao_info = {
                            "loai": "THE_KHONG_KHOP_BIEN_SO",
                            "muc_do": "TRUNG_BINH",
                            "noi_dung": f"Xe nội bộ {bien_so_doc} (Chủ xe: {pt_no_card['ho_ten']}) CHƯA QUẸT THẺ TỪ! Cần bảo vệ kiểm tra thẻ xe."
                        }
                        thong_tin_chu_xe = {
                            "loai_doi_tuong": "NOI_BO",
                            "ho_ten": pt_no_card["ho_ten"],
                            "ma_dinh_danh": pt_no_card["ma_dinh_danh"],
                            "don_vi": pt_no_card["don_vi"],
                            "ma_the_yeu_cau": pt_no_card["ma_the"]
                        }
                    else:
                        ket_qua = "CHO_XAC_NHAN"
                        canh_bao_info = {
                            "loai": "XE_LA",
                            "muc_do": "TRUNG_BINH",
                            "noi_dung": f"Xe lạ {bien_so_doc} chưa đăng ký và chưa có thẻ từ. Bảo vệ cần cấp thẻ khách hoặc xử lý tay."
                        }

            # -------------------------------------------------------------
            # BƯỚC 4: NẾU LÀ CHIỀU RA, GHÉP NỐI LƯỢT VÀO
            # -------------------------------------------------------------
            if huong == "RA":
                cursor.execute("""
                    SELECT id FROM luot_ra_vao
                    WHERE (bien_so_doc = %s OR (the_tu_id IS NOT NULL AND the_tu_id = %s))
                      AND huong = 'VAO' AND ket_qua = 'CHO_PHEP'
                    ORDER BY id DESC LIMIT 1
                """, (bien_so_doc, the_tu_id))
                vao_row = cursor.fetchone()
                if vao_row:
                    luot_vao_id = vao_row["id"]
                else:
                    if not canh_bao_info and ket_qua == "CHO_PHEP":
                        canh_bao_info = {
                            "loai": "LUOT_RA_KHONG_CO_VAO",
                            "muc_do": "CAO",
                            "noi_dung": f"Xe {bien_so_doc} đi RA nhưng không tìm thấy dữ liệu lượt VÀO tương ứng!"
                        }

            # -------------------------------------------------------------
            # BƯỚC 5: GHI BẢN GHI VÀO LUOT_RA_VAO
            # -------------------------------------------------------------
            cursor.execute("""
                INSERT INTO luot_ra_vao (
                    camera_id, huong, thoi_gian, bien_so_doc, loai_xe, do_tin_cay,
                    ma_the_quyet, the_tu_id, phuong_tien_id, dang_ky_khach_id, luot_vao_id,
                    ket_qua, xac_nhan_boi
                ) VALUES (%s, %s, NOW(), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                camera_id, huong, bien_so_doc, loai_xe, do_tin_cay,
                clean_ma_the, the_tu_id, phuong_tien_id, dang_ky_khach_id, luot_vao_id,
                ket_qua, user_id
            ))
            luot_id = cursor.lastrowid

            # -------------------------------------------------------------
            # BƯỚC 6: GHI HÌNH ẢNH ĐÍNH KÈM
            # -------------------------------------------------------------
            if toan_canh_path:
                cursor.execute(
                    "INSERT INTO hinh_anh_luot (luot_id, loai, duong_dan) VALUES (%s, 'TOAN_CANH', %s)",
                    (luot_id, toan_canh_path)
                )
            if bien_so_path:
                cursor.execute(
                    "INSERT INTO hinh_anh_luot (luot_id, loai, duong_dan) VALUES (%s, 'BIEN_SO', %s)",
                    (luot_id, bien_so_path)
                )

            # -------------------------------------------------------------
            # BƯỚC 7: GHI CẢNH BÁO NẾU CÓ
            # -------------------------------------------------------------
            if canh_bao_info:
                cursor.execute("""
                    INSERT INTO canh_bao (luot_id, camera_id, loai, muc_do, noi_dung, trang_thai, tao_luc)
                    VALUES (%s, %s, %s, %s, %s, 'MOI', NOW())
                """, (
                    luot_id, camera_id, canh_bao_info["loai"],
                    canh_bao_info["muc_do"], canh_bao_info["noi_dung"]
                ))

            # Số xe cập nhật trong trường
            counts = get_current_vehicles_in_campus()

            return {
                "success": True,
                "luot_id": luot_id,
                "huong": huong,
                "bien_so": bien_so_doc,
                "ma_the": clean_ma_the,
                "loai_xe": loai_xe,
                "do_tin_cay": do_tin_cay,
                "ket_qua": ket_qua,
                "mo_barie": (ket_qua == "CHO_PHEP"),
                "thoi_gian_xu_ly_ms": thoi_gian_xu_ly_ms,
                "thong_tin_chu_xe": thong_tin_chu_xe,
                "anh_vao_so_sanh": anh_vao_so_sanh,
                "canh_bao": canh_bao_info,
                "counts": counts
            }
    finally:
        conn.close()

def manual_confirm_entry(luot_id: int, bien_so_xac_nhan: str, ket_qua: str, user_id: int = 1, ghi_chu: str = None) -> bool:
    """Xác nhận hoặc hiệu chỉnh thủ công biển số và mở barie từ màn hình Web."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                UPDATE luot_ra_vao
                SET bien_so_xac_nhan = %s,
                    ket_qua = %s,
                    xac_nhan_boi = %s,
                    ghi_chu = %s
                WHERE id = %s
            """, (bien_so_xac_nhan, ket_qua, user_id, ghi_chu, luot_id))
            return cursor.rowcount > 0
    finally:
        conn.close()

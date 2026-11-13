import io
from datetime import datetime, date
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from backend.core.db_connection import get_db_connection
from backend.services.gate_service import get_current_vehicles_in_campus
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment

router = APIRouter(prefix="/api/stats", tags=["Thống kê & Báo cáo"])

@router.get("/summary")
def get_stats_summary():
    """Tổng hợp số liệu từ VIEW v_thong_ke_hom_nay và v_xe_dang_trong_truong."""
    conn = get_db_connection()
    try:
        counts_inside = get_current_vehicles_in_campus()

        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM v_thong_ke_hom_nay LIMIT 1;")
            row = cursor.fetchone() or {}

            return {
                "ngay": str(row.get("ngay") or date.today()),
                "luot_vao_hom_nay": int(row.get("tong_vao_hop_le") or 0),
                "luot_ra_hom_nay": int(row.get("tong_ra_hop_le") or 0),
                "xe_trong_truong": counts_inside["tong_xe_trong_truong"],
                "xe_may_trong_truong": counts_inside["so_xe_may"],
                "o_to_trong_truong": counts_inside["so_o_to"],
                "canh_bao_chua_xu_ly": int(row.get("tong_canh_bao") or 0)
            }
    finally:
        conn.close()

@router.get("/hourly-traffic")
def get_hourly_traffic():
    """Lấy dữ liệu lưu lượng xe theo 24 giờ trong ngày để vẽ biểu đồ Chart.js."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT HOUR(thoi_gian) AS gio,
                       SUM(CASE WHEN huong = 'VAO' THEN 1 ELSE 0 END) AS vao,
                       SUM(CASE WHEN huong = 'RA' THEN 1 ELSE 0 END) AS ra
                FROM luot_ra_vao
                WHERE DATE(thoi_gian) = CURDATE()
                GROUP BY HOUR(thoi_gian)
                ORDER BY gio ASC
            """)
            rows = cursor.fetchall()

            hourly_data = {h: {"vao": 0, "ra": 0} for h in range(24)}
            for r in rows:
                h = int(r["gio"])
                hourly_data[h]["vao"] = int(r["vao"])
                hourly_data[h]["ra"] = int(r["ra"])

            return {
                "labels": [f"{h:02d}:00" for h in range(24)],
                "vao": [hourly_data[h]["vao"] for h in range(24)],
                "ra": [hourly_data[h]["ra"] for h in range(24)]
            }
    finally:
        conn.close()

@router.get("/export-excel")
def export_history_excel():
    """Xuất báo cáo lịch sử lượt ra vào ra file Excel (.xlsx)."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT lrv.id, lrv.huong, lrv.bien_so_doc, lrv.bien_so_xac_nhan,
                       lrv.loai_xe, lrv.do_tin_cay, lrv.thoi_gian,
                       lrv.ket_qua, lrv.ghi_chu,
                       c.ten AS ten_cong, cam.ten AS ten_camera,
                       COALESCE(nd.ho_ten, k.ho_ten, 'Chưa xác định') AS ten_nguoi_di
                FROM luot_ra_vao lrv
                LEFT JOIN camera cam ON lrv.camera_id = cam.id
                LEFT JOIN cong c ON cam.cong_id = c.id
                LEFT JOIN phuong_tien pt ON lrv.phuong_tien_id = pt.id
                LEFT JOIN nguoi_dung nd ON pt.nguoi_dung_id = nd.id
                LEFT JOIN khach k ON lrv.khach_id = k.id
                ORDER BY lrv.id DESC
                LIMIT 500
            """)
            records = cursor.fetchall()

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Nhat_Ky_Ra_Vao"

        headers = [
            "Mã Lượt", "Thời Gian", "Hướng", "Biển Số Đọc", "Biển Số Xác Nhận",
            "Loại Xe", "Độ Tin Cậy", "Kết Quả", "Chủ Xe / Người Đi", "Cổng"
        ]
        ws.append(headers)

        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="1F497D", end_color="1F497D", fill_type="solid")
        for col_idx in range(1, len(headers) + 1):
            cell = ws.cell(row=1, column=col_idx)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal="center", vertical="center")

        for r in records:
            ws.append([
                r["id"],
                str(r["thoi_gian"]),
                r["huong"],
                r["bien_so_doc"],
                r["bien_so_xac_nhan"] or "",
                r["loai_xe"],
                f"{r['do_tin_cay']:.2f}",
                r["ket_qua"],
                r["ten_nguoi_di"],
                r["ten_cong"]
            ])

        for col in ws.columns:
            max_len = max(len(str(cell.value or "")) for cell in col)
            col_letter = openpyxl.utils.get_column_letter(col[0].column)
            ws.column_dimensions[col_letter].width = max(max_len + 3, 12)

        file_stream = io.BytesIO()
        wb.save(file_stream)
        file_stream.seek(0)

        filename = f"VinhGate_Bao_Cao_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        return StreamingResponse(
            file_stream,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    finally:
        conn.close()

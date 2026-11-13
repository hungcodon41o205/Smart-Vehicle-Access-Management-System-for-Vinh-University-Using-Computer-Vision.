"""
==============================================================================
MODULE: XỬ LÝ VIDEO VÀ NHẬN DIỆN LƯỢT XE CỔNG TRƯỜNG (XU LY VIDEO)
File: XuLyVideo.py
Dự án: VinhGate 2.0 (Hệ thống Quản lý Xe Ra Vào Đại học Vinh)
==============================================================================
Quy trình nghiệp vụ:
    1. Đọc luồng video từ file (.mp4) hoặc camera cổng trường.
    2. Sử dụng YOLOv8 phát hiện phương tiện và khung biển số xe.
    3. Tiền xử lý ảnh (ai.TienXuLy) và nhận dạng ký tự bằng PaddleOCR (ai.ChuanHoaBienSo).
    4. Gom nhóm frame theo thời gian thực (Session Tracking):
       - Các frame xuất hiện liên tục trong khoảng thời gian <= 1.2 giây được tự động
         gom thành 1 LƯỢT XE DUY NHẤT.
    5. Thuật toán Bình chọn Đa số (Majority Voting) & Tính điểm chất lượng:
       - Bỏ phiếu mã tỉnh (VD: 37 Nghệ An).
       - Ưu tiên frame ở gần camera nhất (diện tích bounding box lớn, chữ số rõ nét).
       - Khử triệt để lỗi 1 xe xuất hiện 4 biển số khác nhau.
    6. Lưu đúng 1 ảnh cắt biển số rõ nét nhất của mỗi xe vào 'data/detected_plates/'
       và xuất danh sách kết quả tinh gọn ra file CSV chuẩn UTF-8 BOM.
    7. KHÔNG VẼ HUD, KHÔNG DÙNG DEBOUNCE TẠM CŨ ĐỂ TỐI ƯU HIỆU NĂNG SUY LUẬN.
==============================================================================
"""

import sys
import os
import re
import csv
import time
from pathlib import Path
import cv2

# Đảm bảo in tiếng Việt có dấu
if hasattr(sys.stdout, "reconfigure"):
    getattr(sys.stdout, "reconfigure")(encoding="utf-8", errors="replace")

# Thêm đường dẫn gốc vào sys.path
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from ai.PhatHienBienSo import PhatHienBienSo
from ai.ChuanHoaBienSo import doc_bien_so_viet_nam


def tinh_diem_chat_luong_bien_so(ung_vien: dict) -> float:
    """
    Tính điểm chất lượng biển số của từng frame để chọn ra frame tối ưu nhất:
    - Ưu tiên biển có đủ 8-9 ký tự chuẩn Việt Nam.
    - Ưu tiên mã tỉnh 2 số hợp lệ (11-99).
    - Kết hợp độ tin cậy OCR và độ tin cậy phát hiện của YOLO.
    """
    bien_so = ung_vien["plate"]
    ocr_conf = ung_vien["ocr_conf"]
    yolo_conf = ung_vien["conf"]

    clean = re.sub(r'[^A-Z0-9]', '', bien_so)

    # Điểm độ dài: Biển số VN chuẩn có 7-9 ký tự
    diem_do_dai = 0.0
    if len(clean) in (8, 9):
        diem_do_dai = 0.5
    elif len(clean) == 7:
        diem_do_dai = 0.25

    # Điểm mã tỉnh: 2 ký tự đầu là số hợp lệ (11-99)
    diem_ma_tinh = 0.0
    if len(clean) >= 2 and clean[:2].isdigit():
        ma_so = int(clean[:2])
        if 11 <= ma_so <= 99:
            diem_ma_tinh = 0.3

    # Ưu tiên có ký tự sê-ri chữ cái ở vị trí thứ 3
    diem_seri = 0.0
    if len(clean) >= 3 and clean[2].isalpha():
        diem_seri = 0.2

    return (ocr_conf * 0.4) + (yolo_conf * 0.2) + diem_do_dai + diem_ma_tinh + diem_seri


def chon_ung_vien_xuat_sac_nhat(danh_sach_session: list) -> dict:
    """
    Thuật toán Bình chọn đa số (Majority Voting) chọn ra kết quả chuẩn nhất cho 1 lượt xe:
    - Thống kê tần suất xuất hiện của mã tỉnh và chuỗi biển số.
    - Ưu tiên frame gần camera nhất (diện tích bounding box lớn, chữ rõ nét).
    - Ưu tiên chuỗi có cấu trúc chuẩn sê-ri 2 ký tự (như AB, AN, K1, B2...).
    """
    dem_ma_tinh = {}
    dem_bien_so = {}
    for c in danh_sach_session:
        p = c["plate"]
        dem_bien_so[p] = dem_bien_so.get(p, 0) + 1
        clean = re.sub(r'[^A-Z0-9]', '', p)
        if len(clean) >= 2 and clean[:2].isdigit():
            pr = clean[:2]
            dem_ma_tinh[pr] = dem_ma_tinh.get(pr, 0) + 1

    ma_tinh_pho_bien = max(dem_ma_tinh, key=dem_ma_tinh.get) if dem_ma_tinh else None
    dien_tich_lon_nhat = max(c["area"] for c in danh_sach_session) if danh_sach_session else 1

    def tinh_tong_diem(c):
        score = c["quality_score"]
        clean = re.sub(r'[^A-Z0-9]', '', c["plate"])

        # Thưởng nếu trùng mã tỉnh xuất hiện đa số
        if ma_tinh_pho_bien and clean.startswith(ma_tinh_pho_bien):
            score += 1.0

        # Thưởng nếu biển xuất hiện lặp lại nhiều lần
        so_lan_xuat_hien = dem_bien_so.get(c["plate"], 1)
        score += min(so_lan_xuat_hien * 0.2, 0.6)

        # Thưởng nếu ảnh chụp ở gần camera (diện tích to, nét chữ rõ)
        ti_le_dien_tich = c["area"] / dien_tich_lon_nhat
        score += ti_le_dien_tich * 0.5

        # Thưởng nếu có dấu gạch nối và cấu trúc chuẩn
        if "-" in c["plate"]:
            parts = c["plate"].split("-")
            if len(parts) == 2:
                dau, duoi = parts[0], parts[1]
                if len(dau) in (3, 4) and dau[2].isalpha():
                    score += 0.5
                if len(duoi) in (4, 5):
                    score += 0.3

        return score

    return max(danh_sach_session, key=tinh_tong_diem)


def xu_ly_video_nhan_dien_bien_so(
    duong_dan_video: str,
    file_xuat_csv: str = "data/danh_sach_bien_so.csv",
    thu_muc_luu_anh: str = "data/detected_plates",
    nguong_tin_cay_yolo: float = 0.30,
    buoc_nhay_frame: int = 2,
    khoang_cach_xe_s: float = 1.2
):
    """
    Tiến trình đọc và xử lý toàn bộ video.
    """
    file_vid = Path(duong_dan_video)
    if not file_vid.exists():
        print(f"[LỖI] Không tìm thấy file video: {duong_dan_video}")
        return

    thu_muc_anh = Path(thu_muc_luu_anh)
    thu_muc_anh.mkdir(parents=True, exist_ok=True)
    Path(file_xuat_csv).parent.mkdir(parents=True, exist_ok=True)

    print("=" * 75)
    print("  VINHGATE 2.0 - TIẾN TRÌNH XỬ LÝ VIDEO NHẬN DIỆN BIỂN SỐ")
    print("=" * 75)
    print(f"[*] File video nguồn     : {duong_dan_video}")
    print(f"[*] Thư mục lưu ảnh cắt  : {thu_muc_luu_anh}")
    print(f"[*] File CSV tổng hợp    : {file_xuat_csv}")
    print(f"[*] Ngưỡng YOLO & Bước   : conf={nguong_tin_cay_yolo} | Bước nhảy={buoc_nhay_frame} frames")
    print("-" * 75)

    detector = PhatHienBienSo()
    if detector.model is None:
        print("[LỖI] Chưa tải được mô hình YOLOv8! Vui lòng kiểm tra models/best.pt")
        return

    cap = cv2.VideoCapture(str(file_vid))
    if not cap.isOpened():
        print(f"[LỖI] Không thể mở file video: {duong_dan_video}")
        return

    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    tong_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    thoi_luong = tong_frames / fps

    print(f"[*] Độ phân giải: {width}x{height} | FPS: {fps:.2f} | Tổng {tong_frames} frames (~{thoi_luong:.1f}s)")

    cac_luot_xe = []
    session_hien_tai = []
    thoi_gian_xe_truoc = -999.0

    frame_idx = 0
    start_time = time.time()

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        thoi_diem_giay = frame_idx / fps

        if frame_idx % buoc_nhay_frame == 0:
            results = detector.model(frame, conf=nguong_tin_cay_yolo, verbose=False)

            for r in results:
                for box in r.boxes:
                    conf = float(box.conf[0])
                    xyxy = box.xyxy[0].cpu().numpy().astype(int)

                    pad = 4
                    x1 = max(0, xyxy[0] - pad)
                    y1 = max(0, xyxy[1] - pad)
                    x2 = min(width, xyxy[2] + pad)
                    y2 = min(height, xyxy[3] + pad)

                    w_box = x2 - x1
                    h_box = y2 - y1
                    if w_box < 15 or h_box < 15:
                        continue

                    crop = frame[y1:y2, x1:x2]
                    aspect_ratio = float(w_box) / float(h_box)

                    # Tiền xử lý ảnh và đọc OCR bằng PaddleOCR
                    plate_text, ocr_conf = doc_bien_so_viet_nam(
                        crop,
                        su_dung_tien_xu_ly=True,
                        ti_le_khung_hinh=aspect_ratio
                    )

                    if plate_text and len(plate_text) >= 5:
                        # Phân loại phương tiện
                        loai_xe = "Xe Máy" if (aspect_ratio < 2.0 or (len(plate_text.split("-")[0]) >= 4 if "-" in plate_text else False)) else "Ô Tô"

                        ung_vien = {
                            "sec": thoi_diem_giay,
                            "time_str": f"{int(thoi_diem_giay // 60):02d}:{thoi_diem_giay % 60:05.2f}",
                            "plate": plate_text,
                            "loai_xe": loai_xe,
                            "conf": conf,
                            "ocr_conf": ocr_conf,
                            "area": w_box * h_box,
                            "crop": crop
                        }
                        ung_vien["quality_score"] = tinh_diem_chat_luong_bien_so(ung_vien)

                        # Gom nhóm theo khoảng cách thời gian (Session Tracker)
                        if (thoi_diem_giay - thoi_gian_xe_truoc) > khoang_cach_xe_s:
                            if session_hien_tai:
                                cac_luot_xe.append(session_hien_tai)
                            session_hien_tai = [ung_vien]
                        else:
                            session_hien_tai.append(ung_vien)

                        thoi_gian_xe_truoc = thoi_diem_giay

        frame_idx += 1

    cap.release()
    if session_hien_tai:
        cac_luot_xe.append(session_hien_tai)

    # Chọn ra 1 kết quả chuẩn xác nhất cho từng lượt xe
    danh_sach_xe_chot = []
    for idx, session in enumerate(cac_luot_xe, 1):
        if not session:
            continue
        best = chon_ung_vien_xuat_sac_nhat(session)

        bien_sach = best["plate"]
        ten_file_anh = f"bien_so_{idx:02d}_{bien_sach.replace('-', '_')}.jpg"
        duong_dan_anh = thu_muc_anh / ten_file_anh
        cv2.imwrite(str(duong_dan_anh), best["crop"])

        danh_sach_xe_chot.append({
            "stt": idx,
            "bien_so": bien_sach,
            "loai_xe": best["loai_xe"],
            "thoi_gian": best["time_str"],
            "file_anh": f"{thu_muc_luu_anh}/{ten_file_anh}",
            "so_lan_quet": len(session),
            "do_tin_cay": f"{best['ocr_conf']:.1%}"
        })

    # Ghi ra file CSV chuẩn UTF-8 có BOM
    with open(file_xuat_csv, mode="w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["STT", "Biển Số Nhận Diện", "Loại Xe", "Thời Gian Video", "Số Lần Quét", "Độ Tin Cậy", "File Ảnh Biển Số"])
        for v in danh_sach_xe_chot:
            writer.writerow([v["stt"], v["bien_so"], v["loai_xe"], v["thoi_gian"], v["so_lan_quet"], v["do_tin_cay"], v["file_anh"]])

    tong_tg = time.time() - start_time
    print("=" * 75)
    print(f"[HOÀN TẤT] Đã xử lý xong {tong_frames} frames trong {tong_tg:.1f}s (~{tong_frames/tong_tg:.1f} FPS).")
    print(f"[KẾT QUẢ] Đã phát hiện {len(danh_sach_xe_chot)} lượt phương tiện đi qua cổng:")
    for v in danh_sach_xe_chot:
        print(f"  + Lượt #{v['stt']:02d}: Biển {v['bien_so']:<13} | {v['loai_xe']:<7} | Lúc: {v['thoi_gian']} | Tin cậy: {v['do_tin_cay']}")
    print(f"[XUẤT BẢNG] Đã lưu file kết quả tại: {file_xuat_csv}")
    print("=" * 75)
    return danh_sach_xe_chot


if __name__ == "__main__":
    video_input = sys.argv[1] if len(sys.argv) > 1 else "data/raw_videos/sample_test.mp4"
    xu_ly_video_nhan_dien_bien_so(video_input)

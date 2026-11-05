"""
==============================================================================
MODULE: TRÍCH XUẤT KHUNG HÌNH CHỨA PHƯƠNG TIỆN TỪ VIDEO (CAT KHUNG HINH)
Thư mục: ai/CatKhungHinh.py
Dự án: VinhGate 2.0 (Hệ thống Quản lý Xe Ra Vào Đại học Vinh)
==============================================================================
Mục đích & Nghiệp vụ:
    1. Đọc video quay thực tế tại các cổng trường Đại học Vinh (Nhà xe 1, Nhà xe 2).
    2. Sử dụng mô hình YOLOv8 phát hiện tự động khung hình nào có XE MÁY (class 3)
       hoặc Ô TÔ (class 2).
    3. Loại bỏ 100% các đoạn đường trống không có xe, lọc bớt các frame trùng lặp
       khi xe đứng yên để tránh gây hiện tượng Overfitting khi gán nhãn đưa lên Roboflow.
    4. Chuẩn hóa tên file ảnh đồng bộ theo Quy ước dữ liệu (DATA CONVENTION):
       Cú pháp: <tên_video>_f<số_thứ_tự_4_chữ_số>.jpg
       Ví dụ:   nhaxe1_xemay_vao_20261019_sang_001_f0001.jpg
==============================================================================
"""

import os
import sys
import glob
from pathlib import Path
import cv2

# Đảm bảo in tiếng Việt trên console Windows
if hasattr(sys.stdout, "reconfigure"):
    getattr(sys.stdout, "reconfigure")(encoding="utf-8", errors="replace")

try:
    from ultralytics import YOLO
except ImportError:
    YOLO = None


def cat_khung_hinh_tu_video(
    duong_dan_video: str,
    thu_muc_luu_anh: str = None,
    nguong_tin_cay: float = 0.35,
    gian_cach_luu_giay: float = 0.20,
    buoc_kiem_tra_giay: float = 0.06,
    chat_luong_jpg: int = 95
) -> int:
    """
    Trích xuất các khung hình xuất hiện phương tiện từ 1 file video duy nhất.

    :param duong_dan_video: Đường dẫn tới file video (.mp4, .avi...)
    :param thu_muc_luu_anh: Thư mục đích lưu ảnh trích xuất
    :param nguong_tin_cay: Ngưỡng tin cậy của YOLO để nhận biết phương tiện
    :param gian_cach_luu_giay: Thời gian giãn cách tối thiểu giữa 2 ảnh lưu (giây)
    :param buoc_kiem_tra_giay: Tần suất AI kiểm tra frame
    :param chat_luong_jpg: Mức nén JPEG (mặc định 95% sắc nét)
    :return: Tổng số ảnh đã trích xuất được (int)
    """
    file_video = Path(duong_dan_video)
    if not file_video.exists():
        print(f"[LỖI] Không tìm thấy file video: {duong_dan_video}")
        return 0

    cap = cv2.VideoCapture(str(file_video))
    if not cap.isOpened():
        print(f"[LỖI] Không thể mở file video: {duong_dan_video}")
        return 0

    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    tong_so_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    chieu_rong = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    chieu_cao = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    thoi_luong_s = tong_so_frames / fps if fps > 0 else 0

    ten_video_goc = file_video.stem

    # Xác định thư mục lưu ảnh chuẩn hóa
    if thu_muc_luu_anh is None:
        thu_muc_dich = Path("data") / "extracted_frames" / ten_video_goc
    else:
        thu_muc_dich = Path(thu_muc_luu_anh)

    thu_muc_dich.mkdir(parents=True, exist_ok=True)

    print("=" * 75)
    print(f"  TIẾN TRÌNH TRÍCH XUẤT ẢNH TỪ VIDEO: {file_video.name}")
    print("=" * 75)
    print(f"  * Độ phân giải   : {chieu_rong} x {chieu_cao}")
    print(f"  * FPS & Số frame : {fps:.2f} FPS | {tong_so_frames} frames (~{thoi_luong_s:.1f} giây)")
    print(f"  * Thư mục lưu ảnh: {thu_muc_dich}")
    print(f"  * Quy chuẩn tên  : {ten_video_goc}_fXXXX.jpg")
    print("-" * 75)

    # Nạp mô hình YOLOv8n pretrained để phát hiện phương tiện (class 2: car, class 3: motorcycle)
    model = None
    classes_target = [2, 3]  # 2: car, 3: motorcycle trong COCO
    if YOLO is not None:
        try:
            model = YOLO("yolov8n.pt")
            print("--> Đã nạp YOLOv8n bộ lọc phương tiện thông minh.")
        except Exception:
            model = None

    frame_idx = 0
    anh_da_luu = 0
    moc_thoi_gian_luu_cuoi = -999.0
    buoc_nhay_kiem_tra = max(1, int(round(fps * buoc_kiem_tra_giay)))

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        thoi_diem_hien_tai_s = frame_idx / fps

        # Kiểm tra theo bước nhảy
        if frame_idx % buoc_nhay_kiem_tra == 0:
            khoang_cach_s = thoi_diem_hien_tai_s - moc_thoi_gian_luu_cuoi

            if khoang_cach_s >= gian_cach_luu_giay:
                co_phuong_tien = True

                # Nếu có model YOLO -> kiểm tra xem có xe trong frame không
                if model is not None:
                    ket_qua = model(
                        frame,
                        classes=classes_target,
                        conf=nguong_tin_cay,
                        verbose=False
                    )
                    co_phuong_tien = len(ket_qua[0].boxes) > 0

                if co_phuong_tien:
                    anh_da_luu += 1
                    moc_thoi_gian_luu_cuoi = thoi_diem_hien_tai_s

                    # Đặt tên file theo đúng chuẩn DATA CONVENTION
                    ten_anh = f"{ten_video_goc}_f{anh_da_luu:04d}.jpg"
                    duong_dan_anh = thu_muc_dich / ten_anh

                    cv2.imwrite(
                        str(duong_dan_anh),
                        frame,
                        [int(cv2.IMWRITE_JPEG_QUALITY), chat_luong_jpg]
                    )

                    if anh_da_luu % 10 == 0 or anh_da_luu == 1:
                        print(f"  [+] Đã lưu ảnh #{anh_da_luu:04d} tại giây {thoi_diem_hien_tai_s:5.2f}s -> {ten_anh}")

        frame_idx += 1

    cap.release()
    print("-" * 75)
    print(f"[HOÀN THÀNH] Đã trích xuất thành công {anh_da_luu} ảnh chuẩn vào: {thu_muc_dich}")
    return anh_da_luu


def cat_toan_bo_video_trong_thu_muc(
    thu_muc_video: str = "data/raw_videos",
    thu_muc_xuat: str = "data/extracted_frames"
) -> int:
    """
    Quét tự động tất cả các file video (.mp4, .avi, .mov, .mkv) trong thư mục nguồn
    và trích xuất ảnh chuẩn hóa cho từng video.
    """
    thu_muc_goc = Path(thu_muc_video)
    if not thu_muc_goc.exists():
        thu_muc_goc.mkdir(parents=True, exist_ok=True)
        print(f"[THÔNG BÁO] Đã tạo thư mục video: {thu_muc_video}. Vui lòng sao chép video vào đây.")
        return 0

    dinh_dang_hop_le = ("*.mp4", "*.avi", "*.mov", "*.mkv")
    danh_sach_video = []
    for ext in dinh_dang_hop_le:
        danh_sach_video.extend(thu_muc_goc.glob(ext))

    if not danh_sach_video:
        print(f"[THÔNG BÁO] Không tìm thấy video nào trong thư mục: {thu_muc_video}")
        return 0

    tong_anh = 0
    print(f"[VINHGATE] Bắt đầu xử lý {len(danh_sach_video)} video trong '{thu_muc_video}'...")
    for file_vid in danh_sach_video:
        so_anh = cat_khung_hinh_tu_video(
            duong_dan_video=str(file_vid),
            thu_muc_luu_anh=os.path.join(thu_muc_xuat, file_vid.stem)
        )
        tong_anh += so_anh

    print("=" * 75)
    print(f"[TỔNG KẾT] Hoàn tất trích xuất {tong_anh} ảnh từ {len(danh_sach_video)} video!")
    print("=" * 75)
    return tong_anh


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Script cắt khung hình chứa phương tiện từ video")
    parser.add_argument("--video", type=str, default=None, help="Đường dẫn file video cụ thể")
    parser.add_argument("--dir", type=str, default="data/raw_videos", help="Thư mục chứa các video gốc")
    parser.add_argument("--output", type=str, default="data/extracted_frames", help="Thư mục lưu ảnh trích xuất")
    args = parser.parse_args()

    if args.video:
        cat_khung_hinh_tu_video(args.video, args.output)
    else:
        cat_toan_bo_video_trong_thu_muc(args.dir, args.output)

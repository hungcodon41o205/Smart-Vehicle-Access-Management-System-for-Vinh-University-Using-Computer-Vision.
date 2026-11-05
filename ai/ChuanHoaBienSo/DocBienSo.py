"""
==============================================================================
MODULE: ĐỌC BIỂN SỐ XE VIỆT NAM TRỌN GÓI BẰNG PADDLEOCR
Thư mục: ai/ChuanHoaBienSo/DocBienSo.py
Dự án: VinhGate 2.0 (Hệ thống Quản lý Xe Ra Vào Đại học Vinh)
==============================================================================
Quy trình thực thi:
    1. Nhận ma trận ảnh cắt vùng biển số từ YOLOv8 (plate crop).
    2. Gọi bộ tiền xử lý ảnh (ai.TienXuLy) để cân góc, CLAHE, làm nét.
    3. Đưa ảnh vào PaddleOCR Engine quét các khối chữ và độ tin cậy.
    4. Phân tích tọa độ trục Y để chia dòng trên và dòng dưới.
    5. Chuẩn hóa sê-ri, sửa lỗi nhầm lẫn số/chữ theo quy chuẩn Việt Nam.
    6. Trả về kết quả (chuỗi biển số chuẩn, độ tin cậy trung bình).
==============================================================================
"""

import re
import numpy as np
from typing import Tuple

from ai.TienXuLy import tien_xu_ly_bien_so
from ai.ChuanHoaBienSo.PaddleOCR_Engine import lay_paddleocr_engine
from ai.ChuanHoaBienSo.PhanLoaiDong import phan_tich_dong_bien_so
from ai.ChuanHoaBienSo.DinhDangBienSo import dinh_dang_bien_so_viet_nam


def doc_bien_so_viet_nam(
    anh_bien_so_crop: np.ndarray,
    su_dung_tien_xu_ly: bool = True,
    ti_le_khung_hinh: float = None
) -> Tuple[str, float]:
    """
    Hàm đọc và chuẩn hóa biển số xe Việt Nam.

    :param anh_bien_so_crop: Ma trận ảnh cắt vùng biển số BGR (numpy array)
    :param su_dung_tien_xu_ly: Bật/tắt bước tiền xử lý ảnh OpenCV
    :param ti_le_khung_hinh: Tỉ lệ chiều rộng / chiều cao (W/H) từ bounding box YOLO
    :return: (chuỗi_biển_số_chuẩn, độ_tin_cậy_ocr_0_đến_1)
    """
    if anh_bien_so_crop is None or anh_bien_so_crop.size == 0:
        return "", 0.0

    # Bước 1: Tiền xử lý ảnh nếu được yêu cầu
    if su_dung_tien_xu_ly:
        anh_dau_vao_ocr = tien_xu_ly_bien_so(
            anh_bien_so_crop,
            bat_phong_to=True,
            bat_can_goc=True,
            bat_clahe=True,
            bat_lam_net=True
        )
    else:
        anh_dau_vao_ocr = anh_bien_so_crop

    # Bước 2: Nạp OCR Engine
    engine = lay_paddleocr_engine()
    if engine == "MOCK":
        return "37AB-12206", 0.95

    raw_items = []
    # 2.1. Quét với PaddleOCR (Engine chính thức)
    if hasattr(engine, "ocr"):
        try:
            ket_qua_paddle = engine.ocr(anh_dau_vao_ocr, cls=True)
            if ket_qua_paddle and ket_qua_paddle[0]:
                for item in ket_qua_paddle[0]:
                    box, (text, score) = item
                    avg_y = sum(pt[1] for pt in box) / 4.0
                    min_x = min(pt[0] for pt in box)
                    clean_t = re.sub(r'[^A-Z0-9]', '', text.strip().upper())
                    if clean_t:
                        raw_items.append((avg_y, min_x, clean_t, float(score)))
        except Exception as e_pad:
            print(f"[OCR CẢNH BÁO] Lỗi khi chạy PaddleOCR: {e_pad}")

    # 2.2. Hoặc dự phòng với EasyOCR nếu PaddleOCR không khả dụng
    elif hasattr(engine, "readtext"):
        try:
            ket_qua_easy = engine.readtext(
                anh_dau_vao_ocr,
                allowlist='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ.-@',
                detail=1,
                paragraph=False
            )
            for (bbox, text, prob) in ket_qua_easy:
                avg_y = sum(pt[1] for pt in bbox) / 4.0
                min_x = min(pt[0] for pt in bbox)
                clean_t = re.sub(r'[^A-Z0-9]', '', text.strip().upper())
                if clean_t:
                    raw_items.append((avg_y, min_x, clean_t, float(prob)))
        except Exception as e_ez:
            print(f"[OCR CẢNH BÁO] Lỗi khi chạy EasyOCR: {e_ez}")

    if not raw_items:
        return "", 0.0

    # Bước 3: Phân tích và tách dòng 1 / dòng 2 theo trục Y
    chieu_cao_anh = anh_dau_vao_ocr.shape[0]
    dong_1_items, dong_2_items, _ = phan_tich_dong_bien_so(
        raw_items,
        chieu_cao_anh=chieu_cao_anh,
        ti_le_khung_hinh=ti_le_khung_hinh
    )

    dong_1_text = "".join(x[2] for x in dong_1_items)
    dong_2_text = "".join(x[2] for x in dong_2_items)

    # Tính độ tin cậy trung bình của các ký tự nhận diện
    tong_diem = sum(x[3] for x in raw_items)
    do_tin_cay_tb = tong_diem / len(raw_items) if raw_items else 0.0

    # Bước 4: Định dạng chuẩn hóa biển số Việt Nam
    bien_so_chuan = dinh_dang_bien_so_viet_nam(dong_1_text, dong_2_text)

    return bien_so_chuan, round(do_tin_cay_tb, 4)

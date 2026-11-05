"""
==============================================================================
MODULE: PHÓNG TO ẢNH BIỂN SỐ THEO KÍCH THƯỚC TIÊU CHUẨN
Thư mục: ai/TienXuLy/PhongToAnh.py
Dự án: VinhGate 2.0 (Hệ thống Quản lý Xe Ra Vào Đại học Vinh)
==============================================================================
Mục đích:
    Khi xe ở xa camera, vùng ảnh cắt biển số có kích thước pixel nhỏ (chiều rộng < 160px).
    Ký tự lúc này bị co cụm khiến mô hình OCR (PaddleOCR) nhận diện thiếu hoặc sai nét.
    Hàm này tự động nội suy phóng to ảnh (INTER_CUBIC) đạt ngưỡng tối thiểu từ 180px - 220px,
    giúp bảo toàn cấu trúc nét chữ và nét số mà không gây răng cưa.
==============================================================================
"""

import cv2
import numpy as np


def phong_to_anh_bien_so(anh_bien_so: np.ndarray, chieu_rong_toi_thieu: int = 180) -> np.ndarray:
    """
    Phóng to ảnh cắt biển số nếu chiều rộng nhỏ hơn ngưỡng tiêu chuẩn.

    :param anh_bien_so: Ma trận ảnh cắt BGR (numpy array)
    :param chieu_rong_toi_thieu: Chiều rộng pixel tối thiểu mong muốn (mặc định 180px)
    :return: Ma trận ảnh BGR đã được phóng to đạt chuẩn
    """
    if anh_bien_so is None or anh_bien_so.size == 0:
        return anh_bien_so

    chieu_cao, chieu_rong = anh_bien_so.shape[:2]

    # Nếu ảnh đã đủ lớn thì giữ nguyên
    if chieu_rong >= chieu_rong_toi_thieu or chieu_rong <= 0:
        return anh_bien_so

    # Tính tỉ lệ phóng to bảo toàn tỷ lệ khung hình (Aspect Ratio)
    ti_le = float(chieu_rong_toi_thieu) / float(chieu_rong)
    rong_moi = int(round(chieu_rong * ti_le))
    cao_moi = int(round(chieu_cao * ti_le))

    # Sử dụng phép nội suy INTER_CUBIC để chất lượng ảnh phóng to mượt mà nhất
    anh_phong_to = cv2.resize(anh_bien_so, (rong_moi, cao_moi), interpolation=cv2.INTER_CUBIC)
    return anh_phong_to

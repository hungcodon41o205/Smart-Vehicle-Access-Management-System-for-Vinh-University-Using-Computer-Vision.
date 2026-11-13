"""
==============================================================================
MODULE: TĂNG CƯỜNG ĐỘ TƯƠNG PHẢN THÍCH ỨNG CỤC BỘ (CLAHE)
Thư mục: ai/TienXuLy/TangTuongPhan.py
Dự án: VinhGate 2.0 (Hệ thống Quản lý Xe Ra Vào Đại học Vinh)
==============================================================================
Mục đích:
    Khi xe vào bãi lúc sáng sớm, trời mưa, hoặc ánh đèn pha rọi vào buổi chiều muộn,
    biển số thường bị lóa sáng cục bộ hoặc chìm trong bóng râm của đuôi xe.
    Thuật toán CLAHE (Contrast Limited Adaptive Histogram Equalization) phân tích
    từng ô lưới nhỏ (tile) trên kênh sáng (Luminance) trong không gian màu LAB.
    Ký tự màu đen sẽ nổi bật tương phản sắc nét trên nền biển số trắng mà không làm
    khuếch đại nhiễu hạt.
==============================================================================
"""

import cv2
import numpy as np


def tang_tuong_phan_clahe(
    anh_bien_so: np.ndarray,
    clip_limit: float = 2.0,
    tile_size: int = 8
) -> np.ndarray:
    """
    Tăng cường độ tương phản cục bộ bằng CLAHE trên kênh màu L (LAB).

    :param anh_bien_so: Ma trận ảnh cắt BGR (numpy array)
    :param clip_limit: Ngưỡng hạn chế độ tương phản để tránh khuếch đại nhiễu (mặc định 2.0)
    :param tile_size: Kích thước lưới ô vuông chia cục bộ (mặc định 8x8)
    :return: Ảnh BGR đã được cân bằng sáng tối ưu
    """
    if anh_bien_so is None or anh_bien_so.size == 0:
        return anh_bien_so

    # Chuyển đổi từ không gian màu BGR sang không gian màu LAB
    # Tách biệt hoàn toàn kênh Độ sáng (L) và kênh Màu sắc (A, B)
    anh_lab = cv2.cvtColor(anh_bien_so, cv2.COLOR_BGR2LAB)
    kenh_l, kenh_a, kenh_b = cv2.split(anh_lab)

    # Khởi tạo đối tượng CLAHE của OpenCV
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(tile_size, tile_size))
    kenh_l_toi_uu = clahe.apply(kenh_l)

    # Ghép lại các kênh và chuyển ngược về BGR
    anh_lab_gop = cv2.merge([kenh_l_toi_uu, kenh_a, kenh_b])
    anh_ket_qua = cv2.cvtColor(anh_lab_gop, cv2.COLOR_LAB2BGR)

    return anh_ket_qua

"""
==============================================================================
MODULE: LÀM SẮC NÉT CẠNH KÝ TỰ (UNSHARP MASKING)
Thư mục: ai/TienXuLy/LamSacNet.py
Dự án: VinhGate 2.0 (Hệ thống Quản lý Xe Ra Vào Đại học Vinh)
==============================================================================
Mục đích:
    Xe máy và ô tô khi di chuyển qua cổng trường Đại học Vinh thường tạo ra
    hiện tượng nhòe chuyển động (Motion Blur) khiến các nét viền của chữ số
    như '3', '8', 'B', 'D' bị dính nét vào nhau.
    Kỹ thuật Unsharp Masking lấy chênh lệch giữa ảnh gốc và ảnh làm mờ Gaussian
    để nhấn mạnh các đường biên nét chữ, giúp OCR tách bạch các ký tự rõ ràng.
==============================================================================
"""

import cv2
import numpy as np


def lam_sac_net_bien_so(anh_bien_so: np.ndarray, do_manh: float = 0.6) -> np.ndarray:
    """
    Áp dụng thuật toán Unsharp Masking làm sắc nét các nét viền ký tự.

    :param anh_bien_so: Ma trận ảnh cắt BGR (numpy array)
    :param do_manh: Hệ số làm nét (mặc định 0.6 để không bị gai hạt)
    :return: Ảnh BGR đã được làm sắc nét
    """
    if anh_bien_so is None or anh_bien_so.size == 0:
        return anh_bien_so

    # Tạo lớp ảnh mờ nền bằng bộ lọc Gaussian Blur
    anh_mo = cv2.GaussianBlur(anh_bien_so, (0, 0), sigmaX=2.0)

    # Kỹ thuật Unsharp Mask: Ảnh mới = Ảnh gốc * (1 + do_manh) - Ảnh mờ * do_manh
    anh_sac_net = cv2.addWeighted(anh_bien_so, 1.0 + do_manh, anh_mo, -do_manh, 0)

    return anh_sac_net

"""
==============================================================================
MODULE: PIPELINE TIỀN XỬ LÝ ẢNH TỔNG HỢP (TIEN XU LY BIEN SO)
Thư mục: ai/TienXuLy/TienXuLyTongHop.py
Dự án: VinhGate 2.0 (Hệ thống Quản lý Xe Ra Vào Đại học Vinh)
==============================================================================
Quy trình tiền xử lý ảnh tuần tự:
    Ảnh cắt từ YOLO (Crop)
         │
         ▼
    [1. Phóng to ảnh] -> Bảo đảm chiều rộng tối thiểu >= 180px (Nội suy Cubic)
         │
         ▼
    [2. Cân góc nghiêng] -> Xoay thẳng viền ngang bằng Hough Lines / minAreaRect
         │
         ▼
    [3. Tăng tương phản] -> CLAHE thích ứng cục bộ trên kênh L (LAB)
         │
         ▼
    [4. Làm sắc nét viền] -> Unsharp Masking khử mờ chuyển động
         │
         ▼
    Ảnh biển số sạch, rõ ràng -> Đưa vào PaddleOCR Engine
==============================================================================
"""

import numpy as np
from ai.TienXuLy.PhongToAnh import phong_to_anh_bien_so
from ai.TienXuLy.CanGocNghieng import can_goc_nghieng_bien_so
from ai.TienXuLy.TangTuongPhan import tang_tuong_phan_clahe
from ai.TienXuLy.LamSacNet import lam_sac_net_bien_so


def tien_xu_ly_bien_so(
    anh_bien_so: np.ndarray,
    bat_phong_to: bool = True,
    bat_can_goc: bool = True,
    bat_clahe: bool = True,
    bat_lam_net: bool = True
) -> np.ndarray:
    """
    Hàm thực thi toàn bộ chuỗi tiền xử lý ảnh biển số xe trước khi nhận diện OCR.

    :param anh_bien_so: Ma trận ảnh cắt BGR từ bounding box của YOLO
    :param bat_phong_to: Bật/tắt bước phóng to kích thước chuẩn
    :param bat_can_goc: Bật/tắt bước xoay cân chỉnh góc nghiêng
    :param bat_clahe: Bật/tắt bước cân bằng sáng cục bộ CLAHE
    :param bat_lam_net: Bật/tắt bước làm sắc nét cạnh ký tự
    :return: Ma trận ảnh BGR đã tiền xử lý tối ưu
    """
    if anh_bien_so is None or anh_bien_so.size == 0:
        return anh_bien_so

    anh_xu_ly = anh_bien_so.copy()

    # Bước 1: Phóng to nếu ảnh quá nhỏ
    if bat_phong_to:
        anh_xu_ly = phong_to_anh_bien_so(anh_xu_ly, chieu_rong_toi_thieu=180)

    # Bước 2: Cân chỉnh góc nghiêng
    if bat_can_goc:
        anh_xu_ly = can_goc_nghieng_bien_so(anh_xu_ly, goc_nghieng_toi_da=25.0)

    # Bước 3: Tăng tương phản thích ứng cục bộ
    if bat_clahe:
        anh_xu_ly = tang_tuong_phan_clahe(anh_xu_ly, clip_limit=1.8, tile_size=8)

    # Bước 4: Làm nét cạnh ký tự
    if bat_lam_net:
        anh_xu_ly = lam_sac_net_bien_so(anh_xu_ly, do_manh=0.5)

    return anh_xu_ly

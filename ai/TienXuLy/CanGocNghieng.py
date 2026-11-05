"""
==============================================================================
MODULE: CÂN CHỈNH GÓC NGHIÊNG BIỂN SỐ XE (DESKEW)
Thư mục: ai/TienXuLy/CanGocNghieng.py
Dự án: VinhGate 2.0 (Hệ thống Quản lý Xe Ra Vào Đại học Vinh)
==============================================================================
Mục đích:
    Tại cổng trường ĐH Vinh, phương tiện thường cua hoặc đi chéo làn khi tới vạch quét,
    dẫn tới biển số bị nghiêng góc từ 5° đến 25°. Độ nghiêng này khiến bộ tách dòng OCR
    dễ đọc nhầm hoặc cắt sai hàng chữ.
    Hàm này phát hiện góc nghiêng thông qua:
        1. Lọc cạnh Canny Edge Detection
        2. Biến đổi Hough Lines tìm các đoạn thẳng viền biển số
        3. Dự phòng bằng minAreaRect nếu không bắt được đoạn thẳng
        4. Xoay ma trận Affine (WarpAffine) để trả biển số về phương ngang hoàn hảo.
==============================================================================
"""

import cv2
import numpy as np


def can_goc_nghieng_bien_so(anh_bien_so: np.ndarray, goc_nghieng_toi_da: float = 25.0) -> np.ndarray:
    """
    Tự động tính toán góc xoay và cân thẳng lại khung biển số.

    :param anh_bien_so: Ma trận ảnh cắt BGR (numpy array)
    :param goc_nghieng_toi_da: Góc nghiêng tối đa cho phép chỉnh sửa (tránh xoay quá đà gây méo ảnh)
    :return: Ảnh biển số đã được xoay thẳng theo trục ngang
    """
    if anh_bien_so is None or anh_bien_so.size == 0:
        return anh_bien_so

    chieu_cao, chieu_rong = anh_bien_so.shape[:2]

    # Bước 1: Chuyển sang ảnh xám và làm mịn khử nhiễu
    anh_xam = cv2.cvtColor(anh_bien_so, cv2.COLOR_BGR2GRAY)
    lam_mo = cv2.GaussianBlur(anh_xam, (5, 5), 0)

    # Bước 2: Phát hiện cạnh bằng thuật toán Canny
    canh = cv2.Canny(lam_mo, 50, 150, apertureSize=3)

    # Bước 3: Tìm các đoạn thẳng viền bằng HoughLinesP
    duong_thang = cv2.HoughLinesP(
        canh,
        rho=1,
        theta=np.pi / 180,
        threshold=35,
        minLineLength=max(15, chieu_rong // 4),
        maxLineGap=8
    )

    danh_sach_goc = []
    if duong_thang is not None:
        for line in duong_thang:
            x1, y1, x2, y2 = line[0]
            if x2 - x1 == 0:
                continue
            # Tính góc nghiêng (đơn vị độ)
            goc = float(np.degrees(np.arctan2(y2 - y1, x2 - x1)))
            # Chỉ lấy các đoạn thẳng có xu hướng nằm ngang (trong khoảng [-goc_nghieng_toi_da, goc_nghieng_toi_da])
            if abs(goc) <= goc_nghieng_toi_da:
                danh_sach_goc.append(goc)

    # Bước 4: Tính góc xoay trung vị (median) để loại bỏ góc nhiễu đột biến
    if len(danh_sach_goc) > 0:
        goc_xoay = float(np.median(danh_sach_goc))
    else:
        # Nếu Hough Lines không phát hiện, dùng minAreaRect trên toàn bộ tọa độ điểm sáng của cạnh
        toa_do = np.column_stack(np.where(canh > 0))
        if len(toa_do) > 10:
            hinh_chu_nhat = cv2.minAreaRect(toa_do)
            goc_rect = hinh_chu_nhat[-1]
            if goc_rect < -45:
                goc_xoay = -(90 + goc_rect)
            else:
                goc_xoay = -goc_rect
            if abs(goc_xoay) > goc_nghieng_toi_da:
                goc_xoay = 0.0
        else:
            goc_xoay = 0.0

    # Bước 5: Nếu góc nghiêng đáng kể (> 0.5 độ), thực hiện xoay ảnh
    if abs(goc_xoay) > 0.5:
        tam_xoay = (chieu_rong // 2, chieu_cao // 2)
        ma_tran_xoay = cv2.getRotationMatrix2D(tam_xoay, goc_xoay, scale=1.0)
        # Giữ viền BORDER_REPLICATE để nền tiệp màu viền biển số
        anh_da_xoay = cv2.warpAffine(
            anh_bien_so,
            ma_tran_xoay,
            (chieu_rong, chieu_cao),
            flags=cv2.INTER_CUBIC,
            borderMode=cv2.BORDER_REPLICATE
        )
        return anh_da_xoay

    return anh_bien_so

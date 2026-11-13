"""
==============================================================================
MODULE: PHÂN TÍCH VÀ PHÂN LOẠI DÒNG BIỂN SỐ XE (TRỤC TỌA ĐỘ Y & X)
Thư mục: ai/ChuanHoaBienSo/PhanLoaiDong.py
Dự án: VinhGate 2.0 (Hệ thống Quản lý Xe Ra Vào Đại học Vinh)
==============================================================================
Mục đích:
    Biển số xe máy Việt Nam luôn có 2 dòng:
        - Dòng trên (Dòng 1): Mã tỉnh và Sê-ri đăng ký (VD: '37-AB', '37-K1')
        - Dòng dưới (Dòng 2): Dãy số thứ tự đăng ký (VD: '122.06', '660.62')
    Biển số ô tô thường là 1 dòng dài ngang (VD: '37A-123.45').
    Module này nhận danh sách bounding box từ OCR, phân tách dòng trên/dưới
    theo trục Y và sắp xếp thứ tự từ trái sang phải theo trục X.
==============================================================================
"""

from typing import List, Tuple


def phan_tich_dong_bien_so(
    danh_sach_box_text: List[Tuple[float, float, str, float]],
    chieu_cao_anh: int,
    ti_le_khung_hinh: float = None
) -> Tuple[List[Tuple[float, float, str, float]], List[Tuple[float, float, str, float]], bool]:
    """
    Phân tách danh sách các khối ký tự thành Dòng 1 và Dòng 2.

    Mỗi phần tử trong danh_sach_box_text có dạng:
        (toa_do_y_trung_binh, toa_do_x_trai, chuoi_ky_tu, do_tin_cay)

    :param danh_sach_box_text: Danh sách các khối văn bản tìm thấy
    :param chieu_cao_anh: Chiều cao ảnh biển số (pixel)
    :param ti_le_khung_hinh: Tỉ lệ chiều rộng / chiều cao của biển số
    :return: (danh_sach_dong_1, danh_sach_dong_2, la_bien_2_dong)
    """
    if not danh_sach_box_text:
        return [], [], False

    # Nếu chỉ có 1 khối text duy nhất -> Coi là 1 dòng
    if len(danh_sach_box_text) == 1:
        return danh_sach_box_text, [], False

    # Sắp xếp các khối text theo thứ tự từ trên xuống dưới theo trục Y
    danh_sach_sap_xep_y = sorted(danh_sach_box_text, key=lambda x: x[0])

    # Kiểm tra xem có phải biển 2 dòng hay không:
    # 1. Chênh lệch trục Y giữa khối thấp nhất và cao nhất > 25% chiều cao ảnh
    # 2. Hoặc tỉ lệ khung hình < 2.0 (biển số vuông của xe máy)
    khoang_cach_y = danh_sach_sap_xep_y[-1][0] - danh_sach_sap_xep_y[0][0]
    la_bien_2_dong = False

    if khoang_cach_y > 0.22 * chieu_cao_anh or (ti_le_khung_hinh is not None and ti_le_khung_hinh < 2.1):
        la_bien_2_dong = True

    dong_1 = []
    dong_2 = []

    if la_bien_2_dong:
        duong_chia_y = chieu_cao_anh / 2.0
        for item in danh_sach_sap_xep_y:
            y_trung_binh = item[0]
            if y_trung_binh < duong_chia_y:
                dong_1.append(item)
            else:
                dong_2.append(item)
    else:
        # Biển 1 dòng
        dong_1 = danh_sach_sap_xep_y

    # Sắp xếp các ký tự trên từng dòng theo trục X từ trái sang phải
    dong_1_sap_xep = sorted(dong_1, key=lambda x: x[1])
    dong_2_sap_xep = sorted(dong_2, key=lambda x: x[1])

    return dong_1_sap_xep, dong_2_sap_xep, la_bien_2_dong

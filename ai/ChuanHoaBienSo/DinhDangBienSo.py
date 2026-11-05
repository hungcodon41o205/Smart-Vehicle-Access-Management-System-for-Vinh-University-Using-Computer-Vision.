"""
==============================================================================
MODULE: ĐỊNH DẠNG CHUẨN BIỂN SỐ XE VIỆT NAM (FORMATTER)
Thư mục: ai/ChuanHoaBienSo/DinhDangBienSo.py
Dự án: VinhGate 2.0 (Hệ thống Quản lý Xe Ra Vào Đại học Vinh)
==============================================================================
Mục đích:
    Ghép các phần mã tỉnh, sê-ri và dãy số thứ tự thành chuỗi biển số chuẩn hóa:
        1. Biển Xe Máy (2 dòng thông thường):
           Mã tỉnh (2 số) + Sê-ri (1 chữ + 1 số) + '-' + Dãy số (4-5 số)
           Ví dụ: '37B1-12345', '37K1-66062', '37F1-20223'
        2. Biển Xe Máy Điện / Xe 50cc (Học sinh/Sinh viên - 2 dòng):
           Mã tỉnh (2 số) + Sê-ri (2 chữ cái) + '-' + Dãy số (4-5 số)
           Ví dụ: '37AB-12206', '37AN-03879', '37AA-68686'
        3. Biển Ô Tô (1 dòng dài hoặc vuông):
           Mã tỉnh (2 số) + Sê-ri (1 chữ cái) + '-' + Dãy số (4-5 số)
           Ví dụ: '37A-12345', '30F-99999'
==============================================================================
"""

import re
from ai.ChuanHoaBienSo.SuaLoiKyTu import (
    chuyen_thanh_chu_so,
    sua_loi_seri_xe,
    sua_loi_ky_tu_ocr
)


def dinh_dang_bien_so_viet_nam(dong_1: str, dong_2: str = "") -> str:
    """
    Chuẩn hóa và định dạng chuỗi biển số xe Việt Nam.

    :param dong_1: Chuỗi ký tự dòng 1 (hoặc toàn bộ chuỗi nếu là 1 dòng)
    :param dong_2: Chuỗi ký tự dòng 2 (nếu là biển 2 dòng)
    :return: Chuỗi biển số chuẩn hóa (VD: '37AB-12206', '37B2-68686', '37A-88999')
    """
    clean1 = re.sub(r'[^A-Z0-9]', '', dong_1.upper())
    clean2 = re.sub(r'[^A-Z0-9]', '', dong_2.upper()) if dong_2 else ""

    # -------------------------------------------------------------------------
    # TRƯỜNG HỢP 1: BIỂN 2 DÒNG RÕ RÀNG (XE MÁY)
    # -------------------------------------------------------------------------
    if clean1 and clean2:
        # Loại bỏ ký tự viền/ốc vít dính vào đầu dòng 1 (VD: '737K1' -> '37K1')
        if len(clean1) >= 4 and clean1[:3].isdigit():
            clean1 = clean1[1:]
        elif len(clean1) >= 4 and not clean1[0].isdigit() and clean1[1:3].isdigit():
            clean1 = clean1[1:]

        # Mã tỉnh: 2 ký tự đầu luôn là số
        ma_tinh = chuyen_thanh_chu_so(clean1[:2])
        seri_tho = clean1[2:]
        seri = sua_loi_seri_xe(seri_tho)

        # Dãy số dòng 2: luôn là số
        day_so = chuyen_thanh_chu_so(clean2)
        # Nếu dòng 2 bị đọc dính ốc vít thành 6 số (VD: '120223' -> '20223')
        if len(day_so) == 6 and day_so[0] == '1':
            day_so = day_so[1:]

        return f"{ma_tinh}{seri}-{day_so}"

    # -------------------------------------------------------------------------
    # TRƯỜNG HỢP 2: ĐỌC THÀNH 1 DÒNG LIỀN HOẶC BIỂN Ô TÔ
    # -------------------------------------------------------------------------
    chuoi_gop = clean1 + clean2
    if len(chuoi_gop) < 6:
        return chuoi_gop

    chuoi_da_sua = sua_loi_ky_tu_ocr(chuoi_gop)

    ma_tinh = chuoi_da_sua[:2]
    phan_con_lai = chuoi_da_sua[2:]

    # Ký tự đầu của sê-ri bắt buộc là chữ
    s1 = phan_con_lai[0]
    phan_sau_s1 = phan_con_lai[1:]

    # Phân biệt các loại biển số:
    # 1. Xe máy điện / Xe 50cc (2 chữ cái sê-ri: VD 37AB12206, 37AN03879)
    if len(phan_sau_s1) >= 5 and phan_sau_s1[0].isalpha():
        s2 = phan_sau_s1[0]
        day_so = chuyen_thanh_chu_so(phan_sau_s1[1:])
        return f"{ma_tinh}{s1}{s2}-{day_so}"

    # 2. Xe máy thông thường (1 chữ + 1 số: VD 37B112345, 37K166062)
    elif len(phan_sau_s1) >= 5 and phan_sau_s1[0].isdigit() and len(phan_sau_s1[1:]) in (4, 5):
        s2 = phan_sau_s1[0]
        day_so = chuyen_thanh_chu_so(phan_sau_s1[1:])
        return f"{ma_tinh}{s1}{s2}-{day_so}"

    # 3. Ô tô thông thường (1 chữ sê-ri + 4-5 số: VD 37A12345, 30F88999)
    elif len(phan_sau_s1) in (4, 5):
        day_so = chuyen_thanh_chu_so(phan_sau_s1)
        return f"{ma_tinh}{s1}-{day_so}"

    # 4. Mặc định fallback
    else:
        return f"{ma_tinh}{s1}-{chuyen_thanh_chu_so(phan_sau_s1)}"

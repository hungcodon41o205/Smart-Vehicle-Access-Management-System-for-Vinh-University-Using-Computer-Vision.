"""
==============================================================================
MODULE: SỬA LỖI NHẬN DIỆN KÝ TỰ QUANG HỌC BIỂN SỐ XE VIỆT NAM
Thư mục: ai/ChuanHoaBienSo/SuaLoiKyTu.py
Dự án: VinhGate 2.0 (Hệ thống Quản lý Xe Ra Vào Đại học Vinh)
==============================================================================
Mục đích:
    Mô hình OCR thường nhầm lẫn giữa các ký tự có hình dạng tương tự nhau:
        - Số '8' và Chữ 'B'
        - Số '0' và Chữ 'D', 'O', 'Q'
        - Số '1' và Chữ 'I', 'L', 'T'
        - Số '2' và Chữ 'Z'
        - Số '5' và Chữ 'S'
        - Chữ 'A' và ký tự '@', '^', 'W', '4'
    Dựa trên quy chuẩn pháp lý biển số xe cơ giới Việt Nam, vị trí của từng
    ký tự được quy định chặt chẽ:
        - Ký tự 1, 2: BẮT BUỘC LÀ SỐ (Mã tỉnh từ 11 đến 99, Nghệ An là 37)
        - Ký tự 3: BẮT BUỘC LÀ CHỮ CÁI (Sê-ri biển số: A, B, C...)
        - Ký tự 4: Là Chữ cái (nếu xe 50cc / xe máy điện: AB, AA, AN...)
                   hoặc Là Chữ số (nếu xe máy thông thường: B1, B2, K1, F1...)
        - Dãy số cuối: BẮT BUỘC LÀ CHỮ SỐ (4 hoặc 5 số).
==============================================================================
"""

import re

# Bảng chuyển đổi chữ cái nhầm lẫn thành số
CHU_SANG_SO = {
    'O': '0', 'D': '0', 'Q': '0', 'U': '0',
    'I': '1', 'L': '1', 'T': '1', 'J': '1',
    'Z': '2',
    'E': '3',
    'A': '4',
    'S': '5',
    'G': '6', 'b': '6',
    'B': '8',
    'g': '9', 'q': '9'
}

# Bảng chuyển đổi số nhầm lẫn thành chữ cái
SO_SANG_CHU = {
    '0': 'D',
    '1': 'I',
    '2': 'Z',
    '3': 'B',
    '4': 'A',
    '5': 'S',
    '6': 'G',
    '8': 'B'
}


def chuyen_thanh_chu_so(chuoi_ky_tu: str) -> str:
    """Chuyển các ký tự chữ cái bị đọc nhầm thành chữ số."""
    ket_qua = []
    for ky_tu in chuoi_ky_tu:
        ket_qua.append(CHU_SANG_SO.get(ky_tu, ky_tu))
    return "".join(ket_qua)


def chuyen_thanh_chu_cai(ky_tu: str) -> str:
    """Chuyển ký tự số bị đọc nhầm thành chữ cái."""
    return SO_SANG_CHU.get(ky_tu, ky_tu)


def sua_loi_seri_xe(seri_tho: str) -> str:
    """
    Sửa lỗi vùng sê-ri biển số xe máy:
    - Ký tự 'A' hay bị đọc nhầm thành '@', '^', 'W', 'w', hoặc số '4'.
    - Ký tự 'AB' hay bị đọc thành 'HB', 'WB', '4B', 'NB'.
    - Ký tự '1' hay bị đọc thành 'I', 'L', 'T', 'J'.
    - Ký tự '2' hay bị đọc thành 'Z'.
    """
    if not seri_tho:
        return ""

    seri = seri_tho.replace('@', 'A').replace('^', 'A').replace('W', 'A').replace('w', 'A')

    # Nếu nhận diện nhầm HB -> AB khi chữ A bị mờ chóp
    if len(seri) >= 2 and seri[:2] in ('HB', 'WB', '4B', 'NB', 'QB'):
        seri = 'A' + seri[1:]

    # Ký tự đầu của sê-ri bắt buộc là chữ cái
    c1 = seri[0]
    if c1.isdigit():
        c1 = chuyen_thanh_chu_cai(c1)

    if len(seri) == 1:
        return c1

    c2 = seri[1]
    # Nếu ký tự thứ 2 là chữ cái (dòng xe 50cc / sinh viên như AB, AA, AN, AC) -> giữ nguyên
    # Nếu là các ký tự số dễ nhầm: I, L, T, J -> 1; Z -> 2
    if c2 in ('I', 'L', 'T', 'J'):
        c2 = '1'
    elif c2 in ('Z',):
        c2 = '2'

    return c1 + c2


def sua_loi_ky_tu_ocr(chuoi_bien_so: str) -> str:
    """
    Hiệu chỉnh toàn bộ chuỗi ký tự theo quy tắc logic biển số Việt Nam.

    :param chuoi_bien_so: Chuỗi ký tự thô do OCR đọc (đã loại bỏ ký tự đặc biệt)
    :return: Chuỗi ký tự đã được sửa lỗi logic
    """
    if not chuoi_bien_so or len(chuoi_bien_so) < 5:
        return chuoi_bien_so

    clean = re.sub(r'[^A-Z0-9]', '', chuoi_bien_so.upper())

    # Loại bỏ ký tự viền hoặc đinh ốc dính vào đầu (VD: '737K1' -> '37K1')
    if len(clean) >= 6 and clean[:3].isdigit() and not clean[2:4].isdigit():
        clean = clean[1:]

    chars = list(clean)

    # 1. Hai ký tự đầu tiên BẮT BUỘC là số mã tỉnh (VD: 37 Nghệ An, 38 Hà Tĩnh)
    for i in [0, 1]:
        if i < len(chars) and not chars[i].isdigit():
            chars[i] = CHU_SANG_SO.get(chars[i], chars[i])

    # 2. Ký tự thứ 3 BẮT BUỘC là chữ cái (Sê-ri: A, B, C...)
    if len(chars) >= 3 and chars[2].isdigit():
        chars[2] = SO_SANG_CHU.get(chars[2], 'A')
    elif len(chars) >= 3 and chars[2] in ('@', '^', 'W'):
        chars[2] = 'A'

    # 3. Ký tự thứ 4:
    # Nếu có 2 chữ cái sê-ri liên tiếp (xe 50cc / xe máy điện): chars[2] và chars[3] đều là chữ
    # Nếu là xe máy thường: chars[3] là số (1, 2, 3...)
    if len(chars) >= 4:
        if chars[2] in ('H', 'W', '4') and chars[3] == 'B':
            chars[2] = 'A'
        if chars[3] in ('I', 'L', 'T', 'J'):
            chars[3] = '1'
        elif chars[3] in ('Z',):
            chars[3] = '2'

    # 4. Phần dãy số đuôi (từ vị trí thứ 4 hoặc 5 trở đi) BẮT BUỘC là chữ số
    start_num_idx = 4 if len(chars) >= 8 and not chars[3].isalpha() else (5 if len(chars) >= 9 else 3)
    for j in range(start_num_idx, len(chars)):
        if not chars[j].isdigit():
            chars[j] = CHU_SANG_SO.get(chars[j], chars[j])

    # Loại bỏ ký tự ốc vít ở đầu dãy số nếu dãy số bị dư 6 số (VD: '120223' -> '20223')
    num_part = "".join(chars[start_num_idx:])
    if len(num_part) == 6 and num_part[0] == '1':
        chars = chars[:start_num_idx] + list(num_part[1:])

    return "".join(chars)

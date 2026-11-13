"""
==============================================================================
MODULE: KHỞI TẠO VÀ QUẢN LÝ ENGINE PADDLEOCR
Thư mục: ai/ChuanHoaBienSo/PaddleOCR_Engine.py
Dự án: VinhGate 2.0 (Hệ thống Quản lý Xe Ra Vào Đại học Vinh)
==============================================================================
Mục đích:
    Khởi tạo công cụ nhận dạng ký tự quang học PaddleOCR (tiếng Anh / không dấu)
    theo mô hình Lazy Loading (chỉ khởi tạo khi có yêu cầu đầu tiên) và duy trì
    duy nhất một thể hiện (Singleton) trong bộ nhớ RAM/VRAM để tối ưu tốc độ suy luận.
==============================================================================
"""

import sys

# Đảm bảo nạp PyTorch trước nếu có để tránh xung đột DLL trên Windows
try:
    import torch
except ImportError:
    pass

_paddle_ocr_engine = None


def lay_paddleocr_engine():
    """
    Trả về thể hiện PaddleOCR Engine duy nhất của hệ thống.
    """
    global _paddle_ocr_engine
    if _paddle_ocr_engine is None:
        try:
            from paddleocr import PaddleOCR
            print("[OCR] Đang nạp mô hình PaddleOCR Engine...")
            _paddle_ocr_engine = PaddleOCR(
                use_angle_cls=True,
                lang="en",
                show_log=False
            )
            print("[OCR] Khởi tạo PaddleOCR Engine thành công!")
        except Exception as e:
            print(f"[OCR CẢNH BÁO] Không thể nạp PaddleOCR ({e}).")
            # Thử dự phòng sang EasyOCR nếu có
            try:
                import easyocr
                import torch
                has_gpu = torch.cuda.is_available()
                _paddle_ocr_engine = easyocr.Reader(['en'], gpu=has_gpu)
                print(f"[OCR DỰ PHÒNG] Đã nạp thành công EasyOCR (GPU={has_gpu}).")
            except Exception as e_easy:
                print(f"[OCR LỖI] Cả PaddleOCR và EasyOCR đều không khả dụng ({e_easy}).")
                _paddle_ocr_engine = "MOCK"

    return _paddle_ocr_engine

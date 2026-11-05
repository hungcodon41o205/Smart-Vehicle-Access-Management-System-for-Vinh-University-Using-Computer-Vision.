"""
Package: ai.ChuanHoaBienSo
Hệ thống nhận diện PaddleOCR & Chuẩn hóa cấu trúc biển số xe Việt Nam
"""

from ai.ChuanHoaBienSo.PaddleOCR_Engine import lay_paddleocr_engine
from ai.ChuanHoaBienSo.PhanLoaiDong import phan_tich_dong_bien_so
from ai.ChuanHoaBienSo.SuaLoiKyTu import sua_loi_ky_tu_ocr, sua_loi_seri_xe
from ai.ChuanHoaBienSo.DinhDangBienSo import dinh_dang_bien_so_viet_nam
from ai.ChuanHoaBienSo.DocBienSo import doc_bien_so_viet_nam

__all__ = [
    "lay_paddleocr_engine",
    "phan_tich_dong_bien_so",
    "sua_loi_ky_tu_ocr",
    "sua_loi_seri_xe",
    "dinh_dang_bien_so_viet_nam",
    "doc_bien_so_viet_nam"
]

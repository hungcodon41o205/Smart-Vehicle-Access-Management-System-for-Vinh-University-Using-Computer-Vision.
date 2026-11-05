"""
Wrapper tương thích ngược cho ChuanHoaBienSo.DocBienSo
"""
from ai.ChuanHoaBienSo import (
    doc_bien_so_viet_nam,
    dinh_dang_bien_so_viet_nam,
    lay_paddleocr_engine
)

read_vietnamese_plate = doc_bien_so_viet_nam
format_vietnamese_plate = dinh_dang_bien_so_viet_nam
get_ocr_engine = lay_paddleocr_engine

__all__ = [
    "read_vietnamese_plate",
    "format_vietnamese_plate",
    "get_ocr_engine",
    "doc_bien_so_viet_nam"
]

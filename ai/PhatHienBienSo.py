"""
==============================================================================
MODULE: PHÁT HIỆN VÀ NHẬN DIỆN BIỂN SỐ XE (PHAT HIEN BIEN SO)
Thư mục: ai/PhatHienBienSo.py
Dự án: VinhGate 2.0 (Hệ thống Quản lý Xe Ra Vào Đại học Vinh)
==============================================================================
Mục đích:
    1. Tải mô hình YOLOv8n (file trọng số best.pt / best.onnx) chạy trên GPU RTX 4050 / CPU.
    2. Quét vị trí bounding box của biển số trong từng khung hình.
    3. Cắt (crop) vùng biển số kèm padding 4px an toàn.
    4. Chuyển ảnh cắt qua chuỗi Tiền xử lý (ai.TienXuLy) và Nhận dạng (ai.ChuanHoaBienSo).
    5. Phân loại chính xác xe máy (biển 2 dòng) và ô tô (biển 1 dòng).
==============================================================================
"""

import os
from pathlib import Path
import cv2
import numpy as np

from backend.core.config import YOLO_MODEL_PATH, ONNX_MODEL_PATH, USE_ONNX, BASE_DIR
from ai.ChuanHoaBienSo import doc_bien_so_viet_nam
from ai.TheoDoiHuongXe import TheoDoiHuongXe


class PhatHienBienSo:
    """
    Module phát hiện biển số sử dụng YOLOv8 kết hợp bộ đọc PaddleOCR chuẩn hóa.
    """
    def __init__(self, duong_dan_model: str = None, dung_onnx: bool = USE_ONNX):
        self.use_onnx = dung_onnx
        self.model = None
        self.tracker = TheoDoiHuongXe()

        # Tìm kiếm file trọng số mô hình hợp lệ
        target_path = Path(duong_dan_model) if duong_dan_model else YOLO_MODEL_PATH
        if not target_path.exists():
            for alt in [
                BASE_DIR / "models" / "best.pt",
                BASE_DIR / "models" / "yolov8n_vinhgate_best.pt",
                BASE_DIR / "best.pt"
            ]:
                if alt.exists():
                    target_path = alt
                    break

        self.model_path = target_path

        if target_path.exists():
            try:
                if self.use_onnx and target_path.suffix.lower() == ".onnx":
                    import onnxruntime as ort
                    self.session = ort.InferenceSession(str(target_path))
                    print(f"[AI] Đã nạp thành công mô hình ONNX: {target_path}")
                else:
                    from ultralytics import YOLO
                    self.model = YOLO(str(target_path))
                    print(f"[AI] Đã nạp thành công mô hình YOLOv8: {target_path}")
                    print(f"[AI] Danh sách nhãn (Classes): {self.model.names}")
            except Exception as e:
                print(f"[AI CẢNH BÁO] Không thể nạp mô hình từ {target_path}: {e}")
        else:
            print(f"[AI THÔNG BÁO] Chưa tìm thấy file trọng số tại: {target_path}")

    def phat_hien_va_doc(
        self,
        frame: np.ndarray,
        huong_thu_cong: str = None,
        nguong_tin_cay_yolo: float = 0.25
    ) -> list:
        """
        Nhận vào 1 frame (BGR numpy array), phát hiện biển số và đọc OCR chuẩn hóa.

        Trả về danh sách các kết quả phát hiện:
        [
            {
                "bien_so": "37AB-12206",
                "loai_xe": "XE_MAY",
                "do_tin_cay": 0.95,
                "huong": "VAO",
                "crop_img": np.ndarray,
                "plate_box": [x1, y1, x2, y2],
                "yolo_conf": 0.92,
                "ocr_conf": 0.96
            }, ...
        ]
        """
        if frame is None or frame.size == 0:
            return []

        h, w = frame.shape[:2]
        danh_sach_ket_qua = []

        if self.model is not None:
            # Chạy dự đoán với YOLO
            ket_qua_yolo = self.model(frame, conf=nguong_tin_cay_yolo, verbose=False)

            for r in ket_qua_yolo:
                boxes = r.boxes
                for box in boxes:
                    conf = float(box.conf[0])
                    xyxy = box.xyxy[0].cpu().numpy().astype(int)

                    # Bổ sung padding 4px để không phạm vào mép chữ
                    pad = 4
                    x1 = max(0, xyxy[0] - pad)
                    y1 = max(0, xyxy[1] - pad)
                    x2 = min(w, xyxy[2] + pad)
                    y2 = min(h, xyxy[3] + pad)

                    box_w = x2 - x1
                    box_h = y2 - y1
                    if box_w <= 12 or box_h <= 12:
                        continue

                    ti_le_khung_hinh = float(box_w) / float(box_h)
                    anh_crop = frame[y1:y2, x1:x2]

                    # Đọc biển số qua pipeline chuẩn hóa (Tiền xử lý + PaddleOCR)
                    bien_so_text, ocr_conf = doc_bien_so_viet_nam(
                        anh_crop,
                        su_dung_tien_xu_ly=True,
                        ti_le_khung_hinh=ti_le_khung_hinh
                    )

                    # Xác định loại xe:
                    # Tỉ lệ khung hình < 2.0 hoặc có sê-ri 2 chữ cái/chữ+số đặc thù xe máy
                    la_xe_may = (ti_le_khung_hinh < 2.0)
                    if "-" in bien_so_text:
                        dau_bien = bien_so_text.split("-")[0]
                        if len(dau_bien) >= 4:
                            la_xe_may = True
                    loai_xe = "XE_MAY" if la_xe_may else "O_TO"

                    # Tính độ tin cậy tổng hợp
                    do_tin_cay_tong = round(conf * (ocr_conf if ocr_conf > 0 else 0.8), 4)
                    huong = huong_thu_cong or "VAO"

                    danh_sach_ket_qua.append({
                        "bien_so": bien_so_text if bien_so_text else "KHONG_RO",
                        "loai_xe": loai_xe,
                        "do_tin_cay": do_tin_cay_tong,
                        "huong": huong,
                        "crop_img": anh_crop,
                        "plate_box": [x1, y1, x2, y2],
                        "yolo_conf": round(conf, 4),
                        "ocr_conf": round(ocr_conf, 4)
                    })

        return danh_sach_ket_qua

    # Alias phương thức tương thích ngược
    detect_and_read = phat_hien_va_doc


# Alias lớp tương thích ngược
PlateDetector = PhatHienBienSo

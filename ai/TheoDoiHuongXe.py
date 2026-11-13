"""
==============================================================================
MODULE: THEO DÕI QUỸ ĐẠO & XÁC ĐỊNH HƯỚNG XE (THEO DOI HUONG XE)
Thư mục: ai/TheoDoiHuongXe.py
Dự án: VinhGate 2.0 (Hệ thống Quản lý Xe Ra Vào Đại học Vinh)
==============================================================================
Mục đích:
    1. Quản lý tọa độ tâm phương tiện theo track_id do YOLO / ByteTrack cấp.
    2. Xác định hướng di chuyển bằng vector biến thiên tọa độ Y (Delta Y):
       - Delta Y > 0: Xe đang tiến lại gần camera -> Chiều VÀO
       - Delta Y < 0: Xe đang di chuyển xa dần camera -> Chiều RA
    3. Cơ chế Cooldown/Debounce: Ngăn chặn quét trùng lặp khi xe dừng chờ mở barie.
==============================================================================
"""

import time
from collections import defaultdict
from typing import Dict, Tuple, Optional


class TheoDoiHuongXe:
    """
    Theo dõi quỹ đạo phương tiện qua cổng trường Đại học Vinh.
    """
    def __init__(self, thoi_gian_cooldown_giay: int = 30, khoang_dich_chuyen_min_px: int = 20):
        self.cooldown_seconds = thoi_gian_cooldown_giay
        self.min_movement_px = khoang_dich_chuyen_min_px
        # Lưu lịch sử tọa độ tâm (x, y): track_id -> [(x, y, timestamp), ...]
        self.track_history: Dict[int, list] = defaultdict(list)
        # Lưu các biển số đã xử lý gần đây: plate_str -> timestamp
        self.processed_plates: Dict[str, float] = {}

    def cap_nhat_toa_do(self, track_id: int, center_x: int, center_y: int):
        """Thêm một điểm tọa độ tâm mới cho xe mang track_id."""
        now = time.time()
        self.track_history[track_id].append((center_x, center_y, now))
        # Chỉ giữ lại 30 điểm tọa độ gần nhất
        if len(self.track_history[track_id]) > 30:
            self.track_history[track_id].pop(0)

    def xac_dinh_huong(self, track_id: int, huong_mac_dinh: str = "VAO") -> str:
        """
        Xác định hướng di chuyển dựa trên độ biến thiên tọa độ Y:
        delta_y = y_cuoi - y_dau
        - Nếu delta_y > 0: Xe tiến lại gần camera -> Chiều VÀO
        - Nếu delta_y < 0: Xe di chuyển xa dần camera -> Chiều RA
        """
        points = self.track_history.get(track_id, [])
        if len(points) < 3:
            return huong_mac_dinh

        y_dau = points[0][1]
        y_cuoi = points[-1][1]
        delta_y = y_cuoi - y_dau

        if abs(delta_y) < self.min_movement_px:
            return huong_mac_dinh

        return "VAO" if delta_y > 0 else "RA"

    def kiem_tra_cooldown(self, bien_so: str) -> bool:
        """Kiểm tra xem biển số này có đang trong thời gian giãn cách (Debounce) không."""
        now = time.time()
        # Dọn dẹp các biển số đã hết hạn cooldown
        self.processed_plates = {
            p: ts for p, ts in self.processed_plates.items()
            if now - ts < self.cooldown_seconds
        }

        return bien_so in self.processed_plates

    def ghi_nhan_da_xu_ly(self, bien_so: str):
        """Đánh dấu biển số đã được ghi nhận lượt thành công."""
        self.processed_plates[bien_so] = time.time()


# Alias lớp tiếng Anh để tương thích
VehicleTracker = TheoDoiHuongXe

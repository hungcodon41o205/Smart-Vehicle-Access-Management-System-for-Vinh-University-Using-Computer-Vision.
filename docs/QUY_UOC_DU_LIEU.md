# QUY ƯỚC QUẢN LÝ & ĐẶT TÊN DỮ LIỆU (DATA CONVENTION)
> **Dự án**: Hệ thống Quản lý Xe Ra Vào Đại học Vinh bằng Thị giác Máy tính (VinhGate 2.0)  
> **Mục tiêu**: Chuẩn hóa dữ liệu video/ảnh và thiết lập chiến lược chia tập Train/Val/Test theo thời gian (**Temporal Split**) nhằm triệt tiêu hoàn toàn rò rỉ dữ liệu (**Data Leakage**).

---

## 1. Phân chia Khu vực Cổng & Bãi Đỗ Xe Đại học Vinh

* **`nhaxe1`**: **Khu vực Nhà xe Máy** (phục vụ sinh viên, cán bộ đi xe máy/xe điện - đặc thù biển số 2 dòng vuông).
* **`nhaxe2`**: **Khu vực Bãi đỗ Ô tô** (khuôn viên bãi đỗ ô tô cán bộ, giảng viên, khách - đặc thù biển số 1 dòng dài).

---

## 2. Quy tắc Đặt tên File Video Gốc (`data/raw_videos/`)

Cú pháp chuẩn hóa:
```text
[khu_vuc]_[loai_xe]_[lan_xe]_[YYYYMMDD]_[buoi/gio]_[so_thu_tu].mp4
```

### Bảng giải thích chi tiết các trường:

| Trường | Định dạng / Giá trị | Ý nghĩa nghiệp vụ |
| :--- | :--- | :--- |
| **`[khu_vuc]`** | `nhaxe1` / `nhaxe2` | Nhà xe 1 (Xe máy) hoặc Nhà xe 2 (Ô tô) |
| **`[loai_xe]`** | `xemay` / `oto` | Phân loại phương tiện |
| **`[lan_xe]`** | `vao` / `ra` | Hướng di chuyển tại cổng kiểm soát (Làn Vào / Làn Ra) |
| **`[YYYYMMDD]`**| `20261019`, `20261020`... | **Ngày quay thực tế** (Năm-Tháng-Ngày) |
| **`[buoi/gio]`**| `sang` (sáng), `chieu` (chiều), `toi` (tối) hoặc `0730`, `1130` | **Thời điểm / Ca quay** trong ngày |
| **`[so_thu_tu]`**| `001`, `002`, `003`... | Số thứ tự video trong cùng ca quay (3 chữ số) |

### Ví dụ áp dụng thực tế:
* `nhaxe1_xemay_vao_20261019_sang_001.mp4` : Video làn vào nhà xe máy, quay sáng ngày 19/10/2026, file 1.
* `nhaxe1_xemay_ra_20261019_chieu_001.mp4`  : Video làn ra nhà xe máy, quay chiều ngày 19/10/2026, file 1.
* `nhaxe2_oto_vao_20261020_0730_001.mp4`   : Video làn vào ô tô, quay lúc 7h30 sáng 20/10/2026, file 1.

---

## 3. Quy tắc Đặt tên Khung hình Trích xuất (`data/extracted_frames/`)

Khi chạy script `python ai/CatKhungHinh.py`, ảnh chỉ được cắt khi xuất hiện xe và tự động đặt tên theo cấu trúc:
```text
[ten_video_goc]_f[so_thu_tu_4_chu_so].jpg
```

**Ví dụ:**
```text
data/extracted_frames/
└── nhaxe1_xemay_vao_20261019_sang_001/
    ├── nhaxe1_xemay_vao_20261019_sang_001_f0001.jpg
    ├── nhaxe1_xemay_vao_20261019_sang_001_f0002.jpg
    └── ...
```

---

## 4. Chiến lược Phân chia Dữ liệu Tránh Rò rỉ (Temporal Data Splitting)

### ⚠️ Nguy cơ Rò rỉ Dữ liệu (Data Leakage):
* Khi quay một chiếc xe di chuyển qua cổng, camera thu được từ 15 đến 60 khung hình liên tiếp của cùng chiếc xe đó.
* **Không dùng Random Shuffle**: Nếu trích xuất toàn bộ ảnh rồi chia ngẫu nhiên 80% Train - 20% Test, thì các khung hình của cùng 1 xe sẽ xuất hiện ở cả hai tập, dẫn đến hiện tượng "học vẹt" (overfitting).

### ✅ Giải pháp: Phân chia theo Dòng Thời gian (Temporal Split):
Dữ liệu được phân chia theo ngày hoặc ca quay hoàn toàn độc lập:
* **TẬP HUẤN LUYỆN (Train Set - 70%)**: Khung hình từ các video ngày 19/10 đến 23/10.
* **TẬP ĐÁNH GIÁ (Validation Set - 15%)**: Khung hình từ các video ngày 24/10 (tinh chỉnh siêu tham số và checkpoint).
* **TẬP KIỂM THỬ ĐỘC LẬP (Test Set - 15%)**: Khung hình từ video ngày 25/10 (đảm bảo 100% xe trong tập Test là xe mới hoàn toàn).

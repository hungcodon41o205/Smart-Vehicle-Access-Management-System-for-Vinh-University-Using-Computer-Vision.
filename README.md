# VINHGATE 2.0 — HỆ THỐNG QUẢN LÝ XE RA VÀO ĐẠI HỌC VINH BẰNG THỊ GIÁC MÁY TÍNH
> **Phiên bản Hợp nhất Hoàn chỉnh (VinhGate_new)**  
> **Khoa Công Nghệ Thông Tin — Trường Đại Học Vinh**  
> *Đề tài thực tập tốt nghiệp: Hướng tới khuôn viên đại học thông minh (Smart Campus)*

---

## 📌 1. Giới Thiệu & Điểm Nổi Bật Của Hệ Thống

Hệ thống **VinhGate 2.0** tự động hóa 100% quy trình kiểm soát phương tiện tại các cổng Đại học Vinh:
- **Lõi AI Nhận dạng Biển số Chuyên sâu**:
  - Mô hình **YOLOv8** phát hiện xe & biển số với thời gian suy luận $< 15$ms trên GPU.
  - Chuỗi tiền xử lý ảnh **`TienXuLy`**: Cân góc nghiêng **Deskew** (Hough Lines + minAreaRect), tăng tương phản **CLAHE** kênh sáng LAB, và làm nét cạnh ký tự **Unsharp Masking**.
  - Phân hệ chuẩn hóa **`ChuanHoaBienSo`**: Sử dụng **PaddleOCR Engine** kết hợp phân tích tọa độ trục Y để xếp đúng thứ tự dòng 1 & dòng 2, tự động sửa nhầm lẫn ký tự theo quy chuẩn sê-ri biển số Việt Nam (xe ô tô 1 dòng, xe máy 2 dòng thường và xe máy điện/50cc 2 chữ cái `37AB`, `37AN`).
- **Thuật toán Session Tracking & Majority Voting**:
  - Gom các khung hình trong khoảng thời gian $\le 1.2$ giây thành 1 lượt xe duy nhất.
  - Bình chọn mã tỉnh đa số và chọn ra **duy nhất 1 kết quả + 1 ảnh cắt rõ nét nhất** cho mỗi lượt xe qua cổng.
- **Cơ sở dữ liệu 13 bảng chuẩn 3NF (Cách B)**:
  - Quản lý đầy đủ danh sách xe sinh viên/cán bộ nội bộ, danh sách đen (`danh_sach_den`), và phiếu đăng ký xe khách tạm thời (`dang_ky_khach`).
  - View tự động đếm số lượng xe đang có mặt trong khuôn viên trường theo thời gian thực.
- **Hệ thống Web Dashboard Giám sát**:
  - Xây dựng trên nền tảng **FastAPI + WebSocket real-time**, độ trễ cập nhật $< 500$ms.

---

## 📂 2. Cấu Trúc Mã Nguồn Dự Án (VinhGate_new)

```
VinhGate_new/
├── .github/                           # Bộ mẫu quản lý công việc và báo lỗi chuẩn GitHub
├── .vscode/                           # Cấu hình môi trường VSCode tối ưu UTF-8
├── ai/                                # Phân hệ AI & Thị giác Máy tính (Đã chuẩn hóa Việt hóa)
│   ├── TienXuLy/                      # [MODULE MỚI] Gộp các thuật toán tiền xử lý ảnh OpenCV
│   │   ├── PhongToAnh.py              # Phóng to nội suy Cubic đảm bảo kích thước cho OCR
│   │   ├── CanGocNghieng.py           # Thuật toán Deskew cân chỉnh góc nghiêng khi xe vào chéo cổng
│   │   ├── TangTuongPhan.py           # Tăng độ tương phản CLAHE trên kênh L (LAB)
│   │   ├── LamSacNet.py               # Làm sắc nét viền ký tự Unsharp Masking khử mờ chuyển động
│   │   └── TienXuLyTongHop.py         # Pipeline liên kết tuần tự các bước tiền xử lý
│   ├── ChuanHoaBienSo/                # [MODULE MỚI] PaddleOCR Engine & Chuẩn hóa biển số VN
│   │   ├── PaddleOCR_Engine.py        # Quản lý khởi tạo PaddleOCR Engine duy nhất
│   │   ├── PhanLoaiDong.py            # Phân tích tọa độ Y để ghép đúng dòng 1 và dòng 2 (xe máy)
│   │   ├── SuaLoiKyTu.py              # Sửa lỗi nhầm lẫn quang học dựa trên cấu trúc biển số VN
│   │   ├── DinhDangBienSo.py          # Định dạng chuẩn hóa (ô tô, xe máy thường, xe 50cc/điện)
│   │   └── DocBienSo.py               # Hàm đọc trọn gói: Tiền xử lý -> OCR -> Sửa lỗi -> Định dạng
│   ├── CatKhungHinh.py                # [MODULE MỚI] Tự động trích xuất frame có xe bằng YOLO (lọc rác)
│   ├── PhatHienBienSo.py              # YOLOv8 nhận diện biển số + kết nối Tiền xử lý & OCR
│   └── TheoDoiHuongXe.py              # ByteTrack / Delta Y theo dõi hướng Vào/Ra & Debounce
├── backend/                           # Máy chủ Backend (FastAPI + WebSocket)
│   ├── main.py                        # Điểm khởi chạy FastAPI & WebSocket /ws/gate
│   ├── core/
│   │   ├── config.py                  # Cấu hình BASE_DIR và tham số hệ thống
│   │   └── db_connection.py           # Kết nối CSDL MySQL vinh_gate
│   ├── services/
│   │   ├── gate_service.py            # Nghiệp vụ đối chiếu xe, đếm xe, cảnh báo blacklist
│   │   └── guest_service.py           # Nghiệp vụ lập phiếu tạm xe khách (dang_ky_khach)
│   └── routers/
│       ├── api_gate.py                # REST API xử lý sự kiện cổng, xác nhận tay
│       ├── api_vehicles.py            # REST API quản lý xe nội bộ, khách, danh sách đen
│       └── api_stats.py               # REST API thống kê lưu lượng xe, xuất Excel
├── database/                          # Thư mục Cơ sở Dữ liệu MySQL
│   ├── schema.sql                     # Script tạo 13 bảng chuẩn 3NF (Cách B)
│   ├── seed_data.sql                  # Dữ liệu khởi tạo mẫu của ĐH Vinh
│   ├── migrations/                    # Kịch bản nâng cấp CSDL
│   └── queries/                       # Các câu truy vấn nghiệp vụ phức tạp
├── frontend/                          # Giao diện Web Dashboard Giám Sát
│   ├── index.html                     # Trang Giám sát camera, đếm xe, điều khiển barie
│   ├── vehicles.html                  # Trang Quản lý xe cán bộ/SV & lập phiếu khách
│   ├── history.html                   # Trang Lịch sử ra vào & xuất báo cáo
│   ├── css/dashboard.css              # Giao diện phẳng hiện đại tối ưu máy trạm
│   └── js/                            # Script kết nối WebSocket và biểu đồ Chart.js
├── models/                            # Trọng số mô hình học sâu
│   └── best.pt                        # Trọng số YOLOv8 huấn luyện nhận diện biển số
├── docs/                              # Tài liệu kỹ thuật dự án
│   ├── VinhGate_Train_Colab.ipynb     # Jupyter Notebook huấn luyện Colab (GPU Tesla T4)
│   ├── QUY_UOC_DU_LIEU.md             # Quy ước đặt tên video/ảnh và chia tập Temporal Split
│   └── LUONG_HOAT_DONG_HE_THONG.md    # Tài liệu chi tiết luồng xử lý và bảng so sánh
├── data/                              # Thư mục dữ liệu media
│   ├── raw_videos/                    # Chứa video quay thực tế tại cổng trường
│   ├── extracted_frames/              # Chứa các frame đã lọc xe để gán nhãn Roboflow
│   ├── detected_plates/               # Ảnh cắt biển số rõ nét nhất của từng lượt xe
│   └── captured_logs/                 # Ảnh chụp từng lượt xe phục vụ đối soát
├── scripts/
│   ├── init_db.py                     # Khởi tạo tự động CSDL MySQL vinh_gate
│   └── create_github_labels.sh        # Tạo bộ nhãn quản lý dự án trên GitHub
├── XuLyVideo.py                       # Script xử lý video offline với Session Tracking & Voting
├── requirements.txt                   # Danh sách thư viện Python cần thiết
├── .env.example                       # Biến môi trường mẫu
└── README.md                          # Tài liệu hướng dẫn này
```

---

## 🚀 3. Hướng Dẫn Cài Đặt & Vận Hành

### Bước 1: Khởi tạo Môi trường Python
```bash
# Tạo môi trường ảo
python -m venv venv

# Kích hoạt trên Windows PowerShell:
.\venv\Scripts\Activate.ps1

# Cài đặt thư viện:
pip install -r requirements.txt
```
> **Lưu ý:** Nếu máy tính trang bị GPU NVIDIA rời (như RTX 4050), hãy cài đặt PyTorch hỗ trợ CUDA trước:
> ```bash
> pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124
> ```

### Bước 2: Cấu hình Biến Môi Trường (`.env`)
Sao chép `.env.example` thành `.env` và điền thông số MySQL:
```bash
cp .env.example .env
```
Mở `.env` và kiểm tra `DB_HOST`, `DB_USER`, `DB_PASSWORD`.

### Bước 3: Khởi tạo Cơ sở Dữ liệu MySQL (13 Bảng)
Chạy script nạp tự động `schema.sql` và `seed_data.sql`:
```bash
python scripts/init_db.py
```

### Bước 4: Xử lý Video Ngoại Tuyến (Offline Video Processing)
Chạy module xử lý video với thuật toán Session Tracking & Majority Voting:
```bash
python XuLyVideo.py data/raw_videos/sample_test.mp4
```
* Kết quả: Ảnh biển số đẹp nhất lưu tại `data/detected_plates/`, bảng danh sách xe xuất tại `data/danh_sach_bien_so.csv`.

### Bước 5: Khởi chạy Máy chủ Backend & Web Dashboard
```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```
Truy cập hệ thống trên trình duyệt:
- 📹 **Giám sát trực tiếp:** [http://localhost:8000/frontend/index.html](http://localhost:8000/frontend/index.html)
- 🚗 **Quản lý Xe & Lập Phiếu Khách:** [http://localhost:8000/frontend/vehicles.html](http://localhost:8000/frontend/vehicles.html)
- 📜 **Lịch sử & Báo Cáo:** [http://localhost:8000/frontend/history.html](http://localhost:8000/frontend/history.html)
- 📖 **Tài liệu Swagger API:** [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🤖 4. Huấn Luyện AI Trên Google Colab

1. Bỏ video quay thực tế vào `data/raw_videos/`.
2. Chạy lệnh trích xuất các khung hình có xe:
   ```bash
   python ai/CatKhungHinh.py
   ```
3. Đưa ảnh trong `data/extracted_frames/` lên **Roboflow**, gán nhãn 3 lớp: `license_plate`, `motorcycle`, `car`.
4. Mở file [docs/VinhGate_Train_Colab.ipynb](docs/VinhGate_Train_Colab.ipynb) trên Google Colab (chọn GPU Tesla T4):
   - **Cell 1**: Kiểm tra GPU & cài thư viện Ultralytics.
   - **Cell 2**: Nạp dataset và cấu hình `data.yaml`.
   - **Cell 3**: Huấn luyện YOLOv8n (50 epochs, optimizer AdamW).
   - **Cell 4**: Đánh giá chỉ số mAP@0.5, Precision, Recall.
   - **Cell 5**: Kiểm thử dự đoán trên ảnh cổng trường.
   - **Cell 6**: Export ra `best.onnx` và tải về đặt vào thư mục `models/best.pt`.

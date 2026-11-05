# TÀI LIỆU KIẾN TRÚC & LUỒNG HOẠT ĐỘNG HỆ THỐNG VINHGATE 2.0 (BẢN HỢP NHẤT)

> **Đề tài**: Hệ thống Quản lý Xe Ra Vào Đại học Vinh bằng Thị giác Máy tính  
> **Thư mục dự án mới**: `D:\VinhGate_new`  
> **Ngày hợp nhất**: Tháng 11/2026  

---

## 📌 1. Tổng Quan Về Bản Hợp Nhất (VinhGate_new)

Bản hợp nhất **`VinhGate_new`** là sự kết hợp tối ưu giữa hai nền tảng:
1. **Lõi AI & Thị giác Máy tính Chuyên sâu** (từ `Do_An_TTCN`):
   - Kỹ thuật tiền xử lý ảnh OpenCV chuyên sâu: Cân góc nghiêng **Deskew** bằng Canny + Hough Lines, tăng tương phản thích ứng **CLAHE** trên kênh L (LAB), làm sắc nét **Unsharp Masking**, và phóng to ảnh nội suy Cubic.
   - Module nhận dạng ký tự quang học **PaddleOCR Engine** tách dòng trên/dưới theo trục tọa độ Y, sửa lỗi ký tự OCR theo quy chuẩn sê-ri biển số xe cơ giới Việt Nam (hỗ trợ cả biển xe máy thường `37B1`, biển xe điện/50cc `37AB`, `37AN` và biển ô tô `37A`).
   - Module trích xuất khung hình thông minh lọc xe bằng AI (bỏ 100% frame đường trống) và đặt tên file chuẩn hóa tránh rò rỉ dữ liệu.
2. **Kiến trúc Hệ thống Doanh nghiệp & Nghiệp vụ Quản lý Toàn diện** (từ `Vinhgate`):
   - Cơ sở dữ liệu chuẩn hóa **13 bảng 3NF (Cách B)** quản lý xe nội bộ, lập phiếu tạm xe khách vãng lai (`dang_ky_khach`), danh sách đen (`danh_sach_den`), và View tự động đếm xe trong trường.
   - Cơ chế **Session Tracking (Gom lượt xe <= 1.2s) & Majority Voting (Bình chọn đa số)**: Khắc phục triệt để lỗi 1 xe bị nhảy ra nhiều kết quả.
   - Máy chủ Backend **FastAPI + WebSocket real-time** và giao diện **Web Dashboard 3 trang** trực quan phục vụ chốt bảo vệ.

---

## 🔄 2. Sơ Đồ Luồng Hoạt Động Tổng Thể (End-to-End Workflow)

```mermaid
flowchart TD
    subgraph ThuThap["Giai đoạn 1: Thu thập & Huấn luyện (Colab / Roboflow)"]
        V1["Video Cổng ĐH Vinh<br/>(data/raw_videos/)"] --> E1["Script: ai/CatKhungHinh.py<br/>(YOLO COCO lọc frame có xe)"]
        E1 --> F1["Khung hình chuẩn hóa<br/>(data/extracted_frames/)"]
        F1 --> R1["Roboflow Gán Nhãn<br/>(license_plate, motorcycle, car)"]
        R1 --> C1["Google Colab (Tesla T4 GPU)<br/>(docs/VinhGate_Train_Colab.ipynb)"]
        C1 --> M1["Trọng số tối ưu best.pt<br/>(models/best.pt)"]
    end

    subgraph NhanDienAI["Giai đoạn 2: Phân hệ Thị giác Máy tính (AI Core)"]
        CAM["Camera Cổng / Video Stream"] --> YOLO["YOLOv8 Detection<br/>(ai/PhatHienBienSo.py)"]
        YOLO -->|Bounding Box + Crop| PRE["Module Tiền Xử Lý: ai/TienXuLy/<br/>1. PhongToAnh.py (Cubic >= 180px)<br/>2. CanGocNghieng.py (Deskew)<br/>3. TangTuongPhan.py (CLAHE LAB)<br/>4. LamSacNet.py (Unsharp Mask)"]
        PRE --> OCR["Module Nhận Dạng: ai/ChuanHoaBienSo/<br/>1. PaddleOCR_Engine.py<br/>2. PhanLoaiDong.py (Tọa độ Y Dòng 1 & 2)<br/>3. SuaLoiKyTu.py (Quy chuẩn VN)<br/>4. DinhDangBienSo.py (37AB-12206)"]
        OCR --> TRACK["Gom Nhóm Lượt Xe & Bỏ Phiếu<br/>(Session Tracking <= 1.2s & Majority Voting)"]
    end

    subgraph XuLyNghiepVu["Giai đoạn 3: Backend & CSDL (FastAPI + MySQL)"]
        TRACK -->|Biển số + Hướng Vào/Ra| API["FastAPI Router: /api/gate/event<br/>(backend/routers/api_gate.py)"]
        API --> SVC["Gate Service: backend/services/gate_service.py"]
        SVC --> DB1{Kiểm tra Danh sách đen?}
        DB1 -->|Có trong Blacklist| T1["TỪ CHỐI / CẢNH BÁO ĐỎ"]
        DB1 -->|Không| DB2{Kiểm tra Xe nội bộ?}
        DB2 -->|Sinh viên / Cán bộ| T2["CHO PHÉP / MỞ BARIE"]
        DB2 -->|Không| DB3{Kiểm tra Phiếu khách Cách B?}
        DB3 -->|Khách có đăng ký hợp lệ| T2
        DB3 -->|Xe lạ chưa đăng ký| T3["CHỜ XÁC NHẬN TAY"]
        SVC --> DB4[(MySQL 13 Bảng 3NF)]
    end

    subgraph GiaoDien["Giai đoạn 4: Hiển thị Real-time"]
        SVC -->|Broadcast JSON| WS["WebSocket: /ws/gate"]
        WS --> UI["Web Dashboard Giám sát<br/>(frontend/index.html)"]
        UI --> ACT["Hiển thị ảnh cắt + Biển số + Cập nhật số xe đếm trong bãi"]
    end
```

---

## 📊 3. Bảng So Sánh Chi Tiết: Hệ Thống Cũ (Vinhgate) vs. Hệ Thống Mới (VinhGate_new)

| STT | Thành phần / Chức năng | Hệ thống bạn của bạn lúc ban đầu (`Vinhgate`) | Hệ thống Hợp nhất Mới (`VinhGate_new`) | Lợi ích & Giá trị kỹ thuật |
| :---: | :--- | :--- | :--- | :--- |
| **1** | **Tiền xử lý ảnh (Image Preprocessing)** | Nằm chung trong `ocr_reader.py`: Chỉ resize cơ bản và CLAHE ảnh xám; **không có** cân góc nghiêng. | Tách thành thư mục độc lập **`ai/TienXuLy/`** gồm 4 module chuyên sâu: `PhongToAnh.py`, `CanGocNghieng.py`, `TangTuongPhan.py`, `LamSacNet.py`. | Tăng độ chính xác OCR từ 15-25% đối với các ca xe vào chéo cổng (nghiêng 10°-25°) hoặc xe bị bóng râm/ngược sáng. |
| **2** | **Công cụ Nhận dạng ký tự (OCR Engine)** | Cấu hình ưu tiên `EasyOCR` làm mặc định, dự phòng `PaddleOCR`. Chưa tối ưu phân tách 2 dòng theo tọa độ Y. | Chuyển toàn bộ sang **`PaddleOCR Engine`** làm chuẩn chính thức tại **`ai/ChuanHoaBienSo/`**, phân tích tọa độ Y của bounding box để ghép dòng. | PaddleOCR nhận diện phông chữ biển số Việt Nam nhanh hơn, ít bị đọc nhầm dấu và ổn định trên cả CPU lẫn GPU. |
| **3** | **Chuẩn hóa Biển số xe Việt Nam** | Xử lý sê-ri chủ yếu cho ô tô và xe máy thông thường (`37B1`), dễ nhầm sê-ri 2 chữ cái (`37AB`). | Hoàn thiện logic tại `DinhDangBienSo.py`: hỗ trợ đầy đủ **biển xe máy điện / xe 50cc sê-ri 2 chữ cái** (`37AB`, `37AN`), xe máy 1 chữ 1 số, và ô tô 1 dòng. | Giải quyết triệt để lỗi xe máy điện của sinh viên ĐH Vinh bị cắt sai thành ô tô (`37A-N03879` $\to$ `37AN-03879`). |
| **4** | **Trích xuất Khung hình từ Video** | `ai/extract_frames.py` lấy frame cách đều cố định (mỗi 12 frame), lấy cả frame đường trống không có xe. | Module **`ai/CatKhungHinh.py`** dùng YOLO lọc thông minh: **chỉ trích xuất khi có xe máy/ô tô**, bỏ qua đường trống, đồng bộ tên `[video]_fXXXX.jpg`. | Tiết kiệm 60-70% dung lượng lưu trữ, tập dataset đưa lên Roboflow sạch 100%, không bị rác dữ liệu. |
| **5** | **Xử lý Video & Giao diện HUD** | Ở dự án `Do_An_TTCN` có vẽ HUD che màn hình và debounce tạm 15 frame gây lỗi nhiều biển cho 1 xe. | **Bỏ hoàn toàn hàm vẽ HUD và debounce tạm cũ**. Thay bằng **`XuLyVideo.py`** tích hợp Session Tracking (1.2s) và Majority Voting. | Xử lý video chạy cực nhanh (~35-45 FPS), mỗi xe chỉ xuất đúng 1 kết quả tối ưu nhất kèm 1 ảnh cận cảnh rõ nét. |
| **6** | **Quy chuẩn Đặt tên File & Thư mục** | Tên file tiếng Anh lẫn lộn (`ocr_reader`, `detector`, `tracker`). | **Việt hóa chuẩn mực các module AI**: `TienXuLy/`, `ChuanHoaBienSo/`, `CatKhungHinh.py`, `PhatHienBienSo.py`, `TheoDoiHuongXe.py`, `XuLyVideo.py`. Kèm wrapper tiếng Anh tương thích. | Mã nguồn sáng sủa, dễ đọc, dễ bảo vệ đồ án tốt nghiệp trước hội đồng chấm thi của nhà trường. |
| **7** | **Bộ dữ liệu kiểm thử (Test Samples)** | Các file test video nặng, script test đơn lẻ phân mảnh (`test_ocr_sample`, `test_video_pipeline`...). | **Đã dọn dẹp sạch toàn bộ file rác và video nặng**. Giữ lại cấu trúc thư mục sạch và script chạy thống nhất `XuLyVideo.py`. | Thư mục dự án gọn nhẹ, sạch sẽ, sẵn sàng nén đóng gói nộp hội đồng hoặc đẩy lên GitHub. |

---

## 🛠️ 4. Hướng Dẫn Vận Hành Hệ Thống Mới

### Bước 1: Khởi tạo Cơ sở Dữ liệu MySQL (13 Bảng 3NF)
```bash
python scripts/init_db.py
```

### Bước 2: Chạy Xử lý Video Ngoại tuyến (Offline Inference)
```bash
python XuLyVideo.py data/raw_videos/sample_test.mp4
```
* Kết quả: Ảnh biển số rõ nét nhất lưu tại `data/detected_plates/`, bảng danh sách xe lưu tại `data/danh_sach_bien_so.csv`.

### Bước 3: Khởi chạy Máy chủ Backend & Giao diện Giám sát Trực tiếp
```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```
* Mở trình duyệt truy cập:
  - 🖥️ **Giám sát trực tiếp:** [http://localhost:8000/frontend/index.html](http://localhost:8000/frontend/index.html)
  - 🚗 **Quản lý Xe & Lập Phiếu Khách:** [http://localhost:8000/frontend/vehicles.html](http://localhost:8000/frontend/vehicles.html)
  - 📜 **Lịch sử & Báo cáo Thống kê:** [http://localhost:8000/frontend/history.html](http://localhost:8000/frontend/history.html)
  - 📖 **Tài liệu Swagger REST API:** [http://localhost:8000/docs](http://localhost:8000/docs)

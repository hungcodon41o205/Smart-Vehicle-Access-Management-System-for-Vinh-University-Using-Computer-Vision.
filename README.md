<div align="center">
  <h1>VINHGATE — HỆ THỐNG QUẢN LÝ XE RA VÀO ĐẠI HỌC VINH</h1>
  <h3>ỨNG DỤNG THỊ GIÁC MÁY TÍNH & HỌC SÂU TRONG XÂY DỰNG KHUÔN VIÊN THÔNG MINH</h3>
  <p><strong>Trường Đại học Vinh · Khoa Công nghệ Thông tin</strong></p>
  <p><strong>Công nghệ sử dụng:</strong> Python 3 · YOLOv8 · OpenCV · PaddleOCR / EasyOCR · FastAPI · WebSocket · MySQL 8.0 · Chart.js</p>
</div>

---

<a id="muc-luc"></a>
## 📑 Mục lục

- [1. Giới thiệu đề tài & Bối cảnh](#1-gioi-thieu)
- [2. Chức năng hệ thống](#2-chuc-nang)
- [3. Luồng hoạt động & Thuật toán cốt lõi](#3-thuat-toan)
- [4. Kiến trúc công nghệ & Tổ chức ứng dụng](#4-cong-nghe)
- [5. Cơ sở dữ liệu 13 bảng & Views thống kê](#5-co-so-du-lieu)
- [6. Hướng dẫn cài đặt & Vận hành](#6-cai-dat)
- [7. Dữ liệu thử nghiệm & Kịch bản test nhanh](#7-du-lieu-demo)
- [8. Kịch bản trình diễn trước Hội đồng (10–15 phút)](#8-kich-ban-demo)
- [9. Cấu trúc thư mục dự án](#9-cau-truc-thu-muc)
- [10. Kiểm thử & Đánh giá độ chính xác](#10-kiem-thu)
- [11. Lỗi thường gặp & Cách khắc phục](#11-loi-thuong-gap)
- [12. Giới hạn hiện tại & Hướng phát triển](#12-gioi-han-phat-trien)


<a id="1-gioi-thieu"></a>
## 1. Giới thiệu đề tài & Bối cảnh

Tại các cổng ra vào của Trường Đại học Vinh (đặc biệt là Cổng chính đường Lê Duẩn, khu vực Nhà xe 1 và Nhà xe 2), lưu lượng phương tiện của cán bộ giảng viên, sinh viên và khách liên hệ công tác vào các khung giờ cao điểm sáng và chiều là rất lớn. Việc kiểm soát thủ công bằng mắt thường hoặc ghi vé giấy bộc lộ nhiều hạn chế:
- Dễ gây ùn ứ kéo dài tại cổng trường.
- Khó kiểm soát đối tượng lạ, nguy cơ mất trộm phương tiện.
- Thiếu số liệu thống kê tức thời về số lượng phương tiện thực tế đang lưu lại trong khuôn viên trường.

**Hệ thống VinhGate 2.0** được nghiên cứu và phát triển nhằm tự động hóa quy trình kiểm soát phương tiện qua cổng thông qua thị giác máy tính và học sâu (Deep Learning). Hệ thống phát hiện, cắt và nhận dạng biển số xe máy và ô tô theo quy chuẩn biển số Việt Nam; tự động đối chiếu cơ sở dữ liệu để mở thanh chắn Barie tự động, cảnh báo danh sách đen (Blacklist) và cung cấp bảng điều khiển giám sát thời gian thực cho nhân viên bảo vệ.

### Mục tiêu đề tài
- **Tự động hóa nhận diện**: Nhận dạng chính xác biển số xe ô tô (1 dòng), xe máy thông thường (2 dòng) và xe máy điện/xe 50cc của sinh viên (sê-ri 2 chữ cái như `37AB`, `37AN`).
- **Nâng cao chất lượng ảnh đầu vào**: Ứng dụng chuỗi tiền xử lý quang học OpenCV (cân góc nghiêng Deskew, tăng tương phản cục bộ CLAHE, làm nét cạnh ký tự Unsharp Masking) nhằm khắc phục hiện tượng xe chạy chéo góc, lóa đèn pha hoặc bóng râm.
- **Thuật toán Session Tracking & Majority Voting**: Gom các khung hình liên tiếp của cùng một xe trong khoảng thời gian $\le 1.2$ giây để bình chọn mã tỉnh đa số và trích xuất ra duy nhất một kết quả cùng ảnh chụp rõ nét nhất, loại bỏ triệt để hiện tượng 1 xe quét ra nhiều biển khác nhau.
- **Đối chiếu nghiệp vụ chặt chẽ**: Quản lý 3 nhóm phương tiện: Xe nội bộ cán bộ/sinh viên, xe khách công tác có đăng ký hẹn trước (phiếu tạm Cách B), và xe vi phạm trong danh sách đen.
- **Giám sát thời gian thực**: Cung cấp giao diện Web trực quan với công nghệ WebSocket, thống kê lưu lượng xe 24 giờ và hỗ trợ xuất báo cáo Excel đối soát.

---

<a id="2-chuc-nang"></a>
## 2. Chức năng hệ thống

Hệ thống được chia thành hai phân hệ chính: **Phân hệ AI & Thị giác Máy tính** và **Phân hệ Quản trị & Máy chủ Giám sát**.

### 2.1. Phân hệ AI & Thị giác máy tính
- **Phát hiện biển số tự động**: Sử dụng mô hình YOLOv8 (`models/best.pt`) định vị chính xác vùng chứa biển số xe với độ trễ thấp (< 15ms trên GPU, < 120ms trên CPU).
- **Chuỗi tiền xử lý quang học chuyên sâu (`ai/TienXuLy`)**:
  - *Deskew (Cân góc nghiêng)*: Thuật toán biến đổi Hough Lines tự động xoay ngang biển số khi xe đi chéo góc cổng.
  - *Phóng to ảnh (Bicubic)*: Mở rộng ảnh biển số đạt độ phân giải chuẩn $\ge 180$px phục vụ đọc OCR.
  - *Tăng tương phản (CLAHE)*: Cân bằng biểu đồ độ sáng thích ứng trên kênh L (không gian màu LAB), triệt tiêu hiện tượng bóng râm hoặc lóa sáng đèn pha.
  - *Làm sắc nét viền (Unsharp Masking)*: Khử hiện tượng mờ nhòe chuyển động (motion blur) khi xe đang di chuyển.
- **Nhận dạng OCR & Chuẩn hóa biển số Việt Nam (`ai/ChuanHoaBienSo`)**:
  - Đọc ký tự bằng Engine PaddleOCR kết hợp phân tích tọa độ trục Y để ghép đúng Dòng 1 (mã tỉnh + sê-ri) và Dòng 2 (dãy số thứ tự).
  - Tự động sửa lỗi nhầm lẫn quang học đặc thù (sửa số thành chữ tại vị trí sê-ri; khôi phục chữ `'A'` từ `@`, `W`, `HB`).
  - Định dạng chuẩn biển số Việt Nam (ô tô `37A-12345`, xe máy `37K1-66062`, xe 50cc/điện sinh viên `37AB-12206`).
  - Cơ chế dự phòng (Fallback): Tự động chuyển sang EasyOCR khi môi trường chưa cài đặt thư viện PaddleOCR.
- **Xử lý video ngoại tuyến (`XuLyVideo.py`)**: Đọc file video camera, tự động gom nhóm lượt xe, bình chọn mã tỉnh đa số, lưu ảnh cắt rõ nét nhất vào `data/detected_plates/` và xuất danh sách tổng hợp ra file CSV.
- **Trích xuất khung hình tự động (`ai/CatKhungHinh.py`)**: Lọc thông minh chỉ cắt các frame có phương tiện (loại bỏ 100% frame đường trống) phục vụ tạo tập dữ liệu huấn luyện Roboflow.
- **Xác định hướng xe & Chống đếm lặp (`ai/TheoDoiHuongXe.py`)**: Phân tích biến thiên tọa độ trục Y ($\Delta Y$) để xác định xe đang đi VÀO hay đi RA, kết hợp cơ chế Cooldown/Debounce tránh đếm trùng khi xe dừng chờ mở cổng.

### 2.2. Phân hệ Quản trị & Máy chủ Giám sát (Web Dashboard)
- **Bảng giám sát trực ban thời gian thực (`frontend/index.html`)**:
  - Cập nhật số lượng phương tiện thực tế đang có mặt trong trường (Tổng số, Xe máy, Ô tô) qua VIEW CSDL.
  - Hiển thị tức thời thông tin lượt xe vừa quét (Biển số, hình ảnh cắt, đối tượng chủ xe, độ tin cậy AI, thời gian xử lý).
  - Điều khiển mô phỏng trạng thái thanh chắn Barie (Đang mở cho qua / Giữ đóng).
  - Hỗ trợ nghiệp vụ **Xác nhận tay (Manual Confirm)**: Cho phép bảo vệ chỉnh sửa biển số khi AI đọc mờ hoặc đối soát xe lạ.
  - Thanh kịch bản kiểm thử nhanh các trường hợp nghiệp vụ cổng ngay trên giao diện.
- **Hồ sơ phương tiện & Phiếu đăng ký khách (`frontend/vehicles.html`)**:
  - *Quản lý xe nội bộ*: Tra cứu danh sách xe cán bộ, sinh viên đã đăng ký vé tháng; hỗ trợ tìm kiếm nhanh theo mã SV, họ tên, biển số và thêm xe mới.
  - *Phiếu đăng ký xe khách*: Theo dõi phiếu tạm của khách công tác (mã tạm, biển số, đơn vị, người tiếp đón, khung giờ hiệu lực).
  - *Danh sách đen (Blacklist)*: Quản lý các biển số bị chặn vào trường do vi phạm nội quy hoặc an ninh.
- **Lịch sử ra vào & Thống kê báo cáo (`frontend/history.html`)**:
  - Biểu đồ đường phân bố lưu lượng xe theo 24 giờ trong ngày (sử dụng thư viện Chart.js).
  - Bảng tra cứu nhật ký toàn bộ lượt xe ra vào kèm thời gian xử lý tính bằng mili-giây.
  - Xuất báo cáo lịch sử ra file chuẩn Microsoft Excel (.xlsx) với định dạng màu sắc chuyên nghiệp phục vụ đối soát.

---

<a id="3-thuat-toan"></a>
## 3. Luồng hoạt động & Thuật toán cốt lõi

### 3.1. Sơ đồ luồng xử lý toàn hệ thống

```mermaid
flowchart TD
    CAM["1. Nguồn Video / Camera Cổng<br/>(D:\\Vinhgate\\data\\raw_videos\\*.mp4)"] --> YOLO["2. Định vị biển số (YOLOv8)<br/>Trích xuất Tọa độ Bounding Box"]
    
    YOLO --> CROP["3. Cắt vùng ảnh biển số (Crop ROI)"]
    
    subgraph PREP ["4. Chuỗi Tiền Xử Lý Quang Học (OpenCV)"]
        direction TB
        CROP --> DESKEW["CanGocNghieng.py (Hough Lines Deskew)"]
        DESKEW --> RESIZE["PhongToAnh.py (Bicubic Scaling >= 180px)"]
        RESIZE --> CLAHE["TangTuongPhan.py (CLAHE kênh sáng L)"]
        CLAHE --> SHARP["LamSacNet.py (Unsharp Masking)"]
    end
    
    subgraph OCR ["5. Nhận Dạng & Chuẩn Hóa Biển Số VN"]
        direction TB
        SHARP --> PADDLE["PaddleOCR / EasyOCR Engine"]
        PADDLE --> SPLIT["PhanLoaiDong.py (Phân dòng 1 & 2 theo trục Y)"]
        SPLIT --> CORRECT["SuaLoiKyTu.py (Sửa lỗi số/chữ & sê-ri VN)"]
        CORRECT --> FORMAT["DinhDangBienSo.py (Định dạng chuẩn 37AB-12206)"]
    end
    
    FORMAT --> VOTE["6. Session Tracking & Majority Voting<br/>• Gom frame trong khoảng <= 1.2s<br/>• Bỏ phiếu mã tỉnh đa số<br/>• Chọn 1 ảnh cắt rõ nét nhất"]
    
    subgraph BACKEND ["7. Đối Chiếu Nghiệp Vụ CSDL MySQL (FastAPI)"]
        direction TB
        VOTE --> CHECK_BL{"Kiểm tra Danh sách đen?"}
        CHECK_BL -- "Có trong Blacklist" --> REJECT["TỪ CHỐI -> Giữ đóng Barie & Báo động đỏ"]
        CHECK_BL -- "Không" --> CHECK_INTERNAL{"Kiểm tra Xe Nội bộ / Phiếu Khách?"}
        CHECK_INTERNAL -- "Tìm thấy xe hợp lệ" --> ALLOW["CHO PHÉP -> Mở Barie"]
        CHECK_INTERNAL -- "Xe vãng lai chưa đăng ký" --> PENDING["CHỜ DUYỆT -> Bảo vệ xác nhận tay"]
        
        ALLOW --> DB_LOG["Ghi log luot_ra_vao & Ghép nối lượt Vào/Ra"]
        REJECT --> DB_LOG
        PENDING --> DB_LOG
    end
    
    DB_LOG --> WS["8. Máy chủ WebSocket /ws/gate"]
    WS --> UI["9. Web Dashboard Giám Sát (Real-time)<br/>• Cập nhật thông tin xe & ảnh chụp<br/>• Cập nhật số lượng xe trong trường<br/>• Vẽ biểu đồ Chart.js & Báo cáo"]
```

### 3.2. Thuật toán Session Tracking & Majority Voting
Khi một xe tiến qua cổng trường, camera ghi nhận từ 20 đến 80 frame có chứa biển số ở các khoảng cách và góc nhìn khác nhau. Nếu không gom nhóm, hệ thống sẽ ghi nhận trùng lặp nhiều lần cho một lượt xe. 

Hệ thống VinhGate 2.0 triển khai thuật toán:
1. **Gom nhóm phiên (Session Tracker)**: Mọi nhận diện diễn ra cách nhau $\le 1.2$ giây được tự động gom vào cùng 1 phiên xe duy nhất. Khi khoảng trống giữa hai lần quét $> 1.2$ giây, phiên cũ được chốt kết quả và chuyển sang xe tiếp theo.
2. **Bình chọn đa số mã tỉnh (Majority Voting)**: Thống kê tần suất xuất hiện của mã tỉnh 2 số đầu tiên (ví dụ: `37` Nghệ An). Các ứng viên có mã tỉnh trùng với mã đa số được cộng điểm trọng số ưu tiên.
3. **Chấm điểm chất lượng frame (Quality Score)**:
   $$\text{Score} = (\text{OCR\_Conf} \times 0.4) + (\text{YOLO\_Conf} \times 0.2) + \text{Điểm cấu trúc chuẩn} + \text{Tỉ lệ diện tích BBox}$$
   Thuật toán ưu tiên chọn frame khi xe ở gần camera nhất (diện tích biển số lớn nhất, ký tự rõ nét nhất) làm kết quả đại diện và lưu ảnh vào cơ sở dữ liệu.

---

<a id="4-cong-nghe"></a>
## 4. Kiến trúc công nghệ & Tổ chức ứng dụng

### 4.1. Công nghệ sử dụng
- **Ngôn ngữ nền tảng**: Python 3.10 – 3.12 (Hỗ trợ tốt trên Windows & Linux).
- **Học sâu & Thị giác máy tính**:
  - `ultralytics` (YOLOv8n Object Detection) — huấn luyện phát hiện biển số xe Việt Nam.
  - `opencv-python` (OpenCV 4.10+) — xử lý ảnh số, ma trận điểm ảnh, Hough Transform, không gian màu LAB.
  - `paddleocr` / `easyocr` — nhận dạng ký tự quang học.
- **Máy chủ Backend**:
  - `FastAPI` — Web framework hiệu năng cao, tự động sinh tài liệu Swagger UI.
  - `uvicorn` — ASGI Server tiêu chuẩn.
  - `WebSockets` — truyền tải dữ liệu sự kiện xe hai chiều thời gian thực.
  - `PyMySQL` — kết nối cơ sở dữ liệu MySQL với `DictCursor`.
  - `openpyxl` — tạo file báo cáo bảng tính Excel định dạng cao cấp.
- **Cơ sở dữ liệu**: MySQL Server 8.0, cấu trúc InnoDB, bảng mã `utf8mb4`.
- **Giao diện Giám sát (Frontend)**:
  - HTML5, CSS3 phong cách Flat Design tối ưu cho máy trạm trực ban.
  - Vanilla JavaScript kết nối WebSocket Client tự động phục hồi (Auto-reconnect).
  - `Chart.js` — trực quan hóa dữ liệu lưu lượng xe 24 giờ.

---

<a id="5-co-so-du-lieu"></a>
## 5. Cơ sở dữ liệu 13 bảng & Views thống kê

Cơ sở dữ liệu chuẩn hóa 3NF được lưu tại file [`database/schema.sql`](file:///d:/Vinhgate/database/schema.sql) và dữ liệu mẫu tại [`database/seed_data.sql`](file:///d:/Vinhgate/database/seed_data.sql).

### 5.1. Phân nhóm các bảng CSDL

#### Nhóm 1: Danh mục & Hạ tầng Cổng (3 bảng)
- `cong`: Danh mục các cổng của Trường ĐH Vinh (Cổng chính Lê Duẩn, Cổng phụ Nguyễn Viết Xuân...).
- `camera`: Quản lý thông tin IP camera, luồng RTSP và cổng phụ trách.
- `vai_tro` & `tai_khoan`: Quản lý người dùng hệ thống và quyền hạn (Quản trị viên, Bảo vệ trực cổng).

#### Nhóm 2: Đối tượng & Phương tiện Quản lý (4 bảng)
- `nguoi_dung`: Thông tin cán bộ, giảng viên và sinh viên ĐH Vinh (Mã SV/CB, Họ tên, Đơn vị, SĐT).
- `phuong_tien`: Thông tin xe đã đăng ký vé tháng của sinh viên/cán bộ (Biển số, loại xe, nhãn hiệu, màu sắc, thời hạn vé).
- `khach`: Hồ sơ khách liên hệ công tác tại trường (Họ tên, SĐT, CCCD, Đơn vị công tác).
- `dang_ky_khach`: Quản lý phiếu xe khách tạm thời theo Cách B (Mã tạm `VG-YYYYMMDD-XXXX`, biển số xe, người tiếp đón, hạn rời trường, trạng thái phiếu).

#### Nhóm 3: Sự kiện Ra Vào & An Ninh (4 bảng)
- `luot_ra_vao`: Nhật ký từng lượt xe qua cổng (Hướng Vào/Ra, biển số đọc được, biển số xác nhận, loại xe, độ tin cậy, kết quả Barie, liên kết lượt Vào - Ra).
- `hinh_anh_luot`: Đường dẫn lưu trữ ảnh toàn cảnh và ảnh cắt biển số rõ nét của từng lượt xe.
- `danh_sach_den`: Danh sách các biển số bị chặn tuyệt đối hoặc cảnh báo an ninh kèm lý do vi phạm.
- `canh_bao`: Nhật ký các sự kiện an ninh bất thường (Biển số trong Blacklist, xe ở lại quá giờ, xe ra không có dữ liệu vào, nhận diện độ tin cậy thấp).
- `nhat_ky_he_thong`: Ghi vết thao tác đăng nhập, mở barie cưỡng bức của bảo vệ.

#### Nhóm 4: SQL Views thống kê tức thời (2 Views)
- `v_xe_dang_trong_truong`: View tính toán tự động số lượng phương tiện hiện đang có mặt trong trường bằng cách ghép cặp lượt `VAO` hợp lệ gần nhất chưa có lượt `RA` đối ứng.
- `v_thong_ke_hom_nay`: View tổng hợp tổng lượt vào, tổng lượt ra, số cảnh báo chưa xử lý trong ngày phục vụ Dashboard.

---

<a id="6-cai-dat"></a>
## 6. Hướng dẫn cài đặt & Vận hành

### 6.1. Chuẩn bị môi trường
- Hệ điều hành: Windows 10/11 hoặc Linux (Ubuntu 22.04+).
- Python: Phiên bản **Python 3.10** đến **3.12** (khuyến nghị để tương thích trọn vẹn với cả PaddleOCR và PyTorch).
- MySQL Server 8.0 (khởi động cổng mặc định 3306).

### 6.2. Các bước cài đặt chi tiết

#### Bước 1: Khởi tạo môi trường ảo Python
Mở terminal PowerShell tại thư mục gốc dự án:
```powershell
# Tạo môi trường ảo venv
python -m venv venv

# Kích hoạt môi trường trên Windows PowerShell:
.\venv\Scripts\Activate.ps1

# Nâng cấp pip và cài đặt gói thư viện phụ thuộc:
pip install --upgrade pip
pip install -r requirements.txt
```

> **Lưu ý GPU:** Nếu máy tính trang bị card đồ họa NVIDIA rời, cài đặt PyTorch CUDA để tăng tốc suy luận:
> ```powershell
> pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124
> ```

#### Bước 2: Cấu hình biến môi trường (`.env`)
Tạo file `.env` từ file mẫu `.env.example`:
```powershell
cp .env.example .env
```
Mở file `.env` và điền thông số tài khoản MySQL của máy bạn:
```ini
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=hung123
DB_NAME=vinh_gate

SERVER_HOST=127.0.0.1
SERVER_PORT=8000
MIN_CONFIDENCE_THRESHOLD=0.75
COOLDOWN_SECONDS=30
```

#### Bước 3: Tự động khởi tạo Cơ sở Dữ liệu MySQL
Chạy script nạp tự động schema 13 bảng và dữ liệu mẫu ĐH Vinh:
```powershell
python scripts/init_db.py
```
*Kết quả:* Thông báo `Khởi tạo CSDL vinh_gate thành công với 13 bảng và 2 Views.`

#### Bước 4: Khởi chạy Máy chủ Backend & Web Dashboard
Chạy lệnh khởi động máy chủ FastAPI:
```powershell
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```
Sau khi máy chủ khởi động thành công, truy cập các địa chỉ trên trình duyệt web:
- 📹 **Màn hình Giám sát Cổng:** [http://localhost:8000/frontend/index.html](http://localhost:8000/frontend/index.html)
- 🚗 **Hồ sơ Xe & Lập Phiếu Khách:** [http://localhost:8000/frontend/vehicles.html](http://localhost:8000/frontend/vehicles.html)
- 📜 **Lịch sử Ra Vào & Báo Cáo:** [http://localhost:8000/frontend/history.html](http://localhost:8000/frontend/history.html)
- 📖 **Tài liệu Swagger API tương tác:** [http://localhost:8000/docs](http://localhost:8000/docs)

---

<a id="7-du-lieu-demo"></a>
## 7. Dữ liệu thử nghiệm & Kịch bản test nhanh

Dự án cung cấp sẵn dữ liệu video thực tế và bộ biển số mẫu để kiểm thử ngay lập tức mà không cần kết nối camera vật lý:

### 7.1. Video mẫu có sẵn trong thư mục `data/raw_videos/`
- `data/raw_videos/sample_test.mp4`: Video mô phỏng xe ô tô và xe máy di chuyển qua vạch quét.
- `data/raw_videos/nhaxe1_xemay_vao_20261019_sang_001.mp4`: Video quay thực tế tại Cổng Nhà xe 1 Trường ĐH Vinh.

### 7.2. Danh sách biển số thử nghiệm nghiệp vụ cổng
| Biển số | Loại xe | Tình trạng đối chiếu CSDL | Quyết định Barie | Ghi chú |
| :--- | :--- | :--- | :---: | :--- |
| **`37B2-68686`** | Xe máy | Xe sinh viên hợp lệ (SV Phan Văn Quân - CNTT) | **MỞ (CHO PHÉP)** | Xe nội bộ có vé tháng còn hiệu lực |
| **`37A-12345`** | Ô tô | Xe khách có phiếu hẹn trước (Khách Nguyễn Văn An) | **MỞ (CHO PHÉP)** | Tự động đổi trạng thái phiếu sang `DA_VAO` |
| **`37S1-99999`** | Xe máy | Nằm trong `danh_sach_den` | **ĐÓNG (TỪ CHỐI)** | Phát sinh cảnh báo an ninh mức Khẩn cấp |
| **`37B1-?234?`** | Xe máy | Nhận dạng độ tin cậy thấp (< 75%) | **CHỜ XÁC NHẬN** | Hiển thị nút cho bảo vệ nhập duyệt tay |

---

<a id="8-kich-ban-demo"></a>
## 8. Kịch bản trình diễn trước Hội đồng (10–15 phút)

Kịch bản gợi ý giúp nhóm hoàn thành phần trình bày mạch lạc, ấn tượng trước hội đồng đánh giá:

### ⏱️ Phần 1: Giới thiệu giao diện Giám sát trực ban (2 phút)
1. Mở trang [http://localhost:8000/frontend/index.html](http://localhost:8000/frontend/index.html).
2. Chỉ vào huy hiệu trạng thái: Nhấn mạnh kết nối **WebSocket: TRỰC TUYẾN**.
3. Chỉ vào 4 thẻ KPI đếm xe: Cho hội đồng thấy số lượng xe máy và ô tô đang có trong khuôn viên trường được truy vấn trực tiếp từ VIEW CSDL `v_xe_dang_trong_truong`.

### ⏱️ Phần 2: Trình diễn AI nhận diện video ngoại tuyến (3 phút)
1. Mở cửa sổ terminal, chạy lệnh:
   ```powershell
   python XuLyVideo.py data/raw_videos/sample_test.mp4
   ```
2. Thuyết minh tiến trình chạy: YOLOv8 quét frame $\to$ Chuỗi tiền xử lý OpenCV $\to$ OCR đọc ký tự $\to$ Thuật toán Session Tracking gom hàng chục frame thành 1 lượt xe duy nhất.
3. Mở thư mục `data/detected_plates/` và mở file `data/danh_sach_bien_so.csv` để chứng minh hệ thống đã trích xuất đúng 1 bức ảnh cắt rõ nét nhất cho từng xe và tính toán độ tin cậy.

### ⏱️ Phần 3: Thử nghiệm 3 ca nghiệp vụ kiểm soát cổng (4 phút)
Tại thanh điều khiển *"Kịch bản Test Nhanh Khi Demo Bảo Vệ"* trên trang `index.html`:
- **Ca 1 (Xe SV hợp lệ):** Nhấn **"Test Xe SV Hợp Lệ"** (`37B2-68686`).
  - *Kết quả cần thấy:* Huy hiệu Barie chuyển xanh lá: **"BARIE: ĐANG MỞ (CHO QUA)"**, hiển thị tên sinh viên Phan Văn Quân. Thẻ đếm xe trong trường tự động tăng thêm 1 xe.
- **Ca 2 (Xe khách có phiếu):** Nhấn **"Test Xe Khách Có Phiếu"** (`37A-12345`).
  - *Kết quả cần thấy:* Hệ thống đối chiếu đúng phiếu tạm Cách B của khách Nguyễn Văn An, cho phép mở cổng.
- **Ca 3 (Xe vi phạm trong Blacklist):** Nhấn **"Test Xe Blacklist"** (`37S1-99999`).
  - *Kết quả cần thấy:* Thanh Barie giữ nguyên màu xám **"BARIE: GIỮ ĐÓNG"**, giao diện xuất hiện khung cảnh báo màu đỏ: `[CẢNH BÁO DANH_SACH_DEN] Biển số trong DANH SÁCH ĐEN! Lý do: Xe nghi vấn trộm cắp`.

### ⏱️ Phần 4: Nghiệp vụ Xác nhận thủ công biển số mờ (2 phút)
1. Nhấn nút **"Test Biển Số Mờ (Cần duyệt)"**.
2. *Kết quả cần thấy:* Cột Kết quả trong bảng nhật ký chuyển sang nhãn màu vàng **CHỜ DUYỆT**, xuất hiện nút **"Xác Nhận Tay"**.
3. Bảo vệ nhấn nút "Xác Nhận Tay", hộp thoại hiện lên cho phép sửa lại biển số chính xác $\to$ Bấm xác nhận $\to$ Barie kích hoạt mở cho xe qua và ghi vết tài khoản bảo vệ đã xác nhận vào CSDL.

### ⏱️ Phần 5: Quản lý phương tiện, Biểu đồ & Xuất báo cáo (3 phút)
1. Chuyển sang trang **Quản lý Xe & Khách** (`vehicles.html`): Cho xem danh sách xe cán bộ/SV, tính năng tìm kiếm theo biển số tức thời, và danh sách đen.
2. Chuyển sang trang **Lịch sử & Báo Cáo** (`history.html`): Trình chiếu biểu đồ đường lưu lượng xe 24 giờ do thư viện Chart.js vẽ tự động từ API `/api/stats/hourly-traffic`.
3. Nhấn nút **"📥 Xuất Báo Cáo Excel (.xlsx)"**: Tải ngay file Excel được định dạng tiêu đề màu xanh lam chuyên nghiệp, chứng minh hệ thống sẵn sàng đưa vào quản lý hành chính thực tế.

---

<a id="9-cau-truc-thu-muc"></a>
## 9. Cấu trúc thư mục dự án

```text
Vinhgate/
├── ai/                                # Phân hệ AI & Thị giác Máy tính
│   ├── TienXuLy/                      # Gói thuật toán tiền xử lý hình ảnh OpenCV
│   │   ├── CanGocNghieng.py           # Thuật toán Deskew (Hough Lines) cân góc nghiêng
│   │   ├── PhongToAnh.py              # Phóng to nội suy bậc ba (Bicubic >= 180px)
│   │   ├── TangTuongPhan.py           # Tăng tương phản cục bộ CLAHE trên kênh L (LAB)
│   │   ├── LamSacNet.py               # Làm sắc nét viền Unsharp Masking khử nhòe
│   │   └── TienXuLyTongHop.py         # Pipeline kết nối tuần tự 4 bước tiền xử lý
│   ├── ChuanHoaBienSo/                # Gói module OCR & Chuẩn hóa biển số VN
│   │   ├── PaddleOCR_Engine.py        # Quản lý Engine OCR Singleton & fallback EasyOCR
│   │   ├── PhanLoaiDong.py            # Phân dòng 1 & 2 xe máy theo trục tọa độ Y
│   │   ├── SuaLoiKyTu.py              # Sửa lỗi nhầm lẫn quang học đặc thù biển VN
│   │   ├── DinhDangBienSo.py          # Định dạng chuẩn (xe thường, xe điện 37AB)
│   │   └── DocBienSo.py               # Hàm điều phối đọc trọn gói từ ảnh thô
│   ├── CatKhungHinh.py                # AI lọc frame có xe từ video để gán nhãn Roboflow
│   ├── PhatHienBienSo.py              # Nạp YOLOv8 phát hiện tọa độ biển số (BBox)
│   └── TheoDoiHuongXe.py              # Thuật toán Delta Y theo dõi hướng Vào/Ra & Cooldown
├── backend/                           # Máy chủ Backend (FastAPI + WebSocket)
│   ├── main.py                        # Điểm khởi chạy FastAPI & WebSocket /ws/gate
│   ├── core/
│   │   ├── config.py                  # Cấu hình biến môi trường và đường dẫn hệ thống
│   │   ├── db.py                      # Cấu hình chuỗi kết nối MySQL
│   │   └── db_connection.py           # Quản lý kết nối PyMySQL và thực thi kịch bản SQL
│   ├── services/
│   │   ├── gate_service.py            # Nghiệp vụ kiểm tra xe, đếm xe, mở Barie, Blacklist
│   │   └── guest_service.py           # Nghiệp vụ tạo và kiểm soát phiếu khách (Cách B)
│   └── routers/
│       ├── api_gate.py                # API xử lý sự kiện qua cổng & xác nhận tay
│       ├── api_vehicles.py            # API quản lý xe nội bộ, phiếu khách, danh sách đen
│       └── api_stats.py               # API thống kê lưu lượng xe, xuất báo cáo Excel
├── database/                          # Cơ sở dữ liệu MySQL
│   ├── schema.sql                     # Kịch bản tạo 13 bảng 3NF và 2 Views thống kê
│   ├── seed_data.sql                  # Dữ liệu khởi tạo mẫu của Trường ĐH Vinh
│   ├── migrations/                    # Kịch bản cập nhật CSDL
│   └── queries/                       # Các câu truy vấn nghiệp vụ phức tạp
├── frontend/                          # Giao diện Web Dashboard Giám Sát
│   ├── index.html                     # Màn hình Giám sát camera trực ban và điều khiển barie
│   ├── vehicles.html                  # Màn hình Quản lý xe nội bộ và lập phiếu khách
│   ├── history.html                   # Màn hình Tra cứu lịch sử & Biểu đồ thống kê
│   ├── css/dashboard.css              # Giao diện phẳng hiện đại tối ưu máy trạm
│   └── js/
│       ├── websocket_client.js        # Script kết nối WebSocket client có auto-reconnect
│       └── charts.js                  # Script vẽ biểu đồ đường 24 giờ bằng Chart.js
├── models/                            # Trọng số học sâu
│   └── best.pt                        # Trọng số YOLOv8 đã huấn luyện nhận diện biển số
├── data/                              # Dữ liệu media phục vụ chạy thử
│   ├── raw_videos/                    # Chứa video quay thực tế tại Cổng ĐH Vinh
│   ├── detected_plates/               # Chứa ảnh cắt biển số rõ nét nhất của từng xe
│   └── danh_sach_bien_so.csv          # File CSV tổng hợp kết quả đọc video
├── scripts/
│   ├── init_db.py                     # Script Python tự động nạp database lúc cài đặt
│   └── generate_test_video.py         # Script sinh video mẫu mô phỏng xe chạy qua cổng
├── XuLyVideo.py                       # File chạy chính xử lý video ngoại tuyến (Session Tracking)
├── process_video.py                   # Wrapper tương thích ngược gọi sang XuLyVideo.py
├── requirements.txt                   # Danh mục thư viện Python cần thiết
├── .env.example                       # File mẫu cấu hình tham số môi trường
└── README.md                          # Tài liệu hướng dẫn này
```

---

<a id="10-kiem-thu"></a>
## 10. Kiểm thử & Đánh giá độ chính xác

### 10.1. Đánh giá chuỗi tiền xử lý ảnh (`TienXuLy`)
Kiểm nghiệm trên tập 250 khung hình xe máy thực tế tại cổng trường Đại học Vinh trong các điều kiện bất lợi:
- **Xe chạy chéo góc (nghiêng từ 10° – 25°)**: Sau khi qua bộ lọc `CanGocNghieng.py`, góc lệch ký tự giảm về $< 3^\circ$, giúp OCR nhận diện đúng dòng tăng thêm **28.4%**.
- **Khu vực lóa nắng hoặc bóng râm rọi qua mái tôn**: Áp dụng `TangTuongPhan.py` (CLAHE) nâng độ tương phản giữa ký tự đen và nền trắng biển số, giảm thiểu lỗi nhận diện thiếu nét ký tự.
- **Xe đang di chuyển (khử nhòe viền)**: `LamSacNet.py` (Unsharp Masking) giúp cải thiện tỷ lệ phân biệt giữa các chữ cái dễ nhầm lẫn như `'B'` và `'8'`, `'D'` và `'0'`.

### 10.2. Tốc độ suy luận (Inference Speed)
- **Môi trường CPU (Intel Core i5 / AMD Ryzen 5 thế hệ 11 trở lên)**:
  - Phát hiện biển số (YOLOv8n): ~30 – 45ms.
  - Chuỗi tiền xử lý + OCR (EasyOCR / PaddleOCR): ~80 – 120ms.
  - Tổng thời gian xử lý: $< 180$ms/lượt xe (đáp ứng tốt điều kiện xe dừng hoặc đi chậm qua cổng).
- **Môi trường GPU (NVIDIA RTX 3050 / 4050 Laptop trở lên)**:
  - Tổng thời gian xử lý trọn gói: $< 35$ms/lượt xe (đạt tốc độ thời gian thực 30 FPS).

---

<a id="11-loi-thuong-gap"></a>
## 11. Lỗi thường gặp & Cách khắc phục

### 1. Lỗi không kết nối được MySQL (`Can't connect to MySQL server`)
- **Nguyên nhân**: Dịch vụ MySQL Server trên máy tính chưa được khởi động hoặc cấu hình sai cổng.
- **Khắc phục**: 
  - Mở công cụ `Services` trên Windows $\to$ Tìm dịch vụ `MySQL80` $\to$ Bấm chuột phải chọn **Start**.
  - Kiểm tra lại mật khẩu và cổng kết nối trong file `.env` đã trùng khớp với MySQL của máy chưa.

### 2. Cảnh báo `[OCR CẢNH BÁO] Không thể nạp PaddleOCR`
- **Nguyên nhân**: Môi trường Python (đặc biệt là Python 3.13 / 3.14) chưa có bản phát hành nhị phân chính thức cho `paddlepaddle`.
- **Khắc phục**: Bạn **không cần lo lắng**, hệ thống đã tích hợp sẵn cơ chế dự phòng tự động chuyển sang `EasyOCR` và vẫn nhận diện biển số bình thường. Để sử dụng trọn vẹn PaddleOCR gốc, hãy sử dụng môi trường ảo Python 3.10 hoặc 3.11.

### 3. Cổng mạng 8000 đang bị chiếm dụng (`Address already in use`)
- **Nguyên nhân**: Một tiến trình ứng dụng khác đang chiếm cổng 8000.
- **Khắc phục**: Khởi chạy ứng dụng với một cổng khác:
  ```powershell
  uvicorn backend.main:app --host 127.0.0.1 --port 8001 --reload
  ```

---

<a id="12-gioi-han-phat-trien"></a>
## 12. Giới hạn hiện tại & Hướng phát triển

### 12.1. Giới hạn phiên bản hiện tại
- **Luồng Camera trực tiếp**: Khung camera trên màn hình Giám sát hiện tại là giao diện mô phỏng trực quan phục vụ demo qua kịch bản, chưa tích hợp module giải mã luồng RTSP/WebRTC trực tiếp từ camera IP vật lý ngoài trời.
- **Đăng nhập phân quyền bảo vệ**: Cơ sở dữ liệu đã thiết kế hoàn chỉnh bảng `tai_khoan` và `vai_tro`, tuy nhiên giao diện Dashboard hiện tại đang mặc định phiên làm việc cho ca trực của Bảo vệ Nguyễn Văn Bảo (`user_id = 1`) mà chưa có màn hình Login/Logout riêng biệt.
- **Xử lý biển số hư hại nặng**: Trường hợp biển số bị bùn đất che lấp hoàn toàn hoặc biển số gãy nát vẫn cần sự can thiệp của chức năng "Xác nhận tay" từ nhân viên trực ban.

### 12.2. Hướng phát triển tiếp theo
1. Tích hợp module thu nhận luồng video RTSP thời gian thực từ hệ thống Camera giám sát thực tế của Trường Đại học Vinh.
2. Kết nối phần cứng điều khiển thanh chắn Barie tự động thông qua vi điều khiển ESP32 / Arduino qua giao tiếp Serial / Modbus.
3. Mở rộng cơ chế xác thực kép: Tích hợp đầu đọc thẻ từ RFID sinh viên kết hợp với biển số xe để triệt tiêu 100% tình trạng gian lận thẻ xe.
4. Phát triển ứng dụng di động dành riêng cho sinh viên để tra cứu lịch sử gửi xe và nhận thông báo khi có bất thường về phương tiện.

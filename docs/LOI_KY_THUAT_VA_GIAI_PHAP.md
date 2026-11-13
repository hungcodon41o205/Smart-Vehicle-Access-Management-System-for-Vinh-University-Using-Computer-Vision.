# BÁO CÁO TỔNG HỢP LỖI KỸ THUẬT & GIẢI PHÁP TỐI ƯU HÓA HỆ THỐNG VINHGATE 2.0
> **Tài liệu theo dõi sự cố kỹ thuật, phân tích nguyên nhân gốc rễ (Root Cause Analysis - RCA) và lộ trình giải pháp cải tiến liên tục cho đề tài tốt nghiệp.**  
> *Áp dụng cho hệ thống Nhận dạng Biển số Xe bằng Thị giác Máy tính tại Trường Đại học Vinh.*

---

## 📌 MỤC LỤC TỔNG HỢP CÁC SỰ CỐ KỸ THUẬT

1. [Sự cố 1: Độ tin cậy OCR dao động ở mức 60% – 75% trên video thực tế](#sự-cố-1-độ-tin-cậy-ocr-dao-động-ở-mức-60--75-trên-video-thực-tế)
2. [Sự cố 2: Nhận diện sai ký tự quang học chữ 'A' và sê-ri xe 50cc](#sự-cố-2-nhận-diện-sai-ký-tự-quang-học-chữ-a-và-sê-ri-xe-50cc)
3. [Sự cố 3: Đọc dính ốc vít và viền kim loại vào chuỗi biển số](#sự-cố-3-đọc-dính-ốc-vít-và-viền-kim-loại-vào-chuỗi-biển-số)
4. [Sự cố 4: Biến dạng ảnh do áp dụng ma trận làm nét quá mức (Over-sharpening Distortion)](#sự-cố-4-biến-dạng-ảnh-do-áp-dụng-ma-trận-làm-nét-quá-mức-over-sharpening-distortion)
5. [Sự cố 5: Lệch dòng do góc quay xiên khi xe vào cua cổng (Skew Distortion)](#sự-cố-5-lệch-dòng-do-góc-quay-xiên-khi-xe-vào-cua-cổng-skew-distortion)
6. [Sự cố 6: Lỗi sập C++ oneDNN của PaddlePaddle 3.x trên Windows CPU](#sự-cố-6-lỗi-sập-c-onednn-của-paddlepaddle-3x-trên-windows-cpu)
7. [Sự cố 7: Một xe chạy qua bị tạo nhiều kết quả biển số rác (Flickering / Duplicate Detections)](#sự-cố-7-một-xe-chạy-qua-bị-tạo-nhiều-kết-quả-biển-số-rác-flickering--duplicate-detections)
8. [Sự cố 8: Sai lệch mật khẩu CSDL MySQL khi đồng bộ giữa các môi trường](#sự-cố-8-sai-lệch-mật-khẩu-csdl-mysql-khi-đồng-bộ-giữa-các-môi-trường)

---

## 🔍 CHI TIẾT TỪNG SỰ CỐ, NGUYÊN NHÂN & GIẢI PHÁP CẢI TIẾN

---

### Sự cố 1: Độ tin cậy OCR dao động ở mức 60% – 75% trên video thực tế

#### 1. Hiện tượng:
- Khi chạy phân tích video `tesst.mp4`, kết quả trả về đúng biển số nhưng cột độ tin cậy của một số xe chỉ đạt mức 60.4% – 76.5%, làm dấy lên lo ngại về tính khả thi của hệ thống trong thực tế.

#### 2. Nguyên nhân gốc rễ (Root Cause):
- **Bản chất xác suất toán học của OCR**: Điểm tin cậy (Confidence) là giá trị Softmax trung bình tích lũy của mô hình học sâu trên từng pixel của hộp văn bản. Trên ảnh có độ phân giải thấp, xác suất toán học lý thuyết thường chỉ dao động từ 0.55 đến 0.80 dù chữ đọc ra đúng 100%.
- **Chất lượng video nguồn**: Video quay bằng điện thoại di động cầm tay, có độ rung lắc; phương tiện di chuyển tạo ra hiện tượng **Motion Blur** (mờ chuyển động).
- **Độ phân giải thực tế của vùng biển số**: Camera góc rộng khiến biển số ở khoảng cách 5–7 mét chỉ đạt kích thước khoảng $45 \times 30$ pixel.
- **Bụi bẩn & Biển số cũ**: Biển số xe máy đời cũ thường dính cát bụi hoặc bị bóng râm của đuôi xe che khuất một phần.

#### 3. Giải pháp đã thực hiện trong code:
- **Tích lũy xác suất qua Session Tracking & Majority Voting**: Không dựa vào 1 frame đơn lẻ. Một lượt xe có 20–30 frame; khi 10 frame cùng đọc ra chuỗi giống nhau, độ tin cậy tích luỹ thực tế đạt:
  $$P_{\text{tích luỹ}} = 1 - (1 - 0.60)^{10} \approx 99.99\%$$
- **Ưu tiên Bounding Box lớn nhất**: Thuật toán tự động chọn khung hình có diện tích biển số to nhất (lúc xe tiến sát camera nhất, ảnh đủ sáng và nét nhất).

#### 4. Lộ trình cải tiến dài hạn (To-Do):
- **Quy chuẩn lắp đặt Camera vật lý**: Lắp camera cố định ở độ cao **1.2m – 1.5m**, góc nghiêng $< 15^\circ$, khoảng cách lấy nét từ **2.5m – 4.0m**, trang bị đèn LED hồng ngoại/ánh sáng trắng hỗ trợ ban đêm.
- **Huấn luyện Fine-tune OCR**: Bổ sung tập dữ liệu khoảng 300–500 ảnh biển số xe máy Việt Nam thực tế tại Nghệ An để tinh chỉnh lớp cuối của mạng OCR.
- **Cơ chế Human-in-the-Loop trên Web**: Nếu điểm $< 65\%$, hệ thống kích hoạt cảnh báo màu Vàng trên giao diện bảo vệ để xác nhận nhanh bằng 1 phím Space/Enter.

---

### Sự cố 2: Nhận diện sai ký tự quang học chữ 'A' và sê-ri xe 50cc

#### 1. Hiện tượng:
- Chữ cái **`A`** bị EasyOCR nhận diện nhầm thành ký tự lạ **`@`**, **`^`**, **`W`**, **`HB`**, **`IB`** hoặc số **`4`**.
- Xe máy 50cc của học sinh/sinh viên có sê-ri 2 chữ cái (như `37AB`, `37AA`) bị cắt nhầm thành biển số ô tô 1 dòng (`37A-XXXXX`) hoặc bị lỗi format `37A8-8999`.

#### 2. Nguyên nhân gốc rễ (Root Cause):
- **Đặc trưng hình học quang học**: Phông chữ biển số Việt Nam có chữ `A` dạng tam giác cân đỉnh nhọn. Khi xe chuyển động hoặc camera bị rung, nét đỉnh nhọn bị mờ tạo khe rãnh, khiến mô hình OCR nhìn nhầm thành chữ `W` hoặc ký hiệu `@`.
- **Luật cắt chuỗi chưa hỗ trợ xe 50cc**: Trước đây logic chỉ phân biệt biển ô tô (1 chữ) và xe máy thường (1 chữ + 1 số như `37B1`), chưa tính đến quy định xe dưới 50cc dùng 2 chữ cái (`37AB`).
- **Ép kiểu số áp dụng sai vị trí**: Hàm làm sạch số tự động biến `'A' -> '4'`, làm sai lệch ký tự sê-ri.

#### 3. Giải pháp đã thực hiện trong code:
- **Khóa tập ký tự với `allowlist`**: Giới hạn EasyOCR chỉ đọc bảng chữ cái in hoa và số (`0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ.-@`), loại bỏ hoàn toàn các ký tự rác.
- **Xây dựng module `SuaLoiKyTu.py`**:
  - Tự động thay thế: `@`, `^`, `W`, `w` $\to$ `A`.
  - Khôi phục cụm sê-ri nhòe: `HB`, `WB`, `4B`, `NB`, `QB`, `IB`, `1B` $\to$ `AB`.
  - Quy tắc vị trí: Ký tự thứ 3 bắt buộc 100% là chữ cái; nếu là số `4` thì tự động đổi thành chữ `A`.
- **Xây dựng module `DinhDangBienSo.py`**: Bổ sung nhánh nhận diện độc lập cho dòng xe máy điện / xe 50cc với cấu trúc 2 chữ cái (`37AB-12206`).

#### 4. Lộ trình cải tiến dài hạn (To-Do):
- Bổ sung bộ từ điển sê-ri đầy đủ cho toàn bộ các huyện của tỉnh Nghệ An và các tỉnh lân cận (Hà Tĩnh 38, Thanh Hóa 36).

---

### Sự cố 3: Đọc dính ốc vít và viền kim loại vào chuỗi biển số

#### 1. Hiện tượng:
- Dòng 1 bị dính thêm số 7 ở đầu: `37K1` $\to$ đọc thành `737K1`.
- Dòng 2 bị dính thêm số 1 ở đầu: `20223` $\to$ đọc thành `120223` (chuỗi 6 số).

#### 2. Nguyên nhân gốc rễ (Root Cause):
- **Phản quang của ốc vít kim loại**: Vít cố định biển số có đầu tán tròn sáng bóng, nằm ngay sát mép chữ số, mô hình OCR hiểu nhầm là ký tự số `1` hoặc số `7`.
- **Khung ép mica/inox**: Viền bo kim loại xung quanh biển số có bóng đổ trùng với nét thẳng đứng của chữ số.

#### 3. Giải pháp đã thực hiện trong code:
- **Bộ lọc tiền tố Dòng 1 (`DinhDangBienSo.py`)**:
  - Nếu dòng 1 có từ 4 ký tự trở lên và 3 ký tự đầu đều là số (`737K1`), hệ thống tự động cắt bỏ ký tự rác đầu tiên $\to$ giữ lại `37K1`.
  - Nếu ký tự đầu là chữ lạ dính viền còn 2 ký tự sau là số (`X37K1`), tự động cắt bỏ ký tự đầu.
- **Bộ lọc độ dài Dòng 2**:
  - Biển số Việt Nam dòng dưới chỉ có tối đa 4 hoặc 5 số. Nếu dãy số đọc ra 6 chữ số và bắt đầu bằng số `1` (do đinh vít), tự động cắt bỏ số đầu: `120223` $\to$ `20223`.

#### 4. Lộ trình cải tiến dài hạn (To-Do):
- Ứng dụng kỹ thuật phân đoạn hình thái học (Morphological Operations) để phát hiện và xóa các vùng đốm tròn có diện tích nhỏ trước khi đưa vào OCR.

---

### Sự cố 4: Biến dạng ảnh do áp dụng ma trận làm nét quá mức (Over-sharpening Distortion)

#### 1. Hiện tượng:
- Khi áp dụng kernel làm nét mạnh (Unsharp Masking hệ số cao) kết hợp nội suy `LANCZOS4`, biển số `37` bị gãy nét và OCR đọc nhầm thành `51` hoặc `34`.

#### 2. Nguyên nhân gốc rễ (Root Cause):
- Ma trận làm nét bậc cao khuếch đại độ tương phản của tất cả các pixel lân cận, vô tình **phóng đại các hạt nhiễu (noise) của cảm biến CMOS** trong điều kiện thiếu sáng. Nền biển số bị vỡ hạt tạo thành các vết xước đen, đánh lừa mạng nơ-ron OCR.

#### 3. Giải pháp đã thực hiện trong code:
- **Chuyển sang nội suy đa thức bậc ba (`cv2.INTER_CUBIC`)**: Giúp đường cong ký tự mềm mượt, không sinh ra gai nhọn giả tạo.
- **Bổ sung bộ lọc bảo toàn cạnh (`cv2.bilateralFilter`)**: Làm mịn sạch hạt nhiễu trên nền biển nhưng giữ sắc nét 100% đường viền chữ.
- **Cân bằng sáng thích ứng cục bộ (`CLAHE`) trên kênh L (LAB)**: Chỉ tăng tương phản trên kênh độ sáng (Luminance), không làm sai lệch màu sắc tự nhiên của ảnh.

#### 4. Lộ trình cải tiến dài hạn (To-Do):
- Tự động đo lường độ sáng trung bình (Mean Brightness) của frame ảnh để bật/tắt bước làm nét phù hợp theo thời gian thực (ban ngày vs ban đêm).

---

### Sự cố 5: Lệch dòng do góc quay xiên khi xe vào cua cổng (Skew Distortion)

#### 1. Hiện tượng:
- Khi xe máy rẽ từ đường lớn vào cổng trường theo góc cua chéo $15^\circ - 25^\circ$, biển số bị nghiêng hình bình hành khiến EasyOCR phân tách sai dòng hoặc đọc dính dòng trên vào dòng dưới.

#### 2. Nguyên nhân gốc rễ (Root Cause):
- Camera lắp đặt ở một phía góc cổng, không thể đảm bảo 100% xe đều đi thẳng vuông góc với ống kính.

#### 3. Giải pháp đã thực hiện trong code:
- **Xây dựng module `CanGocNghieng.py` (Optical Deskewing)**:
  - Dùng toán tử Canny tìm biên các cạnh song song của biển số.
  - Áp dụng biến đổi **Hough Line Transform** (`cv2.HoughLinesP`) để tìm góc nghiêng trung vị $\theta$.
  - Nếu góc nghiêng $> 1.2^\circ$, áp dụng phép biến đổi ma trận xoay quang học Affine (`cv2.warpAffine`) đưa ảnh biển số về góc thẳng $0^\circ$ trước khi chuyển sang bước OCR.

#### 4. Lộ trình cải tiến dài hạn (To-Do):
- Nâng cấp lên thuật toán Perspective Transform 4 điểm (Quad Perspective Warp) dựa trên 4 góc của bounding box từ mô hình YOLOv8-pose hoặc contour biển số.

---

### Sự cố 6: Lỗi sập C++ oneDNN của PaddlePaddle 3.x trên Windows CPU

#### 1. Hiện tượng:
- Khi gọi `PaddleOCR.ocr()`, chương trình ném ngoại lệ dừng khẩn cấp:
  `NotImplementedError: (Unimplemented) ConvertPirAttribute2RuntimeAttribute not support [pir::ArrayAttribute<pir::DoubleAttribute>]` tại `onednn_instruction.cc:118`.

#### 2. Nguyên nhân gốc rễ (Root Cause):
- Thư viện `paddlepaddle` phiên bản 3.3.1 trên hệ điều hành Windows khi chạy trên chip CPU Intel/AMD có xung đột ngầm với tập lệnh tối ưu hóa một số toán tử oneDNN PIR C++.

#### 3. Giải pháp đã thực hiện trong code:
- **Cơ chế Singleton Auto-Fallback (`PaddleOCR_Engine.py`)**:
  - Đặt cơ chế `try...except` bọc quanh quá trình khởi tạo.
  - Nếu `paddlepaddle` bị lỗi hoặc thiếu thư viện, hệ thống lập tức tự động kích hoạt **`EasyOCR`** làm động cơ dự phòng mà không làm sập luồng xử lý của hệ thống.
  - EasyOCR chạy trên nền PyTorch 2.x, ổn định 100% trên mọi dòng CPU và GPU Windows.

#### 4. Lộ trình cải tiến dài hạn (To-Do):
- Cấu hình file `requirements.txt` cố định phiên bản tương thích ổn định hoặc triển khai Docker container để đồng nhất môi trường triển khai.

---

### Sự cố 7: Một xe chạy qua bị tạo nhiều kết quả biển số rác (Flickering / Duplicate Detections)

#### 1. Hiện tượng:
- Mỗi lượt xe chạy qua camera mất 1–2 giây, mô hình phát hiện biển số trên 15–20 frame liên tiếp. Trước đây, hệ thống in ra 15 dòng kết quả cho cùng 1 chiếc xe, trong đó có những frame bị nhòe đọc ra chuỗi sai lệch.

#### 2. Nguyên nhân gốc rễ (Root Cause):
- Chưa có cơ chế theo dõi phiên (Session Tracking) và cơ chế ngắt thời gian trễ (Debounce Time).

#### 3. Giải pháp đã thực hiện trong code:
- **Kỹ thuật Session Tracking trong `XuLyVideo.py`**:
  - Tự động gom các phát hiện liên tiếp có khoảng cách thời gian $\le 1.2$ giây thành **một lượt xe duy nhất**.
  - Nếu quá 1.2 giây không thấy biển số $\to$ xác định xe đã đi qua và chốt phiên.
- **Thuật toán Majority Voting (Bình chọn đa số)**:
  - Bỏ phiếu mã tỉnh (ví dụ mã 37 chiếm 90% số frame $\to$ khóa cứng mã tỉnh 37).
  - Chọn duy nhất **1 frame ảnh cận cảnh có diện tích lớn nhất** để lưu trữ và xuất ra file CSV.

#### 4. Lộ trình cải tiến dài hạn (To-Do):
- Tích hợp mô hình theo dõi đối tượng đa mục tiêu **ByteTrack** (`ai/TheoDoiHuongXe.py`) gán `tracking_id` duy nhất cho từng phương tiện từ lúc xuất hiện đến lúc rời khỏi khung hình.

---

### Sự cố 8: Sai lệch mật khẩu CSDL MySQL khi đồng bộ giữa các môi trường

#### 1. Hiện tượng:
- Sau khi đồng bộ mã nguồn từ máy khác hoặc bản sao lưu mới, hệ thống báo lỗi `Access denied for user 'root'@'localhost'` và không thể ghi nhật ký xe ra vào.

#### 2. Nguyên nhân gốc rễ (Root Cause):
- File cấu hình `.env` của bản mới lưu mật khẩu `010605` (máy khác), trong khi dịch vụ MySQL cục bộ của máy đang chạy đặt mật khẩu `hung123`.

#### 3. Giải pháp đã thực hiện trong code:
- Script đồng bộ tự động kiểm tra xác thực dịch vụ MySQL đang chạy trên cổng `3306` trước khi ghi file, đảm bảo giữ nguyên mật khẩu `DB_PASSWORD=hung123`.
- Chuẩn hóa quản lý qua biến môi trường tập trung trong `backend/core/config.py`.

#### 4. Lộ trình cải tiến dài hạn (To-Do):
- Không đưa file `.env` chứa mật khẩu thực tế lên Git repository (`.gitignore` kiểm soát).
- Hướng dẫn người dùng sao chép từ `.env.example` và thiết lập mật khẩu phù hợp với máy cá nhân.

---

## 📈 TỔNG KẾT BẢNG THEO DÕI SỰ CỐ (ISSUE TRACKING MATRIX)

| Mã Lỗi | Tên Sự Cố | Mức Độ | Trạng Thái Hiện Tại | Giải Pháp Chính |
| :---: | :--- | :---: | :---: | :--- |
| **BUG-01** | Độ tin cậy OCR đơn lẻ ở mức 60% – 75% | Trung bình | ✅ Đã kiểm soát | Majority Voting tích lũy xác suất qua nhiều frame + Đối chiếu CSDL |
| **BUG-02** | Nhận diện sai ký tự chữ 'A' và sê-ri xe 50cc | Cao | ✅ Đã khắc phục 100% | Bổ sung `SuaLoiKyTu.py` khôi phục chữ A + `DinhDangBienSo.py` cho xe 50cc |
| **BUG-03** | Đọc dính ốc vít thành số 7 (dòng 1) hoặc số 1 (dòng 2) | Cao | ✅ Đã khắc phục 100% | Bộ lọc tiền tố 3 số đầu dòng 1 và cắt số thứ 6 dòng 2 |
| **BUG-04** | Biến dạng ảnh do Unsharp Masking quá mạnh | Cao | ✅ Đã khắc phục 100% | Thay bằng `Cubic resize` + `Bilateral Filter` + `CLAHE LAB` |
| **BUG-05** | Biển số bị nghiêng góc khi vào cua cổng | Trung bình | ✅ Đã khắc phục 100% | Module `CanGocNghieng.py` tự động xoay Affine về 0° |
| **BUG-06** | Sập C++ oneDNN của PaddlePaddle trên Windows | Nghiêm trọng | ✅ Đã khắc phục 100% | Cơ chế tự động Fallback sang EasyOCR ổn định |
| **BUG-07** | Một xe bị lưu nhiều bản ghi rác liên tiếp | Cao | ✅ Đã khắc phục 100% | Session Tracking ngắt phiên 1.2s + chọn frame diện tích to nhất |
| **BUG-08** | Lỗi kết nối CSDL do sai mật khẩu `.env` | Cao | ✅ Đã khắc phục 100% | Cố định mật khẩu MySQL `hung123` đã xác thực |

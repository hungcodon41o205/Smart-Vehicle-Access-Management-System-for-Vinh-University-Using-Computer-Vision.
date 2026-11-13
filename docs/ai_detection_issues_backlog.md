# SỔ TAY GHI NHẬN LỖI & KẾ HOẠCH NÂNG CẤP PHÂN HỆ AI (AI CORE BACKLOG)
**Dự án:** Hệ thống Quản lý Xe Ra Vào Đại học Vinh bằng Thị giác Máy tính (VinhGate)  
**Ngày ghi nhận:** 29/10/2026  
**Trạng thái:** Tạm lưu để chuyển sang Thiết kế CSDL, sẽ quay lại xử lý sau.

---

### VẤN ĐỀ 1: BỎ LỠ 1 XE (Khoảng giây thứ 25 - 30 trong video)
* **Hiện tượng:** Xe máy đi vào luồng cổng nhưng không xuất hiện trong bảng tổng kết cuối video.
* **Nguyên nhân kỹ thuật:**
  1. Ngưỡng tin cậy YOLOv8 đang đặt `conf_threshold = 0.28`. Xe đi ở góc xa khiến độ tin cậy rơi vào khoảng 21% - 29% nên bị bộ lọc bỏ qua.
  2. Kích thước bounding box khi ở xa quá nhỏ (~55x22 px), PaddleOCR trả về chuỗi rỗng `""`. Điều kiện `len(text) >= 4` trong code tự động bỏ qua.
* **Vị trí cần sửa:**
  * File: `src/core/video_detector.py` (Hàm `process_video_stream`) -> Điều chỉnh `conf_threshold` từ `0.28` xuống `0.20 - 0.22`.
  * File: `src/core/preprocessor.py` (Hàm `preprocess_plate`) -> Bổ sung tự động resize nội suy Cubic 2x-3x nếu chiều rộng ảnh cắt < 100px.

---

### VẤN ĐỀ 2: 1 XE RA 4 KẾT QUẢ KHÁC NHAU (`37A-K...`, `37A-R...`, `37A-N...`, `37A-M...`)
* **Hiện tượng:** Cùng 1 xe máy điện/50cc đi qua trong 1.5 giây nhưng tạo thành 4 dòng lịch sử với 4 biển số khác nhau. Biển số thật là `37AN-03879`.
* **Nguyên nhân kỹ thuật:**
  1. Biến `detected_history` trong `video_detector.py` đang dùng chuỗi biển số làm Key từ điển (`detected_history[text]`). Mỗi khi OCR đọc lệch 1 ký tự (`N` thành `K, R, M` do rung lắc/mờ chuyển động), hệ thống coi đó là 1 chiếc xe mới hoàn toàn.
  2. Chưa có cơ chế Session Tracker (theo dõi tâm Bounding Box theo thời gian) và chưa có thuật toán Voting/Lấy độ tin cậy cao nhất của cả lượt xe.
* **Vị trí cần sửa:**
  * File: `src/core/video_detector.py` (Hàm `process_video_stream`) -> Bổ sung Vehicle Session Tracker: Gom các frame cùng một vị trí di chuyển thành 1 lượt xe duy nhất, thu thập danh sách ứng viên (candidate pool) và chốt biển số có `ocr_conf` cao nhất (`37AN-03879` đạt 98.53%).

---

### VẤN ĐỀ 3: 5 BIỂN SỐ BỊ IN SAI ĐỊNH DẠNG KIỂU (`37A-B...`, `37A-K...`, `37A-R...`, `37A-N...`, `37A-M...`)
* **Hiện tượng:** Biển số xe máy điện / xe dưới 50cc có sê-ri 2 chữ cái (`37AN`, `37AB`) bị cắt sai thành kiểu ô tô 1 dòng (`37A-N03879`, `37A-B12206`).
* **Nguyên nhân kỹ thuật:**
  * Trong `src/core/plate_reader.py` (dòng 117-125), logic chỉ kiểm tra:
    ```python
    if full_text[2].isalpha() and full_text[3].isdigit() and len(full_text) >= 8:
        # Biển xe máy 1 chữ + 1 số: 37B2-12345
        formatted = f"{full_text[:4]}-{full_text[4:]}"
    else:
        # Mặc định là ô tô: 37A-12345
        formatted = f"{full_text[:3]}-{full_text[3:]}"
    ```
    Với biển `37AN03879`, ký tự thứ 4 là `N` (không phải chữ số), nên code nhảy vào nhánh `else` và cắt thành `37A-N03879`.
* **Vị trí cần sửa:**
  * File: `src/core/plate_reader.py` (Hàm `read_vietnamese_plate` và `correct_ocr_confusions`) -> Bổ sung nhánh nhận diện sê-ri 2 chữ cái cho xe máy:
    ```python
    if full_text[2].isalpha() and full_text[3].isalpha():
        # Biển xe máy điện / xe 50cc: 37AN-03879
        formatted = f"{full_text[:4]}-{full_text[4:]}"
    ```

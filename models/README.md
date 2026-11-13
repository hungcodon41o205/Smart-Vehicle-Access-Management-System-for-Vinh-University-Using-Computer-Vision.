# Thư mục Trọng số AI (Models) - VinhGate

Thư mục này chứa các file trọng số của mô hình học sâu sau khi đã huấn luyện hoàn tất trên Google Colab:

1. `yolov8n_vinhgate_best.pt`: Trọng số PyTorch gốc được tải về từ thư mục `VinhGate_Models/yolov8n_vinhgate_lp/weights/best.pt` trên Google Drive sau khi chạy Cell 3.
2. `yolov8n_vinhgate_best.onnx`: Trọng số định dạng ONNX xuất ra từ Cell 6 trên Colab để tối ưu tốc độ chạy trên CPU của máy tính cá nhân.

> **Lưu ý:** Không đẩy các file `.pt` và `.onnx` có dung lượng quá lớn lên GitHub. Hãy lưu trên Google Drive hoặc Git LFS.

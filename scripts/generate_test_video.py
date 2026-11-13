import cv2
import numpy as np
from pathlib import Path

def generate_test_gate_video(output_path: str = "data/raw_videos/sample_test.mp4", num_frames: int = 90):
    """
    Tạo 1 video demo ngắn (3 giây, 30fps) mô phỏng xe đi qua cổng:
    - 45 frame đầu: Xe ô tô biển số 37A-88999 di chuyển
    - 45 frame sau: Xe máy biển số 37B2-68686 di chuyển
    """
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    w, h = 640, 480
    fps = 30
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (w, h))

    for i in range(num_frames):
        frame = np.ones((h, w, 3), dtype=np.uint8) * 180 # Nền xám đường đi
        # Vẽ vạch đường
        cv2.line(frame, (0, 350), (640, 350), (255, 255, 255), 2)

        if i < 45:
            # Mô phỏng ô tô tiến lại gần
            scale = 1.0 + (i / 45.0) * 0.5
            pw, ph = int(180 * scale), int(50 * scale)
            px = int(230 - (i * 2))
            py = int(240 + (i * 2))
            # Vẽ thân xe
            cv2.rectangle(frame, (px - 40, py - 60), (px + pw + 40, py + ph + 20), (50, 50, 50), -1)
            # Biển số trắng viền đen
            cv2.rectangle(frame, (px, py), (px + pw, py + ph), (250, 250, 250), -1)
            cv2.rectangle(frame, (px, py), (px + pw, py + ph), (0, 0, 0), 2)
            cv2.putText(frame, "37A-88999", (px + 10, py + int(ph * 0.7)), cv2.FONT_HERSHEY_DUPLEX, 0.7 * scale, (0, 0, 0), 2)
        else:
            # Mô phỏng xe máy biển 2 dòng
            j = i - 45
            scale = 1.0 + (j / 45.0) * 0.4
            pw, ph = int(120 * scale), int(80 * scale)
            px = int(260 + (j * 2))
            py = int(220 + (j * 2))
            # Vẽ đuôi xe máy
            cv2.rectangle(frame, (px - 20, py - 80), (px + pw + 20, py + ph + 10), (70, 70, 70), -1)
            # Biển số trắng viền đen 2 dòng
            cv2.rectangle(frame, (px, py), (px + pw, py + ph), (250, 250, 250), -1)
            cv2.rectangle(frame, (px, py), (px + pw, py + ph), (0, 0, 0), 2)
            cv2.putText(frame, "37-B2", (px + 15, py + int(ph * 0.4)), cv2.FONT_HERSHEY_DUPLEX, 0.6 * scale, (0, 0, 0), 2)
            cv2.putText(frame, "686.86", (px + 10, py + int(ph * 0.85)), cv2.FONT_HERSHEY_DUPLEX, 0.6 * scale, (0, 0, 0), 2)

        out.write(frame)

    out.release()
    print(f"✅ Đã tạo video mẫu thành công: {output_path}")

if __name__ == "__main__":
    generate_test_gate_video()

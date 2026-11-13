import os
from pathlib import Path
from dotenv import load_dotenv

# Tự động xác định thư mục gốc VinhGate/ (lùi 2 cấp từ backend/core/)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Nạp file .env từ thư mục gốc nếu có
env_path = BASE_DIR / ".env"
if env_path.exists():
    load_dotenv(env_path)
else:
    # Nạp từ .env.example làm mặc định nếu chưa tạo .env
    example_env = BASE_DIR / ".env.example"
    if example_env.exists():
        load_dotenv(example_env)

# Định nghĩa đường dẫn tuyệt đối trỏ tới các thư mục hệ thống
DATABASE_DIR = BASE_DIR / "database"
SQL_QUERIES_DIR = DATABASE_DIR / "queries"
MODELS_DIR = BASE_DIR / "models"
CAPTURED_IMG_DIR = BASE_DIR / "data" / "captured_logs"
DATA_DIR = BASE_DIR / "data"
FRONTEND_DIR = BASE_DIR / "frontend"

# Đảm bảo các thư mục media và logs luôn tồn tại
CAPTURED_IMG_DIR.mkdir(parents=True, exist_ok=True)
(DATA_DIR / "raw_videos").mkdir(parents=True, exist_ok=True)
(DATA_DIR / "extracted_frames").mkdir(parents=True, exist_ok=True)
MODELS_DIR.mkdir(parents=True, exist_ok=True)

# Cấu hình kết nối MySQL
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "127.0.0.1"),
    "port": int(os.getenv("DB_PORT", 3306)),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "123456"),
    "database": os.getenv("DB_NAME", "vinhgate_db"),
    "charset": "utf8mb4"
}

# Cấu hình máy chủ
SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("SERVER_PORT", 8000))
SECRET_KEY = os.getenv("SECRET_KEY", "vinhgate_secret_2026")

# Cấu hình AI & Ngưỡng nhận diện
MIN_CONFIDENCE_THRESHOLD = float(os.getenv("MIN_CONFIDENCE_THRESHOLD", 0.75))
COOLDOWN_SECONDS = int(os.getenv("COOLDOWN_SECONDS", 30))

# Tự động tìm trọng số best.pt theo thứ tự ưu tiên
def find_yolo_model_path() -> Path:
    candidates = [
        BASE_DIR / "models" / "best.pt",
        BASE_DIR / "models" / "yolov8n_vinhgate_best.pt",
        BASE_DIR / "best.pt",
        BASE_DIR / "models" / "yolov8n_vinhgate_best.onnx"
    ]
    for p in candidates:
        if p.exists():
            return p
    return BASE_DIR / "models" / "best.pt"

YOLO_MODEL_PATH = find_yolo_model_path()
ONNX_MODEL_PATH = BASE_DIR / os.getenv("ONNX_MODEL_PATH", "models/yolov8n_vinhgate_best.onnx")
USE_ONNX = os.getenv("USE_ONNX", "False").lower() in ("true", "1", "t")

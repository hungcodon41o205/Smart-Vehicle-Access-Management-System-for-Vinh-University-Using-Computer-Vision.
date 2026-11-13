import json
import asyncio
from typing import List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse

from backend.core.config import FRONTEND_DIR, CAPTURED_IMG_DIR, SERVER_HOST, SERVER_PORT
from backend.routers import api_gate, api_vehicles, api_stats

app = FastAPI(
    title="VinhGate API Server",
    description="Hệ thống Quản lý xe ra vào Đại học Vinh bằng thị giác máy tính",
    version="2.0.0"
)

# Cấu hình CORS để giao diện Web kết nối thuận tiện
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gắn các routers API
app.include_router(api_gate.router)
app.include_router(api_vehicles.router)
app.include_router(api_stats.router)

# Mount thư mục tĩnh: Ảnh chụp và Giao diện Web
app.mount("/static_images", StaticFiles(directory=str(CAPTURED_IMG_DIR)), name="captured_images")
app.mount("/frontend", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")

# -------------------------------------------------------------
# Quản lý WebSocket kết nối Real-time tới Web Dashboard
# -------------------------------------------------------------
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in list(self.active_connections):
            try:
                await connection.send_text(json.dumps(message))
            except Exception:
                self.disconnect(connection)

ws_manager = ConnectionManager()

@app.websocket("/ws/gate")
async def websocket_gate_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        # Gửi lời chào kết nối thành công
        await websocket.send_text(json.dumps({
            "type": "INIT",
            "message": "Kết nối WebSocket tới VinhGate Gateway thành công."
        }))
        while True:
            # Nhận lệnh điều khiển hoặc heartbeat từ client
            data = await websocket.receive_text()
            try:
                payload = json.loads(data)
                # Có thể mở rộng xử lý tin nhắn từ Dashboard
            except Exception:
                pass
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)

@app.get("/")
def read_root():
    """Điều hướng trang chủ tới giao diện Giám sát trực tiếp."""
    index_file = FRONTEND_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return {"message": "Chào mừng đến với hệ thống VinhGate 2.0. Mời truy cập /frontend hoặc /docs"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host=SERVER_HOST, port=SERVER_PORT, reload=True)

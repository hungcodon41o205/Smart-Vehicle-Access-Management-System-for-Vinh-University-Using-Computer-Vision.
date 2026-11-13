// WebSocket Client for VinhGate Live Updates
class GateWebSocketClient {
    constructor(onMessageCallback) {
        this.socket = null;
        this.onMessageCallback = onMessageCallback;
        this.reconnectInterval = 3000;
        this.init();
    }

    init() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/gate`;

        try {
            this.socket = new WebSocket(wsUrl);

            this.socket.onopen = () => {
                console.log("[WebSocket] Kết nối thành công tới VinhGate Gateway");
                const badge = document.getElementById("connection-status");
                if (badge) {
                    badge.textContent = "TRỰC TUYẾN";
                    badge.className = "status-badge pulse";
                }
            };

            this.socket.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    if (this.onMessageCallback) {
                        this.onMessageCallback(data);
                    }
                } catch (e) {
                    console.error("[WebSocket] Lỗi giải mã gói tin:", e);
                }
            };

            this.socket.onclose = () => {
                console.warn("[WebSocket] Mất kết nối. Thử kết nối lại sau 3s...");
                const badge = document.getElementById("connection-status");
                if (badge) {
                    badge.textContent = "MẤT KẾT NỐI";
                    badge.className = "status-badge";
                    badge.style.background = "#fde8e8";
                    badge.style.color = "#f05252";
                }
                setTimeout(() => this.init(), this.reconnectInterval);
            };

            this.socket.onerror = (err) => {
                console.error("[WebSocket Error]", err);
            };
        } catch (err) {
            console.error("[WebSocket] Không thể tạo kết nối:", err);
            setTimeout(() => this.init(), this.reconnectInterval);
        }
    }

    send(data) {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify(data));
        }
    }
}

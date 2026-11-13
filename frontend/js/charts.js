// Charts utility for VinhGate Dashboard
async function initTrafficChart(canvasId = "trafficChart") {
    const canvas = document.getElementById(canvasId);
    if (!canvas || typeof Chart === "undefined") return;

    try {
        const response = await fetch("/api/stats/hourly-traffic");
        const data = await response.json();

        const ctx = canvas.getContext("2d");
        new Chart(ctx, {
            type: "line",
            data: {
                labels: data.labels,
                datasets: [
                    {
                        label: "Lượt Vào",
                        data: data.vao,
                        borderColor: "#1a56db",
                        backgroundColor: "rgba(26, 86, 219, 0.1)",
                        fill: true,
                        tension: 0.3
                    },
                    {
                        label: "Lượt Ra",
                        data: data.ra,
                        borderColor: "#0e9f6e",
                        backgroundColor: "rgba(14, 159, 110, 0.1)",
                        fill: true,
                        tension: 0.3
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: "top" }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: { stepSize: 1 }
                    }
                }
            }
        });
    } catch (e) {
        console.warn("[Chart] Không thể nạp dữ liệu biểu đồ:", e);
    }
}

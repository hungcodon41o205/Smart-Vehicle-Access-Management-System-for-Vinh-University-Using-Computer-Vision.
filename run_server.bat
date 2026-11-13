@echo off
chcp 65001 >nul
title VinhGate 2.0 - Khởi Chạy Máy Chủ Giám Sát Cổng ĐH Vinh
echo ======================================================================
echo    VINHGATE 2.0 - HỆ THỐNG QUẢN LÝ XE RA VÀO ĐẠI HỌC VINH
echo    (Xác thực 2 yếu tố: Thẻ từ RFID + Camera AI ANPR)
echo ======================================================================
echo.

cd /d "D:\VinhGate_new"

echo [*] Dang kich hoat moi truong ao Python 3.12 (.venv)...
if exist "D:\Do_An_TTCN\.venv\Scripts\activate.bat" (
    call "D:\Do_An_TTCN\.venv\Scripts\activate.bat"
) else if exist "D:\VinhGate_new\.venv\Scripts\activate.bat" (
    call "D:\VinhGate_new\.venv\Scripts\activate.bat"
) else if exist "D:\VinhGate_new\venv\Scripts\activate.bat" (
    call "D:\VinhGate_new\venv\Scripts\activate.bat"
)

echo [*] Dang mo trinh duyet Dashboard Giam sat cong...
start http://localhost:8000/frontend/index.html

echo [*] Dang khoi chay Uvicorn Backend Server...
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

pause

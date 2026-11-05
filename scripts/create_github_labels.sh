#!/usr/bin/env bash
# ==============================================================================
# VinhGate - Script tự động tạo 27 nhãn (GitHub Labels) theo chuẩn Doanh nghiệp
# Yêu cầu: Đã cài đặt GitHub CLI (gh) và đã đăng nhập (gh auth login)
# ==============================================================================

echo "Đang tạo 27 Labels cho dự án VinhGate trên GitHub..."

# Nhóm 1: Loại công việc (Type - 4)
gh label create "type: task"        --color "0E8A16" --description "Công việc phát triển tính năng mới" --force
gh label create "type: bug"         --color "D93F0B" --description "Báo cáo lỗi phát sinh" --force
gh label create "type: enhancement" --color "1D76DB" --description "Cải tiến tính năng hoặc tối ưu hiệu năng" --force
gh label create "type: docs"        --color "0075CA" --description "Tài liệu kỹ thuật, báo cáo thực tập" --force

# Nhóm 2: Độ ưu tiên (Priority - 4)
gh label create "priority: critical" --color "B60205" --description "Lỗi nghiêm trọng, chặn toàn bộ hệ thống" --force
gh label create "priority: high"     --color "D93F0B" --description "Ưu tiên cao, cần hoàn thành sớm" --force
gh label create "priority: medium"   --color "FBCA04" --description "Ưu tiên bình thường" --force
gh label create "priority: low"      --color "0E8A16" --description "Ưu tiên thấp, có thể làm sau" --force

# Nhóm 3: Trạng thái (Status - 5)
gh label create "status: triage"      --color "CCCCCC" --description "Mới tạo, đang chờ xem xét" --force
gh label create "status: todo"        --color "BFD4F2" --description "Đã lên kế hoạch, chuẩn bị làm" --force
gh label create "status: in-progress" --color "FEF2C0" --description "Đang thực hiện" --force
gh label create "status: in-review"   --color "D4C5F9" --description "Đang kiểm thử hoặc review Pull Request" --force
gh label create "status: blocked"     --color "E99695" --description "Bị chặn do phụ thuộc tác vụ khác" --force

# Nhóm 4: Phân hệ (Module - 6)
gh label create "module: ai-yolo"   --color "5319E7" --description "Phân hệ phát hiện YOLOv8" --force
gh label create "module: ai-ocr"    --color "8532A8" --description "Phân hệ đọc ký tự OCR (PaddleOCR)" --force
gh label create "module: database"  --color "C2E0C6" --description "Phân hệ CSDL MySQL 13 bảng" --force
gh label create "module: backend"   --color "0052CC" --description "Phân hệ Backend FastAPI & WebSocket" --force
gh label create "module: frontend"  --color "E9967A" --description "Phân hệ Giao diện Web Dashboard" --force
gh label create "module: colab"     --color "F9D0C4" --description "Kịch bản huấn luyện trên Google Colab" --force

# Nhóm 5: Chu kỳ Sprint (Sprint - 5)
gh label create "sprint: 1" --color "006B75" --description "Sprint 1: Khởi tạo & CSDL Cách B" --force
gh label create "sprint: 2" --color "006B75" --description "Sprint 2: Dữ liệu & Train AI Colab" --force
gh label create "sprint: 3" --color "006B75" --description "Sprint 3: Backend API & Nghiệp vụ" --force
gh label create "sprint: 4" --color "006B75" --description "Sprint 4: Giao diện Web Dashboard" --force
gh label create "sprint: 5" --color "006B75" --description "Sprint 5: Thống kê, Test & Báo cáo" --force

# Nhóm 6: Mức độ khó (Size - 3)
gh label create "size: S" --color "C5DEF5" --description "Quy mô nhỏ: 1 - 2 giờ" --force
gh label create "size: M" --color "BFDADC" --description "Quy mô vừa: Nửa ngày" --force
gh label create "size: L" --color "C2E0C6" --description "Quy mô lớn: 1 - 2 ngày" --force

echo "Đã tạo thành công 27 GitHub Labels cho VinhGate!"

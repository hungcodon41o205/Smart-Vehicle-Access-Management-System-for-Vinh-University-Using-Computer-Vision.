-- =======================================================================
-- File: database/queries/check_vehicle_or_guest.sql
-- Công dụng: Đối chiếu biển số đọc được với:
-- 1. Danh sách đen (danh_sach_den)
-- 2. Phương tiện nội bộ (phuong_tien + nguoi_dung)
-- 3. Phiếu đăng ký khách đang hiệu lực (dang_ky_khach + khach)
-- =======================================================================

-- Query 1: Kiểm tra Danh sách đen
-- Tham số: %(bien_so)s
SELECT 
    id, bien_so, ly_do, muc_do
FROM danh_sach_den
WHERE bien_so = %(bien_so)s
  AND dang_kich_hoat = 1
LIMIT 1;

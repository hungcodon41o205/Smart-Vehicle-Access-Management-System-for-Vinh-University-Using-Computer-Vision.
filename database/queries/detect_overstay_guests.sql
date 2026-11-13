-- =======================================================================
-- File: database/queries/detect_overstay_guests.sql
-- Công dụng: Tìm các phiếu khách đang ở trong trường mà quá hạn den_luc
-- =======================================================================
SELECT 
    dkk.id AS dang_ky_khach_id,
    dkk.bien_so,
    dkk.loai_xe,
    dkk.ma_tam,
    dkk.ly_do_den,
    dkk.nguoi_tiep_don,
    dkk.den_luc,
    k.ho_ten AS ten_khach,
    k.so_dien_thoai
FROM dang_ky_khach dkk
JOIN khach k ON dkk.khach_id = k.id
WHERE dkk.trang_thai = 'DA_VAO'
  AND dkk.den_luc < NOW();

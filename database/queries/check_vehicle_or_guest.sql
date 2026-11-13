-- =======================================================================
-- File: database/queries/check_vehicle_or_guest.sql
-- Công dụng: Đối chiếu xác thực 2 yếu tố (Thẻ từ RFID + Biển số AI)
-- 1. Kiểm tra Danh sách đen (danh_sach_den)
-- 2. Đối chiếu thẻ nội bộ và danh sách tối đa 3 biển số đăng ký (the_tu + phuong_tien)
-- 3. Kiểm tra vi phạm Anti-Passback thẻ nội bộ
-- 4. Đối chiếu thẻ khách lúc VÀO và lúc RA (Chống trộm xe / Tráo biển số)
-- =======================================================================

-- Query 1: Kiểm tra Danh sách đen
-- Tham số: %(bien_so)s
SELECT 
    id, bien_so, ly_do, muc_do
FROM danh_sach_den
WHERE bien_so = %(bien_so)s
  AND con_hieu_luc = 1
LIMIT 1;

-- Query 2: Đối chiếu Thẻ nội bộ và danh sách tối đa 3 xe
-- Tham số: %(ma_the)s
SELECT 
    t.id AS the_id, t.ma_the, t.trang_thai AS trang_thai_the,
    nd.id AS nguoi_dung_id, nd.ho_ten, nd.ma_dinh_danh, nd.don_vi,
    pt.id AS phuong_tien_id, pt.bien_so, pt.loai_xe, pt.nhan_hieu, pt.mau_sac, pt.trang_thai AS trang_thai_xe
FROM the_tu t
JOIN nguoi_dung nd ON t.nguoi_dung_id = nd.id
LEFT JOIN phuong_tien pt ON pt.the_tu_id = t.id AND pt.trang_thai = 'HOAT_DONG'
WHERE t.ma_the = %(ma_the)s
  AND t.loai_the = 'NOI_BO';

-- Query 3: Kiểm tra Anti-Passback (Thẻ nội bộ đã có xe trong trường)
-- Tham số: %(the_tu_id)s
SELECT 
    v_in.id, v_in.bien_so_doc, v_in.thoi_gian
FROM luot_ra_vao v_in
LEFT JOIN luot_ra_vao v_out ON v_out.luot_vao_id = v_in.id AND v_out.huong = 'RA'
WHERE v_in.the_tu_id = %(the_tu_id)s
  AND v_in.huong = 'VAO'
  AND v_in.ket_qua = 'CHO_PHEP'
  AND v_out.id IS NULL
LIMIT 1;

-- Query 4: Đối chiếu Thẻ khách lúc RA với lúc VÀO (Chống trộm xe khách)
-- Tham số: %(the_tu_id)s
SELECT 
    dkk.id AS phieu_id, dkk.bien_so AS bien_so_vao, dkk.tu_luc, dkk.trang_thai,
    hal.duong_dan AS anh_toan_canh_vao
FROM dang_ky_khach dkk
LEFT JOIN luot_ra_vao lrv ON lrv.dang_ky_khach_id = dkk.id AND lrv.huong = 'VAO'
LEFT JOIN hinh_anh_luot hal ON hal.luot_id = lrv.id AND hal.loai = 'TOAN_CANH'
WHERE dkk.the_tu_id = %(the_tu_id)s 
  AND dkk.trang_thai IN ('DANG_HIEU_LUC', 'DA_VAO')
ORDER BY dkk.id DESC 
LIMIT 1;

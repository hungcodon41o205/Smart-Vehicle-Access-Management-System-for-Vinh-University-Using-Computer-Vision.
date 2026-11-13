-- =======================================================================
-- File: database/queries/count_vehicles_inside.sql
-- Công dụng: Đếm chính xác số lượng xe đang ở trong trường Đại học Vinh
-- Cơ chế: Đếm các lượt VÀO hợp lệ mà chưa có lượt RA tương ứng trỏ vào
-- =======================================================================
SELECT 
    COUNT(*) AS tong_xe_trong_truong,
    SUM(CASE WHEN v_in.loai_xe = 'XE_MAY' THEN 1 ELSE 0 END) AS so_xe_may,
    SUM(CASE WHEN v_in.loai_xe = 'O_TO' THEN 1 ELSE 0 END) AS so_o_to
FROM luot_ra_vao v_in
LEFT JOIN luot_ra_vao v_out 
    ON v_out.luot_vao_id = v_in.id AND v_out.huong = 'RA'
WHERE v_in.huong = 'VAO'
  AND v_in.ket_qua = 'CHO_PHEP'
  AND v_out.id IS NULL;

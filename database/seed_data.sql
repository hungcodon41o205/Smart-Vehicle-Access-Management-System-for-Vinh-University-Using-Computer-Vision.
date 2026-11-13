-- ============================================================================
-- DỮ LIỆU MẪU BAN ĐẦU - ĐẠI HỌC VINH (VINHGATE 2.0)
-- File: database/seed_data.sql
-- Nâng cấp: Nạp thẻ từ định danh (Nội bộ & Khách) và phân luồng làn camera
-- ============================================================================

USE `vinh_gate`;

SET FOREIGN_KEY_CHECKS = 0;

-- 1. Dữ liệu bảng vai_tro
INSERT INTO `vai_tro` (`id`, `ten`, `mo_ta`) VALUES
(1, 'ADMIN', 'Toàn quyền cấu hình, quản trị người dùng, hệ thống'),
(2, 'QUAN_LY', 'Xem báo cáo, thống kê, quản lý danh sách xe và sinh viên'),
(3, 'NHAN_VIEN_CONG', 'Trực cổng bảo vệ, theo dõi camera, xác nhận thủ công')
ON DUPLICATE KEY UPDATE id=id;

-- 2. Dữ liệu bảng cong
INSERT INTO `cong` (`id`, `ten`, `vi_tri`, `trang_thai`) VALUES
(1, 'Cổng chính - Lê Duẩn', 'Số 182 Lê Duẩn, Phường Bến Thủy, TP Vinh', 'HOAT_DONG'),
(2, 'Cổng phụ - Ký túc xá', 'Đường Nguyễn Viết Xuân, Phường Hưng Dũng', 'HOAT_DONG')
ON DUPLICATE KEY UPDATE id=id;

-- 3. Dữ liệu bảng camera (Phân luồng làn: Làn nội bộ & Làn xe khách)
INSERT INTO `camera` (`id`, `cong_id`, `ten`, `nguon`, `huong`, `loai_lan`, `trang_thai`) VALUES
(1, 1, 'CAM-01: Làn Vào Xe Nội Bộ (Cổng chính)', '0', 'VAO', 'NOI_BO', 'ONLINE'),
(2, 1, 'CAM-02: Làn Vào Xe Khách (Cổng chính)', 'data/test_samples/test_khach_vao.mp4', 'VAO', 'KHACH', 'ONLINE'),
(3, 1, 'CAM-03: Làn Ra Xe Nội Bộ (Cổng chính)', '1', 'RA', 'NOI_BO', 'ONLINE'),
(4, 1, 'CAM-04: Làn Ra Xe Khách (Cổng chính)', 'data/test_samples/test_khach_ra.mp4', 'RA', 'KHACH', 'ONLINE')
ON DUPLICATE KEY UPDATE id=id;

-- 4. Dữ liệu bảng tai_khoan
INSERT INTO `tai_khoan` (`id`, `ten_dang_nhap`, `mat_khau_hash`, `ho_ten`, `vai_tro_id`, `trang_thai`, `dang_nhap_cuoi`, `tao_luc`) VALUES
(1, 'admin', '$2b$12$uYQeX0J5s5s9F8n1Y8J1b.jUfO3R0Dq6f1O2m2b4p.V3sQYqG8H2e', 'Quản trị viên Hệ thống', 1, 'HOAT_DONG', NULL, '2026-10-20 17:53:14'),
(2, 'quanly', '$2b$12$uYQeX0J5s5s9F8n1Y8J1b.jUfO3R0Dq6f1O2m2b4p.V3sQYqG8H2e', 'Thầy Nguyễn Văn Quản Lý', 2, 'HOAT_DONG', NULL, '2026-10-20 17:53:14'),
(3, 'baove', '$2b$12$uYQeX0J5s5s9F8n1Y8J1b.jUfO3R0Dq6f1O2m2b4p.V3sQYqG8H2e', 'Bác Hoàng Bảo Vệ Cổng', 3, 'HOAT_DONG', NULL, '2026-10-20 17:53:14')
ON DUPLICATE KEY UPDATE id=id;

-- 5. Dữ liệu bảng nguoi_dung
INSERT INTO `nguoi_dung` (`id`, `ma_dinh_danh`, `ho_ten`, `loai`, `don_vi`, `email`, `so_dien_thoai`, `trang_thai`, `tao_luc`) VALUES
(1, 'SV20260101', 'Nguyễn Thị Thu Hà', 'SINH_VIEN', 'Khoa Công nghệ Thông tin', 'ha.ntt@vinhuni.edu.vn', '0912345678', 'HOAT_DONG', '2026-10-20 17:53:14'),
(2, 'SV20260102', 'Lê Văn Hùng', 'SINH_VIEN', 'Khoa Kinh tế', 'hung.lv@vinhuni.edu.vn', '0987654321', 'HOAT_DONG', '2026-10-20 17:53:14'),
(3, 'SV20260103', 'Phạm Quốc Bảo', 'SINH_VIEN', 'Khoa Luật', 'bao.pq@vinhuni.edu.vn', '0978112233', 'HOAT_DONG', '2026-10-20 17:53:14'),
(4, 'GV00112', 'TS. Trần Đình Dũng', 'GIANG_VIEN', 'Viện Kỹ thuật & Công nghệ', 'dung.td@vinhuni.edu.vn', '0903445566', 'HOAT_DONG', '2026-10-20 17:53:14'),
(5, 'CB00055', 'Nguyễn Thị Mai', 'CAN_BO', 'Phòng Công tác Chính trị', 'mai.nt@vinhuni.edu.vn', '0915667788', 'HOAT_DONG', '2026-10-20 17:53:14')
ON DUPLICATE KEY UPDATE id=id;

-- 6. Dữ liệu bảng the_tu (Thẻ nội bộ & Kho thẻ khách)
INSERT INTO `the_tu` (`id`, `ma_the`, `loai_the`, `nguoi_dung_id`, `trang_thai`, `ngay_cap`, `ghi_chu`) VALUES
(1, '1001', 'NOI_BO', 1, 'SAN_SANG', '2026-09-01 08:00:00', 'Thẻ RFID sinh viên Hà (Đăng ký 2 xe)'),
(2, '1002', 'NOI_BO', 2, 'SAN_SANG', '2026-09-05 08:00:00', 'Thẻ RFID sinh viên Hùng'),
(3, '1003', 'NOI_BO', 3, 'SAN_SANG', '2026-09-10 08:00:00', 'Thẻ RFID sinh viên Bảo'),
(4, '2001', 'NOI_BO', 4, 'SAN_SANG', '2026-01-01 08:00:00', 'Thẻ Giảng viên Dũng (Ô tô)'),
(5, '2002', 'NOI_BO', 5, 'SAN_SANG', '2026-02-15 08:00:00', 'Thẻ Cán bộ Mai (Ô tô)'),
(6, 'KH-01', 'KHACH', NULL, 'DANG_SU_DUNG', '2026-10-01 07:00:00', 'Thẻ khách xoay vòng 01 (Đang phát cho khách 37A-99911)'),
(7, 'KH-02', 'KHACH', NULL, 'SAN_SANG', '2026-10-01 07:00:00', 'Thẻ khách xoay vòng 02'),
(8, 'KH-03', 'KHACH', NULL, 'SAN_SANG', '2026-10-01 07:00:00', 'Thẻ khách xoay vòng 03'),
(9, 'KH-04', 'KHACH', NULL, 'SAN_SANG', '2026-10-01 07:00:00', 'Thẻ khách xoay vòng 04'),
(10, 'KH-05', 'KHACH', NULL, 'SAN_SANG', '2026-10-01 07:00:00', 'Thẻ khách xoay vòng 05')
ON DUPLICATE KEY UPDATE id=id;

-- 7. Dữ liệu bảng phuong_tien (1 thẻ 1001 của SV Hà liên kết 2 xe: 38B1-12345 và 37AB-12206)
INSERT INTO `phuong_tien` (`id`, `nguoi_dung_id`, `the_tu_id`, `bien_so`, `loai_xe`, `nhan_hieu`, `mau_sac`, `trang_thai`, `ngay_dang_ky`, `ngay_het_han`) VALUES
(1, 1, 1, '38B1-12345', 'XE_MAY', 'Honda Vision', 'Trắng', 'HOAT_DONG', '2026-09-01', '2027-09-01'),
(2, 2, 2, '37B2-67890', 'XE_MAY', 'Yamaha Exciter', 'Xanh GP', 'HOAT_DONG', '2026-09-05', '2027-09-05'),
(3, 3, 3, '38F1-55555', 'XE_MAY', 'Honda Air Blade', 'Đen nhám', 'HOAT_DONG', '2026-09-10', '2027-09-10'),
(4, 4, 4, '37A-99999', 'O_TO', 'Mazda CX-5', 'Đỏ Soul', 'HOAT_DONG', '2026-01-01', '2028-01-01'),
(5, 5, 5, '37A-12345', 'O_TO', 'Toyota Vios', 'Bạc', 'HOAT_DONG', '2026-02-15', '2028-02-15'),
(6, 1, 1, '37AB-12206', 'XE_MAY', 'VinFast Klara', 'Xanh Cyan', 'HOAT_DONG', '2026-09-15', '2027-09-15')
ON DUPLICATE KEY UPDATE id=id;

-- 8. Dữ liệu bảng danh_sach_den
INSERT INTO `danh_sach_den` (`id`, `bien_so`, `ly_do`, `con_hieu_luc`, `them_boi`, `them_luc`) VALUES
(1, '29A-88888', 'Đối tượng gây rối trật tự an ninh tại cổng trường', 1, 1, '2026-10-20 17:53:14'),
(2, '37B1-00000', 'Phương tiện nghi vấn trộm cắp, cần giữ xe làm việc', 1, 1, '2026-10-20 17:53:14')
ON DUPLICATE KEY UPDATE id=id;

-- 9. Dữ liệu bảng khach & dang_ky_khach (Gán thẻ KH-01 cho khách)
INSERT INTO `khach` (`id`, `ho_ten`, `so_dien_thoai`, `ly_do_den`, `nguoi_tiep_don`, `tao_luc`, `don_vi_cong_tac`, `so_cccd`) VALUES
(1, 'Trần Văn Khách', '0988776655', 'Công tác tuyển sinh', 'Phòng Đào tạo', '2026-10-23 08:00:00', 'Sở GD&ĐT Nghệ An', '040099123456')
ON DUPLICATE KEY UPDATE id=id;

INSERT INTO `dang_ky_khach` (`id`, `khach_id`, `the_tu_id`, `bien_so`, `loai_xe`, `ma_tam`, `ly_do_den`, `nguoi_tiep_don`, `tu_luc`, `den_luc`, `phi_gui_xe`, `trang_thai`, `nguoi_tao_id`, `ngay_tao`) VALUES
(1, 1, 6, '37A-99911', 'O_TO', 'VG-202610230814-002', 'Họp', 'Văn phòng trường', '2026-10-23 08:14:39', '2026-10-23 18:14:39', '0.00', 'DA_VAO', 1, '2026-10-23 08:14:39')
ON DUPLICATE KEY UPDATE id=id;

SET FOREIGN_KEY_CHECKS = 1;

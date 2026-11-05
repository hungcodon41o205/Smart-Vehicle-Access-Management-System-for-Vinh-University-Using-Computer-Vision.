-- ============================================================================
-- DỮ LIỆU MẪU BAN ĐẦU - ĐẠI HỌC VINH
-- File: database/seed_data.sql
-- ============================================================================

USE `vinh_gate`;

SET FOREIGN_KEY_CHECKS = 0;

-- Dữ liệu bảng vai_tro
INSERT INTO `vai_tro` (`id`, `ten`, `mo_ta`) VALUES
(1, 'ADMIN', 'Toàn quyền cấu hình, quản trị người dùng, hệ thống'),
(2, 'QUAN_LY', 'Xem báo cáo, thống kê, quản lý danh sách xe và sinh viên'),
(3, 'NHAN_VIEN_CONG', 'Trực cổng bảo vệ, theo dõi camera, xác nhận thủ công')
ON DUPLICATE KEY UPDATE id=id;

-- Dữ liệu bảng cong
INSERT INTO `cong` (`id`, `ten`, `vi_tri`, `trang_thai`) VALUES
(1, 'Cổng chính - Lê Duẩn', 'Số 182 Lê Duẩn, Phường Bến Thủy, TP Vinh', 'HOAT_DONG'),
(2, 'Cổng phụ - Ký túc xá', 'Đường Nguyễn Viết Xuân, Phường Hưng Dũng', 'HOAT_DONG')
ON DUPLICATE KEY UPDATE id=id;

-- Dữ liệu bảng camera
INSERT INTO `camera` (`id`, `cong_id`, `ten`, `nguon`, `huong`, `trang_thai`) VALUES
(1, 1, 'CAM-01: Cổng chính Làn Vào', '0', 'VAO', 'ONLINE'),
(2, 1, 'CAM-02: Cổng chính Làn Ra', '1', 'RA', 'ONLINE'),
(3, 2, 'CAM-03: Cổng phụ Làn Vào', 'data/test_samples/test_vao.mp4', 'VAO', 'OFFLINE'),
(4, 2, 'CAM-04: Cổng phụ Làn Ra', 'data/test_samples/test_ra.mp4', 'RA', 'OFFLINE')
ON DUPLICATE KEY UPDATE id=id;

-- Dữ liệu bảng tai_khoan
INSERT INTO `tai_khoan` (`id`, `ten_dang_nhap`, `mat_khau_hash`, `ho_ten`, `vai_tro_id`, `trang_thai`, `dang_nhap_cuoi`, `tao_luc`) VALUES
(1, 'admin', '$2b$12$uYQeX0J5s5s9F8n1Y8J1b.jUfO3R0Dq6f1O2m2b4p.V3sQYqG8H2e', 'Quản trị viên Hệ thống', 1, 'HOAT_DONG', NULL, '2026-10-20 17:53:14'),
(2, 'quanly', '$2b$12$uYQeX0J5s5s9F8n1Y8J1b.jUfO3R0Dq6f1O2m2b4p.V3sQYqG8H2e', 'Thầy Nguyễn Văn Quản Lý', 2, 'HOAT_DONG', NULL, '2026-10-20 17:53:14'),
(3, 'baove', '$2b$12$uYQeX0J5s5s9F8n1Y8J1b.jUfO3R0Dq6f1O2m2b4p.V3sQYqG8H2e', 'Bác Hoàng Bảo Vệ Cổng', 3, 'HOAT_DONG', NULL, '2026-10-20 17:53:14')
ON DUPLICATE KEY UPDATE id=id;

-- Dữ liệu bảng nguoi_dung
INSERT INTO `nguoi_dung` (`id`, `ma_dinh_danh`, `ho_ten`, `loai`, `don_vi`, `email`, `so_dien_thoai`, `trang_thai`, `tao_luc`) VALUES
(1, 'SV20260101', 'Nguyễn Thị Thu Hà', 'SINH_VIEN', 'Khoa Công nghệ Thông tin', 'ha.ntt@vinhuni.edu.vn', '0912345678', 'HOAT_DONG', '2026-10-20 17:53:14'),
(2, 'SV20260102', 'Lê Văn Hùng', 'SINH_VIEN', 'Khoa Kinh tế', 'hung.lv@vinhuni.edu.vn', '0987654321', 'HOAT_DONG', '2026-10-20 17:53:14'),
(3, 'SV20260103', 'Phạm Quốc Bảo', 'SINH_VIEN', 'Khoa Luật', 'bao.pq@vinhuni.edu.vn', '0978112233', 'HOAT_DONG', '2026-10-20 17:53:14'),
(4, 'GV00112', 'TS. Trần Đình Dũng', 'GIANG_VIEN', 'Viện Kỹ thuật & Công nghệ', 'dung.td@vinhuni.edu.vn', '0903445566', 'HOAT_DONG', '2026-10-20 17:53:14'),
(5, 'CB00055', 'Nguyễn Thị Mai', 'CAN_BO', 'Phòng Công tác Chính trị', 'mai.nt@vinhuni.edu.vn', '0915667788', 'HOAT_DONG', '2026-10-20 17:53:14')
ON DUPLICATE KEY UPDATE id=id;

-- Dữ liệu bảng phuong_tien
INSERT INTO `phuong_tien` (`id`, `nguoi_dung_id`, `bien_so`, `loai_xe`, `nhan_hieu`, `mau_sac`, `trang_thai`, `ngay_dang_ky`, `ngay_het_han`) VALUES
(1, 1, '38B1-12345', 'XE_MAY', 'Honda Vision', 'Trắng', 'HOAT_DONG', '2026-09-01', '2027-09-01'),
(2, 2, '37B2-67890', 'XE_MAY', 'Yamaha Exciter', 'Xanh GP', 'HOAT_DONG', '2026-09-05', '2027-09-05'),
(3, 3, '38F1-55555', 'XE_MAY', 'Honda Air Blade', 'Đen nhám', 'HOAT_DONG', '2026-09-10', '2027-09-10'),
(4, 4, '37A-99999', 'O_TO', 'Mazda CX-5', 'Đỏ Soul', 'HOAT_DONG', '2026-01-01', '2028-01-01'),
(5, 5, '37A-12345', 'O_TO', 'Toyota Vios', 'Bạc', 'HOAT_DONG', '2026-02-15', '2028-02-15')
ON DUPLICATE KEY UPDATE id=id;

-- Dữ liệu bảng danh_sach_den
INSERT INTO `danh_sach_den` (`id`, `bien_so`, `ly_do`, `con_hieu_luc`, `them_boi`, `them_luc`) VALUES
(1, '29A-88888', 'Đối tượng gây rối trật tự an ninh tại cổng trường', 1, 1, '2026-10-20 17:53:14'),
(2, '37B1-00000', 'Phương tiện nghi vấn trộm cắp, cần giữ xe làm việc', 1, 1, '2026-10-20 17:53:14')
ON DUPLICATE KEY UPDATE id=id;

-- Dữ liệu bảng dang_ky_khach
INSERT INTO `dang_ky_khach` (`id`, `khach_id`, `bien_so`, `loai_xe`, `ma_tam`, `ly_do_den`, `nguoi_tiep_don`, `tu_luc`, `den_luc`, `phi_gui_xe`, `trang_thai`, `nguoi_tao_id`, `ngay_tao`) VALUES
(1, 1, '37A-99911', 'O_TO', 'VG-202610230814-002', 'Họp', 'Văn phòng trường', '2026-10-23 08:14:39', '2026-10-23 12:14:39', '0.00', 'DANG_HIEU_LUC', NULL, '2026-10-23 08:14:39')
ON DUPLICATE KEY UPDATE id=id;

SET FOREIGN_KEY_CHECKS = 1;

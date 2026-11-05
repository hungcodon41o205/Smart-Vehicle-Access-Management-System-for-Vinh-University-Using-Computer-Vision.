-- ============================================================================
-- HỆ THỐNG QUẢN LÝ XE RA VÀO ĐẠI HỌC VINH (VINHGATE 2.0)
-- File: database/schema.sql
-- Trích xuất chuẩn xác 100% từ cơ sở dữ liệu thực tế: vinh_gate
-- ============================================================================

CREATE DATABASE IF NOT EXISTS `vinh_gate` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `vinh_gate`;

SET FOREIGN_KEY_CHECKS = 0;

-- ------------------------------------------------------------
-- Bảng: camera
-- ------------------------------------------------------------
CREATE TABLE `camera` (
  `id` smallint unsigned NOT NULL AUTO_INCREMENT,
  `cong_id` smallint unsigned NOT NULL,
  `ten` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `nguon` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'RTSP URL, chỉ số Webcam hoặc file video test',
  `huong` enum('VAO','RA','CA_HAI') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'CA_HAI',
  `trang_thai` enum('ONLINE','OFFLINE') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'OFFLINE',
  PRIMARY KEY (`id`),
  KEY `fk_cam_cong` (`cong_id`),
  CONSTRAINT `fk_cam_cong` FOREIGN KEY (`cong_id`) REFERENCES `cong` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------
-- Bảng: canh_bao
-- ------------------------------------------------------------
CREATE TABLE `canh_bao` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `loai` enum('DANH_SACH_DEN','DO_TIN_CAY_THAP','XE_LA','CAMERA_MAT_KET_NOI','LUOT_RA_KHONG_CO_VAO','XE_O_LAI_QUA_LAU') COLLATE utf8mb4_unicode_ci NOT NULL,
  `muc_do` enum('THAP','TRUNG_BINH','CAO') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'TRUNG_BINH',
  `luot_id` bigint unsigned DEFAULT NULL,
  `camera_id` smallint unsigned DEFAULT NULL,
  `noi_dung` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `trang_thai` enum('MOI','DA_XEM','DA_XU_LY') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'MOI',
  `tao_luc` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `xu_ly_boi` int unsigned DEFAULT NULL,
  `xu_ly_luc` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_cb_trangthai` (`trang_thai`),
  KEY `idx_cb_loai` (`loai`),
  KEY `fk_cb_luot` (`luot_id`),
  KEY `fk_cb_cam` (`camera_id`),
  KEY `fk_cb_tk` (`xu_ly_boi`),
  CONSTRAINT `fk_cb_cam` FOREIGN KEY (`camera_id`) REFERENCES `camera` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_cb_luot` FOREIGN KEY (`luot_id`) REFERENCES `luot_ra_vao` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_cb_tk` FOREIGN KEY (`xu_ly_boi`) REFERENCES `tai_khoan` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------
-- Bảng: cong
-- ------------------------------------------------------------
CREATE TABLE `cong` (
  `id` smallint unsigned NOT NULL AUTO_INCREMENT,
  `ten` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'VD: Cổng chính, Cổng phụ',
  `vi_tri` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `trang_thai` enum('HOAT_DONG','BAO_TRI') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'HOAT_DONG',
  PRIMARY KEY (`id`),
  UNIQUE KEY `ten` (`ten`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------
-- Bảng: dang_ky_khach
-- ------------------------------------------------------------
CREATE TABLE `dang_ky_khach` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `khach_id` int unsigned NOT NULL,
  `bien_so` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Biển số xe của khách',
  `loai_xe` enum('XE_MAY','O_TO') COLLATE utf8mb4_unicode_ci NOT NULL,
  `ma_tam` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Mã phiếu tạm thời cấp cho khách',
  `ly_do_den` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `nguoi_tiep_don` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `tu_luc` datetime NOT NULL,
  `den_luc` datetime NOT NULL,
  `phi_gui_xe` decimal(10,2) DEFAULT '0.00',
  `trang_thai` enum('DANG_HIEU_LUC','DA_VAO','DA_RA','QUA_HAN','HUY') COLLATE utf8mb4_unicode_ci DEFAULT 'DANG_HIEU_LUC',
  `nguoi_tao_id` int unsigned DEFAULT NULL,
  `ngay_tao` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ma_tam` (`ma_tam`),
  KEY `idx_dkk_bienso_trangthai` (`bien_so`,`trang_thai`),
  KEY `fk_dkk_khach` (`khach_id`),
  KEY `fk_dkk_nguoitao` (`nguoi_tao_id`),
  CONSTRAINT `fk_dkk_khach` FOREIGN KEY (`khach_id`) REFERENCES `khach` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_dkk_nguoitao` FOREIGN KEY (`nguoi_tao_id`) REFERENCES `tai_khoan` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------
-- Bảng: danh_sach_den
-- ------------------------------------------------------------
CREATE TABLE `danh_sach_den` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `bien_so` varchar(15) COLLATE utf8mb4_unicode_ci NOT NULL,
  `ly_do` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `con_hieu_luc` tinyint(1) NOT NULL DEFAULT '1',
  `them_boi` int unsigned NOT NULL,
  `them_luc` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_dsden_bienso` (`bien_so`),
  KEY `fk_dsden_tk` (`them_boi`),
  CONSTRAINT `fk_dsden_tk` FOREIGN KEY (`them_boi`) REFERENCES `tai_khoan` (`id`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------
-- Bảng: hinh_anh_luot
-- ------------------------------------------------------------
CREATE TABLE `hinh_anh_luot` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `luot_id` bigint unsigned NOT NULL,
  `loai` enum('TOAN_CANH','BIEN_SO') COLLATE utf8mb4_unicode_ci NOT NULL,
  `duong_dan` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Đường dẫn file ảnh lưu trên ổ đĩa',
  `tao_luc` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `fk_anh_luot` (`luot_id`),
  CONSTRAINT `fk_anh_luot` FOREIGN KEY (`luot_id`) REFERENCES `luot_ra_vao` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------
-- Bảng: khach
-- ------------------------------------------------------------
CREATE TABLE `khach` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `ho_ten` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `so_dien_thoai` varchar(15) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `ly_do_den` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Công tác, liên hệ phòng ban nào',
  `nguoi_tiep_don` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `tao_luc` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `don_vi_cong_tac` varchar(150) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `so_cccd` varchar(25) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------
-- Bảng: luot_ra_vao
-- ------------------------------------------------------------
CREATE TABLE `luot_ra_vao` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `camera_id` smallint unsigned NOT NULL,
  `huong` enum('VAO','RA') COLLATE utf8mb4_unicode_ci NOT NULL,
  `thoi_gian` datetime(3) NOT NULL,
  `bien_so_doc` varchar(15) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Biển số đọc tự động từ OCR',
  `bien_so_xac_nhan` varchar(15) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Biển số sau khi nhân viên kiểm tra/sửa',
  `do_tin_cay` decimal(4,3) DEFAULT NULL COMMENT 'Độ tin cậy OCR từ 0.000 đến 1.000',
  `loai_xe` enum('XE_MAY','O_TO') COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `phuong_tien_id` int unsigned DEFAULT NULL COMMENT 'Khóa ngoại nếu là xe đã đăng ký',
  `khach_id` int unsigned DEFAULT NULL COMMENT 'Khóa ngoại nếu là xe khách',
  `luot_vao_id` bigint unsigned DEFAULT NULL COMMENT 'Lượt RA trỏ về lượt VAO tương ứng (ghép cặp)',
  `ket_qua` enum('CHO_PHEP','TU_CHOI','CHO_XAC_NHAN') COLLATE utf8mb4_unicode_ci NOT NULL,
  `xac_nhan_boi` int unsigned DEFAULT NULL COMMENT 'Tài khoản nhân viên xác nhận thủ công',
  `ghi_chu` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_luot_thoigian` (`thoi_gian`),
  KEY `idx_luot_bienso` (`bien_so_xac_nhan`,`bien_so_doc`),
  KEY `idx_luot_pt` (`phuong_tien_id`),
  KEY `idx_luot_huong_kq` (`huong`,`ket_qua`),
  KEY `fk_luot_cam` (`camera_id`),
  KEY `fk_luot_khach` (`khach_id`),
  KEY `fk_luot_vao` (`luot_vao_id`),
  KEY `fk_luot_tk` (`xac_nhan_boi`),
  CONSTRAINT `fk_luot_cam` FOREIGN KEY (`camera_id`) REFERENCES `camera` (`id`) ON UPDATE CASCADE,
  CONSTRAINT `fk_luot_khach` FOREIGN KEY (`khach_id`) REFERENCES `khach` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_luot_pt` FOREIGN KEY (`phuong_tien_id`) REFERENCES `phuong_tien` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_luot_tk` FOREIGN KEY (`xac_nhan_boi`) REFERENCES `tai_khoan` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_luot_vao` FOREIGN KEY (`luot_vao_id`) REFERENCES `luot_ra_vao` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=49 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------
-- Bảng: nguoi_dung
-- ------------------------------------------------------------
CREATE TABLE `nguoi_dung` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `ma_dinh_danh` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Mã sinh viên hoặc Mã cán bộ',
  `ho_ten` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `loai` enum('SINH_VIEN','GIANG_VIEN','CAN_BO') COLLATE utf8mb4_unicode_ci NOT NULL,
  `don_vi` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Khoa, Viện, Phòng, Ban',
  `email` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `so_dien_thoai` varchar(15) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `trang_thai` enum('HOAT_DONG','NGUNG') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'HOAT_DONG',
  `tao_luc` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ma_dinh_danh` (`ma_dinh_danh`),
  KEY `idx_nd_madinhdanh` (`ma_dinh_danh`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------
-- Bảng: nhat_ky_he_thong
-- ------------------------------------------------------------
CREATE TABLE `nhat_ky_he_thong` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `tai_khoan_id` int unsigned DEFAULT NULL,
  `hanh_dong` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'DANG_NHAP, THEM_XE, SUA_BIEN_SO, XAC_NHAN_XE...',
  `doi_tuong` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `chi_tiet` json DEFAULT NULL,
  `tao_luc` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `fk_nk_tk` (`tai_khoan_id`),
  CONSTRAINT `fk_nk_tk` FOREIGN KEY (`tai_khoan_id`) REFERENCES `tai_khoan` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------
-- Bảng: phuong_tien
-- ------------------------------------------------------------
CREATE TABLE `phuong_tien` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `nguoi_dung_id` int unsigned NOT NULL,
  `bien_so` varchar(15) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Chuẩn hóa: không khoảng trắng, không dấu chấm',
  `loai_xe` enum('XE_MAY','O_TO') COLLATE utf8mb4_unicode_ci NOT NULL,
  `nhan_hieu` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Honda, Yamaha, Mazda, Toyota...',
  `mau_sac` varchar(30) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `trang_thai` enum('HOAT_DONG','TAM_KHOA') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'HOAT_DONG',
  `ngay_dang_ky` date NOT NULL,
  `ngay_het_han` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `bien_so` (`bien_so`),
  KEY `idx_pt_bienso` (`bien_so`),
  KEY `fk_pt_nguoidung` (`nguoi_dung_id`),
  CONSTRAINT `fk_pt_nguoidung` FOREIGN KEY (`nguoi_dung_id`) REFERENCES `nguoi_dung` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------
-- Bảng: tai_khoan
-- ------------------------------------------------------------
CREATE TABLE `tai_khoan` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `ten_dang_nhap` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `mat_khau_hash` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Chuỗi băm Bcrypt, không lưu mật khẩu thô',
  `ho_ten` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `vai_tro_id` tinyint unsigned NOT NULL,
  `trang_thai` enum('HOAT_DONG','KHOA') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'HOAT_DONG',
  `dang_nhap_cuoi` datetime DEFAULT NULL,
  `tao_luc` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ten_dang_nhap` (`ten_dang_nhap`),
  KEY `fk_tk_vaitro` (`vai_tro_id`),
  CONSTRAINT `fk_tk_vaitro` FOREIGN KEY (`vai_tro_id`) REFERENCES `vai_tro` (`id`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------
-- Bảng: vai_tro
-- ------------------------------------------------------------
CREATE TABLE `vai_tro` (
  `id` tinyint unsigned NOT NULL AUTO_INCREMENT,
  `ten` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'ADMIN, QUAN_LY, NHAN_VIEN_CONG',
  `mo_ta` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ten` (`ten`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------
-- View: v_thong_ke_hom_nay
-- ------------------------------------------------------------
DROP VIEW IF EXISTS `v_thong_ke_hom_nay`;
CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `v_thong_ke_hom_nay` AS select curdate() AS `ngay`,sum((case when ((`luot_ra_vao`.`huong` = 'VAO') and (`luot_ra_vao`.`ket_qua` = 'CHO_PHEP')) then 1 else 0 end)) AS `tong_vao_hop_le`,sum((case when ((`luot_ra_vao`.`huong` = 'RA') and (`luot_ra_vao`.`ket_qua` = 'CHO_PHEP')) then 1 else 0 end)) AS `tong_ra_hop_le`,sum((case when (`luot_ra_vao`.`ket_qua` = 'TU_CHOI') then 1 else 0 end)) AS `tong_tu_choi`,sum((case when (`luot_ra_vao`.`ket_qua` = 'CHO_XAC_NHAN') then 1 else 0 end)) AS `tong_cho_xac_nhan`,(select count(0) from `canh_bao` where (cast(`canh_bao`.`tao_luc` as date) = curdate())) AS `tong_canh_bao` from `luot_ra_vao` where (cast(`luot_ra_vao`.`thoi_gian` as date) = curdate());

-- ------------------------------------------------------------
-- View: v_xe_dang_trong_truong
-- ------------------------------------------------------------
DROP VIEW IF EXISTS `v_xe_dang_trong_truong`;
CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `v_xe_dang_trong_truong` AS select `v`.`id` AS `luot_vao_id`,`v`.`thoi_gian` AS `thoi_gian_vao`,`v`.`bien_so_doc` AS `bien_so_doc`,`v`.`bien_so_xac_nhan` AS `bien_so_xac_nhan`,coalesce(`v`.`bien_so_xac_nhan`,`v`.`bien_so_doc`) AS `bien_so_hien_thi`,`v`.`loai_xe` AS `loai_xe`,`c`.`ten` AS `cong_vao`,`pt`.`nhan_hieu` AS `nhan_hieu`,`pt`.`mau_sac` AS `mau_sac`,`nd`.`ma_dinh_danh` AS `ma_dinh_danh`,`nd`.`ho_ten` AS `chu_xe`,`nd`.`don_vi` AS `don_vi`,`nd`.`loai` AS `loai_nguoi_dung`,timestampdiff(MINUTE,`v`.`thoi_gian`,now()) AS `so_phut_da_o` from (((((`luot_ra_vao` `v` left join `luot_ra_vao` `r` on((`r`.`luot_vao_id` = `v`.`id`))) left join `camera` `cam` on((`cam`.`id` = `v`.`camera_id`))) left join `cong` `c` on((`c`.`id` = `cam`.`cong_id`))) left join `phuong_tien` `pt` on((`pt`.`id` = `v`.`phuong_tien_id`))) left join `nguoi_dung` `nd` on((`nd`.`id` = `pt`.`nguoi_dung_id`))) where ((`v`.`huong` = 'VAO') and (`v`.`ket_qua` = 'CHO_PHEP') and (`r`.`id` is null));

SET FOREIGN_KEY_CHECKS = 1;

-- ============================================================================
-- VINHGATE 2.0 - BẢN NÂNG CẤP HỆ THỐNG THẺ TỪ ĐỊNH DANH (XÁC THỰC 2 YẾU TỐ)
-- File: database/migrations/v3_add_card_system.sql
-- Mục tiêu:
--   1. Tạo bảng `the_tu` quản lý kho thẻ RFID (Nội bộ & Khách).
--   2. Bổ sung `the_tu_id` vào `phuong_tien` (1 thẻ đăng ký tối đa 3 biển số).
--   3. Bổ sung `loai_lan` vào `camera` (Phân luồng Làn Nội bộ & Làn Khách).
--   4. Bổ sung `ma_the_quyet` và `the_tu_id` vào `luot_ra_vao` và `dang_ky_khach`.
-- ============================================================================

USE `vinh_gate`;

SET FOREIGN_KEY_CHECKS = 0;

-- 1. Tạo bảng the_tu
CREATE TABLE IF NOT EXISTS `the_tu` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `ma_the` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Mã UID thẻ RFID/Barcode, VD: 1001, CARD-NB-001, CARD-KH-01',
  `loai_the` enum('NOI_BO','KHACH') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'NOI_BO',
  `nguoi_dung_id` int unsigned DEFAULT NULL COMMENT 'Chủ thẻ nếu là thẻ nội bộ',
  `trang_thai` enum('SAN_SANG','DANG_SU_DUNG','KHOA','DA_MAT') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'SAN_SANG',
  `ngay_cap` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `ghi_chu` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ma_the` (`ma_the`),
  KEY `idx_the_nguoidung` (`nguoi_dung_id`),
  KEY `idx_the_loai_trangthai` (`loai_the`, `trang_thai`),
  CONSTRAINT `fk_the_nguoidung` FOREIGN KEY (`nguoi_dung_id`) REFERENCES `nguoi_dung` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. Thêm cột the_tu_id vào bảng phuong_tien
SET @col_exists = (SELECT COUNT(*) FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = 'vinh_gate' AND TABLE_NAME = 'phuong_tien' AND COLUMN_NAME = 'the_tu_id');
SET @sql_stmt = IF(@col_exists = 0, 'ALTER TABLE `phuong_tien` ADD COLUMN `the_tu_id` int unsigned DEFAULT NULL COMMENT "Khóa ngoại trỏ sang thẻ từ (Tối đa 3 xe/thẻ)", ADD CONSTRAINT `fk_pt_thetu` FOREIGN KEY (`the_tu_id`) REFERENCES `the_tu` (`id`) ON DELETE SET NULL ON UPDATE CASCADE', 'SELECT "Column the_tu_id already exists in phuong_tien"');
PREPARE stmt FROM @sql_stmt;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 3. Thêm cột loai_lan vào bảng camera
SET @col_exists = (SELECT COUNT(*) FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = 'vinh_gate' AND TABLE_NAME = 'camera' AND COLUMN_NAME = 'loai_lan');
SET @sql_stmt = IF(@col_exists = 0, 'ALTER TABLE `camera` ADD COLUMN `loai_lan` enum("NOI_BO","KHACH","HON_HOP") COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT "HON_HOP" COMMENT "Phân luồng làn xe tại cổng"', 'SELECT "Column loai_lan already exists in camera"');
PREPARE stmt FROM @sql_stmt;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 4. Thêm cột ma_the_quyet và the_tu_id vào bảng luot_ra_vao
SET @col_exists = (SELECT COUNT(*) FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = 'vinh_gate' AND TABLE_NAME = 'luot_ra_vao' AND COLUMN_NAME = 'ma_the_quyet');
SET @sql_stmt = IF(@col_exists = 0, 'ALTER TABLE `luot_ra_vao` ADD COLUMN `ma_the_quyet` varchar(30) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT "Mã thẻ quẹt tại thời điểm qua cổng", ADD COLUMN `the_tu_id` int unsigned DEFAULT NULL COMMENT "ID thẻ từ", ADD CONSTRAINT `fk_luot_thetu` FOREIGN KEY (`the_tu_id`) REFERENCES `the_tu` (`id`) ON DELETE SET NULL ON UPDATE CASCADE', 'SELECT "Columns ma_the_quyet already exist in luot_ra_vao"');
PREPARE stmt FROM @sql_stmt;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 5. Thêm cột the_tu_id vào bảng dang_ky_khach
SET @col_exists = (SELECT COUNT(*) FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = 'vinh_gate' AND TABLE_NAME = 'dang_ky_khach' AND COLUMN_NAME = 'the_tu_id');
SET @sql_stmt = IF(@col_exists = 0, 'ALTER TABLE `dang_ky_khach` ADD COLUMN `the_tu_id` int unsigned DEFAULT NULL COMMENT "Thẻ từ khách mượn", ADD CONSTRAINT `fk_dkk_thetu` FOREIGN KEY (`the_tu_id`) REFERENCES `the_tu` (`id`) ON DELETE SET NULL ON UPDATE CASCADE', 'SELECT "Column the_tu_id already exists in dang_ky_khach"');
PREPARE stmt FROM @sql_stmt;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 6. Cập nhật cảnh báo mới cho loại gian lận thẻ / trộm cắp
ALTER TABLE `canh_bao` MODIFY COLUMN `loai` enum(
  'DANH_SACH_DEN',
  'DO_TIN_CAY_THAP',
  'XE_LA',
  'CAMERA_MAT_KET_NOI',
  'LUOT_RA_KHONG_CO_VAO',
  'XE_O_LAI_QUA_LAU',
  'THE_KHONG_KHOP_BIEN_SO',
  'THE_VI_PHAM_ANTI_PASSBACK',
  'THE_KHACH_LECH_BIEN_SO_RA_VAO',
  'DI_SAI_LAN_QUY_DINH'
) COLLATE utf8mb4_unicode_ci NOT NULL;

SET FOREIGN_KEY_CHECKS = 1;

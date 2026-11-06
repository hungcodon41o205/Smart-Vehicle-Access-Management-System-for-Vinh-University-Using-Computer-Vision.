-- [CSDL VinhGate 2.0] Database Management System
-- ============================================================================
-- Migration: v2_add_dang_ky_khach.sql
-- Nâng cấp mô hình CSDL từ 12 bảng lên 13 bảng (Cách B)
-- Tách riêng bảng DANG_KY_KHACH và cập nhật khóa ngoại trong LUOT_RA_VAO
-- ============================================================================

USE vinhgate_db;

-- 1. Tạo bảng DANG_KY_KHACH nếu chưa có
CREATE TABLE IF NOT EXISTS dang_ky_khach (
    id INT AUTO_INCREMENT PRIMARY KEY,
    khach_id INT NOT NULL,
    bien_so VARCHAR(20) NOT NULL COMMENT 'Biển số xe của khách',
    loai_xe ENUM('XE_MAY', 'O_TO') NOT NULL,
    ma_tam VARCHAR(30) NOT NULL UNIQUE COMMENT 'Mã phiếu tạm thời cấp cho khách',
    ly_do_den VARCHAR(255) NULL,
    nguoi_tiep_don VARCHAR(100) NULL,
    tu_luc DATETIME NOT NULL,
    den_luc DATETIME NOT NULL COMMENT 'Quá giờ này chưa ra sẽ cảnh báo KHACH_QUA_GIO',
    phi_gui_xe DECIMAL(10,2) DEFAULT 0.00,
    trang_thai ENUM('DANG_HIEU_LUC', 'DA_VAO', 'DA_RA', 'QUA_HAN', 'HUY') DEFAULT 'DANG_HIEU_LUC',
    nguoi_tao_id INT NULL,
    ngay_tao DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_dkk_bienso_trangthai (bien_so, trang_thai),
    CONSTRAINT fk_dkk_khach FOREIGN KEY (khach_id) REFERENCES khach(id) ON DELETE CASCADE,
    CONSTRAINT fk_dkk_nguoitao FOREIGN KEY (nguoi_tao_id) REFERENCES tai_khoan(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. Thêm cột dang_ky_khach_id vào bảng luot_ra_vao nếu chưa tồn tại
SET @dbname = DATABASE();
SET @tablename = "luot_ra_vao";
SET @columnname = "dang_ky_khach_id";
SET @preparedStatement = (SELECT IF(
  (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE
      TABLE_SCHEMA = @dbname
      AND TABLE_NAME = @tablename
      AND COLUMN_NAME = @columnname
  ) > 0,
  "SELECT 1",
  "ALTER TABLE luot_ra_vao ADD COLUMN dang_ky_khach_id INT NULL AFTER phuong_tien_id, ADD CONSTRAINT fk_luot_dkkhach FOREIGN KEY (dang_ky_khach_id) REFERENCES dang_ky_khach(id) ON DELETE SET NULL;"
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

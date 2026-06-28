-- ============================================================
--  MySQL Event: Tu dong sao luu CinemaDB luc 2h sang moi ngay
--  Luu y: Can bat MySQL Event Scheduler truoc khi chay
--         SET GLOBAL event_scheduler = ON;
-- ============================================================

-- Kiem tra Event Scheduler dang bat khong
SHOW VARIABLES LIKE 'event_scheduler';
-- Neu OFF thi bat len:
-- SET GLOBAL event_scheduler = ON;

-- Tao bang log de ghi lai lich su backup (tuy chon nhung huu ich)
CREATE TABLE IF NOT EXISTS BackupLog (
    MaLog     INT AUTO_INCREMENT PRIMARY KEY,
    ThoiGian  DATETIME NOT NULL DEFAULT NOW(),
    TrangThai VARCHAR(20) NOT NULL,   -- 'SUCCESS' hoac 'FAILED'
    GhiChu    TEXT
);

-- ============================================================
--  MYSQL EVENT: chay moi ngay luc 02:00:00
-- ============================================================
DELIMITER $$

CREATE EVENT IF NOT EXISTS evt_BackupHangNgay
ON SCHEDULE
    EVERY 1 DAY
    STARTS (CURDATE() + INTERVAL 1 DAY + INTERVAL 2 HOUR)   -- bat dau tu 2h sang ngay mai
DO
BEGIN
    -- MySQL khong the tu dong ghi file ra dia bang EVENT.
    -- Buoc nay ghi log vao bang BackupLog de xac nhan Event dang chay.
    -- Viec dump thuc te (mysqldump) van phai dung backup_cinemadb.bat
    -- hoac mot external script goi tu Task Scheduler / Cron job.
    INSERT INTO BackupLog (TrangThai, GhiChu)
    VALUES ('SUCCESS', CONCAT('Event chay luc: ', NOW(), ' - Vui long kiem tra file dump tai thu muc backup/dumps'));
END$$

DELIMITER ;

-- Kiem tra cac event dang ton tai
SHOW EVENTS FROM CinemaDB;

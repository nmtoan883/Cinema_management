CREATE DATABASE IF NOT EXISTS CinemaDB;
USE CinemaDB;

CREATE TABLE THELOAI (
    MaTheLoai INT AUTO_INCREMENT PRIMARY KEY,
    TenTheLoai VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE DAODIEN (
    MaDaoDien INT AUTO_INCREMENT PRIMARY KEY,
    HoTen VARCHAR(100) NOT NULL,
    NgaySinh DATE
);

CREATE TABLE DIENVIEN (
    MaDienVien INT AUTO_INCREMENT PRIMARY KEY,
    HoTen VARCHAR(100) NOT NULL,
    NgaySinh DATE
);

CREATE TABLE PHIM (
    MaPhim INT AUTO_INCREMENT PRIMARY KEY,
    TenPhim VARCHAR(255) NOT NULL,
    ThoiLuong INT NOT NULL, 
    NgayKhoiChieu DATE,
    GioiHanDoTuoi VARCHAR(10), -- Cột này sẽ được tạo mới thành công
    MaDaoDien INT,
    FOREIGN KEY (MaDaoDien) REFERENCES DAODIEN(MaDaoDien) ON DELETE SET NULL
);

CREATE TABLE PHIM_THELOAI (
    MaPhim INT,
    MaTheLoai INT,
    PRIMARY KEY (MaPhim, MaTheLoai),
    FOREIGN KEY (MaPhim) REFERENCES PHIM(MaPhim) ON DELETE CASCADE,
    FOREIGN KEY (MaTheLoai) REFERENCES THELOAI(MaTheLoai) ON DELETE CASCADE
);

CREATE TABLE PHIM_DIENVIEN (
    MaPhim INT,
    MaDienVien INT,
    PRIMARY KEY (MaPhim, MaDienVien),
    FOREIGN KEY (MaPhim) REFERENCES PHIM(MaPhim) ON DELETE CASCADE,
    FOREIGN KEY (MaDienVien) REFERENCES DIENVIEN(MaDienVien) ON DELETE CASCADE
);

-- II.SQL NÂNG CAO CẦN LÀM
CREATE OR REPLACE VIEW v_DanhSachPhim AS
SELECT 
    p.MaPhim,
    p.TenPhim,
    p.ThoiLuong,
    p.NgayKhoiChieu,
    p.GioiHanDoTuoi,
    IFNULL(dd.HoTen, 'Chưa cập nhật') AS TenDaoDien,
    IFNULL(GROUP_CONCAT(tl.TenTheLoai SEPARATOR ', '), 'Chưa phân loại') AS CacTheLoai
FROM PHIM p
LEFT JOIN DAODIEN dd ON p.MaDaoDien = dd.MaDaoDien
LEFT JOIN PHIM_THELOAI ptl ON p.MaPhim = ptl.MaPhim
LEFT JOIN THELOAI tl ON ptl.MaTheLoai = tl.MaTheLoai
GROUP BY p.MaPhim;

DELIMITER $$

CREATE PROCEDURE sp_ThemPhimMoi(
    IN p_TenPhim VARCHAR(255),
    IN p_ThoiLuong INT,
    IN p_NgayKhoiChieu DATE,
    IN p_GioiHanDoTuoi VARCHAR(10),
    IN p_MaDaoDien INT,
    IN p_DS_MaTheLoai TEXT,   -- Chuỗi dạng '1,2,3'
    IN p_DS_MaDienVien TEXT   -- Chuỗi dạng '4,5,6'
)
BEGIN
    DECLARE v_MaPhimMoi INT;
    DECLARE v_Item TEXT;
    
    -- Khai báo kết thúc nếu có lỗi xảy ra để Rollback dữ liệu
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Lỗi hệ thống! Đã hủy thao tác thêm phim.';
    END;

    START TRANSACTION;

    -- 1. Chèn vào bảng PHIM
    INSERT INTO PHIM (TenPhim, ThoiLuong, NgayKhoiChieu, GioiHanDoTuoi, MaDaoDien)
    VALUES (p_TenPhim, p_ThoiLuong, p_NgayKhoiChieu, p_GioiHanDoTuoi, p_MaDaoDien);
    
    -- Lấy ID của bộ phim vừa tạo
    SET v_MaPhimMoi = LAST_INSERT_ID();

    -- 2. Xử lý chuỗi danh sách Thể loại và chèn vào PHIM_THELOAI
    IF p_DS_MaTheLoai IS NOT NULL AND LENGTH(TRIM(p_DS_MaTheLoai)) > 0 THEN
        WHILE CHAR_LENGTH(p_DS_MaTheLoai) > 0 DO
            SET v_Item = SUBSTRING_INDEX(p_DS_MaTheLoai, ',', 1);
            
            INSERT INTO PHIM_THELOAI (MaPhim, MaTheLoai) 
            VALUES (v_MaPhimMoi, CAST(v_Item AS UNSIGNED));
            
            IF CHAR_LENGTH(p_DS_MaTheLoai) = CHAR_LENGTH(v_Item) THEN
                SET p_DS_MaTheLoai = '';
            ELSE
                SET p_DS_MaTheLoai = SUBSTRING(p_DS_MaTheLoai, CHAR_LENGTH(v_Item) + 2);
            END IF;
        END WHILE;
    END IF;

    -- 3. Xử lý chuỗi danh sách Diễn viên và chèn vào PHIM_DIENVIEN
    IF p_DS_MaDienVien IS NOT NULL AND LENGTH(TRIM(p_DS_MaDienVien)) > 0 THEN
        WHILE CHAR_LENGTH(p_DS_MaDienVien) > 0 DO
            SET v_Item = SUBSTRING_INDEX(p_DS_MaDienVien, ',', 1);
            
            INSERT INTO PHIM_DIENVIEN (MaPhim, MaDienVien) 
            VALUES (v_MaPhimMoi, CAST(v_Item AS UNSIGNED));
            
            IF CHAR_LENGTH(p_DS_MaDienVien) = CHAR_LENGTH(v_Item) THEN
                SET p_DS_MaDienVien = '';
            ELSE
                SET p_DS_MaDienVien = SUBSTRING(p_DS_MaDienVien, CHAR_LENGTH(v_Item) + 2);
            END IF;
        END WHILE;
    END IF;

    COMMIT;
END$$

DELIMITER ;

DELIMITER $$

CREATE FUNCTION f_DemSoPhimCuaDienVien(p_MaDienVien INT) 
RETURNS INT
DETERMINISTIC
READS SQL DATA
BEGIN
    DECLARE v_TongSoPhim INT DEFAULT 0;
    
    SELECT COUNT(*) INTO v_TongSoPhim
    FROM PHIM_DIENVIEN
    WHERE MaDienVien = p_MaDienVien;
    
    RETURN v_TongSoPhim;
END$$

DELIMITER ;

-- III.DỮ LIỆU MẪU
-- 1. Chèn dữ liệu vào bảng THELOAI
INSERT INTO THELOAI (TenTheLoai) VALUES 
('Hành động'),
('Hài kịch'),
('Kinh dị'),
('Tình cảm'),
('Khoa học Viễn tưởng');

-- 2. Chèn dữ liệu vào bảng DAODIEN
INSERT INTO DAODIEN (HoTen, NgaySinh) VALUES 
('Lý Hải', '1968-09-28'),
('Trấn Thành', '1987-02-05'),
('Christopher Nolan', '1970-07-30'),
('Ngô Thanh Vân', '1979-02-26');

-- 3. Chèn dữ liệu vào bảng DIENVIEN
INSERT INTO DIENVIEN (HoTen, NgaySinh) VALUES 
('Ninh Dương Lan Ngọc', '1990-04-04'),
('Kiều Minh Tuấn', '1988-10-29'),
('Kaity Nguyễn', '1999-04-09'),
('Trấn Thành', '1987-02-05'),
('Tuấn Trần', '1992-11-20'),
('Leonardo DiCaprio', '1974-11-11'),
('Cillian Murphy', '1976-05-25'),
('Mạc Văn Khoa', '1992-05-04');

-- 4. Chèn dữ liệu vào bảng PHIM
INSERT INTO PHIM (TenPhim, ThoiLuong, NgayKhoiChieu, GioiHanDoTuoi, MaDaoDien) VALUES 
('Lật Mặt 7: Một Điều Ước', 138, '2024-04-26', 'T13', 1),
('Mai', '131', '2024-02-10', 'T18', 2),
('Nhà Bà Nữ', '102', '2023-01-22', 'T16', 2),
('Inception', '148', '2010-07-16', 'T13', 3),
('Oppenheimer', '180', '2023-07-21', 'T18', 3),
('Hai Phượng', '98', '2019-02-22', 'T18', 4),
('Em Chưa 18', '95', '2017-04-28', 'C16', 2),
('Tiệc Trăng Máu', '118', '2020-10-23', 'T16', NULL), -- Đạo diễn khác/Chưa cập nhật
('Bố Già', '128', '2021-03-05', 'T13', 2),
('Chị Mười Ba', '96', '2020-12-25', 'T16', NULL);

-- 5. Chèn dữ liệu vào bảng trung gian PHIM_THELOAI (Một phim có nhiều thể loại)
INSERT INTO PHIM_THELOAI (MaPhim, MaTheLoai) VALUES 
(1, 2), (1, 4), -- Lật Mặt 7: Hài kịch, Tình cảm
(2, 4),         -- Mai: Tình cảm
(3, 2), (3, 4), -- Nhà Bà Nữ: Hài kịch, Tình cảm
(4, 1), (4, 5), -- Inception: Hành động, Khoa học Viễn tưởng
(5, 1),         -- Oppenheimer: Hành động (Chính kịch)
(6, 1),         -- Hai Phượng: Hành động
(7, 2), (7, 4), -- Em Chưa 18: Hài kịch, Tình cảm
(8, 2), (8, 4), -- Tiệc Trăng Máu: Hài kịch, Tình cảm
(9, 2), (9, 4), -- Bố Già: Hài kịch, Tình cảm
(10, 1), (10, 2);-- Chị Mười Ba: Hành động, Hài kịch

-- 6. Chèn dữ liệu vào bảng trung gian PHIM_DIENVIEN (Một phim nhiều diễn viên, một diễn viên đóng nhiều phim)
INSERT INTO PHIM_DIENVIEN (MaPhim, MaDienVien) VALUES 
(1, 8),         -- Lật Mặt 7: Mạc Văn Khoa
(2, 5),         -- Mai: Tuấn Trần
(2, 4),         -- Mai: Trấn Thành
(3, 4),         -- Nhà Bà Nữ: Trấn Thành
(4, 6),         -- Inception: Leonardo DiCaprio
(4, 7),         -- Inception: Cillian Murphy
(5, 7),         -- Oppenheimer: Cillian Murphy
(7, 2), (7, 3), -- Em Chưa 18: Kiều Minh Tuấn, Kaity Nguyễn
(8, 1), (8, 2), (8, 3), -- Tiệc Trăng Máu: Lan Ngọc, Kiều Minh Tuấn, Kaity Nguyễn
(9, 4), (9, 5), -- Bố Già: Trấn Thành, Tuấn Trần
(10, 2);        -- Chị Mười Ba: Kiều Minh Tuấn

-- Quản lý Rạp, Phòng chiếu & Ghế ngồi --
-- CumRap
CREATE TABLE CumRap (
    MaCumRap INT AUTO_INCREMENT,
    TenCumRap VARCHAR(100) NOT NULL,
    DiaChi VARCHAR(255) NOT NULL,
    Hotline VARCHAR(15) NOT NULL,

    CONSTRAINT PK_CumRap 
        PRIMARY KEY (MaCumRap),

    CONSTRAINT UQ_CumRap_Ten_DiaChi 
        UNIQUE (TenCumRap, DiaChi),

    CONSTRAINT CK_CumRap_Hotline
        CHECK (CHAR_LENGTH(Hotline) BETWEEN 9 AND 15)
);

-- LoaiPhong
CREATE TABLE LoaiPhong (
    MaLoaiPhong INT AUTO_INCREMENT,
    TenLoaiPhong VARCHAR(50) NOT NULL,
    PhuThu DECIMAL(18,2) NOT NULL DEFAULT 0,

    CONSTRAINT PK_LoaiPhong
        PRIMARY KEY (MaLoaiPhong),

    CONSTRAINT UQ_LoaiPhong_TenLoaiPhong
        UNIQUE (TenLoaiPhong),

    CONSTRAINT CK_LoaiPhong_PhuThu
        CHECK (PhuThu >= 0)
);


-- LoaiGhe
CREATE TABLE LoaiGhe (
    MaLoaiGhe INT AUTO_INCREMENT,
    TenLoai VARCHAR(50) NOT NULL,
    PhuThu DECIMAL(18,2) NOT NULL DEFAULT 0,

    CONSTRAINT PK_LoaiGhe
        PRIMARY KEY (MaLoaiGhe),

    CONSTRAINT UQ_LoaiGhe_TenLoai
        UNIQUE (TenLoai),

    CONSTRAINT CK_LoaiGhe_PhuThu
        CHECK (PhuThu >= 0)
);

-- PhongChieu --
CREATE TABLE PhongChieu (
    MaPhong INT AUTO_INCREMENT,
    TenPhong VARCHAR(50) NOT NULL,
    MaCumRap INT NOT NULL,
    MaLoaiPhong INT NOT NULL,
    SucChua INT NOT NULL,

    CONSTRAINT PK_PhongChieu
        PRIMARY KEY (MaPhong),

    CONSTRAINT FK_PhongChieu_CumRap
        FOREIGN KEY (MaCumRap) 
        REFERENCES CumRap(MaCumRap),

    CONSTRAINT FK_PhongChieu_LoaiPhong
        FOREIGN KEY (MaLoaiPhong) 
        REFERENCES LoaiPhong(MaLoaiPhong),

    CONSTRAINT CK_PhongChieu_SucChua
        CHECK (SucChua > 0),

    CONSTRAINT UQ_PhongChieu_CumRap_TenPhong
        UNIQUE (MaCumRap, TenPhong)
);

-- Ghe --
CREATE TABLE Ghe (
    MaGhe INT AUTO_INCREMENT,
    TenGhe VARCHAR(10) NOT NULL,
    MaPhong INT NOT NULL,
    MaLoaiGhe INT NOT NULL,

    CONSTRAINT PK_Ghe
        PRIMARY KEY (MaGhe),

    CONSTRAINT FK_Ghe_PhongChieu
        FOREIGN KEY (MaPhong) 
        REFERENCES PhongChieu(MaPhong),

    CONSTRAINT FK_Ghe_LoaiGhe
        FOREIGN KEY (MaLoaiGhe) 
        REFERENCES LoaiGhe(MaLoaiGhe),

    CONSTRAINT UQ_Ghe_MaPhong_TenGhe
        UNIQUE (MaPhong, TenGhe)
);

-- VIEW --
CREATE VIEW v_ThongKePhongTheoCumRap AS
SELECT 
    cr.MaCumRap,
    cr.TenCumRap,
    cr.DiaChi,
    cr.Hotline,
    COUNT(pc.MaPhong) AS TongSoPhong,
    IFNULL(SUM(pc.SucChua), 0) AS TongSucChua
FROM CumRap cr
LEFT JOIN PhongChieu pc
    ON cr.MaCumRap = pc.MaCumRap
GROUP BY 
    cr.MaCumRap,
    cr.TenCumRap,
    cr.DiaChi,
    cr.Hotline;

-- TRIGGER
DELIMITER $$

CREATE TRIGGER trg_KiemTraSucChuaGhe
AFTER INSERT ON Ghe
FOR EACH ROW
BEGIN
    DECLARE SoGheHienCo INT;
    DECLARE SucChuaPhong INT;

    SELECT COUNT(*)
    INTO SoGheHienCo
    FROM Ghe
    WHERE MaPhong = NEW.MaPhong;

    SELECT SucChua
    INTO SucChuaPhong
    FROM PhongChieu
    WHERE MaPhong = NEW.MaPhong;

    IF SoGheHienCo > SucChuaPhong THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'So luong ghe vuot qua suc chua da khai bao cua phong chieu.';
    END IF;
END$$

DELIMITER ;

-- STORED PROCEDURE
DELIMITER $$

CREATE PROCEDURE sp_TaoPhongVaGhe(
    IN p_TenPhong VARCHAR(50),
    IN p_MaCumRap INT,
    IN p_MaLoaiPhong INT,
    IN p_SucChua INT,
    IN p_MaLoaiGheMacDinh INT
)
BEGIN
    DECLARE v_MaPhongMoi INT;
    DECLARE v_Hang INT DEFAULT 1;
    DECLARE v_Cot INT;
    DECLARE v_KyTuHang CHAR(1);
    DECLARE v_TenGhe VARCHAR(10);

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    -- Kiểm tra cụm rạp có tồn tại không
    IF NOT EXISTS (
        SELECT 1 FROM CumRap WHERE MaCumRap = p_MaCumRap
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Cum rap khong ton tai.';
    END IF;

    -- Kiểm tra loại phòng có tồn tại không
    IF NOT EXISTS (
        SELECT 1 FROM LoaiPhong WHERE MaLoaiPhong = p_MaLoaiPhong
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Loai phong khong ton tai.';
    END IF;

    -- Kiểm tra loại ghế mặc định có tồn tại không
    IF NOT EXISTS (
        SELECT 1 FROM LoaiGhe WHERE MaLoaiGhe = p_MaLoaiGheMacDinh
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Loai ghe mac dinh khong ton tai.';
    END IF;

    -- A1 đến J10 là 100 ghế
    IF p_SucChua < 100 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Suc chua phai lon hon hoac bang 100 de tao ghe tu A1 den J10.';
    END IF;

    START TRANSACTION;

    INSERT INTO PhongChieu(TenPhong, MaCumRap, MaLoaiPhong, SucChua)
    VALUES (p_TenPhong, p_MaCumRap, p_MaLoaiPhong, p_SucChua);

    SET v_MaPhongMoi = LAST_INSERT_ID();

    WHILE v_Hang <= 10 DO
        SET v_KyTuHang = CHAR(64 + v_Hang);
        SET v_Cot = 1;

        WHILE v_Cot <= 10 DO
            SET v_TenGhe = CONCAT(v_KyTuHang, v_Cot);

            INSERT INTO Ghe(TenGhe, MaPhong, MaLoaiGhe)
            VALUES (v_TenGhe, v_MaPhongMoi, p_MaLoaiGheMacDinh);

            SET v_Cot = v_Cot + 1;
        END WHILE;

        SET v_Hang = v_Hang + 1;
    END WHILE;

    COMMIT;
END$$

DELIMITER ;
-- Quản lý Lịch chiếu & Giá vé --
-- =====================================================
-- PHAN HE: LICH CHIEU & GIA VE
-- MySQL
-- =====================================================

CREATE TABLE GiaVe_CoBan (
    MaGiaVe INT AUTO_INCREMENT PRIMARY KEY,
    KhungGio VARCHAR(50) NOT NULL,
    LoaiNgay VARCHAR(50) NOT NULL,
    GiaCoBan DECIMAL(18,2) NOT NULL,
    CHECK (GiaCoBan >= 0)
);

CREATE TABLE NgayLe (
    MaNgayLe INT AUTO_INCREMENT PRIMARY KEY,
    TenNgayLe VARCHAR(100) NOT NULL,
    Ngay DATE NOT NULL,
    PhuThu DECIMAL(18,2) NOT NULL DEFAULT 0,
    UNIQUE (Ngay),
    CHECK (PhuThu >= 0)
);

CREATE TABLE SuatChieu (
    MaSuatChieu INT AUTO_INCREMENT PRIMARY KEY,
    MaPhim INT NOT NULL,
    MaPhong INT NOT NULL,
    MaGiaVe INT NOT NULL,
    GioBatDau DATETIME NOT NULL,
    GioKetThuc DATETIME NOT NULL,

    FOREIGN KEY (MaPhim) REFERENCES Phim(MaPhim),
    FOREIGN KEY (MaPhong) REFERENCES PhongChieu(MaPhong),
    FOREIGN KEY (MaGiaVe) REFERENCES GiaVe_CoBan(MaGiaVe),

    CHECK (GioKetThuc > GioBatDau)
);

-- VIEW: Lich chieu hom nay
CREATE VIEW v_LichChieuHomNay AS
SELECT
    sc.MaSuatChieu,
    p.TenPhim,
    pc.TenPhong,
    cr.MaCumRap,
    cr.TenCumRap,
    sc.GioBatDau,
    sc.GioKetThuc,
    gv.KhungGio,
    gv.LoaiNgay,
    gv.GiaCoBan
FROM SuatChieu sc
JOIN Phim p 
    ON sc.MaPhim = p.MaPhim
JOIN PhongChieu pc 
    ON sc.MaPhong = pc.MaPhong
JOIN CumRap cr 
    ON pc.MaCumRap = cr.MaCumRap
JOIN GiaVe_CoBan gv 
    ON sc.MaGiaVe = gv.MaGiaVe
WHERE DATE(sc.GioBatDau) = CURDATE();

DELIMITER $$

-- TRIGGER: Chong trung suat chieu khi them
CREATE TRIGGER trg_KiemTraTrungSuatChieu_Insert
BEFORE INSERT ON SuatChieu
FOR EACH ROW
BEGIN
    IF EXISTS (
        SELECT 1
        FROM SuatChieu
        WHERE MaPhong = NEW.MaPhong
          AND NEW.GioBatDau < GioKetThuc
          AND NEW.GioKetThuc > GioBatDau
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Phong chieu da co suat chieu trung gio.';
    END IF;
END$$

-- TRIGGER: Chong trung suat chieu khi sua
CREATE TRIGGER trg_KiemTraTrungSuatChieu_Update
BEFORE UPDATE ON SuatChieu
FOR EACH ROW
BEGIN
    IF EXISTS (
        SELECT 1
        FROM SuatChieu
        WHERE MaPhong = NEW.MaPhong
          AND MaSuatChieu <> OLD.MaSuatChieu
          AND NEW.GioBatDau < GioKetThuc
          AND NEW.GioKetThuc > GioBatDau
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Phong chieu da co suat chieu trung gio.';
    END IF;
END$$

-- FUNCTION: Tinh gia ve cuoi cung
CREATE FUNCTION fn_TinhGiaVeCuoiCung(p_MaSuatChieu INT)
RETURNS DECIMAL(18,2)
READS SQL DATA
BEGIN
    DECLARE v_GiaCoBan DECIMAL(18,2);
    DECLARE v_PhuThuLoaiPhong DECIMAL(18,2);
    DECLARE v_PhuThuNgayLe DECIMAL(18,2);
    DECLARE v_GiaCuoiCung DECIMAL(18,2);

    SELECT 
        gv.GiaCoBan,
        lp.PhuThu,
        IFNULL(nl.PhuThu, 0)
    INTO 
        v_GiaCoBan,
        v_PhuThuLoaiPhong,
        v_PhuThuNgayLe
    FROM SuatChieu sc
    JOIN GiaVe_CoBan gv 
        ON sc.MaGiaVe = gv.MaGiaVe
    JOIN PhongChieu pc 
        ON sc.MaPhong = pc.MaPhong
    JOIN LoaiPhong lp 
        ON pc.MaLoaiPhong = lp.MaLoaiPhong
    LEFT JOIN NgayLe nl 
        ON DATE(sc.GioBatDau) = nl.Ngay
    WHERE sc.MaSuatChieu = p_MaSuatChieu;

    SET v_GiaCuoiCung = v_GiaCoBan 
                      + v_PhuThuLoaiPhong 
                      + v_PhuThuNgayLe;

    RETURN v_GiaCuoiCung;
END$$

DELIMITER ;
-- ------Quản lý Khách hàng, Nhân viên & Bắp nước----------
CREATE TABLE HangThanhVien (
    MaHang INT AUTO_INCREMENT PRIMARY KEY,
    TenHang VARCHAR(50) NOT NULL,
    DiemYeuCau INT NOT NULL
);

CREATE TABLE DichVu (
    MaDichVu INT AUTO_INCREMENT PRIMARY KEY,
    TenDichVu VARCHAR(100) NOT NULL,
    GiaBan INT NOT NULL,
    CONSTRAINT CHK_GiaBan CHECK (GiaBan >= 0)
);

CREATE TABLE KhachHang (
    MaKH INT AUTO_INCREMENT PRIMARY KEY,
    HoTen VARCHAR(100) NOT NULL,
    SDT VARCHAR(15) NOT NULL UNIQUE,
    Email VARCHAR(100),
    DiemTichLuy INT DEFAULT 0,
    MaHang INT NOT NULL,
    CONSTRAINT FK_KhachHang_Hang FOREIGN KEY (MaHang) REFERENCES HangThanhVien(MaHang)
);

CREATE TABLE NhanVien (
    MaNV INT AUTO_INCREMENT PRIMARY KEY,
    HoTen VARCHAR(100) NOT NULL,
    ChucVu VARCHAR(50) NOT NULL,
    MaCumRap INT NOT NULL,
    CONSTRAINT FK_NhanVien_CumRap FOREIGN KEY (MaCumRap) REFERENCES CumRap(MaCumRap)
);

-- 2. INSERT DỮ LIỆU
INSERT INTO HangThanhVien (TenHang, DiemYeuCau) VALUES 
('Member (Đồng)', 0), ('VIP (Bạc)', 1000), 
('VVIP (Vàng)', 3000), ('Diamond (Kim Cương)', 5000);

INSERT INTO DichVu (TenDichVu, GiaBan) VALUES 
('Bắp ngọt lớn', 55000), ('Pepsi lớn', 35000), 
('Combo Couple', 110000);

INSERT INTO CumRap (TenCumRap, DiaChi, Hotline) VALUES 
('Cinema Hùng Vương', '123 Hùng Vương', '0901234567');

INSERT INTO KhachHang (HoTen, SDT, Email, DiemTichLuy, MaHang) VALUES 
('Nguyễn Văn A', '0901234567', 'nva@gmail.com', 500, 1),
('Trần Thị B', '0987654321', 'ttb@gmail.com', 3500, 3);

INSERT INTO NhanVien (HoTen, ChucVu, MaCumRap) VALUES 
('Lê Nhân Viên', 'Bán vé', 1), ('Phạm Quản Lý', 'Quản lý rạp', 1);

-- 3. VIEW DANH SÁCH KHÁCH VIP
CREATE VIEW View_DanhSachKhachHangVIP AS
SELECT KH.MaKH, KH.HoTen, KH.SDT, KH.Email, KH.DiemTichLuy, HTV.TenHang
FROM KhachHang KH
JOIN HangThanhVien HTV ON KH.MaHang = HTV.MaHang
WHERE HTV.DiemYeuCau >= 1000;

-- 4. STORED PROCEDURE: TÌM KHÁCH BẰNG SĐT
DELIMITER //
CREATE PROCEDURE sp_TimKhachHangBangSDT(IN p_SoDienThoai VARCHAR(15))
BEGIN
    SELECT KH.HoTen, KH.DiemTichLuy, HTV.TenHang
    FROM KhachHang KH
    JOIN HangThanhVien HTV ON KH.MaHang = HTV.MaHang
    WHERE KH.SDT = p_SoDienThoai;
END //
DELIMITER ;

-- 5. TRIGGER: TỰ ĐỘNG NÂNG HẠNG (Code MySQL cực kỳ ngắn gọn)
DELIMITER //
CREATE TRIGGER trg_TuDongNangHangThanhVien
BEFORE UPDATE ON KhachHang
FOR EACH ROW
BEGIN
    -- Chỉ dò tìm và xét duyệt lại hạng nếu Điểm Tích Lũy có sự thay đổi
    IF NEW.DiemTichLuy <> OLD.DiemTichLuy THEN
        -- Tự động gán Mã Hạng mới cho khách hàng trước khi lưu vào DB
        SET NEW.MaHang = (
            SELECT MaHang 
            FROM HangThanhVien 
            WHERE DiemYeuCau <= NEW.DiemTichLuy 
            ORDER BY DiemYeuCau DESC 
            LIMIT 1 -- LIMIT 1 thay cho TOP 1 của SQL Server
        );
    END IF;
END //
DELIMITER ;

-- Quản lý Đặt Vé, Hóa Đơn & Doanh thu --

CREATE TABLE HOADON (
    MaHoaDon VARCHAR(10) PRIMARY KEY,
    MaKH VARCHAR(10),
    MaNV VARCHAR(10),
    NgayLap DATETIME,
    TongTien DECIMAL(18,2)
);


/*
    TAO BANG CHITIET_VE
*/

CREATE TABLE CHITIET_VE (
    MaVe VARCHAR(10) PRIMARY KEY,
    MaHoaDon VARCHAR(10),
    MaSuatChieu VARCHAR(10),
    MaGhe VARCHAR(10),
    GiaMua DECIMAL(18,2)
);


/*
    TAO BANG CHITIET_DICHVU
*/

CREATE TABLE CHITIET_DICHVU (
    MaHoaDon VARCHAR(10),
    MaDichVu VARCHAR(10),
    SoLuong INT,
    ThanhTien DECIMAL(18,2)
);


/*
    VIEW DOANH THU THEO THANG
*/

CREATE OR REPLACE VIEW v_DoanhThuTheoThang AS
SELECT
    MONTH(NgayLap) AS Thang,
    YEAR(NgayLap) AS Nam,
    SUM(TongTien) AS DoanhThu
FROM HOADON
GROUP BY
    MONTH(NgayLap),
    YEAR(NgayLap);


/*
    TRIGGER CHONG BAN TRUNG GHE
*/

DELIMITER $$

CREATE TRIGGER trg_KiemTraTrungVe
BEFORE INSERT
ON CHITIET_VE
FOR EACH ROW
BEGIN

    IF EXISTS (
        SELECT 1
        FROM CHITIET_VE
        WHERE MaSuatChieu = NEW.MaSuatChieu
          AND MaGhe = NEW.MaGhe
    )
    THEN

        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Ghe nay da duoc ban';

    END IF;

END$$

DELIMITER ;


/*
    STORED PROCEDURE BAN VE
*/

DELIMITER $$

CREATE PROCEDURE sp_BanVe
(
    IN p_MaHoaDon VARCHAR(10),
    IN p_MaKH VARCHAR(10),
    IN p_MaNV VARCHAR(10),
    IN p_MaVe VARCHAR(10),
    IN p_MaSuatChieu VARCHAR(10),
    IN p_MaGhe VARCHAR(10),
    IN p_GiaMua DECIMAL(18,2)
)
BEGIN

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
    END;

    START TRANSACTION;

    INSERT INTO HOADON
    (
        MaHoaDon,
        MaKH,
        MaNV,
        NgayLap,
        TongTien
    )
    VALUES
    (
        p_MaHoaDon,
        p_MaKH,
        p_MaNV,
        NOW(),
        p_GiaMua
    );

    INSERT INTO CHITIET_VE
    (
        MaVe,
        MaHoaDon,
        MaSuatChieu,
        MaGhe,
        GiaMua
    )
    VALUES
    (
        p_MaVe,
        p_MaHoaDon,
        p_MaSuatChieu,
        p_MaGhe,
        p_GiaMua
    );

    COMMIT;

END$$

DELIMITER ;
DROP DATABASE IF EXISTS CinemaDB;
CREATE DATABASE IF NOT EXISTS CinemaDB;
USE CinemaDB;

CREATE TABLE THELOAI (
    MaTheLoai INT AUTO_INCREMENT PRIMARY KEY,
    TenTheLoai VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE GIOIHAN_DOTUOI (
    MaGioiHan INT AUTO_INCREMENT PRIMARY KEY,
    KyHieu VARCHAR(10) NOT NULL UNIQUE,
    MoTa VARCHAR(100)
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
    MaGioiHan INT,
    Poster VARCHAR(500) DEFAULT 'https://upload.wikimedia.org/wikipedia/commons/thumb/6/65/No-Image-Placeholder.svg/1665px-No-Image-Placeholder.svg.png',
    MoTa TEXT,
    TrailerURL VARCHAR(500),
    MaDaoDien INT,
    FOREIGN KEY (MaDaoDien) REFERENCES DAODIEN(MaDaoDien) ON DELETE SET NULL,
    FOREIGN KEY (MaGioiHan) REFERENCES GIOIHAN_DOTUOI(MaGioiHan) ON DELETE SET NULL
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
    IFNULL(gh.KyHieu, 'Chưa phân loại') AS GioiHanDoTuoi,
    p.Poster,
    p.MoTa,
    p.TrailerURL,
    IFNULL(dd.HoTen, 'Chưa cập nhật') AS TenDaoDien,
    IFNULL(GROUP_CONCAT(tl.TenTheLoai SEPARATOR ', '), 'Chưa phân loại') AS CacTheLoai
FROM PHIM p
LEFT JOIN GIOIHAN_DOTUOI gh ON p.MaGioiHan = gh.MaGioiHan
LEFT JOIN DAODIEN dd ON p.MaDaoDien = dd.MaDaoDien
LEFT JOIN PHIM_THELOAI ptl ON p.MaPhim = ptl.MaPhim
LEFT JOIN THELOAI tl ON ptl.MaTheLoai = tl.MaTheLoai
GROUP BY p.MaPhim;

DELIMITER $$

CREATE PROCEDURE sp_ThemPhimMoi(
    IN p_TenPhim VARCHAR(255),
    IN p_ThoiLuong INT,
    IN p_NgayKhoiChieu DATE,
    IN p_MaGioiHan INT,
    IN p_Poster VARCHAR(500),
    IN p_MoTa TEXT,
    IN p_TrailerURL VARCHAR(500),
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
    INSERT INTO PHIM (TenPhim, ThoiLuong, NgayKhoiChieu, MaGioiHan, Poster, MoTa, TrailerURL, MaDaoDien)
    VALUES (p_TenPhim, p_ThoiLuong, p_NgayKhoiChieu, p_MaGioiHan, p_Poster, p_MoTa, p_TrailerURL, p_MaDaoDien);
    
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

-- Thêm mốc giới hạn độ tuổi
INSERT INTO GIOIHAN_DOTUOI (KyHieu, MoTa) VALUES 
('P', 'Phim được phép phổ biến đến người xem ở mọi độ tuổi'),
('K', 'Phim được phổ biến đến người xem dưới 13 tuổi với điều kiện xem cùng cha, mẹ hoặc người giám hộ'),
('T13', 'Phim được phổ biến đến người xem từ đủ 13 tuổi trở lên'),
('T16', 'Phim được phổ biến đến người xem từ đủ 16 tuổi trở lên'),
('T18', 'Phim được phổ biến đến người xem từ đủ 18 tuổi trở lên'),
('C', 'Phim không được phép phổ biến');

-- 4. Chèn dữ liệu vào bảng PHIM
INSERT INTO PHIM (TenPhim, ThoiLuong, NgayKhoiChieu, MaGioiHan, Poster, MoTa, TrailerURL, MaDaoDien) VALUES 
('Lật Mặt 7: Một Điều Ước', 138, '2024-04-26', 3, 'https://upload.wikimedia.org/wikipedia/vi/a/a2/L%E1%BA%ADt_m%E1%BA%B7t_7_M%E1%BB%99t_%C4%91i%E1%BB%81u_%C6%B0%E1%BB%9Bc_poster.jpg', 'Câu chuyện cảm động về tình mẹ con và những giá trị gia đình sâu sắc của bà Hai và 5 người con.', 'https://www.youtube.com/embed/n42rF5K4mks', 1),
('Mai', 131, '2024-02-10', 5, 'https://upload.wikimedia.org/wikipedia/vi/1/1a/Mai_2024_poster.jpg', 'Mai là một cô gái có quá khứ đầy bi kịch, cô luôn khao khát tình yêu và hạnh phúc nhưng phải đối mặt với nhiều định kiến.', 'https://www.youtube.com/embed/1BscLq2nE2s', 2),
('Nhà Bà Nữ', 102, '2023-01-22', 4, 'https://upload.wikimedia.org/wikipedia/vi/6/6f/Nh%C3%A0_b%C3%A0_N%E1%BB%AF_poster.jpg', 'Câu chuyện xoay quanh gia đình bà Nữ làm nghề bán bánh canh cua, với những mâu thuẫn thế hệ gay gắt.', 'https://www.youtube.com/embed/qRhhLOrsW40', 2),
('Inception', 148, '2010-07-16', 3, 'https://upload.wikimedia.org/wikipedia/vi/1/18/Inception_OST.jpg', 'Một kẻ cắp có khả năng đi vào giấc mơ của người khác để đánh cắp bí mật, giờ đây anh ta phải thực hiện một nhiệm vụ bất khả thi: cấy ghép ý tưởng.', 'https://www.youtube.com/embed/YoHD9XEInc0', 3),
('Oppenheimer', 180, '2023-07-21', 5, 'https://upload.wikimedia.org/wikipedia/vi/6/66/Oppenheimer_poster.jpg', 'Câu chuyện về J. Robert Oppenheimer, cha đẻ của bom nguyên tử, và những hệ lụy lịch sử từ phát minh của ông.', 'https://www.youtube.com/embed/bK6ldnjE3Y0', 3),
('Hai Phượng', 98, '2019-02-22', 5, 'https://upload.wikimedia.org/wikipedia/vi/d/d1/Hai_Ph%C6%B0%E1%BB%A3ng_poster.jpg', 'Hành trình nghẹt thở của một người mẹ đi tìm lại đứa con gái bị bọn bắt cóc lấy đi.', 'https://www.youtube.com/embed/9G05M26-hD4', 4),
('Em Chưa 18', 95, '2017-04-28', 4, 'https://upload.wikimedia.org/wikipedia/vi/1/18/Em_ch%C6%B0a_18_poster.jpg', 'Một tay chơi sành điệu vướng vào rắc rối pháp lý sau khi có tình một đêm với một cô bé chưa đủ 18 tuổi.', 'https://www.youtube.com/embed/aY_G2zYn9F4', 2),
('Tiệc Trăng Máu', 118, '2020-10-23', 4, 'https://upload.wikimedia.org/wikipedia/vi/c/c2/Ti%E1%BB%87c_tr%C4%83ng_m%C3%A1u_poster.jpg', 'Bữa tiệc tân gia của một nhóm bạn thân trở nên căng thẳng khi họ quyết định công khai toàn bộ tin nhắn và cuộc gọi điện thoại.', 'https://www.youtube.com/embed/L1Z6Qf-f5YQ', NULL),
('Bố Già', 128, '2021-03-05', 3, 'https://upload.wikimedia.org/wikipedia/vi/9/91/B%E1%BB%91_gi%C3%A0_2021_poster.jpg', 'Câu chuyện về ông Sang - một người cha bao đồng nhưng rất yêu thương gia đình trong một xóm lao động nghèo.', 'https://www.youtube.com/embed/u1mOibZ_RzE', 2),
('Chị Mười Ba', 96, '2020-12-25', 4, 'https://upload.wikimedia.org/wikipedia/vi/5/5e/Ch%E1%BB%8B_M%C6%B0%E1%BB%9Di_Ba_poster.jpg', 'Chị Mười Ba và anh em An Cư Nghĩa Đoàn phải đối đầu với một băng đảng tội phạm nguy hiểm mới nổi.', 'https://www.youtube.com/embed/oP2rD8BqI-c', NULL);

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
        CHECK (CHAR_LENGTH(Hotline) BETWEEN 9 AND 15),

    FULLTEXT INDEX ft_TenCumRap (TenCumRap)
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
    SoHang INT NOT NULL DEFAULT 10,
    SoCot INT NOT NULL DEFAULT 10,
    SucChua INT NOT NULL,

    CONSTRAINT PK_PhongChieu
        PRIMARY KEY (MaPhong),

    CONSTRAINT FK_PhongChieu_CumRap
        FOREIGN KEY (MaCumRap) 
        REFERENCES CumRap(MaCumRap)
        ON DELETE RESTRICT,   -- Ngăn xóa CumRap khi còn PhongChieu đang hoạt động

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
    Hang VARCHAR(5) NOT NULL,
    Cot INT NOT NULL,

    CONSTRAINT PK_Ghe
        PRIMARY KEY (MaGhe),

    CONSTRAINT FK_Ghe_PhongChieu
        FOREIGN KEY (MaPhong) 
        REFERENCES PhongChieu(MaPhong)
        ON DELETE CASCADE,    -- Xóa PhongChieu -> tự động xóa toàn bộ Ghe bên trong

    CONSTRAINT FK_Ghe_LoaiGhe
        FOREIGN KEY (MaLoaiGhe) 
        REFERENCES LoaiGhe(MaLoaiGhe)
        ON DELETE RESTRICT,   -- Ngăn xóa LoaiGhe khi còn Ghe đang dùng loại đó

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
BEFORE INSERT ON Ghe
FOR EACH ROW
BEGIN
    DECLARE SoGheHienCo INT;
    DECLARE SucChuaPhong INT;

    -- BEFORE INSERT: COUNT(*) chưa bao gồm hàng đang thêm, cộng thêm 1 để kiểm tra
    SELECT COUNT(*) + 1
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
    IN p_SoHang INT,
    IN p_SoCot INT,
    IN p_MaLoaiGheMacDinh INT
)
BEGIN
    DECLARE v_MaPhongMoi INT;
    DECLARE v_Hang INT DEFAULT 1;
    DECLARE v_Cot INT;
    DECLARE v_KyTuHang VARCHAR(2);
    DECLARE v_TenGhe VARCHAR(10);
    DECLARE v_SucChua INT;

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

    -- (Loại phòng được gán tại SuatChieu, không phải PhongChieu, nên không kiểm tra ở đây)

    -- Kiểm tra loại ghế mặc định có tồn tại không
    IF NOT EXISTS (
        SELECT 1 FROM LoaiGhe WHERE MaLoaiGhe = p_MaLoaiGheMacDinh
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Loai ghe mac dinh khong ton tai.';
    END IF;

    -- Tính toán sức chứa
    SET v_SucChua = p_SoHang * p_SoCot;

    START TRANSACTION;

    INSERT INTO PhongChieu(TenPhong, MaCumRap, SoHang, SoCot, SucChua)
    VALUES (p_TenPhong, p_MaCumRap, p_SoHang, p_SoCot, v_SucChua);

    SET v_MaPhongMoi = LAST_INSERT_ID();

    WHILE v_Hang <= p_SoHang DO
        -- Nếu số hàng > 26 (Z), có thể mở rộng logic (AA, AB...), nhưng tạm thời giới hạn ở A-Z hoặc đơn giản là ghép số.
        IF v_Hang <= 26 THEN
            SET v_KyTuHang = CHAR(64 + v_Hang);
        ELSE
            SET v_KyTuHang = CONCAT('A', CHAR(64 + v_Hang - 26));
        END IF;
        
        SET v_Cot = 1;

        WHILE v_Cot <= p_SoCot DO
            SET v_TenGhe = CONCAT(v_KyTuHang, v_Cot);

            INSERT INTO Ghe(TenGhe, MaPhong, MaLoaiGhe, Hang, Cot)
            VALUES (v_TenGhe, v_MaPhongMoi, p_MaLoaiGheMacDinh, v_KyTuHang, v_Cot);

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
    CHECK (GiaCoBan >= 0),
    FULLTEXT INDEX ft_KhungGio (KhungGio)
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
    MaLoaiPhong INT NOT NULL DEFAULT 1,
    GioBatDau DATETIME NOT NULL,
    GioKetThuc DATETIME NOT NULL,

    FOREIGN KEY (MaPhim) REFERENCES Phim(MaPhim),
    FOREIGN KEY (MaPhong) REFERENCES PhongChieu(MaPhong),
    FOREIGN KEY (MaGiaVe) REFERENCES GiaVe_CoBan(MaGiaVe),
    FOREIGN KEY (MaLoaiPhong) REFERENCES LoaiPhong(MaLoaiPhong),

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
    lp.TenLoaiPhong as DinhDang,
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
JOIN LoaiPhong lp
    ON sc.MaLoaiPhong = lp.MaLoaiPhong
JOIN CumRap cr 
    ON pc.MaCumRap = cr.MaCumRap
JOIN GiaVe_CoBan gv 
    ON sc.MaGiaVe = gv.MaGiaVe
WHERE DATE(sc.GioBatDau) = CURDATE();

-- VIEW: Suat chieu chi tiet day du
CREATE VIEW v_SuatChieuChiTiet AS
SELECT
    sc.MaSuatChieu,
    sc.MaPhim,
    p.TenPhim,
    sc.MaPhong,
    pc.TenPhong,
    pc.MaCumRap,
    cr.TenCumRap,
    sc.MaLoaiPhong,
    lp.TenLoaiPhong AS DinhDang,
    sc.GioBatDau,
    sc.GioKetThuc,
    sc.MaGiaVe,
    gv.KhungGio,
    gv.LoaiNgay,
    gv.GiaCoBan,
    fn_TinhGiaVeCuoiCung(sc.MaSuatChieu) AS GiaCuoiCung
FROM SuatChieu sc
JOIN Phim p ON sc.MaPhim = p.MaPhim
JOIN PhongChieu pc ON sc.MaPhong = pc.MaPhong
JOIN CumRap cr ON pc.MaCumRap = cr.MaCumRap
JOIN LoaiPhong lp ON sc.MaLoaiPhong = lp.MaLoaiPhong
JOIN GiaVe_CoBan gv ON sc.MaGiaVe = gv.MaGiaVe;

DELIMITER $$

-- TRIGGER: Chong trung suat chieu khi them
CREATE TRIGGER trg_KiemTraTrungSuatChieu_Insert
BEFORE INSERT ON SuatChieu
FOR EACH ROW
BEGIN
    DECLARE v_ThoiLuong INT;
    
    -- Kiểm tra trùng lịch
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

    -- Kiểm tra thời lượng suất chiếu phải đủ cho thời lượng phim
    SELECT ThoiLuong INTO v_ThoiLuong FROM PHIM WHERE MaPhim = NEW.MaPhim;
    IF TIMESTAMPDIFF(MINUTE, NEW.GioBatDau, NEW.GioKetThuc) < v_ThoiLuong THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Thoi gian suat chieu khong du cho thoi luong cua phim.';
    END IF;
END$$

-- TRIGGER: Chong trung suat chieu khi sua
CREATE TRIGGER trg_KiemTraTrungSuatChieu_Update
BEFORE UPDATE ON SuatChieu
FOR EACH ROW
BEGIN
    DECLARE v_ThoiLuong INT;
    
    -- Kiểm tra trùng lịch
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

    -- Kiểm tra thời lượng suất chiếu phải đủ cho thời lượng phim
    SELECT ThoiLuong INTO v_ThoiLuong FROM PHIM WHERE MaPhim = NEW.MaPhim;
    IF TIMESTAMPDIFF(MINUTE, NEW.GioBatDau, NEW.GioKetThuc) < v_ThoiLuong THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Thoi gian suat chieu khong du cho thoi luong cua phim.';
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
    SoLuongTon INT NOT NULL DEFAULT 0,
    CONSTRAINT CHK_GiaBan CHECK (GiaBan >= 0)
);

CREATE TABLE Voucher (
    MaVoucher INT AUTO_INCREMENT PRIMARY KEY,
    MaCode VARCHAR(20) NOT NULL UNIQUE,
    PhanTramGiam INT NOT NULL CHECK (PhanTramGiam > 0 AND PhanTramGiam <= 100),
    GiamToiDa INT NOT NULL CHECK (GiamToiDa > 0),
    NgayHetHan DATETIME NOT NULL,
    SoLuong INT NOT NULL DEFAULT 0 CHECK (SoLuong >= 0)
);

CREATE TABLE KhachHang (
    MaKH INT AUTO_INCREMENT PRIMARY KEY,
    HoTen VARCHAR(100) NOT NULL,
    SDT VARCHAR(15) NOT NULL UNIQUE,
    Email VARCHAR(100),
    MatKhau VARCHAR(255) NOT NULL DEFAULT '123456',
    DiemTichLuy INT DEFAULT 0,
    MaHang INT NOT NULL,
    CONSTRAINT FK_KhachHang_Hang FOREIGN KEY (MaHang) REFERENCES HangThanhVien(MaHang)
);

CREATE TABLE NhanVien (
    MaNV INT AUTO_INCREMENT PRIMARY KEY,
    TenDangNhap VARCHAR(50) UNIQUE,
    MatKhau VARCHAR(255) NOT NULL DEFAULT '123456',
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

INSERT INTO KhachHang (HoTen, SDT, Email, MatKhau, DiemTichLuy, MaHang) VALUES 
('Nguyễn Văn A', '0901234567', 'nva@gmail.com', '123456', 500, 1),
('Trần Thị B', '0987654321', 'ttb@gmail.com', '123456', 3500, 3);

INSERT INTO NhanVien (TenDangNhap, MatKhau, HoTen, ChucVu, MaCumRap) VALUES 
('nhanvien1', '123456', 'Lê Nhân Viên', 'Bán vé', 1), 
('admin', '123456', 'Phạm Quản Lý', 'Quản lý rạp', 1);

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
    MaDichVu INT,
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
DELIMITER $$

-- ==============================================
-- PHẦN CỦA THÀNH VIÊN 4: KHÁCH HÀNG & F&B
-- ==============================================

-- 1. TRIGGER: Tự động cập nhật hạng khách hàng khi điểm tích lũy thay đổi
CREATE TRIGGER trg_CapNhatHangKhach
BEFORE UPDATE ON KhachHang
FOR EACH ROW
BEGIN
    DECLARE v_MaHang INT;
    
    -- Tìm mã hạng cao nhất mà điểm tích lũy mới đáp ứng được
    SELECT MaHang INTO v_MaHang
    FROM HangThanhVien
    WHERE DiemYeuCau <= NEW.DiemTichLuy
    ORDER BY DiemYeuCau DESC
    LIMIT 1;
    
    IF v_MaHang IS NOT NULL THEN
        SET NEW.MaHang = v_MaHang;
    END IF;
END$$

-- 2. TRIGGER: Trừ số lượng tồn kho bắp nước khi bán (Ngăn xuất âm)
CREATE TRIGGER trg_XuatKhoDichVu
BEFORE INSERT ON CHITIET_DICHVU
FOR EACH ROW
BEGIN
    DECLARE v_TonKho INT;
    
    -- Lấy số lượng tồn hiện tại
    SELECT SoLuongTon INTO v_TonKho
    FROM DichVu
    WHERE MaDichVu = NEW.MaDichVu;
    
    IF v_TonKho < NEW.SoLuong THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Lỗi: Tồn kho bắp nước không đủ để xuất!';
    ELSE
        UPDATE DichVu
        SET SoLuongTon = SoLuongTon - NEW.SoLuong
        WHERE MaDichVu = NEW.MaDichVu;
    END IF;
END$$

-- 3. PROCEDURE: Kiểm tra và áp dụng mã Voucher
CREATE PROCEDURE sp_KiemTraVoucher(
    IN p_MaCode VARCHAR(20),
    IN p_TongTien INT,
    OUT p_SoTienGiam INT,
    OUT p_TrangThai VARCHAR(50)
)
BEGIN
    DECLARE v_PhanTram INT;
    DECLARE v_GiamToiDa INT;
    DECLARE v_NgayHetHan DATETIME;
    DECLARE v_SoLuong INT;
    
    SELECT PhanTramGiam, GiamToiDa, NgayHetHan, SoLuong
    INTO v_PhanTram, v_GiamToiDa, v_NgayHetHan, v_SoLuong
    FROM Voucher
    WHERE MaCode = p_MaCode;
    
    IF v_PhanTram IS NULL THEN
        SET p_TrangThai = 'Mã không tồn tại';
        SET p_SoTienGiam = 0;
    ELSEIF v_NgayHetHan < NOW() THEN
        SET p_TrangThai = 'Mã đã hết hạn';
        SET p_SoTienGiam = 0;
    ELSEIF v_SoLuong <= 0 THEN
        SET p_TrangThai = 'Mã đã hết lượt sử dụng';
        SET p_SoTienGiam = 0;
    ELSE
        -- Tính toán số tiền giảm
        SET p_SoTienGiam = (p_TongTien * v_PhanTram) / 100;
        
        IF p_SoTienGiam > v_GiamToiDa THEN
            SET p_SoTienGiam = v_GiamToiDa;
        END IF;
        
        -- Cập nhật lượt dùng
        UPDATE Voucher
        SET SoLuong = SoLuong - 1
        WHERE MaCode = p_MaCode;
        
        SET p_TrangThai = 'Áp dụng thành công';
    END IF;
END$$

DELIMITER ;
-- Dữ liệu mẫu (Mock Data)
INSERT IGNORE INTO CumRap (TenCumRap, DiaChi, Hotline) VALUES 
('CGV Vincom Center', '72 Le Thanh Ton, Q1', '190015670'),
('Lotte Cinema Cantavil', '1 Song Hanh, Q2', '190015680');

INSERT IGNORE INTO LoaiPhong (TenLoaiPhong, PhuThu) VALUES 
('2D', 0),
('3D', 30000),
('IMAX', 50000);

INSERT IGNORE INTO LoaiGhe (TenLoai, PhuThu) VALUES 
('Thuong', 0),
('VIP', 20000),
('Sweetbox', 50000);

-- Tạo Phòng chiếu và Ghế (Sử dụng Stored Procedure sẽ tự sinh ghế A1, A2...)
CALL sp_TaoPhongVaGhe('P01', 1, 10, 10, 1);
CALL sp_TaoPhongVaGhe('P02', 1, 12, 12, 1);
CALL sp_TaoPhongVaGhe('P01', 2, 8, 10, 1);
CALL sp_TaoPhongVaGhe('P02', 2, 8, 10, 1);

INSERT IGNORE INTO Phim (TenPhim, ThoiLuong, NgayKhoiChieu) VALUES 
('Lat Mat 7: Mot Dieu Uoc', 120, '2024-04-26'),
('Mai', 131, '2024-02-10'),
('Godzilla x Kong', 115, '2024-03-29');

INSERT IGNORE INTO GiaVe_CoBan (KhungGio, LoaiNgay, GiaCoBan) VALUES 
('08:00 - 12:00', 'Thuong', 75000),
('12:00 - 17:00', 'Thuong', 85000),
('17:00 - 23:00', 'Thuong', 100000),
('08:00 - 23:00', 'Cuoi Tuan', 120000);

INSERT INTO SuatChieu (MaPhim, MaPhong, MaGiaVe, MaLoaiPhong, GioBatDau, GioKetThuc) VALUES 
(1, 1, 1, 1, CONCAT(CURDATE(), ' 08:30:00'), CONCAT(CURDATE(), ' 10:30:00')),
(2, 2, 3, 2, CONCAT(CURDATE(), ' 19:00:00'), CONCAT(CURDATE(), ' 21:11:00'));

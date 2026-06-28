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

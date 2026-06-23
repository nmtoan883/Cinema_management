# Hệ Thống Quản Lý Rạp Chiếu Phim (Cinema Management System)

Dự án Hệ thống Quản Lý Rạp Chiếu Phim cung cấp nền tảng quản trị và đặt vé xem phim với hệ thống phân quyền (RBAC) nghiêm ngặt.

## 🔐 1. Thông tin Tài khoản Đăng nhập (Mặc định)

Hệ thống được chia làm 3 phân hệ chính. Mật khẩu mặc định cho tất cả các tài khoản demo dưới đây là: `123456`.

| Vai trò | Tên Đăng Nhập (Username / SĐT) | Quyền hạn mô tả |
| :--- | :--- | :--- |
| **Quản Trị Viên (Admin)** | `admin` | Toàn quyền kiểm soát hệ thống. Quản lý Phim, Rạp, Lịch chiếu, Khách hàng, tạo tài khoản Quản Lý / Nhân viên. |
| **Quản Lý Rạp** | *(Dùng Admin tạo)* | Có quyền quản lý Phòng Chiếu, Lịch Chiếu, Nhân Viên thuộc **Cụm rạp của mình**. Chỉ được xem (không sửa) danh sách Phim. |
| **Nhân Viên Bán Vé** | `nhanvien1` | Chỉ được phép thao tác Bán Vé tại quầy và quản lý Khách Hàng. Bị ẩn các chức năng quản trị nhạy cảm. |
| **Khách Hàng** | `0901234567` | Tài khoản dành cho khách đặt vé trực tuyến. (Đăng nhập bằng Số điện thoại) |

*Lưu ý: Bạn có thể đăng nhập bằng tài khoản `admin` và truy cập menu **Nhân Viên** để tự do tạo thêm các tài khoản Quản Lý hoặc Nhân Viên Bán Vé khác.*

---

## 🗄️ 2. Quy ước Database (Dành cho Team Phát triển)

Để đảm bảo các thành viên trong nhóm không bị "lệch" và code đồng nhất, vui lòng tuân thủ các quy ước CSDL sau:

### Tên Bảng & Cột (Naming Convention)
- **Tên Bảng (Table):** Viết hoa chữ cái đầu mỗi từ (PascalCase) hoặc in hoa toàn bộ, ưu tiên PascalCase trong code Python. (Ví dụ: `Phim`, `CumRap`, `NhanVien`).
- **Khóa Chính (Primary Key):** Đặt tên bắt đầu bằng chữ `Ma` kèm theo tên Bảng. Cấu hình tự động tăng `AUTO_INCREMENT`. (Ví dụ: `MaPhim`, `MaCumRap`, `MaNV`).
- **Khóa Ngoại (Foreign Key):** Sử dụng chung tên với Khóa chính của bảng được tham chiếu.
- **Tiền tố Tham số / Thuộc tính:**
  - Tiền tố `So` cho các biến số lượng (Ví dụ: `SoHang`, `SoCot`).
  - Tiền tố `Ten` cho các tên gọi (Ví dụ: `TenPhim`, `TenGhe`).

### Cấu trúc Xử lý Logic (Stored Procedures & Functions)
- **Hàm (Functions):** Bắt đầu bằng `fn_`. (Ví dụ: `fn_TinhGiaVeCuoiCung`).
- **Thủ tục (Procedures):** Bắt đầu bằng `sp_`. Thường dùng để xử lý các logic phức tạp như INSERT/UPDATE nhiều bảng cùng lúc. (Ví dụ: `sp_TaoPhongVaGhe`).
- **Trigger:** Bắt đầu bằng `trg_`. Dùng để ràng buộc dữ liệu tự động (VD: Không cho phép xếp lịch chiếu trùng giờ).
- **View:** Bắt đầu bằng `v_`. (Ví dụ: `v_LichChieuHomNay`).

### Định dạng & Quy ước các trường thông tin (Data Types & Constraints)
Để tránh bị khai báo sai kiểu dữ liệu dẫn đến lỗi hệ thống, toàn bộ thành viên cần tuân thủ các quy định sau khi tạo cột mới:
- **Số Điện Thoại (SDT/Hotline):** Bắt buộc dùng `VARCHAR(15)`. **TUYỆT ĐỐI KHÔNG** dùng kiểu `INT` vì sẽ làm mất số `0` ở đầu số điện thoại.
- **Trạng thái (Status/Boolean):** Dùng kiểu `TINYINT(1)` với quy ước `0` = Sai/Ngừng hoạt động, `1` = Đúng/Đang hoạt động. Không dùng chữ 'True/False'.
- **Ngày giờ (Date/Time):** Sử dụng `DATETIME` cho các mốc thời gian cụ thể (Ví dụ: `GioBatDau`, `GioKetThuc`). Nếu chỉ lưu ngày (Sinh nhật), dùng kiểu `DATE`.
- **Tiền tệ (Giá vé, Doanh thu):** Sử dụng `INT` (hoặc DECIMAL) thay vì FLOAT để tránh sai số thập phân trong giao dịch tài chính tại Việt Nam. Không lưu đuôi `.00`.
- **Mật khẩu (Password):** Mặc định lưu `VARCHAR(255)` để dự trù cho việc băm mật khẩu (Hash - bcrypt/SHA256) sau này. Không giới hạn quá ngắn.
- **Giới hạn độ tuổi (Phim):** Dùng thống nhất các mã phân loại của Cục Điện Ảnh: `P` (Phổ biến), `K` (Khán giả dưới 13 tuổi xem cùng cha mẹ), `T13` (13+), `T16` (16+), `T18` (18+).

### Luồng Dữ liệu Đặc biệt (Lưu ý quan trọng)
1. **Phân quyền Nhân Viên:** Dựa hoàn toàn vào field `ChucVu` trong bảng `NhanVien`. Hiện tại hỗ trợ 3 chuỗi: `'Admin'`, `'Quản Lý'`, `'Nhân Viên Bán Vé'`. Nếu sai chính tả chữ này, hệ thống sẽ tự động hạ quyền xuống mức thấp nhất.
2. **Sơ đồ ghế (Seat Map):** Thay vì tạo lưới ghế ảo, hệ thống sinh ra các Record vật lý vào bảng `Ghe` (Tên ghế: A1, A2...; Dựa vào tọa độ lưới `SoHang`, `SoCot`). Nếu một phòng chiếu có góc khuyết (thiếu ghế), Admin chỉ cần **xóa** ghế đó trong CSDL, giao diện sẽ tự động hiển thị chỗ trống.

---

## 🚀 3. Hướng dẫn Chạy Dự Án

1. Yêu cầu cài đặt: Python 3.9+ & MySQL (hoặc XAMPP).
2. Tải cơ sở dữ liệu từ file `cinema_management.sql`.
3. Cài đặt thư viện: `pip install flask mysql-connector-python`
4. Khởi chạy ứng dụng:
   ```bash
   python app.py
   ```
5. Mở trình duyệt và truy cập: `http://localhost:5000`

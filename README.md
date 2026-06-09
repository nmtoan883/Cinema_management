# 🎬 HỆ THỐNG QUẢN LÝ RẠP CHIẾU PHIM (Cinema Management System)

Đây là mã nguồn của Đồ án môn học **Hệ Quản Trị Cơ Sở Dữ Liệu**. Dự án mô phỏng quá trình quản lý và vận hành một cụm rạp chiếu phim với các nghiệp vụ thực tế như: Quản lý phim, Phòng chiếu, Lịch chiếu, Khách hàng thành viên và Hệ thống Bán vé giao dịch.

Dự án được xây dựng bằng **Python (Flask)** kết hợp với **MySQL** làm hệ quản trị cơ sở dữ liệu.

---

## 🛠️ Công Nghệ Sử Dụng

- **Backend:** Python 3, Flask (sử dụng cấu trúc Blueprint)
- **Cơ Sở Dữ Liệu:** MySQL (Sử dụng SQL Native, Stored Procedures, Triggers, Views, Transactions)
- **Frontend:** HTML5, Vanilla CSS (Thiết kế Dark Mode / Glassmorphism)
- **Kiểm soát phiên bản:** Git & GitHub

---

## 👥 Phân Công 5 Phân Hệ (Modules)

Dự án được chia thành 5 module độc lập tương ứng với 5 thành viên để tránh xung đột mã nguồn (Conflict):

1. **Phân hệ Phim (`modules/phim.py`):** Quản lý Danh mục phim, Đạo diễn, Diễn viên, Thể loại.
2. **Phân hệ Rạp (`modules/rap.py`):** Quản lý Cụm rạp, Phòng chiếu, tự động sinh Sơ đồ ghế ngồi.
3. **Phân hệ Suất Chiếu (`modules/suat_chieu.py`):** Quản lý Lịch chiếu phim. Điểm nhấn: *Sử dụng Trigger chống trùng lặp giờ chiếu*.
4. **Phân hệ Khách Hàng (`modules/khach_hang.py`):** Quản lý Hồ sơ khách hàng, dịch vụ Bắp Nước (F&B). Điểm nhấn: *Sử dụng Trigger tự động thăng hạng thẻ VIP khi đạt đủ điểm*.
5. **Phân hệ Đặt Vé (`modules/dat_ve.py`):** Xử lý giao dịch bán vé và thống kê doanh thu. Điểm nhấn: *Sử dụng Transaction (Giao tác) chống thất thoát khi thanh toán*.

---

## 🚀 Hướng Dẫn Cài Đặt & Chạy Dự Án

### Bước 1: Chuẩn bị Cơ sở dữ liệu (MySQL)
1. Mở phần mềm quản lý MySQL (ví dụ: **MySQL Workbench**, **XAMPP phpMyAdmin**, hoặc **Navicat**).
2. Mở file `cinema_management.sql` nằm ở thư mục gốc của dự án.
3. Chạy toàn bộ file SQL này (Execute All) để hệ thống tự động tạo Database `CinemaDB`, tạo các Bảng, nạp Dữ liệu mẫu, và khởi tạo các Triggers/Procedures.

### Bước 2: Cấu hình kết nối
Mở file `config.py` và sửa đổi thông tin kết nối cho khớp với MySQL trên máy tính của bạn:
```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',         # Thay bằng user MySQL của bạn
    'password': '',         # Nhập mật khẩu MySQL (Nếu dùng XAMPP thì để trống)
    'database': 'CinemaDB'
}
```

### Bước 3: Cài đặt thư viện Python
Mở Terminal/Command Prompt tại thư mục dự án và chạy:
```bash
pip install -r requirements.txt
```

### Bước 4: Khởi động Server Web
Chạy ứng dụng bằng lệnh:
```bash
python app.py
```
*Server sẽ khởi chạy tại địa chỉ:* `http://localhost:5000`

---

## 📸 Cấu Trúc Thư Mục

```text
Cinema_management/
│
├── app.py                  # File chạy chính của ứng dụng
├── config.py               # Cấu hình kết nối MySQL
├── database.py             # Các hàm tiện ích thực thi SQL
├── cinema_management.sql   # File CSDL tổng (Database Backup)
├── requirements.txt        # Danh sách thư viện cần thiết
│
├── modules/                # Thư mục Backend (Chứa code Python của 5 thành viên)
├── static/                 # Thư mục chứa CSS / Hình ảnh
└── templates/              # Thư mục chứa giao diện HTML
```

---
*Dự án được thực hiện phục vụ cho mục đích học tập.*

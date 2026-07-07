from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import database

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password')
        
        # 1. Kiểm tra Khách Hàng trước (Dùng Số Điện Thoại làm Tên đăng nhập)
        query = "SELECT * FROM KhachHang WHERE SDT = %s AND MatKhau = %s"
        khach_hang_list = database.fetch_all(query, (username, password))
        
        if khach_hang_list:
            khach_hang = khach_hang_list[0]
            session['user_id'] = khach_hang['MaKH']
            session['user_name'] = khach_hang['HoTen']
            session['role'] = 'khach'
            flash('Đăng nhập thành công! Chào mừng Khách Hàng.', 'success')
            return redirect(url_for('dat_ve.index')) # Chuyển hướng tới Đặt Vé
            
        # 2. Nếu không phải Khách Hàng, kiểm tra Nhân Viên
        query_nv = "SELECT * FROM NhanVien WHERE TenDangNhap = %s AND MatKhau = %s"
        nhan_vien_list = database.fetch_all(query_nv, (username, password))
        
        if nhan_vien_list:
            nhan_vien = nhan_vien_list[0]
            session['user_id'] = nhan_vien['MaNV']
            session['user_name'] = nhan_vien['HoTen']
            session['role'] = 'nhanvien'
            session['chuc_vu'] = nhan_vien['ChucVu']
            session['ma_cum_rap'] = nhan_vien['MaCumRap']
            flash(f"Đăng nhập thành công! Chào mừng {nhan_vien['ChucVu']}.", 'success')
            return redirect('/')
            
        flash('Sai tài khoản hoặc mật khẩu!', 'error')

    return render_template('auth/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        ho_ten = request.form.get('ho_ten')
        sdt = request.form.get('sdt')
        email = request.form.get('email')
        mat_khau = request.form.get('mat_khau')
        
        # Kiểm tra SDT đã tồn tại chưa
        check_query = "SELECT * FROM KhachHang WHERE SDT = %s"
        if database.fetch_all(check_query, (sdt,)):
            flash('Số điện thoại này đã được đăng ký!', 'error')
            return redirect(url_for('auth.register'))
            
        # MaHang = 1 là hạng mặc định (Member Đồng)
        insert_query = """
            INSERT INTO KhachHang (HoTen, SDT, Email, MatKhau, MaHang) 
            VALUES (%s, %s, %s, %s, 1)
        """
        if database.execute_query(insert_query, (ho_ten, sdt, email, mat_khau)):
            flash('Đăng ký tài khoản thành công! Vui lòng đăng nhập.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Có lỗi xảy ra khi lưu thông tin đăng ký vào cơ sở dữ liệu.', 'error')
            
    return render_template('auth/register.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Đã đăng xuất thành công!', 'success')
    return redirect(url_for('auth.login'))


@auth_bp.route('/profile')
def profile():
    if not session.get('user_id'):
        return redirect(url_for('auth.login'))
        
    user_id = session.get('user_id')
    role = session.get('role')
    
    if role == 'khach':
        user = database.fetch_all("SELECT k.*, h.TenHang FROM KhachHang k LEFT JOIN HangThanhVien h ON k.MaHang = h.MaHang WHERE k.MaKH = %s", (user_id,))
        history = database.fetch_all("""
            SELECT hd.MaHoaDon, hd.NgayLap, hd.TongTien,
                   p.TenPhim, pc.TenPhong, sc.GioBatDau,
                   GROUP_CONCAT(g.TenGhe SEPARATOR ', ') as DanhSachGhe
            FROM hoadon hd
            JOIN chitiet_ve cv ON hd.MaHoaDon = cv.MaHoaDon
            JOIN suatchieu sc ON cv.MaSuatChieu = sc.MaSuatChieu
            JOIN phim p ON sc.MaPhim = p.MaPhim
            JOIN phongchieu pc ON sc.MaPhong = pc.MaPhong
            JOIN ghe g ON cv.MaGhe = g.MaGhe
            WHERE hd.MaKH = %s
            GROUP BY hd.MaHoaDon, hd.NgayLap, hd.TongTien, p.TenPhim, pc.TenPhong, sc.GioBatDau
            ORDER BY hd.NgayLap DESC
        """, (user_id,))
        return render_template('auth/profile_khach.html', user=user[0] if user else None, history=history)
        
    elif role == 'nhanvien':
        user = database.fetch_all("""
            SELECT nv.*, c.TenCumRap, c.DiaChi
            FROM NhanVien nv 
            LEFT JOIN CumRap c ON nv.MaCumRap = c.MaCumRap 
            WHERE nv.MaNV = %s
        """, (user_id,))
        return render_template('auth/profile_nhanvien.html', user=user[0] if user else None)
    
    return redirect('/')

@auth_bp.route('/doi-mat-khau', methods=['POST'])
def doi_mat_khau():
    if not session.get('user_id') or session.get('role') != 'khach':
        return redirect(url_for('auth.login'))
        
    user_id = session.get('user_id')
    old_password = request.form.get('old_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    if new_password != confirm_password:
        flash('Mật khẩu mới và xác nhận không khớp!', 'error')
        return redirect(url_for('auth.profile'))
        
    user = database.fetch_all("SELECT MatKhau FROM KhachHang WHERE MaKH = %s", (user_id,))
    if not user or user[0]['MatKhau'] != old_password:
        flash('Mật khẩu hiện tại không đúng!', 'error')
        return redirect(url_for('auth.profile'))
        
    try:
        conn = database.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE KhachHang SET MatKhau = %s WHERE MaKH = %s", (new_password, user_id))
        conn.commit()
        cursor.close()
        conn.close()
        flash('Đổi mật khẩu thành công!', 'success')
    except Exception as e:
        flash(f'Đã xảy ra lỗi: {str(e)}', 'error')
        
    return redirect(url_for('auth.profile'))

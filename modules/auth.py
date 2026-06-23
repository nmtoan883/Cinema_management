from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import database

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
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
            return redirect(url_for('dat_ve.chon_phim')) # Chuyển hướng tới Đặt Vé
            
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
            
        try:
            # MaHang = 1 là hạng mặc định (Member Đồng)
            insert_query = """
                INSERT INTO KhachHang (HoTen, SDT, Email, MatKhau, MaHang) 
                VALUES (%s, %s, %s, %s, 1)
            """
            database.execute_query(insert_query, (ho_ten, sdt, email, mat_khau))
            flash('Đăng ký tài khoản thành công! Vui lòng đăng nhập.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            flash(f'Có lỗi xảy ra: {str(e)}', 'error')
            
    return render_template('auth/register.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Đã đăng xuất thành công!', 'success')
    return redirect(url_for('auth.login'))

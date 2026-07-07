from flask import Blueprint, render_template, request, flash, redirect, session, url_for
import database

suat_chieu_bp = Blueprint('suat_chieu', __name__)

@suat_chieu_bp.before_request
def check_auth():
    if not session.get('user_id') or session.get('role') != 'nhanvien':
        return redirect(url_for('auth.login'))
    if session.get('chuc_vu') not in ['Admin', 'Quản Lý']:
        flash('Bạn không có quyền quản lý lịch chiếu', 'error')
        return redirect('/')

@suat_chieu_bp.route('/')
def index():
    # Lấy danh sách lịch chiếu hôm nay từ VIEW (Có thể cần điều chỉnh nếu Quản Lý)
    if session.get('chuc_vu') == 'Admin':
        query_homnay = "SELECT * FROM v_LichChieuHomNay ORDER BY GioBatDau"
        ds_homnay = database.fetch_all(query_homnay)
    else:
        query_homnay = """
            SELECT * 
            FROM v_LichChieuHomNay
            WHERE MaCumRap = %s
            ORDER BY GioBatDau
        """
        ds_homnay = database.fetch_all(query_homnay, (session.get('ma_cum_rap'),))

    
    # Lấy TẤT CẢ suất chiếu để quản lý tổng quan
    if session.get('chuc_vu') == 'Admin':
        query_tat_ca = "SELECT * FROM v_SuatChieuChiTiet ORDER BY GioBatDau DESC"
        ds_tatca = database.fetch_all(query_tat_ca)
        ds_phong = database.fetch_all("SELECT MaPhong, TenPhong, MaCumRap FROM PhongChieu")
    else:
        query_tat_ca = "SELECT * FROM v_SuatChieuChiTiet WHERE MaCumRap = %s ORDER BY GioBatDau DESC"
        ds_tatca = database.fetch_all(query_tat_ca, (session.get('ma_cum_rap'),))
        ds_phong = database.fetch_all("SELECT MaPhong, TenPhong, MaCumRap FROM PhongChieu WHERE MaCumRap = %s", (session.get('ma_cum_rap'),))

    # Lấy dữ liệu cho dropdown trong form thêm mới
    ds_phim = database.fetch_all("SELECT MaPhim, TenPhim, ThoiLuong FROM Phim")
    ds_gia_ve = database.fetch_all("SELECT MaGiaVe, KhungGio, LoaiNgay, GiaCoBan FROM GiaVe_CoBan")
    ds_loai_phong = database.fetch_all("SELECT MaLoaiPhong, TenLoaiPhong, PhuThu FROM LoaiPhong")
    ds_cum_rap = database.fetch_all("SELECT MaCumRap, TenCumRap FROM CumRap")
    
    return render_template('suat_chieu/index.html', title="Quản Lý Lịch Chiếu", 
                           ds_homnay=ds_homnay, ds_tatca=ds_tatca,
                           ds_phim=ds_phim, ds_phong=ds_phong, ds_gia_ve=ds_gia_ve, ds_loai_phong=ds_loai_phong, ds_cum_rap=ds_cum_rap)

@suat_chieu_bp.route('/them', methods=['POST'])
def them_suat_chieu():
    # Nhận dữ liệu từ web form
    ma_phim = request.form.get('ma_phim')
    ma_phong = request.form.get('ma_phong')
    ma_gia_ve = request.form.get('ma_gia_ve')
    ma_loai_phong = request.form.get('ma_loai_phong')
    gio_bat_dau = request.form.get('gio_bat_dau')
    gio_ket_thuc = request.form.get('gio_ket_thuc')
    
    if session.get('chuc_vu') != 'Admin':
        pc = database.fetch_all("SELECT MaCumRap FROM PhongChieu WHERE MaPhong = %s", (ma_phong,))
        if not pc or pc[0]['MaCumRap'] != session.get('ma_cum_rap'):
            flash('Bạn không có quyền xếp lịch cho phòng chiếu của rạp khác', 'error')
            return redirect('/suatchieu')

    query = """
        INSERT INTO SuatChieu (MaPhim, MaPhong, MaGiaVe, MaLoaiPhong, GioBatDau, GioKetThuc) 
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    success = database.execute_query(query, (ma_phim, ma_phong, ma_gia_ve, ma_loai_phong, gio_bat_dau, gio_ket_thuc))
    if success:
        flash("Thêm suất chiếu thành công!", "success")
    else:
        flash("Lỗi: Không thể thêm (có thể trùng lịch do Trigger chặn, hoặc sai dữ liệu)", "error")
        
    return redirect('/suatchieu')
@suat_chieu_bp.route('/them-hang-loat', methods=['POST'])
def them_hang_loat():
    import datetime
    
    ma_phim = request.form.get('ma_phim')
    ma_phong = request.form.get('ma_phong')
    ma_gia_ve = request.form.get('ma_gia_ve')
    ma_loai_phong = request.form.get('ma_loai_phong')
    ngay_chieu = request.form.get('ngay_chieu')
    danh_sach_gio_str = request.form.get('danh_sach_gio')
    
    if session.get('chuc_vu') != 'Admin':
        pc = database.fetch_all("SELECT MaCumRap FROM PhongChieu WHERE MaPhong = %s", (ma_phong,))
        if not pc or pc[0]['MaCumRap'] != session.get('ma_cum_rap'):
            flash('Bạn không có quyền xếp lịch cho phòng chiếu của rạp khác', 'error')
            return redirect('/suatchieu')

    # Lấy thời lượng phim để tính giờ kết thúc
    phim_info = database.fetch_all("SELECT ThoiLuong FROM Phim WHERE MaPhim = %s", (ma_phim,))
    if not phim_info:
        flash("Phim không tồn tại", "error")
        return redirect('/suatchieu')
        
    thoi_luong = int(phim_info[0]['ThoiLuong'])
    
    # Xử lý chuỗi danh sách giờ (ví dụ: "08:00, 10:30, 14:00")
    gio_list = [g.strip() for g in danh_sach_gio_str.split(',') if g.strip()]
    
    if not ngay_chieu or not gio_list:
        flash("Thiếu ngày chiếu hoặc danh sách giờ", "error")
        return redirect('/suatchieu')

    thanh_cong = 0
    that_bai = 0
    
    query = """
        INSERT INTO SuatChieu (MaPhim, MaPhong, MaGiaVe, MaLoaiPhong, GioBatDau, GioKetThuc) 
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    
    for gio in gio_list:
        try:
            # Tạo datetime object cho Giờ Bắt Đầu
            gio_bat_dau_str = f"{ngay_chieu} {gio}:00"
            gio_bat_dau_obj = datetime.datetime.strptime(gio_bat_dau_str, '%Y-%m-%d %H:%M:%S')
            
            # Tính Giờ Kết Thúc
            gio_ket_thuc_obj = gio_bat_dau_obj + datetime.timedelta(minutes=thoi_luong)
            
            # Format lại thành chuỗi
            gio_bat_dau = gio_bat_dau_obj.strftime('%Y-%m-%d %H:%M:%S')
            gio_ket_thuc = gio_ket_thuc_obj.strftime('%Y-%m-%d %H:%M:%S')
            
            success = database.execute_query(query, (ma_phim, ma_phong, ma_gia_ve, ma_loai_phong, gio_bat_dau, gio_ket_thuc))
            if success:
                thanh_cong += 1
            else:
                that_bai += 1
        except Exception as e:
            print(f"Lỗi thêm suất chiếu {gio_bat_dau_str}: {e}")
            that_bai += 1

    if that_bai == 0:
        flash(f"Thêm thành công toàn bộ {thanh_cong} suất chiếu!", "success")
    elif thanh_cong > 0:
        flash(f"Thêm thành công {thanh_cong} suất. Thất bại {that_bai} suất (có thể do trùng lịch hoặc sai định dạng giờ).", "warning")
    else:
        flash(f"Lỗi: Không thể thêm bất kỳ suất chiếu nào (thất bại {that_bai} suất).", "error")

    return redirect('/suatchieu')

@suat_chieu_bp.route('/xoa/<int:id>', methods=['POST'])
def xoa_suat_chieu(id):
    if session.get('chuc_vu') not in ['Admin', 'Quản Lý']:
        flash('Bạn không có quyền xóa suất chiếu', 'error')
        return redirect('/suatchieu')
        
    if session.get('chuc_vu') != 'Admin':
        sc = database.fetch_all("""
            SELECT pc.MaCumRap 
            FROM SuatChieu sc 
            JOIN PhongChieu pc ON sc.MaPhong = pc.MaPhong 
            WHERE sc.MaSuatChieu = %s
        """, (id,))
        if not sc or sc[0]['MaCumRap'] != session.get('ma_cum_rap'):
            flash('Bạn không có quyền xóa suất chiếu của rạp khác', 'error')
            return redirect('/suatchieu')

    query = "DELETE FROM SuatChieu WHERE MaSuatChieu = %s"
    try:
        success = database.execute_query(query, (id,))
        if success:
            flash("Đã xóa suất chiếu thành công!", "success")
        else:
            flash("Lỗi khi xóa suất chiếu (suất chiếu không tồn tại)", "error")
    except Exception as e:
        flash("Không thể xóa suất chiếu này (có thể đã có khách hàng đặt vé)", "error")
        
    return redirect('/suatchieu')

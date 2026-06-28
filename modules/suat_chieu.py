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
        # Lọc Suất chiếu hôm nay theo Cụm Rạp (Lưu ý: v_LichChieuHomNay cần join với PhongChieu)
        query_homnay = """
            SELECT sc.* 
            FROM v_LichChieuHomNay sc
            JOIN PhongChieu pc ON sc.MaPhong = pc.MaPhong
            WHERE pc.MaCumRap = %s
            ORDER BY sc.GioBatDau
        """
        ds_homnay = database.fetch_all(query_homnay, (session.get('ma_cum_rap'),))

    
    # Lấy TẤT CẢ suất chiếu để quản lý tổng quan (Hỗ trợ Full-Text Search)
    q = request.args.get('q', '').strip()
    
    if q:
        # Chuẩn bị truy vấn FTS bằng Boolean Mode (nhập từ nào cũng ghép thêm dấu + và * để tìm kiếm linh hoạt)
        fts_q = " ".join([f"+{w}*" for w in q.split() if w])
        like_q = f"%{q}%"
        
        if session.get('chuc_vu') == 'Admin':
            query_tat_ca = """
                SELECT * FROM v_SuatChieuChiTiet
                WHERE MATCH(TenCumRap) AGAINST (%s IN BOOLEAN MODE)
                   OR MATCH(KhungGio) AGAINST (%s IN BOOLEAN MODE)
                   OR TenCumRap LIKE %s
                   OR KhungGio LIKE %s
                ORDER BY GioBatDau DESC
            """
            ds_tatca = database.fetch_all(query_tat_ca, (fts_q, fts_q, like_q, like_q))
            ds_phong = database.fetch_all("SELECT MaPhong, TenPhong FROM PhongChieu")
        else:
            query_tat_ca = """
                SELECT * FROM v_SuatChieuChiTiet
                WHERE (MATCH(TenCumRap) AGAINST (%s IN BOOLEAN MODE)
                   OR MATCH(KhungGio) AGAINST (%s IN BOOLEAN MODE)
                   OR TenCumRap LIKE %s
                   OR KhungGio LIKE %s)
                  AND MaCumRap = %s
                ORDER BY GioBatDau DESC
            """
            ds_tatca = database.fetch_all(query_tat_ca, (fts_q, fts_q, like_q, like_q, session.get('ma_cum_rap')))
            ds_phong = database.fetch_all("SELECT MaPhong, TenPhong FROM PhongChieu WHERE MaCumRap = %s", (session.get('ma_cum_rap'),))
    else:
        if session.get('chuc_vu') == 'Admin':
            query_tat_ca = "SELECT * FROM v_SuatChieuChiTiet ORDER BY GioBatDau DESC"
            ds_tatca = database.fetch_all(query_tat_ca)
            ds_phong = database.fetch_all("SELECT MaPhong, TenPhong FROM PhongChieu")
        else:
            query_tat_ca = "SELECT * FROM v_SuatChieuChiTiet WHERE MaCumRap = %s ORDER BY GioBatDau DESC"
            ds_tatca = database.fetch_all(query_tat_ca, (session.get('ma_cum_rap'),))
            ds_phong = database.fetch_all("SELECT MaPhong, TenPhong FROM PhongChieu WHERE MaCumRap = %s", (session.get('ma_cum_rap'),))

    # Lấy dữ liệu cho dropdown trong form thêm mới
    ds_phim = database.fetch_all("SELECT MaPhim, TenPhim FROM Phim")
    ds_gia_ve = database.fetch_all("SELECT MaGiaVe, KhungGio, LoaiNgay, GiaCoBan FROM GiaVe_CoBan")
    ds_loai_phong = database.fetch_all("SELECT MaLoaiPhong, TenLoaiPhong, PhuThu FROM LoaiPhong")
    
    return render_template('suat_chieu/index.html', title="Quản Lý Lịch Chiếu", 
                           ds_homnay=ds_homnay, ds_tatca=ds_tatca,
                           ds_phim=ds_phim, ds_phong=ds_phong, ds_gia_ve=ds_gia_ve, ds_loai_phong=ds_loai_phong,
                           q=q)

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

@suat_chieu_bp.route('/xoa/<int:id>', methods=['POST'])
def xoa_suat_chieu(id):
    if session.get('chuc_vu') not in ['Admin', 'Quản Lý']:
        flash('Bạn không có quyền xóa suất chiếu', 'error')
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

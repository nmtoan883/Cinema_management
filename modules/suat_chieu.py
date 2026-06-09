from flask import Blueprint, render_template, request, flash, redirect
import database

suat_chieu_bp = Blueprint('suat_chieu', __name__)

@suat_chieu_bp.route('/')
def index():
    # Lấy danh sách lịch chiếu hôm nay từ VIEW
    query_homnay = "SELECT * FROM v_LichChieuHomNay ORDER BY GioBatDau"
    ds_homnay = database.fetch_all(query_homnay)
    
    # Lấy TẤT CẢ suất chiếu để quản lý tổng quan
    query_tat_ca = """
        SELECT sc.MaSuatChieu, p.TenPhim, pc.TenPhong, sc.GioBatDau, sc.GioKetThuc, 
               gv.KhungGio, gv.LoaiNgay, gv.GiaCoBan,
               fn_TinhGiaVeCuoiCung(sc.MaSuatChieu) AS GiaCuoiCung
        FROM SuatChieu sc
        JOIN Phim p ON sc.MaPhim = p.MaPhim
        JOIN PhongChieu pc ON sc.MaPhong = pc.MaPhong
        JOIN GiaVe_CoBan gv ON sc.MaGiaVe = gv.MaGiaVe
        ORDER BY sc.GioBatDau DESC
    """
    ds_tatca = database.fetch_all(query_tat_ca)

    # Lấy dữ liệu cho dropdown trong form thêm mới
    ds_phim = database.fetch_all("SELECT MaPhim, TenPhim FROM Phim")
    ds_phong = database.fetch_all("SELECT MaPhong, TenPhong FROM PhongChieu")
    ds_gia_ve = database.fetch_all("SELECT MaGiaVe, KhungGio, LoaiNgay, GiaCoBan FROM GiaVe_CoBan")
    
    return render_template('suat_chieu/index.html', title="Quản Lý Lịch Chiếu", 
                           ds_homnay=ds_homnay, ds_tatca=ds_tatca,
                           ds_phim=ds_phim, ds_phong=ds_phong, ds_gia_ve=ds_gia_ve)

@suat_chieu_bp.route('/them', methods=['POST'])
def them_suat_chieu():
    # Nhận dữ liệu từ web form
    ma_phim = request.form.get('ma_phim')
    ma_phong = request.form.get('ma_phong')
    ma_gia_ve = request.form.get('ma_gia_ve')
    gio_bat_dau = request.form.get('gio_bat_dau')
    gio_ket_thuc = request.form.get('gio_ket_thuc')
    
    query = """
        INSERT INTO SuatChieu (MaPhim, MaPhong, MaGiaVe, GioBatDau, GioKetThuc) 
        VALUES (%s, %s, %s, %s, %s)
    """
    success = database.execute_query(query, (ma_phim, ma_phong, ma_gia_ve, gio_bat_dau, gio_ket_thuc))
    if success:
        flash("Thêm suất chiếu thành công!", "success")
    else:
        flash("Lỗi: Không thể thêm (có thể trùng lịch do Trigger chặn, hoặc sai dữ liệu)", "error")
        
    return redirect('/suatchieu')

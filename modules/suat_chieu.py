from flask import Blueprint, render_template, request, flash, redirect
import database

suat_chieu_bp = Blueprint('suat_chieu', __name__)

@suat_chieu_bp.route('/')
def index():
    query = "SELECT * FROM View_DanhSachSuatChieu" # Gọi View đã tạo
    results = database.fetch_all(query)
    
    return render_template('suat_chieu/index.html', title="Lịch Chiếu", ds_lich=results)

@suat_chieu_bp.route('/them', methods=['POST'])
def them_suat_chieu():
    # Nhận dữ liệu từ web form
    ma_phim = request.form.get('ma_phim')
    ma_phong = request.form.get('ma_phong')
    gio_bat_dau = request.form.get('gio_bat_dau')
    gio_ket_thuc = request.form.get('gio_ket_thuc')
    gia_ve = request.form.get('gia_ve')
    
    query = """
        INSERT INTO SuatChieu (MaPhim, MaPhong, GioBatDau, GioKetThuc, GiaVeCoBan) 
        VALUES (%s, %s, %s, %s, %s)
    """
    success = database.execute_query(query, (ma_phim, ma_phong, gio_bat_dau, gio_ket_thuc, gia_ve))
    if success:
        flash("Thêm suất chiếu thành công!", "success")
    else:
        flash("Lỗi: Không thể thêm (có thể trùng lịch do Trigger chặn)", "error")
        
    return redirect('/suatchieu')

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import mysql.connector
from config import DB_CONFIG

gia_ve_bp = Blueprint('gia_ve', __name__)

@gia_ve_bp.before_request
def check_auth():
    if not session.get('user_id') or session.get('role') != 'nhanvien':
        return redirect(url_for('auth.login'))
    if session.get('chuc_vu') not in ['Admin', 'Quản Lý']:
        flash('Bạn không có quyền truy cập cấu hình giá vé', 'error')
        return redirect('/')

@gia_ve_bp.route('/')
def index():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)
    try:
        # Giá vé cơ bản
        cursor.execute("SELECT * FROM GiaVe_CoBan ORDER BY MaGiaVe ASC")
        ds_gia_ve = cursor.fetchall()
        
        # Loại phòng
        cursor.execute("SELECT * FROM LoaiPhong ORDER BY MaLoaiPhong ASC")
        ds_loai_phong = cursor.fetchall()
        
        # Loại ghế
        cursor.execute("SELECT * FROM LoaiGhe ORDER BY MaLoaiGhe ASC")
        ds_loai_ghe = cursor.fetchall()
        
        # Ngày lễ
        cursor.execute("SELECT * FROM NgayLe ORDER BY Ngay DESC")
        ds_ngay_le = cursor.fetchall()
        
        return render_template('gia_ve/index.html', ds_gia_ve=ds_gia_ve, ds_loai_phong=ds_loai_phong, ds_loai_ghe=ds_loai_ghe, ds_ngay_le=ds_ngay_le)
    except Exception as e:
        print("Lỗi lấy cấu hình giá:", e)
        flash("Lỗi lấy dữ liệu cấu hình giá", "error")
        return redirect('/')
    finally:
        cursor.close()
        conn.close()

# ---- GIA VE CO BAN ----
@gia_ve_bp.route('/giave_coban/add', methods=['POST'])
def add_giave():
    khung_gio = request.form.get('khungGio')
    loai_ngay = request.form.get('loaiNgay')
    gia = request.form.get('giaCoBan')
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO GiaVe_CoBan (KhungGio, LoaiNgay, GiaCoBan) VALUES (%s, %s, %s)", (khung_gio, loai_ngay, gia))
        conn.commit()
        flash("Thêm giá vé cơ bản thành công!", "success")
    except Exception as e:
        conn.rollback()
        flash("Lỗi khi thêm giá vé cơ bản", "error")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('gia_ve.index') + '#giave')

@gia_ve_bp.route('/giave_coban/edit/<int:id>', methods=['POST'])
def edit_giave(id):
    khung_gio = request.form.get('khungGio')
    loai_ngay = request.form.get('loaiNgay')
    gia = request.form.get('giaCoBan')
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE GiaVe_CoBan SET KhungGio=%s, LoaiNgay=%s, GiaCoBan=%s WHERE MaGiaVe=%s", (khung_gio, loai_ngay, gia, id))
        conn.commit()
        flash("Cập nhật giá vé cơ bản thành công!", "success")
    except Exception as e:
        conn.rollback()
        flash("Lỗi khi cập nhật giá vé cơ bản", "error")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('gia_ve.index') + '#giave')

@gia_ve_bp.route('/giave_coban/delete/<int:id>', methods=['POST'])
def delete_giave(id):
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM GiaVe_CoBan WHERE MaGiaVe=%s", (id,))
        conn.commit()
        flash("Xóa giá vé cơ bản thành công!", "success")
    except mysql.connector.Error as e:
        conn.rollback()
        # Lỗi khóa ngoại (1451)
        if e.errno == 1451:
            flash("Không thể xóa mức giá này vì đang có Suất Chiếu áp dụng nó!", "error")
        else:
            flash("Lỗi khi xóa giá vé cơ bản", "error")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('gia_ve.index') + '#giave')

# ---- LOAI PHONG ----
@gia_ve_bp.route('/loaiphong/edit/<int:id>', methods=['POST'])
def edit_loaiphong(id):
    phu_thu = request.form.get('phuThu')
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE LoaiPhong SET PhuThu=%s WHERE MaLoaiPhong=%s", (phu_thu, id))
        conn.commit()
        flash("Cập nhật phụ thu phòng thành công!", "success")
    except Exception as e:
        conn.rollback()
        flash("Lỗi cập nhật phụ thu phòng", "error")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('gia_ve.index') + '#loaiphong')

# ---- LOAI GHE ----
@gia_ve_bp.route('/loaighe/edit/<int:id>', methods=['POST'])
def edit_loaighe(id):
    phu_thu = request.form.get('phuThu')
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE LoaiGhe SET PhuThu=%s WHERE MaLoaiGhe=%s", (phu_thu, id))
        conn.commit()
        flash("Cập nhật phụ thu ghế thành công!", "success")
    except Exception as e:
        conn.rollback()
        flash("Lỗi cập nhật phụ thu ghế", "error")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('gia_ve.index') + '#loaighe')

# ---- NGAY LE ----
@gia_ve_bp.route('/ngayle/add', methods=['POST'])
def add_ngayle():
    ten = request.form.get('tenNgayLe')
    ngay = request.form.get('ngay')
    phu_thu = request.form.get('phuThu')
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO NgayLe (TenNgayLe, Ngay, PhuThu) VALUES (%s, %s, %s)", (ten, ngay, phu_thu))
        conn.commit()
        flash("Thêm ngày lễ thành công!", "success")
    except Exception as e:
        conn.rollback()
        flash("Lỗi khi thêm ngày lễ (Có thể ngày này đã tồn tại)", "error")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('gia_ve.index') + '#ngayle')

@gia_ve_bp.route('/ngayle/delete/<int:id>', methods=['POST'])
def delete_ngayle(id):
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM NgayLe WHERE MaNgayLe=%s", (id,))
        conn.commit()
        flash("Xóa ngày lễ thành công!", "success")
    except Exception as e:
        conn.rollback()
        flash("Lỗi khi xóa ngày lễ", "error")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('gia_ve.index') + '#ngayle')

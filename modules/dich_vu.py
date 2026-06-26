from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, session
import mysql.connector
from config import DB_CONFIG

dich_vu_bp = Blueprint('dich_vu', __name__)

@dich_vu_bp.before_request
def check_auth():
    if not session.get('user_id') or session.get('role') != 'nhanvien':
        return redirect(url_for('auth.login'))
    if session.get('chuc_vu') not in ['Admin', 'Quản Lý']:
        flash('Bạn không có quyền truy cập quản lý dịch vụ', 'error')
        return redirect('/')

@dich_vu_bp.route('/')
def index():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM DichVu ORDER BY MaDichVu DESC")
        dich_vu_list = cursor.fetchall()
        return render_template('dich_vu/index.html', dich_vu_list=dich_vu_list, section='dichvu')
    except Exception as e:
        print("Error fetching dich vu:", e)
        flash("Lỗi lấy dữ liệu dịch vụ", "error")
        return redirect(url_for('rap.dashboard'))
    finally:
        cursor.close()
        conn.close()

@dich_vu_bp.route('/add', methods=['POST'])
def add():
    ten = request.form.get('tenDichVu')
    gia = request.form.get('giaBan')
    sl = request.form.get('soLuongTon', 0)
    hinh_anh = request.form.get('hinhAnh', '')
    
    if not ten or not gia:
        flash("Vui lòng nhập đầy đủ Tên và Giá bán", "error")
        return redirect(url_for('dich_vu.index'))
        
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO DichVu (TenDichVu, GiaBan, SoLuongTon, HinhAnh) VALUES (%s, %s, %s, %s)", 
                       (ten, gia, sl, hinh_anh))
        conn.commit()
        flash("Thêm dịch vụ thành công!", "success")
    except Exception as e:
        conn.rollback()
        print("Error adding dich vu:", e)
        flash("Có lỗi xảy ra khi thêm dịch vụ", "error")
    finally:
        cursor.close()
        conn.close()
        
    return redirect(url_for('dich_vu.index'))

@dich_vu_bp.route('/edit/<int:id>', methods=['POST'])
def edit(id):
    ten = request.form.get('tenDichVu')
    gia = request.form.get('giaBan')
    sl = request.form.get('soLuongTon', 0)
    hinh_anh = request.form.get('hinhAnh', '')
    
    if not ten or not gia:
        flash("Vui lòng nhập đầy đủ Tên và Giá bán", "error")
        return redirect(url_for('dich_vu.index'))
        
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE DichVu SET TenDichVu=%s, GiaBan=%s, SoLuongTon=%s, HinhAnh=%s WHERE MaDichVu=%s", 
                       (ten, gia, sl, hinh_anh, id))
        conn.commit()
        flash("Cập nhật dịch vụ thành công!", "success")
    except Exception as e:
        conn.rollback()
        print("Error updating dich vu:", e)
        flash("Có lỗi xảy ra khi cập nhật dịch vụ", "error")
    finally:
        cursor.close()
        conn.close()
        
    return redirect(url_for('dich_vu.index'))

@dich_vu_bp.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    try:
        # Check constraints if needed (CHITIET_DICHVU)
        cursor.execute("SELECT COUNT(*) FROM CHITIET_DICHVU WHERE MaDichVu=%s", (id,))
        if cursor.fetchone()[0] > 0:
            flash("Không thể xóa dịch vụ này vì đã có giao dịch liên quan!", "error")
            return redirect(url_for('dich_vu.index'))
            
        cursor.execute("DELETE FROM DichVu WHERE MaDichVu=%s", (id,))
        conn.commit()
        flash("Xóa dịch vụ thành công!", "success")
    except Exception as e:
        conn.rollback()
        print("Error deleting dich vu:", e)
        flash("Có lỗi xảy ra khi xóa dịch vụ", "error")
    finally:
        cursor.close()
        conn.close()
        
    return redirect(url_for('dich_vu.index'))

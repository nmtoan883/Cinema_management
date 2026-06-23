from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import database

nhan_vien_bp = Blueprint('nhan_vien', __name__)

def check_admin_auth():
    """Kiểm tra quyền truy cập (chỉ Admin và Quản Lý được phép)"""
    if not session.get('user_id') or session.get('role') != 'nhanvien':
        return False
    if session.get('chuc_vu') not in ['Admin', 'Quản Lý']:
        return False
    return True

@nhan_vien_bp.route('/nhanvien')
def index():
    if not check_admin_auth():
        flash('Bạn không có quyền truy cập trang này', 'error')
        return redirect(url_for('auth.login'))

    if session.get('chuc_vu') == 'Admin':
        ds_nhan_vien = database.fetch_all("""
            SELECT nv.MaNV, nv.TenDangNhap, nv.HoTen, nv.ChucVu, cr.TenCumRap, nv.MaCumRap
            FROM NhanVien nv
            JOIN CumRap cr ON nv.MaCumRap = cr.MaCumRap
            ORDER BY nv.MaNV ASC
        """)
        ds_cum_rap = database.fetch_all("SELECT MaCumRap, TenCumRap FROM CumRap")
    else:
        ma_cum_rap = session.get('ma_cum_rap')
        ds_nhan_vien = database.fetch_all("""
            SELECT nv.MaNV, nv.TenDangNhap, nv.HoTen, nv.ChucVu, cr.TenCumRap, nv.MaCumRap
            FROM NhanVien nv
            JOIN CumRap cr ON nv.MaCumRap = cr.MaCumRap
            WHERE nv.MaCumRap = %s
            ORDER BY nv.MaNV ASC
        """, (ma_cum_rap,))
        ds_cum_rap = database.fetch_all("SELECT MaCumRap, TenCumRap FROM CumRap WHERE MaCumRap = %s", (ma_cum_rap,))
    
    return render_template('nhan_vien/index.html', ds_nhan_vien=ds_nhan_vien, ds_cum_rap=ds_cum_rap)

@nhan_vien_bp.route('/nhanvien/them', methods=['POST'])
def them_nhan_vien():
    if not check_admin_auth():
        return redirect(url_for('auth.login'))

    ho_ten = request.form.get('HoTen', '').strip()
    ten_dang_nhap = request.form.get('TenDangNhap', '').strip()
    mat_khau = request.form.get('MatKhau', '').strip()
    
    if session.get('chuc_vu') == 'Admin':
        chuc_vu = request.form.get('ChucVu', '').strip()
        ma_cum_rap = request.form.get('MaCumRap', '').strip()
    else:
        chuc_vu = 'Nhân Viên Bán Vé'
        ma_cum_rap = session.get('ma_cum_rap')

    if not ho_ten or not ten_dang_nhap or not mat_khau or not chuc_vu or not ma_cum_rap:
        flash('Vui lòng nhập đầy đủ thông tin nhân viên', 'error')
        return redirect(url_for('nhan_vien.index'))

    # Kiểm tra trùng tên đăng nhập
    if database.fetch_all("SELECT 1 FROM NhanVien WHERE TenDangNhap = %s", (ten_dang_nhap,)):
        flash('Tên đăng nhập đã tồn tại', 'error')
        return redirect(url_for('nhan_vien.index'))

    success = database.execute_query(
        "INSERT INTO NhanVien (TenDangNhap, MatKhau, HoTen, ChucVu, MaCumRap) VALUES (%s, %s, %s, %s, %s)",
        (ten_dang_nhap, mat_khau, ho_ten, chuc_vu, ma_cum_rap)
    )

    if success:
        flash('Đã thêm nhân viên mới thành công', 'success')
    else:
        flash('Đã xảy ra lỗi khi thêm nhân viên', 'error')

    return redirect(url_for('nhan_vien.index'))

@nhan_vien_bp.route('/nhanvien/sua/<int:ma_nv>', methods=['GET', 'POST'])
def sua_nhan_vien(ma_nv):
    if not check_admin_auth():
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        ho_ten = request.form.get('HoTen', '').strip()
        mat_khau = request.form.get('MatKhau', '').strip()
        
        if session.get('chuc_vu') == 'Admin':
            chuc_vu = request.form.get('ChucVu', '').strip()
            ma_cum_rap = request.form.get('MaCumRap', '').strip()
        else:
            chuc_vu = 'Nhân Viên Bán Vé'
            ma_cum_rap = session.get('ma_cum_rap')

        if not ho_ten or not chuc_vu or not ma_cum_rap:
            flash('Vui lòng nhập đầy đủ họ tên, chức vụ và rạp', 'error')
            return redirect(url_for('nhan_vien.sua_nhan_vien', ma_nv=ma_nv))

        if mat_khau: # Nếu có nhập password mới thì đổi luôn
            success = database.execute_query(
                "UPDATE NhanVien SET HoTen = %s, MatKhau = %s, ChucVu = %s, MaCumRap = %s WHERE MaNV = %s",
                (ho_ten, mat_khau, chuc_vu, ma_cum_rap, ma_nv)
            )
        else:
            success = database.execute_query(
                "UPDATE NhanVien SET HoTen = %s, ChucVu = %s, MaCumRap = %s WHERE MaNV = %s",
                (ho_ten, chuc_vu, ma_cum_rap, ma_nv)
            )

        if success:
            flash('Đã cập nhật thông tin nhân viên', 'success')
            return redirect(url_for('nhan_vien.index'))
        else:
            flash('Lỗi khi cập nhật nhân viên', 'error')

    nv = database.fetch_all("SELECT * FROM NhanVien WHERE MaNV = %s", (ma_nv,))
    if not nv:
        flash('Không tìm thấy nhân viên', 'error')
        return redirect(url_for('nhan_vien.index'))
        
    if session.get('chuc_vu') != 'Admin' and nv[0]['MaCumRap'] != session.get('ma_cum_rap'):
        flash('Bạn không có quyền sửa nhân viên của rạp khác', 'error')
        return redirect(url_for('nhan_vien.index'))

    if session.get('chuc_vu') == 'Admin':
        ds_cum_rap = database.fetch_all("SELECT MaCumRap, TenCumRap FROM CumRap")
    else:
        ds_cum_rap = database.fetch_all("SELECT MaCumRap, TenCumRap FROM CumRap WHERE MaCumRap = %s", (session.get('ma_cum_rap'),))
        
    return render_template('nhan_vien/index.html', ds_nhan_vien=None, ds_cum_rap=ds_cum_rap, nhan_vien_form=nv[0])

@nhan_vien_bp.route('/nhanvien/xoa/<int:ma_nv>', methods=['POST'])
def xoa_nhan_vien(ma_nv):
    if not check_admin_auth():
        return redirect(url_for('auth.login'))

    if session.get('chuc_vu') != 'Admin':
        nv = database.fetch_all("SELECT MaCumRap FROM NhanVien WHERE MaNV = %s", (ma_nv,))
        if not nv or nv[0]['MaCumRap'] != session.get('ma_cum_rap'):
            flash('Bạn không có quyền xóa nhân viên của rạp khác', 'error')
            return redirect(url_for('nhan_vien.index'))

    success = database.execute_query("DELETE FROM NhanVien WHERE MaNV = %s", (ma_nv,))
    if success:
        flash('Đã xóa nhân viên', 'success')
    else:
        flash('Không thể xóa nhân viên (có thể do nhân viên này đã thực hiện các giao dịch đặt vé)', 'error')
        
    return redirect(url_for('nhan_vien.index'))

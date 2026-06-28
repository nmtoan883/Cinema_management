<<<<<<< HEAD
from flask import Blueprint, render_template, request, redirect, url_prefix
=======
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
>>>>>>> c8957c6baf28c93dc293f9670386646fe828d06b
import database

phim_bp = Blueprint(
    'phim',
    __name__,
    url_prefix='/phim'
)

@phim_bp.before_request
def check_auth():
    if not session.get('user_id') or session.get('role') != 'nhanvien':
        return redirect(url_for('auth.login'))
    if session.get('chuc_vu') not in ['Admin', 'Quản Lý']:
        flash('Bạn không có quyền truy cập quản lý phim', 'error')
        return redirect('/')

    # Quản Lý chỉ được xem, không được vào các route thay đổi dữ liệu
    if session.get('chuc_vu') != 'Admin' and request.endpoint != 'phim.index':
        flash('Chỉ Admin mới có quyền thao tác với Phim', 'error')
        return redirect(url_for('phim.index'))

@phim_bp.route('/')
def index():
    """Danh sách phim và thể loại có phân trang"""
    
    page = request.args.get('page', 1, type=int)
    per_page = 5
    offset = (page - 1) * per_page
    
    # Đếm tổng số phim
    count_sql = "SELECT COUNT(*) as total FROM PHIM"
    total_result = database.fetch_all(count_sql)
    total_phim = total_result[0]['total'] if total_result else 0
    total_pages = (total_phim + per_page - 1) // per_page

    sql = """
    SELECT
        MaPhim,
        TenPhim,
        ThoiLuong,
        DATE_FORMAT(NgayKhoiChieu, '%d-%m-%Y') AS NgayKhoiChieu,
        GioiHanDoTuoi,
        CacTheLoai AS TheLoai
    FROM v_DanhSachPhim
    ORDER BY MaPhim DESC
    LIMIT %s OFFSET %s
    """

    ds_phim = database.fetch_all(sql, (per_page, offset))

    return render_template(
        'phim/index.html',
        title='Quản lý Phim',
        ds_phim=ds_phim,
        page=page,
        total_pages=total_pages,
        per_page=per_page
    )


import os
from werkzeug.utils import secure_filename

@phim_bp.route('/them', methods=['GET', 'POST'])
def them_phim():

    if request.method == 'POST':

        ten_phim = request.form['ten_phim']
        thoi_luong = request.form['thoi_luong']
        ngay_khoi_chieu = request.form['ngay_khoi_chieu']
        ma_gioi_han = request.form['ma_gioi_han']
        mo_ta = request.form.get('mo_ta', '')
        trailer = request.form.get('trailer', '')
        ma_the_loai = request.form.get('ma_the_loai')
        ma_dao_dien = request.form.get('ma_dao_dien')
        ma_dien_vien_list = request.form.getlist('ma_dien_vien[]')
        ma_dao_dien = int(ma_dao_dien) if ma_dao_dien else None
        ma_dao_dien = request.form.get('ma_dao_dien')
        ma_dien_vien_list = request.form.getlist('ma_dien_vien[]')
        ma_dao_dien = int(ma_dao_dien) if ma_dao_dien else None
        
        # Xử lý upload ảnh
        poster = ''
        if 'poster_file' in request.files:
            file = request.files['poster_file']
            if file and file.filename != '':
                filename = secure_filename(file.filename)
                upload_folder = os.path.join('static', 'uploads', 'posters')
                os.makedirs(upload_folder, exist_ok=True)
                file_path = os.path.join(upload_folder, filename)
                file.save(file_path)
                poster = f'/static/uploads/posters/{filename}'
                
        # Nếu không upload ảnh thì dùng ảnh mặc định
        if not poster:
            poster = 'https://upload.wikimedia.org/wikipedia/commons/thumb/6/65/No-Image-Placeholder.svg/1665px-No-Image-Placeholder.svg.png'

        sql_phim = """
        INSERT INTO PHIM
        (
            TenPhim,
            ThoiLuong,
            NgayKhoiChieu,
            MaGioiHan,
            Poster,
            MoTa,
            TrailerURL,
            MaDaoDien
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """

        database.execute_query(
            sql_phim,
            (
                ten_phim,
                thoi_luong,
                ngay_khoi_chieu,
                ma_gioi_han,
                poster,
                mo_ta,
                trailer,
                ma_dao_dien
            )
        )
        
        # Lấy ID phim vừa tạo và lưu thể loại
        new_movies = database.fetch_all("SELECT MaPhim FROM PHIM ORDER BY MaPhim DESC LIMIT 1")
        if new_movies and ma_the_loai:
            ma_phim_moi = new_movies[0]['MaPhim']
            database.execute_query(
                "INSERT INTO PHIM_THELOAI (MaPhim, MaTheLoai) VALUES (%s, %s)",
                (ma_phim_moi, ma_the_loai)
            )
        if new_movies and ma_dien_vien_list:
            for dv_id in ma_dien_vien_list:
                database.execute_query(
                    "INSERT INTO PHIM_DIENVIEN (MaPhim, MaDienVien) VALUES (%s, %s)",
                    (ma_phim_moi, dv_id)
                )

        return redirect(url_for('phim.index'))

    ds_the_loai = database.fetch_all(
        "SELECT * FROM THELOAI"
    )
    
    ds_gioi_han = database.fetch_all(
        "SELECT * FROM GIOIHAN_DOTUOI"
    )
    
    ds_dao_dien = database.fetch_all(
        "SELECT * FROM DAODIEN"
    )
    
    ds_dien_vien = database.fetch_all(
        "SELECT * FROM DIENVIEN"
    )

    return render_template(
        'phim/them.html',
        ds_the_loai=ds_the_loai,
        ds_gioi_han=ds_gioi_han,
        ds_dao_dien=ds_dao_dien,
        ds_dien_vien=ds_dien_vien,
        title='Thêm phim'
    )


@phim_bp.route('/theloai')
def danh_muc():

    sql = """
    SELECT *
    FROM THELOAI
    ORDER BY TenTheLoai
    """

    ds_the_loai = database.fetch_all(sql)

    return render_template(
        'phim/theloai.html',
        ds_the_loai=ds_the_loai,
        title='Danh mục phim'
    )


@phim_bp.route('/theloai/them', methods=['GET', 'POST'])
def them_the_loai():

    if request.method == 'POST':

        ten_the_loai = request.form['ten_the_loai']

        sql = """
        INSERT INTO THELOAI(TenTheLoai)
        VALUES(%s)
        """

        database.execute_query(
            sql,
            (ten_the_loai,)
        )

        return redirect('/phim/theloai')

    return render_template(
        'phim/them_theloai.html',
        title='Thêm thể loại'
    )


@phim_bp.route('/xoa/<int:id>', methods=['POST'])
def xoa_phim(id):
    database.execute_query(
        "DELETE FROM PHIM WHERE MaPhim = %s",
        (id,)
    )
    return redirect(url_for('phim.index'))

@phim_bp.route('/gioi-han')
def danh_sach_gioi_han():
    ds_gioi_han = database.fetch_all(
        "SELECT * FROM GIOIHAN_DOTUOI"
    )
    return render_template(
        'phim/gioi_han.html',
        ds_gioi_han=ds_gioi_han,
        title='Quản lý Giới Hạn Độ Tuổi'
    )

@phim_bp.route('/gioi-han/them', methods=['GET', 'POST'])
def them_gioi_han():
    if request.method == 'POST':
        ky_hieu = request.form['ky_hieu']
        mo_ta = request.form['mo_ta']

        database.execute_query(
            "INSERT INTO GIOIHAN_DOTUOI (KyHieu, MoTa) VALUES (%s, %s)",
            (ky_hieu, mo_ta)
        )
        return redirect(url_for('phim.danh_sach_gioi_han'))

    return render_template(
        'phim/them_gioi_han.html',
        title='Thêm Giới Hạn Mới'
    )


@phim_bp.route('/theloai/xoa/<int:ma_the_loai>')
def xoa_the_loai(ma_the_loai):

    database.execute_query(
        "DELETE FROM THELOAI WHERE MaTheLoai=%s",
        (ma_the_loai,)
    )

    return redirect('/phim/theloai')

@phim_bp.route('/sua/<int:id>', methods=['GET', 'POST'])
def sua_phim(id):
    if request.method == 'POST':
        ten_phim = request.form['ten_phim']
        thoi_luong = request.form['thoi_luong']
        ngay_khoi_chieu = request.form['ngay_khoi_chieu']
        ma_gioi_han = request.form['ma_gioi_han']
        mo_ta = request.form.get('mo_ta', '')
        trailer = request.form.get('trailer', '')
        ma_the_loai = request.form.get('ma_the_loai')
        ma_dao_dien = request.form.get('ma_dao_dien')
        ma_dien_vien_list = request.form.getlist('ma_dien_vien[]')
        ma_dao_dien = int(ma_dao_dien) if ma_dao_dien else None
        ma_dao_dien = request.form.get('ma_dao_dien')
        ma_dien_vien_list = request.form.getlist('ma_dien_vien[]')
        ma_dao_dien = int(ma_dao_dien) if ma_dao_dien else None

        # Lấy ảnh cũ
        phim_cu = database.fetch_all("SELECT Poster FROM PHIM WHERE MaPhim = %s", (id,))
        poster = phim_cu[0]['Poster'] if phim_cu else ''

        if 'poster_file' in request.files:
            file = request.files['poster_file']
            if file and file.filename != '':
                from werkzeug.utils import secure_filename
                import os
                filename = secure_filename(file.filename)
                upload_folder = os.path.join('static', 'uploads', 'posters')
                os.makedirs(upload_folder, exist_ok=True)
                file_path = os.path.join(upload_folder, filename)
                file.save(file_path)
                poster = f'/static/uploads/posters/{filename}'

        sql_phim = """
        UPDATE PHIM
        SET TenPhim = %s, ThoiLuong = %s, NgayKhoiChieu = %s, MaGioiHan = %s, Poster = %s, MoTa = %s, TrailerURL = %s, MaDaoDien = %s
        WHERE MaPhim = %s
        """
        database.execute_query(sql_phim, (ten_phim, thoi_luong, ngay_khoi_chieu, ma_gioi_han, poster, mo_ta, trailer, ma_dao_dien, id))

        if ma_the_loai:
            database.execute_query("DELETE FROM PHIM_THELOAI WHERE MaPhim = %s", (id,))
            database.execute_query("INSERT INTO PHIM_THELOAI (MaPhim, MaTheLoai) VALUES (%s, %s)", (id, ma_the_loai))
        
        if ma_dien_vien_list:
            database.execute_query("DELETE FROM PHIM_DIENVIEN WHERE MaPhim = %s", (id,))
            for dv_id in ma_dien_vien_list:
                database.execute_query("INSERT INTO PHIM_DIENVIEN (MaPhim, MaDienVien) VALUES (%s, %s)", (id, dv_id))

        flash('Cập nhật phim thành công', 'success')
        return redirect(url_for('phim.index'))

    phim = database.fetch_all("SELECT * FROM PHIM WHERE MaPhim = %s", (id,))
    if not phim:
        flash('Không tìm thấy phim', 'error')
        return redirect(url_for('phim.index'))
        
    phim = phim[0]
    
    # Lấy thể loại
    the_loai = database.fetch_all("SELECT MaTheLoai FROM PHIM_THELOAI WHERE MaPhim = %s", (id,))
    phim['MaTheLoai'] = the_loai[0]['MaTheLoai'] if the_loai else None

    ds_the_loai = database.fetch_all("SELECT * FROM THELOAI")
    ds_gioi_han = database.fetch_all("SELECT * FROM GIOIHAN_DOTUOI")
    ds_dao_dien = database.fetch_all("SELECT * FROM DAODIEN")
    ds_dien_vien = database.fetch_all("SELECT * FROM DIENVIEN")
    
    # Lay danh sach dien vien cua phim nay
    dv_phim = database.fetch_all("SELECT MaDienVien FROM PHIM_DIENVIEN WHERE MaPhim = %s", (id,))
    phim['DSDienVien'] = [dv['MaDienVien'] for dv in dv_phim] if dv_phim else []

    return render_template(
        'phim/them.html',
        phim=phim,
        ds_the_loai=ds_the_loai,
        ds_gioi_han=ds_gioi_han,
        ds_dao_dien=ds_dao_dien,
        ds_dien_vien=ds_dien_vien,
        title='Sửa phim'
    )


@phim_bp.route('/dao-dien')
def danh_sach_dao_dien():
    if session.get('chuc_vu') != 'Admin':
        flash('Bạn không có quyền', 'error')
        return redirect('/')
    ds_dao_dien = database.fetch_all("SELECT * FROM DAODIEN ORDER BY MaDaoDien DESC")
    return render_template('phim/dao_dien.html', ds_dao_dien=ds_dao_dien, title='Quản lý Đạo Diễn')

@phim_bp.route('/dao-dien/them', methods=['GET', 'POST'])
def them_dao_dien():
    if session.get('chuc_vu') != 'Admin':
        flash('Bạn không có quyền', 'error')
        return redirect('/')
    if request.method == 'POST':
        ho_ten = request.form['ho_ten']
        ngay_sinh = request.form['ngay_sinh']
        database.execute_query(
            "INSERT INTO DAODIEN (HoTen, NgaySinh) VALUES (%s, %s)",
            (ho_ten, ngay_sinh)
        )
        flash('Đã thêm đạo diễn thành công', 'success')
        return redirect(url_for('phim.danh_sach_dao_dien'))
    return render_template('phim/them_dao_dien.html', title='Thêm Đạo Diễn')

@phim_bp.route('/dao-dien/xoa/<int:id>')
def xoa_dao_dien(id):
    if session.get('chuc_vu') != 'Admin':
        flash('Bạn không có quyền', 'error')
        return redirect('/')
    try:
        database.execute_query("DELETE FROM DAODIEN WHERE MaDaoDien = %s", (id,))
        flash('Đã xóa đạo diễn', 'success')
    except:
        flash('Không thể xóa do đạo diễn đang có phim trong hệ thống', 'error')
    return redirect(url_for('phim.danh_sach_dao_dien'))


@phim_bp.route('/dien-vien')
def danh_sach_dien_vien():
    if session.get('chuc_vu') != 'Admin':
        flash('Bạn không có quyền', 'error')
        return redirect('/')
    ds_dien_vien = database.fetch_all("SELECT * FROM DIENVIEN ORDER BY MaDienVien DESC")
    return render_template('phim/dien_vien.html', ds_dien_vien=ds_dien_vien, title='Quản lý Diễn Viên')

@phim_bp.route('/dien-vien/them', methods=['GET', 'POST'])
def them_dien_vien():
    if session.get('chuc_vu') != 'Admin':
        flash('Bạn không có quyền', 'error')
        return redirect('/')
    if request.method == 'POST':
        ho_ten = request.form['ho_ten']
        ngay_sinh = request.form['ngay_sinh']
        database.execute_query(
            "INSERT INTO DIENVIEN (HoTen, NgaySinh) VALUES (%s, %s)",
            (ho_ten, ngay_sinh)
        )
        flash('Đã thêm diễn viên thành công', 'success')
        return redirect(url_for('phim.danh_sach_dien_vien'))
    return render_template('phim/them_dien_vien.html', title='Thêm Diễn Viên')

@phim_bp.route('/dien-vien/xoa/<int:id>')
def xoa_dien_vien(id):
    if session.get('chuc_vu') != 'Admin':
        flash('Bạn không có quyền', 'error')
        return redirect('/')
    try:
        database.execute_query("DELETE FROM DIENVIEN WHERE MaDienVien = %s", (id,))
        flash('Đã xóa diễn viên', 'success')
    except:
        flash('Không thể xóa do diễn viên đang có phim trong hệ thống', 'error')
    return redirect(url_for('phim.danh_sach_dien_vien'))


@phim_bp.route('/dao-dien/sua/<int:id>', methods=['GET', 'POST'])
def sua_dao_dien(id):
    if session.get('chuc_vu') != 'Admin':
        flash('Bạn không có quyền', 'error')
        return redirect('/')
    
    if request.method == 'POST':
        ho_ten = request.form['ho_ten']
        ngay_sinh = request.form['ngay_sinh']
        database.execute_query(
            "UPDATE DAODIEN SET HoTen = %s, NgaySinh = %s WHERE MaDaoDien = %s",
            (ho_ten, ngay_sinh, id)
        )
        flash('Đã cập nhật đạo diễn thành công', 'success')
        return redirect(url_for('phim.danh_sach_dao_dien'))
    
    daodien = database.fetch_all("SELECT * FROM DAODIEN WHERE MaDaoDien = %s", (id,))
    if not daodien:
        flash('Không tìm thấy đạo diễn', 'error')
        return redirect(url_for('phim.danh_sach_dao_dien'))
        
    return render_template('phim/them_dao_dien.html', daodien=daodien[0], title='Sửa Đạo Diễn')

@phim_bp.route('/dien-vien/sua/<int:id>', methods=['GET', 'POST'])
def sua_dien_vien(id):
    if session.get('chuc_vu') != 'Admin':
        flash('Bạn không có quyền', 'error')
        return redirect('/')
    
    if request.method == 'POST':
        ho_ten = request.form['ho_ten']
        ngay_sinh = request.form['ngay_sinh']
        database.execute_query(
            "UPDATE DIENVIEN SET HoTen = %s, NgaySinh = %s WHERE MaDienVien = %s",
            (ho_ten, ngay_sinh, id)
        )
        flash('Đã cập nhật diễn viên thành công', 'success')
        return redirect(url_for('phim.danh_sach_dien_vien'))
    
    dienvien = database.fetch_all("SELECT * FROM DIENVIEN WHERE MaDienVien = %s", (id,))
    if not dienvien:
        flash('Không tìm thấy diễn viên', 'error')
        return redirect(url_for('phim.danh_sach_dien_vien'))
        
    return render_template('phim/them_dien_vien.html', dienvien=dienvien[0], title='Sửa Diễn Viên')

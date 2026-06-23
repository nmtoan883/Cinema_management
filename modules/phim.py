from flask import Blueprint, render_template, request, redirect, url_for, session, flash
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
    """Danh sách phim và thể loại"""

    sql = """
    SELECT
        PHIM.MaPhim,
        PHIM.TenPhim,
        PHIM.ThoiLuong,
        PHIM.NgayKhoiChieu,
        PHIM.GioiHanDoTuoi,
        GROUP_CONCAT(THELOAI.TenTheLoai SEPARATOR ', ') AS TheLoai
    FROM PHIM
    LEFT JOIN PHIM_THELOAI
        ON PHIM.MaPhim = PHIM_THELOAI.MaPhim
    LEFT JOIN THELOAI
        ON THELOAI.MaTheLoai = PHIM_THELOAI.MaTheLoai
    GROUP BY PHIM.MaPhim
    ORDER BY PHIM.MaPhim DESC
    """

    ds_phim = database.fetch_all(sql)

    return render_template(
        'phim/index.html',
        title='Quản lý Phim',
        ds_phim=ds_phim
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
            TrailerURL
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s)
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
                trailer
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

        return redirect(url_for('phim.index'))

    ds_the_loai = database.fetch_all(
        "SELECT * FROM THELOAI"
    )
    
    ds_gioi_han = database.fetch_all(
        "SELECT * FROM GIOIHAN_DOTUOI"
    )

    return render_template(
        'phim/them.html',
        ds_the_loai=ds_the_loai,
        ds_gioi_han=ds_gioi_han,
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

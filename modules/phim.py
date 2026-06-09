from flask import Blueprint, render_template, request, redirect, url_for
import database

phim_bp = Blueprint(
    'phim',
    __name__,
    url_prefix='/phim'
)


@phim_bp.route('/')
def index():
    """Danh sách phim và thể loại"""

    sql = """
    SELECT
        PHIM.MaPhim,
        PHIM.TenPhim,
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


@phim_bp.route('/them', methods=['GET', 'POST'])
def them_phim():

    if request.method == 'POST':

        ten_phim = request.form['ten_phim']

        sql = """
        INSERT INTO PHIM
        (
            TenPhim,
        )
        VALUES (%s,%s,%s,%s)
        """

        database.execute_query(
            sql,
            (
                ten_phim,
            )
        )

        return redirect(url_for('phim.index'))

    ds_the_loai = database.fetch_all(
        "SELECT * FROM THELOAI"
    )

    return render_template(
        'phim/them.html',
        ds_the_loai=ds_the_loai,
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


@phim_bp.route('/xoa/<int:ma_phim>')
def xoa_phim(ma_phim):

    database.execute_query(
        "DELETE FROM PHIM WHERE MaPhim=%s",
        (ma_phim,)
    )

    return redirect('/phim')


@phim_bp.route('/theloai/xoa/<int:ma_the_loai>')
def xoa_the_loai(ma_the_loai):

    database.execute_query(
        "DELETE FROM THELOAI WHERE MaTheLoai=%s",
        (ma_the_loai,)
    )

    return redirect('/phim/theloai')

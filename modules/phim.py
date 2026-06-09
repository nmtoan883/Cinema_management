from flask import Blueprint, render_template, request, redirect, flash
import database

# Đăng ký Blueprint
phim_bp = Blueprint('phim', __name__)

# ==========================
# HIỂN THỊ DANH SÁCH PHIM
# ==========================
@phim_bp.route('/')
def index():
    query = """
        SELECT MaPhim,
               TenPhim,
               ThoiLuong,
               NgayKhoiChieu,
               GioiHanDoTuoi
        FROM PHIM
        ORDER BY TenPhim
    """

    ds_phim = database.fetch_all(query)

    return render_template(
        'phim/index.html',
        title='Quản lý Phim',
        ds_phim=ds_phim
    )


# ==========================
# THÊM PHIM
# ==========================
@phim_bp.route('/them', methods=['GET', 'POST'])
def them_phim():

    if request.method == 'POST':

        ten_phim = request.form.get('ten_phim')
        thoi_luong = request.form.get('thoi_luong')
        ngay_khoi_chieu = request.form.get('ngay_khoi_chieu')
        gioi_han_do_tuoi = request.form.get('gioi_han_do_tuoi')
        ma_dao_dien = request.form.get('ma_dao_dien')

        query = """
            INSERT INTO PHIM
            (
                TenPhim,
                ThoiLuong,
                NgayKhoiChieu,
                GioiHanDoTuoi,
                MaDaoDien
            )
            VALUES
            (
                %s,%s,%s,%s,%s
            )
        """

        try:
            database.execute_query(
                query,
                (
                    ten_phim,
                    thoi_luong,
                    ngay_khoi_chieu,
                    gioi_han_do_tuoi,
                    ma_dao_dien
                )
            )

            flash("Thêm phim thành công!", "success")

            return redirect('/phim')

        except Exception as e:
            flash(str(e), "error")

    return render_template(
        'phim/them.html',
        title='Thêm Phim'
    )


# ==========================
# SỬA PHIM
# ==========================
@phim_bp.route('/sua/<ma_phim>', methods=['GET', 'POST'])
def sua_phim(ma_phim):

    if request.method == 'POST':

        ten_phim = request.form.get('ten_phim')
        thoi_luong = request.form.get('thoi_luong')
        ngay_khoi_chieu = request.form.get('ngay_khoi_chieu')
        gioi_han_do_tuoi = request.form.get('gioi_han_do_tuoi')

        query = """
            UPDATE PHIM
            SET TenPhim = %s,
                ThoiLuong = %s,
                NgayKhoiChieu = %s,
                GioiHanDoTuoi = %s
            WHERE MaPhim = %s
        """

        database.execute_query(
            query,
            (
                ten_phim,
                thoi_luong,
                ngay_khoi_chieu,
                gioi_han_do_tuoi,
                ma_phim
            )
        )

        flash("Cập nhật phim thành công!", "success")

        return redirect('/phim')

    query = """
        SELECT *
        FROM PHIM
        WHERE MaPhim = %s
    """

    phim = database.fetch_one(query, (ma_phim,))

    return render_template(
        'phim/sua.html',
        title='Sửa Phim',
        phim=phim
    )


# ==========================
# XÓA PHIM
# ==========================
@phim_bp.route('/xoa/<ma_phim>')
def xoa_phim(ma_phim):

    try:

        query = """
            DELETE FROM PHIM
            WHERE MaPhim = %s
        """

        database.execute_query(query, (ma_phim,))

        flash("Xóa phim thành công!", "success")

    except Exception as e:
        flash(str(e), "error")

    return redirect('/phim')

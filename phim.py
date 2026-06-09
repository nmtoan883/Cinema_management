from flask import Blueprint, render_template, request, flash, redirect
import database

quan_ly_phim_bp = Blueprint('quan_ly_phim', __name__)


@quan_ly_phim_bp.route('/')
def index():
    ds_phim = hien_thi_phim()
    return render_template(
        'quan_ly_phim/index.html',
        title="Quản Lý Phim & Danh Mục Phim",
        ds_phim=ds_phim
    )


@quan_ly_phim_bp.route('/them-phim', methods=['POST'])
def them_phim():
    ten_phim = request.form.get('ten_phim')
    thoi_luong = request.form.get('thoi_luong')
    ngay_khoi_chieu = request.form.get('ngay_khoi_chieu')
    gioi_han_do_tuoi = request.form.get('gioi_han_do_tuoi')
    ma_dao_dien = request.form.get('ma_dao_dien')

    ds_the_loai = request.form.getlist('ma_the_loai')
    ds_dien_vien = request.form.getlist('ma_dien_vien')

    success, message = them_phim_moi(
        ten_phim,
        thoi_luong,
        ngay_khoi_chieu,
        gioi_han_do_tuoi,
        ma_dao_dien,
        ds_the_loai,
        ds_dien_vien
    )

    if success:
        flash("Thêm phim thành công!", "success")
    else:
        flash(f"Lỗi: {message}", "error")

    return redirect('/quanlyphim')


def hien_thi_phim():
    query = "SELECT * FROM v_DanhSachPhim"
    return database.fetch_all(query)


def hien_thi_the_loai():
    query = """
        SELECT MaTheLoai, TenTheLoai
        FROM THELOAI
        ORDER BY TenTheLoai
    """
    return database.fetch_all(query)


def hien_thi_dao_dien():
    query = """
        SELECT MaDaoDien, HoTen
        FROM DAODIEN
        ORDER BY HoTen
    """
    return database.fetch_all(query)


def hien_thi_dien_vien():
    query = """
        SELECT MaDienVien, HoTen
        FROM DIENVIEN
        ORDER BY HoTen
    """
    return database.fetch_all(query)


def them_phim_moi(
        ten_phim,
        thoi_luong,
        ngay_khoi_chieu,
        gioi_han_do_tuoi,
        ma_dao_dien,
        ds_the_loai,
        ds_dien_vien):
    """
    Gọi Stored Procedure sp_ThemPhimMoi()
    """

    if not ten_phim or not thoi_luong:
        return False, "Thiếu tên phim hoặc thời lượng"

    conn = database.get_connection()

    if not conn:
        return False, "Không thể kết nối CSDL"

    cursor = conn.cursor()

    try:
        ds_the_loai_str = ",".join(ds_the_loai)
        ds_dien_vien_str = ",".join(ds_dien_vien)

        cursor.execute(
            """
            CALL sp_ThemPhimMoi(
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
            """,
            (
                ten_phim,
                int(thoi_luong),
                ngay_khoi_chieu,
                gioi_han_do_tuoi,
                ma_dao_dien if ma_dao_dien else None,
                ds_the_loai_str,
                ds_dien_vien_str
            )
        )

        conn.commit()

        return True, "Thêm phim thành công"

    except Exception as err:
        conn.rollback()
        return False, str(err)

    finally:
        cursor.close()
        conn.close()
        
def dem_so_phim_cua_dien_vien(ma_dien_vien):
    query = """
        SELECT f_DemSoPhimCuaDienVien(%s) AS TongSoPhim
    """

    result = database.fetch_one(query, (ma_dien_vien,))

    if result:
        return result["TongSoPhim"]

    return 0

def xoa_phim(ma_phim):
    conn = database.get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "DELETE FROM PHIM WHERE MaPhim = %s",
            (ma_phim,)
        )

        conn.commit()
        return True, "Xóa thành công"

    except Exception as err:
        conn.rollback()
        return False, str(err)

    finally:
        cursor.close()
        conn.close()
        
def cap_nhat_phim(
        ma_phim,
        ten_phim,
        thoi_luong,
        ngay_khoi_chieu,
        gioi_han_do_tuoi,
        ma_dao_dien):

    conn = database.get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            UPDATE PHIM
            SET TenPhim = %s,
                ThoiLuong = %s,
                NgayKhoiChieu = %s,
                GioiHanDoTuoi = %s,
                MaDaoDien = %s
            WHERE MaPhim = %s
            """,
            (
                ten_phim,
                thoi_luong,
                ngay_khoi_chieu,
                gioi_han_do_tuoi,
                ma_dao_dien,
                ma_phim
            )
        )

        conn.commit()
        return True, "Cập nhật thành công"

    except Exception as err:
        conn.rollback()
        return False, str(err)

    finally:
        cursor.close()
        conn.close()
from flask import Blueprint, render_template, request, flash, redirect
import database
import datetime
import random

dat_ve_bp = Blueprint('dat_ve', __name__)


@dat_ve_bp.route('/')
def index():
    ds_phim = hien_thi_phim()
    return render_template('dat_ve/index.html', title="Đặt Vé & Giao Dịch", ds_phim=ds_phim)


@dat_ve_bp.route('/ban-ve', methods=['POST'])
def ban_ve():
    ma_kh = request.form.get('ma_kh')
    ma_nv = request.form.get('ma_nv') or ''
    ma_suat = request.form.get('ma_suat')
    ma_ghe = request.form.get('ma_ghe')
    ma_dich_vu = request.form.getlist('ma_dich_vu')

    ma_hoa_don = request.form.get('ma_hoa_don') or tao_ma_hoa_don()
    ma_ve = request.form.get('ma_ve') or tao_ma_ve()

    success, message = dat_ve(ma_hoa_don, ma_kh, ma_nv, ma_ve, ma_suat, ma_ghe, ma_dich_vu)
    if success:
        flash(f"Bán vé thành công! Mã hóa đơn: {ma_hoa_don}", "success")
    else:
        flash(f"Lỗi bán vé: {message}", "error")
    return redirect('/datve')


def hien_thi_phim():
    query = "SELECT MaPhim, TenPhim, ThoiLuong, NgayKhoiChieu, GioiHanDoTuoi FROM PHIM"
    return database.fetch_all(query)


def hien_thi_suat_chieu(ma_phim):
    query = """
        SELECT MaSuatChieu, MaPhong, MaGiaVe, GioBatDau, GioKetThuc
        FROM SuatChieu
        WHERE MaPhim = %s
    """
    return database.fetch_all(query, (ma_phim,))


def hien_thi_ghe_trong(ma_suat_chieu):
    query = """
        SELECT g.MaGhe, g.TenGhe
        FROM Ghe g
        WHERE g.MaPhong = (
            SELECT MaPhong FROM SuatChieu WHERE MaSuatChieu = %s
        )
        AND g.MaGhe NOT IN (
            SELECT MaGhe FROM CHITIET_VE WHERE MaSuatChieu = %s
        )
    """
    return database.fetch_all(query, (ma_suat_chieu, ma_suat_chieu))


def tao_ma_hoa_don():
    return f"HD{datetime.datetime.now().strftime('%y%m%d%H%M%S')}{random.randint(10, 99)}"


def tao_ma_ve():
    return f"VE{datetime.datetime.now().strftime('%y%m%d%H%M%S')}{random.randint(10, 99)}"


def dat_ve(ma_hoa_don, ma_kh, ma_nv, ma_ve, ma_suat_chieu, ma_ghe, ma_dich_vu=None):
    """Bán vé theo transaction và gọi sp_BanVe()."""
    if not ma_kh or not ma_suat_chieu or not ma_ghe:
        return False, "Thiếu thông tin khách hàng hoặc suất/ghế"

    conn = database.get_connection()
    if not conn:
        return False, "Không thể kết nối tới CSDL"

    cursor = conn.cursor(dictionary=True)
    try:
        conn.start_transaction()

        cursor.execute(
            "SELECT COUNT(*) AS so_luong FROM CHITIET_VE WHERE MaSuatChieu = %s AND MaGhe = %s FOR UPDATE",
            (ma_suat_chieu, ma_ghe)
        )
        if cursor.fetchone().get('so_luong', 0) > 0:
            raise ValueError("Ghế đã được bán cho suất chiếu này")

        cursor.execute(
            "SELECT fn_TinhGiaVeCuoiCung(%s) AS GiaMua",
            (ma_suat_chieu,)
        )
        gia = cursor.fetchone()
        if not gia or gia.get('GiaMua') is None:
            raise ValueError("Không xác định được giá vé cho suất chiếu")

        gia_mua = float(gia['GiaMua'])
        tong_tien = gia_mua

        cursor.execute(
            "CALL sp_BanVe(%s, %s, %s, %s, %s, %s, %s)",
            (ma_hoa_don, ma_kh, ma_nv, ma_ve, ma_suat_chieu, ma_ghe, gia_mua)
        )

        if ma_dich_vu:
            for dich_vu_id in ma_dich_vu:
                cursor.execute(
                    "SELECT GiaBan FROM DichVu WHERE MaDichVu = %s",
                    (dich_vu_id,)
                )
                dv = cursor.fetchone()
                if not dv:
                    raise ValueError(f"Dịch vụ không hợp lệ: {dich_vu_id}")

                gia_dv = float(dv['GiaBan'])
                tong_tien += gia_dv
                cursor.execute(
                    "INSERT INTO CHITIET_DICHVU (MaHoaDon, MaDichVu, SoLuong, ThanhTien) VALUES (%s, %s, %s, %s)",
                    (ma_hoa_don, dich_vu_id, 1, gia_dv)
                )

        cursor.execute(
            "UPDATE HOADON SET TongTien = %s WHERE MaHoaDon = %s",
            (tong_tien, ma_hoa_don)
        )

        diem_tich_luy = int(tong_tien // 10000)
        if diem_tich_luy > 0:
            cursor.execute(
                "UPDATE KhachHang SET DiemTichLuy = DiemTichLuy + %s WHERE MaKH = %s",
                (diem_tich_luy, ma_kh)
            )

        conn.commit()
        return True, ma_hoa_don
    except Exception as err:
        conn.rollback()
        return False, str(err)
    finally:
        cursor.close()
        conn.close()

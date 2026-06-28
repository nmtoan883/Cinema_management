from flask import Blueprint, render_template, request, flash, redirect, jsonify, session
import database
import datetime
import random

dat_ve_bp = Blueprint('dat_ve', __name__)


@dat_ve_bp.route('/')
def index():
    # Lấy ma_phim từ query parameter nếu có
    phim_id = request.args.get('phim_id', '')
    ds_phim = hien_thi_phim()
    return render_template('dat_ve/index.html', title="Đặt Vé & Giao Dịch", ds_phim=ds_phim, selected_phim_id=phim_id)

@dat_ve_bp.route('/api/suatchieu/<int:ma_phim>')
def api_suat_chieu(ma_phim):
    query = """
        SELECT sc.MaSuatChieu, sc.GioBatDau, sc.GioKetThuc, lp.TenLoaiPhong
        FROM SuatChieu sc
        JOIN PhongChieu pc ON sc.MaPhong = pc.MaPhong
        JOIN LoaiPhong lp ON pc.MaLoaiPhong = lp.MaLoaiPhong
        WHERE sc.MaPhim = %s
        ORDER BY sc.GioBatDau ASC
    """
    suat_chieu = database.fetch_all(query, (ma_phim,))
    # Format datetime objects for JSON serialization
    for sc in suat_chieu:
        if isinstance(sc['GioBatDau'], datetime.datetime):
            sc['GioBatDau'] = sc['GioBatDau'].strftime('%Y-%m-%d %H:%M')
        if isinstance(sc['GioKetThuc'], datetime.datetime):
            sc['GioKetThuc'] = sc['GioKetThuc'].strftime('%H:%M')
    return jsonify(suat_chieu)

@dat_ve_bp.route('/api/ghe/<int:ma_suat_chieu>')
def api_ghe(ma_suat_chieu):
    # Lấy thông tin cột của phòng chiếu
    room_query = """
        SELECT pc.SoCot
        FROM SuatChieu sc
        JOIN PhongChieu pc ON sc.MaPhong = pc.MaPhong
        WHERE sc.MaSuatChieu = %s
    """
    room_info = database.fetch_all(room_query, (ma_suat_chieu,))
    so_cot = room_info[0]['SoCot'] if room_info else 10

    # Lấy toàn bộ ghế của phòng chiếu, kèm trạng thái đã bán (MaVe IS NOT NULL)
    query = """
        SELECT g.MaGhe, g.TenGhe, lg.TenLoai, 
               (CASE WHEN cv.MaVe IS NOT NULL THEN 1 ELSE 0 END) AS DaBan
        FROM Ghe g
        JOIN SuatChieu sc ON g.MaPhong = sc.MaPhong
        JOIN LoaiGhe lg ON g.MaLoaiGhe = lg.MaLoaiGhe
        LEFT JOIN CHITIET_VE cv ON cv.MaSuatChieu = sc.MaSuatChieu AND cv.MaGhe = g.MaGhe
        WHERE sc.MaSuatChieu = %s
        ORDER BY g.TenGhe ASC
    """
    ghe = database.fetch_all(query, (ma_suat_chieu,))
    return jsonify({'ghe': ghe, 'so_cot': so_cot})


@dat_ve_bp.route('/ban-ve', methods=['POST'])
def ban_ve():
    # Tự động điền MaKhachHang nếu role là Khách
    if session.get('role') == 'khach':
        ma_kh = session.get('user_id')
        ma_nv = ''
    else:
        # Nếu role là nhân viên, có thể lấy SDT Khách Hàng từ form và tự lookup MaKH
        ma_kh_form = request.form.get('ma_kh')
        kh_query = database.fetch_all("SELECT MaKH FROM KhachHang WHERE SDT = %s", (ma_kh_form,))
        ma_kh = kh_query[0]['MaKH'] if kh_query else None
        ma_nv = session.get('user_id') if session.get('role') == 'nhanvien' else ''

    ma_suat = request.form.get('ma_suat')
    ma_ghe = request.form.get('ma_ghe')
    ma_dich_vu = request.form.getlist('ma_dich_vu')

    if not ma_kh:
         flash("Không tìm thấy Khách Hàng (Sai số điện thoại hoặc chưa đăng nhập).", "error")
         return redirect('/datve')

    ma_hoa_don = tao_ma_hoa_don()
    ma_ve = tao_ma_ve()

    success, message = dat_ve(ma_hoa_don, ma_kh, ma_nv, ma_ve, ma_suat, ma_ghe, ma_dich_vu)
    if success:
        flash(f"Thanh toán thành công! Mã giao dịch: {ma_hoa_don}", "success")
    else:
        flash(f"Lỗi giao dịch: {message}", "error")
    return redirect('/')

def hien_thi_phim():
    query = "SELECT MaPhim, TenPhim, ThoiLuong, NgayKhoiChieu, GioiHanDoTuoi FROM PHIM"
    return database.fetch_all(query)


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

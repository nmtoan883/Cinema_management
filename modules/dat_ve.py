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
        SELECT sc.MaSuatChieu, sc.GioBatDau, sc.GioKetThuc, lp.TenLoaiPhong, cr.MaCumRap, cr.TenCumRap
        FROM SuatChieu sc
        JOIN PhongChieu pc ON sc.MaPhong = pc.MaPhong
        JOIN CumRap cr ON pc.MaCumRap = cr.MaCumRap
        JOIN LoaiPhong lp ON pc.MaLoaiPhong = lp.MaLoaiPhong
        WHERE sc.MaPhim = %s AND sc.GioBatDau > NOW()
        ORDER BY cr.TenCumRap ASC, sc.GioBatDau ASC
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

    # Lấy toàn bộ ghế của phòng chiếu, kèm trạng thái đã bán (MaVe IS NOT NULL) và Giá
    query = """
        SELECT g.MaGhe, g.TenGhe, lg.TenLoai, 
               (CASE WHEN cv.MaVe IS NOT NULL THEN 1 ELSE 0 END) AS DaBan,
               (fn_TinhGiaVeCuoiCung(%s) + lg.PhuThu) AS Gia
        FROM Ghe g
        JOIN SuatChieu sc ON g.MaPhong = sc.MaPhong
        JOIN LoaiGhe lg ON g.MaLoaiGhe = lg.MaLoaiGhe
        LEFT JOIN CHITIET_VE cv ON cv.MaSuatChieu = sc.MaSuatChieu AND cv.MaGhe = g.MaGhe
        WHERE sc.MaSuatChieu = %s
        ORDER BY g.TenGhe ASC
    """
    ghe = database.fetch_all(query, (ma_suat_chieu, ma_suat_chieu))
    return jsonify({'ghe': ghe, 'so_cot': so_cot})


@dat_ve_bp.route('/api/dichvu')
def api_dich_vu():
    dich_vu = database.fetch_all("SELECT MaDichVu, TenDichVu, GiaBan FROM DichVu ORDER BY MaDichVu ASC")
    return jsonify(dich_vu)


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
    
    dich_vu_list = []
    for key, value in request.form.items():
        if key.startswith('dv_') and value.isdigit() and int(value) > 0:
            dv_id = key.split('_')[1]
            dich_vu_list.append({'id': dv_id, 'so_luong': int(value)})

    if not ma_kh:
         flash("Không tìm thấy Khách Hàng (Sai số điện thoại hoặc chưa đăng nhập).", "error")
         return redirect('/datve')

    ma_hoa_don = tao_ma_hoa_don()
    ma_ve = tao_ma_ve()

    success, message = dat_ve(ma_hoa_don, ma_kh, ma_nv, ma_ve, ma_suat, ma_ghe, dich_vu_list)
    if success:
        flash(f"Thanh toán thành công! Mã giao dịch: {ma_hoa_don}", "success")
    else:
        flash(f"Lỗi giao dịch: {message}", "error")
    return redirect('/')

def hien_thi_phim():
    query = """
        SELECT MaPhim, TenPhim, ThoiLuong, NgayKhoiChieu, GioiHanDoTuoi 
        FROM v_DanhSachPhim p
        WHERE EXISTS (
            SELECT 1 FROM SuatChieu sc 
            WHERE sc.MaPhim = p.MaPhim AND sc.GioBatDau > NOW()
        )
        ORDER BY NgayKhoiChieu DESC
    """
    return database.fetch_all(query)


def tao_ma_hoa_don():
    return f"HD{datetime.datetime.now().strftime('%y%m%d%H%M%S')}{random.randint(10, 99)}"


def tao_ma_ve():
    return f"VE{datetime.datetime.now().strftime('%y%m%d%H%M%S')}{random.randint(10, 99)}"


def dat_ve(ma_hoa_don, ma_kh, ma_nv, ma_ve, ma_suat_chieu, ma_ghe, dich_vu_list=None):
    """Bán vé theo transaction và gọi sp_BanVe()."""
    if not ma_kh or not ma_suat_chieu or not ma_ghe:
        return False, "Thiếu thông tin khách hàng hoặc suất/ghế"

    conn = database.get_connection()
    if not conn:
        return False, "Hệ thống đang bận, không thể kết nối. Vui lòng thử lại sau."

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
            """
            SELECT fn_TinhGiaVeCuoiCung(%s) + lg.PhuThu AS GiaMua
            FROM Ghe g
            JOIN LoaiGhe lg ON g.MaLoaiGhe = lg.MaLoaiGhe
            WHERE g.MaGhe = %s
            """,
            (ma_suat_chieu, ma_ghe)
        )
        gia = cursor.fetchone()
        if not gia or gia.get('GiaMua') is None:
            raise ValueError("Không xác định được giá vé cho suất chiếu")

        gia_mua = float(gia['GiaMua'])
        tong_tien = gia_mua

        cursor.execute(
            "INSERT INTO HOADON (MaHoaDon, MaKH, MaNV, NgayLap, TongTien) VALUES (%s, %s, %s, NOW(), 0)",
            (ma_hoa_don, ma_kh, ma_nv)
        )
        cursor.execute(
            "INSERT INTO CHITIET_VE (MaVe, MaHoaDon, MaSuatChieu, MaGhe, GiaMua) VALUES (%s, %s, %s, %s, %s)",
            (ma_ve, ma_hoa_don, ma_suat_chieu, ma_ghe, gia_mua)
        )

        if dich_vu_list:
            for dv_item in dich_vu_list:
                dich_vu_id = dv_item['id']
                so_luong = dv_item['so_luong']
                cursor.execute(
                    "SELECT GiaBan FROM DichVu WHERE MaDichVu = %s",
                    (dich_vu_id,)
                )
                dv = cursor.fetchone()
                if not dv:
                    raise ValueError(f"Dịch vụ không hợp lệ: {dich_vu_id}")

                gia_dv = float(dv['GiaBan'])
                thanh_tien = gia_dv * so_luong
                tong_tien += thanh_tien
                cursor.execute(
                    "INSERT INTO CHITIET_DICHVU (MaHoaDon, MaDichVu, SoLuong, ThanhTien) VALUES (%s, %s, %s, %s)",
                    (ma_hoa_don, dich_vu_id, so_luong, thanh_tien)
                )

        cursor.execute(
            "UPDATE HOADON SET TongTien = %s WHERE MaHoaDon = %s",
            (tong_tien, ma_hoa_don)
        )

        cursor.execute(
            "SELECT fn_TinhDiemTichLuy(%s) AS diem_tich_luy",
            (tong_tien,)
        )
        diem_result = cursor.fetchone()
        diem_tich_luy = int(diem_result['diem_tich_luy']) if diem_result and diem_result.get('diem_tich_luy') is not None else 0
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

@dat_ve_bp.route('/ve/<ma_hoa_don>')
def xem_ve(ma_hoa_don):
    if not session.get('user_id'):
        return redirect(url_for('auth.login'))
        
    query = """
        SELECT hd.MaHoaDon, hd.NgayLap, hd.TongTien,
               cv.MaVe,
               p.TenPhim, p.ThoiLuong, p.Poster,
               sc.GioBatDau,
               cr.TenCumRap, cr.DiaChi,
               pc.TenPhong,
               GROUP_CONCAT(g.TenGhe SEPARATOR ', ') as DanhSachGhe
        FROM hoadon hd
        JOIN chitiet_ve cv ON hd.MaHoaDon = cv.MaHoaDon
        JOIN suatchieu sc ON cv.MaSuatChieu = sc.MaSuatChieu
        JOIN phongchieu pc ON sc.MaPhong = pc.MaPhong
        JOIN cumrap cr ON pc.MaCumRap = cr.MaCumRap
        JOIN phim p ON sc.MaPhim = p.MaPhim
        JOIN ghe g ON cv.MaGhe = g.MaGhe
        WHERE hd.MaHoaDon = %s AND hd.MaKH = %s
        GROUP BY hd.MaHoaDon, hd.NgayLap, hd.TongTien, cv.MaVe, p.TenPhim, p.ThoiLuong, p.Poster, sc.GioBatDau, cr.TenCumRap, cr.DiaChi, pc.TenPhong
    """
    ve = database.fetch_all(query, (ma_hoa_don, session.get('user_id')))
    
    if not ve:
        flash('Không tìm thấy vé hoặc bạn không có quyền xem vé này.', 'error')
        return redirect(url_for('auth.profile'))
        
    return render_template('dat_ve/ve.html', ve=ve[0])

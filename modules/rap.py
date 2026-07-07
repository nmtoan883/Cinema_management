from decimal import Decimal, InvalidOperation

from flask import Blueprint, flash, redirect, render_template, request, url_for, session

import database

rap_bp = Blueprint('rap', __name__)

@rap_bp.before_request
def check_auth():
    if not session.get('user_id') or session.get('role') != 'nhanvien':
        return redirect(url_for('auth.login'))
    if session.get('chuc_vu') not in ['Admin', 'Quản Lý']:
        flash('Bạn không có quyền truy cập quản lý rạp', 'error')
        return redirect('/')


def _cum_rap_da_ton_tai(ten_cum_rap, dia_chi, ma_cum_rap=None):
    query = """
        SELECT MaCumRap
        FROM CumRap
        WHERE TenCumRap = %s AND DiaChi = %s
    """
    params = [ten_cum_rap, dia_chi]

    if ma_cum_rap is not None:
        query += " AND MaCumRap <> %s"
        params.append(ma_cum_rap)

    return bool(database.fetch_all(query, tuple(params)))


def _du_lieu_cum_rap_hop_le(ten_cum_rap, dia_chi, hotline, ma_cum_rap=None):
    if not ten_cum_rap or not dia_chi or not hotline:
        return 'Vui long nhap day du ten cum rap, dia chi va hotline.'

    if not hotline.isdigit():
        return 'Hotline chi duoc chua chu so.'

    if len(hotline) < 9 or len(hotline) > 15:
        return 'Hotline phai co do dai tu 9 den 15 chu so.'

    if _cum_rap_da_ton_tai(ten_cum_rap, dia_chi, ma_cum_rap):
        return 'Cum rap voi ten va dia chi nay da ton tai.'

    return None


def _loai_phong_da_ton_tai(ten_loai_phong, ma_loai_phong=None):
    query = """
        SELECT MaLoaiPhong
        FROM LoaiPhong
        WHERE TenLoaiPhong = %s
    """
    params = [ten_loai_phong]

    if ma_loai_phong is not None:
        query += " AND MaLoaiPhong <> %s"
        params.append(ma_loai_phong)

    return bool(database.fetch_all(query, tuple(params)))


def _du_lieu_loai_phong_hop_le(ten_loai_phong, ma_loai_phong=None):
    if not ten_loai_phong:
        return 'Vui long nhap day du ten loai phong.'
    
    if _kiem_tra_trung_lap('LoaiPhong', 'TenLoaiPhong', ten_loai_phong, 'MaLoaiPhong', ma_loai_phong):
        return 'Ten loai phong nay da ton tai.'
    return None


def _du_lieu_loai_ghe_hop_le(ten_loai_ghe, ma_loai_ghe=None):
    if not ten_loai_ghe:
        return 'Vui long nhap day du ten loai ghe.'
    
    if _kiem_tra_trung_lap('LoaiGhe', 'TenLoai', ten_loai_ghe, 'MaLoaiGhe', ma_loai_ghe):
        return 'Ten loai ghe nay da ton tai.'
    return None


def _cum_rap_hop_le(ma_cum_rap):
    return bool(database.fetch_all("SELECT MaCumRap FROM CumRap WHERE MaCumRap = %s", (ma_cum_rap,)))


def _loai_phong_hop_le(ma_loai_phong):
    return bool(database.fetch_all("SELECT MaLoaiPhong FROM LoaiPhong WHERE MaLoaiPhong = %s", (ma_loai_phong,)))


def _phong_chieu_da_ton_tai(ten_phong, ma_cum_rap, ma_phong=None):
    query = "SELECT MaPhong FROM PhongChieu WHERE TenPhong = %s AND MaCumRap = %s"
    params = [ten_phong, ma_cum_rap]
    if ma_phong:
        query += " AND MaPhong != %s"
        params.append(ma_phong)
    return bool(database.fetch_all(query, tuple(params)))


def _du_lieu_phong_chieu_hop_le(ten_phong, ma_cum_rap, so_hang, so_cot, ma_phong=None):
    if not ten_phong or not ma_cum_rap or not so_hang or not so_cot:
        return None, None, None, 'Vui long nhap day du ten phong, cum rap, so hang va so cot.'

    try:
        ma_cum_rap_value = int(ma_cum_rap)
        so_hang_value = int(so_hang)
        so_cot_value = int(so_cot)
    except ValueError:
        return None, None, None, 'Cum rap, so hang va so cot phai la gia tri hop le.'

    if so_hang_value <= 0 or so_cot_value <= 0:
        return None, None, None, 'So hang va so cot phai lon hon 0.'

    if not _cum_rap_hop_le(ma_cum_rap_value):
        return None, None, None, 'Cum rap khong ton tai.'

    if _phong_chieu_da_ton_tai(ten_phong, ma_cum_rap_value, ma_phong):
        return None, None, None, 'Ten phong da ton tai trong cum rap nay.'

    return ma_cum_rap_value, so_hang_value, so_cot_value, None


def _du_lieu_tao_phong_va_ghe_hop_le(ten_phong, ma_cum_rap, so_hang, so_cot, ma_loai_ghe_mac_dinh):
    ma_cum_rap_value, so_hang_value, so_cot_value, loi = _du_lieu_phong_chieu_hop_le(
        ten_phong, ma_cum_rap, so_hang, so_cot
    )
    if loi:
        return None, None, None, None, loi

    if not ma_loai_ghe_mac_dinh:
        return None, None, None, None, 'Vui long chon loai ghe mac dinh.'

    try:
        ma_loai_ghe_value = int(ma_loai_ghe_mac_dinh)
    except ValueError:
        return None, None, None, None, 'Loai ghe mac dinh phai la gia tri hop le.'

    if ma_loai_ghe_value != 0 and not _loai_ghe_hop_le(ma_loai_ghe_value):
        return None, None, None, None, 'Loai ghe mac dinh khong ton tai.'

    return ma_cum_rap_value, so_hang_value, so_cot_value, ma_loai_ghe_value, None


def _phong_hop_le(ma_phong):
    return bool(database.fetch_all("SELECT MaPhong FROM PhongChieu WHERE MaPhong = %s", (ma_phong,)))


def _loai_ghe_hop_le(ma_loai_ghe):
    return bool(database.fetch_all("SELECT MaLoaiGhe FROM LoaiGhe WHERE MaLoaiGhe = %s", (ma_loai_ghe,)))


def _ghe_da_ton_tai(ten_ghe, ma_phong, ma_ghe=None):
    query = """
        SELECT MaGhe
        FROM Ghe
        WHERE TenGhe = %s AND MaPhong = %s
    """
    params = [ten_ghe, ma_phong]

    if ma_ghe is not None:
        query += " AND MaGhe <> %s"
        params.append(ma_ghe)

    return bool(database.fetch_all(query, tuple(params)))


def _vuot_suc_chua_phong(ma_phong, ma_ghe=None):
    ds_phong = database.fetch_all(
        """
        SELECT SucChua
        FROM PhongChieu
        WHERE MaPhong = %s
        """,
        (ma_phong,),
    )
    if not ds_phong:
        return True

    so_ghe_hien_co = database.fetch_all(
        """
        SELECT COUNT(*) AS TongSoGhe
        FROM Ghe
        WHERE MaPhong = %s
        """
        if ma_ghe is None else
        """
        SELECT COUNT(*) AS TongSoGhe
        FROM Ghe
        WHERE MaPhong = %s AND MaGhe <> %s
        """,
        (ma_phong,) if ma_ghe is None else (ma_phong, ma_ghe),
    )
    tong_so_ghe = so_ghe_hien_co[0]['TongSoGhe'] if so_ghe_hien_co else 0
    return tong_so_ghe + 1 > ds_phong[0]['SucChua']


def _du_lieu_ghe_hop_le(ten_ghe, ma_phong, ma_loai_ghe, ma_ghe=None):
    if not ten_ghe or not ma_phong or not ma_loai_ghe:
        return None, None, 'Vui long nhap day du ten ghe, phong chieu va loai ghe.'

    try:
        ma_phong_value = int(ma_phong)
        ma_loai_ghe_value = int(ma_loai_ghe)
    except ValueError:
        return None, None, 'Phong chieu va loai ghe phai la gia tri hop le.'

    if not _phong_hop_le(ma_phong_value):
        return None, None, 'Phong chieu khong ton tai.'

    if not _loai_ghe_hop_le(ma_loai_ghe_value):
        return None, None, 'Loai ghe khong ton tai.'

    if _ghe_da_ton_tai(ten_ghe, ma_phong_value, ma_ghe):
        return None, None, 'Ten ghe da ton tai trong phong chieu nay.'

    if _vuot_suc_chua_phong(ma_phong_value, ma_ghe):
        return None, None, 'So luong ghe vuot qua suc chua da khai bao cua phong chieu.'

    return ma_phong_value, ma_loai_ghe_value, None


def _tao_context_quan_ly(active_section='cumrap', cum_rap_form_data=None, cum_rap_editing_id=None,
                         loai_phong_form_data=None, loai_phong_editing_id=None,
                         loai_ghe_form_data=None, loai_ghe_editing_id=None,
                         phong_chieu_form_data=None, phong_chieu_editing_id=None,
                         ghe_form_data=None, ghe_editing_id=None):
    if session.get('chuc_vu') == 'Admin':
        ds_cum_rap = database.fetch_all(
            """
            SELECT MaCumRap, TenCumRap, DiaChi, Hotline
            FROM CumRap
            ORDER BY MaCumRap ASC
            """
        )
    else:
        ds_cum_rap = database.fetch_all(
            """
            SELECT MaCumRap, TenCumRap, DiaChi, Hotline
            FROM CumRap
            WHERE MaCumRap = %s
            ORDER BY MaCumRap ASC
            """, (session.get('ma_cum_rap'),)
        )
    ds_loai_phong = database.fetch_all(
        """
        SELECT MaLoaiPhong, TenLoaiPhong, PhuThu
        FROM LoaiPhong
        ORDER BY MaLoaiPhong ASC
        """
    )
    ds_loai_ghe = database.fetch_all(
        """
        SELECT MaLoaiGhe, TenLoai, PhuThu
        FROM LoaiGhe
        ORDER BY MaLoaiGhe ASC
        """
    )
    
    if session.get('chuc_vu') == 'Admin':
        ds_phong_chieu = database.fetch_all(
            """
            SELECT
                pc.MaPhong,
                pc.TenPhong,
                pc.MaCumRap,
                pc.SoHang,
                pc.SoCot,
                pc.SucChua,
                cr.TenCumRap
            FROM PhongChieu pc
            JOIN CumRap cr ON pc.MaCumRap = cr.MaCumRap
            ORDER BY pc.MaPhong ASC
            """
        )
    else:
        ds_phong_chieu = database.fetch_all(
            """
            SELECT
                pc.MaPhong,
                pc.TenPhong,
                pc.MaCumRap,
                pc.SoHang,
                pc.SoCot,
                pc.SucChua,
                cr.TenCumRap
            FROM PhongChieu pc
            JOIN CumRap cr ON pc.MaCumRap = cr.MaCumRap
            WHERE pc.MaCumRap = %s
            ORDER BY pc.MaPhong ASC
            """, (session.get('ma_cum_rap'),)
        )

    from flask import request
    import math

    page = request.args.get('page', 1, type=int)
    per_page = 20
    offset = (page - 1) * per_page

    loc_cum_rap = request.args.get('loc_cum_rap', '')
    loc_phong = request.args.get('loc_phong', '')
    
    where_clauses = ["1=1"]
    params_count = []
    
    if session.get('chuc_vu') != 'Admin':
        where_clauses.append("pc.MaCumRap = %s")
        params_count.append(session.get('ma_cum_rap'))
    else:
        if loc_cum_rap:
            where_clauses.append("pc.MaCumRap = %s")
            params_count.append(loc_cum_rap)
            
    if loc_phong:
        where_clauses.append("g.MaPhong = %s")
        params_count.append(loc_phong)
        
    where_str = " AND ".join(where_clauses)
    
    query_count = f"SELECT COUNT(*) AS c FROM Ghe g JOIN PhongChieu pc ON g.MaPhong = pc.MaPhong WHERE {where_str}"
    total_ghe = database.fetch_all(query_count, tuple(params_count))[0]['c']
    total_pages = math.ceil(total_ghe / per_page) if total_ghe > 0 else 1

    params_data = params_count.copy()
    params_data.extend([per_page, offset])

    query_data = f"""
        SELECT
            g.MaGhe,
            g.TenGhe,
            g.MaPhong,
            g.MaLoaiGhe,
            pc.TenPhong,
            cr.TenCumRap,
            lg.TenLoai
        FROM Ghe g
        JOIN PhongChieu pc ON g.MaPhong = pc.MaPhong
        JOIN CumRap cr ON pc.MaCumRap = cr.MaCumRap
        JOIN LoaiGhe lg ON g.MaLoaiGhe = lg.MaLoaiGhe
        WHERE {where_str}
        ORDER BY g.MaGhe ASC
        LIMIT %s OFFSET %s
    """
    ds_ghe = database.fetch_all(query_data, tuple(params_data))
    if session.get('chuc_vu') == 'Admin':
        ds_thong_ke_cum_rap = database.fetch_all(
            """
            SELECT
                MaCumRap,
                TenCumRap,
                DiaChi,
                Hotline,
                TongSoPhong,
                TongSucChua
            FROM v_ThongKePhongTheoCumRap
            ORDER BY MaCumRap ASC
            """
        )
    else:
        ds_thong_ke_cum_rap = database.fetch_all(
            """
            SELECT
                MaCumRap,
                TenCumRap,
                DiaChi,
                Hotline,
                TongSoPhong,
                TongSucChua
            FROM v_ThongKePhongTheoCumRap
            WHERE MaCumRap = %s
            ORDER BY MaCumRap ASC
            """, (session.get('ma_cum_rap'),)
        )
    return {
        'title': 'Quan Ly Rap',
        'active_section': active_section,
        'ds_cum_rap': ds_cum_rap,
        'cum_rap_form_data': cum_rap_form_data or {},
        'cum_rap_editing_id': cum_rap_editing_id,
        'ds_loai_phong': ds_loai_phong,
        'loai_phong_form_data': loai_phong_form_data or {},
        'loai_phong_editing_id': loai_phong_editing_id,
        'ds_loai_ghe': ds_loai_ghe,
        'loai_ghe_form_data': loai_ghe_form_data or {},
        'loai_ghe_editing_id': loai_ghe_editing_id,
        'ds_phong_chieu': ds_phong_chieu,
        'phong_chieu_form_data': phong_chieu_form_data or {},
        'phong_chieu_editing_id': phong_chieu_editing_id,
        'ds_ghe': ds_ghe,
        'ghe_form_data': ghe_form_data or {},
        'ghe_editing_id': ghe_editing_id,
        'loc_cum_rap': loc_cum_rap,
        'loc_phong': loc_phong,
        'ghe_page': page,
        'ghe_total_pages': total_pages,
        'ds_thong_ke_cum_rap': ds_thong_ke_cum_rap,
    }


@rap_bp.route('/')
def index():
    active_section = request.args.get('section', 'cumrap')
    if active_section not in ('cumrap', 'loaiphong', 'loaighe', 'phongchieu', 'ghe', 'thongke'):
        active_section = 'cumrap'
    return render_template('rap/index.html', **_tao_context_quan_ly(active_section=active_section))


@rap_bp.route('/them', methods=['POST'])
def them_cum_rap():
    if session.get('chuc_vu') != 'Admin':
        flash('Chỉ Admin mới có quyền thêm Cụm rạp', 'error')
        return redirect(url_for('rap.index', section='cumrap'))
        
    ten_cum_rap = request.form.get('TenCumRap', '').strip()
    dia_chi = request.form.get('DiaChi', '').strip()
    hotline = request.form.get('Hotline', '').strip()

    loi = _du_lieu_cum_rap_hop_le(ten_cum_rap, dia_chi, hotline)
    if loi:
        flash(loi, 'error')
        return redirect(url_for('rap.index', section='cumrap'))

    success = database.execute_query(
        """
        INSERT INTO CumRap (TenCumRap, DiaChi, Hotline)
        VALUES (%s, %s, %s)
        """,
        (ten_cum_rap, dia_chi, hotline),
    )

    if success:
        flash('Da them cum rap moi.', 'success')
    else:
        flash('Không thể thêm cụm rạp. Vui lòng kiểm tra lại dữ liệu.', 'error')

    return redirect(url_for('rap.index', section='cumrap'))


@rap_bp.route('/sua/<int:ma_cum_rap>', methods=['GET', 'POST'])
def sua_cum_rap(ma_cum_rap):
    if session.get('chuc_vu') != 'Admin':
        flash('Chỉ Admin mới có quyền sửa Cụm rạp', 'error')
        return redirect(url_for('rap.index', section='cumrap'))

    if request.method == 'POST':
        ten_cum_rap = request.form.get('TenCumRap', '').strip()
        dia_chi = request.form.get('DiaChi', '').strip()
        hotline = request.form.get('Hotline', '').strip()

        loi = _du_lieu_cum_rap_hop_le(ten_cum_rap, dia_chi, hotline, ma_cum_rap)
        if loi:
            flash(loi, 'error')
            return redirect(url_for('rap.sua_cum_rap', ma_cum_rap=ma_cum_rap))

        success = database.execute_query(
            """
            UPDATE CumRap
            SET TenCumRap = %s, DiaChi = %s, Hotline = %s
            WHERE MaCumRap = %s
            """,
            (ten_cum_rap, dia_chi, hotline, ma_cum_rap),
        )

        if success:
            flash('Da cap nhat cum rap.', 'success')
            return redirect(url_for('rap.index', section='cumrap'))

        flash('Khong the cap nhat cum rap.', 'error')

    cum_rap = database.fetch_all(
        """
        SELECT MaCumRap, TenCumRap, DiaChi, Hotline
        FROM CumRap
        WHERE MaCumRap = %s
        """,
        (ma_cum_rap,),
    )

    if not cum_rap:
        flash('Khong tim thay cum rap can sua.', 'error')
        return redirect(url_for('rap.index', section='cumrap'))

    return render_template(
        'rap/index.html',
        **_tao_context_quan_ly(
            active_section='cumrap',
            cum_rap_form_data=cum_rap[0],
            cum_rap_editing_id=ma_cum_rap,
        ),
    )


@rap_bp.route('/xoa/<int:ma_cum_rap>', methods=['POST'])
def xoa_cum_rap(ma_cum_rap):
    if session.get('chuc_vu') != 'Admin':
        flash('Chỉ Admin mới có quyền xóa Cụm rạp', 'error')
        return redirect(url_for('rap.index', section='cumrap'))

    success = database.execute_query(
        "DELETE FROM CumRap WHERE MaCumRap = %s",
        (ma_cum_rap,),
    )

    if success:
        flash('Da xoa cum rap.', 'success')
    else:
        flash('Khong the xoa cum rap. Cum rap co the dang duoc lien ket voi phong chieu.', 'error')

    return redirect(url_for('rap.index', section='cumrap'))


@rap_bp.route('/loaiphong/them', methods=['POST'])
def them_loai_phong():
    ten_loai_phong = request.form.get('TenLoaiPhong', '').strip()

    loi = _du_lieu_loai_phong_hop_le(ten_loai_phong)
    if loi:
        flash(loi, 'error')
        return redirect(url_for('rap.index', section='loaiphong'))

    success = database.execute_query(
        """
        INSERT INTO LoaiPhong (TenLoaiPhong, PhuThu)
        VALUES (%s, 0)
        """,
        (ten_loai_phong,),
    )

    if success:
        flash('Da them loai phong moi.', 'success')
    else:
        flash('Khong the them loai phong.', 'error')

    return redirect(url_for('rap.index', section='loaiphong'))


@rap_bp.route('/loaiphong/sua/<int:ma_loai_phong>', methods=['GET', 'POST'])
def sua_loai_phong(ma_loai_phong):
    if request.method == 'POST':
        ten_loai_phong = request.form.get('TenLoaiPhong', '').strip()

        loi = _du_lieu_loai_phong_hop_le(ten_loai_phong, ma_loai_phong)
        if loi:
            flash(loi, 'error')
            return redirect(url_for('rap.sua_loai_phong', ma_loai_phong=ma_loai_phong))

        success = database.execute_query(
            """
            UPDATE LoaiPhong
            SET TenLoaiPhong = %s
            WHERE MaLoaiPhong = %s
            """,
            (ten_loai_phong, ma_loai_phong),
        )

        if success:
            flash('Da cap nhat loai phong.', 'success')
            return redirect(url_for('rap.index', section='loaiphong'))

        flash('Khong the cap nhat loai phong.', 'error')

    loai_phong = database.fetch_all(
        """
        SELECT MaLoaiPhong, TenLoaiPhong, PhuThu
        FROM LoaiPhong
        WHERE MaLoaiPhong = %s
        """,
        (ma_loai_phong,),
    )

    if not loai_phong:
        flash('Khong tim thay loai phong can sua.', 'error')
        return redirect(url_for('rap.index', section='loaiphong'))

    return render_template(
        'rap/index.html',
        **_tao_context_quan_ly(
            active_section='loaiphong',
            loai_phong_form_data=loai_phong[0],
            loai_phong_editing_id=ma_loai_phong,
        ),
    )


@rap_bp.route('/loaiphong/xoa/<int:ma_loai_phong>', methods=['POST'])
def xoa_loai_phong(ma_loai_phong):
    success = database.execute_query(
        "DELETE FROM LoaiPhong WHERE MaLoaiPhong = %s",
        (ma_loai_phong,),
    )

    if success:
        flash('Da xoa loai phong.', 'success')
    else:
        flash('Khong the xoa loai phong. Loai phong co the dang duoc su dung.', 'error')

    return redirect(url_for('rap.index', section='loaiphong'))


@rap_bp.route('/loaighe/them', methods=['POST'])
def them_loai_ghe():
    ten_loai_ghe = request.form.get('TenLoai', '').strip()

    loi = _du_lieu_loai_ghe_hop_le(ten_loai_ghe)
    if loi:
        flash(loi, 'error')
        return redirect(url_for('rap.index', section='loaighe'))

    success = database.execute_query(
        """
        INSERT INTO LoaiGhe (TenLoai, PhuThu)
        VALUES (%s, 0)
        """,
        (ten_loai_ghe,),
    )

    if success:
        flash('Da them loai ghe moi.', 'success')
    else:
        flash('Khong the them loai ghe.', 'error')

    return redirect(url_for('rap.index', section='loaighe'))


@rap_bp.route('/loaighe/sua/<int:ma_loai_ghe>', methods=['GET', 'POST'])
def sua_loai_ghe(ma_loai_ghe):
    if request.method == 'POST':
        ten_loai_ghe = request.form.get('TenLoai', '').strip()

        loi = _du_lieu_loai_ghe_hop_le(ten_loai_ghe, ma_loai_ghe)
        if loi:
            flash(loi, 'error')
            return redirect(url_for('rap.sua_loai_ghe', ma_loai_ghe=ma_loai_ghe))

        success = database.execute_query(
            """
            UPDATE LoaiGhe
            SET TenLoai = %s
            WHERE MaLoaiGhe = %s
            """,
            (ten_loai_ghe, ma_loai_ghe),
        )

        if success:
            flash('Da cap nhat loai ghe.', 'success')
            return redirect(url_for('rap.index', section='loaighe'))

        flash('Khong the cap nhat loai ghe.', 'error')

    loai_ghe = database.fetch_all(
        """
        SELECT MaLoaiGhe, TenLoai, PhuThu
        FROM LoaiGhe
        WHERE MaLoaiGhe = %s
        """,
        (ma_loai_ghe,),
    )

    if not loai_ghe:
        flash('Khong tim thay loai ghe can sua.', 'error')
        return redirect(url_for('rap.index', section='loaighe'))

    return render_template(
        'rap/index.html',
        **_tao_context_quan_ly(
            active_section='loaighe',
            loai_ghe_form_data=loai_ghe[0],
            loai_ghe_editing_id=ma_loai_ghe,
        ),
    )


@rap_bp.route('/loaighe/xoa/<int:ma_loai_ghe>', methods=['POST'])
def xoa_loai_ghe(ma_loai_ghe):
    success = database.execute_query(
        "DELETE FROM LoaiGhe WHERE MaLoaiGhe = %s",
        (ma_loai_ghe,),
    )

    if success:
        flash('Da xoa loai ghe.', 'success')
    else:
        flash('Khong the xoa loai ghe. Loai ghe co the dang duoc su dung.', 'error')

    return redirect(url_for('rap.index', section='loaighe'))


@rap_bp.route('/phongchieu/them', methods=['POST'])
def them_phong_chieu():
    ten_phong = request.form.get('TenPhong', '').strip()
    
    if session.get('chuc_vu') == 'Admin':
        ma_cum_rap = request.form.get('MaCumRap', '').strip()
    else:
        ma_cum_rap = session.get('ma_cum_rap')

    so_hang = request.form.get('SoHang', '').strip()
    so_cot = request.form.get('SoCot', '').strip()

    ma_cum_rap_value, so_hang_value, so_cot_value, loi = _du_lieu_phong_chieu_hop_le(
        ten_phong, ma_cum_rap, so_hang, so_cot
    )
    if loi:
        flash(loi, 'error')
        return redirect(url_for('rap.index', section='phongchieu'))

    success = database.execute_query(
        """
        INSERT INTO PhongChieu (TenPhong, MaCumRap, SoHang, SoCot, SucChua)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (ten_phong, ma_cum_rap_value, so_hang_value, so_cot_value, so_hang_value * so_cot_value),
    )

    if success:
        flash('Da them phong chieu moi.', 'success')
    else:
        flash('Khong the them phong chieu.', 'error')

    return redirect(url_for('rap.index', section='phongchieu'))


@rap_bp.route('/phongchieu/tao-va-sinh-ghe', methods=['POST'])
def tao_phong_va_sinh_ghe():
    ten_phong_input = request.form.get('TenPhong', '').strip()
    
    if session.get('chuc_vu') == 'Admin':
        ma_cum_rap = request.form.get('MaCumRap', '').strip()
    else:
        ma_cum_rap = session.get('ma_cum_rap')

    so_hang = request.form.get('SoHang', '').strip()
    so_cot = request.form.get('SoCot', '').strip()
    ma_loai_ghe_mac_dinh = request.form.get('MaLoaiGheMacDinh', '').strip()

    if not ten_phong_input:
        flash('Vui lòng nhập tên phòng.', 'error')
        return redirect(url_for('rap.index', section='phongchieu'))

    # Split the input by comma and clean up spaces
    danh_sach_phong = [p.strip() for p in ten_phong_input.split(',') if p.strip()]
    
    if not danh_sach_phong:
        flash('Vui lòng nhập tên phòng hợp lệ.', 'error')
        return redirect(url_for('rap.index', section='phongchieu'))

    thanh_cong_count = 0
    that_bai_count = 0
    loi_details = []

    for ten_phong in danh_sach_phong:
        ma_cum_rap_value, so_hang_value, so_cot_value, ma_loai_ghe_value, loi = _du_lieu_tao_phong_va_ghe_hop_le(
            ten_phong, ma_cum_rap, so_hang, so_cot, ma_loai_ghe_mac_dinh
        )
        if loi:
            that_bai_count += 1
            loi_details.append(f"{ten_phong}: {loi}")
            continue

        if ma_loai_ghe_value == 0:
            success = database.execute_query(
                "INSERT INTO PhongChieu (TenPhong, MaCumRap, SoHang, SoCot) VALUES (%s, %s, %s, %s)",
                (ten_phong, ma_cum_rap_value, so_hang_value, so_cot_value),
            )
            if success:
                thanh_cong_count += 1
            else:
                that_bai_count += 1
                loi_details.append(f"{ten_phong}: Lỗi CSDL")
        else:
            success = database.execute_query(
                "CALL sp_TaoPhongVaGhe(%s, %s, %s, %s, %s)",
                (ten_phong, ma_cum_rap_value, so_hang_value, so_cot_value, ma_loai_ghe_value),
            )
            if success:
                thanh_cong_count += 1
            else:
                that_bai_count += 1
                loi_details.append(f"{ten_phong}: Lỗi khi gọi SP")

    if that_bai_count == 0:
        flash(f'Đã tạo thành công {thanh_cong_count} phòng chiếu mới!', 'success')
    elif thanh_cong_count > 0:
        error_msg = f'Tạo thành công {thanh_cong_count} phòng. Thất bại {that_bai_count} phòng.'
        flash(error_msg, 'warning')
    else:
        error_msg = f'Không thể tạo phòng nào. (Lỗi: {loi_details[0][:50]}...)'
        flash(error_msg, 'error')

    return redirect(url_for('rap.index', section='phongchieu'))


@rap_bp.route('/phongchieu/sua/<int:ma_phong>', methods=['GET', 'POST'])
def sua_phong_chieu(ma_phong):
    # Check ownership if Quản Lý
    if session.get('chuc_vu') != 'Admin':
        pc = database.fetch_all("SELECT MaCumRap FROM PhongChieu WHERE MaPhong = %s", (ma_phong,))
        if not pc or pc[0]['MaCumRap'] != session.get('ma_cum_rap'):
            flash('Bạn không có quyền sửa phòng chiếu của rạp khác', 'error')
            return redirect(url_for('rap.index', section='phongchieu'))

    if request.method == 'POST':
        ten_phong = request.form.get('TenPhong', '').strip()
        
        if session.get('chuc_vu') == 'Admin':
            ma_cum_rap = request.form.get('MaCumRap', '').strip()
        else:
            ma_cum_rap = session.get('ma_cum_rap')

        so_hang = request.form.get('SoHang', '').strip()
        so_cot = request.form.get('SoCot', '').strip()

        ma_cum_rap_value, so_hang_value, so_cot_value, loi = _du_lieu_phong_chieu_hop_le(
            ten_phong, ma_cum_rap, so_hang, so_cot, ma_phong
        )
        if loi:
            flash(loi, 'error')
            return redirect(url_for('rap.sua_phong_chieu', ma_phong=ma_phong))

        success = database.execute_query(
            """
            UPDATE PhongChieu
            SET TenPhong = %s, MaCumRap = %s, SoHang = %s, SoCot = %s, SucChua = %s
            WHERE MaPhong = %s
            """,
            (ten_phong, ma_cum_rap_value, so_hang_value, so_cot_value, so_hang_value * so_cot_value, ma_phong),
        )

        if success:
            flash('Da cap nhat phong chieu.', 'success')
            return redirect(url_for('rap.index', section='phongchieu'))

        flash('Khong the cap nhat phong chieu.', 'error')

    phong_chieu = database.fetch_all(
        """
        SELECT MaPhong, TenPhong, MaCumRap, MaLoaiPhong, SoHang, SoCot, SucChua
        FROM PhongChieu
        WHERE MaPhong = %s
        """,
        (ma_phong,),
    )

    if not phong_chieu:
        flash('Khong tim thay phong chieu can sua.', 'error')
        return redirect(url_for('rap.index', section='phongchieu'))

    return render_template(
        'rap/index.html',
        **_tao_context_quan_ly(
            active_section='phongchieu',
            phong_chieu_form_data=phong_chieu[0],
            phong_chieu_editing_id=ma_phong,
        ),
    )


@rap_bp.route('/phongchieu/xoa/<int:ma_phong>', methods=['POST'])
def xoa_phong_chieu(ma_phong):
    if session.get('chuc_vu') != 'Admin':
        pc = database.fetch_all("SELECT MaCumRap FROM PhongChieu WHERE MaPhong = %s", (ma_phong,))
        if not pc or pc[0]['MaCumRap'] != session.get('ma_cum_rap'):
            flash('Bạn không có quyền xóa phòng chiếu của rạp khác', 'error')
            return redirect(url_for('rap.index', section='phongchieu'))

    success = database.execute_query(
        "DELETE FROM PhongChieu WHERE MaPhong = %s",
        (ma_phong,),
    )

    if success:
        flash('Da xoa phong chieu.', 'success')
    else:
        flash('Khong the xoa phong chieu. Phong chieu co the dang duoc su dung.', 'error')

    return redirect(url_for('rap.index', section='phongchieu'))


@rap_bp.route('/ghe/them', methods=['POST'])
def them_ghe():
    ten_ghe = request.form.get('TenGhe', '').strip()
    ma_phong = request.form.get('MaPhong', '').strip()
    ma_loai_ghe = request.form.get('MaLoaiGhe', '').strip()

    if session.get('chuc_vu') != 'Admin':
        pc = database.fetch_all("SELECT MaCumRap FROM PhongChieu WHERE MaPhong = %s", (ma_phong,))
        if not pc or pc[0]['MaCumRap'] != session.get('ma_cum_rap'):
            flash('Bạn không có quyền thêm ghế cho phòng chiếu của rạp khác', 'error')
            return redirect(url_for('rap.index', section='ghe'))

    ma_phong_value, ma_loai_ghe_value, loi = _du_lieu_ghe_hop_le(ten_ghe, ma_phong, ma_loai_ghe)
    if loi:
        flash(loi, 'error')
        return redirect(url_for('rap.index', section='ghe'))

    success = database.execute_query(
        """
        INSERT INTO Ghe (TenGhe, MaPhong, MaLoaiGhe)
        VALUES (%s, %s, %s)
        """,
        (ten_ghe, ma_phong_value, ma_loai_ghe_value),
    )

    if success:
        flash('Da them ghe moi.', 'success')
    else:
        flash('Khong the them ghe.', 'error')

    return redirect(url_for('rap.index', section='ghe'))


@rap_bp.route('/ghe/sua/<int:ma_ghe>', methods=['GET', 'POST'])
def sua_ghe(ma_ghe):
    if session.get('chuc_vu') != 'Admin':
        ghe_cur = database.fetch_all("SELECT MaPhong FROM Ghe WHERE MaGhe = %s", (ma_ghe,))
        if not ghe_cur:
            flash('Không tìm thấy ghế', 'error')
            return redirect(url_for('rap.index', section='ghe'))
        pc_cur = database.fetch_all("SELECT MaCumRap FROM PhongChieu WHERE MaPhong = %s", (ghe_cur[0]['MaPhong'],))
        if not pc_cur or pc_cur[0]['MaCumRap'] != session.get('ma_cum_rap'):
            flash('Bạn không có quyền sửa ghế của rạp khác', 'error')
            return redirect(url_for('rap.index', section='ghe'))

    if request.method == 'POST':
        ten_ghe = request.form.get('TenGhe', '').strip()
        ma_phong = request.form.get('MaPhong', '').strip()
        ma_loai_ghe = request.form.get('MaLoaiGhe', '').strip()

        if session.get('chuc_vu') != 'Admin':
            pc_target = database.fetch_all("SELECT MaCumRap FROM PhongChieu WHERE MaPhong = %s", (ma_phong,))
            if not pc_target or pc_target[0]['MaCumRap'] != session.get('ma_cum_rap'):
                flash('Bạn không có quyền chuyển ghế sang rạp khác', 'error')
                return redirect(url_for('rap.index', section='ghe'))

        ma_phong_value, ma_loai_ghe_value, loi = _du_lieu_ghe_hop_le(ten_ghe, ma_phong, ma_loai_ghe, ma_ghe)
        if loi:
            flash(loi, 'error')
            return redirect(url_for('rap.sua_ghe', ma_ghe=ma_ghe))

        success = database.execute_query(
            """
            UPDATE Ghe
            SET TenGhe = %s, MaPhong = %s, MaLoaiGhe = %s
            WHERE MaGhe = %s
            """,
            (ten_ghe, ma_phong_value, ma_loai_ghe_value, ma_ghe),
        )

        if success:
            flash('Da cap nhat ghe.', 'success')
            return redirect(url_for('rap.index', section='ghe'))

        flash('Khong the cap nhat ghe.', 'error')

    ghe = database.fetch_all(
        """
        SELECT MaGhe, TenGhe, MaPhong, MaLoaiGhe
        FROM Ghe
        WHERE MaGhe = %s
        """,
        (ma_ghe,),
    )

    if not ghe:
        flash('Khong tim thay ghe can sua.', 'error')
        return redirect(url_for('rap.index', section='ghe'))

    return render_template(
        'rap/index.html',
        **_tao_context_quan_ly(
            active_section='ghe',
            ghe_form_data=ghe[0],
            ghe_editing_id=ma_ghe,
        ),
    )


@rap_bp.route('/ghe/xoa/<int:ma_ghe>', methods=['POST'])
def xoa_ghe(ma_ghe):
    if session.get('chuc_vu') != 'Admin':
        ghe_cur = database.fetch_all("SELECT MaPhong FROM Ghe WHERE MaGhe = %s", (ma_ghe,))
        if not ghe_cur:
            flash('Không tìm thấy ghế', 'error')
            return redirect(url_for('rap.index', section='ghe'))
        pc_cur = database.fetch_all("SELECT MaCumRap FROM PhongChieu WHERE MaPhong = %s", (ghe_cur[0]['MaPhong'],))
        if not pc_cur or pc_cur[0]['MaCumRap'] != session.get('ma_cum_rap'):
            flash('Bạn không có quyền xóa ghế của rạp khác', 'error')
            return redirect(url_for('rap.index', section='ghe'))

    success = database.execute_query(
        "DELETE FROM Ghe WHERE MaGhe = %s",
        (ma_ghe,),
    )

    if success:
        flash('Da xoa ghe.', 'success')
    else:
        flash('Khong the xoa ghe.', 'error')

    return redirect(url_for('rap.index', section='ghe'))

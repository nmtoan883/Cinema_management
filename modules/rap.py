from decimal import Decimal, InvalidOperation

from flask import Blueprint, flash, redirect, render_template, request, url_for

import database

rap_bp = Blueprint('rap', __name__)


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


def _du_lieu_loai_phong_hop_le(ten_loai_phong, phu_thu, ma_loai_phong=None):
    if not ten_loai_phong or not phu_thu:
        return None, 'Vui long nhap day du ten loai phong va phu thu.'

    try:
        phu_thu_value = Decimal(phu_thu)
    except InvalidOperation:
        return None, 'Phu thu phai la mot so hop le.'

    if phu_thu_value < 0:
        return None, 'Phu thu khong duoc am.'

    if _loai_phong_da_ton_tai(ten_loai_phong, ma_loai_phong):
        return None, 'Loai phong nay da ton tai.'

    return phu_thu_value, None


def _loai_ghe_da_ton_tai(ten_loai_ghe, ma_loai_ghe=None):
    query = """
        SELECT MaLoaiGhe
        FROM LoaiGhe
        WHERE TenLoai = %s
    """
    params = [ten_loai_ghe]

    if ma_loai_ghe is not None:
        query += " AND MaLoaiGhe <> %s"
        params.append(ma_loai_ghe)

    return bool(database.fetch_all(query, tuple(params)))


def _du_lieu_loai_ghe_hop_le(ten_loai_ghe, phu_thu, ma_loai_ghe=None):
    if not ten_loai_ghe or not phu_thu:
        return None, 'Vui long nhap day du ten loai ghe va phu thu.'

    try:
        phu_thu_value = Decimal(phu_thu)
    except InvalidOperation:
        return None, 'Phu thu ghe phai la mot so hop le.'

    if phu_thu_value < 0:
        return None, 'Phu thu ghe khong duoc am.'

    if _loai_ghe_da_ton_tai(ten_loai_ghe, ma_loai_ghe):
        return None, 'Loai ghe nay da ton tai.'

    return phu_thu_value, None


def _phong_chieu_da_ton_tai(ten_phong, ma_cum_rap, ma_phong=None):
    query = """
        SELECT MaPhong
        FROM PhongChieu
        WHERE TenPhong = %s AND MaCumRap = %s
    """
    params = [ten_phong, ma_cum_rap]

    if ma_phong is not None:
        query += " AND MaPhong <> %s"
        params.append(ma_phong)

    return bool(database.fetch_all(query, tuple(params)))


def _cum_rap_hop_le(ma_cum_rap):
    return bool(database.fetch_all("SELECT MaCumRap FROM CumRap WHERE MaCumRap = %s", (ma_cum_rap,)))


def _loai_phong_hop_le(ma_loai_phong):
    return bool(database.fetch_all("SELECT MaLoaiPhong FROM LoaiPhong WHERE MaLoaiPhong = %s", (ma_loai_phong,)))


def _du_lieu_phong_chieu_hop_le(ten_phong, ma_cum_rap, ma_loai_phong, suc_chua, ma_phong=None):
    if not ten_phong or not ma_cum_rap or not ma_loai_phong or not suc_chua:
        return None, None, None, 'Vui long nhap day du ten phong, cum rap, loai phong va suc chua.'

    try:
        ma_cum_rap_value = int(ma_cum_rap)
        ma_loai_phong_value = int(ma_loai_phong)
        suc_chua_value = int(suc_chua)
    except ValueError:
        return None, None, None, 'Cum rap, loai phong va suc chua phai la gia tri hop le.'

    if suc_chua_value <= 0:
        return None, None, None, 'Suc chua phai lon hon 0.'

    if not _cum_rap_hop_le(ma_cum_rap_value):
        return None, None, None, 'Cum rap khong ton tai.'

    if not _loai_phong_hop_le(ma_loai_phong_value):
        return None, None, None, 'Loai phong khong ton tai.'

    if _phong_chieu_da_ton_tai(ten_phong, ma_cum_rap_value, ma_phong):
        return None, None, None, 'Ten phong da ton tai trong cum rap nay.'

    return ma_cum_rap_value, ma_loai_phong_value, suc_chua_value, None


def _du_lieu_tao_phong_va_ghe_hop_le(ten_phong, ma_cum_rap, ma_loai_phong, suc_chua, ma_loai_ghe_mac_dinh):
    ma_cum_rap_value, ma_loai_phong_value, suc_chua_value, loi = _du_lieu_phong_chieu_hop_le(
        ten_phong, ma_cum_rap, ma_loai_phong, suc_chua
    )
    if loi:
        return None, None, None, None, loi

    if not ma_loai_ghe_mac_dinh:
        return None, None, None, None, 'Vui long chon loai ghe mac dinh.'

    try:
        ma_loai_ghe_value = int(ma_loai_ghe_mac_dinh)
    except ValueError:
        return None, None, None, None, 'Loai ghe mac dinh phai la gia tri hop le.'

    if not _loai_ghe_hop_le(ma_loai_ghe_value):
        return None, None, None, None, 'Loai ghe mac dinh khong ton tai.'

    if suc_chua_value < 100:
        return None, None, None, None, 'Suc chua phai lon hon hoac bang 100 de sinh ghe tu A1 den J10.'

    return ma_cum_rap_value, ma_loai_phong_value, suc_chua_value, ma_loai_ghe_value, None


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
    ds_cum_rap = database.fetch_all(
        """
        SELECT MaCumRap, TenCumRap, DiaChi, Hotline
        FROM CumRap
        ORDER BY MaCumRap ASC
        """
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
    ds_phong_chieu = database.fetch_all(
        """
        SELECT
            pc.MaPhong,
            pc.TenPhong,
            pc.MaCumRap,
            pc.MaLoaiPhong,
            pc.SucChua,
            cr.TenCumRap,
            lp.TenLoaiPhong
        FROM PhongChieu pc
        JOIN CumRap cr ON pc.MaCumRap = cr.MaCumRap
        JOIN LoaiPhong lp ON pc.MaLoaiPhong = lp.MaLoaiPhong
        ORDER BY pc.MaPhong ASC
        """
    )
    ds_ghe = database.fetch_all(
        """
        SELECT
            g.MaGhe,
            g.TenGhe,
            g.MaPhong,
            g.MaLoaiGhe,
            pc.TenPhong,
            lg.TenLoai
        FROM Ghe g
        JOIN PhongChieu pc ON g.MaPhong = pc.MaPhong
        JOIN LoaiGhe lg ON g.MaLoaiGhe = lg.MaLoaiGhe
        ORDER BY g.MaGhe ASC
        """
    )
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
        flash('Khong the them cum rap. Kiem tra du lieu trung hoac loi CSDL.', 'error')

    return redirect(url_for('rap.index', section='cumrap'))


@rap_bp.route('/sua/<int:ma_cum_rap>', methods=['GET', 'POST'])
def sua_cum_rap(ma_cum_rap):
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
    phu_thu = request.form.get('PhuThu', '').strip()

    phu_thu_value, loi = _du_lieu_loai_phong_hop_le(ten_loai_phong, phu_thu)
    if loi:
        flash(loi, 'error')
        return redirect(url_for('rap.index', section='loaiphong'))

    success = database.execute_query(
        """
        INSERT INTO LoaiPhong (TenLoaiPhong, PhuThu)
        VALUES (%s, %s)
        """,
        (ten_loai_phong, phu_thu_value),
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
        phu_thu = request.form.get('PhuThu', '').strip()

        phu_thu_value, loi = _du_lieu_loai_phong_hop_le(ten_loai_phong, phu_thu, ma_loai_phong)
        if loi:
            flash(loi, 'error')
            return redirect(url_for('rap.sua_loai_phong', ma_loai_phong=ma_loai_phong))

        success = database.execute_query(
            """
            UPDATE LoaiPhong
            SET TenLoaiPhong = %s, PhuThu = %s
            WHERE MaLoaiPhong = %s
            """,
            (ten_loai_phong, phu_thu_value, ma_loai_phong),
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
    phu_thu = request.form.get('PhuThu', '').strip()

    phu_thu_value, loi = _du_lieu_loai_ghe_hop_le(ten_loai_ghe, phu_thu)
    if loi:
        flash(loi, 'error')
        return redirect(url_for('rap.index', section='loaighe'))

    success = database.execute_query(
        """
        INSERT INTO LoaiGhe (TenLoai, PhuThu)
        VALUES (%s, %s)
        """,
        (ten_loai_ghe, phu_thu_value),
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
        phu_thu = request.form.get('PhuThu', '').strip()

        phu_thu_value, loi = _du_lieu_loai_ghe_hop_le(ten_loai_ghe, phu_thu, ma_loai_ghe)
        if loi:
            flash(loi, 'error')
            return redirect(url_for('rap.sua_loai_ghe', ma_loai_ghe=ma_loai_ghe))

        success = database.execute_query(
            """
            UPDATE LoaiGhe
            SET TenLoai = %s, PhuThu = %s
            WHERE MaLoaiGhe = %s
            """,
            (ten_loai_ghe, phu_thu_value, ma_loai_ghe),
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
    ma_cum_rap = request.form.get('MaCumRap', '').strip()
    ma_loai_phong = request.form.get('MaLoaiPhong', '').strip()
    suc_chua = request.form.get('SucChua', '').strip()

    ma_cum_rap_value, ma_loai_phong_value, suc_chua_value, loi = _du_lieu_phong_chieu_hop_le(
        ten_phong, ma_cum_rap, ma_loai_phong, suc_chua
    )
    if loi:
        flash(loi, 'error')
        return redirect(url_for('rap.index', section='phongchieu'))

    success = database.execute_query(
        """
        INSERT INTO PhongChieu (TenPhong, MaCumRap, MaLoaiPhong, SucChua)
        VALUES (%s, %s, %s, %s)
        """,
        (ten_phong, ma_cum_rap_value, ma_loai_phong_value, suc_chua_value),
    )

    if success:
        flash('Da them phong chieu moi.', 'success')
    else:
        flash('Khong the them phong chieu.', 'error')

    return redirect(url_for('rap.index', section='phongchieu'))


@rap_bp.route('/phongchieu/tao-va-sinh-ghe', methods=['POST'])
def tao_phong_va_sinh_ghe():
    ten_phong = request.form.get('TenPhong', '').strip()
    ma_cum_rap = request.form.get('MaCumRap', '').strip()
    ma_loai_phong = request.form.get('MaLoaiPhong', '').strip()
    suc_chua = request.form.get('SucChua', '').strip()
    ma_loai_ghe_mac_dinh = request.form.get('MaLoaiGheMacDinh', '').strip()

    ma_cum_rap_value, ma_loai_phong_value, suc_chua_value, ma_loai_ghe_value, loi = _du_lieu_tao_phong_va_ghe_hop_le(
        ten_phong, ma_cum_rap, ma_loai_phong, suc_chua, ma_loai_ghe_mac_dinh
    )
    if loi:
        flash(loi, 'error')
        return redirect(url_for('rap.index', section='phongchieu'))

    success = database.execute_query(
        "CALL sp_TaoPhongVaGhe(%s, %s, %s, %s, %s)",
        (ten_phong, ma_cum_rap_value, ma_loai_phong_value, suc_chua_value, ma_loai_ghe_value),
    )

    if success:
        flash('Da tao phong chieu va sinh ghe tu dong.', 'success')
    else:
        flash('Khong the goi stored procedure sp_TaoPhongVaGhe.', 'error')

    return redirect(url_for('rap.index', section='phongchieu'))


@rap_bp.route('/phongchieu/sua/<int:ma_phong>', methods=['GET', 'POST'])
def sua_phong_chieu(ma_phong):
    if request.method == 'POST':
        ten_phong = request.form.get('TenPhong', '').strip()
        ma_cum_rap = request.form.get('MaCumRap', '').strip()
        ma_loai_phong = request.form.get('MaLoaiPhong', '').strip()
        suc_chua = request.form.get('SucChua', '').strip()

        ma_cum_rap_value, ma_loai_phong_value, suc_chua_value, loi = _du_lieu_phong_chieu_hop_le(
            ten_phong, ma_cum_rap, ma_loai_phong, suc_chua, ma_phong
        )
        if loi:
            flash(loi, 'error')
            return redirect(url_for('rap.sua_phong_chieu', ma_phong=ma_phong))

        success = database.execute_query(
            """
            UPDATE PhongChieu
            SET TenPhong = %s, MaCumRap = %s, MaLoaiPhong = %s, SucChua = %s
            WHERE MaPhong = %s
            """,
            (ten_phong, ma_cum_rap_value, ma_loai_phong_value, suc_chua_value, ma_phong),
        )

        if success:
            flash('Da cap nhat phong chieu.', 'success')
            return redirect(url_for('rap.index', section='phongchieu'))

        flash('Khong the cap nhat phong chieu.', 'error')

    phong_chieu = database.fetch_all(
        """
        SELECT MaPhong, TenPhong, MaCumRap, MaLoaiPhong, SucChua
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
    if request.method == 'POST':
        ten_ghe = request.form.get('TenGhe', '').strip()
        ma_phong = request.form.get('MaPhong', '').strip()
        ma_loai_ghe = request.form.get('MaLoaiGhe', '').strip()

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
    success = database.execute_query(
        "DELETE FROM Ghe WHERE MaGhe = %s",
        (ma_ghe,),
    )

    if success:
        flash('Da xoa ghe.', 'success')
    else:
        flash('Khong the xoa ghe.', 'error')

    return redirect(url_for('rap.index', section='ghe'))

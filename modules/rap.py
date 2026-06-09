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


@rap_bp.route('/')
def index():
    ds_cum_rap = database.fetch_all(
        """
        SELECT MaCumRap, TenCumRap, DiaChi, Hotline
        FROM CumRap
        ORDER BY MaCumRap ASC
        """
    )
    return render_template(
        'rap/index.html',
        title='Quan Ly Cum Rap',
        ds_cum_rap=ds_cum_rap,
        form_data={},
        editing_id=None,
    )


@rap_bp.route('/them', methods=['POST'])
def them_cum_rap():
    ten_cum_rap = request.form.get('TenCumRap', '').strip()
    dia_chi = request.form.get('DiaChi', '').strip()
    hotline = request.form.get('Hotline', '').strip()

    loi = _du_lieu_cum_rap_hop_le(ten_cum_rap, dia_chi, hotline)
    if loi:
        flash(loi, 'error')
        return redirect(url_for('rap.index'))

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

    return redirect(url_for('rap.index'))


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
            return redirect(url_for('rap.index'))

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
        return redirect(url_for('rap.index'))

    ds_cum_rap = database.fetch_all(
        """
        SELECT MaCumRap, TenCumRap, DiaChi, Hotline
        FROM CumRap
        ORDER BY MaCumRap ASC
        """
    )

    return render_template(
        'rap/index.html',
        title='Quan Ly Cum Rap',
        ds_cum_rap=ds_cum_rap,
        form_data=cum_rap[0],
        editing_id=ma_cum_rap,
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

    return redirect(url_for('rap.index'))

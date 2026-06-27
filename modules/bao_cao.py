from flask import Blueprint, flash, redirect, render_template, request, session
import database
import datetime

bao_cao_bp = Blueprint('bao_cao', __name__)


@bao_cao_bp.before_request
def require_manager_access():
    if session.get('role') != 'nhanvien':
        flash('Bạn cần đăng nhập bằng tài khoản nhân viên để xem báo cáo.', 'error')
        return redirect('/')

    chuc_vu = session.get('chuc_vu', '')
    if chuc_vu not in ['Admin', 'Quản Lý']:
        flash('Bạn không có quyền xem báo cáo phân tích.', 'error')
        return redirect('/')


@bao_cao_bp.route('/')
def index():
    from_date = request.args.get('from_date') or (datetime.datetime.now() - datetime.timedelta(days=30)).strftime('%Y-%m-%d')
    to_date = request.args.get('to_date') or datetime.datetime.now().strftime('%Y-%m-%d')
    group_by = request.args.get('group_by', 'phim')

    if not from_date:
        from_date = (datetime.datetime.now() - datetime.timedelta(days=30)).strftime('%Y-%m-%d')
    if not to_date:
        to_date = datetime.datetime.now().strftime('%Y-%m-%d')

    report_data, summary = lay_du_lieu_bao_cao(from_date, to_date, group_by)

    return render_template(
        'bao_cao/index.html',
        title='Báo Cáo Phân Tích',
        report_data=report_data,
        summary=summary,
        from_date=from_date,
        to_date=to_date,
        group_by=group_by,
    )


def lay_du_lieu_bao_cao(from_date, to_date, group_by):
    start_dt = datetime.datetime.strptime(from_date, '%Y-%m-%d')
    end_dt = datetime.datetime.strptime(to_date, '%Y-%m-%d') + datetime.timedelta(days=1)

    if group_by == 'cumrap':
        query = """
            SELECT
                cr.TenCumRap AS Nhom,
                COUNT(DISTINCT cv.MaVe) AS SoVe,
                ROUND(SUM(COALESCE(cv.GiaMua, CAST(fn_TinhGiaVeCuoiCung(CAST(cv.MaSuatChieu AS UNSIGNED)) AS DECIMAL(18,2)))), 2) AS DoanhThu
            FROM CHITIET_VE cv
            JOIN HOADON hd ON cv.MaHoaDon = hd.MaHoaDon
            JOIN SuatChieu sc ON cv.MaSuatChieu = sc.MaSuatChieu
            JOIN PhongChieu pc ON sc.MaPhong = pc.MaPhong
            JOIN CumRap cr ON pc.MaCumRap = cr.MaCumRap
            WHERE hd.NgayLap >= %s AND hd.NgayLap < %s
            GROUP BY cr.MaCumRap, cr.TenCumRap
            ORDER BY DoanhThu DESC, SoVe DESC
        """
        params = (start_dt, end_dt)
    elif group_by == 'thoigian':
        query = """
            SELECT
                DATE(hd.NgayLap) AS Nhom,
                COUNT(DISTINCT cv.MaVe) AS SoVe,
                ROUND(SUM(COALESCE(cv.GiaMua, CAST(fn_TinhGiaVeCuoiCung(CAST(cv.MaSuatChieu AS UNSIGNED)) AS DECIMAL(18,2)))), 2) AS DoanhThu
            FROM CHITIET_VE cv
            JOIN HOADON hd ON cv.MaHoaDon = hd.MaHoaDon
            WHERE hd.NgayLap >= %s AND hd.NgayLap < %s
            GROUP BY DATE(hd.NgayLap)
            ORDER BY Nhom ASC
        """
        params = (start_dt, end_dt)
    else:
        query = """
            SELECT
                p.TenPhim AS Nhom,
                COUNT(DISTINCT cv.MaVe) AS SoVe,
                ROUND(SUM(COALESCE(cv.GiaMua, CAST(fn_TinhGiaVeCuoiCung(CAST(cv.MaSuatChieu AS UNSIGNED)) AS DECIMAL(18,2)))), 2) AS DoanhThu
            FROM CHITIET_VE cv
            JOIN HOADON hd ON cv.MaHoaDon = hd.MaHoaDon
            JOIN SuatChieu sc ON cv.MaSuatChieu = sc.MaSuatChieu
            JOIN Phim p ON sc.MaPhim = p.MaPhim
            WHERE hd.NgayLap >= %s AND hd.NgayLap < %s
            GROUP BY p.MaPhim, p.TenPhim
            ORDER BY DoanhThu DESC, SoVe DESC
        """
        params = (start_dt, end_dt)

    rows = database.fetch_all(query, params)

    summary = {
        'from_date': from_date,
        'to_date': to_date,
        'group_by': group_by,
        'tong_doanh_thu': sum(float(item.get('DoanhThu', 0) or 0) for item in rows),
        'tong_ve': sum(int(item.get('SoVe', 0) or 0) for item in rows),
    }

    return rows, summary

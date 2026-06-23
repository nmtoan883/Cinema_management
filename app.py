from flask import Flask, render_template, session
import database

from modules.dat_ve import dat_ve_bp
from modules.khach_hang import khach_hang_bp
from modules.phim import phim_bp
from modules.rap import rap_bp
from modules.suat_chieu import suat_chieu_bp
from modules.auth import auth_bp
from modules.nhan_vien import nhan_vien_bp

app = Flask(__name__)
app.secret_key = 'cinema-management-secret-key'

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(phim_bp, url_prefix='/phim')
app.register_blueprint(rap_bp, url_prefix='/rap')
app.register_blueprint(suat_chieu_bp, url_prefix='/suatchieu')
app.register_blueprint(khach_hang_bp, url_prefix='/khachhang')
app.register_blueprint(dat_ve_bp, url_prefix='/datve')
app.register_blueprint(nhan_vien_bp)

@app.context_processor
def inject_user():
    return dict(
        current_user_name=session.get('user_name'),
        current_user_role=session.get('role'),
        current_user_id=session.get('user_id')
    )

@app.route('/')
def index():
    query = "SELECT * FROM v_DanhSachPhim ORDER BY NgayKhoiChieu DESC LIMIT 8"
    ds_phim = database.fetch_all(query)
    return render_template('index.html', title='Trang Chủ', ds_phim=ds_phim)

@app.route('/chi-tiet-phim/<int:ma_phim>')
def chi_tiet_phim(ma_phim):
    query = "SELECT * FROM v_DanhSachPhim WHERE MaPhim = %s"
    phim = database.fetch_all(query, (ma_phim,))
    if not phim:
        return "Không tìm thấy phim", 404
        
    # Truy vấn danh sách suất chiếu tương lai của phim này
    query_sc = """
        SELECT sc.MaSuatChieu, sc.GioBatDau, cr.TenCumRap, lp.TenLoaiPhong
        FROM SuatChieu sc
        JOIN PhongChieu pc ON sc.MaPhong = pc.MaPhong
        JOIN CumRap cr ON pc.MaCumRap = cr.MaCumRap
        JOIN LoaiPhong lp ON pc.MaLoaiPhong = lp.MaLoaiPhong
        WHERE sc.MaPhim = %s AND sc.GioBatDau >= NOW()
        ORDER BY cr.TenCumRap, sc.GioBatDau ASC
    """
    ds_suat_chieu = database.fetch_all(query_sc, (ma_phim,))
    
    # Nhóm lịch chiếu theo Rạp
    lich_chieu = {}
    for sc in ds_suat_chieu:
        cum_rap = sc['TenCumRap']
        if cum_rap not in lich_chieu:
            lich_chieu[cum_rap] = []
        lich_chieu[cum_rap].append(sc)
        
    return render_template('chi_tiet_phim.html', title=phim[0]['TenPhim'], phim=phim[0], lich_chieu=lich_chieu)

if __name__ == '__main__':
    app.run(debug=True, port=5000)

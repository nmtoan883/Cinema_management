from flask import Flask, render_template

from modules.dat_ve import dat_ve_bp
from modules.khach_hang import khach_hang_bp
from modules.phim import phim_bp
from modules.rap import rap_bp
from modules.suat_chieu import suat_chieu_bp

app = Flask(__name__)
app.secret_key = 'cinema-management-secret-key'

app.register_blueprint(phim_bp, url_prefix='/phim')
app.register_blueprint(rap_bp, url_prefix='/rap')
app.register_blueprint(suat_chieu_bp, url_prefix='/suatchieu')
app.register_blueprint(khach_hang_bp, url_prefix='/khachhang')
app.register_blueprint(dat_ve_bp, url_prefix='/datve')


@app.route('/')
def index():
    return render_template('base.html', title='Trang Chu')


if __name__ == '__main__':
    app.run(debug=True, port=5000)

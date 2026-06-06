from flask import Flask, render_template

# Khởi tạo ứng dụng Flask
app = Flask(__name__)

# Import các Blueprint của 5 thành viên
from modules.phim import phim_bp
from modules.rap import rap_bp
from modules.suat_chieu import suat_chieu_bp
from modules.khach_hang import khach_hang_bp
from modules.dat_ve import dat_ve_bp

# Đăng ký Blueprint (Gắn URL cho từng phân hệ)
app.register_blueprint(phim_bp, url_prefix='/phim')
app.register_blueprint(rap_bp, url_prefix='/rap')
app.register_blueprint(suat_chieu_bp, url_prefix='/suatchieu')
app.register_blueprint(khach_hang_bp, url_prefix='/khachhang')
app.register_blueprint(dat_ve_bp, url_prefix='/datve')

@app.route('/')
def index():
    # Trang chủ hiển thị tổng quan
    return render_template('base.html', title="Trang Chủ")

if __name__ == '__main__':
    # Chạy server ở chế độ debug để tự reload khi sửa code
    app.run(debug=True, port=5000)

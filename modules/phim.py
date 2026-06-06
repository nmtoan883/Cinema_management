from flask import Blueprint, render_template, request, redirect, url_prefix
import database

# Đăng ký Blueprint cho module Phim
phim_bp = Blueprint('phim', __name__)

@phim_bp.route('/')
def index():
    """Trang chủ của module quản lý phim: Hiển thị danh sách"""
    query = "SELECT MaPhim, TenPhim, ThoiLuong, NgayKhoiChieu, DoTuoi FROM Phim"
    results = database.fetch_all(query)
    
    return render_template('phim/index.html', title="Quản lý Phim", ds_phim=results)

@phim_bp.route('/them', methods=['GET', 'POST'])
def them_phim():
    """Trang thêm phim mới"""
    if request.method == 'POST':
        # Lấy dữ liệu từ form (tự viết HTML form nhé)
        ten_phim = request.form.get('ten_phim')
        thoi_luong = request.form.get('thoi_luong')
        # Gọi SQL insert ở đây...
        
        return redirect('/phim')
    return render_template('phim/them.html', title="Thêm Phim")

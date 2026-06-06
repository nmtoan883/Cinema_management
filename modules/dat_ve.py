from flask import Blueprint, render_template, request, flash, redirect
import database

dat_ve_bp = Blueprint('dat_ve', __name__)

@dat_ve_bp.route('/')
def index():
    return render_template('dat_ve/index.html', title="Đặt Vé & Giao Dịch")

@dat_ve_bp.route('/ban-ve', methods=['POST'])
def ban_ve():
    # Nhận dữ liệu từ form thanh toán
    # TODO: Thành viên 5 gọi database.execute_query với lệnh Transaction ở đây
    flash("Chức năng đang được xây dựng (cần gọi Transaction).", "info")
    return redirect('/datve')

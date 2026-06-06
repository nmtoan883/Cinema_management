from flask import Blueprint, render_template, request
import database

khach_hang_bp = Blueprint('khach_hang', __name__)

@khach_hang_bp.route('/')
def index():
    # Lấy danh sách VIP
    query_vip = "SELECT * FROM View_DanhSachKhachHangVIP"
    ds_vip = database.fetch_all(query_vip)
    
    # Lấy danh sách Bắp Nước (Dịch Vụ)
    query_dv = "SELECT MaDichVu, TenDichVu, GiaBan FROM DichVu"
    ds_dv = database.fetch_all(query_dv)
    
    return render_template('khach_hang/index.html', title="Khách Hàng & Dịch Vụ", ds_vip=ds_vip, ds_dv=ds_dv)

@khach_hang_bp.route('/tim-kiem', methods=['GET'])
def tim_khach_hang():
    sdt = request.args.get('sdt')
    ket_qua = []
    if sdt:
        query = "CALL sp_TimKhachHangBangSDT(%s)"
        ket_qua = database.fetch_all(query, (sdt,))
        
    return render_template('khach_hang/index.html', title="Tìm Khách", ket_qua_tim=ket_qua)

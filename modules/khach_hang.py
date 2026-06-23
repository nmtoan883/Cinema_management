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
    
    # Lấy danh sách Nhân viên
    query_nv = """
        SELECT NV.MaNV, NV.HoTen, NV.ChucVu, CR.TenCumRap
        FROM NhanVien NV
        JOIN CumRap CR ON NV.MaCumRap = CR.MaCumRap
    """
    ds_nv = database.fetch_all(query_nv)
    
    return render_template('khach_hang/index.html', title="Khách Hàng & Dịch Vụ", ds_vip=ds_vip, ds_dv=ds_dv, ds_nv=ds_nv)

@khach_hang_bp.route('/tim-kiem', methods=['GET'])
def tim_khach_hang():
    sdt = request.args.get('sdt')
    ket_qua = []
    if sdt:
        query = "CALL sp_TimKhachHangBangSDT(%s)"
        ket_qua = database.fetch_all(query, (sdt,))
        
    return render_template('khach_hang/index.html', title="Tìm Khách", ket_qua_tim=ket_qua)

@khach_hang_bp.route('/them', methods=['GET', 'POST'])
def them_khach():
    if request.method == 'POST':
        ho_ten = request.form.get('ho_ten')
        sdt = request.form.get('sdt')
        email = request.form.get('email')
        
        # Mặc định thêm khách hàng với hạng Đồng (MaHang = 1)
        query = "INSERT INTO KhachHang (HoTen, SDT, Email, DiemTichLuy, MaHang) VALUES (%s, %s, %s, 0, 1)"
        database.execute_query(query, (ho_ten, sdt, email))
        return redirect('/khachhang')
        
    return render_template('khach_hang/them_khach.html', title="Thêm Khách Hàng")

@khach_hang_bp.route('/dichvu/them', methods=['GET', 'POST'])
def them_dich_vu():
    if request.method == 'POST':
        ten_dich_vu = request.form.get('ten_dich_vu')
        gia_ban = request.form.get('gia_ban')
        
        query = "INSERT INTO DichVu (TenDichVu, GiaBan) VALUES (%s, %s)"
        database.execute_query(query, (ten_dich_vu, gia_ban))
        return redirect('/khachhang')
        
    return render_template('khach_hang/them_dichvu.html', title="Thêm Dịch Vụ")

@khach_hang_bp.route('/dichvu/sua/<int:id>', methods=['GET', 'POST'])
def sua_dich_vu(id):
    if request.method == 'POST':
        gia_ban = request.form.get('gia_ban')
        query = "UPDATE DichVu SET GiaBan = %s WHERE MaDichVu = %s"
        database.execute_query(query, (gia_ban, id))
        return redirect('/khachhang')
        
    # Lấy thông tin dịch vụ hiện tại để hiển thị lên form
    query = "SELECT * FROM DichVu WHERE MaDichVu = %s"
    dich_vu = database.fetch_all(query, (id,))
    if dich_vu:
        return render_template('khach_hang/sua_dichvu.html', title="Sửa Dịch Vụ", dich_vu=dich_vu[0])
    return redirect('/khachhang')

@khach_hang_bp.route('/dichvu/xoa/<int:id>', methods=['GET'])
def xoa_dich_vu(id):
    query = "DELETE FROM DichVu WHERE MaDichVu = %s"
    database.execute_query(query, (id,))
    return redirect('/khachhang')

@khach_hang_bp.route('/nhanvien/them', methods=['GET', 'POST'])
def them_nhan_vien():
    if request.method == 'POST':
        ho_ten = request.form.get('ho_ten')
        chuc_vu = request.form.get('chuc_vu')
        ma_cum_rap = request.form.get('ma_cum_rap')
        
        query = "INSERT INTO NhanVien (HoTen, ChucVu, MaCumRap) VALUES (%s, %s, %s)"
        database.execute_query(query, (ho_ten, chuc_vu, ma_cum_rap))
        return redirect('/khachhang')
        
    # Lấy danh sách cụm rạp để chọn
    ds_rap = database.fetch_all("SELECT MaCumRap, TenCumRap FROM CumRap")
    return render_template('khach_hang/them_nhanvien.html', title="Thêm Nhân Viên", ds_rap=ds_rap)

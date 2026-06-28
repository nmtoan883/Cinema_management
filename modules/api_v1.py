from flask import Blueprint, jsonify, request
import database

api_v1_bp = Blueprint('api_v1', __name__)

@api_v1_bp.route('/phim', methods=['GET'])
def get_phim():
    """Lấy danh sách tất cả các phim"""
    sql = """
    SELECT
        PHIM.MaPhim,
        PHIM.TenPhim,
        PHIM.ThoiLuong,
        DATE_FORMAT(PHIM.NgayKhoiChieu, '%Y-%m-%d') AS NgayKhoiChieu,
        PHIM.GioiHanDoTuoi,
        PHIM.Poster,
        PHIM.MoTa,
        PHIM.TrailerURL,
        GROUP_CONCAT(THELOAI.TenTheLoai SEPARATOR ', ') AS TheLoai
    FROM PHIM
    LEFT JOIN PHIM_THELOAI ON PHIM.MaPhim = PHIM_THELOAI.MaPhim
    LEFT JOIN THELOAI ON THELOAI.MaTheLoai = PHIM_THELOAI.MaTheLoai
    GROUP BY PHIM.MaPhim
    ORDER BY PHIM.MaPhim DESC
    """
    ds_phim = database.fetch_all(sql)
    return jsonify({
        'status': 'success',
        'data': ds_phim
    })

@api_v1_bp.route('/phim/<int:ma_phim>', methods=['GET'])
def get_chi_tiet_phim(ma_phim):
    """Lấy chi tiết một bộ phim"""
    sql = """
    SELECT
        PHIM.MaPhim,
        PHIM.TenPhim,
        PHIM.ThoiLuong,
        DATE_FORMAT(PHIM.NgayKhoiChieu, '%Y-%m-%d') AS NgayKhoiChieu,
        PHIM.GioiHanDoTuoi,
        PHIM.Poster,
        PHIM.MoTa,
        PHIM.TrailerURL
    FROM PHIM
    WHERE MaPhim = %s
    """
    phim = database.fetch_all(sql, (ma_phim,))
    if not phim:
        return jsonify({'status': 'error', 'message': 'Không tìm thấy phim'}), 404
        
    return jsonify({
        'status': 'success',
        'data': phim[0]
    })

@api_v1_bp.route('/rap', methods=['GET'])
def get_rap():
    """Lấy danh sách các cụm rạp"""
    sql = "SELECT MaCumRap, TenCumRap, DiaChi, Hotline FROM CumRap ORDER BY MaCumRap ASC"
    ds_rap = database.fetch_all(sql)
    return jsonify({
        'status': 'success',
        'data': ds_rap
    })

@api_v1_bp.route('/suatchieu', methods=['GET'])
def get_suat_chieu():
    """Lấy danh sách suất chiếu, có thể lọc theo phim_id hoặc rap_id"""
    phim_id = request.args.get('phim_id')
    rap_id = request.args.get('rap_id')
    
    sql = """
    SELECT
        SC.MaSuat,
        P.TenPhim,
        CR.TenCumRap,
        PC.TenPhong,
        DATE_FORMAT(SC.ThoiGianChieu, '%Y-%m-%d %H:%i:%s') AS ThoiGianChieu,
        SC.GiaCoBan
    FROM SUATCHIEU SC
    JOIN PHIM P ON SC.MaPhim = P.MaPhim
    JOIN PHONGCHIEU PC ON SC.MaPhong = PC.MaPhong
    JOIN CUMRAP CR ON PC.MaCumRap = CR.MaCumRap
    WHERE 1=1
    """
    params = []
    
    if phim_id:
        sql += " AND SC.MaPhim = %s"
        params.append(phim_id)
        
    if rap_id:
        sql += " AND CR.MaCumRap = %s"
        params.append(rap_id)
        
    sql += " ORDER BY SC.ThoiGianChieu ASC"
    
    ds_suat_chieu = database.fetch_all(sql, tuple(params))
    
    return jsonify({
        'status': 'success',
        'count': len(ds_suat_chieu),
        'data': ds_suat_chieu
    })

@api_v1_bp.route('/phongchieu/<int:ma_phong>/sodo', methods=['GET'])
def get_sodo_phong(ma_phong):
    """Lấy sơ đồ và danh sách ghế của một phòng chiếu"""
    # Lấy thông tin phòng
    phong = database.fetch_all("SELECT MaPhong, TenPhong, SoHang, SoCot FROM PhongChieu WHERE MaPhong = %s", (ma_phong,))
    if not phong:
        return jsonify({'status': 'error', 'message': 'Không tìm thấy phòng chiếu'}), 404
        
    # Lấy danh sách ghế
    sql_ghe = """
        SELECT G.MaGhe, G.TenGhe, G.MaLoaiGhe, L.TenLoai, G.Hang, G.Cot
        FROM Ghe G
        JOIN LoaiGhe L ON G.MaLoaiGhe = L.MaLoaiGhe
        WHERE G.MaPhong = %s
        ORDER BY G.Hang ASC, G.Cot ASC
    """
    ghe_list = database.fetch_all(sql_ghe, (ma_phong,))
    
    return jsonify({
        'status': 'success',
        'data': {
            'phong': phong[0],
            'ghe': ghe_list
        }
    })

@api_v1_bp.route('/phongchieu/<int:ma_phong>/capnhat_sodo', methods=['POST'])
def capnhat_sodo_phong(ma_phong):
    """Cập nhật sơ đồ ghế (thêm, sửa, xóa)"""
    data = request.json
    if not data:
        return jsonify({'status': 'error', 'message': 'Không có dữ liệu'}), 400
        
    updates = data.get('updates', [])
    adds = data.get('adds', [])
    deletes = data.get('deletes', [])
    
    conn = database.get_connection()
    cursor = conn.cursor()
    try:
        # Xử lý cập nhật
        for u in updates:
            cursor.execute("UPDATE Ghe SET MaLoaiGhe = %s, TenGhe = %s WHERE MaGhe = %s AND MaPhong = %s", (u['MaLoaiGhe'], u['TenGhe'], u['MaGhe'], ma_phong))
            
        # Xử lý xóa
        for d in deletes:
            cursor.execute("DELETE FROM Ghe WHERE MaGhe = %s AND MaPhong = %s", (d['MaGhe'], ma_phong))
            
        # Xử lý thêm
        for a in adds:
            cursor.execute("INSERT INTO Ghe (TenGhe, MaPhong, MaLoaiGhe, Hang, Cot) VALUES (%s, %s, %s, %s, %s)", (a['TenGhe'], ma_phong, a['MaLoaiGhe'], a['Hang'], a['Cot']))
            
        conn.commit()
        return jsonify({'status': 'success', 'message': 'Đã cập nhật sơ đồ'})
    except Exception as e:
        conn.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

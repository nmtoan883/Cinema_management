import mysql.connector
from config import DB_CONFIG

def get_connection():
    """
    Tạo và trả về một đối tượng kết nối (connection) tới CSDL.
    Mỗi khi cần query, các thành viên gọi hàm này để lấy connection.
    """
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except mysql.connector.Error as err:
        print(f"Lỗi kết nối CSDL: {err}")
        return None

def execute_query(query, params=None):
    """
    Thực thi một câu lệnh INSERT/UPDATE/DELETE.
    Tự động commit nếu thành công, rollback nếu có lỗi.
    """
    conn = get_connection()
    if not conn:
        return False
        
    cursor = conn.cursor()
    try:
        cursor.execute(query, params or ())
        conn.commit()
        return True
    except mysql.connector.Error as err:
        print(f"Lỗi truy vấn: {err}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

def fetch_all(query, params=None):
    """
    Thực thi câu lệnh SELECT và trả về tất cả các dòng dữ liệu.
    """
    conn = get_connection()
    if not conn:
        return []
        
    cursor = conn.cursor(dictionary=True) # Trả về dạng Dictionary (cột: giá trị)
    try:
        cursor.execute(query, params or ())
        results = cursor.fetchall()
        return results
    except mysql.connector.Error as err:
        print(f"Lỗi truy vấn: {err}")
        return []
    finally:
        cursor.close()
        conn.close()

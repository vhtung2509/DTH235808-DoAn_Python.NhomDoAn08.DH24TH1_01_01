import pyodbc
from tkinter import messagebox

# --- CẤU HÌNH KẾT NỐI SQL SERVER ---
SERVER_NAME = r'TUNG-IT\MSSQL_EXP_2008R2' 
DATABASE_NAME = 'QL_VLXD' 
DRIVER_NAME = '{SQL Server}'  # Hoặc '{ODBC Driver 17 for SQL Server}'

# --- CHUỖI KẾT NỐI (Windows Authentication) ---
CONNECTION_STRING = (
    f"DRIVER={DRIVER_NAME};"
    f"SERVER={SERVER_NAME};"
    f"DATABASE={DATABASE_NAME};"
    "Trusted_Connection=yes;"
)

def get_db_connection():
    """Trả về đối tượng kết nối SQL Server hoặc None nếu thất bại."""
    try:
        # === ĐÃ THÊM autocommit=True ===
        conn = pyodbc.connect(CONNECTION_STRING, autocommit=True)
        # ================================
        return conn
    
    except pyodbc.InterfaceError as ex:
        messagebox.showerror("Lỗi Kết Nối SQL", 
            "Không thể tìm thấy driver hoặc server.\n"
            "➡ Kiểm tra lại tên server hoặc driver trong SQL_connect.py")
        return None
    except pyodbc.Error as ex:
        messagebox.showerror("Lỗi Kết Nối CSDL", 
            f"Không thể kết nối đến SQL Server.\nChi tiết: {ex}")
        return None
    except Exception as e:
        messagebox.showerror("Lỗi Kết Nối", f"Lỗi không xác định: {e}")
        return None

# --- HÀM KIỂM TRA ĐĂNG NHẬP ---
def check_login_credentials(username, password):
    conn = get_db_connection()
    if conn is None:
        return "ERROR_DB_CONNECTION"

    try:
        cursor = conn.cursor()
        sql = "SELECT Quyen FROM TaiKhoan WHERE TenDangNhap = ? AND MatKhau = ?"
        cursor.execute(sql, (username, password))
        result = cursor.fetchone()
        if result:
            return result[0].strip() if result[0] else None
        return None
    except pyodbc.Error as ex:
        messagebox.showerror("Lỗi Truy Vấn", f"Lỗi khi truy cập bảng TaiKhoan:\n{ex}")
        return "ERROR_DB_CONNECTION"
    finally:
        if conn:
            conn.close()

# --- HÀM MỚI ĐỂ XÓA HÓA ĐƠN CŨ ---
def clear_invoice_data():
    """Xóa tất cả dữ liệu trong bảng ChiTietHoaDon và HoaDon, 
       sau đó reset bộ đếm MaHD về 0."""
    
    conn = get_db_connection()
    if conn is None:
        messagebox.showerror("Lỗi Reset CSDL", "Không thể kết nối để xóa dữ liệu hóa đơn cũ.")
        return False # Báo lỗi

    try:
        cursor = conn.cursor()
        
        print("[RESET] Đang xóa ChiTietHoaDon...")
        cursor.execute("DELETE FROM ChiTietHoaDon")
        
        print("[RESET] Đang xóa HoaDon...")
        cursor.execute("DELETE FROM HoaDon")
        
        print("[RESET] Đang reset bộ đếm MaHD...")
        cursor.execute("DBCC CHECKIDENT ('HoaDon', RESEED, 0)") 
        
        # conn.commit() # Không cần commit nữa vì đã bật autocommit=True
        
        print("[RESET] Xóa và reset hóa đơn thành công!")
        return True # Báo thành công

    except pyodbc.Error as e:
        messagebox.showerror("Lỗi Reset CSDL", f"Lỗi khi xóa/reset hóa đơn:\n{e}")
        return False # Báo lỗi
    finally:
        if conn:
            conn.close()
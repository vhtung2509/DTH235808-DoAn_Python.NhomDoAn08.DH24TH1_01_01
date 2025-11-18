import tkinter as tk
from tkinter import messagebox
from tkinter import font as tkFont
import sys

# === CHỈ IMPORT Dashboard VÀ SQL_connect ===
try:
    from Dashboard import run_dashboard
except ImportError as e:
    messagebox.showerror("Lỗi Import Chính", f"Không thể tìm thấy file Dashboard.py!\n{e}")
    sys.exit() # Thoát nếu không có Dashboard

try:
    from SQL_connect import check_login_credentials, clear_invoice_data
except ImportError:
     messagebox.showerror("Lỗi Import Chính", "Không thể tìm thấy file SQL_connect.py!")
     sys.exit()
# ==========================================

# Biến toàn cục
login_successful_flag = False
logged_in_user_role = None

# === HÀM ĐĂNG NHẬP (Giữ nguyên) ===
def show_login_window():
    """Hiển thị cửa sổ đăng nhập."""
    global login_successful_flag, logged_in_user_role
    login_successful_flag = False
    logged_in_user_role = None
    user_closed_window = False

    login_window = tk.Tk()
    login_window.title("Hệ thống quản lý cửa hàng vật liệu xây dựng")
    login_window.geometry("450x350")
    login_window.resizable(False, False)
    login_window.config(bg="#f0f0f0")

    label_font = tkFont.Font(family="Segoe UI", size=12)
    entry_font = tkFont.Font(family="Segoe UI", size=12)
    button_font = tkFont.Font(family="Segoe UI", size=12, weight="bold")
    title_font = tkFont.Font(family="Segoe UI", size=20, weight="bold")
    show_password_var = tk.BooleanVar()

    def toggle_password():
        password_entry.config(show="" if show_password_var.get() else "*")

    def handle_login():
        global login_successful_flag, logged_in_user_role
        username = username_entry.get()
        password = password_entry.get()
        try:
            # (Không cần import trong hàm nữa)
            role = check_login_credentials(username, password)
            if role == "ERROR_DB_CONNECTION":
                status_label.config(text="Lỗi kết nối CSDL!", fg="#dc3545")
            elif role is not None:
                status_label.config(text="Đăng nhập thành công!", fg="#28a745")
                messagebox.showinfo("Thành công", f"Chào mừng {role}, {username}!")
                login_successful_flag = True
                logged_in_user_role = role
                login_window.destroy()
            else:
                status_label.config(text="Sai tài khoản hoặc mật khẩu!", fg="#dc3545")
        except Exception as e:
             messagebox.showerror("Lỗi Đăng Nhập", f"Lỗi không xác định: {e}")

    def on_closing():
        nonlocal user_closed_window
        user_closed_window = True
        login_window.destroy()

    # (Giao diện đăng nhập giữ nguyên)
    main_frame = tk.Frame(login_window, bg="#f0f0f0", padx=30, pady=30); main_frame.pack(expand=True, fill="both"); main_frame.columnconfigure(1, weight=1)
    title_label = tk.Label(main_frame, text="ĐĂNG NHẬP", font=title_font, bg="#f0f0f0", fg="#00529B"); title_label.grid(row=0, column=0, columnspan=2, pady=(0, 25))
    username_label = tk.Label(main_frame, text="Tài khoản:", font=label_font, bg="#f0f0f0"); username_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")
    username_entry = tk.Entry(main_frame, width=30, font=entry_font, relief="solid", bd=1); username_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
    password_label = tk.Label(main_frame, text="Mật khẩu:", font=label_font, bg="#f0f0f0"); password_label.grid(row=2, column=0, padx=10, pady=10, sticky="w")
    password_entry = tk.Entry(main_frame, width=30, show="*", font=entry_font, relief="solid", bd=1); password_entry.grid(row=2, column=1, padx=10, pady=10, sticky="ew")
    show_password_check = tk.Checkbutton(main_frame, text="Hiện mật khẩu", variable=show_password_var, font=("Segoe UI", 10), bg="#f0f0f0", activebackground="#f0f0f0", command=toggle_password); show_password_check.grid(row=3, column=1, padx=10, pady=5, sticky="w")
    login_button = tk.Button(main_frame, text="Đăng nhập", command=handle_login, font=button_font, bg="#0078D4", fg="white", relief="flat", padx=15, pady=5); login_button.grid(row=4, column=0, columnspan=2, pady=20)
    status_label = tk.Label(main_frame, text="", font=label_font, bg="#f0f0f0"); status_label.grid(row=5, column=0, columnspan=2)
    login_window.protocol("WM_DELETE_WINDOW", on_closing); login_window.mainloop()
    return user_closed_window

# ===================================================================
# KHỐI CHẠY CHÍNH (GỌI LOGIN -> GỌI DASHBOARD)
# ===================================================================
if __name__ == "__main__":
    try:
        print("Đang xóa dữ liệu hóa đơn cũ...")
        if not clear_invoice_data():
             print("Lỗi: Không thể xóa dữ liệu hóa đơn cũ.")
    except Exception as e:
         print(f"Lỗi khi gọi clear_invoice_data: {e}")

    print("Bắt đầu chương trình.")
    user_chose_to_exit = show_login_window()

    if user_chose_to_exit:
        print("Người dùng đã đóng cửa sổ đăng nhập.")
    elif login_successful_flag and logged_in_user_role:
        print(f"Đăng nhập thành công. Mở Dashboard cho Quyền: {logged_in_user_role}...")
        # === GỌI DASHBOARD MỚI ===
        run_dashboard(logged_in_user_role)
        print("Dashboard đã đóng.")
    else:
         print("Đăng nhập thất bại.")

    print("Chương trình kết thúc hoàn toàn.")
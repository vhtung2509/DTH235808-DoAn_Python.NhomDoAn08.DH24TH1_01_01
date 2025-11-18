# File: Dashboard_full.py (ĐÃ THÊM NÚT THOÁT)
import tkinter as tk
from tkinter import ttk, messagebox, font as tkFont

# --- IMPORT CÁC HÀM TẠO FRAME ---
try:
    from WareHouse import create_warehouse_frame
except ImportError:
    messagebox.showerror("Lỗi Import (Dashboard)", "Không tìm thấy WareHouse.py hoặc create_warehouse_frame")
    create_warehouse_frame = None

try:
    from ManagerEmployee import create_employee_frame
except ImportError:
    messagebox.showerror("Lỗi Import (Dashboard)", "Không tìm thấy ManagerEmployee.py hoặc create_employee_frame")
    create_employee_frame = None

try:
    from Sales import create_sales_frame
except ImportError:
    messagebox.showerror("Lỗi Import (Dashboard)", "Không tìm thấy Sales.py hoặc create_sales_frame")
    create_sales_frame = None

try:
    from Revenue import create_revenue_frame
except ImportError:
    messagebox.showerror("Lỗi Import (Dashboard)", "Không tìm thấy Revenue.py hoặc create_revenue_frame")
    create_revenue_frame = None

try:
    from Transports import create_transport_frame
except ImportError:
    messagebox.showerror("Lỗi Import (Dashboard)", "Không tìm thấy Transports.py hoặc create_transport_frame")
    create_transport_frame = None

try:
    from SaveInvoice import create_invoice_frame
except ImportError:
    messagebox.showerror("Lỗi Import (Dashboard)", "Không tìm thấy SaveInvoice.py hoặc create_invoice_frame")
    create_invoice_frame = None

# ===========================================
def run_dashboard(role):
    """Tạo cửa sổ Dashboard với Sidebar và nhúng tất cả form."""
    dashboard = tk.Tk()
    dashboard.title(f"Hệ thống Quản lý VLXD (Quyền: {role})")
    dashboard.geometry("1200x750")
    dashboard.config(bg="#f0f0f0")

    sidebar_font = tkFont.Font(family="Segoe UI", size=11, weight="bold")
    sidebar_bg = "#2c3e50"
    content_bg = "#f0f0f0"
    button_fg = "white"
    button_active_bg = "#3498db"

    # --- Khung chính ---
    sidebar_frame = tk.Frame(dashboard, bg=sidebar_bg, width=200)
    sidebar_frame.pack(side="left", fill="y")
    content_frame = tk.Frame(dashboard, bg=content_bg)
    content_frame.pack(side="right", fill="both", expand=True)

    current_content_frame = None

    # --- Hàm chuyển frame ---
    def switch_content(frame_function, frame_name):
        nonlocal current_content_frame
        if current_content_frame:
            current_content_frame.destroy()
        if not frame_function:
            messagebox.showerror("Lỗi", f"Không thể tải {frame_name} (Lỗi Import).")
            return
        try:
            new_frame = frame_function(content_frame)
            if new_frame and isinstance(new_frame, (tk.Frame, ttk.Frame)):
                new_frame.pack(fill="both", expand=True)
                current_content_frame = new_frame
                print(f"[DEBUG] Chuyển sang: {frame_name}")
            else:
                messagebox.showerror("Lỗi Logic", f"Hàm {frame_name} không trả về Frame hợp lệ.")
        except Exception as e:
            messagebox.showerror("Lỗi Khởi Chạy Form", f"Không thể mở {frame_name}:\n{e}")
            print(f"!!! LỖI khi mở {frame_name}: {e}")

    # --- Nút sidebar ---
    buttons_info = [
        ("Quản lý Kho", create_warehouse_frame, create_warehouse_frame),
        ("Quản lý Bán hàng", create_sales_frame, create_sales_frame),
        ("Quản lý Nhân viên", create_employee_frame, create_employee_frame, "Quản lý"),
        ("Báo Cáo Doanh Thu", create_revenue_frame, create_revenue_frame, "Quản lý"),
        ("Vận Chuyển", create_transport_frame, create_transport_frame),
        ("Hóa đơn", create_invoice_frame, create_invoice_frame)
    ]

    for (text, func, check_import, *req_role) in buttons_info:
        if req_role and role.strip() != req_role[0]:
            continue
        if check_import is None:
            continue
        btn = tk.Button(
            sidebar_frame, text=text,
            font=sidebar_font,
            bg=sidebar_bg, fg=button_fg,
            relief="flat", anchor="w",
            padx=20, pady=10,
            activebackground=button_active_bg,
            activeforeground=button_fg,
            command=lambda f=func, n=text: switch_content(f, n)
        )
        btn.pack(fill="x", pady=2, padx=10)
        
    # Nút Thoát (được đẩy xuống dưới cùng bằng side="bottom")
    btn_thoat = tk.Button(
        sidebar_frame, 
        text="Thoát Ứng Dụng",
        command=dashboard.destroy, # 'dashboard' là cửa sổ tk.Tk() chính
        font=sidebar_font,
        bg="#c0392b", # Màu đỏ
        fg="white",
        relief="flat", 
        anchor="w",
        padx=20, 
        pady=10,
        activebackground="#e74c3c", # Màu đỏ nhạt hơn khi nhấn
        activeforeground="white"
    )
    btn_thoat.pack(side="bottom", fill="x", pady=10, padx=10)
    # --- Mở mặc định frame Kho ---
    if create_warehouse_frame:
        switch_content(create_warehouse_frame, "Quản lý Kho")

    dashboard.mainloop()
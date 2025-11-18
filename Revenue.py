# File: Revenue.py (Phiên bản TRANG TRÍ - ĐÃ SỬA CHO SIDEBAR)
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import font as tkFont # Import font
import pyodbc

# Import hàm kết nối
from SQL_connect import get_db_connection

# SỬA 1: Đổi tên hàm
def create_revenue_frame(parent_container):
    """Tạo và trả về một Frame Báo cáo Doanh thu."""

    # SỬA 2: Tạo Frame chính
    main_frame = tk.Frame(parent_container, bg="#f0f0f0")
    # Thêm padding ở .pack()
    main_frame.pack(expand=True, fill="both", padx=20, pady=20) 

    # --- Biến lưu trữ giá trị ---
    total_salary_var = tk.StringVar(value="Đang tải...")
    total_sales_var = tk.StringVar(value="Đang tải...")
    transport_cost_var = tk.StringVar(value="0")
    other_cost_var = tk.StringVar(value="0")
    contract_profit_var = tk.StringVar(value="0")
    net_revenue_var = tk.StringVar(value="Chưa tính")
    
    # --- Định nghĩa Font ---
    label_font = tkFont.Font(family="Segoe UI", size=12) 
    entry_font = tkFont.Font(family="Segoe UI", size=12) 
    total_font = tkFont.Font(family="Segoe UI", size=14, weight="bold")
    header_font = tkFont.Font(family="Segoe UI", size=16, weight="bold")
    button_font = tkFont.Font(family="Segoe UI", size=12, weight="bold")

    # --- (Hàm logic load_initial_revenue_data và calculate_net_revenue giữ nguyên) ---
    def load_initial_revenue_data():
        conn = get_db_connection()
        if conn is None: total_salary_var.set("Lỗi CSDL"); total_sales_var.set("Lỗi CSDL"); return
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT SUM(Luong) FROM NhanVien")
            result_salary = cursor.fetchone()
            total_salary = result_salary[0] if result_salary and result_salary[0] is not None else 0
            total_salary_var.set(f"{total_salary:,.0f} VND")
            cursor.execute("SELECT SUM(TongTien) FROM HoaDon")
            result_sales = cursor.fetchone()
            total_sales = result_sales[0] if result_sales and result_sales[0] is not None else 0
            total_sales_var.set(f"{total_sales:,.0f} VND")
        except pyodbc.Error as e: messagebox.showerror("Lỗi CSDL", f"Lỗi tải dữ liệu:\n{e}"); total_salary_var.set("Lỗi"); total_sales_var.set("Lỗi")
        except Exception as e: messagebox.showerror("Lỗi", f"Lỗi không xác định:\n{e}"); total_salary_var.set("Lỗi"); total_sales_var.set("Lỗi")
        finally:
            if conn: conn.close()

    def calculate_net_revenue():
        try:
            salary_str = total_salary_var.get().replace(' VND', '').replace(',', '')
            sales_str = total_sales_var.get().replace(' VND', '').replace(',', '')
            transport_cost_str = transport_cost_var.get().replace(',', '')
            other_cost_str = other_cost_var.get().replace(',', '')
            contract_profit_str = contract_profit_var.get().replace(',', '')
            total_salary_val = int(salary_str) if salary_str.isdigit() else 0
            total_sales_val = int(sales_str) if sales_str.isdigit() else 0
            if not transport_cost_str.isdigit(): messagebox.showerror("Lỗi nhập liệu", "Chi phí vận chuyển phải là số."); return
            if not other_cost_str.isdigit(): messagebox.showerror("Lỗi nhập liệu", "Chi phí phát sinh khác phải là số."); return
            if not contract_profit_str.isdigit(): messagebox.showerror("Lỗi nhập liệu", "Lợi nhuận hợp đồng phải là số."); return
            transport_cost_val = int(transport_cost_str)
            other_cost_val = int(other_cost_str)
            contract_profit_val = int(contract_profit_str)
            total_income = total_sales_val + contract_profit_val
            total_expenses = total_salary_val + transport_cost_val + other_cost_val
            net_revenue = total_income - total_expenses
            net_revenue_var.set(f"{net_revenue:,.0f} VND")
        except Exception as e: messagebox.showerror("Lỗi", f"Lỗi không xác định: {e}"); net_revenue_var.set("Lỗi")

    # --- GIAO DIỆN (Gắn vào main_frame) ---
    tk.Label(main_frame, text="BÁO CÁO DOANH THU", 
              font=header_font, bg="#f0f0f0", foreground="#00529B").pack(pady=(0, 20), fill="x")

    form_frame = tk.Frame(main_frame, bg="#f0f0f0")
    form_frame.pack(fill="x")
    form_frame.columnconfigure(1, weight=1)

    row_idx = 0
    def create_report_row(row_label_text, row_var, row_color):
        nonlocal row_idx
        label = tk.Label(form_frame, text=row_label_text, font=label_font, bg="#f0f0f0", anchor="w")
        label.grid(row=row_idx, column=0, sticky="w", pady=5, padx=5)
        data_label = tk.Label(form_frame, textvariable=row_var, font=label_font, bg="#f0f0f0", fg=row_color, anchor="e")
        data_label.grid(row=row_idx, column=1, sticky="ew", pady=5, padx=5)
        row_idx += 1
    def create_report_entry_row(row_label_text, row_var):
        nonlocal row_idx
        label = tk.Label(form_frame, text=row_label_text, font=label_font, bg="#f0f0f0", anchor="w")
        label.grid(row=row_idx, column=0, sticky="w", pady=5, padx=5)
        entry = tk.Entry(form_frame, textvariable=row_var, font=entry_font, justify="right",
                         relief="solid", bd=1) 
        entry.grid(row=row_idx, column=1, sticky="ew", pady=5, padx=5)
        row_idx += 1

    create_report_row("Tổng lương nhân viên:", total_salary_var, "blue")
    create_report_row("Tổng tiền bán VL:", total_sales_var, "green")
    create_report_entry_row("Lợi nhuận hợp đồng CT (VND):", contract_profit_var)
    create_report_entry_row("Chi phí vận chuyển (VND):", transport_cost_var)
    create_report_entry_row("Chi phí phát sinh khác (VND):", other_cost_var)
    
    tk.Button(main_frame, text="Tính Doanh Thu Cuối Cùng", command=calculate_net_revenue, 
              font=button_font, bg="#0078D4", fg="white", relief="flat", pady=5).pack(pady=20)

    result_frame = tk.Frame(main_frame, bg="#f0f0f0")
    result_frame.pack(fill="x", pady=(10, 0))
    result_frame.columnconfigure(1, weight=1)
    tk.Label(result_frame, text="Doanh thu cuối cùng:", font=total_font, bg="#f0f0f0", anchor="w").grid(row=0, column=0, sticky="w", padx=5)
    tk.Label(result_frame, textvariable=net_revenue_var, font=total_font, bg="#f0f0f0", foreground="red", anchor="e").grid(row=0, column=1, sticky="ew", padx=5)

    # --- Tải dữ liệu ban đầu ---
    load_initial_revenue_data()
    
    # === SỬA 3: Xóa mainloop và protocol ===

    # === SỬA 4: Trả về main_frame ===
    return main_frame
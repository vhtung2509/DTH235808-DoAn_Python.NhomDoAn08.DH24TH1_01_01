# File: ManagerEmployee.py (Phiên bản TRANG TRÍ - ĐÃ SỬA CHO SIDEBAR)
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import font as tkFont # Import font
import pyodbc
from datetime import datetime

# Import hàm kết nối
from SQL_connect import get_db_connection

# SỬA 1: Đổi tên hàm và tham số
def create_employee_frame(parent_container):
    """Hàm này tạo và trả về một Frame quản lý nhân viên."""

    current_mode = None
    _selected_treeview_item_id = None

    # SỬA 2: Tạo Frame chính, không tạo Toplevel/Tk
    # Tất cả widget sẽ nằm trong 'main_frame' này
    main_frame = ttk.Frame(parent_container, padding=10)
    
    phai_var = tk.StringVar()

    # --- Style (Đã thêm) ---
    style = ttk.Style(); style.theme_use("clam")
    btn_font = ("Segoe UI", 10, "bold"); header_font = ("Segoe UI", 10, "bold"); default_font = ("Segoe UI", 10)
    style.configure("Green.TButton", font=btn_font, padding=(10, 5), background="MediumSeaGreen", foreground="white")
    style.map("Green.TButton", background=[('active', 'DarkSeaGreen'), ('disabled', '#9E9E9E')], foreground=[('active', 'white'), ('disabled', '#F5F5F5')])
    
    # Cấu hình style cho Frame chính (nền #f0f0f0)
    style.configure("Main.TFrame", background="#f0f0f0")
    main_frame.configure(style="Main.TFrame")
    
    style.configure("TLabel", font=default_font, background="#f0f0f0")
    style.configure("TEntry", font=default_font, padding=3, fieldbackground="white")
    style.configure("TCombobox", font=default_font, padding=5); style.map("TCombobox", fieldbackground=[('readonly', 'white')])
    style.configure("TLabelframe", font=header_font, background="#f0f0f0"); style.configure("TLabelframe.Label", font=header_font, background="#f0f0f0")
    style.configure("Treeview.Heading", font=header_font, padding=5); style.configure("Treeview", font=default_font, rowheight=27)
    style.configure("TRadiobutton", font=default_font, background="#f0f0f0")

    # --- Functions (Tất cả hàm logic giữ nguyên) ---
    def clear_form(reset_selection=True):
        nonlocal current_mode, _selected_treeview_item_id
        ma_nv_entry.config(state="normal")
        ma_nv_entry.delete(0, "end"); ho_lot_entry.delete(0, "end"); ten_entry.delete(0, "end")
        ngay_sinh_entry.delete(0, "end"); bo_phan_combo.set(""); phai_var.set(""); luong_entry.delete(0, "end")
        current_mode = None
        if reset_selection:
             _selected_treeview_item_id = None
             if tree.selection(): tree.selection_remove(tree.selection())
        status_label.config(text="Sẵn sàng."); btn_them.config(state="normal"); btn_sua.config(state="disabled")
        btn_xoa.config(state="disabled"); btn_luu.config(state="disabled")

    def on_item_select(event):
        nonlocal _selected_treeview_item_id, current_mode
        selected_items = tree.selection()
        if not selected_items:
             _selected_treeview_item_id = None
             if current_mode not in ['them', 'sua']: clear_form(reset_selection=False)
             return
        _selected_treeview_item_id = selected_items[0]
        values = tree.item(_selected_treeview_item_id, 'values')
        if len(values) < 7: messagebox.showerror("Lỗi dữ liệu", "Dữ liệu dòng chọn không đầy đủ."); return
        if current_mode not in ['them', 'sua']:
            clear_form(reset_selection=False)
            ma_nv_entry.insert(0, values[0]); ho_lot_entry.insert(0, values[1]); ten_entry.insert(0, values[2])
            phai_var.set(values[3]); ngay_sinh_entry.insert(0, values[4]); bo_phan_combo.set(values[5])
            luong_str = str(values[6]).replace(',', ''); luong_entry.insert(0, luong_str)
            ma_nv_entry.config(state="disabled"); btn_them.config(state="disabled"); btn_sua.config(state="normal")
            btn_xoa.config(state="normal"); btn_luu.config(state="disabled")
            status_label.config(text=f"Đã chọn NV: {values[0]}. Nhấn 'Sửa' hoặc 'Xóa'."); current_mode = None

    def set_mode(mode):
        nonlocal current_mode, _selected_treeview_item_id
        if mode == 'them':
            clear_form(reset_selection=True)
            ma_nv_entry.config(state="normal")
            status_label.config(text="Chế độ THÊM. Nhập thông tin và bấm LƯU.")
            current_mode = mode
        elif mode == 'sua':
            if not _selected_treeview_item_id:
                 messagebox.showwarning("Chưa chọn", "Vui lòng chọn nhân viên cần sửa."); return
            current_mode = mode
            ma_nv_entry.config(state="disabled")
            status_label.config(text="Chế độ SỬA. Thay đổi thông tin và bấm LƯU.")
        if current_mode:
            btn_luu.config(state="normal"); btn_them.config(state="disabled")
            btn_sua.config(state="disabled"); btn_xoa.config(state="disabled")

    def validate_and_save():
        nonlocal _selected_treeview_item_id
        ma_nv_entry_value = ma_nv_entry.get().strip()
        ma_nv_to_use = _selected_treeview_item_id if current_mode == 'sua' else ma_nv_entry_value
        ho_lot=ho_lot_entry.get().strip(); ten=ten_entry.get().strip(); phai=phai_var.get().strip()
        ngay_sinh_str=ngay_sinh_entry.get().strip(); bo_phan=bo_phan_combo.get().strip(); luong_str=luong_entry.get().strip()
        if current_mode == 'them' and not ma_nv_to_use: messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập Mã NV."); return
        if not all([ho_lot, ten, phai, ngay_sinh_str, bo_phan, luong_str]): messagebox.showwarning("Thiếu thông tin", "Vui lòng điền đầy đủ."); return
        try: ngay_sinh_dt = datetime.strptime(ngay_sinh_str, '%d/%m/%Y')
        except ValueError: messagebox.showerror("Lỗi định dạng", "Ngày sinh không hợp lệ (DD/MM/YYYY)."); return
        try:
            luong = int(luong_str)
            if luong < 0: raise ValueError
        except ValueError: messagebox.showerror("Lỗi định dạng", "Lương phải là số nguyên dương."); return
        conn = get_db_connection()
        if conn is None: return
        try:
            cursor = conn.cursor()
            if current_mode == 'them':
                cursor.execute("SELECT MaNV FROM NhanVien WHERE MaNV = ?", ma_nv_to_use)
                if cursor.fetchone(): messagebox.showerror("Lỗi trùng lặp", f"Mã nhân viên '{ma_nv_to_use}' đã tồn tại."); conn.close(); return
                sql = "INSERT INTO NhanVien (MaNV, HoLot, TenNV, Phai, NgaySinh, BoPhan, Luong) VALUES (?, ?, ?, ?, ?, ?, ?)"
                cursor.execute(sql, (ma_nv_to_use, ho_lot, ten, phai, ngay_sinh_dt, bo_phan, luong))
                status_label.config(text=f"Đã thêm mới nhân viên {ma_nv_to_use}.")
            elif current_mode == 'sua':
                if not _selected_treeview_item_id: messagebox.showerror("Lỗi Logic", "Không xác định mã NV cần sửa."); conn.close(); return
                sql = "UPDATE NhanVien SET HoLot = ?, TenNV = ?, Phai = ?, NgaySinh = ?, BoPhan = ?, Luong = ? WHERE MaNV = ?"
                cursor.execute(sql, (ho_lot, ten, phai, ngay_sinh_dt, bo_phan, luong, _selected_treeview_item_id))
                status_label.config(text=f"Đã cập nhật nhân viên {_selected_treeview_item_id}.")
            else: messagebox.showerror("Lỗi Logic", f"Trạng thái không hợp lệ ('{current_mode}').")
            load_data_to_treeview(); clear_form(reset_selection=True)
        except pyodbc.Error as e: messagebox.showerror("Lỗi CSDL", f"Lỗi SQL khi lưu: {e}")
        except Exception as e: messagebox.showerror("Lỗi Python", f"Lỗi khi lưu:\n{e}")
        finally:
            if conn: conn.close()

    def delete_employee():
        nonlocal _selected_treeview_item_id
        ma_nv_to_delete = _selected_treeview_item_id
        if not ma_nv_to_delete: messagebox.showwarning("Chưa chọn", "Vui lòng chọn nhân viên cần xóa."); return
        confirm = messagebox.askyesno("Xác nhận Xóa", f"Bạn có chắc muốn xóa nhân viên {ma_nv_to_delete} không?")
        if confirm:
            conn = get_db_connection()
            if conn is None: return
            try:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM TaiKhoan WHERE MaNV = ?", ma_nv_to_delete)
                cursor.execute("DELETE FROM NhanVien WHERE MaNV = ?", ma_nv_to_delete)
                messagebox.showinfo("Thành công", f"Đã xóa nhân viên {ma_nv_to_delete}.")
                load_data_to_treeview(); clear_form(reset_selection=True)
            except pyodbc.Error as e:
                error_code, error_message = e.args
                if "FK__HoaDon__MaNV" in error_message or ("REFERENCE constraint" in error_message and "HoaDon" in error_message):
                     messagebox.showerror("Lỗi Xóa (Khóa Ngoại)", f"Không thể xóa {ma_nv_to_delete}.\nNhân viên này đã lập hóa đơn.")
                else: messagebox.showerror("Lỗi CSDL", f"Lỗi khi xóa:\n{error_message}")
            except Exception as e: messagebox.showerror("Lỗi Python", f"Lỗi khi xóa:\n{e}")
            finally:
                if conn: conn.close()

    def load_data_to_treeview(search_term=None):
        tree.delete(*tree.get_children())
        conn = get_db_connection()
        if conn is None: status_label.config(text="Lỗi kết nối CSDL."); return
        try:
            cursor = conn.cursor()
            if search_term:
                sql_query = "SELECT MaNV, HoLot, TenNV, Phai, NgaySinh, BoPhan, Luong FROM NhanVien WHERE MaNV LIKE ? ORDER BY MaNV"
                params = (f"%{search_term}%",)
            else:
                sql_query = "SELECT MaNV, HoLot, TenNV, Phai, NgaySinh, BoPhan, Luong FROM NhanVien ORDER BY MaNV"
                params = ()
            cursor.execute(sql_query, params)
            rows = cursor.fetchall()
            for row in rows:
                ngay_sinh_str = ""
                if row.NgaySinh:
                    try: ngay_sinh_str = row.NgaySinh.strftime('%d/%m/%Y')
                    except AttributeError:
                        try:
                            date_obj = datetime.strptime(str(row.NgaySinh).split()[0], '%Y-%m-%d')
                            ngay_sinh_str = date_obj.strftime('%d/%m/%Y')
                        except: ngay_sinh_str = str(row.NgaySinh)
                    except: ngay_sinh_str = str(row.NgaySinh)
                luong_formatted = f"{row.Luong:,}" if row.Luong is not None else ""
                tree.insert('', tk.END, iid=row.MaNV, values=(row.MaNV, row.HoLot, row.TenNV, row.Phai, ngay_sinh_str, row.BoPhan, luong_formatted))
            if search_term: status_label.config(text=f"Đã tìm thấy {len(rows)} nhân viên.", foreground="blue")
            else: status_label.config(text=f"Đã tải {len(rows)} nhân viên.", foreground="green")
        except pyodbc.Error as e: messagebox.showerror("Lỗi Truy Vấn", f"Lỗi tải dữ liệu:\n{e}"); status_label.config(text="Lỗi tải dữ liệu.")
        except Exception as e: messagebox.showerror("Lỗi Python", f"Lỗi xử lý dữ liệu:\n{e}"); print(f"!!! LỖI PYTHON KHÁC KHI TẢI: {e}")
        finally:
            if conn: conn.close()

    # SỬA 3: Xóa hàm confirm_exit
    # def confirm_exit(): ...

    def perform_search_nv():
        term = search_entry_nv.get().strip()
        if not term: messagebox.showinfo("Thông báo", "Vui lòng nhập Mã Nhân Viên để tìm."); return
        load_data_to_treeview(search_term=term)

    def reset_view_nv():
        search_entry_nv.delete(0, "end")
        load_data_to_treeview() 

    # --- SETUP GIAO DIỆN (Gắn vào main_frame) ---
    form_frame = ttk.LabelFrame(main_frame, text="Thông tin Nhân viên", padding=(20, 10)); form_frame.pack(padx=20, pady=10, fill="x")
    def create_form_row(parent, label_text, row):
        ttk.Label(parent, text=label_text, width=15, anchor="w").grid(row=row, column=0, sticky="w", pady=5, padx=5)
        entry = ttk.Entry(parent, width=30); entry.grid(row=row, column=1, sticky="ew", pady=5, padx=5); return entry
    ma_nv_entry = create_form_row(form_frame, "Mã NV:", 0); ho_lot_entry = create_form_row(form_frame, "Họ Lót:", 1); ten_entry = create_form_row(form_frame, "Tên:", 2)
    ttk.Label(form_frame, text="Phái:", width=15, anchor="w").grid(row=3, column=0, sticky="w", pady=5, padx=5); phai_frame = ttk.Frame(form_frame); phai_frame.grid(row=3, column=1, sticky="w", pady=5, padx=5)
    ttk.Radiobutton(phai_frame, text="Nam", variable=phai_var, value="Nam").pack(side=tk.LEFT, padx=10); ttk.Radiobutton(phai_frame, text="Nữ", variable=phai_var, value="Nữ").pack(side=tk.LEFT, padx=10)
    ngay_sinh_entry = create_form_row(form_frame, "Ngày sinh (DD/MM/YYYY):", 4)
    ttk.Label(form_frame, text="Bộ phận:", width=15, anchor="w").grid(row=5, column=0, sticky="w", pady=5, padx=5)
    bo_phan_combo = ttk.Combobox(form_frame, width=28, state="readonly", values=["Quản lý", "Thu ngân", "Bán hàng", "Giao nhận", "Kho", "Công trình"]); bo_phan_combo.grid(row=5, column=1, sticky="ew", pady=5, padx=5)
    luong_entry = create_form_row(form_frame, "Lương:", 6)
    
    button_frame = ttk.Frame(main_frame, padding=(20, 10)); button_frame.pack(padx=20, pady=5, fill="x")
    btn_them = ttk.Button(button_frame, text="Thêm", command=lambda: set_mode('them'), width=10, style="Green.TButton"); btn_them.pack(side=tk.LEFT, padx=5)
    btn_sua = ttk.Button(button_frame, text="Sửa", command=lambda: set_mode('sua'), state="disabled", width=10, style="Green.TButton"); btn_sua.pack(side=tk.LEFT, padx=5)
    btn_xoa = ttk.Button(button_frame, text="Xóa", command=delete_employee, state="disabled", width=10, style="Green.TButton"); btn_xoa.pack(side=tk.LEFT, padx=5)
    btn_luu = ttk.Button(button_frame, text="LƯU", command=validate_and_save, state="disabled", width=10, style="Green.TButton"); btn_luu.pack(side=tk.LEFT, padx=50)
    btn_huy = ttk.Button(button_frame, text="Hủy/Mới", command=lambda: clear_form(reset_selection=True), width=10, style="Green.TButton"); btn_huy.pack(side=tk.LEFT, padx=5)
    
    list_title_font = tkFont.Font(family="Segoe UI", size=14, weight="bold")
    list_title_label = tk.Label(main_frame, text="Danh Sách Nhân Viên", font=list_title_font, bg="#f0f0f0", fg="#00529B")
    list_title_label.pack(pady=(15, 0))

    list_frame = ttk.Frame(main_frame, padding=(20, 10)) 
    list_frame.pack(padx=20, pady=(0, 10), fill="both", expand=True)

    # Khung Tìm kiếm
    search_frame_nv = ttk.Frame(list_frame)
    search_frame_nv.pack(fill="x", padx=0, pady=(0, 10))
    search_label_nv = ttk.Label(search_frame_nv, text="Tìm theo Mã NV:")
    search_label_nv.pack(side="left", padx=(0, 5))
    search_entry_nv = ttk.Entry(search_frame_nv)
    search_entry_nv.pack(side="left", fill="x", expand=True, padx=5)
    search_button_nv = ttk.Button(search_frame_nv, text="Tìm", command=perform_search_nv, style="Green.TButton")
    search_button_nv.pack(side="left", padx=5)
    reset_button_nv = ttk.Button(search_frame_nv, text="Tải lại DS", command=reset_view_nv, style="Green.TButton")
    reset_button_nv.pack(side="left", padx=5)
    
    # Bảng Treeview
    tree = ttk.Treeview(list_frame, columns=("ma_nv", "ho_lot", "ten", "phai", "ngay_sinh", "bo_phan", "luong"), show="headings", height=10)
    tree.heading("ma_nv", text="Mã NV"); tree.heading("ho_lot", text="Họ Lót"); tree.heading("ten", text="Tên"); tree.heading("phai", text="Phái")
    tree.heading("ngay_sinh", text="Ngày sinh"); tree.heading("bo_phan", text="Bộ phận"); tree.heading("luong", text="Lương (VND)")
    tree.column("ma_nv", width=80, anchor="center"); tree.column("ho_lot", width=180); tree.column("ten", width=80); tree.column("phai", width=50, anchor="center")
    tree.column("ngay_sinh", width=100, anchor="center"); tree.column("bo_phan", width=130); tree.column("luong", width=100, anchor="e")
    scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=tree.yview); tree.configure(yscrollcommand=scrollbar.set); scrollbar.pack(side="right", fill="y"); tree.pack(fill="both", expand=True)
    tree.bind('<<TreeviewSelect>>', on_item_select)
    
    status_label = ttk.Label(main_frame, text="Đang tải dữ liệu...", relief="sunken", anchor="w", padding=5); 
    status_label.pack(side=tk.BOTTOM, fill=tk.X)

    load_data_to_treeview() # Tải dữ liệu ban đầu
    clear_form() # Đặt trạng thái ban đầu

    # === SỬA 4: Xóa mainloop và protocol ===
    
    # === SỬA 5: Trả về main_frame ===
    return main_frame
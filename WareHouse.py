# File: WareHouse.py (Phiên bản TRANG TRÍ - ĐÃ SỬA CHO SIDEBAR)
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import font as tkFont
import pyodbc

# Import hàm kết nối
from SQL_connect import get_db_connection

# SỬA 1: Đổi tên hàm và tham số
def create_warehouse_frame(parent_container):
    """
    Hàm này TẠO VÀ TRẢ VỀ một Frame 'Quản lý Vật Liệu Xây Dựng'.
    """

    current_mode = None
    selected_item = None
    
    # SỬA 2: Tạo Frame chính, không tạo Toplevel/Tk
    # Tất cả widget sẽ nằm trong 'main_frame' này
    main_frame = ttk.Frame(parent_container, padding=10)
    
    loai_vt_var = tk.StringVar()

    # --- Style ---
    style = ttk.Style()
    style.theme_use("clam")
    default_font = ("Segoe UI", 10); label_font = ("Segoe UI", 10); title_font = ("Segoe UI", 16, "bold")
    btn_font = ("Segoe UI", 10, "bold"); header_font = ("Segoe UI", 10, "bold")
    style.configure("Green.TButton", font=btn_font, padding=(10, 5), background="MediumSeaGreen", foreground="white")
    style.map("Green.TButton", background=[('active', 'DarkSeaGreen'), ('disabled', 'grey')], foreground=[('active', 'white'), ('disabled', 'white')])
    
    style.configure("Main.TFrame", background="#f0f0f0")
    main_frame.configure(style="Main.TFrame")
    
    style.configure("TLabel", font=label_font, background="#f0f0f0"); style.configure("TEntry", font=default_font, padding=3, fieldbackground="white")
    style.configure("TCombobox", font=default_font); style.map("TCombobox", fieldbackground=[('readonly', 'white')])
    style.configure("TLabelframe", font=header_font, background="#f0f0f0"); style.configure("TLabelframe.Label", font=header_font, background="#f0f0f0")
    style.configure("Treeview.Heading", font=header_font); style.configure("Treeview", font=default_font, rowheight=25); style.configure("TRadiobutton", font=default_font, background="#f0f0f0")

    DVT_MAP = {
        "Xi măng": "Bao", "Cát": "Khối (m3)", "Đá": "Khối (m3)",
        "Gạch": "Viên", "Sắt thép": "kg", "Sơn": "Hộp",
        "Thiết bị vệ sinh": "Cái", "Gỗ": "Cây"
    }

    # --- CÁC HÀM LOGIC (Giữ nguyên) ---
    def on_loai_vat_tu_selected(event=None):
        selected_loai = loai_vt_var.get(); default_dvt = DVT_MAP.get(selected_loai, ""); dvt_combo.set(default_dvt)
    
    def clear_form(reset_selection=True):
        nonlocal current_mode, selected_item
        ma_vt_entry.config(state="normal"); ma_vt_entry.delete(0, "end"); ten_vt_entry.delete(0, "end")
        so_luong_entry.delete(0, "end"); gia_nhap_entry.delete(0, "end"); gia_ban_entry.delete(0, "end")
        loai_vt_var.set(""); dvt_combo.set("")
        if reset_selection:
            for item_ in tree.selection(): tree.selection_remove(item_)
            selected_item = None
        current_mode = None; ma_vt_entry.focus(); status_label.config(text="Sẵn sàng.")
    
    def load_data_from_db(search_term=None):
        tree.delete(*tree.get_children())
        conn = get_db_connection()
        if not conn: status_label.config(text="Lỗi kết nối CSDL.", foreground="red"); return
        try:
            cursor = conn.cursor()
            if search_term:
                sql_query = "SELECT MaVatTu, TenVatTu, DonViTinh, LoaiVatTu, SoLuongTon, GiaNhap, GiaBan FROM VatTu WHERE MaVatTu LIKE ? ORDER BY MaVatTu"
                params = (f"%{search_term}%",)
            else:
                sql_query = "SELECT MaVatTu, TenVatTu, DonViTinh, LoaiVatTu, SoLuongTon, GiaNhap, GiaBan FROM VatTu ORDER BY MaVatTu"
                params = ()
            cursor.execute(sql_query, params)
            rows = cursor.fetchall()
            for row in rows:
                ma_vt = row.MaVatTu
                gia_nhap_formatted = f"{int(row.GiaNhap):,.0f}" if row.GiaNhap is not None else "0"
                gia_ban_formatted = f"{int(row.GiaBan):,.0f}" if row.GiaBan is not None else "0"
                tree.insert("", "end", iid=ma_vt, values=(
                    row.MaVatTu, row.TenVatTu, row.DonViTinh, row.LoaiVatTu, 
                    int(row.SoLuongTon) if row.SoLuongTon is not None else 0,
                    gia_nhap_formatted, gia_ban_formatted ))
            if search_term: status_label.config(text=f"Đã tìm thấy {len(rows)} vật tư khớp.", foreground="blue")
            else: status_label.config(text=f"Đã tải {len(rows)} vật tư.", foreground="green")
        except pyodbc.Error as ex: messagebox.showerror("Lỗi Đọc CSDL", f"Lỗi: {ex}"); status_label.config(text="Lỗi tải dữ liệu.", foreground="red")
        except Exception as e: messagebox.showerror("Lỗi", f"Lỗi không xác định: {e}")
        finally:
            if conn: conn.close()

    def perform_search():
        term = search_entry.get().strip()
        if not term: messagebox.showinfo("Thông báo", "Vui lòng nhập Mã Vật Tư để tìm."); return
        load_data_from_db(search_term=term)

    def reset_view():
        search_entry.delete(0, "end"); load_data_from_db() 
    
    def click_them():
        nonlocal current_mode; clear_form(reset_selection=True); current_mode = "new"
        ma_vt_entry.config(state="normal"); ma_vt_entry.focus(); status_label.config(text="Chế độ: Thêm Mới.", foreground="blue")
    
    def click_sua():
        nonlocal current_mode, selected_item
        try: selected_item_id = tree.selection()[0]
        except IndexError: messagebox.showwarning("Chưa chọn", "Vui lòng chọn vật tư để sửa!"); return
        item_data = tree.item(selected_item_id, "values")
        if not item_data or len(item_data) < 7: messagebox.showerror("Lỗi Dữ Liệu", "Dữ liệu hàng không hợp lệ."); return
        clear_form(reset_selection=False); current_mode = "edit"; selected_item = selected_item_id
        ma_vt_entry.insert(0, item_data[0]); ma_vt_entry.config(state="disabled")
        ten_vt_entry.insert(0, item_data[1]); dvt_combo.set(item_data[2]); loai_vt_var.set(item_data[3])
        so_luong_str = str(item_data[4]).replace(',', ''); gia_nhap_str = str(item_data[5]).replace(',', ''); gia_ban_str = str(item_data[6]).replace(',', '')
        so_luong_entry.insert(0, so_luong_str); gia_nhap_entry.insert(0, gia_nhap_str); gia_ban_entry.insert(0, gia_ban_str)  
        ten_vt_entry.focus(); status_label.config(text=f"Chế độ: Sửa mã {item_data[0]}.", foreground="orange")
    
    def click_luu():
        nonlocal current_mode, selected_item
        ma_vt = ma_vt_entry.get().strip(); ten_vt = ten_vt_entry.get().strip(); dvt = dvt_combo.get().strip()
        loai_vt = loai_vt_var.get().strip(); so_luong_str = so_luong_entry.get().replace(",", "").strip()
        gia_nhap_str = gia_nhap_entry.get().replace(",", "").strip(); gia_ban_str = gia_ban_entry.get().replace(",", "").strip()
        if current_mode == "new" and not ma_vt: messagebox.showerror("Thiếu thông tin", "Vui lòng nhập Mã vật tư!"); return
        if not ten_vt or not dvt or not loai_vt or not so_luong_str or not gia_nhap_str or not gia_ban_str:
            messagebox.showerror("Thiếu thông tin", "Vui lòng nhập đầy đủ thông tin!"); return
        try:
            sl_ton = int(so_luong_str); gia_nhap = int(gia_nhap_str); gia_ban = int(gia_ban_str)
            if sl_ton < 0 or gia_nhap < 0 or gia_ban < 0: messagebox.showerror("Lỗi dữ liệu", "Số lượng và Giá không được âm!"); return
        except ValueError: messagebox.showerror("Lỗi dữ liệu", "Số lượng và Giá phải là số nguyên!"); return
        conn = get_db_connection();
        if not conn: return
        try:
            cursor = conn.cursor()
            if current_mode == "new":
                sql = "INSERT INTO VatTu (MaVatTu, TenVatTu, DonViTinh, LoaiVatTu, SoLuongTon, GiaNhap, GiaBan) VALUES (?, ?, ?, ?, ?, ?, ?)"
                cursor.execute(sql, ma_vt, ten_vt, dvt, loai_vt, sl_ton, gia_nhap, gia_ban)
                status_label.config(text=f"Đã thêm mới vật tư: {ma_vt}.", foreground="green")
            elif current_mode == "edit":
                if not selected_item: messagebox.showerror("Lỗi", "Không xác định vật tư cần sửa."); conn.close(); return
                sql = "UPDATE VatTu SET TenVatTu=?, DonViTinh=?, LoaiVatTu=?, SoLuongTon=?, GiaNhap=?, GiaBan=? WHERE MaVatTu=?"
                cursor.execute(sql, ten_vt, dvt, loai_vt, sl_ton, gia_nhap, gia_ban, selected_item)
                status_label.config(text=f"Đã cập nhật vật tư: {selected_item}.", foreground="green")
            else: messagebox.showwarning("Chưa rõ", "Vui lòng nhấn 'Thêm Mới' hoặc 'Sửa' trước."); conn.close(); return
            clear_form(reset_selection=True); load_data_from_db()
        except pyodbc.IntegrityError as e:
             if "PRIMARY KEY constraint" in str(e): messagebox.showerror("Lỗi Trùng Lặp", f"Mã vật tư '{ma_vt}' đã tồn tại!")
             else: messagebox.showerror("Lỗi CSDL", f"Lỗi ràng buộc dữ liệu:\n{e}")
        except pyodbc.Error as ex: messagebox.showerror("Lỗi CSDL", f"Lỗi khi lưu dữ liệu:\n{ex}")
        except Exception as e: messagebox.showerror("Lỗi", f"Lỗi không xác định khi lưu:\n{e}")
        finally:
            if conn: conn.close()
    
    def click_xoa():
        try: selected_item_id_to_delete = tree.selection()[0]
        except IndexError: messagebox.showwarning("Chưa chọn", "Vui lòng chọn vật tư để xóa!"); return
        item_data = tree.item(selected_item_id_to_delete, "values")
        if messagebox.askyesno("Xác nhận xóa", f"Bạn có chắc muốn xóa vật tư '{item_data[1]}'?"):
            conn = get_db_connection();
            if not conn: return
            try:
                cursor = conn.cursor(); sql = "DELETE FROM VatTu WHERE MaVatTu = ?"
                cursor.execute(sql, selected_item_id_to_delete)
                status_label.config(text=f"Đã xóa vật tư: {item_data[0]}.", foreground="green")
                clear_form(reset_selection=True); load_data_from_db()
            except pyodbc.Error as ex:
                if "REFERENCE constraint" in str(ex): messagebox.showerror("Lỗi Xóa", f"Không thể xóa vật tư '{item_data[0]}'.\nVật tư này đã được sử dụng trong hóa đơn.\nLỗi: {ex}")
                else: messagebox.showerror("Lỗi CSDL", f"Lỗi khi xóa vật tư:\n{ex}")
            except Exception as e: messagebox.showerror("Lỗi", f"Lỗi không xác định khi xóa:\n{e}")
            finally:
                if conn: conn.close()
    
    def on_item_select_warehouse(event):
        nonlocal current_mode, selected_item
        try:
            selected_id = tree.selection()[0]; item_data = tree.item(selected_id, "values")
            if not item_data or len(item_data) < 7: return
            if current_mode not in ['new', 'edit']:
                clear_form(reset_selection=False); ma_vt_entry.config(state="normal"); ma_vt_entry.insert(0, item_data[0])
                ma_vt_entry.config(state="disabled"); ten_vt_entry.insert(0, item_data[1]); dvt_combo.set(item_data[2])
                loai_vt_var.set(item_data[3]); so_luong_entry.insert(0, str(item_data[4]).replace(',', ''))
                gia_nhap_entry.insert(0, str(item_data[5]).replace(',', '')); gia_ban_entry.insert(0, str(item_data[6]).replace(',', ''))  
                selected_item = selected_id; status_label.config(text=f"Đã chọn: {item_data[1]}. Nhấn 'Sửa' hoặc 'Xóa'.", foreground="darkblue")
        except IndexError: pass
        except Exception as e: print(f"Lỗi: {e}"); clear_form(reset_selection=True)
    
    # --- GUI Setup (Gắn vào main_frame) ---
    title_label = tk.Label(main_frame, text="QUẢN LÝ KHO VẬT LIỆU XÂY DỰNG", font=title_font, bg="#f0f0f0", fg="#00529B"); title_label.pack(pady=(10, 20))
    input_frame = ttk.LabelFrame(main_frame, text="Thông tin vật tư", padding=(20, 10)); input_frame.pack(fill="x", padx=20, pady=5)
    input_frame.columnconfigure(1, weight=1); input_frame.columnconfigure(3, weight=1)
    loai_vt_frame = ttk.LabelFrame(input_frame, text="Loại vật tư"); loai_vt_frame.grid(row=0, column=0, columnspan=4, sticky="ew", padx=5, pady=10)
    loai_vt_options = ["Xi măng", "Cát", "Đá", "Gạch", "Sắt thép", "Sơn", "Thiết bị vệ sinh", "Gỗ"]
    for i, option in enumerate(loai_vt_options):
        rb = ttk.Radiobutton(loai_vt_frame, text=option, variable=loai_vt_var, value=option, command=on_loai_vat_tu_selected)
        rb.pack(side="left", padx=10, pady=5)
    ttk.Label(input_frame, text="Mã vật tư:").grid(row=1, column=0, sticky="w", padx=5, pady=5); ma_vt_entry = ttk.Entry(input_frame, width=20); ma_vt_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
    ttk.Label(input_frame, text="Số lượng tồn:").grid(row=1, column=2, sticky="w", padx=15, pady=5); so_luong_entry = ttk.Entry(input_frame, width=20); so_luong_entry.grid(row=1, column=3, sticky="ew", padx=5, pady=5)
    ttk.Label(input_frame, text="Tên vật tư:").grid(row=2, column=0, sticky="w", padx=5, pady=5); ten_vt_entry = ttk.Entry(input_frame, width=20); ten_vt_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
    ttk.Label(input_frame, text="Đơn vị tính:").grid(row=2, column=2, sticky="w", padx=15, pady=5); dvt_options = ["Bao", "Khối (m3)", "Tấn", "Cái", "Thanh", "Hộp", "Lít", "kg", "Viên", "Cây"]; dvt_combo = ttk.Combobox(input_frame, values=dvt_options, state="readonly", width=17); dvt_combo.grid(row=2, column=3, sticky="ew", padx=5, pady=5)
    ttk.Label(input_frame, text="Giá Nhập (VND):").grid(row=3, column=0, sticky="w", padx=5, pady=5); gia_nhap_entry = ttk.Entry(input_frame, width=20); gia_nhap_entry.grid(row=3, column=1, sticky="ew", padx=5, pady=5)
    ttk.Label(input_frame, text="Giá Bán (VND):").grid(row=3, column=2, sticky="w", padx=15, pady=5); gia_ban_entry = ttk.Entry(input_frame, width=20); gia_ban_entry.grid(row=3, column=3, sticky="ew", padx=5, pady=5)
    
    button_frame = ttk.Frame(main_frame, padding=(10, 10)); button_frame.pack(fill="x", padx=15)
    ttk.Button(button_frame, text="Thêm Mới", command=click_them, style="Green.TButton").pack(side="left", padx=5, expand=True, fill='x')
    ttk.Button(button_frame, text="Lưu", command=click_luu, style="Green.TButton").pack(side="left", padx=5, expand=True, fill='x')
    ttk.Button(button_frame, text="Sửa", command=click_sua, style="Green.TButton").pack(side="left", padx=5, expand=True, fill='x')
    ttk.Button(button_frame, text="Hủy", command=lambda: clear_form(reset_selection=True), style="Green.TButton").pack(side="left", padx=5, expand=True, fill='x')
    ttk.Button(button_frame, text="Xóa", command=click_xoa, style="Green.TButton").pack(side="left", padx=5, expand=True, fill='x')
    # SỬA 3: Xóa nút Thoát
    
    list_frame = ttk.LabelFrame(main_frame, text="Danh sách vật tư", padding=(10, 10)); list_frame.pack(fill="both", expand=True, padx=20, pady=(10, 20))
    
    search_frame = ttk.Frame(list_frame)
    search_frame.pack(fill="x", padx=0, pady=(0, 10)) 
    search_label = ttk.Label(search_frame, text="Tìm theo Mã VT:")
    search_label.pack(side="left", padx=(0, 5))
    search_entry = ttk.Entry(search_frame)
    search_entry.pack(side="left", fill="x", expand=True, padx=5)
    search_button = ttk.Button(search_frame, text="Tìm", command=perform_search, style="Green.TButton")
    search_button.pack(side="left", padx=5)
    reset_button = ttk.Button(search_frame, text="Tải lại DS", command=reset_view, style="Green.TButton")
    reset_button.pack(side="left", padx=5)
    
    columns = ("ma_vt", "ten_vt", "dvt", "loai_vt", "so_luong", "gia_nhap", "gia_ban"); tree = ttk.Treeview(list_frame, columns=columns, show="headings")
    tree.heading("ma_vt", text="Mã vật tư"); tree.heading("ten_vt", text="Tên vật tư"); tree.heading("dvt", text="ĐVT"); tree.heading("loai_vt", text="Loại vật tư")
    tree.heading("so_luong", text="SL tồn"); tree.heading("gia_nhap", text="Giá Nhập (VND)"); tree.heading("gia_ban", text="Giá Bán (VND)")
    tree.column("ma_vt", width=80, anchor="center"); tree.column("ten_vt", width=180); tree.column("dvt", width=70, anchor="center"); tree.column("loai_vt", width=100)
    tree.column("so_luong", width=70, anchor="e"); tree.column("gia_nhap", width=100, anchor="e"); tree.column("gia_ban", width=100, anchor="e")
    scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=tree.yview); tree.configure(yscrollcommand=scrollbar.set); scrollbar.pack(side="right", fill="y"); tree.pack(fill="both", expand=True)
    tree.bind('<<TreeviewSelect>>', on_item_select_warehouse)
    
    status_label = ttk.Label(main_frame, text="Đang tải dữ liệu...", relief="sunken", anchor="w", padding=5); 
    status_label.pack(side="bottom", fill="x")

    load_data_from_db()

    # SỬA 4: Xóa mainloop và protocol
    
    # SỬA 5: Trả về main_frame
    return main_frame
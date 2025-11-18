# File: Transport_gui_with_logo.py
import tkinter as tk
from tkinter import ttk, messagebox
import pyodbc
from SQL_connect import get_db_connection
import os

def create_transport_frame(parent):
    current_mode = None
    selected_item = None

    main_frame = tk.Frame(parent, bg="#f0f4f8", padx=10, pady=10)

    # --- Variables ---
    fields = ["ma_vc", "ten_nv", "bo_phan", "phuong_tien", "chi_phi"]
    vars_ = {f: tk.StringVar() for f in fields}

    # --- Logo ---
    logo_path = os.path.join(os.path.dirname(__file__), "LogoVanChuyen.PNG")
    try:
        logo_img = tk.PhotoImage(file=logo_path)
        lbl_logo = tk.Label(main_frame, image=logo_img, bg="#f0f4f8")
        lbl_logo.image = logo_img  # giữ tham chiếu
        lbl_logo.pack(pady=10)
    except:
        lbl_logo = tk.Label(main_frame, text="QUẢN LÝ VẬN CHUYỂN", 
                            font=("Segoe UI", 20, "bold"), fg="#00529B", bg="#f0f4f8")
        lbl_logo.pack(pady=20)

    # --- Functions ---
    def clear_form(reset_selection=True):
        nonlocal current_mode, selected_item
        for var in vars_.values():
            var.set("")
        main_entries["ma_vc"].config(state="normal")
        if reset_selection:
            tree.selection_remove(tree.selection())
            selected_item = None
        current_mode = None
        main_entries["ma_vc"].focus()
        status_label.config(text="Sẵn sàng.", fg="#333")

    def load_data():
        tree.delete(*tree.get_children())
        conn = get_db_connection()
        if not conn:
            status_label.config(text="Lỗi kết nối CSDL.", fg="red")
            return
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT MaVC, TenNguoiVC, BoPhan, PhuongTien, ChiPhi FROM VanChuyen ORDER BY MaVC")
            for row in cursor.fetchall():
                chi_phi_fmt = f"{int(row.ChiPhi):,}" if row.ChiPhi else "0"
                bo_phan_val = row.BoPhan or ""
                tree.insert("", "end", iid=row.MaVC, values=(row.MaVC, row.TenNguoiVC, bo_phan_val, row.PhuongTien, chi_phi_fmt))
            status_label.config(text=f"Đã tải {len(tree.get_children())} vận chuyển.", fg="green")
        except pyodbc.Error as e:
            messagebox.showerror("Lỗi CSDL", e)
        finally:
            conn.close() if conn else None

    def save_data():
        nonlocal current_mode, selected_item
        ma_vc = vars_["ma_vc"].get().strip()
        ten_nv = vars_["ten_nv"].get().strip()
        bo_phan = vars_["bo_phan"].get().strip()
        phuong_tien = vars_["phuong_tien"].get().strip()
        chi_phi_str = vars_["chi_phi"].get().replace(",", "").strip()

        if current_mode == "new" and not ma_vc:
            messagebox.showerror("Thiếu thông tin", "Vui lòng nhập Mã vận chuyển!")
            return
        if not ten_nv or not phuong_tien or not chi_phi_str:
            messagebox.showerror("Thiếu thông tin", "Vui lòng nhập đầy đủ thông tin!")
            return

        try:
            chi_phi = int(chi_phi_str)
            if chi_phi < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Lỗi dữ liệu", "Chi phí phải là số nguyên không âm!")
            return

        conn = get_db_connection()
        if not conn:
            return
        try:
            cursor = conn.cursor()
            if current_mode == "new":
                cursor.execute("INSERT INTO VanChuyen (MaVC, TenNguoiVC, BoPhan, PhuongTien, ChiPhi) VALUES (?, ?, ?, ?, ?)",
                               ma_vc, ten_nv, bo_phan, phuong_tien, chi_phi)
                status_label.config(text=f"Đã thêm vận chuyển: {ma_vc}", fg="green")
            elif current_mode == "edit" and selected_item:
                cursor.execute("UPDATE VanChuyen SET TenNguoiVC=?, BoPhan=?, PhuongTien=?, ChiPhi=? WHERE MaVC=?",
                               ten_nv, bo_phan, phuong_tien, chi_phi, selected_item)
                status_label.config(text=f"Đã cập nhật: {selected_item}", fg="green")
            else:
                messagebox.showwarning("Chưa rõ", "Nhấn 'Thêm Mới' hoặc 'Sửa' trước!")
                return
            conn.commit()
            clear_form()
            load_data()
        except pyodbc.IntegrityError:
            messagebox.showerror("Lỗi trùng lặp", f"Mã vận chuyển '{ma_vc}' đã tồn tại!")
        except pyodbc.Error as e:
            messagebox.showerror("Lỗi CSDL", e)
        finally:
            conn.close()

    def delete_data():
        nonlocal selected_item
        try:
            selected_item_id = tree.selection()[0]
        except IndexError:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn vận chuyển để xóa!")
            return
        values = tree.item(selected_item_id, "values")
        if messagebox.askyesno("Xác nhận xóa", f"Bạn có chắc muốn xóa '{values[1]}'?"):
            conn = get_db_connection()
            if not conn:
                return
            try:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM VanChuyen WHERE MaVC=?", selected_item_id)
                conn.commit()
                status_label.config(text=f"Đã xóa: {values[1]}", fg="green")
                clear_form()
                load_data()
            except pyodbc.Error as e:
                messagebox.showerror("Lỗi CSDL", e)
            finally:
                conn.close()

    def on_select(event):
        nonlocal selected_item, current_mode
        try:
            selected_id = tree.selection()[0]
            values = tree.item(selected_id, "values")
            if current_mode not in ["new", "edit"]:
                clear_form(reset_selection=False)
                for i, f in enumerate(fields):
                    vars_[f].set(values[i])
                main_entries["ma_vc"].config(state="disabled")
                selected_item = selected_id
                status_label.config(text=f"Đã chọn: {values[1]}", fg="#00529B")
        except IndexError:
            pass

    def set_mode(mode):
        nonlocal current_mode
        clear_form()
        current_mode = mode
        if mode == "edit" and selected_item:
            main_entries["ma_vc"].config(state="disabled")
        status_label.config(text=f"Chế độ: {'Thêm Mới' if mode=='new' else 'Sửa'}", fg="#00529B")

    # --- Input Frame ---
    input_frame = tk.LabelFrame(main_frame, text="Thông tin vận chuyển", bg="#e6eefc", font=("Segoe UI", 12, "bold"), padx=10, pady=10)
    input_frame.pack(fill="x", padx=20, pady=10)
    input_frame.columnconfigure((1,3), weight=1)

    labels = ["Mã VC:", "Tên NV:", "Bộ Phận:", "Phương tiện:", "Chi phí:"]
    main_entries = {}
    for idx, (label_text, f) in enumerate(zip(labels, fields)):
        row, col = divmod(idx, 2)
        tk.Label(input_frame, text=label_text, bg="#e6eefc", font=("Segoe UI", 10)).grid(row=row, column=col*2, sticky="w", padx=5, pady=5)
        entry = ttk.Entry(input_frame, textvariable=vars_[f])
        entry.grid(row=row, column=col*2+1, sticky="ew", padx=5, pady=5)
        main_entries[f] = entry

    # --- Buttons ---
    button_frame = tk.Frame(main_frame, bg="#f0f4f8", padx=10, pady=10)
    button_frame.pack(fill="x", padx=20, pady=5)

    btn_specs = [
        ("Thêm Mới", lambda: set_mode("new")),
        ("Lưu", save_data),
        ("Sửa", lambda: set_mode("edit")),
        ("Hủy", clear_form),
        ("Xóa", delete_data)
    ]

    for text, cmd in btn_specs:
        tk.Button(button_frame, text=text, font=("Segoe UI", 10, "bold"), bg="#4CAF50", fg="white", command=cmd).pack(side="left", expand=True, fill="x", padx=5)

    # --- Treeview ---
    list_frame = tk.LabelFrame(main_frame, text="Danh sách vận chuyển", bg="#e6eefc", font=("Segoe UI", 12, "bold"), padx=5, pady=5)
    list_frame.pack(fill="both", expand=True, padx=20, pady=10)

    tree = ttk.Treeview(list_frame, columns=fields, show="headings")
    for f, h in zip(fields, ["Mã VC", "Tên NV", "Bộ Phận", "Phương tiện", "Chi phí (VND)"]):
        tree.heading(f, text=h)
    tree.column("ma_vc", width=80, anchor="center")
    tree.column("ten_nv", width=150)
    tree.column("bo_phan", width=100)
    tree.column("phuong_tien", width=100)
    tree.column("chi_phi", width=100, anchor="e")

    scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    tree.pack(fill="both", expand=True)
    tree.bind("<<TreeviewSelect>>", on_select)

    # --- Status bar ---
    status_label = tk.Label(main_frame, text="Đang tải dữ liệu...", bg="#f0f4f8", fg="#333", anchor="w", relief="sunken", padx=5)
    status_label.pack(fill="x", pady=5)

    load_data()
    return main_frame

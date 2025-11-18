# File: Sales.py (Phiên bản TRANG TRÍ - HOÀN CHỈNH)
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import font as tkFont
from datetime import datetime
import pyodbc

# Import hàm kết nối
from SQL_connect import get_db_connection

def create_sales_frame(parent_container):
    """Tạo và trả về một Frame Quản lý Bán Hàng (Hóa Đơn)."""

    main_frame = ttk.Frame(parent_container, padding=10)

    current_invoice_id = None
    ma_nv_list = []
    vt_data_map = {}
    tong_tien_var = tk.StringVar(value="0 VND")

    # --- FONT CHỮ ---
    title_font = tkFont.Font(family="Segoe UI", size=20, weight="bold")
    section_label_font = tkFont.Font(family="Segoe UI", size=11, weight="bold")
    default_font = tkFont.Font(family="Segoe UI", size=10)
    header_font = tkFont.Font(family="Segoe UI", size=10, weight="bold")
    tree_font = tkFont.Font(family="Segoe UI", size=10)
    total_font = tkFont.Font(family="Segoe UI", size=12, weight="bold")

    # --- STYLE ---
    style = ttk.Style()
    style.theme_use("clam")

    style.configure("Main.TFrame", background="#f9f9f9")
    main_frame.configure(style="Main.TFrame")

    style.configure("TLabel", font=default_font, background="#f9f9f9")
    style.configure("TButton", font=default_font, padding=5, background="#2ecc71", foreground="white")
    style.map("TButton", background=[("active", "#27ae60")], foreground=[("active", "white")])
    style.configure("TEntry", font=default_font, padding=5, fieldbackground="white")
    style.configure("TCombobox", font=default_font, padding=5)
    style.map("TCombobox", fieldbackground=[('readonly', 'white')])
    style.configure("Treeview.Heading", font=header_font, padding=5, background="#3498db", foreground="white")
    style.configure("Treeview", font=tree_font, rowheight=27, background="#ffffff", fieldbackground="#ffffff", foreground="#2c3e50")

    # --- LOGIC ---
    def load_initial_data():
        try:
            conn = get_db_connection()
            if not conn: return
            cursor = conn.cursor()

            # Nhân viên
            ma_nv_list.clear()
            cursor.execute("SELECT MaNV, TenNV FROM NhanVien ORDER BY MaNV")
            for row in cursor.fetchall():
                ten_nv = row.TenNV if row.TenNV else "Chưa có tên"
                ma_nv_list.append(f"{row.MaNV} - {ten_nv}")
            cbb_nhanvien['values'] = ma_nv_list
            default_employee_code = "NV003"
            default_selection = next((item for item in ma_nv_list if item.strip().startswith(default_employee_code)), None)
            if default_selection: cbb_nhanvien.set(default_selection)
            elif ma_nv_list: cbb_nhanvien.current(0)

            # Vật tư
            vt_data_map.clear()
            tree_vattu.delete(*tree_vattu.get_children())
            cursor.execute("SELECT MaVatTu, TenVatTu, GiaBan, SoLuongTon FROM VatTu ORDER BY MaVatTu")
            rows_vt = cursor.fetchall()
            for i, row in enumerate(rows_vt):
                gia_ban_val = row.GiaBan if row.GiaBan is not None else 0
                sl_ton_val = row.SoLuongTon if row.SoLuongTon is not None else 0
                vt_data_map[row.MaVatTu] = {"ten": row.TenVatTu, "gia": gia_ban_val, "ton": sl_ton_val}
                tag = 'evenrow' if i % 2 == 0 else 'oddrow'
                tree_vattu.insert("", tk.END, iid=row.MaVatTu, values=(
                    row.MaVatTu, row.TenVatTu, f"{gia_ban_val:,.0f}", sl_ton_val
                ), tags=(tag,))

            # Treeview striping
            tree_vattu.tag_configure('oddrow', background="#ffffff")
            tree_vattu.tag_configure('evenrow', background="#f2f2f2")
            tree_chitiethoadon.tag_configure('oddrow', background="#ffffff")
            tree_chitiethoadon.tag_configure('evenrow', background="#f2f2f2")

            conn.close()
        except Exception as e:
            messagebox.showerror("Lỗi CSDL", f"Lỗi khi tải dữ liệu khởi tạo:\n{e}")

    def tao_hoa_don_moi():
        nonlocal current_invoice_id
        selected_nv = cbb_nhanvien.get()
        if not selected_nv: messagebox.showwarning("Thiếu thông tin", "Vui lòng chọn Nhân viên."); return
        try:
            conn = get_db_connection()
            if not conn: return
            cursor = conn.cursor()
            ma_nv = selected_nv.split(" - ")[0]
            cursor.execute("INSERT INTO HoaDon (NgayLap, MaNV, TongTien) VALUES (?, ?, ?)", (datetime.now(), ma_nv, 0))
            cursor.execute("SELECT @@IDENTITY")
            result = cursor.fetchone()
            if result and result[0] is not None:
                current_invoice_id = int(result[0])
                messagebox.showinfo("Thành công", f"Tạo hóa đơn mới thành công!\nMã hóa đơn: {current_invoice_id}")
                tree_chitiethoadon.delete(*tree_chitiethoadon.get_children())
                tong_tien_var.set("0 VND")
            else:
                messagebox.showerror("Lỗi Lấy MaHD", "Không thể lấy mã hóa đơn vừa tạo!")
                current_invoice_id = None
            conn.close()
        except Exception as e:
            messagebox.showerror("Lỗi CSDL", f"Lỗi khi tạo hóa đơn mới:\n{e}")
            current_invoice_id = None

    def them_vat_tu():
        nonlocal current_invoice_id
        if not current_invoice_id: messagebox.showwarning("Chưa có hóa đơn", "Vui lòng 'Tạo hóa đơn mới' trước."); return
        selected = tree_vattu.selection()
        if not selected: messagebox.showwarning("Chưa chọn vật tư", "Vui lòng chọn vật tư."); return
        ma_vt = tree_vattu.item(selected[0])['values'][0]
        so_luong_str = entry_soluong.get().strip()
        if not so_luong_str.isdigit() or int(so_luong_str) <= 0: messagebox.showwarning("Số lượng không hợp lệ", "Số lượng phải > 0."); return
        so_luong = int(so_luong_str)
        if ma_vt not in vt_data_map: messagebox.showerror("Lỗi Dữ liệu", f"Không tìm thấy thông tin cho {ma_vt}."); return
        vt_info = vt_data_map[ma_vt]
        if so_luong > vt_info['ton']: messagebox.showwarning("Không đủ hàng", f"'{vt_info['ten']}' chỉ còn {vt_info['ton']}."); return
        try:
            conn = get_db_connection()
            if not conn: return
            cursor = conn.cursor()
            gia_ban_hien_tai = vt_info['gia']
            cursor.execute("INSERT INTO ChiTietHoaDon (MaHD, MaVatTu, SoLuong, DonGia) VALUES (?, ?, ?, ?)",
                           (current_invoice_id, ma_vt, so_luong, gia_ban_hien_tai))
            cursor.execute("UPDATE VatTu SET SoLuongTon = SoLuongTon - ? WHERE MaVatTu = ?", (so_luong, ma_vt))
            cursor.execute("SELECT SUM(SoLuong * DonGia) FROM ChiTietHoaDon WHERE MaHD = ?", current_invoice_id)
            new_total = cursor.fetchone()[0] or 0
            cursor.execute("UPDATE HoaDon SET TongTien = ? WHERE MaHD = ?", (new_total, current_invoice_id))
            conn.close()
            vt_info['ton'] -= so_luong
            tree_vattu.item(selected[0], values=(ma_vt, vt_info['ten'], f"{vt_info['gia']:,.0f}", vt_info['ton']))
            thanh_tien = so_luong * gia_ban_hien_tai
            i = len(tree_chitiethoadon.get_children())
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            tree_chitiethoadon.insert("", tk.END, values=(ma_vt, vt_info['ten'], so_luong, f"{gia_ban_hien_tai:,.0f}", f"{thanh_tien:,.0f}"), tags=(tag,))
            tong_tien_var.set(f"{new_total:,.0f} VND")
            entry_soluong.delete(0, tk.END); entry_soluong.focus()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi thêm chi tiết:\n{e}")

    # --------------------------
    # GIAO DIỆN
    # --------------------------
    lbl_title = tk.Label(main_frame, text="QUẢN LÝ BÁN HÀNG", font=title_font, bg="#f9f9f9", fg="#00529B")
    lbl_title.pack(pady=10)

    frame_top = ttk.Frame(main_frame)
    frame_top.pack(pady=10, fill=tk.X, padx=20)
    tk.Label(frame_top, text="Nhân viên lập hóa đơn:", font=section_label_font, bg="#f9f9f9").pack(side=tk.LEFT, padx=5)
    cbb_nhanvien = ttk.Combobox(frame_top, width=30, state="readonly", font=default_font)
    cbb_nhanvien.pack(side=tk.LEFT, padx=5)
    btn_taohoadon = ttk.Button(frame_top, text="Tạo hóa đơn mới", command=tao_hoa_don_moi)
    btn_taohoadon.pack(side=tk.LEFT, padx=10)

    frame_mid = ttk.Frame(main_frame)
    frame_mid.pack(pady=10, fill=tk.X, padx=20)
    tk.Label(frame_mid, text="Danh sách Vật tư:", font=section_label_font, bg="#f9f9f9").pack(anchor=tk.W)
    tree_vattu = ttk.Treeview(frame_mid, columns=("MaVT", "TenVT", "Gia", "Ton"), show="headings", height=7)
    tree_vattu.heading("MaVT", text="Mã VT"); tree_vattu.heading("TenVT", text="Tên vật tư")
    tree_vattu.heading("Gia", text="Giá Bán (VND)"); tree_vattu.heading("Ton", text="SL Tồn")
    tree_vattu.column("MaVT", width=100, anchor=tk.CENTER); tree_vattu.column("TenVT", width=300)
    tree_vattu.column("Gia", width=120, anchor=tk.E); tree_vattu.column("Ton", width=80, anchor=tk.E)
    tree_vattu.pack(fill=tk.X, pady=5)

    tk.Label(frame_mid, text="Số lượng:", font=section_label_font, bg="#f9f9f9").pack(side=tk.LEFT)
    entry_soluong = ttk.Entry(frame_mid, width=10, font=default_font)
    entry_soluong.pack(side=tk.LEFT, padx=5)
    btn_themvattu = ttk.Button(frame_mid, text="Thêm vào hóa đơn", command=them_vat_tu)
    btn_themvattu.pack(side=tk.LEFT, padx=10)

    tk.Label(main_frame, text="Chi tiết hóa đơn:", font=section_label_font, bg="#f9f9f9").pack(anchor=tk.W, padx=20)
    tree_chitiethoadon = ttk.Treeview(main_frame, columns=("MaVT", "TenVT", "SL", "Gia", "ThanhTien"), show="headings", height=7)
    tree_chitiethoadon.heading("MaVT", text="Mã VT"); tree_chitiethoadon.heading("TenVT", text="Tên vật tư")
    tree_chitiethoadon.heading("SL", text="Số lượng"); tree_chitiethoadon.heading("Gia", text="Đơn Giá (VND)")
    tree_chitiethoadon.heading("ThanhTien", text="Thành Tiền (VND)")
    tree_chitiethoadon.column("MaVT", width=100, anchor=tk.CENTER); tree_chitiethoadon.column("TenVT", width=300)
    tree_chitiethoadon.column("SL", width=80, anchor=tk.E); tree_chitiethoadon.column("Gia", width=120, anchor=tk.E)
    tree_chitiethoadon.column("ThanhTien", width=150, anchor=tk.E)
    tree_chitiethoadon.pack(fill=tk.X, padx=20, pady=5)

    frame_bottom = tk.Frame(main_frame, bg="#f9f9f9")
    frame_bottom.pack(pady=10)
    tk.Label(frame_bottom, text="Tổng tiền:", font=total_font, bg="#f9f9f9").pack(side=tk.LEFT, padx=5)
    tk.Label(frame_bottom, textvariable=tong_tien_var, font=total_font, bg="#f9f9f9", foreground="#27ae60").pack(side=tk.LEFT)

    load_initial_data()
    return main_frame
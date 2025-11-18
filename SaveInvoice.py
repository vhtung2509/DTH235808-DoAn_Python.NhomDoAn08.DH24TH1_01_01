# File: SaveInvoice.py
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import pyodbc
from SQL_connect import get_db_connection  # Hàm kết nối DB bạn đã dùng

def create_invoice_frame(parent_container):
    """
    Tạo Frame quản lý Hóa đơn công trình
    """

    main_frame = ttk.Frame(parent_container, padding=10)

    # --- Biến ---
    ma_nv_var = tk.StringVar()
    tong_tien_var = tk.StringVar()
    chi_tiet_vt = []  # Danh sách vật tư trong hóa đơn tạm thời

    # --- Hàm logic ---
    def load_invoice_list():
        tree_invoice.delete(*tree_invoice.get_children())
        conn = get_db_connection()
        if not conn:
            return
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT h.MaHD, h.NgayLap, n.TenNV, h.TongTien
                FROM HoaDon h
                JOIN NhanVien n ON h.MaNV = n.MaNV
                ORDER BY h.MaHD DESC
            """)
            rows = cursor.fetchall()
            for row in rows:
                tong_tien_formatted = f"{int(row.TongTien):,}" if row.TongTien else "0"
                tree_invoice.insert("", "end", iid=row.MaHD, values=(row.MaHD, row.NgayLap.strftime("%d-%m-%Y %H:%M"), row.TenNV, tong_tien_formatted))
            status_label.config(text=f"Đã tải {len(rows)} hóa đơn.", foreground="green")
        except pyodbc.Error as e:
            messagebox.showerror("Lỗi CSDL", f"Lỗi khi tải hóa đơn:\n{e}")
        finally:
            if conn:
                conn.close()

    def load_invoice_details(ma_hd):
        tree_detail.delete(*tree_detail.get_children())
        conn = get_db_connection()
        if not conn:
            return
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT v.TenVatTu, c.SoLuong, c.DonGia, (c.SoLuong*c.DonGia) as ThanhTien
                FROM ChiTietHoaDon c
                JOIN VatTu v ON c.MaVatTu = v.MaVatTu
                WHERE c.MaHD = ?
            """, ma_hd)
            rows = cursor.fetchall()
            for row in rows:
                thanh_tien = f"{int(row.ThanhTien):,}"
                tree_detail.insert("", "end", values=(row.TenVatTu, row.SoLuong, f"{row.DonGia:,}", thanh_tien))
        except pyodbc.Error as e:
            messagebox.showerror("Lỗi CSDL", f"Lỗi khi tải chi tiết hóa đơn:\n{e}")
        finally:
            if conn:
                conn.close()

    def on_invoice_select(event):
        try:
            selected_id = tree_invoice.selection()[0]
            load_invoice_details(selected_id)
        except IndexError:
            pass

    def click_tao_hoa_don():
        try:
            tong_tien = int(tong_tien_var.get().replace(",", ""))
            ma_nv = ma_nv_var.get().strip()
            if not ma_nv or tong_tien <= 0:
                messagebox.showwarning("Thiếu dữ liệu", "Vui lòng tính doanh thu trước khi tạo hóa đơn!")
                return
        except ValueError:
            messagebox.showerror("Dữ liệu không hợp lệ", "Tổng tiền phải là số nguyên.")
            return

        if not chi_tiet_vt:
            messagebox.showwarning("Chi tiết rỗng", "Hóa đơn chưa có vật tư!")
            return

        conn = get_db_connection()
        if not conn:
            return
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO HoaDon (NgayLap, MaNV, TongTien) VALUES (?, ?, ?)", datetime.now(), ma_nv, tong_tien)
            cursor.execute("SELECT @@IDENTITY as NewID")
            new_id = cursor.fetchone().NewID
            for vt in chi_tiet_vt:
                cursor.execute("INSERT INTO ChiTietHoaDon (MaHD, MaVatTu, SoLuong, DonGia) VALUES (?, ?, ?, ?)",
                               new_id, vt['MaVatTu'], vt['SoLuong'], vt['DonGia'])
            conn.commit()
            status_label.config(text=f"Đã tạo hóa đơn số {new_id}.", foreground="green")
            chi_tiet_vt.clear()
            tong_tien_var.set("0")
            load_invoice_list()
            tree_detail.delete(*tree_detail.get_children())
        except pyodbc.Error as e:
            messagebox.showerror("Lỗi lưu hóa đơn", f"Lỗi khi lưu hóa đơn:\n{e}")
        finally:
            if conn:
                conn.close()

    def click_xoa_hoa_don():
        try:
            selected_id = tree_invoice.selection()[0]
        except IndexError:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn hóa đơn để xóa!")
            return
        if messagebox.askyesno("Xác nhận xóa", f"Bạn có chắc muốn xóa hóa đơn {selected_id}?"):
            conn = get_db_connection()
            if not conn:
                return
            try:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM ChiTietHoaDon WHERE MaHD=?", selected_id)
                cursor.execute("DELETE FROM HoaDon WHERE MaHD=?", selected_id)
                conn.commit()
                status_label.config(text=f"Đã xóa hóa đơn {selected_id}.", foreground="green")
                load_invoice_list()
                tree_detail.delete(*tree_detail.get_children())
            except pyodbc.Error as e:
                messagebox.showerror("Lỗi xóa hóa đơn", f"Lỗi: {e}")
            finally:
                if conn:
                    conn.close()

    # --- GUI ---
    ttk.Label(main_frame, text="QUẢN LÝ HÓA ĐƠN CÔNG TRÌNH", font=("Segoe UI", 16, "bold")).pack(pady=(10, 20))

    button_frame = ttk.Frame(main_frame)
    button_frame.pack(fill="x", padx=20)
    ttk.Button(button_frame, text="Tạo Hóa Đơn", command=click_tao_hoa_don).pack(side="left", padx=5)
    ttk.Button(button_frame, text="Xóa Hóa Đơn", command=click_xoa_hoa_don).pack(side="left", padx=5)

    invoice_frame = ttk.LabelFrame(main_frame, text="Danh sách hóa đơn", padding=5)
    invoice_frame.pack(fill="both", expand=True, padx=20, pady=(10, 5))
    columns_invoice = ("mahd", "ngaylap", "tennv", "tongtien")
    tree_invoice = ttk.Treeview(invoice_frame, columns=columns_invoice, show="headings")
    for col, txt in zip(columns_invoice, ("Mã HD", "Ngày lập", "Nhân viên", "Tổng tiền")):
        tree_invoice.heading(col, text=txt)
        tree_invoice.column(col, anchor="center")
    tree_invoice.pack(fill="both", expand=True)
    tree_invoice.bind('<<TreeviewSelect>>', on_invoice_select)

    detail_frame = ttk.LabelFrame(main_frame, text="Chi tiết hóa đơn", padding=5)
    detail_frame.pack(fill="both", expand=True, padx=20, pady=(5, 10))
    columns_detail = ("tenvt", "soluong", "dongia", "thanhtien")
    tree_detail = ttk.Treeview(detail_frame, columns=columns_detail, show="headings")
    for col, txt in zip(columns_detail, ("Vật tư", "Số lượng", "Đơn giá", "Thành tiền")):
        tree_detail.heading(col, text=txt)
        tree_detail.column(col, anchor="center")
    tree_detail.pack(fill="both", expand=True)

    status_label = ttk.Label(main_frame, text="Đang tải dữ liệu...", relief="sunken", anchor="w", padding=5)
    status_label.pack(side="bottom", fill="x")

    load_invoice_list()

    return main_frame

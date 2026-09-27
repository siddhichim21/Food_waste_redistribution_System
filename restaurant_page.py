import re
import tkinter as tk
from tkinter import ttk, messagebox
from db import get_connection
from theme import BG
from widgets import build_topbar

TIME_RE = re.compile(r"^([01]\d|2[0-3]):[0-5]\d:[0-5]\d$")


class RestaurantPage(tk.Frame):
    def __init__(self, parent, controller, user_id=None):
        super().__init__(parent, bg=BG)
        self.controller = controller
        self.user_id = user_id

        build_topbar(self, "Restaurant Dashboard", controller,
                     subtitle="Manage the food you're donating",
                     logout_command=controller.go_to_login)

        actions = tk.Frame(self, bg=BG)
        actions.pack(fill="x", padx=20, pady=15)
        ttk.Button(actions, text="+ Add Food Donation", style="Primary.TButton",
                   command=self.open_add_dialog).pack(side="left")
        ttk.Button(actions, text="Refresh", style="Accent.TButton",
                   command=self.load_donations).pack(side="left", padx=10)

        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        columns = ("ID", "Food", "Quantity", "Date", "Prepared", "Expiry", "Address", "Status")
        self.table = ttk.Treeview(body, columns=columns, show="headings")
        for c in columns:
            self.table.heading(c, text=c)
            self.table.column(c, width=95)
        self.table.pack(fill="both", expand=True)

        self.load_donations()

    def load_donations(self):
        for row in self.table.get_children():
            self.table.delete(row)
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT d.donation_id, f.food_name, d.quantity, d.donation_date,
                       d.prepared_time, d.expiry_time, d.pickup_address, d.status
                FROM donations d
                JOIN food_items f ON d.food_id = f.food_id
                JOIN food_providers p ON d.provider_id = p.provider_id
                WHERE p.user_id = %s
                ORDER BY d.donation_id DESC
            """, (self.user_id,))
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
        except Exception as e:
            messagebox.showerror("Database Error", str(e))
            return

        for row in rows:
            self.table.insert("", "end", values=row)

    def open_add_dialog(self):
        dialog = tk.Toplevel(self)
        dialog.title("Add Food Donation")
        dialog.geometry("420x520")
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        dialog.configure(bg="white")

        tk.Label(dialog, text="ADD FOOD DONATION", bg="white",
                 font=("Segoe UI", 16, "bold")).pack(pady=(20, 15))

        food_data = []
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT food_id, food_name FROM food_items ORDER BY food_name")
            food_data = cursor.fetchall()
            cursor.close()
            conn.close()
        except Exception as e:
            messagebox.showerror("Database Error", str(e))
            dialog.destroy()
            return

        tk.Label(dialog, text="Food Name", bg="white",
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=40)
        food_combo = ttk.Combobox(dialog, width=32, state="readonly",
                                  values=[f[1] for f in food_data])
        food_combo.pack(pady=(2, 10), padx=40)

        tk.Label(dialog, text="Quantity", bg="white",
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=40)
        qty_spin = tk.Spinbox(dialog, from_=1, to=100000, width=34)
        qty_spin.pack(pady=(2, 10), padx=40)

        tk.Label(dialog, text="Prepared Time (HH:MM:SS)", bg="white",
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=40)
        prepared_entry = ttk.Entry(dialog, width=34)
        prepared_entry.insert(0, "18:00:00")
        prepared_entry.pack(pady=(2, 10), padx=40)

        tk.Label(dialog, text="Expiry Time (HH:MM:SS)", bg="white",
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=40)
        expiry_entry = ttk.Entry(dialog, width=34)
        expiry_entry.insert(0, "22:00:00")
        expiry_entry.pack(pady=(2, 10), padx=40)

        tk.Label(dialog, text="Pickup Address", bg="white",
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=40)
        address_entry = ttk.Entry(dialog, width=34)
        address_entry.pack(pady=(2, 16), padx=40)

        def save():
            food_name = food_combo.get()
            prepared = prepared_entry.get().strip()
            expiry = expiry_entry.get().strip()
            address = address_entry.get().strip()

            if not food_name or not address:
                messagebox.showerror("Error", "Food and pickup address are required.")
                return
            if not TIME_RE.match(prepared) or not TIME_RE.match(expiry):
                messagebox.showerror("Error", "Times must be in HH:MM:SS 24-hour format.")
                return
            if expiry <= prepared:
                messagebox.showerror("Error", "Expiry time must be after prepared time.")
                return
            try:
                quantity = int(qty_spin.get())
                if quantity <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Quantity must be a positive whole number.")
                return

            food_id = next(f[0] for f in food_data if f[1] == food_name)

            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT provider_id FROM food_providers WHERE user_id = %s",
                    (self.user_id,),
                )
                provider = cursor.fetchone()
                if provider is None:
                    messagebox.showerror("Error", "Provider profile not found.")
                    cursor.close()
                    conn.close()
                    return
                provider_id = provider[0]

                cursor.execute("""
                    INSERT INTO donations
                    (provider_id, food_id, quantity, donation_date,
                     prepared_time, expiry_time, pickup_address, status)
                    VALUES (%s, %s, %s, CURDATE(), %s, %s, %s, 'AVAILABLE')
                """, (provider_id, food_id, quantity, prepared, expiry, address))
                conn.commit()
                cursor.close()
                conn.close()
            except Exception as e:
                messagebox.showerror("Database Error", str(e))
                return

            messagebox.showinfo("Success", "Food donation added successfully!")
            dialog.destroy()
            self.load_donations()

        ttk.Button(dialog, text="SAVE DONATION", style="Primary.TButton",
                   command=save).pack(pady=10, padx=40, fill="x")

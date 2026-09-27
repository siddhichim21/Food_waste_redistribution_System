import re
import tkinter as tk
from tkinter import ttk, messagebox
from db import get_connection
from theme import BG
from widgets import build_topbar

TIME_RE = re.compile(r"^([01]\d|2[0-3]):[0-5]\d:[0-5]\d$")


class DonationManagerPage(tk.Frame):
    def __init__(self, parent, controller, user_id=None):
        super().__init__(parent, bg=BG)
        self.controller = controller
        self.user_id = user_id
        self.providers = []
        self.foods = []

        build_topbar(self, "Donation Manager", controller,
                     subtitle="Create, update and remove donation records",
                     logout_command=controller.go_to_login)

        top_actions = tk.Frame(self, bg=BG)
        top_actions.pack(fill="x", padx=20, pady=(10, 0))
        ttk.Button(top_actions, text="\u2190 Back to Admin", style="Primary.TButton",
                   command=lambda: controller.go_to_role("ADMIN", user_id)
                   ).pack(side="left")

        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True, padx=20, pady=15)

        form = tk.Frame(body, bg="white", padx=20, pady=20,
                         highlightbackground="#E2E8F0", highlightthickness=1)
        form.pack(side="left", fill="y")

        tk.Label(form, text="Donation ID (update/delete)", bg="white",
                 font=("Segoe UI", 9, "bold")).pack(anchor="w")
        self.id_entry = ttk.Entry(form, width=28)
        self.id_entry.pack(pady=(2, 10))

        tk.Label(form, text="Provider", bg="white",
                 font=("Segoe UI", 9, "bold")).pack(anchor="w")
        self.provider_combo = ttk.Combobox(form, width=26, state="readonly")
        self.provider_combo.pack(pady=(2, 10))

        tk.Label(form, text="Food Item", bg="white",
                 font=("Segoe UI", 9, "bold")).pack(anchor="w")
        self.food_combo = ttk.Combobox(form, width=26, state="readonly")
        self.food_combo.pack(pady=(2, 10))

        tk.Label(form, text="Quantity", bg="white",
                 font=("Segoe UI", 9, "bold")).pack(anchor="w")
        self.qty_spin = tk.Spinbox(form, from_=1, to=100000, width=27)
        self.qty_spin.pack(pady=(2, 10))

        tk.Label(form, text="Prepared Time (HH:MM:SS)", bg="white",
                 font=("Segoe UI", 9, "bold")).pack(anchor="w")
        self.prepared_entry = ttk.Entry(form, width=28)
        self.prepared_entry.insert(0, "18:00:00")
        self.prepared_entry.pack(pady=(2, 10))

        tk.Label(form, text="Expiry Time (HH:MM:SS)", bg="white",
                 font=("Segoe UI", 9, "bold")).pack(anchor="w")
        self.expiry_entry = ttk.Entry(form, width=28)
        self.expiry_entry.insert(0, "22:00:00")
        self.expiry_entry.pack(pady=(2, 10))

        tk.Label(form, text="Pickup Address", bg="white",
                 font=("Segoe UI", 9, "bold")).pack(anchor="w")
        self.address_entry = ttk.Entry(form, width=28)
        self.address_entry.pack(pady=(2, 14))

        ttk.Button(form, text="CREATE", style="Primary.TButton",
                   command=self.create_donation).pack(fill="x", pady=4)
        ttk.Button(form, text="UPDATE QUANTITY", style="Accent.TButton",
                   command=self.update_donation).pack(fill="x", pady=4)
        ttk.Button(form, text="DELETE", style="Danger.TButton",
                   command=self.delete_donation).pack(fill="x", pady=4)

        list_panel = tk.Frame(body, bg=BG)
        list_panel.pack(side="left", fill="both", expand=True, padx=(15, 0))

        columns = ("ID", "Provider", "Food", "Quantity", "Date", "Status")
        self.table = ttk.Treeview(list_panel, columns=columns, show="headings")
        for c in columns:
            self.table.heading(c, text=c)
            self.table.column(c, width=110)
        self.table.pack(fill="both", expand=True)
        self.table.bind("<<TreeviewSelect>>", self.fill_id_from_selection)

        self.load_lookups()
        self.read_donations()

    def load_lookups(self):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT provider_id, provider_name FROM food_providers ORDER BY provider_name")
            self.providers = cursor.fetchall()
            self.provider_combo["values"] = [p[1] for p in self.providers]

            cursor.execute("SELECT food_id, food_name FROM food_items ORDER BY food_name")
            self.foods = cursor.fetchall()
            self.food_combo["values"] = [f[1] for f in self.foods]

            cursor.close()
            conn.close()
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    def fill_id_from_selection(self, event=None):
        selected = self.table.selection()
        if not selected:
            return
        values = self.table.item(selected[0], "values")
        self.id_entry.delete(0, tk.END)
        self.id_entry.insert(0, values[0])

    def create_donation(self):
        provider_name = self.provider_combo.get()
        food_name = self.food_combo.get()
        prepared = self.prepared_entry.get().strip()
        expiry = self.expiry_entry.get().strip()
        address = self.address_entry.get().strip()

        if not provider_name or not food_name or not address:
            messagebox.showerror("Error", "Provider, food and address are required.")
            return
        if not TIME_RE.match(prepared) or not TIME_RE.match(expiry):
            messagebox.showerror("Error", "Times must be in HH:MM:SS 24-hour format.")
            return
        if expiry <= prepared:
            messagebox.showerror("Error", "Expiry time must be after prepared time.")
            return
        try:
            quantity = int(self.qty_spin.get())
            if quantity <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Quantity must be a positive whole number.")
            return

        provider_id = next(p[0] for p in self.providers if p[1] == provider_name)
        food_id = next(f[0] for f in self.foods if f[1] == food_name)

        try:
            conn = get_connection()
            cursor = conn.cursor()
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

        messagebox.showinfo("Created", "Donation created successfully!")
        self.read_donations()

    def update_donation(self):
        donation_id = self.id_entry.get().strip()
        if not donation_id.isdigit():
            messagebox.showerror("Error", "Select a donation or enter a valid numeric ID.")
            return
        try:
            quantity = int(self.qty_spin.get())
            if quantity <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Quantity must be a positive whole number.")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE donations SET quantity = %s WHERE donation_id = %s",
                (quantity, donation_id),
            )
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            messagebox.showerror("Database Error", str(e))
            return

        messagebox.showinfo("Updated", "Donation updated successfully!")
        self.read_donations()

    def delete_donation(self):
        donation_id = self.id_entry.get().strip()
        if not donation_id.isdigit():
            messagebox.showerror("Error", "Select a donation or enter a valid numeric ID.")
            return
        if not messagebox.askyesno("Confirm", f"Delete donation #{donation_id}?"):
            return
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM donations WHERE donation_id = %s", (donation_id,))
            conn.commit()
            cursor.close()
            conn.close()
        except Exception:
            messagebox.showerror(
                "Delete Error",
                "This donation may be linked to a request or pickup and can't be removed.",
            )
            return

        messagebox.showinfo("Deleted", "Donation deleted successfully!")
        self.read_donations()

    def read_donations(self):
        for row in self.table.get_children():
            self.table.delete(row)
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT d.donation_id, p.provider_name, f.food_name,
                       d.quantity, d.donation_date, d.status
                FROM donations d
                JOIN food_providers p ON d.provider_id = p.provider_id
                JOIN food_items f ON d.food_id = f.food_id
                ORDER BY d.donation_id DESC
            """)
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
        except Exception as e:
            messagebox.showerror("Database Error", str(e))
            return

        for row in rows:
            self.table.insert("", "end", values=row)

import tkinter as tk
from tkinter import ttk, messagebox
from db import get_connection
from theme import BG
from widgets import build_topbar


class NgoPage(tk.Frame):
    def __init__(self, parent, controller, ngo_id=None):
        super().__init__(parent, bg=BG)
        self.controller = controller
        self.ngo_id = ngo_id

        build_topbar(self, "NGO Dashboard", controller,
                     subtitle="Browse and request available food",
                     logout_command=controller.go_to_login)

        actions = tk.Frame(self, bg=BG)
        actions.pack(fill="x", padx=20, pady=15)
        ttk.Button(actions, text="Refresh", style="Accent.TButton",
                   command=self.load_food).pack(side="left")
        ttk.Button(actions, text="Request Selected", style="Primary.TButton",
                   command=self.open_request_dialog).pack(side="left", padx=10)

        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        columns = ("Donation ID", "Food", "Quantity", "Restaurant", "Expiry", "Address")
        self.table = ttk.Treeview(body, columns=columns, show="headings")
        for c in columns:
            self.table.heading(c, text=c)
            self.table.column(c, width=120)
        self.table.pack(fill="both", expand=True)

        self.load_food()

    def load_food(self):
        for row in self.table.get_children():
            self.table.delete(row)
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT d.donation_id, f.food_name, d.quantity, p.provider_name,
                       d.expiry_time, d.pickup_address
                FROM donations d
                JOIN food_items f ON d.food_id = f.food_id
                JOIN food_providers p ON d.provider_id = p.provider_id
                WHERE d.status = 'AVAILABLE' AND d.quantity > 0
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

    def open_request_dialog(self):
        selected = self.table.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a food donation first.")
            return
        values = self.table.item(selected[0], "values")
        donation_id, food_name, available_quantity = values[0], values[1], int(values[2])

        dialog = tk.Toplevel(self)
        dialog.title("Request Food")
        dialog.geometry("360x300")
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        dialog.configure(bg="white")

        tk.Label(dialog, text="REQUEST FOOD", bg="white",
                 font=("Segoe UI", 16, "bold")).pack(pady=(20, 10))
        tk.Label(dialog, text=f"Food: {food_name}", bg="white").pack(pady=4)
        tk.Label(dialog, text=f"Available Quantity: {available_quantity}", bg="white").pack(pady=4)
        tk.Label(dialog, text="Requested Quantity", bg="white",
                 font=("Segoe UI", 9, "bold")).pack(pady=(14, 2))
        qty_spin = tk.Spinbox(dialog, from_=1, to=available_quantity, width=20)
        qty_spin.pack(pady=4)

        def save():
            try:
                quantity = int(qty_spin.get())
                if quantity <= 0 or quantity > available_quantity:
                    raise ValueError
            except ValueError:
                messagebox.showerror(
                    "Error", f"Enter a quantity between 1 and {available_quantity}.",
                )
                return

            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO donation_requests
                    (donation_id, ngo_id, requested_quantity)
                    VALUES (%s, %s, %s)
                """, (donation_id, self.ngo_id, quantity))
                conn.commit()
                cursor.close()
                conn.close()
            except Exception as e:
                messagebox.showerror("Database Error", str(e))
                return

            messagebox.showinfo("Success", "Food request submitted successfully!")
            dialog.destroy()
            self.load_food()

        ttk.Button(dialog, text="SUBMIT REQUEST", style="Primary.TButton",
                   command=save).pack(pady=20, padx=40, fill="x")

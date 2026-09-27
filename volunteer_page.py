import tkinter as tk
from tkinter import ttk, messagebox
from db import get_connection
from theme import BG
from widgets import build_topbar


class VolunteerPage(tk.Frame):
    def __init__(self, parent, controller, volunteer_id=None):
        super().__init__(parent, bg=BG)
        self.controller = controller
        self.volunteer_id = volunteer_id

        build_topbar(self, "Volunteer Dashboard", controller,
                     subtitle="Manage your assigned pickups",
                     logout_command=controller.go_to_login)

        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True, padx=20, pady=15)

        columns = ("Pickup ID", "Restaurant", "NGO", "Food", "Quantity", "Status")
        self.table = ttk.Treeview(body, columns=columns, show="headings")
        for c in columns:
            self.table.heading(c, text=c)
            self.table.column(c, width=130)
        self.table.pack(fill="both", expand=True)

        button_frame = tk.Frame(self, bg=BG)
        button_frame.pack(pady=15)

        ttk.Button(button_frame, text="Accept", style="Primary.TButton",
                   command=lambda: self.set_status("ACCEPTED")).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Picked Up", style="Accent.TButton",
                   command=lambda: self.set_status("PICKED UP", "pickup_time")
                   ).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Delivered", style="Primary.TButton",
                   command=lambda: self.set_status("DELIVERED", "delivery_time")
                   ).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Refresh", style="Accent.TButton",
                   command=self.load_pickups).pack(side="left", padx=5)

        self.load_pickups()

    def load_pickups(self):
        for row in self.table.get_children():
            self.table.delete(row)
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.pickup_id, fp.provider_name, n.ngo_name, fi.food_name,
                       dr.requested_quantity, p.status
                FROM pickups p
                JOIN donation_requests dr ON p.request_id = dr.request_id
                JOIN donations d ON dr.donation_id = d.donation_id
                JOIN food_providers fp ON d.provider_id = fp.provider_id
                JOIN ngos n ON dr.ngo_id = n.ngo_id
                JOIN food_items fi ON d.food_id = fi.food_id
                WHERE p.volunteer_id = %s
                ORDER BY p.pickup_id DESC
            """, (self.volunteer_id,))
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
        except Exception as e:
            messagebox.showerror("Database Error", str(e))
            return

        for row in rows:
            self.table.insert("", "end", values=row)

    def set_status(self, status, time_column=None):
        selected = self.table.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a pickup.")
            return
        pickup_id = self.table.item(selected[0], "values")[0]

        set_clause = "status = %s"
        params = [status]
        if time_column:
            # time_column only ever comes from the hard-coded calls above,
            # never from user input, so this is safe to interpolate.
            set_clause += f", {time_column} = NOW()"

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                f"UPDATE pickups SET {set_clause} WHERE pickup_id = %s",
                (*params, pickup_id),
            )
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            messagebox.showerror("Database Error", str(e))
            return

        messagebox.showinfo("Success", f"Pickup marked as {status.title()}.")
        self.load_pickups()

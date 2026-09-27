import tkinter as tk
from tkinter import ttk, messagebox
from db import get_connection
from theme import BG, TEXT
from widgets import build_topbar, stat_card


class AdminPage(tk.Frame):
    def __init__(self, parent, controller, user_id=None):
        super().__init__(parent, bg=BG)
        self.controller = controller
        self.user_id = user_id

        build_topbar(self, "Admin Dashboard", controller,
                     subtitle="Overview of the whole platform",
                     logout_command=controller.go_to_login)

        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True, padx=25, pady=20)

        actions = tk.Frame(body, bg=BG)
        actions.pack(fill="x", pady=(0, 15))
        ttk.Button(actions, text="Refresh Reports", style="Primary.TButton",
                   command=self.load_reports).pack(side="left")
        ttk.Button(actions, text="Top Donating Restaurants (>100)",
                   style="Accent.TButton",
                   command=self.load_top_restaurants).pack(side="left", padx=10)
        ttk.Button(actions, text="Donation Manager (CRUD)", style="Primary.TButton",
                   command=lambda: controller.go_to_donation_manager(user_id)
                   ).pack(side="left")

        self.stats_frame = tk.Frame(body, bg=BG)
        self.stats_frame.pack(fill="x", pady=(0, 20))

        self.list_label = tk.Label(body, text="", bg=BG, fg=TEXT,
                                    font=("Segoe UI", 11, "bold"))
        self.list_label.pack(anchor="w")

        self.result_box = tk.Listbox(body, font=("Segoe UI", 10),
                                      highlightthickness=1, bd=0)
        self.result_box.pack(fill="both", expand=True, pady=(5, 0))

        self.load_reports()

    def load_reports(self):
        for w in self.stats_frame.winfo_children():
            w.destroy()
        self.list_label.config(text="")
        self.result_box.delete(0, tk.END)

        try:
            conn = get_connection()
            cursor = conn.cursor()
            metrics = []
            for label, query in [
                ("Total Food Donated", "SELECT COALESCE(SUM(quantity),0) FROM donations"),
                ("Total Food Distributed", "SELECT COALESCE(SUM(quantity),0) FROM distributions"),
                ("Total NGOs", "SELECT COUNT(*) FROM ngos"),
                ("Total Restaurants", "SELECT COUNT(*) FROM food_providers"),
                ("Total Volunteers", "SELECT COUNT(*) FROM volunteers"),
                ("Pending Requests", "SELECT COUNT(*) FROM donation_requests WHERE status='PENDING'"),
            ]:
                cursor.execute(query)
                metrics.append((label, cursor.fetchone()[0]))
            cursor.close()
            conn.close()
        except Exception as e:
            messagebox.showerror("Database Error", str(e))
            return

        colors = ["#2E7D5B", "#FF8A3D", "#3B82F6", "#8B5CF6", "#0EA5E9", "#DC3545"]
        for i, (label, value) in enumerate(metrics):
            card = stat_card(self.stats_frame, label, value, colors[i % len(colors)])
            card.grid(row=0, column=i, padx=8, sticky="nsew")
            self.stats_frame.grid_columnconfigure(i, weight=1)

    def load_top_restaurants(self):
        self.list_label.config(text="Restaurants with more than 100 units donated")
        self.result_box.delete(0, tk.END)
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT provider_name FROM food_providers
                WHERE provider_id IN (
                    SELECT provider_id FROM donations
                    GROUP BY provider_id HAVING SUM(quantity) > 100
                )
            """)
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
        except Exception as e:
            messagebox.showerror("Database Error", str(e))
            return

        if not rows:
            self.result_box.insert(tk.END, "No restaurant has donated more than 100 units.")
        for row in rows:
            self.result_box.insert(tk.END, row[0])

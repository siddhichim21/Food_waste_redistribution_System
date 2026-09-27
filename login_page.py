import re
import tkinter as tk
from tkinter import ttk, messagebox
from db import get_connection
from theme import BG, PRIMARY, PRIMARY_DARK, MUTED, TEXT, BORDER

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class LoginPage(tk.Frame):
    def __init__(self, parent, controller, prefill_email=None):
        super().__init__(parent, bg=BG)
        self.controller = controller

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=9)
        self.grid_columnconfigure(1, weight=11)

        # ---- Left branding panel -------------------------------------
        left = tk.Frame(self, bg=PRIMARY)
        left.grid(row=0, column=0, sticky="nsew")

        brand = tk.Frame(left, bg=PRIMARY)
        brand.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(brand, text="\U0001F372", bg=PRIMARY, font=("Segoe UI", 64)).pack()
        tk.Label(
            brand, text="Food Donation &\nRedistribution System", bg=PRIMARY,
            fg="white", font=("Segoe UI", 20, "bold"), justify="center",
        ).pack(pady=(15, 10))
        tk.Label(
            brand, text="Connecting restaurants, NGOs and volunteers\nto put surplus food to good use.",
            bg=PRIMARY, fg="#D9F0E4", font=("Segoe UI", 11), justify="center",
        ).pack()

        # ---- Right form panel ------------------------------------------
        right = tk.Frame(self, bg=BG)
        right.grid(row=0, column=1, sticky="nsew")

        wrapper = tk.Frame(right, bg=BG)
        wrapper.place(relx=0.5, rely=0.5, anchor="center")

        card = tk.Frame(
            wrapper, bg="white", padx=45, pady=40,
            highlightbackground=BORDER, highlightthickness=1,
        )
        card.pack()

        tk.Label(
            card, text="Welcome Back", bg="white", fg=PRIMARY_DARK,
            font=("Segoe UI", 20, "bold"),
        ).pack(anchor="w")
        tk.Label(
            card, text="Sign in to continue", bg="white", fg=MUTED,
            font=("Segoe UI", 10),
        ).pack(anchor="w", pady=(0, 20))

        tk.Label(card, text="Email", bg="white", fg=TEXT,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w")
        self.email_entry = ttk.Entry(card, width=34, font=("Segoe UI", 10))
        self.email_entry.pack(pady=(2, 12), ipady=4)
        if prefill_email:
            self.email_entry.insert(0, prefill_email)

        tk.Label(card, text="Password", bg="white", fg=TEXT,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w")
        self.password_entry = ttk.Entry(card, width=34, show="\u2022",
                                         font=("Segoe UI", 10))
        self.password_entry.pack(pady=(2, 6), ipady=4)

        self.error_label = tk.Label(card, text="", bg="white", fg="#DC3545",
                                     font=("Segoe UI", 9), wraplength=280, justify="left")
        self.error_label.pack(anchor="w")

        ttk.Button(card, text="LOGIN", style="Primary.TButton",
                   command=self.login).pack(fill="x", pady=(14, 18))

        divider = tk.Frame(card, bg="white")
        divider.pack(fill="x")
        tk.Frame(divider, bg=BORDER, height=1).pack(fill="x", pady=(0, 14))

        register_row = tk.Frame(card, bg="white")
        register_row.pack()
        tk.Label(register_row, text="New here?", bg="white", fg=MUTED,
                 font=("Segoe UI", 10)).pack(side="left")
        link = tk.Label(
            register_row, text="Create an account", bg="white", fg=PRIMARY,
            font=("Segoe UI", 10, "bold"), cursor="hand2",
        )
        link.pack(side="left", padx=(6, 0))
        link.bind("<Button-1>", lambda e: controller.go_to_register())

        self.password_entry.bind("<Return>", lambda e: self.login())
        (self.password_entry if prefill_email else self.email_entry).focus_set()

    def login(self):
        email = self.email_entry.get().strip()
        password = self.password_entry.get()

        # ---- input constraints ----
        if not email or not password:
            self.error_label.config(text="Email and password are required.")
            return
        if not EMAIL_RE.match(email):
            self.error_label.config(text="Enter a valid email address.")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT user_id, role FROM users WHERE email = %s AND password = %s",
                (email, password),
            )
            user = cursor.fetchone()
            cursor.close()
            conn.close()
        except Exception as e:
            messagebox.showerror("Database Error", str(e))
            return

        if not user:
            self.error_label.config(text="Invalid email or password.")
            return

        user_id, role = user
        role_ref_id = None

        try:
            if role == "NGO":
                role_ref_id = self._lookup(user_id, "ngos", "ngo_id")
                if role_ref_id is None:
                    messagebox.showerror("Error", "NGO profile not found.")
                    return
            elif role == "VOLUNTEER":
                role_ref_id = self._lookup(user_id, "volunteers", "volunteer_id")
                if role_ref_id is None:
                    messagebox.showerror("Error", "Volunteer profile not found.")
                    return
        except Exception as e:
            messagebox.showerror("Database Error", str(e))
            return

        self.controller.go_to_role(role, user_id, role_ref_id)

    def _lookup(self, user_id, table, id_column):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(f"SELECT {id_column} FROM {table} WHERE user_id = %s", (user_id,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        return row[0] if row else None

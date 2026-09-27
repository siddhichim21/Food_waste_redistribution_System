import re
import tkinter as tk
from tkinter import ttk, messagebox
from db import get_connection
from theme import BG, PRIMARY, PRIMARY_DARK, MUTED, TEXT, BORDER

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

# Display label -> role code stored in the users table
ROLE_OPTIONS = {
    "Restaurant / Food Provider": "PROVIDER",
    "NGO": "NGO",
    "Volunteer": "VOLUNTEER",
    "Admin": "ADMIN",
}

# Role -> (label for the extra name field, table, name column)
ROLE_PROFILE = {
    "PROVIDER": ("Restaurant / Business Name", "food_providers", "provider_name"),
    "NGO": ("NGO Name", "ngos", "ngo_name"),
}


class RegisterPage(tk.Frame):
    def __init__(self, parent, controller):
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

        tk.Label(brand, text="\U0001F91D", bg=PRIMARY, font=("Segoe UI", 64)).pack()
        tk.Label(
            brand, text="Join the Movement", bg=PRIMARY, fg="white",
            font=("Segoe UI", 20, "bold"),
        ).pack(pady=(15, 10))
        tk.Label(
            brand,
            text="Register as a restaurant, NGO or volunteer\nand start reducing food waste today.",
            bg=PRIMARY, fg="#D9F0E4", font=("Segoe UI", 11), justify="center",
        ).pack()

        # ---- Right form panel ------------------------------------------
        right = tk.Frame(self, bg=BG)
        right.grid(row=0, column=1, sticky="nsew")

        outer = tk.Frame(right, bg=BG)
        outer.place(relx=0.5, rely=0.5, anchor="center")

        card = tk.Frame(
            outer, bg="white", padx=45, pady=35,
            highlightbackground=BORDER, highlightthickness=1,
        )
        card.pack()

        tk.Label(card, text="Create Your Account", bg="white", fg=PRIMARY_DARK,
                 font=("Segoe UI", 18, "bold")).pack(anchor="w")
        tk.Label(card, text="Fill in your details to get started", bg="white",
                 fg=MUTED, font=("Segoe UI", 10)).pack(anchor="w", pady=(0, 15))

        self.name_entry = self._field(card, "Full Name")
        self.email_entry = self._field(card, "Email")
        self.password_entry = self._field(card, "Password", show="\u2022")
        self.confirm_entry = self._field(card, "Confirm Password", show="\u2022")

        tk.Label(card, text="I am registering as", bg="white", fg=TEXT,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(10, 2))
        self.role_combo = ttk.Combobox(
            card, width=32, state="readonly", values=list(ROLE_OPTIONS.keys()),
        )
        self.role_combo.pack(ipady=4)
        self.role_combo.bind("<<ComboboxSelected>>", self._on_role_change)

        self.profile_label_widget = tk.Label(card, text="", bg="white", fg=TEXT,
                                              font=("Segoe UI", 9, "bold"))
        self.profile_entry = ttk.Entry(card, width=34, font=("Segoe UI", 10))
        # Both packed later, only when the role needs the extra field.

        self.error_label = tk.Label(card, text="", bg="white", fg="#DC3545",
                                     font=("Segoe UI", 9), wraplength=280, justify="left")
        self.error_label.pack(anchor="w", pady=(12, 0))

        ttk.Button(card, text="REGISTER", style="Primary.TButton",
                   command=self.register).pack(fill="x", pady=(14, 16))

        tk.Frame(card, bg=BORDER, height=1).pack(fill="x", pady=(0, 14))

        back_row = tk.Frame(card, bg="white")
        back_row.pack()
        tk.Label(back_row, text="Already have an account?", bg="white", fg=MUTED,
                 font=("Segoe UI", 10)).pack(side="left")
        link = tk.Label(back_row, text="Back to login", bg="white", fg=PRIMARY,
                         font=("Segoe UI", 10, "bold"), cursor="hand2")
        link.pack(side="left", padx=(6, 0))
        link.bind("<Button-1>", lambda e: controller.go_to_login())

        self.name_entry.focus_set()

    def _field(self, parent, label_text, show=None):
        tk.Label(parent, text=label_text, bg="white", fg="#1F2937",
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(8, 2))
        entry = ttk.Entry(parent, width=34, font=("Segoe UI", 10), show=show or "")
        entry.pack(ipady=4)
        return entry

    def _on_role_change(self, event=None):
        role = ROLE_OPTIONS.get(self.role_combo.get())
        self.profile_label_widget.pack_forget()
        self.profile_entry.pack_forget()
        self.profile_entry.delete(0, tk.END)

        if role in ROLE_PROFILE:
            label_text, _table, _column = ROLE_PROFILE[role]
            self.profile_label_widget.config(text=label_text)
            self.profile_label_widget.pack(anchor="w", pady=(8, 2), before=self.error_label)
            self.profile_entry.pack(ipady=4, before=self.error_label)

    def register(self):
        name = self.name_entry.get().strip()
        email = self.email_entry.get().strip()
        password = self.password_entry.get()
        confirm = self.confirm_entry.get()
        role_label = self.role_combo.get()
        profile_value = self.profile_entry.get().strip()

        # ---- constraints ----
        if not name or not email or not password or not role_label:
            self.error_label.config(text="Name, email, password and role are required.")
            return
        if not EMAIL_RE.match(email):
            self.error_label.config(text="Enter a valid email address.")
            return
        if len(password) < 6:
            self.error_label.config(text="Password must be at least 6 characters.")
            return
        if password != confirm:
            self.error_label.config(text="Passwords do not match.")
            return

        role = ROLE_OPTIONS[role_label]
        if role in ROLE_PROFILE:
            label_text, table, column = ROLE_PROFILE[role]
            if not profile_value:
                self.error_label.config(text=f"{label_text} is required.")
                return

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT 1 FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                self.error_label.config(text="An account with this email already exists.")
                cursor.close()
                conn.close()
                return

            # Find whichever "name" column your users table actually has,
            # instead of guessing and risking a NOT-NULL insert failure.
            cursor.execute("SHOW COLUMNS FROM users")
            user_columns = {row[0] for row in cursor.fetchall()}
            name_column = next(
                (c for c in ("full_name", "name", "fullname", "username", "user_name")
                 if c in user_columns),
                None,
            )

            if name_column:
                cursor.execute(
                    f"INSERT INTO users ({name_column}, email, password, role) "
                    f"VALUES (%s, %s, %s, %s)",
                    (name, email, password, role),
                )
            else:
                cursor.execute(
                    "INSERT INTO users (email, password, role) VALUES (%s, %s, %s)",
                    (email, password, role),
                )

            user_id = cursor.lastrowid

            if role in ROLE_PROFILE:
                _label, table, column = ROLE_PROFILE[role]
                cursor.execute(
                    f"INSERT INTO {table} (user_id, {column}) VALUES (%s, %s)",
                    (user_id, profile_value),
                )
            elif role == "VOLUNTEER":
                cursor.execute(
                    "INSERT INTO volunteers (user_id) VALUES (%s)",
                    (user_id,),
                )

            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            messagebox.showerror("Database Error", str(e))
            return

        messagebox.showinfo("Success", "Account created! Please log in.")
        self.controller.go_to_login(prefill_email=email)

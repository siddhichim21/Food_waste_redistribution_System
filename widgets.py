import tkinter as tk
from tkinter import ttk
from theme import PRIMARY, MUTED, BORDER


def build_topbar(parent, title, controller, subtitle=None, logout_command=None):
    """A colored header bar used at the top of every dashboard page."""
    bar = tk.Frame(parent, bg=PRIMARY, height=70)
    bar.pack(fill="x")
    bar.pack_propagate(False)

    text_frame = tk.Frame(bar, bg=PRIMARY)
    text_frame.pack(side="left", padx=25)
    tk.Label(
        text_frame, text=title, bg=PRIMARY, fg="white",
        font=("Segoe UI", 16, "bold"),
    ).pack(anchor="w", pady=(12, 0))
    if subtitle:
        tk.Label(
            text_frame, text=subtitle, bg=PRIMARY, fg="#D9F0E4",
            font=("Segoe UI", 9),
        ).pack(anchor="w")

    if logout_command:
        ttk.Button(
            bar, text="Logout", style="Danger.TButton", command=logout_command
        ).pack(side="right", padx=20, pady=15)

    return bar


def stat_card(parent, label, value, color):
    """A small white metric tile used on the admin overview."""
    card = tk.Frame(parent, bg="white", highlightbackground=BORDER, highlightthickness=1)
    tk.Label(
        card, text=str(value), bg="white", fg=color, font=("Segoe UI", 22, "bold")
    ).pack(pady=(18, 0))
    tk.Label(
        card, text=label, bg="white", fg=MUTED, font=("Segoe UI", 10)
    ).pack(pady=(0, 16))
    return card

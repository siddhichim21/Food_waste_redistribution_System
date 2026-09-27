import tkinter as tk
from tkinter import ttk

# ---- Palette -----------------------------------------------------------
BG = "#F4F6F8"
SURFACE = "#FFFFFF"
PRIMARY = "#2E7D5B"
PRIMARY_DARK = "#1F5C41"
ACCENT = "#FF8A3D"
TEXT = "#1F2937"
MUTED = "#6B7280"
DANGER = "#DC3545"
SUCCESS = "#1F8A46"
BORDER = "#E2E8F0"

FONT_TITLE = ("Segoe UI", 22, "bold")
FONT_SUBTITLE = ("Segoe UI", 13)
FONT_LABEL = ("Segoe UI", 10, "bold")
FONT_BODY = ("Segoe UI", 10)
FONT_BUTTON = ("Segoe UI", 10, "bold")


def apply_theme(root):
    root.configure(bg=BG)
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    style.configure("TFrame", background=BG)
    style.configure("Card.TFrame", background=SURFACE)
    style.configure("TLabel", background=BG, foreground=TEXT, font=FONT_BODY)
    style.configure("Card.TLabel", background=SURFACE, foreground=TEXT, font=FONT_BODY)
    style.configure("Title.TLabel", background=BG, foreground=PRIMARY_DARK, font=FONT_TITLE)
    style.configure("Muted.TLabel", background=BG, foreground=MUTED, font=FONT_BODY)

    style.configure(
        "Primary.TButton",
        background=PRIMARY, foreground="white",
        font=FONT_BUTTON, padding=10, borderwidth=0,
    )
    style.map("Primary.TButton", background=[("active", PRIMARY_DARK)])

    style.configure(
        "Accent.TButton",
        background=ACCENT, foreground="white",
        font=FONT_BUTTON, padding=10, borderwidth=0,
    )
    style.map("Accent.TButton", background=[("active", "#E67329")])

    style.configure(
        "Danger.TButton",
        background=DANGER, foreground="white",
        font=FONT_BUTTON, padding=8, borderwidth=0,
    )
    style.map("Danger.TButton", background=[("active", "#B02A37")])

    style.configure("TEntry", fieldbackground="white", padding=6)
    style.configure("TCombobox", fieldbackground="white", padding=4)

    style.configure(
        "Treeview",
        background="white", fieldbackground="white", foreground=TEXT,
        rowheight=28, font=FONT_BODY, borderwidth=0,
    )
    style.configure(
        "Treeview.Heading",
        background=PRIMARY, foreground="white", font=FONT_LABEL, relief="flat",
    )
    style.map("Treeview.Heading", background=[("active", PRIMARY_DARK)])
    style.map("Treeview", background=[("selected", PRIMARY)], foreground=[("selected", "white")])

"""Theme graphique de l'application (couleurs + styles ttk)."""
import tkinter as tk
from tkinter import ttk

DARK = "#1a1a1a"
BG = "#f4f1ec"
CARD = "#ffffff"
ACCENT = "#c9a96e"
ACCENT_HOVER = "#b8944f"
TEXT = "#1f2937"
MUTED = "#6b7280"
SUCCESS = "#16a34a"
DANGER = "#dc2626"
WARNING = "#d97706"

FONT = ("Segoe UI", 10)
FONT_BOLD = ("Segoe UI", 10, "bold")
FONT_TITLE = ("Playfair Display", 16, "bold")
FONT_SMALL = ("Segoe UI", 9)


def setup_style(root: tk.Tk):
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    style.configure(".", background=BG, foreground=TEXT, font=FONT)
    style.configure("TFrame", background=BG)
    style.configure("Card.TFrame", background=CARD)
    style.configure("Dark.TFrame", background=DARK)
    style.configure("TLabel", background=BG, foreground=TEXT)
    style.configure("Card.TLabel", background=CARD, foreground=TEXT)
    style.configure("Muted.TLabel", background=CARD, foreground=MUTED,
                    font=FONT_SMALL)
    style.configure("Title.TLabel", background=CARD, foreground=TEXT,
                    font=FONT_TITLE)
    style.configure("H2.TLabel", background=CARD, foreground=TEXT,
                    font=("Segoe UI", 12, "bold"))

    style.configure("TButton", background="#e5e0d8", foreground=TEXT,
                    padding=(10, 6), borderwidth=0)
    style.map("TButton",
              background=[("active", "#d8d2c6"), ("pressed", "#cfc8ba")])

    style.configure("Accent.TButton", background=ACCENT, foreground="#1a1a1a",
                    font=FONT_BOLD, padding=(12, 7))
    style.map("Accent.TButton",
              background=[("active", ACCENT_HOVER), ("pressed", "#a5833f")],
              foreground=[("active", "#1a1a1a")])

    style.configure("Danger.TButton", background=DANGER, foreground="white",
                    padding=(10, 6))
    style.map("Danger.TButton", background=[("active", "#b91c1c")])

    style.configure("Success.TButton", background=SUCCESS, foreground="white",
                    font=FONT_BOLD, padding=(12, 7))
    style.map("Success.TButton", background=[("active", "#15803d")])

    style.configure("TNotebook", background=BG, borderwidth=0, tabmargins=(0, 0, 0, 0))
    style.configure("TNotebook.Tab", background="#e9e4da", foreground=MUTED,
                    padding=(18, 9), font=FONT_BOLD)
    style.map("TNotebook.Tab",
              background=[("selected", CARD)],
              foreground=[("selected", TEXT)])

    style.configure("Treeview", background=CARD, fieldbackground=CARD,
                    foreground=TEXT, rowheight=28, borderwidth=0)
    style.configure("Treeview.Heading", background="#efe9de", foreground=TEXT,
                    font=FONT_BOLD, padding=(6, 6), relief="flat")
    style.map("Treeview", background=[("selected", ACCENT)],
              foreground=[("selected", "#1a1a1a")])
    style.map("Treeview.Heading", background=[("active", "#e5ddcd")])

    style.configure("TLabelframe", background=CARD, borderwidth=0)
    style.configure("TLabelframe.Label", background=CARD, foreground=TEXT,
                    font=FONT_BOLD)

    style.configure("TEntry", fieldbackground="white", padding=5)
    style.configure("TCombobox", fieldbackground="white", padding=4)


def money(amount) -> str:
    return f"{float(amount):,.0f}".replace(",", " ") + " FCFA"

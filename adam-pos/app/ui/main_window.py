"""Fenetre principale : en-tete + onglets selon le role de l'utilisateur."""
import tkinter as tk
from tkinter import ttk
from datetime import datetime

from . import theme
from .widgets import Scrollable
from .views.cash_view import CashView
from .views.floor_view import FloorView
from .views.menu_view import MenuView
from .views.pos_view import PosView
from .views.reports_view import ReportsView
from .views.staff_view import StaffView
from .views.stock_view import StockView
from .views.suppliers_view import SuppliersView


class MainWindow(tk.Tk):
    def __init__(self, state, on_logout=None):
        super().__init__()
        self.state = state
        self.logout_requested = False
        self.title("Restaurant ADAM — Gestion")
        # Taille minimale adaptee a l'ecran : sur un petit ecran la fenetre
        # ne doit PAS etre plus large/haute que ce que l'ecran peut afficher.
        self.minsize(min(900, self.winfo_screenwidth()),
                     min(560, self.winfo_screenheight()))
        self.configure(bg=theme.BG)
        theme.setup_style(self)
        self.views = []
        self._build()
        self._center()
        self.bind("<Escape>", lambda e: self.do_logout())

    def _center(self):
        """Utilise tout l'espace disponible a l'ecran, sans jamais depasser
        celui-ci meme sur un petit ecran."""
        self.update_idletasks()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        w = max(560, min(sw - 20, sw))
        h = max(400, min(sh - 80, sh))
        x = max(0, (sw - w) // 2)
        y = max(0, (sh - h) // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")
        try:
            self.wm_state("zoomed")           # Windows
        except tk.TclError:
            try:
                self.attributes("-zoomed", True)  # Linux
            except tk.TclError:
                pass

    # ------------------------------------------------------------- header --
    def _build(self):
        user = self.state.user
        settings = self.state.settings

        header = tk.Frame(self, bg=theme.DARK, height=58)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(header, text="ADAM", font=("Playfair Display", 17, "bold"),
                 bg=theme.DARK, fg=theme.ACCENT).pack(side="left", padx=(18, 2))
        tk.Label(header, text="· " + settings.get("restaurant_name", ""),
                 font=theme.FONT_SMALL, bg=theme.DARK,
                 fg="#8a8378").pack(side="left", pady=(6, 0))

        right = tk.Frame(header, bg=theme.DARK)
        right.pack(side="right", padx=14)

        role_label = self.state.role_label() or "Administrateur"
        tk.Label(right, text=f"{user['name']}", font=theme.FONT_BOLD,
                 bg=theme.DARK, fg="white").pack(side="left", padx=4)
        badge = tk.Label(right, text=role_label.upper(), font=("Segoe UI", 8, "bold"),
                         bg="#3a332a", fg=theme.ACCENT, padx=7, pady=2)
        badge.pack(side="left", padx=(2, 12))

        self.clock = tk.Label(right, text="", font=theme.FONT_SMALL,
                              bg=theme.DARK, fg="#9ca3af")
        self.clock.pack(side="left", padx=10)

        ttk.Button(right, text=self.state.tr("main.logout"),
                   command=self.do_logout).pack(side="left", padx=(8, 0))

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=0, pady=0)

        tabs = []
        if self.state.can_access("dashboard"):
            tabs.append(("tab.dashboard", ReportsView))
        if self.state.can_access("pos"):
            tabs.append(("tab.pos", PosView))
        if self.state.can_access("cash"):
            tabs.append(("tab.cash", CashView))
        if self.state.can_access("floor"):
            tabs.append(("tab.floor", FloorView))
        if self.state.can_access("menu"):
            tabs.append(("tab.menu", MenuView))
        if self.state.can_access("stock"):
            tabs.append(("tab.stock", StockView))
        if self.state.can_access("suppliers"):
            tabs.append(("tab.suppliers", SuppliersView))
        if self.state.can_access("staff"):
            tabs.append(("tab.staff", StaffView))

        for key, ViewCls in tabs:
            label = self.state.tr(key)
            if ViewCls is PosView:
                # Le POS gere son propre defilement (grille produits + panier)
                # et doit remplir tout l'onglet : pas de conteneur externe.
                view = ViewCls(self.notebook, self.state)
                self.notebook.add(view, text="  " + label + "  ")
            else:
                scroll = Scrollable(self.notebook,
                                    make_view=ViewCls, state=self.state)
                self.notebook.add(scroll, text="  " + label + "  ")
                view = scroll.view
            self.views.append(view)

        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)
        self._after_id = None
        self._tick()

    def _tick(self):
        try:
            self.clock.config(text=datetime.now().strftime("%a %d %b %Y   %H:%M:%S"))
        except tk.TclError:
            return
        self._after_id = self.after(1000, self._tick)

    def destroy(self):
        if self._after_id:
            try:
                self.after_cancel(self._after_id)
            except tk.TclError:
                pass
            self._after_id = None
        super().destroy()

    def _on_tab_changed(self, _event):
        widget = self.nametowidget(self.notebook.select())
        if isinstance(widget, Scrollable):
            widget = widget.view
        if hasattr(widget, "refresh"):
            try:
                widget.refresh()
            except Exception as exc:
                from .widgets import show_error
                show_error(self, self.state.tr("main.error_display", err=exc))

    def do_logout(self):
        import tkinter.messagebox as mb
        if mb.askyesno(self.state.tr("common.confirm_title"),
                       self.state.tr("main.confirm_logout"), parent=self):
            # Fermer la caisse ouverte
            try:
                self.state.cash.auto_close_on_logout(self.state.user)
            except Exception:
                pass
            # Liberer les tables occupees par les commandes ouvertes
            # de cet utilisateur
            try:
                for o in self.state.orders.open_orders():
                    if (o.get("created_by") == self.state.user["name"]
                            and o.get("unit_id") and self.state.floor):
                        self.state.floor.set_status(o["unit_id"], "free")
            except Exception:
                pass
            self.logout_requested = True
            self.state.logout()
            self.destroy()

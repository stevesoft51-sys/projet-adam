"""Widgets reutilisables : cartes KPI, boites de dialogue, helpers."""
import tkinter as tk
from tkinter import ttk

from . import theme
from ..i18n import TGlobal
from ..services import BizError
from datetime import date, timedelta


class Scrollable(ttk.Frame):
    """Conteneur a defilement vertical.

    Contient un objet `view` (la vue d'onglet) et permet de faire defiler
    son contenu quand celui-ci depasse la hauteur disponible (ecrans
    plus petits). Tous les boutons/sections restent donc accessibles.
    Le defilement se fait a la molette et aux fleches.
    """

    def __init__(self, parent, make_view=None, *args, **kwargs):
        super().__init__(parent, style="TFrame")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.canvas = tk.Canvas(self, bg=theme.BG, highlightthickness=0)
        vbar = ttk.Scrollbar(self, orient="vertical",
                             command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=vbar.set)
        vbar.grid(row=0, column=1, sticky="ns")
        self.canvas.grid(row=0, column=0, sticky="nsew")

        self.view = make_view(self.canvas, *args, **kwargs)
        self._win = self.canvas.create_window((0, 0), window=self.view,
                                               anchor="nw", width=0)
        self.canvas.bind("<Configure>", self._sync_width)
        self.view.bind("<Configure>", self._refresh_scrollregion)
        self.after(50, self._refresh_scrollregion)
        self._bind_wheel(self.view)
        self.canvas.bind("<MouseWheel>", self._on_wheel)
        self.canvas.bind("<Button-4>", self._on_wheel)
        self.canvas.bind("<Button-5>", self._on_wheel)
        self.canvas.bind("<Up>", lambda e: self.canvas.yview_scroll(-1, "units"))
        self.canvas.bind("<Down>",
                         lambda e: self.canvas.yview_scroll(1, "units"))

    def _bind_wheel(self, widget):
        """Relie la molette a defiler, y compris sur les sous-widgets.
        On evite bind_all pour ne pas entrer en conflit avec les zones qui
        gerent leur propre defilement (ex: grille produit du POS)."""
        for seq in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
            try:
                widget.bind(seq, self._on_wheel)
            except tk.TclError:
                pass
        try:
            for child in widget.winfo_children():
                self._bind_wheel(child)
        except tk.TclError:
            pass

    def _sync_width(self, event):
        try:
            self.canvas.itemconfigure(self._win, width=event.width)
            self.after(10, self._refresh_scrollregion)
        except tk.TclError:
            pass

    def _refresh_scrollregion(self, _event=None):
        try:
            self.update_idletasks()
            ch = self.canvas.winfo_height()
            req = self.view.winfo_reqheight()
            if req < ch:
                self.canvas.itemconfigure(self._win, height=ch)
            else:
                self.canvas.itemconfigure(self._win, height=req)
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        except tk.TclError:
            pass

    def _on_wheel(self, event):
        if event.num == 4:
            self.canvas.yview_scroll(-1, "units")
            return "break"
        if event.num == 5:
            self.canvas.yview_scroll(1, "units")
            return "break"
        if getattr(event, "delta", 0):
            delta = -1 if event.delta > 0 else 1
            self.canvas.yview_scroll(delta, "units")
            return "break"


class CalendarPopup:
    def __init__(self, parent, anchor_widget, on_select, initial=None,
                 min_date=None, max_date=None, title=None):
        self.root = parent.winfo_toplevel()
        self.on_select = on_select
        self.anchor = anchor_widget
        self.title = title or TGlobal("cal.title")
        self.min_date = min_date or date(2000, 1, 1)
        self.max_date = max_date or date(2100, 12, 31)
        cur = initial or date.today()
        self.year, self.month = cur.year, cur.month
        self.selected = cur if initial else None
        self._build()
        self._show()

    def _build(self):
        f = tk.Toplevel(self.root)
        f.withdraw()
        f.overrideredirect(True)
        f.configure(bg=theme.CARD, highlightthickness=1,
                    highlightbackground="#b9ae95")
        self.win = f
        head = tk.Frame(f, bg="#fdf6e7")
        head.pack(fill="x", padx=6, pady=6)
        ttk.Button(head, text="◀", width=3, command=self._prev).pack(side="left")
        self.lbl = tk.Label(head, text="", bg="#fdf6e7", fg=theme.ACCENT_HOVER,
                            font=theme.FONT_BOLD, width=14)
        self.lbl.pack(side="left", expand=True)
        ttk.Button(head, text="▶", width=3, command=self._next).pack(side="right")
        grid = tk.Frame(f, bg=theme.CARD)
        grid.pack(padx=6, pady=(0, 6))
        self.grid = grid
        self.buttons = {}
        for i, wname in enumerate(_cal_weekdays()):
            tk.Label(grid, text=wname, bg=theme.CARD, fg=theme.MUTED,
                     font=("Segoe UI", 8, "bold"), width=3
                     ).grid(row=0, column=i, padx=2, pady=2)
        self._draw()
        tk.Label(f, text=self.title, bg=theme.CARD, fg=theme.MUTED,
                 font=theme.FONT_SMALL).pack(anchor="w", padx=8, pady=(0, 6))

    def _prev(self):
        if self.month == 1:
            self.month, self.year = 12, self.year - 1
        else:
            self.month -= 1
        self._draw()

    def _next(self):
        if self.month == 12:
            self.month, self.year = 1, self.year + 1
        else:
            self.month += 1
        self._draw()

    def _draw(self):
        for w in self.buttons.values():
            w.destroy()
        self.buttons = {}
        self.lbl.config(text=f"{self._month_name()} {self.year}")
        first = date(self.year, self.month, 1)
        start_col = first.weekday()
        if self.month == 12:
            ndays = date(self.year + 1, 1, 1) - timedelta(days=1)
        else:
            ndays = date(self.year, self.month + 1, 1) - timedelta(days=1)
        ndays = ndays.day
        for d in range(1, ndays + 1):
            row = (start_col + d - 1) // 7 + 1
            col = (start_col + d - 1) % 7
            dd = date(self.year, self.month, d)
            enabled = self.min_date <= dd <= self.max_date
            is_sel = dd == self.selected
            bg = theme.ACCENT if is_sel else theme.CARD
            b = tk.Label(self.grid, text=str(d), bg=bg,
                         fg="#1a1a1a" if is_sel else
                         (theme.TEXT if enabled else "#c8c2b8"),
                         font=("Segoe UI", 9), width=3)
            b.grid(row=row, column=col, padx=1, pady=1)
            if enabled:
                b.bind("<Button-1>", lambda e, x=dd: self._pick(x))
            self.buttons[(self.year, self.month, d)] = b

    def _month_name(self):
        return _cal_month_name(self.month)

    def _pick(self, dd):
        self.win.destroy()
        self.on_select(dd.strftime("%Y-%m-%d"))

    def _show(self):
        self.win.update_idletasks()
        try:
            x = self.anchor.winfo_rootx()
            y = self.anchor.winfo_rooty() + self.anchor.winfo_height() + 2
            w = self.win.winfo_reqwidth()
            h = self.win.winfo_reqheight()
            sw = self.root.winfo_screenwidth()
            sh = self.root.winfo_screenheight()
            if x + w > sw:
                x = sw - w - 4
            if y + h > sh:
                y = self.anchor.winfo_rooty() - h - 2
            self.win.geometry(f"+{x}+{y}")
        except tk.TclError:
            pass
        self.win.deiconify()
        self.win.lift()
        self.win.focus_set()


def _cal_weekdays():
    name = TGlobal("cal.weekdays")
    parts = [p for p in name.split("|") if p]
    if len(parts) >= 7:
        return parts[:7]
    return ["Lu", "Ma", "Me", "Je", "Ve", "Sa", "Di"]


def _cal_month_name(m):
    name = TGlobal("cal.months")
    parts = [x for x in name.split("|") if x]
    if parts and 1 <= m <= len(parts):
        return parts[m - 1]
    return str(m)


def card(parent, **pack) -> ttk.Frame:
    """Cadre blanc arrondi (visuel carte) avec padding."""
    outer = tk.Frame(parent, bg=theme.BG)
    inner = tk.Frame(outer, bg=theme.CARD, highlightthickness=1,
                     highlightbackground="#e5ded0")
    inner.pack(fill="both", expand=True, padx=1, pady=1)
    pack.setdefault("fill", "x")
    pack.setdefault("pady", 6)
    outer.pack(**pack)
    return inner


class DataGrid(tk.Frame):
    """Tableau simple avec de VERITABLES lignes de separation fines
    autour de chaque cellule (contrairement au Treeview de Tk qui ne
    sait pas dessiner de grille). Supporte des images par colonne et
    la selection d'une ligne."""

    SEP = "#c9c1b0"
    HEAD_BG = "#ece5d4"
    ZEBRA = "#faf6ec"
    SELECT_BG = "#f0e4cd"

    def __init__(self, parent, columns):
        """columns : liste de (cle, titre, largeur_min, ancre, extensible)"""
        super().__init__(parent, bg="white", highlightthickness=1,
                         highlightbackground=DataGrid.SEP)
        self.columns = columns
        self.on_select = None
        self.selected_row = None
        self._row_labels = {}
        self._row_bgs = {}
        self.canvas = tk.Canvas(self, bg="white", highlightthickness=0)
        self.vsb = ttk.Scrollbar(self, orient="vertical",
                                 command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)
        self.inner = tk.Frame(self.canvas, bg="white")
        self.win = self.canvas.create_window((0, 0), window=self.inner,
                                             anchor="nw")
        self.inner.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")))
        self.canvas.bind(
            "<Configure>", self._sync_width)
        self._col_widths = [width for (_k, _t, width, _a, _s) in columns]
        for seq in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
            self.canvas.bind(seq, self._wheel)
        self.vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        for c, (_key, title, width, anc, stretch) in enumerate(columns):
            self.inner.columnconfigure(c, minsize=width,
                                       weight=1 if stretch else 0)
            tk.Label(self.inner, text=title.upper(),
                     bg=DataGrid.HEAD_BG, fg=theme.TEXT,
                     font=("Segoe UI", 9, "bold"), anchor=anc,
                     padx=8, pady=6,
                     highlightbackground=DataGrid.SEP,
                     highlightthickness=1
                     ).grid(row=0, column=c, sticky="nsew")

    def _sync_width(self, event):
        """Largeur des colonnes adaptee a l'ecran : si la somme des largeurs
        minimales depasse la largeur disponible, les colonnes sont reduites
        proportionnellement pour qu'aucune n'ait plus large que l'ecran."""
        try:
            self.canvas.itemconfig(self.win, width=event.width)
        except tk.TclError:
            return
        if not getattr(self, "_col_widths", None):
            return
        avail = event.width - 2
        if avail <= 10:
            return
        total = sum(self._col_widths)
        factor = max(0.35, avail / total) if total > avail else 1.0
        for c, w in enumerate(self._col_widths):
            try:
                self.inner.columnconfigure(c, minsize=max(30, int(w * factor)))
            except tk.TclError:
                pass

    def _wheel(self, event):
        delta = -1 if getattr(event, "delta", 120) > 0 or event.num == 4 else 1
        self.canvas.yview_scroll(delta, "units")

    def add_row(self, values, fg=None, bg=None, fonts=None, images=None):
        """Ajoute une ligne ; fg/fonts/images peuvent etre uniques ou
        par colonne (images[c] = PhotoImage ou None)."""
        r = self.inner.grid_size()[1]
        zebra = bg or ("white" if r % 2 else DataGrid.ZEBRA)
        labels = []
        for c, val in enumerate(values):
            key, _t, _w, anc, _st = self.columns[c]
            color = fg[c] if isinstance(fg, (list, tuple)) else (fg or theme.TEXT)
            font = fonts[c] if isinstance(fonts, (list, tuple)) \
                else (fonts or theme.FONT)
            lbl = tk.Label(self.inner, text=str(val), bg=zebra, fg=color,
                           font=font, anchor=anc, padx=8, pady=5,
                           highlightbackground=DataGrid.SEP,
                           highlightthickness=1)
            if images is not None:
                img = images[c] if isinstance(images, (list, tuple)) \
                    else images
                if img is not None:
                    lbl.configure(image=img)
            lbl.grid(row=r, column=c, sticky="nsew")
            lbl.bind("<Button-1>", lambda _e, rr=r: self.select_row(rr))
            labels.append(lbl)
        self._row_labels[r] = labels
        self._row_bgs[r] = zebra
        return r

    def select_row(self, r):
        if self.selected_row is not None \
                and self.selected_row in self._row_labels:
            old = self._row_bgs.get(self.selected_row, "white")
            for lbl in self._row_labels[self.selected_row]:
                try:
                    lbl.configure(bg=old)
                except tk.TclError:
                    pass
        self.selected_row = r
        for lbl in self._row_labels.get(r, []):
            lbl.configure(bg=DataGrid.SELECT_BG)
        if self.on_select:
            self.on_select(r)


def kpi_card(parent, title: str, value: str, subtitle="", color=None):
    body = card(parent)
    tk.Label(body, text=title.upper(), bg=theme.CARD, fg=theme.MUTED,
             font=theme.FONT_SMALL).pack(anchor="w", padx=14, pady=(12, 2))
    vcolor = color or theme.TEXT
    tk.Label(body, text=value, bg=theme.CARD, fg=vcolor,
             font=("Segoe UI", 17, "bold")).pack(anchor="w", padx=14)
    if subtitle:
        tk.Label(body, text=subtitle, bg=theme.CARD, fg=theme.MUTED,
                 font=theme.FONT_SMALL).pack(anchor="w", padx=14, pady=(2, 10))
    else:
        tk.Label(body, text="", bg=theme.CARD).pack(pady=(2, 6))
    return body


class Dialog(tk.Toplevel):
    """Boite de dialogue modale avec zone formulaire et boutons."""

    def __init__(self, parent, title: str, width=420):
        super().__init__(parent)
        self.title(title)
        self.configure(bg=theme.CARD)
        self.resizable(False, False)
        self.transient(parent.winfo_toplevel())
        self.grab_set()
        self.result = None
        self.body = tk.Frame(self, bg=theme.CARD, padx=18, pady=14)
        self.body.pack(fill="both", expand=True)
        self.footer = tk.Frame(self, bg=theme.CARD)
        self.footer.pack(fill="x", padx=18, pady=(0, 14))
        self._center(width)

    def _center(self, width):
        self.update_idletasks()
        w = width
        h = self.winfo_reqheight()
        x = max(0, (self.winfo_screenwidth() - w) // 2)
        y = max(0, (self.winfo_screenheight() - h) // 3)
        self.geometry(f"{w}x{h}+{x}+{y}")

    def add_buttons(self, on_ok, ok_text="Enregistrer", ok_style="Accent.TButton"):
        def cancel():
            self.destroy()

        def ok():
            if on_ok():
                self.destroy()

        btns = tk.Frame(self.footer, bg=theme.CARD)
        btns.pack()
        ttk.Button(btns, text=TGlobal("common.cancel"), command=cancel,
                   width=10).pack(side="left", padx=4)
        ttk.Button(btns, text=ok_text, style=ok_style, command=ok, width=14).pack(
            side="left", padx=4)
        self.bind("<Escape>", lambda e: cancel())
        self.bind("<Return>", lambda e: ok())

    def error(self, label: tk.Label, msg: str):
        label.config(text=msg, fg=theme.DANGER)

def form_row(parent, label_text, widget) -> tk.Frame:
    row = tk.Frame(parent, bg=theme.CARD)
    row.pack(fill="x", pady=4)
    tk.Label(row, text=label_text, bg=theme.CARD, fg=theme.MUTED,
             font=theme.FONT_SMALL, width=18, anchor="w").pack(side="left")
    widget.pack(side="left", fill="x", expand=True)
    return row


def ask_string(parent, title, label, initial="", required=True) -> str | None:
    d = Dialog(parent, title, width=380)
    err = tk.Label(d.body, bg=theme.CARD, font=theme.FONT_SMALL)
    entry = ttk.Entry(d.body, font=theme.FONT)
    form_row(d.body, label, entry)
    err.pack(anchor="w", pady=(2, 0))
    entry.insert(0, initial)

    def submit():
        val = entry.get().strip()
        if required and not val:
            d.error(err, TGlobal("common.required"))
            return False
        d.result = val
        return True

    d.add_buttons(submit, TGlobal("common.validate"))
    d.wait_window()
    return d.result


def ask_float(parent, title, label, initial="") -> float | None:
    val = ask_string(parent, title, label, initial)
    if val is None:
        return None
    try:
        return float(val.replace(",", ".").replace(" ", ""))
    except ValueError:
        from tkinter.messagebox import showerror
        showerror(TGlobal("common.error_title"), TGlobal("common.invalid_number"),
                  parent=parent)
        return None


def confirm(parent, message) -> bool:
    from tkinter.messagebox import askyesno
    return askyesno(TGlobal("common.confirm_title"), message, parent=parent)


def info(parent, message):
    from tkinter.messagebox import showinfo
    showinfo(TGlobal("common.info_title"), message, parent=parent)


def show_error(parent, message):
    from tkinter.messagebox import showerror
    showerror(TGlobal("common.error_title"), str(message), parent=parent)


def clear(frame: tk.Frame):
    for child in frame.winfo_children():
        child.destroy()

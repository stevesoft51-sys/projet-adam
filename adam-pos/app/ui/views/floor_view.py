"""Onglet Plan de salle (admin) : tables et boucaros.

Meme principe que Stocks : formulaires FLOTTANTS camoufles dans l'onglet,
aucune fenetre de dialogue ; tableaux DataGrid avec vraies separations.
"""
import tkinter as tk
from tkinter import ttk

from .. import theme
from ...services import TABLE_STATUSES
from ..widgets import DataGrid, clear, confirm, show_error


class FloorView(ttk.Frame):
    def __init__(self, parent, state):
        super().__init__(parent, style="TFrame")
        self.state = state
        self._grid_rows = {}
        self._build()
        self.refresh()

    # ------------------------------------------------------------- layout --
    def _build(self):
        holder = tk.Frame(self, bg=theme.CARD, highlightthickness=1,
                          highlightbackground="#e5ded0")
        holder.pack(fill="both", expand=True, padx=10, pady=10)

        top = tk.Frame(holder, bg=theme.CARD)
        top.pack(fill="x", padx=10, pady=(10, 4))
        tk.Label(top, text=self.state.tr("floor.title"),
                 bg=theme.CARD, font=("Segoe UI", 12, "bold")).pack(side="left")
        btns = tk.Frame(top, bg=theme.CARD)
        btns.pack(side="right")
        ttk.Button(btns, text=self.state.tr("floor.add_table"), style="Accent.TButton",
                   command=self.new_table).pack(side="left", padx=2)
        ttk.Button(btns, text=self.state.tr("floor.add_boucaro"), style="Accent.TButton",
                   command=self.new_boucaro).pack(side="left", padx=2)

        self.kpis = tk.Frame(holder, bg=theme.CARD)
        self.kpis.pack(fill="x", padx=12, pady=(2, 6))

        self.grid_holder = tk.Frame(holder, bg=theme.CARD)
        self.grid_holder.pack(fill="both", expand=True, padx=12,
                              pady=(2, 0))

        actions = tk.Frame(holder, bg=theme.CARD)
        actions.pack(fill="x", padx=10, pady=(6, 8))
        ttk.Button(actions, text=self.state.tr("floor.edit_selection"),
                   command=self.edit_selected).pack(side="left")
        ttk.Button(actions, text=self.state.tr("floor.delete"), style="Danger.TButton",
                   command=self.delete_selected).pack(side="left", padx=6)
        tk.Label(actions, text=self.state.tr("floor.selection_status"),
                 bg=theme.CARD, fg=theme.MUTED,
                 font=theme.FONT_SMALL).pack(side="left", padx=(18, 4))
        ttk.Button(actions, text=self.state.tr("floor.status_free"), style="Success.TButton",
                   command=lambda: self._apply_status("free")
                   ).pack(side="left", padx=2)
        ttk.Button(actions, text=self.state.tr("floor.status_occupied"), style="Danger.TButton",
                   command=lambda: self._apply_status("occupied")
                   ).pack(side="left", padx=2)
        ttk.Button(actions, text=self.state.tr("floor.status_reserved"),
                   command=lambda: self._apply_status("reserved")
                   ).pack(side="left", padx=2)

        # section flottante unique (camouffee) pour le formulaire
        self._build_float_section()

    def _build_float_section(self):
        f = tk.Frame(self, bg=theme.CARD, highlightthickness=1,
                     highlightbackground="#b9ae95")
        inner = tk.Frame(f, bg=theme.CARD)
        inner.pack(fill="both", expand=True, padx=1, pady=1)
        self.float_card = f

        banner = tk.Frame(inner, bg="#fdf6e7")
        banner.pack(fill="x")
        self.lbl_title = tk.Label(banner, text="", bg="#fdf6e7",
                                  fg=theme.ACCENT_HOVER,
                                  font=("Segoe UI", 12, "bold"))
        self.lbl_title.pack(anchor="w", padx=18, pady=(10, 2))
        self.lbl_sub = tk.Label(banner, text="", bg="#fdf6e7",
                                fg=theme.MUTED, font=theme.FONT_SMALL)
        self.lbl_sub.pack(anchor="w", padx=18, pady=(0, 10))

        self.f_body = tk.Frame(inner, bg=theme.CARD)
        self.f_body.pack(fill="both", expand=True, padx=18, pady=(10, 4))
        self.f_foot = tk.Frame(inner, bg=theme.CARD)
        self.f_foot.pack(fill="x", padx=18, pady=(6, 14))
        f.bind("<Escape>", lambda e: self._hide_form())

    # ------------------------------------------------- formulaire flottant --
    def _open_form(self, title, sub):
        self.lbl_title.config(text=title)
        self.lbl_sub.config(text=sub)
        clear(self.f_body)
        clear(self.f_foot)
        self.float_card.place(relx=0.5, rely=0.5, anchor="center", width=480)
        self.float_card.lift()

    def _hide_form(self):
        self.float_card.place_forget()

    @staticmethod
    def _frow(body, row, label, widget):
        tk.Label(body, text=label, bg=theme.CARD, fg=theme.MUTED,
                 font=theme.FONT_SMALL, width=16, anchor="w"
                 ).grid(row=row, column=0, sticky="w", pady=5)
        widget.grid(row=row, column=1, sticky="ew", pady=5)

    def new_table(self):
        self._show_unit_form(None, "table")

    def new_boucaro(self):
        self._show_unit_form(None, "boucaro")

    def _show_unit_form(self, unit, kind=None):
        """unit=None : creation du type kind ; sinon modification."""
        kind = kind or unit["kind"]
        self._form_unit = unit
        if unit:
            title = self.state.tr("floor.form_modify", name=unit['name'])
        else:
            title = (self.state.tr("floor.form_new_table")
                     if kind == "table"
                     else self.state.tr("floor.form_new_boucaro"))
        self._open_form(
            title,
            sub=self.state.tr("floor.form_subtitle"))
        body = self.f_body
        body.columnconfigure(1, weight=1)
        self.u_var_kind = tk.StringVar(value=kind)
        kf = tk.Frame(body, bg=theme.CARD)
        for value, txt in (("table", self.state.tr("floor.kind_table")),
                           ("boucaro", self.state.tr("floor.kind_boucaro"))):
            tk.Radiobutton(kf, text=txt, variable=self.u_var_kind,
                           value=value, bg=theme.CARD, selectcolor="#efe9de"
                           ).pack(side="left", padx=4)
        self._frow(body, 0, self.state.tr("floor.label_type"), kf)
        self.u_e_name = ttk.Entry(body)
        self._frow(body, 1, self.state.tr("floor.label_name"), self.u_e_name)
        self.u_e_seats = ttk.Entry(body, justify="right")
        self.u_e_seats.insert(0, str(unit["seats"]) if unit else "4")
        self._frow(body, 2, self.state.tr("floor.label_seats"), self.u_e_seats)
        self.u_e_zone = ttk.Entry(body)
        self._frow(body, 3, self.state.tr("floor.label_zone"), self.u_e_zone)
        self.u_e_note = ttk.Entry(body)
        self._frow(body, 4, self.state.tr("floor.label_note"), self.u_e_note)
        self.u_err = tk.Label(body, bg=theme.CARD, fg=theme.DANGER,
                              font=theme.FONT_SMALL)
        self.u_err.grid(row=5, column=0, columnspan=2, sticky="w")
        if unit:
            self.u_e_name.insert(0, unit["name"])
            self.u_e_zone.insert(0, unit.get("zone") or "")
            self.u_e_note.insert(0, unit.get("note") or "")
        ttk.Button(self.f_foot, text=self.state.tr("floor.cancel"),
                   command=self._hide_form).pack(side="right")
        ttk.Button(self.f_foot, text=self.state.tr("floor.save"), style="Accent.TButton",
                   command=self._save_unit).pack(side="right", padx=8)
        self.u_e_name.focus_set()

    def _save_unit(self):
        try:
            seats_raw = (self.u_e_seats.get() or "0").strip()
            seats = int(float(seats_raw.replace(",", "."))) \
                if seats_raw else 0
        except ValueError:
            self.u_err.config(text=self.state.tr("floor.error_invalid_seats"))
            return
        data = {
            "kind": self.u_var_kind.get(),
            "name": self.u_e_name.get(),
            "seats": seats,
            "zone": self.u_e_zone.get().strip(),
            "note": self.u_e_note.get().strip(),
        }
        try:
            self.state.floor.save_unit(
                data, unit_id=self._form_unit["id"] if self._form_unit
                else None)
        except Exception as exc:
            self.u_err.config(text=str(exc))
            return
        self._hide_form()
        self.refresh()

    # ------------------------------------------------------------- actions --
    def edit_selected(self):
        unit = self._selected()
        if not unit:
            show_error(self, self.state.tr("floor.error_select_row"))
            return
        self._show_unit_form(unit)

    def delete_selected(self):
        unit = self._selected()
        if not unit:
            show_error(self, self.state.tr("floor.error_select_row"))
            return
        if not confirm(self, self.state.tr("floor.confirm_delete", name=unit['name'])):
            return
        self.state.floor.delete_unit(unit["id"])
        self.refresh()

    def _apply_status(self, status):
        unit = self._selected()
        if not unit:
            show_error(self, self.state.tr("floor.error_select_unit"))
            return
        try:
            self.state.floor.set_status(unit["id"], status)
        except Exception as exc:
            show_error(self, exc)
            return
        self.refresh()

    def _selected(self):
        r = getattr(self.grid, "selected_row", None)
        return self._grid_rows.get(r) if r is not None else None

    # ------------------------------------------------------------- refresh --
    def refresh(self):
        units = self.state.floor.units()
        tables = [u for u in units if u["kind"] == "table"]
        bouc = [u for u in units if u["kind"] == "boucaro"]
        counts = {k: sum(1 for u in units if u["status"] == k)
                  for k in TABLE_STATUSES}

        clear(self.kpis)
        for title, val, color in (
                (self.state.tr("floor.kpi_tables"), str(len(tables)), theme.TEXT),
                (self.state.tr("floor.kpi_boucaros"), str(len(bouc)), theme.TEXT),
                (self.state.tr("floor.kpi_free"), str(counts["free"]), theme.SUCCESS),
                (self.state.tr("floor.kpi_occupied"), str(counts["occupied"]), theme.DANGER),
                (self.state.tr("floor.kpi_reserved"), str(counts["reserved"]), "#a2701c")):
            f = tk.Frame(self.kpis, bg=theme.CARD)
            f.pack(side="left", padx=(0, 30))
            tk.Label(f, text=title.upper(), bg=theme.CARD, fg=theme.MUTED,
                     font=theme.FONT_SMALL).pack(anchor="w")
            tk.Label(f, text=val, bg=theme.CARD, fg=color,
                     font=("Segoe UI", 13, "bold")).pack(anchor="w")

        for w in self.grid_holder.winfo_children():
            w.destroy()
        self.grid = DataGrid(self.grid_holder, [
            ("type", self.state.tr("floor.col_type"), 90, "center", False),
            ("name", self.state.tr("floor.col_name"), 120, "w", True),
            ("seats", self.state.tr("floor.col_seats"), 80, "center", False),
            ("zone", self.state.tr("floor.col_zone"), 150, "w", True),
            ("note", self.state.tr("floor.col_note"), 180, "w", True),
            ("status", self.state.tr("floor.col_status"), 110, "center", False),
        ])
        self.grid.pack(fill="both", expand=True)
        self._grid_rows = {}
        st_fg = {"free": theme.SUCCESS, "occupied": theme.DANGER,
                 "reserved": "#a2701c"}
        for u in units:
            r = self.grid.add_row(
                (self.state.tr("floor.kind_table") if u["kind"] == "table"
                 else self.state.tr("floor.kind_boucaro"),
                 u["name"], u.get("seats", ""), u.get("zone", ""),
                 u.get("note", ""), TABLE_STATUSES[u["status"]]),
                fg=[theme.MUTED, theme.TEXT, theme.TEXT, theme.TEXT,
                    theme.MUTED, st_fg[u["status"]]])
            self._grid_rows[r] = u

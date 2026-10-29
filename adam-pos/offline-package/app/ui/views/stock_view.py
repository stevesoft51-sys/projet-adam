"""Onglet Stocks (admin) : ingredients, mouvements, recettes.

Les boutons ouvrent des FORMULAIRES FLOTTANTS camoufles dans l'onglet
(une seule section reutilisee, contenu selon l'action) : aucune fenetre
de dialogue.
"""
import tkinter as tk
from tkinter import ttk

from .. import theme
from ...services import MOVEMENT_TYPES
from ..widgets import DataGrid, clear, confirm, show_error, info

UNITS = ["kg", "g", "L", "cl", "pièce", "sachet", "bouteille"]
REASONS = ["Achat marché", "Réception fournisseur", "Perte/casse",
           "Consommation interne", "Correction inventaire"]


class StockView(ttk.Frame):
    def __init__(self, parent, state):
        super().__init__(parent, style="TFrame")
        self.state = state
        self._build()
        self.refresh()

    def _build(self):
        holder = tk.Frame(self, bg=theme.CARD, highlightthickness=1,
                          highlightbackground="#e5ded0")
        holder.pack(fill="both", expand=True, padx=10, pady=10)

        top = tk.Frame(holder, bg=theme.CARD)
        top.pack(fill="x", padx=10, pady=(10, 4))
        tk.Label(top, text=self.state.tr("stock.title"), bg=theme.CARD,
                 font=("Segoe UI", 12, "bold")).pack(side="left")
        btns = tk.Frame(top, bg=theme.CARD)
        btns.pack(side="right")
        ttk.Button(btns, text=self.state.tr("stock.btn_new_ingredient"),
                   command=self.new_ingredient).pack(side="left", padx=2)
        ttk.Button(btns, text=self.state.tr("stock.btn_movement"),
                   style="Accent.TButton",
                   command=self.add_movement).pack(side="left", padx=2)
        ttk.Button(btns, text=self.state.tr("stock.btn_recipes"),
                   command=self.edit_recipes).pack(side="left", padx=2)

        self.kpis = tk.Frame(holder, bg=theme.CARD)
        self.kpis.pack(fill="x", padx=12, pady=(2, 6))

        self.grid_holder = tk.Frame(holder, bg=theme.CARD)
        self.grid_holder.pack(fill="both", expand=True, padx=12, pady=(2, 0))

        actions = tk.Frame(holder, bg=theme.CARD)
        actions.pack(fill="x", padx=10, pady=(4, 8))
        ttk.Button(actions, text=self.state.tr("stock.btn_edit_selected"),
                   command=self.edit_ingredient).pack(side="left")
        ttk.Button(actions, text=self.state.tr("stock.btn_delete"),
                   style="Danger.TButton",
                   command=self.delete_ingredient).pack(side="left", padx=6)

        hist_label = tk.Label(holder, text=self.state.tr("stock.history_title"),
                              bg=theme.CARD, font=("Segoe UI", 11, "bold"))
        hist_label.pack(anchor="w", padx=12, pady=(8, 2))

        self.hist_holder = tk.Frame(holder, bg=theme.CARD)
        self.hist_holder.pack(fill="both", expand=True, padx=12,
                              pady=(0, 10))

        # section flottante unique (camouffee) pour tous les formulaires
        self._build_float_section()

    # ============================================ section flottante unique ==
    def _build_float_section(self):
        f = tk.Frame(self, bg=theme.CARD, highlightthickness=1,
                     highlightbackground="#b9ae95")
        inner = tk.Frame(f, bg=theme.CARD)
        inner.pack(fill="both", expand=True, padx=1, pady=1)
        self.float_card = f

        self.f_banner = tk.Frame(inner, bg="#fdf6e7")
        self.f_banner.pack(fill="x")
        self.lbl_title = tk.Label(self.f_banner, text="", bg="#fdf6e7",
                                  fg=theme.ACCENT_HOVER,
                                  font=("Segoe UI", 12, "bold"))
        self.lbl_title.pack(anchor="w", padx=18, pady=(10, 2))
        self.lbl_sub = tk.Label(self.f_banner, text="", bg="#fdf6e7",
                                fg=theme.MUTED, font=theme.FONT_SMALL,
                                wraplength=520, justify="left")
        self.lbl_sub.pack(anchor="w", padx=18, pady=(0, 10))

        self.f_body = tk.Frame(inner, bg=theme.CARD)
        self.f_body.pack(fill="both", expand=True, padx=18, pady=(10, 4))
        self.f_foot = tk.Frame(inner, bg=theme.CARD)
        self.f_foot.pack(fill="x", padx=18, pady=(6, 14))
        f.bind("<Escape>", lambda e: self._hide_form())

    def _open_form(self, title, sub="", width=480, banner_bg="#fdf6e7",
                   banner_fg=None):
        self.lbl_title.config(text=title, bg=banner_bg,
                              fg=banner_fg or theme.ACCENT_HOVER)
        self.lbl_sub.config(text=sub, bg=banner_bg)
        self.f_banner.config(bg=banner_bg)
        clear(self.f_body)
        clear(self.f_foot)
        self.float_card.place(relx=0.5, rely=0.5, anchor="center",
                              width=width)
        self.float_card.lift()

    def _hide_form(self):
        self.float_card.place_forget()

    @staticmethod
    def _frow(body, row, label, widget, sticky="ew"):
        tk.Label(body, text=label, bg=theme.CARD, fg=theme.MUTED,
                 font=theme.FONT_SMALL, width=16, anchor="nw"
                 ).grid(row=row, column=0, sticky="nw", pady=5)
        widget.grid(row=row, column=1, sticky=sticky, pady=5)

    @staticmethod
    def _num(raw):
        try:
            return float((raw or "0").replace(",", ".").replace(" ", "")
                         or 0)
        except ValueError:
            return 0.0

    # ------------------------------------------- formulaire ingredient ----
    def new_ingredient(self):
        self._show_ingredient_form(None)

    def edit_ingredient(self):
        ing = self._selected_ingredient()
        if not ing:
            show_error(self, self.state.tr("stock.error_select_ingredient"))
            return
        self._show_ingredient_form(ing)

    def _show_ingredient_form(self, ing):
        self._form_ing = ing
        sups = self.state.suppliers.suppliers(active_only=True)
        self._form_sups = sups
        self._open_form(self.state.tr("stock.form_title_edit_ingredient") if ing
                        else self.state.tr("stock.form_title_new_ingredient"),
                        sub=self.state.tr("stock.form_sub_edit_stock",
                            stock=float(ing['current_stock']),
                            unit=ing.get('unit', '')) if ing else
                        self.state.tr("stock.form_sub_new_stock"))
        body = self.f_body
        body.columnconfigure(1, weight=1)
        self.i_e_name = ttk.Entry(body)
        self._frow(body, 0, self.state.tr("stock.field_name"), self.i_e_name)
        self.i_cb_unit = ttk.Combobox(body, values=UNITS, state="readonly")
        self.i_cb_unit.current(0)
        self._frow(body, 1, self.state.tr("stock.field_unit"), self.i_cb_unit)
        self.i_e_min = ttk.Entry(body, justify="right")
        self._frow(body, 2, self.state.tr("stock.field_min_stock"), self.i_e_min)
        self.i_e_cost = ttk.Entry(body, justify="right")
        self._frow(body, 3, self.state.tr("stock.field_cost"), self.i_e_cost)

        sup_names = [self.state.tr("stock.no_supplier")] + [s["name"] for s in sups]
        self.i_cb_sup = ttk.Combobox(
            body, values=sup_names, state="readonly")
        self._frow(body, 4, self.state.tr("stock.field_supplier"), self.i_cb_sup)
        if ing:
            sid = ing.get("supplier_id")
            if sid:
                for j, s in enumerate(sups):
                    if s["id"] == sid:
                        self.i_cb_sup.current(j + 1)
                        break
                else:
                    self.i_cb_sup.current(0)
            else:
                self.i_cb_sup.current(0)
        else:
            self.i_cb_sup.current(0)

        self.i_err = tk.Label(body, bg=theme.CARD, fg=theme.DANGER,
                              font=theme.FONT_SMALL)
        self.i_err.grid(row=5, column=0, columnspan=2, sticky="w")
        if ing:
            self.i_e_name.insert(0, ing["name"])
            self.i_cb_unit.set(ing.get("unit") or "kg")
            self.i_e_min.insert(
                0, f"{float(ing.get('min_stock') or 0):g}")
            self.i_e_cost.insert(
                0, f"{float(ing.get('cost_price') or 0):g}")
        ttk.Button(self.f_foot, text=self.state.tr("stock.btn_cancel"),
                   command=self._hide_form).pack(side="right")
        ttk.Button(self.f_foot, text=self.state.tr("stock.btn_save"),
                   style="Accent.TButton",
                   command=self._save_ingredient).pack(side="right", padx=8)
        self.i_e_name.focus_set()

    def _save_ingredient(self):
        sup_idx = self.i_cb_sup.current()
        supplier_id = None
        if sup_idx > 0:
            supplier_id = self._form_sups[sup_idx - 1]["id"]
        data = {
            "name": self.i_e_name.get(),
            "unit": self.i_cb_unit.get(),
            "min_stock": self._num(self.i_e_min.get()),
            "cost_price": self._num(self.i_e_cost.get()),
            "supplier_id": supplier_id,
        }
        try:
            self.state.stock.save_ingredient(
                data, ing_id=self._form_ing["id"] if self._form_ing else None)
        except Exception as exc:
            self.i_err.config(text=str(exc))
            return
        self._hide_form()
        self.refresh()

    # --------------------------------------------- formulaire mouvement ---
    def add_movement(self):
        ing_list = self.state.stock.ingredients()
        self._mov_ings = ing_list
        self._open_form(self.state.tr("stock.form_title_movement"),
                        sub=self.state.tr("stock.form_sub_movement"))
        body = self.f_body
        body.columnconfigure(1, weight=1)
        names = [f"{i['name']} ({float(i['current_stock']):g} "
                 f"{i.get('unit', '')})" for i in ing_list]
        self.m_cb_ing = ttk.Combobox(body, values=names, state="readonly")
        self._frow(body, 0, self.state.tr("stock.field_movement_ingredient"), self.m_cb_ing)
        if names:
            self.m_cb_ing.current(0)
        self.m_var_type = tk.StringVar(value="in")
        types_frame = tk.Frame(body, bg=theme.CARD)
        for value, label in (("in", self.state.tr("stock.movement_type_in")),
                             ("out", self.state.tr("stock.movement_type_out")),
                             ("adjust", self.state.tr("stock.movement_type_adjust"))):
            tk.Radiobutton(types_frame, text=label,
                           variable=self.m_var_type, value=value,
                           bg=theme.CARD, selectcolor="#efe9de"
                           ).pack(side="left", padx=4)
        self._frow(body, 1, self.state.tr("stock.field_movement_type"), types_frame)
        self.m_e_qty = ttk.Entry(body, justify="right")
        self._frow(body, 2, self.state.tr("stock.field_movement_qty"), self.m_e_qty)
        self.m_cb_reason = ttk.Combobox(body, values=REASONS)
        self.m_cb_reason.current(0)
        self._frow(body, 3, self.state.tr("stock.field_movement_reason"), self.m_cb_reason)
        self.m_err = tk.Label(body, bg=theme.CARD, fg=theme.DANGER,
                              font=theme.FONT_SMALL)
        self.m_err.grid(row=4, column=0, columnspan=2, sticky="w")
        if not names:
            self.m_err.config(text=self.state.tr("stock.error_create_ingredient_first"))
        ttk.Button(self.f_foot, text=self.state.tr("stock.btn_cancel"),
                   command=self._hide_form).pack(side="right")
        ttk.Button(self.f_foot, text=self.state.tr("stock.btn_save_movement"),
                   style="Accent.TButton",
                   command=self._save_movement).pack(side="right", padx=8)
        if names:
            self.m_e_qty.focus_set()

    def _save_movement(self):
        try:
            qty = float(self.m_e_qty.get().replace(",", ".")
                        .replace(" ", ""))
            idx = self.m_cb_ing.current()
            ing = self._mov_ings[idx]
            mtype = self.m_var_type.get()
            reason = self.m_cb_reason.get().strip() or self.state.tr("stock.default_reason")
            self.state.stock.add_movement(ing["id"], mtype, qty, reason,
                                          self.state.user["name"])
        except IndexError:
            self.m_err.config(text=self.state.tr("stock.error_create_ingredient_first"))
            return
        except ValueError:
            self.m_err.config(text=self.state.tr("stock.error_invalid_qty"))
            return
        except Exception as exc:
            self.m_err.config(text=str(exc))
            return
        self._hide_form()
        self.refresh()

    # ---------------------------------------------- formulaire recettes ---
    def edit_recipes(self):
        prods = sorted(self.state.catalog.products(),
                       key=lambda p: p["name"].lower())
        if not prods:
            info(self, self.state.tr("stock.info_create_products"))
            return
        self._rec_prods = prods
        self._open_form(self.state.tr("stock.form_title_recipes"),
                        sub=self.state.tr("stock.form_sub_recipes"), width=560)
        body = self.f_body
        body.columnconfigure(0, weight=1)
        topf = tk.Frame(body, bg=theme.CARD)
        topf.grid(row=0, column=0, sticky="ew")
        self.r_cb_prod = ttk.Combobox(topf, values=[p["name"]
                                                    for p in prods],
                                      state="readonly", width=36)
        self.r_cb_prod.pack(anchor="w")
        self.r_cb_prod.current(0)
        self.r_cb_prod.bind("<<ComboboxSelected>>",
                            lambda e: self._load_recipe())

        self.r_lines = tk.Frame(body, bg=theme.CARD)
        self.r_lines.grid(row=1, column=0, sticky="nsew", pady=(8, 0))
        body.rowconfigure(1, weight=1)
        self.rec_rows = []

        add_row = tk.Frame(body, bg=theme.CARD)
        add_row.grid(row=2, column=0, sticky="ew", pady=(8, 0))
        ing_list = self.state.stock.ingredients()
        self._rec_ings = ing_list
        self.r_cb_add = ttk.Combobox(add_row,
                                     values=[f"{i['name']} "
                                             f"({i.get('unit', '')})"
                                             for i in ing_list],
                                     state="readonly", width=26)
        self.r_cb_add.pack(side="left")
        if ing_list:
            self.r_cb_add.current(0)
        self.r_e_qty = ttk.Entry(add_row, width=8, justify="right")
        self.r_e_qty.insert(0, "0")
        self.r_e_qty.pack(side="left", padx=6)
        ttk.Button(add_row, text=self.state.tr("stock.btn_add_to_recipe"),
                   style="Accent.TButton",
                   command=self._add_recipe_line).pack(side="left")

        self.r_err = tk.Label(body, bg=theme.CARD, fg=theme.DANGER,
                              font=theme.FONT_SMALL)
        self.r_err.grid(row=3, column=0, sticky="w", pady=(4, 0))

        ttk.Button(self.f_foot, text=self.state.tr("stock.btn_cancel"),
                   command=self._hide_form).pack(side="right")
        ttk.Button(self.f_foot, text=self.state.tr("stock.btn_save_recipe"),
                   style="Accent.TButton",
                   command=self._save_recipes).pack(side="right", padx=8)
        self._load_recipe()

    def _recipe_line_frame(self, ing, qty_txt):
        frame = tk.Frame(self.r_lines, bg=theme.CARD)
        frame.pack(fill="x", pady=2)
        tk.Label(frame, text=f"• {ing['name']}", bg=theme.CARD,
                 width=24, anchor="w").pack(side="left")
        entry = ttk.Entry(frame, width=8, justify="right")
        entry.insert(0, qty_txt)
        entry.pack(side="left")
        tk.Label(frame, text=ing.get("unit", ""), bg=theme.CARD,
                 fg=theme.MUTED,
                 font=theme.FONT_SMALL).pack(side="left", padx=4)
        ttk.Button(frame, text="✕", width=3,
                   command=lambda: self._remove_recipe_line(frame)
                   ).pack(side="left", padx=6)
        self.rec_rows.append({"frame": frame, "id": ing["id"],
                              "qty": entry})

    def _load_recipe(self):
        for r in self.rec_rows:
            r["frame"].destroy()
        self.rec_rows.clear()
        prod = self._rec_prods[self.r_cb_prod.current()]
        for line in self.state.stock.recipe_for(prod["id"]):
            ing = self.state.stock.ingredient_by_id(line["ingredient_id"])
            if not ing:
                continue
            self._recipe_line_frame(ing, f"{line['qty']:g}")

    def _add_recipe_line(self):
        if not self._rec_ings:
            return
        idx = self.r_cb_add.current()
        if idx < 0:
            return
        ing = self._rec_ings[idx]
        existing = next((r for r in self.rec_rows
                         if r["id"] == ing["id"]), None)
        add = self._num(self.r_e_qty.get())
        if existing:
            cur = self._num(existing["qty"].get())
            existing["qty"].delete(0, "end")
            existing["qty"].insert(0, f"{cur + add:g}")
            return
        self._recipe_line_frame(ing, f"{add:g}")

    def _remove_recipe_line(self, frame):
        self.rec_rows = [r for r in self.rec_rows
                         if r["frame"] is not frame]
        frame.destroy()

    def _save_recipes(self):
        lines = []
        for r in self.rec_rows:
            qty = self._num(r["qty"].get())
            if qty > 0:
                lines.append({"ingredient_id": r["id"], "qty": qty})
        prod = self._rec_prods[self.r_cb_prod.current()]
        try:
            self.state.stock.set_recipe(prod["id"], lines)
        except Exception as exc:
            self.r_err.config(text=str(exc))
            return
        self._hide_form()
        self.refresh()

    # ------------------------------------------------------------- refresh --
    def refresh(self):
        clear(self.kpis)
        ing_list = self.state.stock.ingredients()
        low = [i for i in ing_list
               if float(i["current_stock"]) <= float(i.get("min_stock", 0))]
        value = sum(float(i["current_stock"]) *
                    float(i.get("cost_price") or 0) for i in ing_list)
        for title, val, color in (
                (self.state.tr("stock.kpi_references"), str(len(ing_list)), theme.TEXT),
                (self.state.tr("stock.kpi_stock_value"), theme.money(value), theme.ACCENT_HOVER),
                (self.state.tr("stock.kpi_low_alerts"), str(len(low)),
                 theme.DANGER if low else theme.SUCCESS)):
            f = tk.Frame(self.kpis, bg=theme.CARD)
            f.pack(side="left", padx=(0, 34))
            tk.Label(f, text=title.upper(), bg=theme.CARD, fg=theme.MUTED,
                     font=theme.FONT_SMALL).pack(anchor="w")
            tk.Label(f, text=val, bg=theme.CARD, fg=color,
                     font=("Segoe UI", 13, "bold")).pack(anchor="w")

        # -- tableau ingredients (DataGrid : vraies separations) ------------
        for w in self.grid_holder.winfo_children():
            w.destroy()
        self.pgrid = DataGrid(self.grid_holder, [
            ("name", self.state.tr("stock.col_ingredient"), 200, "w", True),
            ("unit", self.state.tr("stock.col_unit"), 80, "center", False),
            ("stock", self.state.tr("stock.col_stock"), 100, "e", False),
            ("min", self.state.tr("stock.col_min_stock"), 90, "e", False),
            ("value", self.state.tr("stock.col_value"), 110, "e", False),
            ("status", self.state.tr("stock.col_status"), 110, "center", False),
        ])
        self.pgrid.pack(fill="both", expand=True)
        self._grid_ing = {}
        self.pgrid.on_select = lambda r: None
        for i in ing_list:
            cur = float(i["current_stock"])
            mini = float(i.get("min_stock", 0) or 0)
            if cur <= mini:
                row_bg = "#fdecea"
                status = self.state.tr("stock.status_to_order")
                st_fg = theme.DANGER
            elif cur <= mini * 1.5:
                row_bg = "#fef7e6"
                status = self.state.tr("stock.status_low")
                st_fg = "#a2701c"
            else:
                row_bg = None
                status = self.state.tr("stock.status_ok")
                st_fg = theme.SUCCESS
            r = self.pgrid.add_row(
                (i["name"], i.get("unit", ""), f"{cur:g}", f"{mini:g}",
                 theme.money(cur * float(i.get("cost_price") or 0)),
                 status),
                fg=[theme.TEXT, theme.MUTED,
                    theme.TEXT if cur > mini else theme.DANGER,
                    theme.MUTED, theme.TEXT, st_fg],
                bg=row_bg)
            self._grid_ing[r] = i

        # -- historique des mouvements -------------------------------------
        for w in self.hist_holder.winfo_children():
            w.destroy()
        self.hist = DataGrid(self.hist_holder, [
            ("ing", self.state.tr("stock.col_ingredient"), 150, "w", False),
            ("type", self.state.tr("stock.col_type"), 110, "center", False),
            ("qty", self.state.tr("stock.col_qty"), 90, "e", False),
            ("after", self.state.tr("stock.col_after"), 90, "e", False),
            ("reason", self.state.tr("stock.col_reason"), 230, "w", True),
            ("by", self.state.tr("stock.col_by"), 100, "center", False),
        ])
        self.hist.pack(fill="both", expand=True)
        for m in self.state.stock.movements(limit=40):
            kind = MOVEMENT_TYPES[m["type"]]
            qty_txt = ("+" if m["type"] == "in" else
                       "−" if m["type"] == "out" else "") + \
                f"{abs(m['qty']):g} {m.get('unit', '')}".strip()
            color = {"in": theme.SUCCESS, "out": theme.DANGER,
                     "adjust": "#a2701c"}.get(m["type"], theme.TEXT)
            self.hist.add_row(
                (m["ingredient_name"], kind, qty_txt,
                 f"{m['after']:g}", m["reason"], m["by"]),
                fg=[theme.TEXT, color, color, theme.TEXT,
                    theme.MUTED, theme.MUTED])

    # -------------------------------------------------------------- actions --
    def _selected_ingredient(self):
        r = getattr(self.pgrid, "selected_row", None)
        ing = self._grid_ing.get(r) if r is not None else None
        if not ing:
            return None
        return self.state.stock.ingredient_by_id(ing["id"])

    def delete_ingredient(self):
        ing = self._selected_ingredient()
        if not ing:
            info(self, self.state.tr("stock.info_select_first"))
            return
        if not confirm(self, self.state.tr("stock.confirm_delete", name=ing['name'])):
            return
        self.state.stock.delete_ingredient(ing["id"])
        self.refresh()
